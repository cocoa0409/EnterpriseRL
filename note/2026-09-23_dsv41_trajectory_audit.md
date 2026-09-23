# DS V4.1 真实轨迹审计：转换前任务的问题定位

运行结果：`/home/ubuntu/github/enterprise_rl/jobs/dsv41_max_30tasks_16runs`

实际使用的任务快照：`/home/ubuntu/github/enterprise_rl/env_cache/harbor_tasks`。该快照包含 See also hint，与后来重新转换的无 hint 版本不同。30 个任务的 checksum 均与运行记录一致。

下面以 **转换前 `/home/ubuntu/github/enterprise_rl/env/` 下的任务 JSON 绝对路径**定位。任务编号采用文件名中的 0-based 编号。

审计结论：确认一处任务需求与评分目标冲突，以及另一道题的客户模拟器披露时序问题。两者性质不同：前者应修任务设计，后者是运行中客户模拟器未稳定遵守场景要求，不能认定该题标准答案错误。

## 1. 宴会结算 task 1：财务邮箱副本需求与标准答案冲突

**转换前任务绝对路径：**

`/home/ubuntu/github/enterprise_rl/env/env_0013_workplace_dining_and_catering_provider/tasks/banquet_event_desk/tasks/1.json`

**问题位置：**

- [user_scenario，第 4 行](/home/ubuntu/github/enterprise_rl/env/env_0013_workplace_dining_and_catering_provider/tasks/banquet_event_desk/tasks/1.json:4)：最后一段要求客户在付款记录完成后询问副本是否会送到财务邮箱，并接受肯定答复。原句包含 “asks whether a copy will reach the finance mailbox, takes a yes”。
- [evaluation_criteria，第 984 行起](/home/ubuntu/github/enterprise_rl/env/env_0013_workplace_dining_and_catering_provider/tasks/banquet_event_desk/tasks/1.json:984)：标准答案只覆盖开具最终账单和客户付款，没有副本发送或转人工动作。
- [agent 系统提示，第 64 行](/home/ubuntu/github/enterprise_rl/rollout/prompts.py:64)：没有政策覆盖的请求必须转人工。
- [场景共享工具，第 543 行](/home/ubuntu/github/enterprise_rl/env/env_0013_workplace_dining_and_catering_provider/blueprint/share_tools.py:543)：`transfer_to_human_agent` 会写入 `handoff_log`。

**为什么是问题：**

任务知识库和工具没有提供向财务邮箱发送结算副本的流程。客户却必须追问该事项，agent 按系统提示转人工后，会产生标准答案中没有的 `handoff_log`。评分比较整个数据库，因此业务结算正确也会失败。

这会让遵守转人工要求的轨迹失败，而未转人工、仅口头拒绝副本请求的轨迹可能通过，评价目标不一致。

**真实轨迹证据：**

[amJfRcU 的对话](/home/ubuntu/github/enterprise_rl/jobs/dsv41_max_30tasks_16runs/env_0013_workplace_dining_and_ca__amJfRcU/agent/transcript.json)中，agent 正确开票 **143,520.00**，客户正确支付 **68,045.00**。随后客户问财务邮箱副本，agent 用 `POLICY_NOT_COVERED` 转人工，最终 reward=0。

独立回放确认，有 **9/16 条轨迹**的最终数据库与标准答案的唯一差别就是该转接记录。对应 trial 后缀为：

`amJfRcU`、`DCu2WTJ`、`YtMnvto`、`cCE92LF`、`oDkRfed`、`usPBy3w`、`GEyZnEA`、`JvPd8qc`、`vk54Dcb`。

这些 trial 均位于上述运行目录，前缀为 `env_0013_workplace_dining_and_ca__`。该题原始成绩为 **5/16**。

成功对照：[Aogri56](/home/ubuntu/github/enterprise_rl/jobs/dsv41_max_30tasks_16runs/env_0013_workplace_dining_and_ca__Aogri56/agent/transcript.json)。结算正确，口头拒绝发送副本，没有写入转接记录，reward=1。

**建议修改：**

若测试目标只包含宴会结算，删除 `user_scenario` 最后一段中的财务邮箱副本请求，改为客户确认付款已记录后结束通话。若需要保留副本需求，应补齐政策、操作及标准答案。不要直接忽略所有 `handoff_log`，否则会放过无理由转人工。

## 2. 餐饮取消 task 1：客户在写入后才披露关键渠道，或漏掉该事实

**转换前任务绝对路径：**

`/home/ubuntu/github/enterprise_rl/env/env_0013_workplace_dining_and_catering_provider/tasks/catering_order_desk/tasks/1.json`

**问题位置：**

- [user_scenario，第 4 行](/home/ubuntu/github/enterprise_rl/env/env_0013_workplace_dining_and_catering_provider/tasks/catering_order_desk/tasks/1.json:4)：最后一段规定，在 agent 需要客户自己执行操作时，客户说明该取消通过具名 catering account manager 提交，再询问和读回参数并执行。
- [evaluation_criteria，第 1803 行](/home/ubuntu/github/enterprise_rl/env/env_0013_workplace_dining_and_catering_provider/tasks/catering_order_desk/tasks/1.json:1803)：取消操作的正确 `order_channel` 为 `account_manager`。
- [原始 task_tools.py，第 121 行](/home/ubuntu/github/enterprise_rl/env/env_0013_workplace_dining_and_catering_provider/tasks/catering_order_desk/task_tools.py:121)：参数定义明确区分经过 account manager 的指令和直接打给服务台、未经过其他人的 `phone`。

