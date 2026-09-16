# cc-sub：Claude Code 多订阅账号管理

`cc-sub` 在多个 Claude 订阅账号之间自动挑选**额度最充裕**的一个来启动 Claude Code。
它把整套配置隔离在 `~/.claude-sub/`（通过 `CLAUDE_CONFIG_DIR`），不碰默认的 `~/.claude`，
也不受 `~/.bashrc` 里 `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL` 那套代理网关配置的影响。

本目录是 `~/.claude-sub` 的**核心文件摘录**，用来在一台新机器上从零复原这套环境。

## 目录里有什么

| 文件 | 作用 | 是否要改 |
|---|---|---|
| `cc-sub` | 启动器本体（单文件 Python 3 脚本，只依赖 `curl`） | 换机器时可能要改顶部的代理常量 |
| `settings.json` | 放进 `~/.claude-sub/` 的 Claude Code 设置（状态栏、模型 effort、主题等） | `statusLine.command` 里的绝对路径要改成你的家目录 |
| `accounts.txt` | 账号清单：每行 `名字  token`。**这里的是示例格式，token 是私密数据** | 必须换成你自己的 token |
| `.bashrc` | 要追加到 `~/.bashrc` 的 alias 片段 | 不用改 |

`~/.claude-sub/` 运行后会多出 `.claude.json`、`status.json`、`projects/`、`sessions/`、
`plugins/`、`history.jsonl`、`backups/` 等，全部是运行时自动生成的，不需要从这里拷贝。

## 前置条件

- 已安装 Claude Code CLI，`claude --version` 能跑（本机是 2.1.x）
- `python3`（3.8+）和 `curl`
- 机器能访问 `api.anthropic.com`。`cc-sub` 顶部有两个常量 `PROXY` 和 `NO_PROXY`，
  分别是探测和启动时使用的 HTTP 代理地址与免代理列表。按你所在网络环境填写；
  如果直连可达，`PROXY` 留空并把 `probe()` 里 `curl` 的 `-x PROXY` 参数去掉。

## 从零初始化（新机器）

### 1. 拷贝核心文件

在本目录下执行：

```bash
mkdir -p ~/.claude-sub/backups
cp cc-sub settings.json ~/.claude-sub/
chmod 700 ~/.claude-sub/cc-sub
```

不要直接拷 `accounts.txt`，下一步自己生成。

### 2. 修正 settings.json 里的路径

`statusLine.command` 是绝对路径，指向摘录来源机器的家目录。换成你的家目录：

```bash
sed -i -E "s|/home/[^/]+/\.claude-sub|$HOME/.claude-sub|g" ~/.claude-sub/settings.json
```

或者把 `statusLine` 这个键整个删掉，`cc-sub` 第一次启动时会用正确路径自动补上。

其他键的含义：

- `model: "opus"`：只是兜底。`cc-sub` 启动时总会传 `--model claude-fable-5-1`（见脚本里的 `DEFAULT_MODEL`），
  因为 `/model` 选择器不列 Fable 且会改写这个键。
- `modelSettings.*.effortLevel: "high"`：Fable 5.1 / Opus 5 默认高 effort。
- `skipDangerousModePermissionPrompt: true`：配合 alias 里的 `--dangerously-skip-permissions`，不再弹确认。

### 3. 为每个账号生成长期 OAuth token

在**任意一台能开浏览器的机器**上，对每个订阅账号执行一次：

```bash
claude setup-token
```

按提示在浏览器里登录该账号，终端会打印：

```
Your OAuth token (valid for 1 year):
 sk-ant-oat01-xxxxxxxx...
```

复制整段 `sk-ant-oat01-...`（108 个字符，终端折行了要拼回去）。一年后过期，需重新生成。

### 4. 写 accounts.txt

```bash
cat > ~/.claude-sub/accounts.txt <<'ACC'
# name    token        (one per line; lines starting with # are ignored)
1   sk-ant-oat01-...
2   sk-ant-oat01-...
ACC
chmod 600 ~/.claude-sub/accounts.txt
```

- `name` 是任意标识，纯数字时表格按数值排序（1, 2, …, 10）；建议就用递增数字。
- 名字和 token 之间任意空白分隔。
- 以后加账号直接追加一行即可，无需重启任何东西。

### 5. 加 shell alias

把本目录 `.bashrc` 的内容追加到 `~/.bashrc`：

```bash
cat .bashrc >> ~/.bashrc && source ~/.bashrc
```

内容就一行：

