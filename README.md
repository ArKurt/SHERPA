# homerouter

QNAP 家用单臂旁路由：旁路只做透明代理，主路由继续管网。

## 约束

- **DHCP** 只由主路由负责  
- 旁路由不发地址、不接管寻址；最多被指为网关 / DNS  

## 推荐路径

**Virtualization Station + 官方 ImmortalWrt + Nikki（mihomo）**

- 网络：与 NAS 同二层、独立 IP；VM 内关 DHCP  
- 代理：ImmortalWrt 上用 Nikki；不用 ShellCrash  
- ShellCrash 仅作免 Wrt 的 Docker 备选（见 05）；`01` 的 host Debian 不采用  

## 文档

1. [06 ImmortalWrt + Nikki](06-qnap旁路由_nikki_cursor_composer.md) — **当前推荐方案**  
2. [03 实施稿](03-qnap旁路由_opus_5.md) — VS + ImmortalWrt 底座  
3. [04 现场与验收](04-qnap旁路由_cursor_composer.md) — 现场表、易踩坑、回滚  
4. [02 方案排序](02-qnap旁路由_cursor_grok.md) — 为何 VM 优先  
5. [05 Docker 问题](05-docker_shellcrash问题_cursor_composer.md) — 免 Wrt 时再读  
6. [01 Gemini 原稿](01-qnap+shellcrash_gemini.md) — 反例，勿直接照做  

多棒对照表：[00 文稿索引](00-文稿索引.md)
