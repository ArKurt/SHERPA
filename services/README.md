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
| [Syncthing](syncthing.md) | 设备之间的点对点文件同步 ·&nbsp;需你拍板 |
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

## 收录标准，以及为什么会变

**收录标准是"手册能对它负责"**：在真实硬件上跑过，而且它的坑是作者亲自踩过、
写得出症状和修法的。

**手册没收录 ≠ 不该用。** 自托管生态里好东西远不止这些——
只是那意味着你得自己读它的官方文档、自己踩它的坑。
本手册的判据（存储落点、验收视角、`conflicts`、凭证纪律）仍然适用。

### 这份清单会变，这是正常的

服务有出有进：上游停更、更好的替代出现、或者某个场景反复证明缺了它不行。
**清单变动本身不是问题，漏改才是。**

真实教训：某次一口气剔掉 5 个服务，忘了清理外链白名单里的 6 条残留，
是审查者发现的。所以下面这两张表是**给未来的自己**准备的。

### 加一个服务

- [ ] `services/<id>.md`，frontmatter 照 [`_schema.md`](_schema.md) 填全
- [ ] `blurb` 要**给不懂的人看**——它解决什么问题，尽量类比一个大家知道的东西
- [ ] `docs` 至少一条官方链接，**并把域名登记进 `scripts/allowed-domains.txt`**
- [ ] 它的坑写进 [`../pitfalls/services.md`](../pitfalls/services.md)，
      并在[症状索引](../pitfalls/README.md)加一行
- [ ] `goals` 用已有的；要新增目标，确认它在向导第一轮里说得通
- [ ] 加进上面的清单表
- [ ] `scripts/build-catalog.py` 重新生成，`scripts/check.sh` 全绿

### 剔一个服务

**比加更容易漏。** 逐项确认：

- [ ] 删 `services/<id>.md`
- [ ] 删排障区里它的条目 **＋ 症状索引里对应的行**
- [ ] 清 `scripts/allowed-domains.txt` 里只有它用的域名
- [ ] 查它是不是某个 `goals` 的唯一支撑——**是的话那个目标会消失**，
      要么接受，要么找替代
- [ ] 查 `blueprints/` 有没有引用它。**锚点记录的是历史事实，不要为了迎合
      当前菜单去改写历史**——保留真实清单，加注"本手册未收录"
- [ ] 查 `REVIEW.md`、`reviews/` 里有没有针对它的任务项
- [ ] 从上面的清单表移除
- [ ] 重新生成 + `scripts/check.sh` 全绿

> 💡 **剔之前先问一句：这个服务是不是某个场景的唯一解？**
> 有一次剔掉文件同步类服务后，"多人共享素材库"这个需求在手册里直接无解了——
> 两轮之后由审查者独立发现，才把它加回来。

## 不在这里的## 不在这里的

| 东西 | 在哪 |
|---|---|
| 反向代理、隧道客户端、组网工具 | [层 6 · 公网入口](../layers/6-ingress.md)——基础设施，不是可选服务 |
| 局域网唤醒 | [`../ops/wol.md`](../ops/wol.md) |
| 常驻 AI harness | [`../advanced/resident-ai-harness.md`](../advanced/resident-ai-harness.md) |

## 装的时候出问题

去 [排障区](../pitfalls/README.md)，**按症状查**。
各服务已知的坑集中在 [`pitfalls/services.md`](../pitfalls/services.md)。