```bash
alias cc-sub="~/.claude-sub/cc-sub --dangerously-skip-permissions"
```

### 6. 验证

```bash
cc-sub --list
```

会并发探测所有账号（每个账号一次 1-token 的 Haiku 请求）并打印两张表：

```
cc-sub · 11 accounts · probed 10:19:50 · 0 with ≥ 75% week left

● usable (6)
┌──────┬────────────────────────┬───────────────────────────┬────────────────┐
│ acct │ 5h left · reset        │ week left · reset         │ status         │
├──────┼────────────────────────┼───────────────────────────┼────────────────┤
│ ➜ 3  │ ▰▰▰▰▰▰▰▰▰▰ 100% ↻0h50m │ ▰▱▱▱▱▱▱▱▱▱   5% ↻1d07h40m │ ▲ near limit   │
│   6  │ ▰▰▰▰▰▰▰▰▱▱  84% ↻0h50m │ ▰▰▰▰▰▰▰▱▱▱  67% ↻5d17h40m │ ● ok           │
└──────┴────────────────────────┴───────────────────────────┴────────────────┘

✖ rate-limited (5) · refused until the window resets
┌──────┬────────────────────────┬───────────────────────────┬────────────────┐
│   2  │ ▰▰▰▰▰▰▰▰▰▰ 100% ↻4h50m │ ▱▱▱▱▱▱▱▱▱▱   0% ↻0d10h40m │ ✖ rate-limited │
└──────┴────────────────────────┴───────────────────────────┴────────────────┘
```

- `➜` 标记的是本次会选中的账号。
- 某行显示 `ERR HTTP 401 (bad token?)` 说明 token 失效或拼错；`ERR curl: ...` / `timeout` 说明代理不通。
- 两个账号的用量和重置时间完全一样，通常意味着它们属于同一个组织、共享同一份配额。

### 7. 启动

```bash
cc-sub                       # 自动选号，启动 claude
cc-sub --use 3               # 强制用账号 3
cc-sub --min-weekly-left 50  # 把周额度门槛从 75% 放宽到 50%
cc-sub -p "hello"            # 其余参数原样透传给 claude
```

第一次启动时 `cc-sub` 会在 `~/.claude-sub/.claude.json` 写入 `hasCompletedOnboarding: true`，
跳过 Claude Code 的交互式引导（否则即使给了 token 也会弹登录选择）。

## 选号规则

1. 先筛掉当前 `rejected`（被限流）和探测失败的账号；
2. 剩下的里保留周剩余 ≥ `--min-weekly-left`（默认 75%）的；
3. 在其中选 5 小时窗口剩余最多的，平手看周剩余；
4. 没人过周额度门槛时，退而求其次选最好的那个，并打印黄色提示。

数据来源是 API 响应头 `anthropic-ratelimit-unified-{status,5h-utilization,7d-utilization,5h-reset,7d-reset}`。

## 状态栏

`settings.json` 把 Claude Code 的状态栏接到 `cc-sub --statusline`，显示：

```
acct 7 │ near limit │ 5h ▰▰▰▰▰▱▱▱▱▱ 47% ↻2h23m │ wk 19% ↻3d02h43m │ Fable 5.1 │ ctx 12%
```

样本超过 5 分钟会在后台自动重探当前账号（`cc-sub --refresh NAME`），结果写到 `status.json`。
这两个子命令是内部用的，不需要手动调。

## 运行时机制速查

- `CLAUDE_CONFIG_DIR=~/.claude-sub`：会话、历史、插件全部落在这里，和 `~/.claude` 互不干扰。
- 启动前从环境里剔除 `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL` / `ANTHROPIC_MODEL` / `ANTHROPIC_AUTH_TOKEN`，
  改为设置 `CLAUDE_CODE_OAUTH_TOKEN=<选中账号的 token>` 和 `HTTPS_PROXY`。
- `CC_SUB_ACCOUNT=<名字>` 传给子进程，状态栏靠它知道当前是哪个号。

## 安全注意

- `accounts.txt` 里是**一年有效的账号凭证**，等同密码。保持 `chmod 600`，不要提交到 git。
  本目录位于 git 仓库内且未被 `.gitignore` 覆盖，提交前务必确认没把它加进去
  （建议在仓库 `.gitignore` 加一行 `.claude-sub/accounts.txt`）。
- 改 `cc-sub` 或 `accounts.txt` 前先备份到 `~/.claude-sub/backups/`，脚本自身不会自动备份。
