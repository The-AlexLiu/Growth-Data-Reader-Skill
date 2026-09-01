# GPTs 配置

## 0. 基本信息

- 名称：`INIA Growth Data Analyst`
- 描述：`只读分析 INIA 的 GA4、Google Search Console 与 Google Ads 数据，输出投放、SEO、落地页和转化优化建议。`
- 推荐能力：开启“代码解释器与数据分析”；Web Search 按需开启；不要同时启用 Apps。

建议的对话开场白：

```text
分析最近 7 个完整日的网站、自然搜索和广告表现
检查昨天 Google Ads 花费和 GA4 购买收入是否异常
找出最近 30 天高流量低转化的落地页
分析自然搜索点击下降来自曝光、排名还是 CTR
```

## 1. Instructions

将 [GPT_INSTRUCTIONS.md](GPT_INSTRUCTIONS.md) 全文粘贴到 GPT 的 Instructions。

## 2. Action 架构

在“添加操作”页面点击“通过 URL 导入”，填写：

```text
https://raw.githubusercontent.com/The-AlexLiu/Growth-Data-Reader-Skill/main/gpts/openapi.yaml
```

也可以把 [openapi.yaml](openapi.yaml) 全文粘贴到“架构”。

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