**为什么是问题：**

渠道决定取消通知时间的计算，继而影响取消费。客户模拟器没有稳定按场景要求在执行前披露关键事实：有时直接按 agent 给出的 `phone` 写入，然后才提 account manager；有时直到结束都未提。

这是客户模拟器执行场景的可靠性问题。现有场景和标准答案对正确渠道本身是一致的；agent 没有主动澄清也可能参与导致失败，不能把这些轨迹全部当作 agent 本应成功的结果。

**真实轨迹分布：**

| Trial 后缀 | 实际行为 | 判断 |
|---|---|---|
| `N49mrsR`、`o3KvJsf` | 执行时写入 phone，直到结束未披露 account manager | 客户遗漏关键事实 |
| `xCdXumP`、`f3rLqCS`、`EsK4VfH` | 先写入 phone，执行后才披露 account manager | 客户披露过晚 |
| `sU3xkq3` | 执行前已披露，但 agent 仍保留 phone | agent 判断错误，不属于客户遗漏 |

这些 trial 均位于上述运行目录，前缀为 `env_0013_workplace_dining_and_ca__`。该题 **10/16** 通过；6 条失败轨迹均写入了 phone，其中 5 条存在上述遗漏或延迟披露。

代表证据：[f3rLqCS 的对话](/home/ubuntu/github/enterprise_rl/jobs/dsv41_max_30tasks_16runs/env_0013_workplace_dining_and_ca__f3rLqCS/agent/transcript.json)。客户先执行 phone 渠道的取消，再说明通过 account manager 提交。agent 随后将取消费改成正确的 **1,409.29**，但已经写入的渠道仍错误。该轨迹与标准答案的业务动作参数唯一差别是 `order_channel`。

**建议修改：**

强化 `user_scenario` 的交接时序：在第一次执行取消工具前，必须先说明 account manager 事实并读回参数；若给出的渠道与该事实冲突，先报告冲突，等待 agent 重新交接，再执行。客户应继续遵守“使用 agent 明确给出的参数”，不要自行改参数。

## 3. 五道零通过 HARD 题：目前证据主要指向 agent 漏步骤

以下题目也已审查，但**未因零通过率认定为任务 bug**。列出转换前路径，避免把它们和上面两类问题混淆。

| 转换前任务绝对路径 | 16 条轨迹中观察到的问题 |
|---|---|
| `/home/ubuntu/github/enterprise_rl/env/env_0004_ski_resort_operator/tasks/equipment_rental_desk/tasks/0.json` | 13 次未让客户结清租赁余额；5 次未评估损伤；3 次未登记晚还费用，计数可重叠。 |
| `/home/ubuntu/github/enterprise_rl/env/env_0015_car_sharing_marketplace/tasks/host_protection_and_claims_desk/tasks/0.json` | 10 次未进行损失评估；14 次未登记 host share。 |
| `/home/ubuntu/github/enterprise_rl/env/env_0015_car_sharing_marketplace/tasks/host_protection_and_claims_desk/tasks/1.json` | 11 次未恢复保障；11 次未登记维修补充；1 次未撤回客户自己的索赔。 |
| `/home/ubuntu/github/enterprise_rl/env/env_0015_car_sharing_marketplace/tasks/vehicle_listing_desk/tasks/0.json` | 16 次未记录车辆缺陷；15 次未重估车辆；15 次未重新划分价值等级。 |
| `/home/ubuntu/github/enterprise_rl/env/env_0015_car_sharing_marketplace/tasks/vehicle_listing_desk/tasks/1.json` | 16 次都跳过登记文件验证、完成检查、登记平台里程，直接让客户报里程。 |

车辆里程 task 1 的前置规则在 **16/16 条实际检索输出中均出现**，但模型仍全部直接提交 `reported_miles_consumed=635`；完成前置步骤后应为 40。这不是“检索没有返回规则”的证据。

## 4. 审计边界和执行层结果

- 全量独立回放 480 条轨迹：标准答案 hash、实际动作 replay、保存的 final_db 与原评分全部一致。
- 交叉核对 14,577 次工具调用：状态日志、对话事件和评分轨迹一致，双方 tool_call_id 配对无缺失。
- 人工检查重点问题题目和成功对照；未逐字阅读全部 17,904 次模型生成，也未对全部政策进行独立数学证明。
- 7 次 agent 生成耗尽 32,768 token，仅有思考、无可见回答，后续对话继续；其中最终 2 成功、5 失败。这是运行预算限制，不能直接归因成题目或评分 bug。
- 本次只记录审计结论，未修改原始任务、历史轨迹或原始分数。

完整审计：[trajectory_audit.md](/home/ubuntu/github/enterprise_rl/jobs/dsv41_max_30tasks_16runs/trajectory_audit.md)。全量动作与数据库差异：[trajectory_audit_data.json](/home/ubuntu/github/enterprise_rl/jobs/dsv41_max_30tasks_16runs/trajectory_audit_data.json)。
