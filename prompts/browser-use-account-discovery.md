# Browser Use 一键账户发现 Prompt

将下面整段提示词复制给支持 Browser Use、Chrome Control 或其他已登录浏览器操作能力的智能体，只需替换目标品牌和网站。

```text
你现在需要为 Growth Data Reader 创建一个可迁移的 Google 数据账户 Profile。

目标品牌：[填写品牌名称]
目标网站：[填写网站，例如 https://example.com]

请使用 Browser Use 或当前可用的浏览器控制工具，在我已经登录的 Google 会话中，以只读方式完成 GA4、Google Search Console、Google Ads 和 Google Cloud 的账户信息发现。

安全要求：
1. 只读取页面，不修改账户、权限、预算、广告、转化、数据流、Sitemap、Cloud 项目或 API 设置。
2. 不读取、复制或输出密码、Cookie、Local Storage、OAuth Access Token、Refresh Token、Developer Token、Reader Token、API Key 或完整认证请求头。
3. 不把任何敏感值写入聊天、文件或终端。
4. 如果需要 Google OAuth，只生成后续授权所需的 scope 和操作说明，不替我绕过授权。
5. 如果同一平台存在多个可能匹配的账户，请列出候选名称与非敏感 ID，让我选择一次后继续，不要自行猜测。

请按下面流程执行：

A. GA4
- 打开 Google Analytics。
- 找到与目标网站匹配的 Account、GA4 Property 和 Web Data Stream。
- 收集 Account 名称与 Account ID、Property 名称与 Property ID、API Property Name（properties/数字）、Property 时区、币种、Data Stream 名称、Stream ID、Measurement ID。
- 确认当前登录账号至少可以查看该 Property。

B. Google Search Console
- 打开 Search Console。
- 找到目标网站对应的 Domain Property 或 URL-prefix Property。
- 收集精确 siteUrl，例如 sc-domain:example.com 或 https://example.com/。
- 收集当前权限等级；确认可以查看 Performance 数据。

C. Google Ads
- 打开 Google Ads。
- 找到与目标品牌匹配的客户账号。
- 收集客户账号名称、Customer ID（输出时去掉连字符）、账号时区和币种。
- 判断当前账号是直接访问还是通过 Manager Account 访问。
- 如通过 MCC，收集 Login Customer ID（去掉连字符）；直接访问则留空。
- 只记录 Google Ads API Access Level 是否为 Explorer、Basic 或 Standard，不显示 Developer Token。

D. Google Cloud
- 打开 Google Cloud Console 项目选择器。
- 找到计划用于部署 Reader Gateway 的 Project ID；如果没有明确项目，标记“需创建或选择”，不要自行创建。
- 检查以下 API 是否已启用，仅报告状态，不进行启用：Google Analytics Data API、Search Console API、Google Ads API、Cloud Run、Secret Manager、Cloud Build。

E. 生成文件
- 在当前工作目录创建 output/account-profile.json，只保存非敏感信息。
- 在当前工作目录创建 output/account-discovery-report.md，记录候选项、最终选择、权限检查、缺失项和下一步授权动作。
- 不要在文件中保存 Token、密码、Cookie 或 OAuth JSON。

account-profile.json 必须使用以下结构：
{
  "profileId": "品牌英文小写-市场",
  "displayName": "品牌与市场名称",
  "website": "https://example.com",
  "ga4": {
    "accountId": "accounts/数字",
    "propertyName": "properties/数字",
    "propertyDisplayName": "Property 名称",
    "timezone": "GA4 时区",
    "currency": "GA4 币种",
    "streamId": "Stream ID",
    "measurementId": "G-XXXXXXXXXX"
  },
  "gsc": {
    "siteUrl": "sc-domain:example.com",
    "permissionLevel": "权限等级"
  },
  "googleAds": {
    "customerId": "10位数字",
    "loginCustomerId": "10位数字或空字符串",
    "descriptiveName": "广告账号名称",
    "timezone": "广告账号时区",
    "currency": "广告账号币种",
    "apiAccessLevel": "Explorer/Basic/Standard/需确认"
  },
  "deployment": {
    "googleCloudProjectId": "Project ID 或需确认",
    "requiredOAuthScopes": [
      "https://www.googleapis.com/auth/analytics.readonly",
      "https://www.googleapis.com/auth/webmasters.readonly",
      "https://www.googleapis.com/auth/adwords",
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

完成后请输出：
1. 一句话结论：三渠道是否全部具备迁移条件。
2. 已确认信息表。
3. 缺失信息和对应页面位置。
4. 需要用户本人完成的授权动作。
5. 两个生成文件的绝对路径。

不要只给操作教程；请实际使用浏览器读取并生成文件。
```
