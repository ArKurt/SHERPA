---
id: aria2
name: aria2 + AriaNg
layer: service
priority: P0
category: download
goals: [下载]
summary: 常驻的下载器，配一个网页界面
blurb: |
  把下载任务丢给家里那台常开的机器，它慢慢下，你关掉电脑也不受影响。
  支持 HTTP、种子、磁力，网页界面在任何设备的浏览器里都能打开。
  适合「睡前丢一批、早上起来已经好了」这种用法。
docs:
  - type: official
    title: aria2 官方手册
    url: https://aria2.github.io/manual/en/html/
  - type: official
    title: AriaNg 网页界面
    url: https://github.com/mayswind/AriaNg
requires:
  arch: [x86_64, aarch64]
  substrate: [bare-metal, vm, container]
conflicts: []
risk: low
needs_human: false
verify: |
  # 从【另一台设备】调 RPC 接口。
  # ⚠️ 密钥走 stdin（-d @-），不要写进命令行——argv 是所有人可读的。
  read -rs RPC_SECRET
  printf '{"jsonrpc":"2.0","id":"1","method":"aria2.getVersion","params":["token:%s"]}' \
    "$RPC_SECRET" \
    | curl -s -X POST -d @- http://192.0.2.10:6800/jsonrpc
  unset RPC_SECRET
  # 期望: 返回 JSON，含 version 字段
rollback: |
  docker compose down
---

# aria2 + AriaNg

命令行下载器 + 它的 Web 界面。两者是分开的：aria2 提供 RPC，AriaNg 是纯前端。

## RPC 密钥必须设

aria2 的 RPC 接口**默认没有认证**。不设密钥就等于把"往这台机器上任意写文件"的能力
开放给整个局域网。

- 必须设 `--rpc-secret`
- **绝不要把 RPC 端口转发到公网**

## AriaNg 是纯前端

它是一堆静态文件，在**浏览器里**连 aria2 的 RPC。所以：

- AriaNg 和 aria2 可以不在同一台机器上
- 浏览器要能直接访问 aria2 的 RPC 地址
- 如果用反向代理，**AriaNg 和 RPC 要同源**，否则跨域会被浏览器拦下

同源部署（同一个域名下不同路径）是最省事的做法，零额外配置。

## 存储

下载目录要大，放外接盘/网络挂载都行。

⚠️ **磁盘写入权限**：容器内的用户要对下载目录有写权限。
exFAT 没有 POSIX 权限模型，容器挂载时权限行为可能出乎意料——
如果下载一直失败且报权限错误，先查这个。

## 与代理层的关系

下载器通常**不该走代理**——大流量会把代理带宽吃光，影响所有人。

如果这台机器走旁路由，考虑在旁路由上给下载器的目标域名加直连规则，
或者把这台机器排除在旁路由之外。→ [层 4](../layers/4-routing-dns.md)

## 架构

有 multi-arch 镜像，也可以直接装发行版包。
