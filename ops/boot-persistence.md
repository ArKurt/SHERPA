# 开机自恢复

> 断电、重启、系统更新之后，**东西要能自己回来**。
> 这一章的每一条都来自"以为配好了、结果重启后发现没有"。

## 原则

**"我手动跑起来了"和"它能自己起来"是两件完全不同的事。**
只做了前者的系统，在下一次意外断电时会完全消失，而你可能不在家。

## 三类东西要分别处理

| 类别 | 手段 |
|---|---|
| 容器服务 | 容器运行时的重启策略 |
| 原生服务 | 系统的服务管理器 |
| 虚拟机 | 单独处理，最容易被漏 —— 见下 |

## 容器

设置重启策略（`unless-stopped` 或 `always`），并确认**容器运行时本身是开机自启的**。

⚠️ 常见疏漏：容器策略配对了，但容器运行时（Docker Desktop / OrbStack 一类的桌面应用）
需要登录后才启动。于是"重启后服务没回来"，而 `docker ps` 一看又都正常——
因为你是登录之后才去看的。

## 虚拟机（最容易漏）

旁路由跑在 VM 里时，**VM 的自启动往往是最后才被想起来的一环**，
而它偏偏是影响面最大的（它挂了全屋断网）。

### 别让虚拟机进程脱离监管

虚拟机命令行常有一个"后台化/守护化"选项（`-daemonize` 一类）。
用了它，进程会 fork 到后台——**而服务管理器认不认这个新进程，取决于你怎么配它**。

- **systemd 默认的 `Type=simple`**：管理器盯的是它 fork 出来的那个进程。
  程序自己再 fork 一次并退出，管理器就以为服务已经结束，可能立刻再拉起一个——
  **两个实例抢同一块虚拟磁盘。**
- **`Type=forking` + `PIDFile=`**：这是给传统守护进程准备的兼容路径。
  正确的 `PIDFile=` **有助于** systemd 认出主进程——但**这不是保证**：
  路径写错、写入太晚、残留了旧 PID，照样会追错。
  而且 systemd 手册对这个类型的原话是 *"The use of this type is discouraged,
  use notify, notify-reload, or dbus instead."*

**所以正确做法是让虚拟机以前台进程运行，由服务管理器直接持有它**——
不是因为守护化在任何管理器下都必然出事，而是因为前台这条路不需要你把
`Type=` 和 `PIDFile=` 配对，少一个配错就翻车的环节。

macOS 的 launchd 是另一套语义（`KeepAlive` / `RunAtLoad`），按它自己的文档配，
别把 systemd 的结论搬过去。

