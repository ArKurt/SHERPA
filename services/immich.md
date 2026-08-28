---
id: immich
name: Immich
layer: service
install_when: anytime
category: media
goals: [照片备份, 多媒体影音]
summary: 自托管的照片与视频库
blurb: |
  手机照片自动备份到你自己家里的机器上，多端同步，能按人脸、时间、地点浏览。
  可以理解为「自己家的 Google Photos」——照片存在你自己的硬盘上，
  不占云端空间、不按月付费、不看别人脸色。
  代价是：**这是本手册里对存储要求最苛刻的服务**，选它之前先看清楚硬盘怎么摆。
docs:
  - type: official
    title: Immich 官方文档
    url: https://immich.app/docs
  - type: official
    title: 官方安装指引（Docker Compose）
    url: https://immich.app/docs/install/docker-compose
requires:
  arch: [x86_64, aarch64]
  substrate: [bare-metal, vm, container]
  storage: [internal, das-enclosure]      # 数据库落点；媒体库可另择
conflicts: []
risk: low
needs_human: false
verify: |
  # 从【另一台设备的浏览器】打开，不是在服务器本机 curl
  curl -s -o /dev/null -w '%{http_code}\n' http://192.0.2.10:2283/api/server/ping
  # 期望: 200
rollback: |
  docker compose down    # 数据在卷里，不会丢
---

# Immich

自托管照片/视频库。**本手册里对存储要求最苛刻的服务，先读这一条再决定装不装。**

## 组成

四个组件缺一不可：主服务、机器学习服务、PostgreSQL（带向量扩展）、Redis。

## 存储要求（最重要）

**PostgreSQL 的数据目录必须落在本地原生文件系统上。**

| 落点 | 可否 |
|---|---|
| 内置盘（ext4/btrfs/xfs/APFS） | ✅ |
| 外接硬盘柜，原生文件系统 | ✅ |
| **exFAT** | ❌ 官方写明不支持（*not supported*） |
| **网络挂载（SMB/NFS）** | ❌ **官方不支持**——安装文档写明 *Network shares are not supported for the database*，requirements 页要求 *never a network share of any kind* |
| **USB 移动硬盘** | ❌ 掉线一次可能就要从备份恢复 |

**照片库本身**（原图存放）对**掉线风险**宽松得多，外接盘、网络挂载都可以。

⚠️ **但对文件系统不宽松。** 照片库是 Immich 的**上传目录**——容器要以非 root
身份持续往里写。它是[层 5 说的"可写媒体"](../layers/5-storage.md#三类用途要求递增)，
不是只读媒体：

| 落点 | 照片库 |
|---|---|
| 原生文件系统（ext4/btrfs/xfs/APFS） | ✅ |
| **exFAT** | ⚠️ 需按容器实际 UID/GID 挂载后验收，见下 |
| 网络挂载 | ⚠️ 可行但要调挂载参数（uid/gid），先小规模验证 |

**外接盘出厂常是 exFAT。** 拿来放影音库直接可用；拿来当 Immich 的上传目录要多做一步——
exFAT 不存逐文件属主，得在**挂载时**把整卷映射成容器实际运行的 UID/GID，再**从容器里**跑写入验收。
做法见[层 5 的 exFAT 一节](../layers/5-storage.md#exfat-的限制到底在哪)。
**别一上来就重新格式化**——那会擦掉盘上现有数据，属于必须问用户的事。

⚠️ **但数据库那半不让步**：Immich 官方 requirements 写明
*It will not work on any filesystem formatted in NTFS or ex/FAT/32*。
挂载参数救不了数据库，因为缺的不是权限，是日志。

→ 所以标准做法是**拆开**：数据库在内置盘，照片库在大容量盘上。
详见 [层 5](../layers/5-storage.md#组合示例不是推荐是说明判据怎么用)。

### 真实后果

数据库和照片库放同一块 USB 盘上，盘被搬走后挂载点变成空的临时文件系统，
数据库以为是全新安装 → 初始化 → 失败 → 重启 → 累计崩溃数千次。
原图一个字节没丢，但服务完全起不来。→ [锚点 A](../blueprints/a-single-laptop.md)

## 版本必须钉死且一致

**把主服务和机器学习服务钉在同一个版本号上。**

这是社区的普遍实践——**官方文档没有明文要求**，但 release notes 和社区 issue 都按这个假设走。
手册这边观察到过一次版本错配之后主服务进入崩溃重启循环（[锚点 A](../blueprints/a-single-laptop.md)），
一次事故不足以写成"必然"，但钉死版本的成本是零，没有理由不做。

不要用 `latest`。在 compose 里写死具体版本，升级时两个一起改。

升级前**必读官方 release notes**——Immich 迭代快，有过需要手工迁移的破坏性变更。

## 移动端与"不开外网"的后果

Immich 的主要用法是**手机 App 自动备份**。如果层 6 选了 `ingress: none`（只在内网用）：

- **只有连着家里 Wi-Fi 时才会备份。** 在外面拍的照片会攒着，回家才补传
- App 里填的是**内网地址**，出门在外打不开
- 这通常可以接受，但**必须让用户明确知道**——很多人默认"自动备份"是随时随地的

如果用户不能接受，那就需要回到 [层 6](../layers/6-ingress.md)。
最轻的方案是组网工具（零公网暴露），不必上隧道或端口转发。

App 里填的地址要稳定——见 [层 2 · 静态 IP 怎么来](../layers/2-gateway.md#静态-ip-怎么来)。

## 资源

机器学习服务（人脸识别、对象检测）吃内存和 CPU。首次导入大量照片时会有很长的任务风暴——
**这段时间机器会很忙，别和其它重活撞一起**。可以先关掉后台任务，导入完再开。

> ⚠️ **本手册不给内存与容量的具体数字。** 需求随版本、照片数量、是否开启机器学习
> 变化很大，给一个过时的数字比不给更糟。
> **做法是实测**：先用几百张照片跑一轮，观察内存峰值与缩略图占用，再按比例外推。
> 尤其注意**缩略图默认落在内置盘上**，大库可能把系统盘挤爆——
> 见 [层 5](../layers/5-storage.md)。

## 备份

Immich 自带定时数据库备份，**先确认它开着**。备份文件默认落在照片库目录下——
如果照片库在外接盘上，那备份和数据一起丢。**把备份复制到另一块物理盘。**

## 架构

主流版本都发 multi-arch，ARM 可用。但数据库镜像（带向量扩展的 Postgres）
要单独确认有你的架构构建。

---

> 📎 **本页断言的出处与强度**：[`appendix/sources.md`](../appendix/sources.md#services-immich)
