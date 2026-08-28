---
id: home-assistant
name: Home Assistant
layer: service
install_when: anytime
category: home
goals: [智能家居]
summary: 本地优先的智能家居中枢
blurb: |
  把不同品牌的智能设备（灯、插座、传感器、空调、扫地机）统一到一个界面里，
  并且可以写自动化：回家开灯、没人时关空调、门开了推送通知。
  关键是**本地运行** —— 断网也能用，不必把家里的一举一动送到厂商云上。
docs:
  - type: official
    title: Home Assistant 官方文档
    url: https://www.home-assistant.io/docs/
  - type: official
    title: 容器安装方式
    url: https://www.home-assistant.io/installation/
requires:
  arch: [x86_64, aarch64]
  substrate: [bare-metal, vm, container]
  storage: [internal, das-enclosure]      # 配置目录频繁小量写入
conflicts: []
risk: low
needs_human: false
verify: |
  # 从【另一台设备】访问
  curl -s -o /dev/null -w '%{http_code}\n' http://192.0.2.10:8123/
  # 期望: 200 或 302
  # ★ 真正的验收：能不能发现局域网设备。见下
rollback: |
  docker compose down
---

# Home Assistant

家居自动化中枢。**卡点在网络模式，不在安装。**

## 发现类集成需要能收到局域网广播

HA 的很多集成靠 mDNS / SSDP / 广播来发现设备（智能灯、音箱、电视、打印机）。

**这些广播不会穿过容器的默认桥接网络。** 用默认 bridge 模式装 HA，
典型症状是：Web 界面完全正常，但**一个设备都发现不了**，而且不报错。

（这是在 Docker 默认 bridge 上观察到的；HA 官方安装文档一律要求 host 网络，
但没有说明原因——所以上面这个机制解释是社区共识，不是官方原话。）

### 解法

| 方案 | 说明 |
|---|---|
| **host 网络模式** | 最简单，容器直接用宿主的网络栈 |
| **macvlan** | 给容器独立局域网 IP。宿主访问不到它，需另做处理 |
| **原生安装** | 不套容器，天然没这问题 |
| 手工配置每个设备的 IP | 可行但繁琐，且设备 IP 变了就断 |

> ⚠️ **注意与旁路由的区别**：这里说的 host 网络是给 HA 用的，
> 和 [层 2 明确否决的"代理跑 host 网络"](../layers/2-gateway.md#container-macvlan--只在跑不了-vm-时)
> 不是一回事。HA 需要收广播，代理需要独立 IP，需求相反。

## 别把它放在会睡眠的机器上

自动化的意义在于**你不在的时候它还在跑**。宿主睡眠 = 自动化停摆，
而且你不会立刻发现。→ [`ops/boot-persistence.md`](../ops/boot-persistence.md)

## 存储

配置目录会频繁小量写入（状态记录、历史数据库）。放本地盘。
长期历史数据会持续增长，注意定期检查体积。

## 架构

官方发 multi-arch。

## 真正的验收

```sh
# Web 能开只是第一步。真正的验收是：
# 1. 设置 → 设备与服务 → 看有没有自动发现的条目
# 2. 至少接通一个真实设备并能控制它
```

只测 HTTP 200 会漏掉最常见的那个失败。

---

> 📎 **本页断言的出处与强度**：[`appendix/sources.md`](../appendix/sources.md#services-home-assistant)
