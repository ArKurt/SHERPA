---
id: sunpanel
name: SunPanel（导航面板）
layer: service
priority: P1
requires:
  arch: [x86_64, aarch64]
  substrate: [bare-metal, vm, container]
conflicts: []
risk: none
needs_human: false
verify: |
  curl -s -o /dev/null -w '%{http_code}\n' http://192.0.2.10:3002/
  # 期望: 200
rollback: |
  docker compose down
---

# SunPanel

服务导航面板——把你装的一堆服务做成一个入口页。装了七八个服务之后会很需要它。

## 打开方式：新标签页，不要内嵌

面板通常支持"内嵌 iframe 打开"和"新标签页打开"两种。

**对下面这些一律用新标签页**：

- 需要认证的服务（尤其反向代理上的 Basic Auth）
- 路由器/代理的管理界面

原因：跨域 iframe + 认证 + 目标页面自己的重定向，三者叠加会失效，
而且**症状是"点了没反应"，看不出是哪一环的问题**。

真实案例：路由器和代理面板配成内嵌模式，点击无反应；
排查一轮后才发现内嵌本身就是失败原因——**而当时还误判成了别的问题**。

## 存储

配置是个小数据库，放本地盘。改过配置后记得备份——重建面板的图标和分组很烦。

## 架构

有 multi-arch 镜像。
