# 安全设计

- Skill、Prompt、Profile 和 GitHub Release 不包含真实 Token。
- Account Profile 只保存非敏感 ID、时区、币种和名称。
- OAuth Refresh Token、Developer Token 和 Reader Token 只保存在 Secret Manager。
- 一个部署绑定一个 Profile；调用方不能在请求中覆盖账号 ID。
- Google Ads 仅允许单条 GAQL `SELECT`，拒绝写入词和超大结果。
- GSC URL Inspection 限制在 Profile Property 范围内。
- GA4 Report 自动移除请求中的 Property 字段。
- 对请求大小、日期范围、维度、筛选器和返回行数设置上限。
- 生产环境应为不同客户生成不同 Reader Token，并记录轮换时间。
