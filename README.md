# anyserver

**把你手上任何一台机器，变成一台真能用的家庭 / 工作室服务器。**

```
旧笔记本  →  服务器
NAS      →  服务器
迷你主机  →  服务器
```

这不是一份"照着做"的教程，是一份**按你的硬件条件求解**的手册。
它不假设你有什么设备，而是先问你有什么，再给出与之匹配的方案和代价。

## 两条铁律

```
① 只做旁路由，不做软路由。不碰 PPPoE、不接管寻址、不改主路由配置。
② DHCP 只由主路由负责。旁路由不发地址，最多被指为客户端的网关 / DNS。
```

改主路由是这里唯一一类"改错了全家立刻断网、且你连补救的网都没有"的操作。
本手册把它挡在门外。

## 你会得到什么

- **一条适配你硬件的完整路径** —— 而不是照抄别人的配置
- **每一步都有"怎么算成功"** —— 可执行的验收命令，不是"应该能看到"
- **每一步都有回退** —— 且回退不依赖你刚改坏的那条链路
- **一本坑典** —— 二十多个真实踩过的坑，每个都标了"症状看起来像什么"
- **可选的服务菜单** —— 相册、影音、音乐、下载、密码库、家居自动化…按需装

## 怎么开始

**先开 [`wizard.html`](wizard.html)** —— 双击就能打开，不联网、不上传任何东西。
回答三轮问题（大约五分钟），它会生成一份**装机清单**。

```
你 → wizard.html → 装机清单 → 你的 AI 助手 → 这本手册
     问卷、有解释      ↑接口↑        判据、验收、排障
```

**然后把装机清单连同这个仓库交给你的 AI 助手**，让它先读
[`AGENTS.md`](AGENTS.md) —— 那里写着它该怎么用这份手册，
以及**哪些事必须停下来问你**（改错了会全家断网或擦掉硬盘的那些）。

**想自己读**：从 [`00-probe.md`](00-probe.md) 进，不用通读。
出问题了直接查 [坑典](appendix/pitfalls.md)，那是按**症状**索引的。

## 目录

| | |
|---|---|
| [**wizard.html**](wizard.html) | **人从这里进** —— 三轮问卷，生成装机清单 |
| [**00-probe.md**](00-probe.md) | **从这里开始** —— 探测你的环境，产出一个配置向量 |
| [layers/](layers/) | **主干** —— 六层，每层给若干选项和选型判据 |
| [blueprints/](blueprints/) | **三条参考架构** —— 拿你的向量先来这里对号入座（[快速排除表](blueprints/README.md)） |
| [services/](services/) | **服务菜单** —— 全部可选，按需挑 |
| [services/_deployment.md](services/_deployment.md) | 服务怎么摆——目录布局、版本、端口表 |
| [ops/](ops/) | 开机自恢复、冷启动验收、备份、**凭证**、唤醒、迁移退役 |
| [advanced/](advanced/) | 常驻 AI harness（可选） |
| [appendix/pitfalls.md](appendix/pitfalls.md) | **坑典** —— 出问题了按症状查这里 |
| [archive/](archive/) | 历史素材，**不是现行方案** |

### 六层主干

```
层 1  虚拟化底座      你这台机器能承载什么形态
层 2  旁路由形态      要不要做、做成什么样      ┐
层 3  代理栈          装哪一套（只能装一套）      ├ 不需要代理就整片跳过
层 4  分流与 DNS      ★ 代理的成败在这一层，坑最多 ┘
层 5  存储            四种形态，不推荐，但给硬判据
层 6  公网入口        ★ 只在内网用的话，整层跳过
层 7  内网寻址        ★ 所有人都要读——服务装好了怎么访问它
```

### 三条参考架构

| | 形态 | 状态 |
|---|---|---|
| [A · 老笔记本一肩挑](blueprints/a-single-laptop.md) | 旁路由 + 服务 + 仓库全在一台旧笔记本 | 已验证 · 已退役 |
| [B · 混合](blueprints/b-hybrid-mini.md) | 服务原生跑，旁路由单独一个轻量 VM | 已验证 · 在用 |
| [C · NAS 底座](blueprints/c-nas.md) | 厂商虚拟化套件 + 单臂旁路由 | ⚠️ **未落地验证** |

