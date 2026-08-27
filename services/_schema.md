# 模块 frontmatter 规范

> 本规范同时约束 `layers/` 里的每个**选项**与 `services/` 里的每个**服务模块**。
> 读这个仓库的 agent 依赖这些字段做选型与验收，字段写错比不写更糟。

## 完整字段表

```yaml
---
id: nikki                      # 全仓唯一，kebab-case，与文件名一致
name: Nikki (mihomo)           # 人类可读名
layer: 3                       # 1-6；服务模块写 service
requires:                      # 前置条件；全部满足才可选
  arch:      [x86_64, aarch64] # 缺省表示不限
  substrate: [vm]              # 层1 取值，见 layers/1-substrate.md
  gateway:   [vm-openwrt]      # 层2 取值，见 layers/2-gateway.md
conflicts: [openclash, shellcrash, passwall, homeproxy]
risk: high                     # none | low | medium | high
needs_human: true              # true 时 agent 必须停下来问用户
verify: |                      # ★ 必须从客户端视角，见下
  <cmd>
  # 期望: <output>
rollback: |                    # 单条或少数几条，能一步退回
  <cmd>
---
```

## 字段释义

### `requires`

前置条件的**合取**——全部满足才允许选中。缺省的键表示"不限"。

**键名与配置向量的字段一一对应**（`arch` / `substrate` / `gateway` / `proxy` / `storage` /
`ingress`），取值必须落在对应层文档定义的枚举里。

### 两种判定语义，别搞混

配置向量里有两类字段，`requires` 对它们的判定方式**不同**：

| 字段 | 向量里是 | `requires` 的含义 |
|---|---|---|
| `arch` `gateway` `proxy` `ingress` | **单值** | 向量的值**必须在**列表里（属于） |
| `substrate` `storage` `addressing` | **多值**（一台机器可以既有内置盘又有外接盘） | 向量与列表**交集非空**（至少有一个） |

举例：`services/immich.md` 声明 `requires.storage: [internal, das-enclosure]`，
用户的向量是 `storage: [internal, usb-portable]`。

- 按"属于"判 → `usb-portable` 不在列表里 → **误判为不可用** ❌
- 按"交集非空"判 → 有 `internal` → **可用**，且这正好告诉你数据库该落在 `internal` 上 ✅

**多值字段的 `requires` 表达的是"必须存在一个合格的落点"，不是"你只能有这些"。**

`scripts/check.sh` 会校验键名、取值枚举，以及多值字段是否写成了列表。

### `conflicts`

**硬约束，不是建议。** 列出的模块与本模块不可共存。透明代理这一类尤其致命：
两套同时装会各自往防火墙里塞劫持规则，互相打架，症状是"看起来都启动了但客户端全断"。

`conflicts` 必须**双向对称**——A 声明冲突 B，则 B 也要声明冲突 A。`scripts/check.sh` 会查。

### `risk`

| 值 | 含义 |
|---|---|
| `none` | 装错了只影响这个服务本身 |
| `low` | 影响同机其它服务 |
| `medium` | 影响该设备的网络可达性 |
| `high` | **全屋断网级**——改错了所有人立刻掉线，且你可能连补救的网都没有 |

### `needs_human`

`true` 表示 agent **必须停下来问用户**，不得自行决定。适用于：

- 任何 `risk: high` 的动作
- 需要在主路由上操作的（绑定静态 IP、指定网关）
- 会改变全屋默认路径的（把客户端网关指向旁路由）
- 涉及花钱、买硬件、改物理接线的

### `verify` —— 最重要的字段

**必须从客户端视角写，不能是服务自身或路由器的自测。**

> **「核能出海」≠「客户端能借道」。**

这条规则来自一个真实教训——完整案例见
[层 3 · 坑一](../layers/3-proxy-stack.md#坑一裸核模式几乎人人踩)。
简言之：组件自测全绿、客户端却完全不通，而两者都"没报错"。

agent 比人更容易停在"自测通过"就宣布完成，所以这条写进规范而不是靠提醒。

写法：

```yaml
verify: |
  # 在一台【客户端】设备上执行（不是路由器、不是服务所在主机）
  curl -s -o /dev/null -w '%{http_code}\n' https://<某个被代理的目标>
  # 期望: 204
```

### 占位符与"可执行"的冲突，以及怎么解

手册出于[脱敏原则](../appendix/redaction.md)不写真实域名，于是有些 `verify` 里是
`<某个被代理的目标>` 这类占位符——**这跟"verify 必须能照着执行"是直接冲突的。**

解法不是取消占位符，而是**在执行前把它们敲定并写下来**：

> 动手之前，先和用户一起把这次部署要用的**具体探测目标**定下来，
> 记在你自己的工作笔记里（不是本仓库），然后所有 `verify` 都用这一组固定目标。

一组好的探测目标应当满足：

| 用途 | 要求 |
|---|---|
| 连通性探测 | 返回**稳定的状态码**、响应体极小、不需要认证 |
| 直连 / 代理对照 | 两个目标的可达性有明确差异，便于分辨走了哪条路 |
| 出口地区回显 | 能返回**调用方出口 IP** 的服务 |

⚠️ **每次都换目标去试，等于每次都在验证不同的东西。** 固定一组，
才能在几周后重跑时判断"是不是退化了"。

### `rollback`

必须能**一步退回**，且退回路径不依赖刚刚配坏的那条链路。

典型反例：把 SSH 也走了代理，代理配坏 → 进不去 → 没法回滚。
所以旁路由类模块的 `rollback` 前要注明"管理通道必须是局域网直连、不经代理"。

## 配置向量

`00-probe.md` 探测完环境后输出一个**配置向量**，后续所有选型都基于它：

```yaml
# 单值字段
arch:      x86_64 | aarch64
gateway:   none | vm-openwrt | container-macvlan | dedicated-box | client-only
proxy:     none | nikki | shellcrash | openclash | homeproxy | client-side
ingress:   none | tailscale | tunnel | port-forward

# 多值字段（写成列表；一台机器可以同时具备多项）
substrate:  [bare-metal, vm, container]     # 或 [none]
storage:    [internal, usb-portable]        # 有几块写几块
addressing: [ip-static, lan-dns]            # 内网怎么访问服务
services:   [immich, jellyfin]
```

拿到向量后**先对 `blueprints/` 的三条锚点**——对得上就走已验证路径，对不上再逐层求解。
