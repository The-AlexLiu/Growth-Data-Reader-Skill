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

## 3. 完成组合 OAuth

```bash
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform
```

OAuth 账号必须能读取 Profile 中的 GA4、GSC 和 Google Ads 账户。

## 4. 创建 Secret

将以下内容分别保存到 Secret Manager：

- `growth-data-oauth-credentials`：ADC OAuth JSON；
- `growth-data-ads-developer-token`：Google Ads Developer Token；
- `growth-data-reader-token`：随机生成的 Gateway Reader Token；
- `growth-data-account-profile`：`account-profile.json`。

不要把这些值提交到 Git。

## 5. 部署

```bash
gcloud run deploy growth-data-gateway \
  --source services/growth-data-gateway \
  --region us-central1 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
  --set-secrets GOOGLE_OAUTH_CREDENTIALS_JSON=growth-data-oauth-credentials:latest,GOOGLE_ADS_DEVELOPER_TOKEN=growth-data-ads-developer-token:latest,GROWTH_DATA_READER_TOKEN=growth-data-reader-token:latest,ACCOUNT_PROFILE_JSON=growth-data-account-profile:latest \
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
