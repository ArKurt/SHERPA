# 坑典

> 全手册所有已知坑的索引。**每一条都有同一个特征：症状不指向真凶。**
>
> 这份索引是给"已经出问题了、在找原因"的人用的——按症状查，而不是按层查。

## 按症状查

| 症状 | 多半是 | 在哪 |
|---|---|---|
| 路由器自测能出海，客户端全断 | **裸核模式没关** | [层 3](../layers/3-proxy-stack.md#坑一裸核模式几乎人人踩) |
| 用 IP 能连，用主机名连不上 | fake-ip 吃掉了名字 | [层 4](../layers/4-routing-dns.md#坑一局域网服务访问不了裸主机名) |
| 组网工具 IP 通、名字不通 | 同上，`*.ts.net` 被劫持 | [层 4](../layers/4-routing-dns.md#坑二组网工具的域名被吃掉) |
| DNS 结果随机、时对时错 | 两套 DNS 劫持打架 | [层 4](../layers/4-routing-dns.md#坑三两套-dns-劫持打架) |
| 某服务用着用着掉登录 | 分流漏了 OAuth 域名 | [层 4](../layers/4-routing-dns.md#别抄社区规则集会过期) |
| 某服务某天突然不可用，没人改过配置 | 兜底组漂到了被屏蔽地区 | [层 4](../layers/4-routing-dns.md#地区敏感服务兜底链路会静默杀死它们) |
| 网络时好时坏，换设备表现又不同 | 旁路由的 DHCP 没关干净 | [层 2](../layers/2-gateway.md#为什么绝不能发-dhcp) |
| 两个代理插件都显示运行中，但全断 | 并装了两套透明代理 | [层 3](../layers/3-proxy-stack.md#绝对约束只装一套) |
| 终端 curl 通，服务进程间歇 502 | **幽灵路由**（指向已退役设备） | [层 6](../layers/6-ingress.md#幽灵路由--一类极难诊断的故障) |
| 隧道全挂，换协议好了，过几天又挂 | 固定了隧道传输协议 | [层 6](../layers/6-ingress.md#不要固定隧道传输协议重要) |
| 数据库崩溃重启循环，但原始数据没丢 | 数据库落在会掉线的外接盘上 | [层 5](../layers/5-storage.md#usb-portable--外接移动硬盘) |
| 服务起来了但看不到数据 | 挂载晚于服务启动 | [`ops/boot-persistence.md`](../ops/boot-persistence.md#挂载依赖) |
| 重启后服务没回来，但登录后一看又都正常 | 容器运行时需要登录才启动 | [`ops/boot-persistence.md`](../ops/boot-persistence.md#容器) |
| 两个虚拟机实例抢同一块磁盘 | 用了后台化选项，管理器失去子进程 | [`ops/boot-persistence.md`](../ops/boot-persistence.md#别让虚拟机进程脱离监管) |
| 冷启动后旁路由不可用，登录后才好 | 全盘加密，登录前用户级服务不运行 | [`ops/boot-persistence.md`](../ops/boot-persistence.md#全盘加密会限制自恢复能力) |
| AI CLI 报证书自签，怀疑代理 MITM | **包装器注入了会话代理** | [`advanced/`](../advanced/resident-ai-harness.md#四排查陷阱先剥掉环境变量再下结论) |
| Home Assistant 一个设备都发现不了 | 容器用了默认桥接网络 | [`services/home-assistant.md`](../services/home-assistant.md#发现类集成需要能收到局域网广播) |
| SearXNG 能打开但搜不出东西 | 出口 IP 被搜索引擎限制 | [`services/searxng.md`](../services/searxng.md#最常见的失败装好了但搜不出东西) |
| Immich 主服务崩溃重启循环 | 主服务与 ML 版本不一致 | [`services/immich.md`](../services/immich.md#版本必须钉死且一致) |
| 密码库客户端登录后无法解锁 | 不是 HTTPS，加密上下文不成立 | [`services/vaultwarden.md`](../services/vaultwarden.md#必须是-https) |
| 面板里点某些服务没反应 | 内嵌 iframe + 认证 + 重定向 | [`services/sunpanel.md`](../services/sunpanel.md#打开方式新标签页不要内嵌) |
| WoL 从没成功过 | BIOS 没开，或系统关机时切了网卡电 | [`ops/wol.md`](../ops/wol.md#前置条件清单) |
| 串流卡顿 | 流量走了代理 | [`services/sunshine-moonlight.md`](../services/sunshine-moonlight.md#与代理层的冲突) |
| 我的电脑能开，电视/安卓打不开 | 用了 `.local`，那些设备不支持 mDNS | [层 7](../layers/7-lan-addressing.md#mdns--local-自动发现) |
| 内网域名解析时对时错 | `.local` 当普通 DNS 后缀用，两套机制打架 | [层 7](../layers/7-lan-addressing.md#用什么后缀) |
| 服务 IP 变了，全屋客户端一起失效 | 只做了 `hosts-file`，没做 `lan-dns` | [层 7](../layers/7-lan-addressing.md#hosts-file--客户端硬编) |
| 改了密钥，部分功能好部分不好 | 轮换只改了一半 | [`ops/secrets.md`](../ops/secrets.md#轮换) |
| `.gitignore` 加了但凭证还在库里 | 文件在加之前就已被跟踪 | [`ops/secrets.md`](../ops/secrets.md#1-环境变量文件起步够用) |

## 几条通用规律

这些坑背后有共同的模式，认出模式比记住条目更有用：

### 规律一：「A 能通」不等于「B 能通」

- 核能出海 ≠ 客户端能借道
- 终端 curl 通 ≠ 服务进程连得上
- 从睡眠唤醒成功 ≠ 从关机唤醒成功
- Web 界面能开 ≠ 功能可用

**验证必须在真实的使用路径上做。** 这就是本手册所有 `verify`
都要求"从客户端跑"的原因。

### 规律二：兜底链路会静默失效

任何"其它情况走 X"的兜底，都要问一句：**X 会漂到哪里去？**
如果它可能漂到一个不可用的地方，那么故障是必然的，只是时间问题。
而且它**不报错**。

### 规律三：总开关

很多配置项**各自带一个默认关闭的总开关**。只填了内容没开开关 = 白填，
而且看起来像"配置不生效"，会让你去怀疑语法。

改完配置后回头确认开关状态。

### 规律四：退役的东西会留下影子

关机 ≠ 清理干净。指向已死设备的残留配置会造成间歇性、不可复现、
且症状指向别处的故障。→ [`ops/migration-retirement.md`](../ops/migration-retirement.md)

### 规律五：外部依赖会过期

社区规则集、第三方镜像、非官方分支——**用之前看更新日期和维护活跃度**。
它们不会通知你自己已经过时了。

### 规律六：症状的严重程度和原因的深度无关

最难查的几个坑，症状都很轻微（间歇 502、偶尔掉登录、某个设备发现不了）。
**症状轻不代表原因简单。**
