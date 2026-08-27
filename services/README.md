# 服务菜单

**全部可选。** 按需要挑，不要全装——每个服务都是要维护的东西。

选之前先过一遍它的 `requires`，尤其**存储要求**：有些服务对数据库落点很苛刻，
可能反过来影响你在 [层 5](../layers/5-storage.md) 的决定。

格式规范见 [`_schema.md`](_schema.md)；**怎么组织部署**见 [`_deployment.md`](_deployment.md)。

## 清单

| 服务 | 用途 | 关键约束 |
|---|---|---|
| [immich](immich.md) | 照片 / 视频库 | ⚠️ **数据库落点最苛刻**；主服务与 ML 版本必须一致 |
| [jellyfin](jellyfin.md) | 影音库 | 硬件转码高度依赖平台；macOS 上要硬解须原生装 |
| [home-assistant](home-assistant.md) | 家居自动化 | ⚠️ 默认桥接网络**发现不了任何设备** |
| [aria2](aria2.md) | 下载器 | ⚠️ RPC 默认无认证，必须设密钥 |
| [vaultwarden](vaultwarden.md) | 密码库 | ⚠️ 必须 HTTPS；备份必须验证过能恢复 |
| [navidrome](navidrome.md) | 音乐库 | 依赖文件元数据标签 |
| [sunpanel](sunpanel.md) | 导航面板 | 认证类服务用新标签页打开，别内嵌 |
| [lanraragi](lanraragi.md) | 漫画 / 图集 | 吃压缩包，建议只读挂载 |
| [searxng](searxng.md) | 元搜索 | ⚠️ 出口 IP 敏感，"能打开但搜不出东西"是常态故障 |
| [syncthing](syncthing.md) | 文件同步 | ⚠️ **会双向删除**；不是备份 |
| [hugo](hugo.md) | 静态博客 | 不是常驻服务，攻击面几乎为零 |
| [sunshine-moonlight](sunshine-moonlight.md) | 远程桌面 / 串流 | 需原生 + GPU + 已登录会话；**绝不能走代理** |
| [webdav](webdav.md) | 简易文件服务 | ⚠️ Basic Auth 等同明文，公网必须 HTTPS |

## 不在这里的

**反向代理、隧道客户端、组网工具**不在服务菜单里——它们属于
[层 6 · 公网入口](../layers/6-ingress.md)，是基础设施不是可选服务。

**局域网唤醒**属于 [`ops/wol.md`](../ops/wol.md)。

## 挑完之后

1. 核对每个服务的 `requires` 是否被你的配置向量满足
2. 检查有没有 `conflicts`
3. 把所有 `needs_human: true` 的挑出来，**先和用户确认这些**
4. 按 `verify` 逐个验收——**从客户端跑**

## 通用注意

| 事项 | 一句话 | 详见 |
|---|---|---|
| **架构** | 别假设有你的架构，动手前逐个查 manifest | [`../ops/migration-retirement.md`](../ops/migration-retirement.md#先做架构预检再定架构) |
| **版本** | 不用 `latest`；有依赖的组件钉同一版本 | [`_deployment.md`](_deployment.md#版本) |
| **一次装一个** | 验收通过再装下一个 | [`_deployment.md`](_deployment.md#一次装一个) |
| **凭证** | 不进版本库，任何版本库 | [`../ops/secrets.md`](../ops/secrets.md) |

⚠️ **首次导入**：媒体类服务首次扫描会持续很久并大量读盘。
**如果媒体在外接盘或网络挂载上，这段时间的 I/O 压力最容易触发掉线。**
先用小目录验证通路，再放全量。
