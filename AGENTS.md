# AGENTS.md — 操作契约

> 给受用户委托、读本仓库并在其机器上实施的 agent。
> 人类读者请从 [README.md](README.md) 进。
> *English version below.*

---

## 两条铁律

```
① 只做旁路由，不做软路由。
   不碰 PPPoE、不接管寻址、不做端口转发规划、不改主路由配置。

② DHCP 只由主路由负责。
   旁路由不发地址，最多被指为客户端的网关 / DNS。
```

这不只是范围声明，是风险边界。**改主路由是本手册涉及的唯一一类"改错了全家立刻断网、
且你连补救的网都没有"的操作。** 网络不通时最诱人的动作就是去动主路由——不要。停下来问用户。

需要用户在主路由上做的事（如给旁路由绑定静态 IP），**告诉用户怎么做，不要代劳**。

---

## 怎么读这个仓库

**索引优先，不要全库扫。** 顺序固定：

1. [README.md](README.md) 的目录 —— 知道东西在哪
2. [`00-probe.md`](00-probe.md) —— 探测用户环境，产出**配置向量**
3. [`blueprints/`](blueprints/) —— 拿向量去对三条已验证锚点
   - **对得上** → 走那条已验证路径，只读它引用的层
   - **对不上** → 进 [`layers/`](layers/) 逐层求解
4. 只读命中的层与模块。不要预读整个 `layers/`。

[`archive/`](archive/) 是历史素材（一道旧题的多模型横向对比），**不是现行方案，不要照着执行**。

---

## 选型规则

0. **用户没提的东西不要主动引入。** 尤其是代理——"想要一台家庭服务器"和"想要代理"
   是两个独立需求。用户没提过代理 / 订阅 / 机场，就按 `gateway: none` + `proxy: none`
   处理，**跳过层 2、3、4**，并明确告诉用户你跳过了。
   透明代理会显著增加故障面，而且是"全屋断网"这个风险的主要来源。
