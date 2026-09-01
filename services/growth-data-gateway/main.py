import datetime as dt
import hmac
import json
import os
import re
import threading
import time
from urllib.parse import quote, urlparse

import requests
from flask import Flask, jsonify, request


TOKEN_URL = "https://oauth2.googleapis.com/token"
GA4_BASE = "https://analyticsdata.googleapis.com/v1beta"
GSC_BASE = "https://searchconsole.googleapis.com"
ADS_BASE = "https://googleads.googleapis.com"
MAX_REQUEST_BYTES = 64 * 1024
MAX_GA4_ROWS = 10_000
MAX_GSC_ROWS = 25_000
MAX_ADS_ROWS = 10_000
MAX_QUERY_CHARS = 20_000
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}|today|yesterday|\d+daysAgo)$")
ADS_LIMIT_RE = re.compile(r"\bLIMIT\s+(\d+)\s*$", re.IGNORECASE)
ADS_FORBIDDEN_RE = re.compile(
    r"\b(MUTATE|CREATE|UPDATE|DELETE|INSERT|REMOVE)\b", re.IGNORECASE
)
GSC_DIMENSIONS = {
    "country",
    "date",
    "device",
    "hour",
    "page",
    "query",
    "searchAppearance",
}
GSC_OPERATORS = {
    "contains",
    "equals",
    "excludingRegex",
    "includingRegex",
    "notContains",
    "notEquals",
}
GSC_TYPES = {"discover", "googleNews", "image", "news", "video", "web"}
GSC_STATES = {"all", "final", "hourly_all"}
GSC_AGGREGATIONS = {"auto", "byNewsShowcasePanel", "byPage", "byProperty"}


app = Flask(__name__)
_token_lock = threading.Lock()
_token_cache = {"access_token": "", "expires_at": 0.0}


def error(message: str, status: int):
    return jsonify({"error": message}), status


def authorized() -> bool:
    expected = os.environ.get("GROWTH_DATA_READER_TOKEN", "")
    supplied = request.headers.get("X-GROWTH-DATA-TOKEN", "")
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


def profile() -> dict:
    raw = os.environ.get("ACCOUNT_PROFILE_JSON", "")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("ACCOUNT_PROFILE_JSON is invalid") from exc
    if not isinstance(value, dict) or not value.get("profileId"):
        raise RuntimeError("ACCOUNT_PROFILE_JSON must include profileId")
    return value


def oauth_info() -> dict:
    raw = os.environ.get("GOOGLE_OAUTH_CREDENTIALS_JSON", "")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Google OAuth credentials are invalid") from exc
    required = ("client_id", "client_secret", "refresh_token")
    if not all(isinstance(value.get(key), str) and value[key] for key in required):
        raise RuntimeError("Google OAuth credentials are incomplete")
    return value


