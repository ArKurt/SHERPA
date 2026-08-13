# homerouter

QNAP 家用单臂旁路由：旁路只做透明代理，主路由继续管网。

## 约束

- **DHCP** 只由主路由负责  
- 旁路由不发地址、不接管寻址；最多被指为网关 / DNS  

## 推荐路径

底座统一：**Virtualization Station + 官方 ImmortalWrt**（独立 IP；VM 内关 DHCP）。

代理按订阅分支（**二选一，勿叠装**）：

| 客户订阅 | 代理栈 | 文档 |
| --- | --- | --- |
| Shadowrocket / 格式未核实 / 要少转换 | **ShellCrash（Meta）** | [08](08-qnap旁路由_shellcrash订阅优先.md) |
| 已是 Clash / Mihomo YAML | **Nikki** | [06](06-qnap旁路由_nikki_cursor_composer.md) |

Docker ShellCrash 仅免 Wrt 备选（[05](05-docker_shellcrash问题_cursor_composer.md)）；`01` host Debian 不采用。

## 文档

1. [08 订阅优先 · ShellCrash](08-qnap旁路由_shellcrash订阅优先.md) — Shadowrocket 链接优先时用  
2. [06 YAML 优先 · Nikki](06-qnap旁路由_nikki_cursor_composer.md) — 已是 Clash/Mihomo 时用  
3. [07 订阅转换](07-订阅格式转换_shadowrocket_nikki.md) — 坚持 Nikki 时再转格式  
4. [03 实施稿](03-qnap旁路由_opus_5.md) — VS + ImmortalWrt 底座  
5. [04 现场与验收](04-qnap旁路由_cursor_composer.md) — 现场表、易踩坑、回滚  
6. [02 方案排序](02-qnap旁路由_cursor_grok.md) — 为何 VM 优先  
7. [05 Docker 问题](05-docker_shellcrash问题_cursor_composer.md) — 免 Wrt 时再读  
8. [01 Gemini 原稿](01-qnap+shellcrash_gemini.md) — 反例，勿直接照做  

多棒对照表：[00 文稿索引](00-文稿索引.md)