1. **`requires` 是准入**：全部满足才可选。取值枚举见各层文档。
   注意**单值字段判"属于"、多值字段（`substrate` / `storage`）判"交集非空"**——
   见 [`services/_schema.md`](services/_schema.md#两种判定语义别搞混)。
2. **`conflicts` 是硬约束，不是建议**。尤其：**绝不并装两套透明代理**。两套会各自往防火墙塞
   劫持规则，症状是"看起来都启动了但客户端全断"，且极难诊断。
3. **不确定就不装**。手册里没有的方案，不要即兴发挥后写进用户的机器。

---

## 执行规则

### 停下来问人

遇到以下任一情况，**停止执行，向用户说明并等待答复**：

- 模块标了 `needs_human: true`
- 模块标了 `risk: high`
- 需要在主路由上操作
- 需要把客户端（尤其是全屋默认）的网关指向新设备
- 需要花钱、买硬件、改物理接线
- 现场情况与文档描述不符

最后一条尤其重要：**现场与文档不符时报告，不要猜。** 本手册基于三套真实硬件写成，
不可能覆盖所有型号与固件版本。猜错的代价是用户断网，而你无法远程补救。

### 验收

**只认模块的 `verify` 字段，且必须从客户端跑。**

不要用"服务启动了"、"端口在监听"、"路由器自测能出海"代替验收。这条来自真实教训：

> **「核能出海」≠「客户端能借道」。**

路由器上自测代理端口返回 204、判定成功，客户端借道却国内外全断——因为代理插件在裸核模式下
只启动了内核，一条防火墙劫持规则都没生效。你比人更容易停在自测通过就收工。

### 回滚

动手前先确认 `rollback` 可执行，且**回滚路径不依赖你正要改的那条链路**。

具体说：**到旁路由的管理通道必须是局域网直连、不经代理。** 否则代理配坏 → SSH 进不去 →
无法回滚。改高风险配置前先验证这一点。

### 顺序

先改**可逆的、影响面小的**，再改全局的。典型的安全顺序：

```
VM 起在隔离网络（NAT）里验证内核与插件
  → 切桥接、拿到独立 IP、只用一台测试设备指网关
    → 实测通过后才考虑扩大范围
```

不要一步到位把全屋网关切过去。

---

## 凭证

用户的订阅链接、API 密钥、SSH 私钥会经过你的手。**规则见
[`ops/secrets.md`](ops/secrets.md#给-agent-的额外要求)**，最要紧的三条：

- **不要把凭证写进任何会被提交、上传或分享的地方**，包括你自己的工作笔记
- **不要在回复里回显完整凭证**——确认时只显示前后几位
- 用户让你"记下来"时，记的是**它在哪**，不是它是什么

## 写回

如果用户让你把实施结果记录下来，写到用户自己的地方。**不要往本仓库写用户的现场信息**——
这是一份公开手册，不是某个人的配置备份。

---

## 脱敏

本仓库示例中的地址、域名、MAC 全部是占位符（约定见
[`appendix/redaction.md`](appendix/redaction.md)）。**照抄会连不上。** 每个占位符都需要
替换成用户现场的真实值——替换前先确认你知道正确的值，不要用示例值试。

---
---

# AGENTS.md — Operating Contract (English)

> For agents acting on a user's behalf, reading this repo and implementing on their machines.
> Human readers: start at [README.md](README.md).

## Two hard rules

```
1. Side-gateway only, never main router.
   Don't touch PPPoE, addressing, port-forward planning, or the main router's config.

2. DHCP belongs to the main router alone.
   The side gateway hands out no addresses. At most it is named as a client's gateway/DNS.
```

Touching the main router is the one class of change here that takes the whole household
offline instantly — and may leave you without a network to fix it from. When things break,
the tempting move is to change the main router. Don't. Stop and ask the user.

When something must be done on the main router (e.g. a static lease for the side gateway),
**tell the user how — don't do it yourself.**

## How to read this repo

Index first, never scan everything. Fixed order:

1. [README.md](README.md) table of contents
2. [`00-probe.md`](00-probe.md) — probe the environment, produce a **config vector**
3. [`blueprints/`](blueprints/) — match the vector against three verified anchors.
   Match → follow that verified path. No match → solve layer by layer in [`layers/`](layers/).
4. Read only the layers you hit.

[`archive/`](archive/) is historical research material, **not a current plan. Do not execute it.**

## Selection rules

- `requires` gates admission — all conditions must hold.
- `conflicts` is a hard constraint, not advice. **Never install two transparent proxies.**
  Both will inject firewall hijack rules and fight; the symptom is "everything looks up but
  no client can get through", and it is very hard to diagnose.
- If it isn't in this handbook, don't improvise it onto a user's machine.
- **Don't introduce what the user didn't ask for** — especially a proxy. "I want a home
  server" and "I want a proxy" are separate needs. If they never mentioned one, set
  `gateway: none` / `proxy: none`, skip layers 2–4, and say so.

## Execution rules

**Stop and ask** when: `needs_human: true`, `risk: high`, anything on the main router,
pointing a household's default gateway at a new device, spending money or changing cabling,
or when reality doesn't match the docs. That last one especially — **report, don't guess.**

**Acceptance**: only the module's `verify` field counts, and it must run **from a client**.
Not "the service started", not "the port is listening", not "the router's own test reached
the internet".

> **"The core can reach the internet" ≠ "clients can get through it."**

**Rollback**: confirm it works before you start, and make sure the rollback path doesn't
depend on the link you're about to change. Management access to the side gateway must be
direct LAN, not through the proxy.

**Order**: reversible and narrow first. Bring a VM up on an isolated network, verify, then
bridge it, then point one test client at it. Never flip the whole household in one step.

## Redaction

All addresses, domains and MACs in examples are placeholders (see
[`appendix/redaction.md`](appendix/redaction.md)). **Copying them verbatim will not work.**
