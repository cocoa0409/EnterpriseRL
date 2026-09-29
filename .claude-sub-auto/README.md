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
| `~/.claude-sub/cc-sub` | `cc-sub-auto` 以模块方式导入它的探测和表格代码；分配规则见下文，比 `cc-sub` 多了两道额度门槛和并发上限 |

本目录只有三个文件：`cc-sub-auto`（脚本）、`README.md`、`.bashrc`（alias 片段）。运行后会多出
`~/.claude-sub-auto/auto.log`（记录每一次启动、切换、等待和退出）和 `.pick.lock`（选号锁）。

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
cc-sub-auto                       # 自动分配账号启动，之后自动换号
cc-sub-auto --use 3               # 第一次启动强制账号 3（换号时不再受此限制）
cc-sub-auto --min-weekly-left 10  # 周额度剩余低于此百分比的账号不做候选，默认 10
cc-sub-auto --min-5h-left 20      # 5 小时额度剩余低于此百分比的账号不做候选，默认 20
cc-sub-auto --max-per-account 2   # 一个账号上最多几个 claude 会话，默认 2
cc-sub-auto --poll 60             # 运行中多久探测一次当前账号，默认 60 秒（下限 15）
cc-sub-auto --wait 300            # 没有可分配账号时多久重扫一次，默认 300 秒（下限 30）
cc-sub-auto -c                    # 接续本目录最近的会话，之后照常自动换号
cc-sub-auto -p "..."              # 无头模式；撞限流退出后自动换号重跑
cc-sub-auto --model claude-fable-5-1 --effort max   # 覆盖默认模型 / effort
```

不带 `--model` / `--effort` 时默认传 `--model claude-opus-5-5 --effort high`（脚本里的 `DEFAULT_MODEL` /
`DEFAULT_EFFORT`，与 `cc-sub` 默认的 Fable 5.1 不同）。会话内 `/model` 照常可用。

其余参数原样透传给 `claude`。`--session-id` / `--resume` / `-c` 由 `cc-sub-auto` 接管：
第一次启动它自己生成一个会话 id 传给 `claude --session-id`，之后每次换号都 `--resume` 这个 id，
所以同目录多开也不会接错会话。

## 账号怎么分配

第一次启动和每次换号走同一条规则：

1. 探测全部账号，去掉探测失败的和 `rejected` 的；
2. 去掉周额度剩余 < `--min-weekly-left`% 的，去掉 5 小时额度剩余 < `--min-5h-left`% 的；
3. 去掉本机上已经有 `--max-per-account` 个 `claude` 会话在用的（从活着的 `claude` 进程的
   `CC_SUB_ACCOUNT` 环境变量数出来，普通 `cc-sub` 开的会话也算）；
4. 剩下的按"在用会话数最少 → 5 小时剩余最多 → 周剩余最多"排序，取第一个。

"探测 → 选号 → 拉起 claude"这一段持有 `~/.claude-sub-auto/.pick.lock` 文件锁，同时启动的多个
`cc-sub-auto` 会排队，后一个数会话时一定能看见前一个刚拉起的进程，所以 10 个并发会摊到 10 个账号上，
而不是一起挤到最空的那个。表格里每个账号都标明它是候选、被选中，还是因为哪条规则被排除。

## 运行时发生什么

**账号在会话中途用尽（最常见）**
1. 每 `--poll` 秒对当前账号发一次 1-token 的 Haiku 探测（和状态栏用的是同一个请求）。
   被限流的账号探测会被拒，但响应头里仍带状态，不额外消耗额度。
2. 状态变成 `rejected` 后，向 `claude` 发 SIGTERM（10 秒不退再 SIGKILL）。
3. 重探全部账号，按"账号怎么分配"一节的规则选一个，
   `claude --resume <同一会话id> "<接续提示>"` 重新拉起。接续提示是一段英文，告诉模型：上一条请求因额度中断，
   从中断处继续，最后一次没结果的工具调用重做，已完成的不要重复。
4. 你看到的是：画面闪一下，`claude` 带着完整历史在新账号上打开，模型自己接着干。

**没有可分配的账号**
屏幕上打印"no account is allocatable (N rate-limited, M busy …) · re-scanning in Ns · earliest reset: acct X in …"，
然后等待 `--wait` 秒重扫，直到出现候选账号就自动接续。等待期间不持锁。Ctrl+C 退出等待。

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

`~/.claude-sub-auto/auto.log`，每行一个事件，方括号里是 supervisor 的 pid，多开时用它区分：

```
2026-09-20 07:32:45  [4711] launching on acct 2 (live 0) · session 8ef9ec95-… · attempt 0
2026-09-20 07:33:39  [4711] acct 2 rejected while running (5h reset 0h59m, …); stopping claude
2026-09-20 07:33:40  [4711] switch away from acct 2 (rc=143, killed=True) · resume 8ef9ec95-…
2026-09-20 07:33:41  [4711] none allocatable (10 rate-limited, 1 busy (2 sessions)); waiting 300s · earliest reset: acct 5 in 0h59m
2026-09-20 07:38:42  [4711] resuming on acct 5 (live 0) · session 8ef9ec95-… · attempt 1
2026-09-20 08:10:03  [4711] exit rc=0: claude exited rc=0 on acct 5; account not limited
```

每一种退出（正常结束、Ctrl+C、找不到 transcript、未捕获异常）都会写一行 `exit` 或 `crash`。

`killed=False` 表示 `claude` 自己退出后才发现账号已限流（用户退出或 `-p` 失败）；
`killed=True` 表示是后台探测发现限流后主动停掉的。

## 想要完全隔离的环境？

把 `cc-sub-auto` 里 `run_claude()` 的 `"CLAUDE_CONFIG_DIR": SUB_DIR` 改成别的目录即可，
账号清单和探测代码仍从 `~/.claude-sub/` 读。代价是会话、skills、plugins 和 `cc-sub` 不再共享，
状态栏也要在新目录的 `settings.json` 里重新接。
