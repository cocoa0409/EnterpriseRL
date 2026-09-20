# cc-sub-auto：限流时自动换号并接续会话

`cc-sub-auto` 是 `cc-sub` 的守护版。`cc-sub` 只在启动时挑一个额度最充裕的账号，之后就把自己替换成
`claude`；`cc-sub-auto` 启动 `claude` 后**留在后台盯着当前账号**，额度用尽时自动停掉 `claude`、
换到额度最多的账号、用 `--resume` 接上**同一个会话**，并告诉模型从中断处继续。全程不需要人操作。

它不是另一套环境，而是复用 `~/.claude-sub/` 的一切：

| 复用项 | 说明 |
|---|---|
| `~/.claude-sub/accounts.txt` | 同一份账号清单，不用再抄 token |
| `CLAUDE_CONFIG_DIR=~/.claude-sub` | 会话、历史、skills、plugins 全部共用；`cc-sub` 和 `cc-sub-auto` 开的会话互相都能 `--resume` |
| 状态栏 | 还是 `cc-sub --statusline`，`acct N` 和额度条照常显示，切换后自动变成新账号 |
| `~/.claude-sub/cc-sub` | `cc-sub-auto` 以模块方式导入它的探测、选号、表格代码，选号规则完全一致 |

本目录只有三个文件：`cc-sub-auto`（脚本）、`README.md`、`.bashrc`（alias 片段）。运行后会多出
`~/.claude-sub-auto/auto.log`，记录每一次切换。

## 安装

前置条件：`cc-sub` 已按 `../.claude-sub/README.md` 装好并能 `cc-sub --list`。

```bash
mkdir -p ~/.claude-sub-auto
cp cc-sub-auto ~/.claude-sub-auto/ && chmod 700 ~/.claude-sub-auto/cc-sub-auto
cat .bashrc >> ~/.bashrc && source ~/.bashrc
cc-sub-auto --list        # 应打出和 cc-sub --list 一样的两张表
```

## 用法

```bash
cc-sub-auto                       # 自动选号启动，之后自动换号
cc-sub-auto --use 3               # 第一次启动强制账号 3（换号时不再受此限制）
cc-sub-auto --min-weekly-left 50  # 选号的周额度门槛，默认 75%
cc-sub-auto --poll 60             # 运行中多久探测一次当前账号，默认 60 秒（下限 15）
cc-sub-auto --wait 300            # 全部账号限流时多久重探一次，默认 300 秒（下限 30）
cc-sub-auto -c                    # 接续本目录最近的会话，之后照常自动换号
cc-sub-auto -p "..."              # 无头模式；撞限流退出后自动换号重跑
```

其余参数原样透传给 `claude`。`--session-id` / `--resume` / `-c` 由 `cc-sub-auto` 接管：
第一次启动它自己生成一个会话 id 传给 `claude --session-id`，之后每次换号都 `--resume` 这个 id，
所以同目录多开也不会接错会话。

## 运行时发生什么

**账号在会话中途用尽（最常见）**
1. 每 `--poll` 秒对当前账号发一次 1-token 的 Haiku 探测（和状态栏用的是同一个请求）。
   被限流的账号探测会被拒，但响应头里仍带状态，不额外消耗额度。
2. 状态变成 `rejected` 后，向 `claude` 发 SIGTERM（10 秒不退再 SIGKILL）。
3. 重探全部账号，按 `cc-sub` 的规则选一个（排除刚刚用尽的），
   `claude --resume <同一会话id> "<接续提示>"` 重新拉起。接续提示是一段英文，告诉模型：上一条请求因额度中断，
   从中断处继续，最后一次没结果的工具调用重做，已完成的不要重复。
4. 你看到的是：画面闪一下，`claude` 带着完整历史在新账号上打开，模型自己接着干。

**全部账号都限流**
屏幕上打印“every account is rate-limited · re-probing in Ns · earliest 5h reset: acct X in …”，
然后等待。等待时长取 `--wait` 和“最近一个 5 小时窗口重置时间”中较短者。一有账号可用就自动接续。
Ctrl+C 退出等待。

**你自己退出了 claude，而账号恰好已限流**
打印“resuming on another account in 3s · Ctrl+C to quit instead”。不按就自动换号接续，按了就真退出。
账号没限流的正常退出不受影响。

**`-p` 无头模式**
请求被拒导致非零退出时，换号 `--resume` 并重发同一条 prompt；成功结束（退出码 0）不会重跑。

## 代价与限制

- **检测有最多一个 `--poll` 周期的延迟**。这期间 `claude` 会显示限流提示并等待。
- **正在运行的工具会被打断**。限流那一刻若有长命令在跑，`claude` 被停时它也一起结束；
  恢复后模型会看到这个调用没有结果，通常会重跑。账号被拒时它本来也没法完成。
- **接续的第一次请求要重发整个上下文**，一次性消耗新账号一小块 5 小时额度。
- 运行中无法换 token：`CLAUDE_CODE_OAUTH_TOKEN` 只在 `claude` 启动时读一次，`apiKeyHelper` 也只支持
  API key。所以“停掉再拉起”是唯一路径，这也是为什么要有一个守护进程。

## 日志

`~/.claude-sub-auto/auto.log`，每行一个事件：

```
2026-09-20 07:32:45  launching on acct 2 · session 8ef9ec95-… · attempt 0
2026-09-20 07:32:50  switch away from acct 2 (rc=1, killed=False) · resume 8ef9ec95-…
2026-09-20 07:32:51  resuming on acct 1 · session 8ef9ec95-… · attempt 1
2026-09-20 07:33:39  acct 1 rejected while running (5h reset 0h59m, …); stopping claude
```

`killed=False` 表示 `claude` 自己退出后才发现账号已限流（用户退出或 `-p` 失败）；
`killed=True` 表示是后台探测发现限流后主动停掉的。

## 想要完全隔离的环境？

把 `cc-sub-auto` 里 `run_claude()` 的 `"CLAUDE_CONFIG_DIR": SUB_DIR` 改成别的目录即可，
账号清单和探测代码仍从 `~/.claude-sub/` 读。代价是会话、skills、plugins 和 `cc-sub` 不再共享，
状态栏也要在新目录的 `settings.json` 里重新接。
