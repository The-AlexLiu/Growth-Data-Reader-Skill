---
name: growth-data-reader-aily
description: 统一读取并分析 GA4、Google Search Console 和 Google Ads 数据，用于飞书 Aily 中的渠道、SEO、落地页、转化漏斗、收入和投放诊断；仅支持只读分析，不修改任何平台配置。
---

# Growth Data Reader for Feishu Aily

通过管理员配置的 Growth Data Gateway 查询一个固定 Account Profile。Profile 可包含 GA4、GSC 和 Google Ads 三个数据源。

## 连接要求

使用 Aily 中已配置的 Gateway HTTPS 操作。所有受保护操作使用私密 Header `X-GROWTH-DATA-TOKEN`。Token 必须由应用级 Secret 注入，禁止写入 URL、请求体、Prompt 或回复。

如连接不可用，停止并报告管理员需要配置 Gateway 与持久化 Reader Token。不要安装 `gcloud`、发起个人 OAuth、抓取 Google 后台或索取 Refresh Token、Developer Token、Cookie。

## 数据源路由

- GA4：流量、渠道、Campaign、落地页、事件、漏斗、电商、收入、设备与地区。
- GSC：点击、曝光、CTR、平均排名、搜索词、页面、设备、国家、Sitemap 与 URL Inspection。
- Google Ads：花费、点击、展示、Campaign、广告组、广告、搜索词、转化、价值、CPA 与 ROAS。

根据问题选择最小必要数据源。跨源分析时先分别核对每个数据源总计，再按日期、Campaign 或落地页连接；不得把 GSC clicks、GA4 sessions 和 Ads clicks 当成同一指标。

## 分析口径

1. 从 `/v1/profile` 读取 Profile、时区、币种和数据源，不在请求中传入账户 ID。
2. GA4 日期按 Property 时区；GSC 日期按 Pacific Time；Google Ads 日期按 Ads Account 时区。
3. GA4 使用 `totalUsers` 进行用户漏斗，事件量使用 `eventCount`。
4. GSC CTR 用汇总 clicks / impressions 重算，不平均 CTR 或 position。
5. Google Ads 区分 `conversions` 与 `all_conversions`，并将 `cost_micros / 1,000,000` 转为币种金额。
6. 跨源差异需考虑时区、数据延迟、Consent、跳转、归因模型、转化日期与点击日期。
7. 小样本结论标记 `需观察`，不编造缺失字段。

## 输出

使用中文，先给结论，再给数据表、口径和动作建议。行级结果优先 TSV，诊断优先 Markdown 表格。明确数据源、日期、时区、币种、过滤条件和完整性。

本 Skill 只读，不修改预算、广告、GA4、GSC、GTM、Sitemap、索引或网站。
