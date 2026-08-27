---
id: searxng
name: SearXNG
layer: service
priority: P2
category: privacy
goals: [密码与隐私]
summary: 不追踪的聚合搜索
blurb: |
  它自己不索引网页，而是替你去问一堆搜索引擎再把结果汇总起来。
  好处是**不记录你搜过什么、不给你画像**，也没有广告。
  ⚠️ 装好了搜不出东西是常见故障，和你的网络出口有关，选之前先看说明。
docs:
  - type: official
    title: SearXNG 官方文档
    url: https://docs.searxng.org/
requires: {arch: [x86_64, aarch64], substrate: [bare-metal, vm, container]}
conflicts: []
risk: low
needs_human: false
verify: |
  # ★ 不能只测首页能开——必须真的搜出结果
  curl -s 'http://192.0.2.10:8080/search?q=test&format=json' | head -c 200
  # 期望: 返回含结果的 JSON，不是空列表
rollback: |
  docker compose down
---

# SearXNG

元搜索引擎——它自己不索引，而是去问一堆搜索引擎再汇总。

## 最常见的失败：装好了但搜不出东西

首页正常打开，搜索返回空结果或大量引擎报错。**这几乎总是出口 IP 的问题**：

各家搜索引擎会限制来自数据中心、VPN 出口、或高频请求源的访问。
你的出口一旦被判定为"非正常用户"，引擎就返回验证码或直接拒绝。

### 排查顺序

1. **看是哪些引擎失败**——SearXNG 的统计页会列出各引擎的错误率。
   全挂 vs 部分挂，指向完全不同的原因
2. **换出口试**——如果这台机器走旁路由，换个节点地区再试
3. **禁掉持续失败的引擎**，别让它们拖慢每次搜索

### 与代理层的关系

这个服务**对出口地区敏感**。如果它走旁路由，
可以考虑在旁路由上给它指定一个稳定的出口，而不是跟着自动组漂
——理由和方法见 [层 4 · 地区敏感服务](../layers/4-routing-dns.md#地区敏感服务兜底链路会静默杀死它们)。

## 依赖

需要一个 Redis/Valkey 做缓存。

## 架构

官方发 multi-arch。
