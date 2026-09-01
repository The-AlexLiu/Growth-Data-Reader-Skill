# WorkBuddy First Use

管理员将以下值配置为项目或团队级持久化 Secret：

```text
GROWTH_DATA_API_URL=https://YOUR_GATEWAY_URL
GROWTH_DATA_READER_TOKEN=<Reader Token>
```

不要仅放入聊天、Prompt、临时终端环境变量或沙箱主目录。会话重建后临时值可能消失。

验证：

```bash
python3 scripts/growth_data_reader.py --profile
```

应返回 Profile ID，以及已配置的 GA4、GSC、Google Ads 三个数据源。