def access_token() -> str:
    now = time.monotonic()
    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]
    with _token_lock:
        now = time.monotonic()
        if _token_cache["access_token"] and now < _token_cache["expires_at"]:
            return _token_cache["access_token"]
        info = oauth_info()
        response = requests.post(
            TOKEN_URL,
            data={
                "client_id": info["client_id"],
                "client_secret": info["client_secret"],
                "refresh_token": info["refresh_token"],
                "grant_type": "refresh_token",
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        token = payload.get("access_token", "")
        if not token:
            raise RuntimeError("Google OAuth did not return an access token")
        expires_in = int(payload.get("expires_in", 3600))
        _token_cache["access_token"] = token
        _token_cache["expires_at"] = time.monotonic() + max(60, expires_in - 300)
        return token


def google_request(method: str, url: str, *, body=None, headers=None):
    request_headers = {
        "Authorization": f"Bearer {access_token()}",
        "Accept": "application/json",
    }
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if project_id:
        request_headers["x-goog-user-project"] = project_id
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    if headers:
        request_headers.update(headers)
    return requests.request(
        method, url, headers=request_headers, json=body, timeout=90
    )


def source_config(source: str) -> dict:
    value = profile().get(source)
    if not isinstance(value, dict):
        raise RuntimeError(f"{source} is not configured in the account profile")
    return value


def ga4_property_name() -> str:
    value = str(source_config("ga4").get("propertyName", ""))
    if not re.fullmatch(r"properties/\d+", value):
        raise RuntimeError("ga4.propertyName must look like properties/123456789")
    return value


def sanitize_ga4_report(body: dict) -> dict:
    if not isinstance(body, dict):
        raise ValueError("request body must be a JSON object")
    ranges = body.get("dateRanges")
    if not isinstance(ranges, list) or not 1 <= len(ranges) <= 4:
        raise ValueError("dateRanges must contain 1-4 ranges")
    for item in ranges:
        if not isinstance(item, dict) or not DATE_RE.match(
            str(item.get("startDate", ""))
        ) or not DATE_RE.match(str(item.get("endDate", ""))):
            raise ValueError("dateRanges contain an invalid GA4 date")
    clean = dict(body)
    clean.pop("property", None)
    try:
        limit = int(clean.get("limit", 1_000))
        offset = int(clean.get("offset", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("limit and offset must be integers") from exc
    if not 1 <= limit <= MAX_GA4_ROWS or offset < 0:
        raise ValueError("GA4 limit or offset is outside the allowed range")
    clean["limit"] = str(limit)
    clean["offset"] = str(offset)
    clean["returnPropertyQuota"] = True
    return clean


def gsc_site_url() -> str:
    value = str(source_config("gsc").get("siteUrl", "")).strip()
    if value.startswith("sc-domain:") and len(value) > len("sc-domain:"):
        return value
    if value.startswith(("https://", "http://")):
        return value
    raise RuntimeError("gsc.siteUrl is invalid")


def parse_date(value, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must use YYYY-MM-DD")
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field} must use YYYY-MM-DD") from exc


def sanitize_gsc_query(body: dict) -> dict:
    if not isinstance(body, dict):
        raise ValueError("request body must be a JSON object")
    allowed = {
        "aggregationType",
        "dataState",
        "dimensionFilterGroups",
        "dimensions",
        "endDate",
        "rowLimit",
        "startDate",
        "startRow",
        "type",
    }
    unknown = sorted(set(body) - allowed)
    if unknown:
        raise ValueError(f"unsupported fields: {', '.join(unknown)}")
    clean = dict(body)
    clean["startDate"] = parse_date(clean.get("startDate"), "startDate")
    clean["endDate"] = parse_date(clean.get("endDate"), "endDate")
    if clean["startDate"] > clean["endDate"]:
        raise ValueError("startDate must not be after endDate")
    dimensions = clean.get("dimensions", [])
    if not isinstance(dimensions, list) or not all(
        isinstance(value, str) and value in GSC_DIMENSIONS for value in dimensions
    ) or len(dimensions) > 5:
        raise ValueError("dimensions contain an unsupported value")
    row_limit = clean.get("rowLimit", 1_000)
    start_row = clean.get("startRow", 0)
    if not isinstance(row_limit, int) or isinstance(row_limit, bool):
        raise ValueError("rowLimit must be an integer")
    if not 1 <= row_limit <= MAX_GSC_ROWS:
        raise ValueError(f"rowLimit must be between 1 and {MAX_GSC_ROWS}")
    if not isinstance(start_row, int) or isinstance(start_row, bool) or start_row < 0:
        raise ValueError("startRow must be a non-negative integer")
    clean["rowLimit"] = row_limit
    clean["type"] = clean.get("type", "web")
    clean["dataState"] = clean.get("dataState", "final")
    if clean["type"] not in GSC_TYPES or clean["dataState"] not in GSC_STATES:
        raise ValueError("type or dataState contains an unsupported value")
    if clean.get("aggregationType", "auto") not in GSC_AGGREGATIONS:
        raise ValueError("aggregationType contains an unsupported value")
    groups = clean.get("dimensionFilterGroups", [])
    if not isinstance(groups, list) or len(groups) > 5:
        raise ValueError("dimensionFilterGroups must have at most 5 groups")
    for group in groups:
        if not isinstance(group, dict) or set(group) - {"filters", "groupType"}:
            raise ValueError("dimensionFilterGroups contain unsupported fields")
        if group.get("groupType", "and") != "and":
            raise ValueError("only and filter groups are supported")
        filters = group.get("filters", [])
        if not isinstance(filters, list) or len(filters) > 10:
            raise ValueError("each filter group may contain at most 10 filters")
        for item in filters:
            if not isinstance(item, dict) or set(item) - {
                "dimension",
                "expression",
                "operator",
            }:
                raise ValueError("filters contain unsupported fields")
            if item.get("dimension") not in GSC_DIMENSIONS:
                raise ValueError("filter dimension is unsupported")
            if item.get("operator", "equals") not in GSC_OPERATORS:
                raise ValueError("filter operator is unsupported")
            expression = item.get("expression")
            if not isinstance(expression, str) or not expression or len(expression) > 4096:
                raise ValueError("filter expression is invalid")
    return clean


def inspection_belongs_to_property(inspection_url: str, site_url: str) -> bool:
    parsed = urlparse(inspection_url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if site_url.startswith("sc-domain:"):
        domain = site_url.removeprefix("sc-domain:").lower()
        hostname = (parsed.hostname or "").lower()
        return hostname == domain or hostname.endswith(f".{domain}")
    property_parts = urlparse(site_url)
    property_path = property_parts.path or "/"
    return (
        parsed.scheme == property_parts.scheme
        and parsed.hostname == property_parts.hostname
        and parsed.port == property_parts.port
        and parsed.path.startswith(property_path)
    )


def sanitize_gsc_inspection(body: dict) -> dict:
    if not isinstance(body, dict) or set(body) - {"inspectionUrl", "languageCode"}:
        raise ValueError("inspection body may contain inspectionUrl and languageCode only")
    inspection_url = body.get("inspectionUrl")
    site_url = gsc_site_url()
    if (
        not isinstance(inspection_url, str)
        or len(inspection_url) > 2048
        or not inspection_belongs_to_property(inspection_url, site_url)
    ):
        raise ValueError("inspectionUrl must belong to the configured GSC property")
    clean = {"inspectionUrl": inspection_url, "siteUrl": site_url}
    language_code = body.get("languageCode")
    if language_code is not None:
        if not isinstance(language_code, str) or not 1 <= len(language_code) <= 16:
            raise ValueError("languageCode must be a string of at most 16 characters")
        clean["languageCode"] = language_code
    return clean


def ads_config() -> dict:
    value = source_config("googleAds")
    customer_id = re.sub(r"\D", "", str(value.get("customerId", "")))
    login_id = re.sub(r"\D", "", str(value.get("loginCustomerId", "")))
    if not re.fullmatch(r"\d{10}", customer_id):
        raise RuntimeError("googleAds.customerId must contain 10 digits")
    if login_id and not re.fullmatch(r"\d{10}", login_id):
        raise RuntimeError("googleAds.loginCustomerId must contain 10 digits")
    return {"customerId": customer_id, "loginCustomerId": login_id}


def sanitize_ads_query(body: dict) -> str:
    if not isinstance(body, dict) or set(body) != {"query"}:
        raise ValueError("request body must contain one query field")
    query = body.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty GAQL string")
    query = query.strip()
    if len(query) > MAX_QUERY_CHARS or ";" in query:
        raise ValueError("query is too long or contains multiple statements")
    if not re.match(r"^SELECT\b", query, re.IGNORECASE) or not re.search(
        r"\bFROM\b", query, re.IGNORECASE
    ) or ADS_FORBIDDEN_RE.search(query):
        raise ValueError("only one read-only GAQL SELECT statement is allowed")
    limit = ADS_LIMIT_RE.search(query)
    if limit and int(limit.group(1)) > MAX_ADS_ROWS:
        raise ValueError(f"LIMIT must not exceed {MAX_ADS_ROWS}")
    return query if limit else f"{query}\nLIMIT {MAX_ADS_ROWS}"


def proxy_json(response):
    try:
        payload = response.json() if response.content else {}
    except ValueError:
        return error("Google returned a non-JSON response", 502)
    return jsonify(payload), response.status_code


@app.get("/health")
def health():
    try:
        configured = profile()
    except RuntimeError as exc:
        return error(str(exc), 503)
    return jsonify(
        {
            "status": "ok",
            "service": "growth-data-gateway",
            "version": "1.0.0",
            "profileId": configured["profileId"],
            "configuredSources": [
                name for name in ("ga4", "gsc", "googleAds") if name in configured
            ],
        }
    )


@app.get("/v1/profile")
def read_profile():
    if not authorized():
        return error("unauthorized", 401)
    try:
        return jsonify(profile())
    except RuntimeError as exc:
        return error(str(exc), 503)


@app.post("/v1/ga4/report")
def ga4_report():
    if not authorized():
        return error("unauthorized", 401)
    if request.content_length and request.content_length > MAX_REQUEST_BYTES:
        return error("request body is too large", 413)
    try:
        property_name = ga4_property_name()
        body = sanitize_ga4_report(request.get_json(silent=True))
        response = google_request(
            "POST", f"{GA4_BASE}/{property_name}:runReport", body=body
        )
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception:
        app.logger.exception("GA4 request failed")
        return error("GA4 request failed", 502)
    return proxy_json(response)


@app.get("/v1/ga4/metadata")
def ga4_metadata():
    if not authorized():
        return error("unauthorized", 401)
    try:
        response = google_request(
            "GET", f"{GA4_BASE}/{ga4_property_name()}/metadata"
        )
    except Exception:
        app.logger.exception("GA4 metadata request failed")
        return error("GA4 request failed", 502)
    return proxy_json(response)


@app.post("/v1/gsc/query")
def gsc_query():
    if not authorized():
        return error("unauthorized", 401)
    if request.content_length and request.content_length > MAX_REQUEST_BYTES:
        return error("request body is too large", 413)
    try:
        encoded = quote(gsc_site_url(), safe="")
        body = sanitize_gsc_query(request.get_json(silent=True))
        response = google_request(
            "POST", f"{GSC_BASE}/webmasters/v3/sites/{encoded}/searchAnalytics/query", body=body
        )
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception:
        app.logger.exception("GSC query failed")
        return error("GSC request failed", 502)
    return proxy_json(response)


@app.get("/v1/gsc/metadata")
def gsc_metadata():
    if not authorized():
        return error("unauthorized", 401)
    try:
        encoded = quote(gsc_site_url(), safe="")
        response = google_request("GET", f"{GSC_BASE}/webmasters/v3/sites/{encoded}")
    except Exception:
        app.logger.exception("GSC metadata request failed")
        return error("GSC request failed", 502)
    return proxy_json(response)


@app.get("/v1/gsc/sitemaps")
def gsc_sitemaps():
    if not authorized():
        return error("unauthorized", 401)
    try:
        encoded = quote(gsc_site_url(), safe="")
        response = google_request("GET", f"{GSC_BASE}/webmasters/v3/sites/{encoded}/sitemaps")
    except Exception:
        app.logger.exception("GSC sitemaps request failed")
        return error("GSC request failed", 502)
    return proxy_json(response)


@app.post("/v1/gsc/inspect")
def gsc_inspect():
    if not authorized():
        return error("unauthorized", 401)
    if request.content_length and request.content_length > MAX_REQUEST_BYTES:
        return error("request body is too large", 413)
    try:
        body = sanitize_gsc_inspection(request.get_json(silent=True))
        response = google_request("POST", f"{GSC_BASE}/v1/urlInspection/index:inspect", body=body)
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception:
        app.logger.exception("GSC inspection request failed")
        return error("GSC request failed", 502)
    return proxy_json(response)


def ads_request(query: str):
    config = ads_config()
    developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "").strip()
    if not developer_token:
        raise RuntimeError("GOOGLE_ADS_DEVELOPER_TOKEN is not configured")
    headers = {"developer-token": developer_token}
    if config["loginCustomerId"]:
        headers["login-customer-id"] = config["loginCustomerId"]
    return google_request(
        "POST",
        f"{ADS_BASE}/v25/customers/{config['customerId']}/googleAds:searchStream",
        body={"query": query},
        headers=headers,
    )


@app.post("/v1/google-ads/query")
def google_ads_query():
    if not authorized():
        return error("unauthorized", 401)
    if request.content_length and request.content_length > MAX_REQUEST_BYTES:
        return error("request body is too large", 413)
    try:
        response = ads_request(sanitize_ads_query(request.get_json(silent=True)))
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception:
        app.logger.exception("Google Ads query failed")
        return error("Google Ads request failed", 502)
    return proxy_json(response)


@app.get("/v1/google-ads/metadata")
def google_ads_metadata():
    if not authorized():
        return error("unauthorized", 401)
    query = (
        "SELECT customer.id, customer.descriptive_name, customer.currency_code, "
        "customer.time_zone FROM customer LIMIT 1"
    )
    try:
        response = ads_request(query)
    except Exception:
        app.logger.exception("Google Ads metadata request failed")
        return error("Google Ads request failed", 502)
    return proxy_json(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
