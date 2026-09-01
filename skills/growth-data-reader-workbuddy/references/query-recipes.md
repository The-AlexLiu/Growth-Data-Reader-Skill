# Query Recipes

## GA4

```json
{
  "dateRanges": [{"startDate": "7daysAgo", "endDate": "yesterday"}],
  "dimensions": [{"name": "date"}],
  "metrics": [{"name": "sessions"}, {"name": "totalUsers"}],
  "limit": 1000
}
```

## GSC

```json
{
  "startDate": "2026-08-01",
  "endDate": "2026-08-07",
  "dimensions": ["date", "query"],
  "type": "web",
  "dataState": "final",
  "rowLimit": 1000
}
```

## Google Ads

```json
{
  "query": "SELECT segments.date, metrics.cost_micros, metrics.clicks, metrics.conversions, metrics.conversions_value FROM customer WHERE segments.date BETWEEN '2026-08-01' AND '2026-08-07' ORDER BY segments.date"
}
```