A 和 B 是"这么干过，代价是这些"。C 是"应该这么干，但你是第一个"。

## 不需要代理？这本手册照样能用

层 2、3、4 讲的是旁路由和透明代理。**如果你只想跑相册、影音、家庭自动化，
不需要代理——这三层整片跳过。**

探针的第一个问题就是这个（[Q2a](00-probe.md#q2a-需不需要代理)）。
不需要就走：**层 1（底座）→ 层 5（存储）→ 层 7（内网寻址）→ 挑服务 → 运维**。

⚠️ 三条参考架构全部包含旁路由，所以这种情况下**一条都不会对上**——
这是正常的，直接逐层求解就好。

## 怎么验证这本手册

`scripts/check.sh` 做三项机械检查：脱敏、frontmatter 一致性、内链有效性。
**但它查不了内容对不对。**

真正的验收是**端到端演练**：给一份虚构的硬件条件，让一个 agent 只读本仓库，
跑一遍 `00-probe` → 选型 → 输出配置清单，全程 dry-run 不碰真机。看三件事：

1. 它能不能收敛到一个**不自相矛盾**的组合
2. 它有没有在 `needs_human` 的地方**停下来问人**
3. 它引用的 `verify` 是不是**客户端视角的那条**

这份手册已经这样跑过一次，并据此修掉了若干处矛盾与缺口。

## 关于示例里的地址

所有 IP、域名、MAC **都是占位符**（用了 RFC 5737 的文档保留段）。
**照抄不会连上任何东西** —— 这是有意的：抄错要失败得干脆，而不是恰好命中你的真机。

约定见 [`appendix/redaction.md`](appendix/redaction.md)。

## 许可

手册正文 CC BY 4.0，`scripts/` 下的脚本 MIT。详见 [LICENSE](LICENSE)。

## 状态

素材来自三套真实硬件上的实际部署与踩坑记录。
标了 ⚠️ **未落地验证**的部分，请当作推理而不是经验。

---
---

# anyserver (English)

**Turn whatever hardware you have into a home or studio server you can actually live with.**

Not a follow-along tutorial — a handbook that **solves for your hardware**. It doesn't assume
what you own; it asks first, then gives you a matching path and its costs.

## Two hard rules

```
1. Side-gateway only, never main router.
2. DHCP belongs to the main router alone.
```

Touching the main router is the one class of change that takes a household offline instantly,
possibly leaving you without a network to fix it from. This handbook stays out.

## What you get

- A complete path matched to your hardware, not someone else's config
- Machine-checkable acceptance criteria for every step — run from a *client*, not the box itself
- A rollback for every step, that doesn't depend on the link you just broke
- A catalogue of ~25 real pitfalls, each indexed by **what the symptom looks like**
- An optional service menu: photos, media, music, downloads, passwords, home automation

## Getting started

**Human**: start at [`00-probe.md`](00-probe.md). It asks a few questions and points you at
the two or three chapters you actually need. Don't read it front to back.

**Using an AI to set things up**: hand it this repo and have it read [`AGENTS.md`](AGENTS.md)
first — that's the operating contract, including **what it must stop and ask you about**.

## Layout

`00-probe.md` → `layers/` (six-layer trunk) → `blueprints/` (three reference architectures)
→ `services/` (all optional) → `ops/` → `appendix/pitfalls.md`

`archive/` holds historical research material — **not a current plan.**

## About the addresses in examples

Every IP, domain and MAC is a **placeholder** (RFC 5737 documentation ranges).
**Copying them will not work** — deliberately. A wrong copy should fail loudly rather than
happen to hit a real machine on your network.

## Status

Drawn from real deployments on three hardware substrates. Anything marked
⚠️ **未落地验证 / not verified in production** is reasoning, not experience.
