# 迁移到其他账户

## 迁移原则

Skill 与账户配置完全分离。迁移时不修改 Skill，只替换：

1. `ACCOUNT_PROFILE_JSON`；
2. 组合 Google OAuth Secret；
3. Google Ads Developer Token Secret；
4. 新 Profile 的 Reader Token。

## 一键发现账户信息

使用 [Browser Use 一键账户发现 Prompt](../prompts/browser-use-account-discovery.md)。它会在已登录浏览器中读取非敏感账户信息并生成 `account-profile.json`。

Browser Use 能读取 ID、时区、币种和权限，但不能代替 Google OAuth。用户仍需本人确认一次 OAuth Consent，这是 Google 的安全要求。

## 组合 OAuth Scope

```text
https://www.googleapis.com/auth/analytics.readonly
https://www.googleapis.com/auth/webmasters.readonly
https://www.googleapis.com/auth/adwords
https://www.googleapis.com/auth/cloud-platform
```

如果同一个 Google 账号同时有三套资产权限，可使用一个 Refresh Token。若资产分属不同 Google 账号，v1 建议先把一个专用 Google 用户添加到三套资产；后续多用户版本可为每个数据源保存独立 OAuth Connection。

## Google Ads Developer Token

平台运营方可以共用一个已批准的 Developer Token，客户无需获取。自托管用户则必须在自己的 Manager Account API Center 获取 Developer Token。

## 验收

- `/v1/profile` 返回正确 Profile；
- GA4 返回最近 7 天 sessions；
- GSC 返回最近 7 个完整日 clicks；
- Google Ads 返回最近 7 天 cost_micros；
- 三个接口都无法通过请求覆盖 Profile 中的账号 ID；
- 新 Reader Token 只能访问当前部署的 Profile。