→ [坑典](../pitfalls/boot-ops.md#两个虚拟机实例抢同一块磁盘)

### 优雅关机

服务管理器发停止信号时，直接杀掉虚拟机等同于**拔电源**——
来宾系统的文件系统可能损坏（这正是 [层 5](../layers/5-storage.md) 里说的那种反复损坏）。

正确做法是先通过虚拟机的管理接口发一个"关机"请求，等来宾自己退出，
超时之后才强制终止。

### 崩溃重启策略

只对**异常退出**重启，不要对正常退出重启——否则你主动关掉它，它又起来了。

## 全盘加密会限制自恢复能力

> 📌 **先分清是哪一套加密。** 下面讲的是 **macOS + FileVault**——本手册见过实例的那套。
> Windows BitLocker 与 Linux LUKS 各有各的解锁与自启动语义（LUKS 还常配 TPM 自动解锁
> 或 initramfs 里的远程解锁），**不要把这一节的结论直接搬过去**，按各自文档核。

**开了 FileVault，重启之后必须有一次 FileVault 身份验证，机器才会继续启动。**
Apple 的说明是：FileVault 打开时自动登录不可用，**必须人工登录**。

**先落到下面这一档，再去谈可用性——别读完整节才做判断：**

| 你这台机器 | 断电/重启之后 |
|---|---|
| Apple 芯片 + macOS 26+，已开「远程登录」、网络可达 | **可以远程解锁**（SSH），不必到场 |
| 你主动发起的那一次重启，事先跑了 `fdesetup authrestart` | 这一次免解锁 |
| 其它情况（Intel、更早的系统、没开远程登录） | **要有人到场解锁** |

在解锁完成之前，**正常系统和依赖加密卷的服务都还没起来**——
你的相册、代理、常驻 harness 一个都不在。

所以：

- **"没人做任何操作、旁路由也自己回来"这个承诺给不了**
- 计划外断电之后，机器不会自己回到可用状态
- 远程重启是**要先想清楚的操作**——落在上表第三档的话，它会停在那儿等人，而你进不去

⚠️ **"那我把它做成系统级服务（LaunchDaemon）不就绕过去了？"——绕不过去。**
卡住的不是用户会话，是**解锁本身**，整个启动都排在它后面。
换成系统级只改变服务在启动完成后什么时候起，不改变启动能不能开始。

### 上表两档例外的依据

- **SSH 远程解锁**：Apple 原文 *"On a Mac with Apple silicon with macOS 26 or later,
  FileVault can be unlocked over SSH after a restart if Remote Login is turned on and a
  network connection is available."*
  ⚠️ 它推翻的是"必须有**人到场**"，**不是**"断电后会自己恢复"——
  仍然需要一个人去远程解锁，只是不必到机器跟前。
- **`fdesetup authrestart`**：得在机器还开着、你有凭证的时候执行。**救不了计划外断电。**

📌 差别很实在：落第一档是"断电后有人远程点一下就回来"，
落第三档是"断电后必须有人回家"。**部署前就要问清楚这台机器在哪一档。**

**部署前就要告诉用户这个限制**，而不是等第一次断电后才发现。

## 睡眠

如果这台机器要给别人当网关或跑自动化：**它睡了，依赖它的东西就断了。**

睡眠策略必须先解决。低功耗和常驻可用互相拉扯，
要么明确选一边，要么把两类职责分到不同机器上。

### 错过的定时任务，会不会补跑？

**这是个二维问题，别压成一句话。** 两个维度是：**机器当时是睡着还是关机**，
以及**你用的是哪一类调度**。手册这里前后写错过两次，就是因为把它压成了一维。

| 调度 | 睡眠期间错过 | 关机期间错过 |
|---|---|---|
| `cron` | ❌ 跳过 | ❌ 跳过 |
| launchd · `StartCalendarInterval` | ✅ **唤醒时跑** | ❌ 不跑 |
| launchd · 其它调度键 | ❌ 跳过 | ❌ 跳过 |
| systemd · `OnCalendar=` timer | ✅ **恢复后补上** | ❌ 不跑，除非 `Persistent=true` |
| systemd · 单调 timer（`OnUnitActiveSec=` 一类） | 按各自语义 | `Persistent=` **对它无效** |

三条原文，都值得记住：

- **launchd**：*"If you schedule a launchd job by setting the `StartCalendarInterval` key
  and the computer is asleep when the job should have run, your job will run when the
  computer wakes up."* 但同页紧接着写 *"However, if the machine is off when the job should
  have run, the job does not execute until the next designated time occurs."*
  以及 ***"All other launchd jobs are skipped when the computer is turned off or asleep."***
- **systemd**：*"When a calendar timer elapses while the system is sleeping it will not be
  acted on immediately, but once the system is later resumed it will catch up and process
  all timers that triggered while the system was sleeping."*
- **`Persistent=`**：*"This is useful to catch up on missed runs of the service when the
  system was powered down."* 而且 *"only has an effect on timers configured with `OnCalendar=`"*。

⚠️ **两条最容易搞错的：**

1. **`Persistent=true` 不是"睡眠补跑开关"。** systemd 的日历 timer 睡醒本来就会补，
   `Persistent=` 管的是**关机**（或 timer 单元不活跃）期间的遗漏。
   为了解决睡眠补跑去加这个开关，等于加了个不解决问题的东西。
2. **"补跑"不等于"一次不落"。** launchd 明说多次错过 *"coalesced into one event"*，
   systemd 明说 *"only result in a single service activation"*。
   幂等的清理任务无所谓；**"每小时同步一次增量"这种，合并就是丢数据**。

📌 **所以验收要按你实际的那一格设计**——先确认"机器是睡还是关"、"用的哪类调度"，
再去测。测错了格子，结论没有意义。

## 挂载依赖

服务启动时外接盘/网络挂载可能还没就绪。症状是服务起来了但看不到数据，
有些服务还会因此**创建一个空的数据目录**，把事情搞得更糟。

需要显式的挂载依赖或启动前等待。

## 验收

配完之后**必须真的重启一次验证**。见 [`cold-start-acceptance.md`](cold-start-acceptance.md)。

不重启验证的自启动配置，等于没配。

---

> 📎 **本页断言的出处与强度**：[`appendix/sources.md`](../appendix/sources.md#ops-boot-persistence)
