import json
import os
import unittest
from unittest.mock import MagicMock, patch

os.environ["GROWTH_DATA_READER_TOKEN"] = "test-reader-token"
os.environ["ACCOUNT_PROFILE_JSON"] = json.dumps(
    {
        "profileId": "example-us",
        "displayName": "Example US",
        "website": "https://example.com",
        "ga4": {"propertyName": "properties/123456789"},
        "gsc": {"siteUrl": "sc-domain:example.com"},
        "googleAds": {
            "customerId": "123-456-7890",
            "loginCustomerId": "098-765-4321",
        },
    }
)
os.environ["GOOGLE_OAUTH_CREDENTIALS_JSON"] = json.dumps(
    {
        "client_id": "client-id",
        "client_secret": "client-secret",
        "refresh_token": "refresh-token",
    }
)
os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "developer-token"

from main import app, sanitize_ads_query, sanitize_ga4_report, sanitize_gsc_inspection  # noqa: E402


class GatewayTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        self.headers = {"X-GROWTH-DATA-TOKEN": "test-reader-token"}

    def test_health_lists_three_sources(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["profileId"], "example-us")
        self.assertEqual(len(response.json["configuredSources"]), 3)

    def test_profile_requires_token(self):
        self.assertEqual(self.client.get("/v1/profile").status_code, 401)

    def test_ga4_cannot_override_property(self):
        body = sanitize_ga4_report(
            {
                "property": "properties/999",
                "dateRanges": [{"startDate": "2026-08-01", "endDate": "2026-08-02"}],
                "metrics": [{"name": "sessions"}],
            }
        )
        self.assertNotIn("property", body)

    def test_gsc_inspection_rejects_other_domain(self):
        with self.assertRaises(ValueError):
            sanitize_gsc_inspection({"inspectionUrl": "https://other.example/"})

    def test_ads_rejects_mutation(self):
        with self.assertRaises(ValueError):
            sanitize_ads_query({"query": "DELETE FROM campaign"})

    def test_ads_adds_limit(self):
        query = sanitize_ads_query({"query": "SELECT campaign.id FROM campaign"})
        self.assertTrue(query.endswith("LIMIT 10000"))

    @patch("main.google_request")
    def test_ga4_endpoint_uses_profile_property(self, request_factory):
        upstream = MagicMock(status_code=200, content=b"{}")
        upstream.json.return_value = {"rowCount": 0}
        request_factory.return_value = upstream
        response = self.client.post(
            "/v1/ga4/report",
            headers=self.headers,
            json={
                "property": "properties/999",
                "dateRanges": [{"startDate": "2026-08-01", "endDate": "2026-08-02"}],
                "metrics": [{"name": "sessions"}],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("properties/123456789:runReport", request_factory.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
