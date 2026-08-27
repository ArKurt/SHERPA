---
id: jellyfin
name: Jellyfin（媒体服务器）
layer: service
priority: P0
requires:
  arch: [x86_64, aarch64]
  substrate: [bare-metal, vm, container]
conflicts: []
risk: low
needs_human: false
verify: |
  # 从【另一台设备】访问
  curl -s -o /dev/null -w '%{http_code}\n' http://192.0.2.10:8096/health
  # 期望: 200
  # 再用一台真实播放设备播一个文件——Web 能开不等于能播
rollback: |
  docker compose down
---

# Jellyfin

自托管影音库。**卡点在硬件转码，不在安装。**

## 存储

宽松。媒体库放哪都行——外接盘、网络挂载都可以。

配置与元数据库放本地盘（会频繁读写，且损坏了要重扫全库，很痛）。

## 硬件转码

不配硬解时，转码会吃满 CPU，多路并发直接卡死。但硬解的配置**高度依赖平台**：

| 平台 | 做法 |
|---|---|
| Linux + Intel 核显 | 容器里透传 `/dev/dri`，用 VAAPI/QSV |
| Linux + 独显 | 透传对应设备，装厂商运行时 |
| macOS | VideoToolbox；**容器里拿不到，需要原生安装** |
| NAS | 看厂商是否开放了硬件编解码设备 |

**macOS 上要硬解就得原生装，不能用容器。** 这是 [锚点 B](../blueprints/b-hybrid-mini.md)
把它放在原生层的原因。

### 先确认要不要转码

**能直接播放（direct play）就不需要转码。** 如果播放设备支持你的媒体格式，
Jellyfin 只是把文件流过去，几乎不耗 CPU。

转码只在格式不兼容或需要降码率时发生。先看实际播放场景，别为不存在的需求配硬解。

## 架构

官方发 multi-arch。

## 首次扫描

大媒体库首次扫描会持续很久并大量读盘。**如果媒体在外接盘或网络挂载上，
这段时间的 I/O 压力最容易触发掉线。** 先扫小目录验证通路，再放全量。
