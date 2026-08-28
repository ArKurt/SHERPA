---
id: sunshine-moonlight
name: Sunshine + Moonlight
layer: service
install_when: anytime
category: remote
goals: [远程访问自己的机器]
summary: 低延迟的桌面与游戏串流
blurb: |
  把家里那台强机器的画面实时传到手上的设备，键鼠手柄都能用。
  可以在客厅电视上玩书房的游戏，或者出门时远程用家里的工作站。
  Sunshine 装在被控的机器上，Moonlight 是你手上的客户端。
docs:
  - type: official
    title: Sunshine 官方文档
    url: https://docs.lizardbyte.dev/projects/sunshine/
  - type: official
    title: Moonlight 客户端
    url: https://moonlight-stream.org/
requires:
  arch: [x86_64, aarch64]
  substrate: [bare-metal]        # 需要直接访问 GPU 与显示会话，容器里很别扭
conflicts: []
risk: medium
needs_human: true
verify: |
  # ★ 唯一有效的验收是用 Moonlight 客户端真的连一次并看到画面
  # HTTP 探活不能证明串流可用
rollback: |
  停止 Sunshine 服务
---

# Sunshine + Moonlight

低延迟桌面 / 游戏串流。Sunshine 是被控端（装在服务器/工作机上），
Moonlight 是客户端。

## 为什么 `substrate: bare-metal`

它需要**抓取一个真实的显示会话并用 GPU 编码**。这两件事在容器里都很麻烦，
在虚拟机里通常拿不到硬件编码器。**原生安装。**

## 需要有人登录

被控端必须处于**已登录的图形会话**中。没登录时：无桌面可抓、无 GPU 会话。

如果要做到"冷启动后无人值守可用"，需要配置自动登录——
**而自动登录意味着物理接触这台机器的人可以直接用它**。这是安全权衡，
所以标了 `needs_human`。

无头运行（不接显示器）时还需要虚拟显示器，配置因平台而异。

## 与代理层的冲突

串流走 UDP、对延迟极其敏感。**流量绝不能走代理**——延迟会毁掉体验。

如果被控端或客户端在旁路由后面，**必须给串流的目标加直连规则**。
→ [层 4 · 保留网段](../layers/4-routing-dns.md#保留网段什么不该被代理)

## 公网访问

要从外网串流的话，需要转发若干端口（含 UDP）。**这触及铁律①**——
告诉用户需要开哪些，由用户自己在主路由上操作。

或者走组网工具，延迟会高一些但零暴露。

## 相关

配合 [`ops/wol.md`](../ops/wol.md) 可以做到"远程唤醒 + 串流进去"。

---

> 📎 **本页断言的出处与强度**：[`appendix/sources.md`](../appendix/sources.md#services-sunshine-moonlight)
