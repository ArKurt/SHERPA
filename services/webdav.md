---
id: webdav
name: WebDAV
layer: service
priority: P2
category: files
goals: [文件同步]
summary: 最通用的简易文件服务
blurb: |
  开一个目录出来，让别的设备当网络硬盘用。
  它的价值在于**几乎什么都能连**——系统自带的文件管理器、各类 App 大多原生支持，
  不用装专门的客户端。常用来给某个 App 当配置同步的后端。
docs:
  - type: official
    title: hacdias/webdav（一种轻量实现）
    url: https://github.com/hacdias/webdav
requires: {arch: [x86_64, aarch64], substrate: [bare-metal, vm, container]}
conflicts: []
risk: medium              # 明文 HTTP 时凭证会裸奔
needs_human: false
verify: |
  curl -s -u '<user>:<pass>' -o /dev/null -w '%{http_code}\n' http://192.0.2.10:6065/
  # 期望: 200；不带凭证时应为 401
rollback: |
  停止服务；数据是普通文件，不受影响
---

# WebDAV

最简单的自托管文件服务。**它的价值在于"什么都能连"**——
系统文件管理器、各类客户端 App 大多原生支持 WebDAV，不需要装专门的客户端。

典型用途：给某个 App 做配置同步的后端。

## 明文 HTTP 的风险

WebDAV 的认证通常是 Basic Auth ——**凭证经 base64 编码后原样发送，等同明文**。

| 场景 | 可否 |
|---|---|
| 仅局域网、明文 HTTP | ⚠️ 可接受，但知道自己在做什么 |
| 经组网工具访问 | ✅ 组网工具本身加密 |
| **公网 + 明文 HTTP** | ❌ **绝对不行** |
| 公网 + HTTPS | ✅ |

## 客户端填 IP，别填主机名

移动端和部分客户端连 WebDAV 时，**填 IP 地址而不是裸主机名**。

裸主机名在走透明代理的网络里会被解析成假地址，导致连不上——
而错误信息通常只是"连接失败"，看不出是 DNS 的问题。
→ [层 4 坑 ①](../layers/4-routing-dns.md)

## 存储

服务目录随意。注意它暴露的是**真实文件系统**——
只共享你打算共享的目录，别把整个盘挂上去。

## 架构

轻量实现通常是单个二进制，各架构都有。
