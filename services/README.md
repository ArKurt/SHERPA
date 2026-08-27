# 服务菜单

**全部可选。** 按需要挑，不要全装——每个服务都是以后要维护的东西。

> 不知道该挑什么？**开 [`wizard.html`](../wizard.html)** ——
> 它会按你的目标筛一遍，每个服务都带一段给人看的介绍。

## 清单

| 服务 | 是什么 |
|---|---|
| [Immich](immich.md) | 自托管的照片与视频库 |
| [Jellyfin](jellyfin.md) | 自托管的影音库与播放服务 |
| [Navidrome](navidrome.md) | 自托管的音乐库与流媒体服务 |
| [aria2 + AriaNg](aria2.md) | 常驻的下载器，配一个网页界面 |
| [Home Assistant](home-assistant.md) | 本地优先的智能家居中枢 |
| [Vaultwarden](vaultwarden.md) | 自托管的密码库 ·&nbsp;需你拍板 |
| [Sunshine + Moonlight](sunshine-moonlight.md) | 低延迟的桌面与游戏串流 ·&nbsp;需你拍板 |
| [SunPanel](sunpanel.md) | 服务导航面板 ·&nbsp;等其它服务就位后再装 |

标「需你拍板」的，装之前必须和用户确认——不是难装，是**决定本身**要人来做。
标「等其它服务就位」的，装早了没意义（导航面板得先有导航对象）。

> **这个顺序不代表推荐度。** 手册不排"你该先装哪个"——
> 那取决于你想要什么，而不是我们觉得什么重要。

## 选之前

1. 看该服务页的 `requires`，尤其**存储要求**——有些服务对数据库落点很苛刻，
   会反过来影响你在 [层 5](../layers/5-storage.md) 的决定
2. 检查 `conflicts`
3. 按 `verify` 逐个验收，**从客户端跑**

装法与目录布局见 [`_deployment.md`](_deployment.md)；字段含义见 [`_schema.md`](_schema.md)。

## 这里为什么只有 8 个

**收录标准是"手册能对它负责"**：这 8 个都在真实硬件上跑过，
而且它们的坑是手册作者亲自踩过、能写出症状和修法的。

自托管生态里好东西远不止这些。**手册没收录 ≠ 不该用**——
但那意味着你得自己去读它的官方文档、自己踩它的坑，
本手册的判据（存储落点、验收视角、conflicts）仍然适用。

## 不在这里的

| 东西 | 在哪 |
|---|---|
| 反向代理、隧道客户端、组网工具 | [层 6 · 公网入口](../layers/6-ingress.md)——基础设施，不是可选服务 |
| 局域网唤醒 | [`../ops/wol.md`](../ops/wol.md) |
| 常驻 AI harness | [`../advanced/resident-ai-harness.md`](../advanced/resident-ai-harness.md) |

## 装的时候出问题

去 [排障区](../pitfalls/README.md)，**按症状查**。
各服务已知的坑集中在 [`pitfalls/services.md`](../pitfalls/services.md)。
