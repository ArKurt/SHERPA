---
id: navidrome
name: Navidrome
layer: service
install_when: anytime
category: media
goals: [多媒体影音]
summary: 自托管的音乐库与流媒体服务
blurb: |
  把你的音乐收藏放在家里的机器上，手机和电脑随时点播。
  它兼容一套通用的音乐协议，所以**能用大量现成的第三方 App**，
  不必忍受某个厂商自带的难用客户端。
  可以理解为「自己的 Spotify，但曲库是你自己的收藏」。
docs:
  - type: official
    title: Navidrome 官方文档
    url: https://www.navidrome.org/docs/
requires:
  arch: [x86_64, aarch64]
  substrate: [bare-metal, vm, container]
  storage: [internal, das-enclosure]      # SQLite 落点；音乐库可另择
conflicts: []
risk: low
needs_human: false
verify: |
  curl -s -o /dev/null -w '%{http_code}\n' http://192.0.2.10:4533/ping
  # 期望: 200
rollback: |
  docker compose down
---

# Navidrome

音乐服务器，兼容 Subsonic API，所以能用大量现成的第三方客户端（手机、桌面）。

## 存储

- **音乐库**：宽松，放外接盘/网络挂载都行，只读挂载更安全
- **数据库**：SQLite，放本地盘

## 扫描

首次扫描大库耗时长。**扫描依赖文件的元数据标签**——标签乱的库扫出来就是乱的，
Navidrome 不猜。整理标签是导入前的事，不是它的职责。

## 歌词

歌词通常靠外部服务或本地 `.lrc` 文件。如果用外部歌词服务，
注意它可能需要走代理才能访问——见 [层 4](../layers/4-routing-dns.md)。

## 架构

官方发 multi-arch。

---

> 📎 **本页断言的出处与强度**：[`appendix/sources.md`](../appendix/sources.md#services-navidrome)
