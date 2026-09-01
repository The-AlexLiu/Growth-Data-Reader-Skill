---
name: growth-data-reader-workbuddy
description: 统一读取并分析 GA4、Google Search Console 和 Google Ads 数据，用于 WorkBuddy 中的渠道、SEO、落地页、转化漏斗、收入和投放诊断；仅支持只读分析，不修改任何平台配置。
---

# Growth Data Reader for WorkBuddy

通过 Growth Data Gateway 查询管理员配置的固定 Account Profile。

## 持久化连接

WorkBuddy 项目或团队级私密凭据必须包含：

```text
GROWTH_DATA_API_URL
GROWTH_DATA_READER_TOKEN
```

先运行 `python3 scripts/growth_data_reader.py --profile`。不得显示 Token。若凭据缺失，停止并读取 [references/first-use.md](references/first-use.md)，不要发起个人 Google OAuth。

## 查询命令

- `--ga4 --request FILE`
- `--gsc --request FILE`
- `--gsc-inspect --request FILE`
- `--gsc-sitemaps`
- `--ads --request FILE`
- `--profile`

请求格式见 [references/query-recipes.md](references/query-recipes.md)。

## 分析口径

1. Profile 决定账户 ID、时区和币种，禁止在查询中覆盖。
2. GA4、GSC、Google Ads 先分别核对总计，再连接日期、Campaign 或 URL。
3. GSC clicks、GA4 sessions、Ads clicks 不是同一指标。
4. GA4 用户漏斗优先 `totalUsers`；GSC CTR 用 clicks / impressions 重算；Ads 花费用 cost_micros 转换。
5. 说明时区、数据延迟、归因与样本量。
6. 本 Skill 只读，不修改任何 Google 平台或网站。

## 输出

使用中文，先给结论，再给表格、口径与动作建议。行级结果优先 TSV；缺失字段不得编造。
