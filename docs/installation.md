# 飞书 Aily 与 WorkBuddy 安装

## 飞书 Aily

1. 在 Aily 的技能管理中上传 `growth-data-reader-aily-v1.0.0.skill`。
2. 新建一个 HTTPS 连接器，Base URL 填部署后的 Gateway 地址。
3. 将 Reader Token 保存为应用级 Secret，并给所有受保护接口添加统一 Header：

```text
X-GROWTH-DATA-TOKEN: <Reader Token>
```

Token 必须保存为应用或团队级 Secret。

需要创建的操作：

| 操作名 | Method | Path | 用途 |
|---|---|---|---|
| `read_profile` | GET | `/v1/profile` | 检查当前绑定账户 |
| `ga4_report` | POST | `/v1/ga4/report` | GA4 报表 |
| `ga4_metadata` | GET | `/v1/ga4/metadata` | GA4 字段元数据 |
| `gsc_query` | POST | `/v1/gsc/query` | 搜索表现 |
| `gsc_metadata` | GET | `/v1/gsc/metadata` | GSC Property 信息 |
| `gsc_sitemaps` | GET | `/v1/gsc/sitemaps` | Sitemap 状态 |
| `gsc_inspect` | POST | `/v1/gsc/inspect` | URL Inspection |
| `google_ads_query` | POST | `/v1/google-ads/query` | Google Ads GAQL 查询 |
| `google_ads_metadata` | GET | `/v1/google-ads/metadata` | Ads 账户信息 |

所有 POST 操作的请求体类型均为 JSON。建议先运行 `read_profile`，确认 Profile 后再查询数据。

## WorkBuddy

1. 在 WorkBuddy 的技能导入页面上传 `growth-data-reader-workbuddy-v1.0.0.zip`。
2. 勾选“非高风险自动安装”。
3. 在项目或团队级持久化凭据中配置：

```text
GROWTH_DATA_API_URL=https://YOUR_GATEWAY_URL
GROWTH_DATA_READER_TOKEN=<Reader Token>
```

不要只把 Token 粘贴到聊天或临时环境变量；会话重启后会丢失。

首次使用可直接输入：

```text
读取当前 Growth Data Profile，分别验证 GA4、GSC 和 Google Ads 连接。成功后查询最近 7 个完整日的 GA4 sessions 与 purchaseRevenue、GSC clicks 与 impressions、Google Ads cost 与 conversions，并按日期输出一张对比表。不要显示任何 Token 或认证请求头。
```

验证：

```text
读取当前 Growth Data Profile，并分别验证 GA4 最近 7 天 sessions、GSC 最近 7 个完整日 clicks、Google Ads 最近 7 天 cost。
```
