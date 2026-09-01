# GPTs 配置

## 1. Instructions

将 [GPT_INSTRUCTIONS.md](GPT_INSTRUCTIONS.md) 全文粘贴到 GPT 的 Instructions。

## 2. Action 架构

在“添加操作”页面把 [openapi.yaml](openapi.yaml) 全文粘贴到“架构”。

## 3. 身份验证

- 身份验证类型：API Key
- API Key 类型：自定义请求头
- Header：`X-GROWTH-DATA-TOKEN`
- Value：Secret Manager 中 `growth-data-reader-token` 的最新版本

Token 只粘贴到身份验证弹窗，不要放进架构、Instructions、Knowledge 或聊天。

## 4. 隐私政策

填写：

```text
https://github.com/The-AlexLiu/Growth-Data-Reader-Skill/blob/main/gpts/PRIVACY.md
```

## 5. 验收提示词

```text
读取当前 Growth Data Profile，分别验证 GA4、GSC 和 Google Ads。然后查询最近 7 个完整日：GA4 的 sessions、ecommercePurchases、purchaseRevenue；GSC 的 clicks、impressions、CTR、position；Google Ads 的 cost、clicks、conversions、conversionValue。按日期输出，并解释三平台的时区、归因和数据口径差异。不要显示任何认证信息。
```
