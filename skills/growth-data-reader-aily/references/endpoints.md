# Gateway Endpoints

| 数据源 | Method | Path |
|---|---|---|
| Profile | GET | `/v1/profile` |
| GA4 Report | POST | `/v1/ga4/report` |
| GA4 Metadata | GET | `/v1/ga4/metadata` |
| GSC Search Analytics | POST | `/v1/gsc/query` |
| GSC Metadata | GET | `/v1/gsc/metadata` |
| GSC Sitemaps | GET | `/v1/gsc/sitemaps` |
| GSC URL Inspection | POST | `/v1/gsc/inspect` |
| Google Ads GAQL | POST | `/v1/google-ads/query` |
| Google Ads Metadata | GET | `/v1/google-ads/metadata` |

所有受保护接口使用 `X-GROWTH-DATA-TOKEN`。Gateway 根据 Token 和服务端 Profile 固定账户，调用方不能覆盖 Property 或 Customer ID。
