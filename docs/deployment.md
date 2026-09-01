# 统一 Gateway 部署

## 1. 获取账户 Profile

先运行 [Browser Use 一键账户发现 Prompt](../prompts/browser-use-account-discovery.md)，生成 `account-profile.json`。

## 2. 启用 API

```bash
gcloud services enable \
  analyticsdata.googleapis.com \
  searchconsole.googleapis.com \
  googleads.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com
```

## 3. 完成授权

```bash
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform
```

Cloud Run 服务身份需要获得 GA4 Property 只读权限。GSC 与 Google Ads 可以使用同一个或两个不同的 OAuth 用户，但对应用户必须能读取 Profile 中的资产。

## 4. 创建 Secret

将以下内容分别保存到 Secret Manager：

- `growth-data-gsc-oauth-credentials`：包含 GSC Scope 的 OAuth JSON；
- `growth-data-ads-oauth-credentials`：包含 Google Ads Scope 的 OAuth JSON；
- `growth-data-ads-developer-token`：Google Ads Developer Token；
- `growth-data-reader-token`：随机生成的 Gateway Reader Token；
- `growth-data-account-profile`：`account-profile.json`。

不要把这些值提交到 Git。

## 5. 部署

```bash
gcloud run deploy growth-data-gateway \
  --source services/growth-data-gateway \
  --region us-central1 \
  --service-account YOUR_GA4_READER_SERVICE_ACCOUNT \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
  --set-secrets GSC_OAUTH_CREDENTIALS_JSON=growth-data-gsc-oauth-credentials:latest,GOOGLE_ADS_OAUTH_CREDENTIALS_JSON=growth-data-ads-oauth-credentials:latest,GOOGLE_ADS_DEVELOPER_TOKEN=growth-data-ads-developer-token:latest,GROWTH_DATA_READER_TOKEN=growth-data-reader-token:latest,ACCOUNT_PROFILE_JSON=growth-data-account-profile:latest \
  --allow-unauthenticated
```

## 6. 验证

依次调用：

- `GET /health`；
- `GET /v1/profile`；
- `POST /v1/ga4/report`；
- `POST /v1/gsc/query`；
- `POST /v1/google-ads/query`。

后三个数据源必须返回 Profile 中对应的账户数据。
