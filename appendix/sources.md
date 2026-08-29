# 手册断言的出处与强度

> 本附录合并自第四轮「出处标注」的三份独立报告（由三个不同的模型分工完成，
> 各自逐条去核手册断言在上游文档里到底怎么写）。三份报告的共同基线为 `6f593fa`；
> 外部资料最后核对日期为 2026-08-28。行号是该基线的定位提示，后续编辑可能使其漂移。
>
> 标记含义：`[官方]` 为上游文档、源码、RFC 或标准明文；`[实测]` 为具体环境观察；
> `[社区]` 为可查的社区报告；`[推理]` 为由已知机制推出但未直接验证。
>
> ---
>
> ⚠️ **怎么读这份附录：它是「当时的证据记录」，不是「现在的手册内容」。**
>
> 每条里的「**手册怎么说**」引的是**基线 `6f593fa` 时的措辞**。
> 而「**是否需改写**」的建议，**批次 2 与批次 3 已经全部落地到正文了**。
>
> 所以顺着正文页尾那行链接过来的人会看到一种时态错位：
> 条目说「手册说 X（建议改成 Y）」，而正文早就是 Y 了。**这是预期的。**
>
> - **要知道手册现在怎么说 → 看正文。**
> - **要知道这个说法的依据有多硬、当初为什么改 → 看这里。**
>
> ---
>
> 🔴 **摘录规则（这条是用一次真实错误换来的，别省）**
>
> **摘一句规范性语句时，必须把紧随其后的限定、例外、反向许可一起摘。**
>
> 代价实例：`.local` 那条只摘了 RFC 6762 的 “MUST be sent to the mDNS … multicast
> address”，漏掉了下一句的 “MAY choose to look up such names concurrently via
> …Unicast DNS”。附录据此建议正文"改得更强"，正文照做，**结论就从"冲突且不可预测"
> 变成了不实的"根本不会生效"**。
>
> 📌 **一个专门用来防止误引上游的附录，因为截断了一句话，亲手生产了一次误引。**
> `MUST 做 A` 从来不等于 `MUST NOT 做 B` —— 摘录时把这两件事分清楚。
>
> 逐条标了「状态」的是已经单独确认过落地的；没标的不代表没改，
> 只代表没有逐条记录。**判断现行内容一律以正文为准。**
>
> 本附录记录证据强度与建议措辞，不把单次观察升级为普适结论。没有逐字原文的条目
> 明示为“取证受限”或“无逐字上游原文”。

## layers/1-substrate.md
<a id="layers-1-substrate"></a>

### L65 · `sysctl kern.hv_support` 为 `1` 即可用 hvf，VM 性能接近原生

- **强度**：[官方]（可用性）+ [推理]（性能）
- **出处/依据**：https://developer.apple.com/documentation/hypervisor ； https://www.qemu.org/docs/master/system/introduction.html
- **原文/取证说明**：Apple："At runtime, determine whether the Hypervisor APIs are available on a particular machine with the sysctl command, passing `kern.hv_support` as an argument."；QEMU 只把 `Hypervisor Framework (hvf)` 列为 macOS 的 accelerator，没有给“接近原生”的性能承诺。
- **手册怎么说**："`sysctl kern.hv_support` 为 `1` 即可用 hvf，VM 性能接近原生"
- **是否需改写**：**是** —— 建议：「macOS：`kern.hv_support=1` 表示该机可用 Apple Hypervisor API；QEMU 可选 `hvf` 加速器。性能需在目标负载上实测，本文无 ‘接近原生’的可引用基准。」
- **来源报告**：`S1`

### L66 · `/dev/kvm` 存在且可读写。不存在多半是 BIOS 没开 VT-x/AMD-V

- **强度**：[官方]（设备节点是 KVM API 入口）+ [推理]（缺失原因）
- **出处/依据**：https://docs.kernel.org/virt/kvm/api.html
- **原文/取证说明**："An initial open('/dev/kvm') obtains a handle to the kvm subsystem; this handle can be used to issue system ioctls."
- **手册怎么说**："`/dev/kvm` 存在且可读写。不存在多半是 BIOS 没开 VT-x/AMD-V"
- **是否需改写**：**是** —— 上游只支持“可打开 `/dev/kvm` 才能使用 KVM API”，不支持 “不存在多半是 BIOS”。建议：「Linux：以当前执行用户能打开 `/dev/kvm` 为 准。缺失或不可访问可能来自硬件/固件虚拟化、内核模块、权限或嵌套虚拟化限制； 不要直接把原因判成 BIOS，按现场报告继续查。」
- **来源报告**：`S1`

### L82-85 · 把旁路由、容器宿主、代码仓库三个职能压在一台老笔记本上…… 盘一走，数据库进入崩溃重启循环，几千次

- **强度**：[实测]
- **出处/依据**：`blueprints/a-single-laptop.md` 的单次事故记录
- **原文/取证说明**："一台 x86_64 老笔记本"、"17 个容器"、"USB 盘被物理移除后，数据库 在空挂载点上反复初始化/重启数千次"。记录没有宿主系统/VM/数据库版本，也没有 事故年份。
- **手册怎么说**："把旁路由、容器宿主、代码仓库三个职能压在一台老笔记本上…… 盘一走，数据库进入崩溃重启循环，几千次"
- **是否需改写**：**是（补限定与元数据缺口）** —— 建议：「在锚点 A 的一台 x86_64 老 笔记本（服务与 OpenWrt VM 合体、17 个容器；软件版本和事故年份未记录）上， 曾观察到 USB 盘移除后数据库在空挂载点反复初始化/重启数千次。」不要把这次 事故写成所有合体方案或所有数据库的确定结果。
- **来源报告**：`S1`

### L91-94 · 宿主机自己的默认网关必须指向主路由……否则会死锁

- **强度**：[推理]
- **出处/依据**：起点是“宿主默认路由依赖宿主内尚未启动的 VM”；未找到虚拟化上游把该 拓扑写成普适死锁。是否真死锁还取决于 VM 启动是否需要联网、宿主是否有备用路由。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："宿主机自己的默认网关必须指向主路由……否则会死锁"
- **是否需改写**：**是（轻度）** —— 建议：「不要让宿主的唯一默认路由依赖同一宿主里 尚未启动的旁路由 VM；如果 VM 启动或修复需要外网，这会形成启动依赖环。」
- **来源报告**：`S1`

### L98-101 · 桥接会短暂中断……有第二条路才能在出问题时不失联

- **强度**：[推理]
- **出处/依据**：起点是“重配正在承载管理会话的接口可能中断该会话”；未找到跨 macOS、 Linux、NAS 和各网络管理器都保证中断的官方原文。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："桥接会短暂中断……有第二条路才能在出问题时不失联"
- **是否需改写**：**是（轻度）** —— 建议：「重配正在使用的网卡为桥接时可能中断管理 会话；操作前准备独立管理链路或可触达的物理控制台。」
- **来源报告**：`S1`

### L107 · 硬件加速用 hvf，性能接近原生

- **强度**：[官方]（hvf 是加速器）+ [推理]（性能）
- **出处/依据**：同 L65。
- **原文/取证说明**：QEMU："Hypervisor Framework (hvf) | MacOS | x86, Arm"。
- **手册怎么说**："硬件加速用 hvf，性能接近原生"
- **是否需改写**：**是** —— 建议：「硬件加速使用 hvf；本文没有可引用的‘接近原生’ 基准，性能在目标工作负载上验收。」
- **来源报告**：`S1`

### L108-109 · FileVault 会让开机自启动不可靠：登录前用户级服务不运行

- **强度**：[官方]（两个条件分别成立）+ [推理]（合并后的后果）
- **出处/依据**：https://support.apple.com/en-ie/102316 ； https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html
- **原文/取证说明**：Apple Support："manual login is required" when "FileVault is turned on."；Apple Developer："A user agent ... executes only while that user is logged in."
- **手册怎么说**："FileVault 会让开机自启动不可靠：登录前用户级服务不运行"
- **是否需改写**：**是** —— FileVault 并不让所有系统级 daemon 都不可靠。建议：「若 VM 依赖 Login Item 或 LaunchAgent，FileVault 开启后重启必须先人工登录，用户级 agent 才会运行；LaunchDaemon 是另一种启动语义，需按实际实现核对。」
- **来源报告**：`S1`

### L120-122 · 旁路由跑在 NAS 上，意味着 NAS 重启 = 全屋断网

- **强度**：[推理]
- **出处/依据**：起点是“全屋客户端的唯一网关在该 NAS 内运行”；这是拓扑推论，不是 NAS 厂商的跨产品保证。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："旁路由跑在 NAS 上，意味着 NAS 重启 = 全屋断网"
- **是否需改写**：**是（轻度）** —— 建议：「若全屋客户端把运行在 NAS 上的 VM 设为 唯一网关，则 NAS 或该 VM 停机期间这些客户端失去这条网关路径。」
- **来源报告**：`S1`

## layers/2-gateway.md
<a id="layers-2-gateway"></a>

### L117-118 · macvlan 的宿主不可达问题——宿主机默认访问不到自己上面 macvlan 容器的 IP。

- **强度**：`[官方]`
- **出处/依据**：<https://docs.docker.com/engine/network/drivers/macvlan/>
- **原文/取证说明**：“Containers attached to a macvlan network cannot communicate with the host directly”；“connect the containers to a bridge network as well as the macvlan”
- **手册怎么说**：**macvlan 的宿主不可达问题**——宿主机默认**访问不到**自己上面 macvlan 容器的 IP。
- **是否需改写**：**是** —— 建议：「macvlan 默认隔离宿主；若宿主必须访问该容器，按 Docker 官方给出的 bridge 双接入或宿主 macvlan 接口方案设计并验收。」
- **来源报告**：`S3`

### L110–111 · 容器要当旁路由必须有独立的局域网 IP，所以需要 macvlan 或等价的网络模式。默认的 bridge/NAT 模式不行，host 模式更不行。

- **强度**：`[推理]`（由 macvlan 的官方限制 + 单臂旁路由的需求推出）
- **出处/依据**：无单一上游出处；推理起点见“原文/取证说明”。
- **原文/取证说明**：无逐字上游原文；推理起点：报告所列机制
- **手册怎么说**：容器要当旁路由必须有**独立的局域网 IP**，所以需要 macvlan 或等价的网络模式。默认的 bridge/NAT 模式不行，host 模式更不行。
- **是否需改写**：否，但**建议标为推理**。它是从两个已确认前提推出的，不是某处文档写明的。
- **来源报告**：`S3`

## layers/3-proxy-stack.md
<a id="layers-3-proxy-stack"></a>

### L17-22 · 两套会各自往防火墙里塞流量劫持规则……客户端连不上任何东西

- **强度**：[推理]
- **出处/依据**：Nikki 官方 README 写其启动流程会 "Set ip rule/route"、"Generate nftables and apply it"：https://github.com/nikkinikki-org/OpenWrt-nikki ； OpenClash 默认配置也声明会接管 transparent proxy 端口： https://github.com/vernesong/OpenClash/blob/master/luci-app-openclash/root/usr/share/openclash/res/default.yaml 。未找到上游保证“两套并装必然表现为客户端全断”的原文。
- **原文/取证说明**：Nikki："Set ip rule/route"；"Generate nftables and apply it."
- **手册怎么说**："两套会各自往防火墙里塞流量劫持规则……客户端连不上任何东西"
- **是否需改写**：**是（保留硬约束）** —— 建议：「本手册禁止并装两套透明代理。理由是 两套都可能管理策略路由、防火墙和透明代理入口，规则所有权重叠；实际症状取决于 各栈实现，不保证一定是‘两个面板正常、客户端全断’。」
- **来源报告**：`S1`

### L30 / L78 · Nikki 只吃 Clash / mihomo YAML"；"含 `proxies` 或 `proxy-providers`

- **强度**：[官方]
- **出处/依据**：https://github.com/nikkinikki-org/OpenWrt-nikki/wiki ； https://github.com/nikkinikki-org/OpenWrt-nikki/blob/main/nikki/files/nikki.init
- **原文/取证说明**："订阅下载成功后会校验是否是正确的yaml格式，且必须包含`proxies`或 `proxy-providers`，如果校验失败则不会保存。"；源码判定为 `has("proxies") or has("proxy-providers")`。
- **手册怎么说**："Nikki 只吃 Clash / mihomo YAML"；"含 `proxies` 或 `proxy-providers`"
- **是否需改写**：否
- **来源报告**：`S1`

### L31 · ShellCrash 吃得杂，转换能力强

- **强度**：[官方]（多内核和导入）+ [推理]（“吃得杂/转换强”）
- **出处/依据**：https://github.com/juewuy/ShellCrash
- **原文/取证说明**："Multi-Kernel Support: Easily manage and switch between mihomo and sing-box kernels"；"Supports online import of subscription links and configuration files"。README 没有列出保证接受的订阅格式，也没有“转换能力强” 的可核边界。
- **手册怎么说**："ShellCrash 吃得杂，转换能力强"
- **是否需改写**：**是** —— 建议：「ShellCrash 支持 mihomo/sing-box 内核，并支持在线 导入订阅链接和配置文件；具体订阅格式必须按当前版本文档或一次无凭证泄露的格式 探测确认，不以‘吃得杂’作为准入保证。」
- **来源报告**：`S1`

### L32 · OpenClash：mihomo；Clash 系 YAML

- **强度**：[官方]
- **出处/依据**：https://github.com/vernesong/OpenClash/blob/master/README.md ； https://github.com/vernesong/OpenClash/wiki/%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6
- **原文/取证说明**："本插件是一个可运行在 OpenWrt 上的 Mihomo(Clash) 客户端"； "OpenClash 使用`yaml`格式（兼容`yml`格式）的配置文件"。
- **手册怎么说**："OpenClash：mihomo；Clash 系 YAML"
- **是否需改写**：否
- **来源报告**：`S1`

### L33 / L80 · HomeProxy 的订阅格式是 sing-box JSON

- **强度**：[官方]（源码；且原断言不实）
- **出处/依据**：https://github.com/immortalwrt/homeproxy/blob/master/root/etc/homeproxy/scripts/update_subscriptions.uc 原文代码: `nodes = json(res).servers || json(res);`； `/* Shadowsocks SIP008 format */`；`nodes = decodeBase64Str(res);`； `config = parse_uri(node);`；`case 'ss':`；`case 'trojan':`； `case 'vless':`；`case 'vmess':`；`case 'hysteria2':`。
- **原文/取证说明**：逐字源码片段已列在“出处/依据”中。
- **手册怎么说**："HomeProxy 的订阅格式是 sing-box JSON"
- **是否需改写**：**是** —— 建议：「HomeProxy 由 sing-box 驱动；其订阅更新器接受 SIP008/节点 URI 列表等并生成 sing-box JSON。不要把‘运行时配置是 JSON’写成 ‘订阅必须是 sing-box JSON’；准入格式按当前 `update_subscriptions.uc` 支持列表 核对。」
- **来源报告**：`S1`

### L82-83 · 同一个 URL 会按请求头返回不同格式；换 User-Agent 往往能拿到 Clash 版

- **强度**：[推理]
- **出处/依据**：Nikki 官方只确认订阅有可填写的“用户代理（UA）”，ShellCrash 官方只确认 可导入订阅；没有找到服务商或插件上游支持“同 URL 往往会切格式”的普适原文。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："同一个 URL 会按请求头返回不同格式；换 User-Agent 往往能拿到 Clash 版"
- **是否需改写**：**是** —— 建议：「有些订阅服务可能按 User-Agent 返回不同表示；这是 服务端行为，不是插件保证。若服务商文档给出指定 UA，再按文档尝试。」
- **来源报告**：`S1`

### L90-100 · 代理插件普遍有裸核模式……防火墙劫持规则全部不生效……客户端全断

- **强度**：[官方]（**仅 Nikki**）+ [实测]（单次故障症状）
- **出处/依据**：https://github.com/nikkinikki-org/OpenWrt-nikki/wiki ； https://github.com/nikkinikki-org/OpenWrt-nikki/discussions/886
- **原文/取证说明**：Nikki Wiki："仅核心：是否仅运行核心，启用时将禁用混入和代理，仅启动 核心。"；维护者说明裸核可自行开 TUN，并写道："如果你既不需要本机/局域网 客户端的分流，也不需要绕过大陆，也不使用 TProxy，那么其实没什么区别。" OpenClash、ShellCrash、HomeProxy 未核到同义且同语义的开关。手册所写 “路由器自测 204、客户端全断”来自一个 Nikki 场景，但事故的软件版本/年份未记。
- **手册怎么说**："代理插件普遍有裸核模式……防火墙劫持规则全部不生效……客户端全断"
- **是否需改写**：**是** —— 建议：「**Nikki 用户**切到旁路由集成时，先确认‘仅核心’已按 设计处理：该开关会禁用 Nikki 的混入和代理集成。若选择让 mihomo 裸核自行用 TUN/auto-route，则不能据此断言‘所有劫持都没有’或‘客户端必断’，必须从客户端 逐项验收。其它插件是否存在同类模式，以各自版本文档为准。」保留“核能出海不等于 客户端能借道”作为验收原则，但不要把单插件事故写成跨插件定律。
- **来源报告**：`S1`

### L104-116 · 旁路由上按进程分流（PROCESS-NAME）不工作

- **强度**：[推理]（转发流量）+ [官方]（内核能力边界的旁证）
- **出处/依据**：https://wiki.metacubex.one/en/config/general/ ； https://wiki.metacubex.one/en/config/rules/ ； https://github.com/MetaCubeX/mihomo/issues/3135
- **原文/取证说明**：Mihomo："PROCESS-NAME: Matches using the process name"； `find-process-mode: off` 为 "Does not match processes, recommended for use on routers."。官方 issue 的 Linux 复现把查找链写成 socket UID → inode → process path；远端客户端的进程不在旁路由本机的 socket/process 表中。
- **手册怎么说**："旁路由上按进程分流（PROCESS-NAME）不工作"
- **是否需改写**：**是（限定对象）** —— 建议：「旁路由不能用 `PROCESS-NAME` 识别 **LAN 客户端转发流量在源客户端上的进程**；它没有源设备的本机 socket/进程表。 旁路由本机发起的流量仍可能匹配本机进程，因此不要写成‘旁路由上全部不工作’。」
- **来源报告**：`S1`

### L127-129 · 工作机要么走旁路由、要么走本机客户端，不要叠加（叠加会绕出 难以预测的路径）

- **强度**：[推理]
- **出处/依据**：起点是两层代理会改变 DNS、路由与出口；未找到证明所有叠加都不可预测的 上游原文，显式链式代理本身也是合法设计。
- **原文/取证说明**：无逐字上游原文；推理起点：起点是两层代理会改变 DNS、路由与出口；未找到证明所有叠加都不可预测的 上游原文，显式链式代理本身也是合法设计。
- **手册怎么说**："工作机要么走旁路由、要么走本机客户端，不要叠加（叠加会绕出 难以预测的路径）"
- **是否需改写**：**是** —— 建议：「不要无设计地叠加本机客户端与旁路由。若确需链式代理， 必须明确 DNS、直连例外、出口和回滚路径，并分别验收；本文不提供该路径。」
- **来源报告**：`S1`

### L137 · 代理插件默认接管的通常只有 IPv4

- **强度**：[推理]
- **出处/依据**：Nikki 官方 Wiki 只证明 IPv4/IPv6 是分开的开关： https://github.com/nikkinikki-org/OpenWrt-nikki/wiki ，原文为 "IPv4/IPv6 代理：是否启用 IPv4/IPv6 代理。"；Mihomo 内核文档反而写 `ipv6` 默认 `true`：https://wiki.metacubex.one/en/config/general/ ，原文 "Available values: `true/false`. Default: `true`." 内核接收 IPv6 与插件是否 劫持 IPv6又不是同一层。没有跨插件默认值统计。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："代理插件默认接管的通常只有 IPv4"
- **是否需改写**：**是** —— 建议：「不要假定 IPv6 已被接管。分别核对所选插件的 IPv6 代理开关、DNS 劫持与内核 `ipv6` 配置，并用 `-4`/`-6` 分族验收。」
- **来源报告**：`S1`

### L138-141 · 双栈站点时系统可能优先走 IPv6

- **强度**：[官方]
- **出处/依据**：https://www.rfc-editor.org/rfc/rfc8305.html
- **原文/取证说明**："while preferring the use of IPv6"；"the preference policy for the host destination address favors IPv6 over IPv4."
- **手册怎么说**："双栈站点时系统可能优先走 IPv6"
- **是否需改写**：否 —— 原文用“可能”，没有升级成每次必走 IPv6。
- **来源报告**：`S1`

### L170-171 · 下错架构的包，症状是装上了但内核起不来"；"发行版打包的一键 脚本版本往往滞后

- **强度**：[推理]
- **出处/依据**：未找到四个插件上游共同支持这两个具体症状/频率的原文。
- **原文/取证说明**：无逐字上游原文；推理起点：未找到四个插件上游共同支持这两个具体症状/频率的原文。
- **手册怎么说**："下错架构的包，症状是装上了但内核起不来"；"发行版打包的一键 脚本版本往往滞后"
- **是否需改写**：**是（轻度）** —— 建议：「安装前核对包支持的系统、CPU 架构、内核与 防火墙版本；安装来源优先级按所选项目官方文档，不用‘往往滞后’作无出处判据。」
- **来源报告**：`S1`

## layers/4-routing-dns.md
<a id="layers-4-routing-dns"></a>

### L18-19 · 透明代理普遍默认开 fake-ip

- **强度**：[官方]（Mihomo 默认值；且原断言不实）
- **出处/依据**：https://wiki.metacubex.one/config/dns/
- **原文/取证说明**："可选值 `fake-ip`/`redir-host`，默认`redir-host`"。
- **手册怎么说**："透明代理普遍默认开 fake-ip"
- **是否需改写**：**是** —— 建议：「部分透明代理配置会启用 fake-ip；**Mihomo 内核的 `enhanced-mode` 默认值是 `redir-host`，不是 fake-ip**。先读当前生效配置，只有 确认启用 fake-ip 才应用本节后续判据。」
- **来源报告**：`S1`

### L18-24 · fake-ip 返回保留段假地址……为了让代理拿到域名

- **强度**：[官方]（配置行为）+ [推理]（目的表述）
- **出处/依据**：https://wiki.metacubex.one/config/dns/
- **原文/取证说明**：`enhanced-mode: fake-ip`；`fake-ip-range: 198.18.0.1/16`； "以下地址不会下发 fakeip 映射用于连接"。官方没有 “否则所有域名规则全失效”的原文。
- **手册怎么说**："fake-ip 返回保留段假地址……为了让代理拿到域名"
- **是否需改写**：**是（轻度）** —— 建议：「fake-ip 模式会对未过滤的名字下发映射地址， 连接时借此保留域名映射；具体范围读 `fake-ip-range`，不要把示例 `/16` 或常见 `/15` 当成固定值。」
- **来源报告**：`S1`

### L39 · 三条都有同一个陷阱：相关开关默认是关的

- **强度**：[实测]（仅 Nikki 一套配置）
- **出处/依据**：作者共享知识库的现场记录《Nikki 规则覆写（mixin）与服务固定落地》（ImmortalWrt VM、Nikki/mihomo、2026-08-27；非公开记录，内部地址已省略）
- **原文/取证说明**："`mixin_file_content` 默认是 `0` —— 光写 `mixin.yaml` 不生效,必须置 1。" 这只验证混入文件总开关，没有验证表中三项、也没有验证其它插件。
- **手册怎么说**："三条都有同一个陷阱：相关开关默认是关的"
- **是否需改写**：**是** —— 建议：「在 2026-08-27 的这套 Nikki 配置中， `mixin_file_content` 默认 0；其它 DNS/过滤开关和其它插件的默认值未验证。 应逐项读取当前生效配置，不要统一假定‘默认关闭’。」
- **来源报告**：`S1`

### L41 · 过滤列表通常是整表替换语义

- **强度**：[官方]（仅 Nikki 合并实现）+ [推理]（跨插件外推）
- **出处/依据**：https://github.com/nikkinikki-org/OpenWrt-nikki/blob/main/nikki/files/nikki.init 原文代码: `eval-all`；`. as $item ireduce ({}; . * $item )`； `.rules = .nikki-rules + .rules`。这能核 Nikki 当前实现，但不是 “多数插件”的统计。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："过滤列表通常是整表替换语义"
- **是否需改写**：**是** —— 建议：「数组是追加还是替换取决于所选插件的合并实现。 Nikki 当前对 `nikki-rules` 显式前置，对其它数组按 yq 深合并表达式处理；应用前 对临时副本检查最终数组，不把一种实现推广到所有插件。」
- **来源报告**：`S1`

### L57-61 · 自动组按延迟挑节点……Anthropic（Claude）屏蔽香港，OpenAI 有 类似限制

- **强度**：[官方]（支持地区）+ [实测]（一套分流环境）+ [推理]（“屏蔽”动作）
- **出处/依据**：https://www.anthropic.com/supported-countries ； https://help.openai.com/en/articles/5347006-openai-api-supported-countries-and-territories ；另有作者的一次实测环境（2026-08，未公开）
- **原文/取证说明**：Anthropic："Countries, regions, and territories where we currently offer commercial API access"，其清单不含 Hong Kong；OpenAI："If a location is not included in the list below, our API is not supported there."，清单也 不含 Hong Kong。作者在一套 Nikki/mihomo 环境上实测到：兜底的自动组可能落到香港，因此把 Claude 单独钉到了一个支持地区并验证了分流链。官方没有“所有产品按香港出口 IP 一律屏蔽”的原文。
- **手册怎么说**："自动组按延迟挑节点……Anthropic（Claude）屏蔽香港，OpenAI 有 类似限制"
- **是否需改写**：**是** —— 建议：「截至 2026-08-28，Anthropic 与 OpenAI API 的官方 支持地区清单均不含香港；官方措辞是‘不在支持范围’，不是‘屏蔽’。实测中兜底的自动组 可能落到不受支持的地区，所以要把这类服务单独钉到一个支持地区并验证分流链； 不要把一次实测升级为所有产品/账号/出口的永久定律。」
- **来源报告**：`S1`

### L92-95 · 域名少而稳定的服务（一年变不了一次），照官方 allowlist 写死后缀

- **强度**：[推理]
- **出处/依据**：查了 Anthropic 当前网络要求；官方列表会随产品面变化，未找到“一年变不了 一次”或“永久完整 allowlist”的承诺。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："域名少而稳定的服务（一年变不了一次），照官方 allowlist 写死后缀"
- **是否需改写**：**是** —— 建议：「域名条目较少时，可从该产品当前官方网络要求建立本地 规则；记录核对日期并定期复核。不要承诺一年不变，也不要把某一产品面的清单当作 覆盖 Web/API/Desktop/CLI 的永久全集。」
- **来源报告**：`S1`

### L98-100 · 某规则集漏掉 OAuth 令牌刷新域名，表现为用着用着掉登录

- **强度**：[实测]（规则差异与分流）+ [官方]（端点用途）
- **出处/依据**：https://github.com/blackmatrix7/ios_rule_script/blob/master/rule/Clash/Claude/README.md ； https://code.claude.com/docs/en/network-config ；以及上述 2026-08-27 Nikki runbook。
- **原文/取证说明**：社区规则页："最后更新时间：2025-06-06 09:20:01"、"TOTAL | 3"； Anthropic："OAuth token exchange, refresh, and revocation also go to `platform.claude.com`"。现场记录：该 3 条规则漏 `claude.com`/`platform.claude.com`/`claudeusercontent.com`。但记录没有一条 受控实验直接证明“掉登录”已经由该遗漏触发；这部分仍是机制推断。
- **手册怎么说**："某规则集漏掉 OAuth 令牌刷新域名，表现为用着用着掉登录"
- **是否需改写**：**是（轻度）** —— 建议：「2026-08-27 核对时，该社区 Claude 规则页 只有 3 条、标注最后更新 2025-06-06，且未覆盖官方说明承载 OAuth 刷新的 `platform.claude.com`；因此存在登录续期失败风险。‘用着用着掉登录’是预期症状， 不是这次核对已复现的结果。」
- **来源报告**：`S1`

### L104-112 · 多数插件提供混入/覆写；典型顺序是订阅→混入文件→界面配置； 混入文件默认停用

- **强度**：[官方]（仅 Nikki）+ [推理]（跨插件）
- **出处/依据**：https://github.com/nikkinikki-org/OpenWrt-nikki/blob/main/nikki/files/nikki.init ； https://github.com/nikkinikki-org/OpenWrt-nikki/wiki
- **原文/取证说明**：Nikki Wiki："追加的代理节点/规则将插入到最前面"；源码用 `mixin_file_content` 决定是否把 `$MIXIN_FILE_PATH` 交给 yq。没有跨插件共同顺序。
- **手册怎么说**："多数插件提供混入/覆写；典型顺序是订阅→混入文件→界面配置； 混入文件默认停用"
- **是否需改写**：**是** —— 建议：「Nikki 当前实现会把 `nikki-rules`/`nikki-proxy-groups` 前置，并由 `mixin_file_content` 控制混入文件；其它插件的合并顺序、数组语义和 默认开关必须分别查当前版本。」
- **来源报告**：`S1`

### L139-154 · 多数 mihomo 系内核提供 HTTP 控制接口；`/rules`、`/proxies`、 `/connections` 可看规则、选择和实际链

- **强度**：[官方]（Mihomo）
- **出处/依据**：https://wiki.metacubex.one/en/api/
- **原文/取证说明**：`/rules`："Retrieve rule information"；`/proxies`："Retrieve proxy information"；`/connections`："Retrieve connection information"，字段包括 `chains`、`rule`、`rulePayload`。
- **手册怎么说**："多数 mihomo 系内核提供 HTTP 控制接口；`/rules`、`/proxies`、 `/connections` 可看规则、选择和实际链"
- **是否需改写**：**是（轻度）** —— 把“多数 mihomo 系”改为「Mihomo 提供 HTTP API； 所选插件是否暴露、监听在哪、是否启用密钥，以插件配置为准」。
- **来源报告**：`S1`

### L217 · 多数插件默认就包含这些保留网段

- **强度**：[推理]
- **出处/依据**：核过 Nikki、Mihomo 文档，没有得到四插件默认规则的同口径清单；Mihomo DNS 示例中的 `100.64.0.0/10` 还是 fallback-filter 示例，不等于透明代理默认直连。
- **原文/取证说明**：无逐字上游原文；推理起点：核过 Nikki、Mihomo 文档，没有得到四插件默认规则的同口径清单；Mihomo DNS 示例中的 `100.64.0.0/10` 还是 fallback-filter 示例，不等于透明代理默认直连。
- **手册怎么说**："多数插件默认就包含这些保留网段"
- **是否需改写**：**是** —— 建议：「不要依赖插件默认值；从最终生效规则中确认本地网段、 Tailscale CGNAT、ULA 与 loopback 直连且不被劫持。」
- **来源报告**：`S1`

## layers/5-storage.md
<a id="layers-5-storage"></a>

### L23-27 / L96 · 十几个服务的配置卷加起来往往不到 1 GB"；"状态数据一律 优先放内置盘，它总共不过 1 GB 量级

- **强度**：[实测]（单一部署）
- **出处/依据**：锚点 A 的现场记录只说该部署的状态数据小；现行 Immich 官方 requirements 反例为 https://docs.immich.app/install/requirements ，原文："The Postgres database files are typically between 1-3 GB in size."
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："十几个服务的配置卷加起来往往不到 1 GB"；"状态数据一律 优先放内置盘，它总共不过 1 GB 量级"
- **是否需改写**：**是** —— 建议：「锚点 A 的那套部署曾观察到状态数据相对媒体很小， 但不能据此给所有服务写 `<1 GB`。按所选服务官方容量说明与现场占用实测预留； 例如现行 Immich 文档称其 Postgres 文件通常为 1–3 GB。」
- **来源报告**：`S1`

### L29-30 · 最常见也最致命的错误：把数据库和媒体库放同一块外接盘

- **强度**：[实测]
- **出处/依据**：锚点 A 的一次事故；没有事故统计能支持“最常见”。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："最常见也最致命的错误：把数据库和媒体库放同一块外接盘"
- **是否需改写**：**是** —— 建议：「本手册素材里有一次高代价事故：数据库与媒体同在 USB 直通盘，盘移除后数据库反复重启。它证明需要分离故障域，不证明这是所有 部署中‘最常见’的错误。」
- **来源报告**：`S1`

### L56 / L62 / L71 · 可写媒体需要 POSIX 权限——exFAT 不行；挂给相册上传目录就会出权限问题；表格把 exFAT 可写媒体列为绝对不适用

- **强度**：[官方]（Linux 内核源码；原绝对结论不实）
- **出处/依据**：https://github.com/torvalds/linux/blob/master/fs/exfat/super.c
- **原文/取证说明**：`fsparam_uid("uid", Opt_uid)`、`fsparam_gid("gid", Opt_gid)`、 `fsparam_u32oct("umask", Opt_umask)`、`fsparam_u32oct("dmask", Opt_dmask)`、 `fsparam_u32oct("fmask", Opt_fmask)`；解析后写入 `opts->fs_uid`、 `opts->fs_gid`、`opts->fs_fmask`、`opts->fs_dmask`，inode 使用 `inode->i_uid = sbi->options.fs_uid` 和 `inode->i_gid = sbi->options.fs_gid`。
- **手册怎么说**："可写媒体需要 POSIX 权限——exFAT 不行"；"挂给相册上传 目录就会出权限问题"；表格把 exFAT 可写媒体列为绝对 ❌
- **是否需改写**：**是** —— 建议：「exFAT 不存逐文件 POSIX 属主/权限，但 Linux 驱动可用 `uid=`/`gid=`/`umask=`/`dmask=`/`fmask=`把**整个挂载**呈现为目标容器可写。 可写媒体可走这一分支：按容器实际 UID/GID 挂载，并以该容器身份做小规模创建、 改写、重启后再写的验收；需要逐文件 chown/chmod、硬链接或数据库语义的用途仍 不合格。」
- **来源报告**：`S1`

### L71 / L74 · exFAT 数据库绝对不行；没有 POSIX 权限、没有硬链接、日志能力很弱

- **强度**：[官方]（缺失语义）+ [推理]（数据库政策）
- **出处/依据**：https://github.com/torvalds/linux/blob/master/fs/exfat/namei.c ； https://learn.microsoft.com/en-us/windows/win32/fileio/exfat-specification 原文代码（`exfat_dir_inode_operations` 的全部成员）: `.create`、`.lookup`、 `.unlink`、`.mkdir`、`.rmdir`、`.rename`、`.setattr`、`.getattr`、 `.fileattr_get`。Microsoft："TexFAT is an extension to exFAT that adds transaction-safe operational semantics on top of the base file system."
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："exFAT 数据库绝对不行；没有 POSIX 权限、没有硬链接、日志能力很弱"
- **是否需改写**：**是（保住结论，校准依据）** —— 建议：「本手册不把数据库放 exFAT： base exFAT 不提供逐文件 POSIX 属主/权限，Linux exFAT inode operations 没有 hard-link 操作，transaction-safe 语义属于另一个 TexFAT 扩展。对具体数据库还要 另查其上游要求；在未查到时，这是保守的手册准入政策，不要谎称所有数据库上游 都明文禁止。」
- **来源报告**：`S1`

### L75-76 · 服务一写就报权限错误，而且挂载参数怎么调都绕不过去

- **强度**：[官方]（内核源码；原断言不实）
- **出处/依据**：同上 `fs/exfat/super.c`。
- **原文/取证说明**：同上五个挂载参数。
- **手册怎么说**："服务一写就报权限错误，而且挂载参数怎么调都绕不过去"
- **是否需改写**：**是** —— 建议：「若容器只需要统一的属主/掩码，Linux exFAT 挂载参数 可能解决写权限；它解决不了逐文件属主、chmod/chown 与硬链接语义。先按目标 容器 UID/GID 挂载并做小规模写入验收，失败再判不兼容。」
- **来源报告**：`S1`

### L77 · 数据库在异常关机后损坏

- **强度**：[推理]
- **出处/依据**：起点是 base exFAT 缺 transaction-safe 语义；Microsoft 原文只说明 TexFAT 才“adds transaction-safe operational semantics”。没有上游原文保证任意数据库 在一次异常关机后会损坏。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："数据库在异常关机后损坏"
- **是否需改写**：**是** —— 建议：「缺少 transaction-safe 文件系统语义会扩大异常断电 后的一致性风险；是否损坏取决于数据库与写入时机。该风险足以让本文拒绝把数据库 放 exFAT，但不能写成确定后果。」
- **来源报告**：`S1`

### L79-85 · exFAT 只能放只读媒体；只有格式化或只读两条路；没有第三条路

- **强度**：[官方]（内核源码；原二选一不实）
- **出处/依据**：同上 `fs/exfat/super.c`。
- **原文/取证说明**：同上五个挂载参数。
- **手册怎么说**："exFAT 只能放只读媒体；只有格式化或只读两条路；没有第三条路"
- **是否需改写**：**是** —— 建议完整替换为：「数据库、索引和需要逐文件 POSIX 语义的 目录不要放 exFAT。若用途只是容器写入媒体文件，可先确认目标容器 UID/GID， 用 `uid=`/`gid=` 与合适 mask 挂载，并做小规模写入、重启、再次写入验收；通过 才扩大使用。若服务要求 chown/chmod、硬链接或官方明确不支持 exFAT，再选择 迁移/格式化（会擦盘，必须问用户）或另找可写落点。」
- **来源报告**：`S1`

### L108 / L116 · USB 外接盘绝不能承载任何数据库"；"掉一次可能就是文件系统 损坏

- **强度**：[推理]（手册风险政策）+ [实测]（一次事故）
- **出处/依据**：锚点 A 证明某 USB 直通盘发生过异常断连与数据库重启循环；没有数据库或 USB 上游支持“任何数据库、掉一次即损坏”的全集命题。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："USB 外接盘绝不能承载任何数据库"；"掉一次可能就是文件系统 损坏"
- **是否需改写**：**是** —— 建议：「本手册不把状态数据库放 `usb-portable`，因为供电、 线缆、睡眠和直通都增加意外断连面；这是风险边界。锚点 A 曾观察到一次移盘后 数据库反复重启，但不把该结果写成每块 USB 盘或每种数据库的必然行为。」
- **来源报告**：`S1`

### L112-113 · USB 最大风险不是盘体老化，是意外断连

- **强度**：[推理]
- **出处/依据**：单次事故能证明意外断连存在，不能给各种 USB 介质的失效原因排序。
- **原文/取证说明**：无逐字上游原文；推理起点：单次事故能证明意外断连存在，不能给各种 USB 介质的失效原因排序。
- **手册怎么说**："USB 最大风险不是盘体老化，是意外断连"
- **是否需改写**：**是（轻度）** —— 建议：「USB 外接盘除介质老化外，还要单独评估意外 断连：线缆、供电、睡眠与直通链路。」
- **来源报告**：`S1`

### L118-120 · 盘一走，数据库崩溃重启几千次；原始数据没丢，SMART 全绿

- **强度**：[实测]
- **出处/依据**：锚点 A 单次事故。已知环境：x86_64 老笔记本、OpenWrt VM 与 17 个容器、 USB 直通移动盘；宿主/数据库/文件系统版本与年份未记录。
- **原文/取证说明**：无上游原文；实测环境/元数据：锚点 A 单次事故。已知环境：x86_64 老笔记本、OpenWrt VM 与 17 个容器、 USB 直通移动盘；宿主/数据库/文件系统版本与年份未记录。
- **手册怎么说**："盘一走，数据库崩溃重启几千次；原始数据没丢，SMART 全绿"
- **是否需改写**：**是（补限定）** —— 建议以「在锚点 A 的上述环境曾观察到」开头，并在 素材允许时补齐年份、系统、数据库和文件系统版本；当前不能升级为 USB 普适后果。
- **来源报告**：`S1`

### L131-132 · 绝大多数服务都支持配置/数据库与媒体库拆分

- **强度**：[推理]
- **出处/依据**：本轮没有逐个上游统计“绝大多数”；S2 只核了部分服务。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："绝大多数服务都支持配置/数据库与媒体库拆分"
- **是否需改写**：**是** —— 建议：「优先选择上游明确支持把状态数据与媒体目录分开的服务； 对每个已选服务分别查配置项。若某服务不能拆分，本手册不给它套用这条路径。」
- **来源报告**：`S1`

### L143 / L156-157 · 硬盘柜比移动硬盘稳定得多"；"宿主挂载再共享通常比 USB 直通 VM 稳

- **强度**：[推理]
- **出处/依据**：没有给定硬盘柜、桥接芯片、供电、虚拟化栈或故障率资料；无法支持跨硬件 排序。
- **原文/取证说明**：无逐字上游原文；推理起点：没有给定硬盘柜、桥接芯片、供电、虚拟化栈或故障率资料；无法支持跨硬件 排序。
- **手册怎么说**："硬盘柜比移动硬盘稳定得多"；"宿主挂载再共享通常比 USB 直通 VM 稳"
- **是否需改写**：**是** —— 建议：「独立供电、多盘位并不自动等于更可靠；按具体柜体、 盘、桥接芯片和链路验收。USB 直通会增加宿主—虚拟机设备交接这一层，是否比宿主 挂载更不稳定需在目标虚拟化栈实测。」
- **来源报告**：`S1`

### L165-175 · 网络挂载绝不能承载数据库；多数服务官方明确禁止；数据库依赖 文件锁定，网络抖动会静默损坏

- **强度**：[官方]（**数据库/服务各异；原全集命题不实**）
- **出处/依据**：PostgreSQL https://www.postgresql.org/docs/18/creating-cluster.html ； SQLite https://www.sqlite.org/useovernet.html ； Immich https://docs.immich.app/install/requirements
- **原文/取证说明**：PostgreSQL（2026-08-28 复核 `docs/current`，逐字）：
  "It is possible to use an NFS file system for storing the PostgreSQL data
  directory."、"PostgreSQL does not use any functionality that is known to have
  nonstandard behavior on NFS, such as file locking."、**"The only firm
  requirement for using NFS with PostgreSQL is that the file system is mounted
  using the `hard` option."**、"With the `hard` option, processes can \"hang\"
  indefinitely if there are network problems, so this configuration will require
  a careful monitoring setup."、**"it is strongly recommended to use the `sync`
  export option on the NFS _server_ … Otherwise, an `fsync` or equivalent on the
  NFS client is not actually guaranteed to reach permanent storage on the server,
  which could cause corruption similar to running with the parameter `fsync`
  off."**；SQLite："network filesystem sync and locking reliability vary among
  implementations and installations"，并警告错误锁实现曾导致 corruption；
  Immich：Postgres 数据 "should ideally use local SSD storage, and never a
  network share of any kind."
- **手册怎么说**："网络挂载绝不能承载数据库；多数服务官方明确禁止；数据库依赖 文件锁定，网络抖动会静默损坏"
- **是否需改写**：**是** —— 建议：「是否允许网络文件系统由数据库引擎和服务共同
  决定，不是文件系统定律。SQLite 官方警告网络文件系统的同步/锁语义随实现而异并
  可能导致损坏；Immich 明确要求其 Postgres 数据不要放网络共享；而 PostgreSQL
  上游明确允许 NFS——**但带两个必须写出来的条件**：客户端要以 `hard` 挂载
  （代价是网络出问题时进程会无限期挂起，需要配监控），NFS **服务端**要开
  `sync` 导出（否则客户端的 `fsync` 不保证真落盘，后果等同于关掉 `fsync`）。
  本文可继续把 NAS 上的数据库设为默认拒绝，但要写成手册的风险政策，并允许在
  **所选服务与数据库上游明确支持、上述挂载/导出条件逐条满足、且做过掉线验收**
  时例外，不能写成"任何数据库绝对不行"。」
  ⚠️ **写手册时不要只写"上游允许 NFS"就收尾**——条件不写出来，读者无从核对，
  等于把一个有前提的许可变成了无条件的许可。
- **来源报告**：`S1`

### L179 · 大量小文件操作在网络挂载上会慢一个数量级

- **强度**：[推理]
- **出处/依据**：SQLite 社区/上游材料能支持网络文件系统可能更慢，但没有给本手册的 SMB/NFS、NAS、网络、文件大小与服务负载做“一个数量级”基准。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："大量小文件操作在网络挂载上会慢一个数量级"
- **是否需改写**：**是** —— 建议：「大量小文件操作在网络挂载上可能受往返延迟显著影响； 用目标 NAS、协议和数据集基准测试，不预填‘一个数量级’。」
- **来源报告**：`S1`

### L200-202 · 外接盘掉线时数据库完好，插回去就恢复

- **强度**：[推理]
- **出处/依据**：由“数据库确实完全在内置盘、媒体盘只承载可丢失引用”推出；服务是否自动 恢复取决于它对 I/O 错误和重新挂载的处理。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："外接盘掉线时数据库完好，插回去就恢复"
- **是否需改写**：**是（轻度）** —— 建议：「这种拆分把数据库与外接盘故障隔离；盘重新 挂载后数据库仍在。服务能否自动恢复需用本页拔盘演练证明，不能预先承诺‘插回去 就恢复’。」
- **来源报告**：`S1`

### L213 · 很多服务自带定时数据库备份功能

- **强度**：[推理]
- **出处/依据**：未对服务集合做统计；S2 只确认 Immich 有自动数据库备份。
- **原文/取证说明**：无逐字上游原文；推理起点：未对服务集合做统计；S2 只确认 Immich 有自动数据库备份。
- **手册怎么说**："很多服务自带定时数据库备份功能"
- **是否需改写**：**是（轻度）** —— 建议：「若所选服务官方提供数据库备份功能，确认其 已启用、目标盘独立且做过恢复演练；没有则使用该数据库官方备份方法。」
- **来源报告**：`S1`

## layers/6-ingress.md
<a id="layers-6-ingress"></a>

### L34-42 · `100.64.0.0/10`（`100.64.x.x`–`100.127.x.x`）是运营商共享地址段。

- **强度**：`[官方]`
- **出处/依据**：<https://www.rfc-editor.org/rfc/rfc6598.html> §7（2026-08-28 抓取）
- **原文/取证说明**：“The Shared Address Space address range is 100.64.0.0/10.”
- **手册怎么说**：`100.64.0.0/10`（`100.64.x.x`–`100.127.x.x`）是运营商共享地址段。
- **是否需改写**：否
- **来源报告**：`S3`

### L180-186 · 不要固定隧道传输协议

- **强度**：`[实测]` —— **单次经历，且只在一个服务商上**
- **出处/依据**：手册素材或现场记录；环境信息见“原文/取证说明”。
- **原文/取证说明**：无上游原文；实测环境/元数据：报告未完整记录
- **手册怎么说**："不要固定隧道传输协议"
- **是否需改写**：**是** ⚠️ **这是我这格里最典型的"单次观察写成普适"** 手册现在的口吻是"当前网络路径上哪个协议可用**是会变的**"。 依据只有一次：强制某协议→恢复→几天后反转。 建议改成：**在一次真实故障中观察到**，两次可用协议正好相反； 由此**推断**协议可用性会随网络路径变化。**做法（让客户端自动探测）仍然推荐**—— 它同时也是上游的默认行为。
- **来源报告**：`S3`

### L111-116 · 声明子网路由后还要在管理后台批准这条路由——默认不会自动批准。

- **强度**：`[官方]`
- **出处/依据**：<https://tailscale.com/docs/features/subnet-routers>（2026-08-28 抓取）
- **原文/取证说明**（⚠️ **主规则和例外必须一起摘**——这条曾经只摘了例外）：
  主规则：广告出来的子网路由要在管理后台**批准之后**才在 tailnet 中生效。
  例外一：符合 `autoApprovers` 的设备会**自动批准**。
  例外二：“You can skip this step if you use `autoApprovers`.”
- **手册怎么说**：声明子网路由后还要**在管理后台批准这条路由**——默认**不会**自动批准。
- **是否需改写**：**是** —— 建议把泛化的 KB 首页换成上述 subnet routers 具体页，并写清：未配置 `autoApprovers` 时，需要在管理后台批准广告路由。
- **来源报告**：`S3`

## layers/7-lan-addressing.md
<a id="layers-7-lan-addressing"></a>

### L87-89 · `.local` 是 mDNS 保留后缀；绝对不要拿来当普通 DNS 后缀用

- **强度**：`[官方]`
- **出处/依据**：<https://www.rfc-editor.org/rfc/rfc6762.html> §3
- **原文/取证说明**（⚠️ **两句必须一起读**）：
  “Any DNS query for a name ending with '.local.' MUST be sent to the mDNS IPv4
  link-local multicast address 224.0.0.251 (or its IPv6 equivalent FF02::FB).”
  **紧接着的一句**：实现 “MAY choose to look up such names concurrently via other
  mechanisms (e.g., Unicast DNS) and coalesce the results.”
- **手册怎么说**（基线措辞）：`.local` 是 mDNS 保留后缀，绝对不要拿来当普通 DNS 后缀用——两套解析机制会打架。
- **是否需改写**：**是（但不是往"更强"改）** ——
  `MUST` 发组播 **不等于** `MUST NOT` 同时发单播。结论（别拿 `.local` 当私有单播后缀）
  保留，理由应写成：**同一个后缀压着两套命名语义，谁的答案胜出取决于实现与时序，
  结果不可预测。** 不要写成"单播 DNS 收不到""不会生效"。
- **状态**：✅ 已落地（`layers/7-lan-addressing.md`）
- **来源报告**：`S3`（原始标注）；**范围错误由第三轮 R1 查出并纠正**

> 🔴 **这一条是本附录自己制造的错误，留作教训，不要删。**
>
> S3 只摘了 `MUST` 那一句、漏了紧随其后的 `MAY`，然后据此建议正文"改得更强"。
> 正文照做了 —— **于是一个专门用来防止误引上游的机制，亲手生产了一次误引。**
>
> 由此立一条编辑规则，见本页开头的「摘录规则」。

### L111 · `home.arpa` 由 RFC 8375 为家庭网络保留，但签不了公开信任的证书

- **强度**：`[官方]`（保留与 DNSSEC 两半）+ `[推理]`（**公开证书那半**）
- **出处/依据**：<https://www.rfc-editor.org/rfc/rfc8375.html> Abstract / §1 / §6.1
- **原文/取证说明**：“'home.arpa.' is designated for non-unique use in residential home networks.”；“cannot be secured using DNSSEC based on the root domain's trust anchor”
  ⚠️ **RFC 8375 全文不讨论证书。** “签不了公开信任的证书”这半**不能从上面两句推出**——
  它的依据是公开 CA 不为不可注册的名称签发证书（属于 CA/浏览器论坛与各 CA 的规则），
  本条**没有引到那一侧的一手来源**。别把它一起标成 `[官方]`。
- **手册怎么说**：| `home.arpa` | ✅ RFC 8375 专为家庭网络保留，安全但**签不了公开信任的证书** |
- **是否需改写**：**是** —— 建议：「`.home.arpa` 不能取得公开信任证书，也不能用公共 DNS 根信任链验证 DNSSEC；后者是 RFC 8375 明列的边界。」
- **来源报告**：`S3`

### L112 · `.internal` 由 ICANN 指定为私有使用，同样签不了证书

- **强度**：`[官方]`
- **出处/依据**：<https://www.icann.org/en/board-activities-and-meetings/materials/approved-resolutions-special-meeting-of-the-icann-board-29-07-2024-en>（决议 2024.07.29.06；2026-08-28 抓取）
- **原文/取证说明**：“Resolved (2024.07.29.06), the Board reserves .INTERNAL from delegation in the DNS root zone permanently to provide for its use in private-use applications.”
- **手册怎么说**：| `.internal` | ✅ ICANN 已指定为私有使用，同上，签不了证书 |
- **是否需改写**：**是** —— 建议：「`.internal` 已由 ICANN 董事会决议 2024.07.29.06 永久保留、不在 DNS 根区委派，供私有应用使用；它仍不能签公开信任的证书。」
- **来源报告**：`S3`

### L124 · 签出来的证书对内网 IP 同样有效，因为验证的是域名所有权，不是可达性。

- **强度**：`[官方]`（机制成立）但 **⚠️ 这句话按字面是错的** - **★★★ 两位 reviewer 独立指出同一处**（codex-B B1-19 · deepseek-B №19）
- **出处/依据**：<https://letsencrypt.org/docs/challenge-types/>（2026-08-28 抓取）
- **原文/取证说明**：“You can use this challenge to validate domain names whose webservers aren’t exposed to the public internet.”；“It cannot be used to validate IP Addresses.”
- **手册怎么说**：签出来的证书对内网 IP 同样有效，因为验证的是**域名所有权**，不是可达性。
- **是否需改写**：**是** 建议改成：证书对**那个域名**有效，而域名由你的内网 DNS 解析到内网 IP。 **直接用 IP 访问仍然不受证书覆盖**——所以内网也得走域名，不能图省事敲 IP。
- **来源报告**：`S3`

### L81-85 · mDNS 平台表：macOS/iOS 原生；Linux 通常有 Avahi；Windows/Android 有限制；电视/机顶盒“基本别想”。

- **强度**：`[社区]`（取证受限：报告未附至少一个可查出处）
- **出处/依据**：无单一权威来源；各平台行为分散在各自文档与社区报告里
- **原文/取证说明**：取证受限：来源报告未取得覆盖整张平台表的逐字权威原文。
- **手册怎么说**：mDNS 平台表：macOS/iOS 原生；Linux 通常有 Avahi；Windows/Android 有限制；电视/机顶盒“基本别想”。
- **是否需改写**：**是** —— 表格现在是断言口吻（"❌ 基本别想"）。 建议标明这是**社区普遍报告**而非厂商声明，并提醒读者**以自己手上的设备实测为准**。
- **来源报告**：`S3`

## services/immich.md
<a id="services-immich"></a>

> **文档版本冲突（按逐字原文裁定）**：2026-08-27 的第三轮报告引用旧版措辞
> “it is not recommended to use a network share for your database location”；
> 2026-08-28 的 S2 重新抓取现行安装文档，得到 “Network shares are not supported
> for the database”，requirements 页另写 “never a network share of any kind”。
> 两边都有逐字记录，按文档改版处理；本附录采用 2026-08-28 现行措辞，并保留日期。

### L53 · 网络挂载（SMB/NFS）：手册称官方文档明确禁止

- **强度**：[官方]
- **出处/依据**：https://docs.immich.app/install/docker-compose （.env 注释）； https://docs.immich.app/install/requirements
- **原文/取证说明**：.env 注释："Network shares are not supported for the database"； requirements 页：数据库 "should ideally use local SSD storage, and never a network share of any kind."
- **手册怎么说**："**网络挂载（SMB/NFS）** | ❌ **官方文档明确禁止**"
- **是否需改写**：**是** —— 官方全文没有 prohibit / ban / must not 一类"禁止"字样， 最强措辞是 *not supported* 和 *never a network share of any kind*。 建议改为：「**官方不支持**：安装文档写明 *Network shares are not supported for the database*，requirements 页并要求 *never a network share of any kind*」。 （注：任务书里记的原文措辞是 *not recommended*，与现行文档不符—— 现行文档比任务书记忆的更强，但仍是"不支持"，不是"禁止"。以本条引用为准。）
- **来源报告**：`S2`

### L52 · exFAT：权限模型失效，异常关机后损坏

- **强度**：[官方]（前半）+ [推理]（后半）
- **出处/依据**：https://docs.immich.app/FAQ ； https://docs.immich.app/install/requirements
- **原文/取证说明**：FAQ："NTFS and ex/FAT/32 filesystems are not supported."； requirements 页："It will not work on any filesystem formatted in NTFS or ex/FAT/32."，并要求文件系统 "with support for user/group ownership and permissions."
- **手册怎么说**："**exFAT** | ❌ 权限模型失效，异常关机后损坏"
- **是否需改写**：**是（轻度）** —— "异常关机后损坏"是 exFAT 无日志的机制推论， 官方文档没有这句话。建议改为：「官方不支持（*not supported*）——无 POSIX 权限模型；（无日志导致的断电损坏风险是机制推论，非官方原文）」。
- **来源报告**：`S2`

### L65 · 照片库 exFAT 没有 POSIX 权限，容器写入会失败

- **强度**：[官方] + [推理]
- **出处/依据**：同上（"not supported" 覆盖的是数据库位置；对上传目录官方未单独点名 exFAT）
- **原文/取证说明**：同上。
- **手册怎么说**：照片库 exFAT "❌ **没有 POSIX 权限，容器写入会失败**"
- **是否需改写**：**是（轻度）** —— "会失败"是绝对口吻，依据是权限模型推理而非官方对 上传目录的明文。建议改为「官方判据同样适用：文件系统需支持 user/group ownership and permissions，exFAT 不满足，预期会出权限问题」。
- **来源报告**：`S2`

### L82 · 主服务和机器学习服务必须是同一个版本号。 版本错配会让主服务 进入崩溃重启循环。

- **强度**：[社区]（前半）+ [实测]（后半）
- **出处/依据**：官方文档核不到这句话——install 页只写 "You can pin this to a specific version like v2.1.0"，未要求 server 与 ML 同版本；FAQ 只要求移动 App 与 server 同版本。社区一致建议同版本：如 https://github.com/immich-app/immich/issues/27127
- **原文/取证说明**：（官方无原文——这正是问题）
- **手册怎么说**："**主服务和机器学习服务必须是同一个版本号。** 版本错配会让主服务 进入崩溃重启循环。"
- **是否需改写**：**是** —— "必须"和"会让…进入崩溃重启循环"都是普适口吻。 建议：「社区实践是 server 与 ML 钉同一版本号（官方文档未明文要求，但 release notes 与社区 issue 均按此假设）；我们观察到过一次版本错配导致 主服务崩溃重启循环（锚点 A）」。
- **来源报告**：`S2`

### L74-78 · 真实后果：数据库和照片库放同一块 USB 盘上…累计崩溃数千次

- **强度**：[实测]
- **出处/依据**：手册素材来自锚点 A 的单次事故（2026，本手册作者现场），无上游确认
- **原文/取证说明**：无上游原文；实测环境/元数据：手册素材来自锚点 A 的单次事故（2026，本手册作者现场），无上游确认
- **手册怎么说**："真实后果：数据库和照片库放同一块 USB 盘上…累计崩溃数千次"
- **是否需改写**：否 —— 原文已是叙事口吻（"真实后果"+具体情节），可加一句 "单次观察"更稳，但不强制。
- **来源报告**：`S2`

### L114-115 · Immich 自带定时数据库备份…备份文件默认落在照片库目录下

- **强度**：[官方]
- **出处/依据**：https://docs.immich.app/administration/backup-and-restore
- **原文/取证说明**："Immich automatically creates database backups for disaster-recovery purposes."；备份 "stored in UPLOAD_LOCATION/backups"；默认 "keep last 14 backups, create daily at 2:00 AM"
- **手册怎么说**："Immich 自带定时数据库备份…备份文件默认落在照片库目录下"
- **是否需改写**：否 —— 且官方写明默认**开启**，"先确认它开着"可保留为谨慎做法。
- **来源报告**：`S2`

## services/vaultwarden.md
<a id="services-vaultwarden"></a>

### L63 · 备份本身是加密的（用主密码派生的密钥），但仍不要放进任何公开位置

- **强度**：[官方]（原断言为事实错误）
- **出处/依据**：https://github.com/dani-garcia/vaultwarden/wiki/Backing-up-your-Vault
- **原文/取证说明**："Adding an extra layer of encryption on your backups would generally be a good idea"；config.json "does contain some data in plaintext that could be considered sensitive (admin token, SMTP credentials, etc.)"
- **手册怎么说**："**备份本身是加密的（用主密码派生的密钥），但仍不要放进任何公开位置**"
- **是否需改写**：**是** —— 官方立场相反：数据目录里**有明文敏感内容**，官方建议 对备份**额外**加密。建议改为：「保险库条目由各用户主密码加密，但数据目录 并非整盘加密——config.json 含明文的 admin token、SMTP 凭证等， 官方建议对备份再加一层加密（*an extra layer of encryption on your backups would generally be a good idea*）」。
- **来源报告**：`S2`

### L61-62 · 数据目录（含 SQLite 数据库和附件）定期复制到另一块物理盘

- **强度**：[官方]（做法与上游冲突）
- **出处/依据**：同上 wiki 页
- **原文/取证说明**：用 SQLite `.backup` 命令："This command uses the Online Backup API, which SQLite documents as the best way to back up a database file that may be in active use."；v1.32.1+ 内置 `/vaultwarden backup` 命令
- **手册怎么说**："数据目录（含 SQLite 数据库和附件）定期**复制**到另一块物理盘"
- **是否需改写**：**是** —— "直接复制正在写入的 db.sqlite3"正是上游避开的做法 （可能抓到半写状态）。建议改为：「用官方方式备份： `/vaultwarden backup`（v1.32.1+）或 SQLite `.backup` 命令， 不要在服务运行时直接 cp 数据库文件；备份产物复制到另一块物理盘」。
- **来源报告**：`S2`

### L51-52 · Bitwarden 客户端依赖浏览器的加密 API，只在安全上下文里可用。 纯 HTTP 访问（localhost 除外）时，客户端会无法解锁

- **强度**：[官方]
- **出处/依据**：https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API
- **原文/取证说明**："Secure context: This feature is available only in secure contexts (HTTPS), in some or all supporting browsers."
- **手册怎么说**："Bitwarden 客户端依赖浏览器的加密 API，**只在安全上下文里可用**。 纯 HTTP 访问（localhost 除外）时，客户端会无法解锁"
- **是否需改写**：否 —— "localhost 除外"与 MDN 对 secure context 的定义一致。
- **来源报告**：`S2`

### L67 · 放本地原生文件系统，不要 exFAT、不要网络挂载——理由同层 5

- **强度**：[推理]
- **出处/依据**：依据层 5 的通用判据（SQLite + 权限模型）；Vaultwarden wiki 未对 文件系统类型给明文要求（查了 wiki 主页与备份页，无此条）
- **原文/取证说明**：无逐字上游原文；推理起点：依据层 5 的通用判据（SQLite + 权限模型）；Vaultwarden wiki 未对 文件系统类型给明文要求（查了 wiki 主页与备份页，无此条）
- **手册怎么说**："放本地原生文件系统，**不要 exFAT、不要网络挂载**——理由同层 5"
- **是否需改写**：否 —— 判据成立，但标注应承认是通用推理而非上游明文。
- **来源报告**：`S2`

### L72 · 自用的话把开放注册关掉，只留邀请

- **强度**：[推理]
- **出处/依据**：`SIGNUPS_ALLOWED=false` 是已知配置项；本轮未去 wiki 核原文措辞
- **原文/取证说明**：无逐字上游原文；推理起点：`SIGNUPS_ALLOWED=false` 是已知配置项；本轮未去 wiki 核原文措辞
- **手册怎么说**："自用的话把开放注册关掉，只留邀请"
- **是否需改写**：否 ——（补核时 cite wiki Configuration 页即可）
- **来源报告**：`S2`

## services/jellyfin.md
<a id="services-jellyfin"></a>

### L53 / L56 · macOS | VideoToolbox；容器里拿不到，需要原生安装" / "macOS 上要硬解就得原生装，不能用容器。

- **强度**：[推理]
- **出处/依据**：Jellyfin 官方文档（https://jellyfin.org/docs/general/post-install/transcoding/hardware-acceleration/， 注：旧 URL `administration/hardware-acceleration/` 已 301 到此）把 Video Toolbox 列为 macOS 选项，但**未明文讲容器限制**。结论由机制推出： macOS 上的容器（Docker Desktop）跑在 Linux VM 里，VideoToolbox 是 macOS 专属 API，Linux 容器访问不到。
- **原文/取证说明**：（官方无容器限制原文）
- **手册怎么说**："macOS | VideoToolbox；**容器里拿不到，需要原生安装**" / "**macOS 上要硬解就得原生装，不能用容器。**"
- **是否需改写**：否 —— 推理链坚实，结论保住；建议行内标 `[推理：macOS 容器实为 Linux VM，无 VideoToolbox]`。
- **来源报告**：`S2`

### L47 · 不配硬解时，转码会吃满 CPU，多路并发直接卡死

- **强度**：[推理]
- **出处/依据**：软件转码的计算量是机制常识；官方文档无此量化表述
- **原文/取证说明**：无逐字上游原文；推理起点：软件转码的计算量是机制常识；官方文档无此量化表述
- **手册怎么说**："不配硬解时，转码会吃满 CPU，多路并发直接卡死"
- **是否需改写**：否 ——（"直接卡死"略口语，可不管）
- **来源报告**：`S2`

### L72-73 · 大媒体库首次扫描会持续很久并大量读盘

- **强度**：[推理]
- **出处/依据**：机制常识，官方文档无量化；未深核
- **原文/取证说明**：无逐字上游原文；推理起点：机制常识，官方文档无量化；未深核
- **手册怎么说**："大媒体库首次扫描会持续很久并大量读盘"
- **是否需改写**：否
- **来源报告**：`S2`

## services/home-assistant.md
<a id="services-home-assistant"></a>

### L43-44 · 这些广播不会穿过容器的默认桥接网络。 …症状是：Web 界面完全 正常，但一个设备都发现不了，而且不报错

- **强度**：[社区]（机制；取证受限：报告未附所述 Docker 社区 issue 链接）+ [实测]（症状）
- **出处/依据**：HA 官方安装文档只**指令** host 网络而**不解释原因**—— https://www.home-assistant.io/installation/alternative/ ： "In the **Network** section, set the Network dropdown as `host`."； "Within **Network** and select Network Mode to **Host**." （该页唯一的 mDNS 说明是 VMware 场景："There are confirmed mDNS/Multicast discovery issues when using VMware's `VMXnet3` virtual network adapter."） mDNS/SSDP 不跨 Docker 默认桥接是广泛社区经验（Docker GitHub issue 多年长青）， 无单一权威原文可引。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："**这些广播不会穿过容器的默认桥接网络。** …症状是：Web 界面完全 正常，但**一个设备都发现不了**，而且不报错"
- **是否需改写**：**是（轻度）** —— "一个设备都发现不了"是绝对口吻而依据是单次/经验 观察。建议改为「典型症状是：Web 界面完全正常，但一个设备都发现不了， 而且不报错（在 Docker 默认 bridge 上观察到；HA 官方安装文档一律要求 host 网络，未附原因）」。
- **来源报告**：`S2`

### L66 · 配置目录会频繁小量写入…长期历史数据会持续增长

- **强度**：[推理]
- **出处/依据**：机制常识（recorder 写 SQLite）；未核官方原文
- **原文/取证说明**：无逐字上游原文；推理起点：机制常识（recorder 写 SQLite）；未核官方原文
- **手册怎么说**："配置目录会频繁小量写入…长期历史数据会持续增长"
- **是否需改写**：否
- **来源报告**：`S2`

## services/aria2.md
<a id="services-aria2"></a>

### L45 · aria2 的 RPC 接口默认没有认证。不设密钥就等于把…能力开放给 整个局域网

- **强度**：[官方]
- **出处/依据**：https://aria2.github.io/manual/en/html/aria2c.html
- **原文/取证说明**："It is strongly recommended to set secret authorization token using --rpc-secret option"（启用 RPC 时）；"As of 1.18.4, in addition to HTTP basic authorization, aria2 provides RPC method-level authorization." —— 默认既无 basic auth 也无 secret，"strongly recommended"正是官方对 裸奔风险的背书。
- **手册怎么说**："aria2 的 RPC 接口**默认没有认证**。不设密钥就等于把…能力开放给 整个局域网"
- **是否需改写**：否
- **来源报告**：`S2`

### L57 · 如果用反向代理，AriaNg 和 RPC 要同源，否则跨域会被浏览器拦下

- **强度**：[推理]
- **出处/依据**：浏览器同源策略机制；未核 AriaNg 文档明文
- **原文/取证说明**：无逐字上游原文；推理起点：浏览器同源策略机制；未核 AriaNg 文档明文
- **手册怎么说**："如果用反向代理，**AriaNg 和 RPC 要同源**，否则跨域会被浏览器拦下"
- **是否需改写**：否
- **来源报告**：`S2`

## services/syncthing.md
<a id="services-syncthing"></a>

### L55 · GUI 默认只绑 `127.0.0.1`…报错只是'连接被拒绝'

- **强度**：[官方]
- **出处/依据**：https://docs.syncthing.net/users/faq.html
- **原文/取证说明**："The default listening address is 127.0.0.1:8384, so you can only access the GUI from the same machine."
- **手册怎么说**："**GUI 默认只绑 `127.0.0.1`**…报错只是'连接被拒绝'"
- **是否需改写**：否
- **来源报告**：`S2`

### L42-43 · Syncthing 同步的是'状态'，不是'追加'。 一端删了文件， 另一端也会删

- **强度**：`[官方]`（2026-08-29 复核后**从 `[推理]` 升级**）
- **出处/依据**：<https://docs.syncthing.net/users/syncthing.html> ；<https://docs.syncthing.net/users/faq.html>
- **原文/取证说明**：官方文档逐字写明文件的 creation / modification / **deletion**
  都会复制到其它设备；FAQ 同样说明删除会传播，并把 **versioning** 列为例外
  （开了版本控制的话，被删的文件会进版本库而不是直接消失）。
  ⚠️ 上一轮标为"未命中原文"是**抓取没到位**，不是上游没写。
- **手册怎么说**："**Syncthing 同步的是'状态'，不是'追加'。** 一端删了文件， 另一端也会删"
- **是否需改写**：**是（补例外）** —— 结论成立且现在有一手依据；建议正文补一句
  **versioning 是这条的例外**，否则读者以为删了就没救了。
- **来源报告**：`S2`

## services/navidrome.md
<a id="services-navidrome"></a>

### L33 · 兼容 Subsonic API，所以能用大量现成的第三方客户端

- **强度**：[官方]
- **出处/依据**：https://www.navidrome.org/docs/overview/
- **原文/取证说明**："can also work as a lightweight Subsonic-API compatible server"； "Compatible with all Subsonic/Madsonic/Airsonic clients."
- **手册怎么说**："兼容 Subsonic API，所以能用大量现成的第三方客户端"
- **是否需改写**：否
- **来源报告**：`S2`

### L38 · 数据库：SQLite，放本地盘

- **强度**：[官方]
- **出处/依据**：https://www.navidrome.org/docs/usage/configuration/options/ （`ND_DBPATH` 指向 SQLite 数据库文件；overview/FAQ 页无明文，需到配置页）
- **原文/取证说明**：配置项 ND_DB_PATH/NDDBPATH 描述 SQLite 数据库路径（本轮经检索确认 该页为出处，未逐字抓原文）
- **手册怎么说**："数据库：SQLite，放本地盘"
- **是否需改写**：否 ——（落地时可从 options 页补一句原文）
- **来源报告**：`S2`

### L42 · 标签乱的库扫出来就是乱的，Navidrome 不猜

- **强度**：[推理]
- **出处/依据**：机制常识（扫描依赖标签）；未核官方原文
- **原文/取证说明**：无逐字上游原文；推理起点：机制常识（扫描依赖标签）；未核官方原文
- **手册怎么说**："标签乱的库扫出来就是乱的，Navidrome 不猜"
- **是否需改写**：否
- **来源报告**：`S2`

## services/sunshine-moonlight.md
<a id="services-sunshine-moonlight"></a>

### L45 · 被控端必须处于已登录的图形会话中。没登录时：无桌面可抓、 无 GPU 会话

- **强度**：[官方]（间接）
- **出处/依据**：https://docs.lizardbyte.dev/projects/sunshine/v0.21.0/about/usage.html
- **原文/取证说明**：文档以指南形式承认默认前提——headless 指南标题即 "setup a headless streaming server **without autologin** and dummy plugs" （反面印证：常规路径需要 autologin/已登录会话）
- **手册怎么说**："被控端必须处于**已登录的图形会话**中。没登录时：无桌面可抓、 无 GPU 会话"
- **是否需改写**：否
- **来源报告**：`S2`

### L55 · 串流走 UDP、对延迟极其敏感，流量绝不能走代理

- **强度**：[推理]
- **出处/依据**：机制常识（Moonlight 官方文档给端口清单含 UDP，但"不能走代理"是 本手册的运维判断）；未核原文
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："串流走 UDP、对延迟极其敏感，**流量绝不能走代理**"
- **是否需改写**：否 —— 作为运维建议成立，不必引官方。
- **来源报告**：`S2`

## services/sunpanel.md
<a id="services-sunpanel"></a>

### L43-47 · 跨域 iframe + 认证 + 重定向…真实案例：路由器和代理面板配成 内嵌模式，点击无反应

- **强度**：[实测]
- **出处/依据**：手册素材来自单次现场事故（本手册作者，2026）；上游无此文档
- **原文/取证说明**：无上游原文；实测环境/元数据：手册素材来自单次现场事故（本手册作者，2026）；上游无此文档
- **手册怎么说**："跨域 iframe + 认证 + 重定向…真实案例：路由器和代理面板配成 内嵌模式，点击无反应"
- **是否需改写**：否 —— 原文已用"真实案例"叙事口吻，且明确写了"当时还误判"， 符合规范①。
- **来源报告**：`S2`

## advanced/resident-ai-harness.md
<a id="advanced-resident-ai-harness"></a>

### L91 · 已知：Anthropic（Claude）屏蔽香港，OpenAI 也有类似的地区限制

- **强度**：[官方]（Anthropic 部分）+ [社区]（OpenAI 部分）
- **出处/依据**：https://www.anthropic.com/supported-countries
- **原文/取证说明**：官方**没有任何"屏蔽"表述**——只是支持地区列表（"Countries, regions, and territories where we currently offer Claude.ai access"）不含香港 （及中国大陆）。OpenAI 部分本轮未核原文。
- **手册怎么说**："**已知：Anthropic（Claude）屏蔽香港**，OpenAI 也有类似的地区限制"
- **是否需改写**：**是（轻度）** —— "屏蔽"是手册升级的动词。建议改为：「Anthropic 的 支持地区列表不含香港（官方未作"屏蔽"声明，只是不提供访问）；OpenAI 的 地区限制有类似报告，未核官方原文」。
- **来源报告**：`S2`

### L127-128 · 很多启动 AI CLI 的包装器 / 启动脚本会给会话注入代理 环境变量

- **强度**：[实测]
- **出处/依据**：手册素材来自单次真实案例（一个包装器）；"很多"无统计依据
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："**很多**启动 AI CLI 的包装器 / 启动脚本会**给会话注入代理 环境变量**"
- **是否需改写**：**是（轻度）** —— 建议改"一些启动 AI CLI 的包装器会…"并在 真实案例句保持叙事。
- **来源报告**：`S2`

### L65 · 低功耗和'一直在'是矛盾的，没有两全的配置。

- **强度**：[推理]
- **出处/依据**：设计层判断（如休眠+WoL 按需唤醒即部分两全，手册自己也用了）， 非上游结论
- **原文/取证说明**：无逐字上游原文；推理起点：设计层判断（如休眠+WoL 按需唤醒即部分两全，手册自己也用了）， 非上游结论
- **手册怎么说**："**低功耗和'一直在'是矛盾的，没有两全的配置。**"
- **是否需改写**：**是（轻度）** —— "没有两全"与本章第一节的"WoL 按需唤醒强机器" 方案张力明显。建议软化为"低功耗和'一直在'天然矛盾，折中方案（睡眠+ 唤醒）牺牲的是即时可用性"。
- **来源报告**：`S2`

## ops/boot-persistence.md
<a id="ops-boot-persistence"></a>

### L34-38 · 用了 `-daemonize` 一类后台化选项，服务管理器就失去了真正的子进程。

- **强度**：`[官方]`（仅特定服务管理语义）+ `[推理]`（跨平台结论）
- **出处/依据**：freedesktop.org 渲染页自动取证失败；改核 systemd 官方源码中的 man page：<https://github.com/systemd/systemd/blob/main/man/systemd.service.xml>（2026-08-28）
- **原文/取证说明**：“The use of this type is discouraged”；“recommended to also use the PIDFile= option”
- **手册怎么说**：用了 `-daemonize` 一类后台化选项，服务管理器就失去了真正的子进程。
- **是否需改写**：**是** —— 建议：「对 systemd，默认 `Type=simple` 不应配合自行守护化；传统守护进程可用 `Type=forking` 并配置 `PIDFile=`，但上游不推荐该类型。对 macOS launchd 另按 Apple 语义表述，不写成跨平台必然。」
- **来源报告**：`S3`

### L56-66 · 宿主机开了全盘加密时，解锁前用户级服务不运行；这是加密的固有性质。

- **强度**：`[官方]`（launchd 的 per-user domain 语义）+ `[实测]`（原始事故）
- **出处/依据**：<https://support.apple.com/en-ie/102316>；<https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html>
- **原文/取证说明**：Apple Support：“manual login is required” when “FileVault is turned on.”；Apple Developer：“executes only while that user is logged in.”
- **手册怎么说**：宿主机开了全盘加密时，解锁前用户级服务不运行；这是加密的固有性质。
- **是否需改写**：**是** —— 建议：「在 macOS + FileVault 且任务依赖用户登录会话时，重启后需先解锁并登录，用户级任务才会运行；不要把这一行为推广到所有全盘加密方案或系统级服务。」
- **来源报告**：`S3`

### L73-74 · 低功耗和常驻可用是一对矛盾，没有两全的配置。

> ⚠️ **本条原来的「是否需改写」写的是调度器补跑，与断言对不上**——那是 S3 报告里
> 一处错位的行号引用带过来的（补跑那句根本不在本文件里）。已拆成两条，见下一条。

- **强度**：`[实测]` + `[推理]`
- **出处/依据**：无单一上游出处。
- **原文/取证说明**：无逐字上游原文；依据是单次现场观察，未记录系统/版本。
- **手册怎么说**（基线措辞）：低功耗和常驻可用是一对矛盾，没有两全的配置。
- **是否需改写**：**是** —— 建议：「低功耗和"一直在"天然矛盾；折中方案（睡眠 + 按需唤醒）
  不是没有，但它牺牲的是**即时可用性**。」不要写成"没有两全的配置"，
  因为本手册第一节自己就给了 WoL 唤醒这个折中。
- **状态**：✅ **已落地**（`advanced/resident-ai-harness.md`）
- **来源报告**：`S3`

### （补）睡眠期间错过的定时任务会不会补跑

> 这条断言原本被 S3 错记在上一条的行号下。它真实的落点是
> `00-probe.md`、`pitfalls/boot-ops.md`、`advanced/resident-ai-harness.md` 三处。

- **强度**：`[官方]`（各调度器行为）
- **出处/依据**：`launchd.plist(5)`（StartCalendarInterval 条目）
- **原文/取证说明**：*"Unlike cron which skips job invocations when the computer is asleep,
  launchd will start the job the next time the computer wakes up. If multiple intervals
  transpire before the computer is woken, those events will be coalesced into one event
  upon wake from sleep."*（2026-08-28 复核，逐字一致）
- **手册怎么说**（基线措辞）：睡眠期间到点的任务**不会补跑**，那一次就是没跑。
- **是否需改写**：**是（原句在 macOS 上是错的）** —— 按机制分别写：
  `cron` 跳过 / macOS `launchd` **唤醒时补跑但多次错过合并成一次** /
  `systemd` timer 默认跳过、`Persistent=true` 补跑。
- **状态**：✅ **已落地**（权威表述在 `ops/boot-persistence.md`，另三处指路）
- **来源报告**：`S3`（断言）+ zcode 裁决表审计（证伪与取证）

## ops/wol.md
<a id="ops-wol"></a>

### L10 · 魔术包必须能到达目标机器所在的二层广播域。 这决定了它跨网段不工作。

- **强度**：`[推理]`（由广播的定义直接推出，业界公认）
- **出处/依据**：无单一上游出处；推理起点见“原文/取证说明”。
- **原文/取证说明**：无逐字上游原文；推理起点：报告所列机制
- **手册怎么说**：**魔术包必须能到达目标机器所在的二层广播域。** 这决定了它跨网段不工作。
- **是否需改写**：否。这是广播语义的必然，不需要额外出处。
- **来源报告**：`S3`

## ops/secrets.md
<a id="ops-secrets"></a>

### L95-103 · 这段 `/proc/$pid/cmdline` 自检已实测；stdin 两种写法显示“干净”，把密钥放 argv 会显示“泄露”。

- **强度**：`[实测]` —— **我在本机 Linux 上跑过对照实验**（对照组泄露、两种新写法干净）
- **出处/依据**：手册素材或现场记录；环境信息见“原文/取证说明”。
- **原文/取证说明**：2026 年在作者的一台 Linux 主机做过对照；发行版、内核与工具版本未记录。macOS 没有 `/proc`，该自检会假阴性。
- **手册怎么说**：这段 `/proc/$pid/cmdline` 自检已实测；stdin 两种写法显示“干净”，把密钥放 argv 会显示“泄露”。
- **是否需改写**：**是** —— 建议：「下列 `/proc/$pid/environ` 自检只适用于提供该接口的 Linux；macOS 没有 `/proc`，不要用这条命令判定环境变量是否泄漏，必须另用该平台可核的方法。」照现文在 macOS 执行会把空输入判成“干净”，形成恒定假阴性。
- **来源报告**：`S3`

## pitfalls/proxy-dns.md
<a id="pitfalls-proxy-dns"></a>

### L18-24 · 代理插件普遍有只启动内核模式……没有控制接口/透明端口/防火墙 规则/tun，客户端两条路都断

- **强度**：[官方]（仅 Nikki）+ [实测]（单次症状）
- **出处/依据**：同 `layers/3-proxy-stack.md` L90-100 条目。
- **原文/取证说明**：见“出处/依据”中的交叉引用；不重复转述。
- **手册怎么说**："代理插件普遍有只启动内核模式……没有控制接口/透明端口/防火墙 规则/tun，客户端两条路都断"
- **是否需改写**：**是** —— 建议把标题和原因改成「Nikki 的‘仅核心’未按设计处理」；正文 使用同一限定措辞。尤其删除“没有 tun 设备”的必然结论：Nikki 维护者讨论明确以 裸核自行启用 TUN/auto-route 为有效对照。
- **来源报告**：`S1`

### L47-48 · 透明代理默认开 fake-ip

- **强度**：[官方]（Mihomo；原断言不实）
- **出处/依据**：https://wiki.metacubex.one/config/dns/
- **原文/取证说明**："可选值 `fake-ip`/`redir-host`，默认`redir-host`"。
- **手册怎么说**："透明代理默认开 fake-ip"
- **是否需改写**：**是** —— 建议：「**启用了 fake-ip 的配置**会返回映射地址；Mihomo `enhanced-mode` 默认是 `redir-host`，先检查生效配置再进入本坑。」
- **来源报告**：`S1`

### L59-60 · 代理不认识裸主机名，于是给了个 fake-ip；客户端拿着 198.18.x.x 去连，那里什么都没有

- **强度**：[推理]
- **出处/依据**：Mihomo 官方只定义 fake-ip 过滤行为，没有承诺所有无法上游解析的裸主机名 都会获得 fake-ip；结果还取决于搜索域、hosts、sniffer 与 DNS 配置。
- **原文/取证说明**：无逐字上游原文；推理起点：Mihomo 官方只定义 fake-ip 过滤行为，没有承诺所有无法上游解析的裸主机名 都会获得 fake-ip；结果还取决于搜索域、hosts、sniffer 与 DNS 配置。
- **手册怎么说**："代理不认识裸主机名，于是给了个 fake-ip；客户端拿着 198.18.x.x 去连，那里什么都没有"
- **是否需改写**：**是** —— 建议：「若该名字被 Mihomo fake-ip 处理且未被本地解析/过滤， 客户端可能得到 fake-ip 映射而访问失败；用 DNS 查询结果确认，不把所有裸主机名 失败都判成这一因果。」
- **来源报告**：`S1`

### L79-80 · 过滤列表往往整表替换

- **强度**：[官方]（仅 Nikki）+ [推理]（跨插件）
- **出处/依据**：同 `layers/4-routing-dns.md` L41 条目。
- **原文/取证说明**：见“出处/依据”中的交叉引用；不重复转述。
- **手册怎么说**："过滤列表往往整表替换"
- **是否需改写**：**是** —— 建议改成按所选插件检查最终数组，不写“往往”。
- **来源报告**：`S1`

### L90-100 · 插件默认把 100.64/10 与 fc00::/7 直连；Tailscale DNS 是 100.100.100.100；两项各有默认关闭总开关

- **强度**：[官方]（Tailscale DNS）+ [推理]（插件默认值）
- **出处/依据**：https://tailscale.com/docs/reference/faq/dns-resolv-conf
- **原文/取证说明**："Tailscale's MagicDNS server still replies at `100.100.100.100` (or `fd7a:115c:a1e0::53`)"。未找到四个代理插件共同默认直连这些网段、共同有两个默认关闭 总开关的来源。
- **手册怎么说**："插件默认把 100.64/10 与 fc00::/7 直连；Tailscale DNS 是 100.100.100.100；两项各有默认关闭总开关"
- **是否需改写**：**是** —— 建议：「Tailscale MagicDNS 服务地址为 `100.100.100.100` （IPv6 为 `fd7a:115c:a1e0::53`）。代理侧是否已将 Tailscale IPv4/IPv6 网段 直连、是否需 fake-ip 过滤及其开关默认值，必须从所选插件最终配置确认。」
- **来源报告**：`S1`

### L107-114 · 两套 DNS 劫持同时开，谁生效取决于规则顺序，结果不可预测；多数 插件文档明写要关路由 DNS 重定向

- **强度**：[官方]（仅 Nikki）+ [推理]（多数插件）
- **出处/依据**：https://github.com/nikkinikki-org/OpenWrt-nikki/wiki
- **原文/取证说明**："请自行关闭`网络 -> DHCP/DNS -> DNS 重定向`这一选项，否则可能会导致 DNS污染/分流错误的的情况发生。（如无此项请忽略）。"
- **手册怎么说**："两套 DNS 劫持同时开，谁生效取决于规则顺序，结果不可预测；多数 插件文档明写要关路由 DNS 重定向"
- **是否需改写**：**是** —— 建议：「Nikki 官方明确要求关闭 OpenWrt 的 DNS 重定向，否则 **可能**导致污染/分流错误。其它插件按各自文档；不要升级为多数插件共同明写， 也不要把结果写成必然随机。」
- **来源报告**：`S1`

### L122-133 · 自动组延迟最低往往是最近地区；Anthropic 屏蔽香港；漂过去立即 失效

- **强度**：[实测]（一套订阅/组）+ [官方]（支持地区）+ [推理]（普适因果）
- **出处/依据**：同 `layers/4-routing-dns.md` L57-61 条目。
- **原文/取证说明**：见“出处/依据”中的交叉引用；不重复转述。
- **手册怎么说**："自动组延迟最低往往是最近地区；Anthropic 屏蔽香港；漂过去立即 失效"
- **是否需改写**：**是** —— 建议限定为 2026-08-27 的 Nikki/Auto 配置，并把“屏蔽”改成 “官方支持地区不含香港”；自动组算法必须读具体组类型，不能假定都按延迟或都选 最近地区。
- **来源报告**：`S1`

### L157-161 · 代理只接管 IPv4；系统可能优先 IPv6；同一命令两次不稳定

- **强度**：[官方]（IPv6 选择可能性）+ [推理]（插件状态与随机症状）
- **出处/依据**：RFC 8305，原文同 `layers/3-proxy-stack.md` L138-141；Nikki 的 IPv4/IPv6 代理开关是分立的，原文同该页 L137 条目。
- **原文/取证说明**：无逐字上游原文；推理起点：RFC 8305，原文同 `layers/3-proxy-stack.md` L138-141；Nikki 的 IPv4/IPv6 代理开关是分立的，原文同该页 L137 条目。
- **手册怎么说**："代理只接管 IPv4；系统可能优先 IPv6；同一命令两次不稳定"
- **是否需改写**：**是** —— 建议：「**若实测确认所选代理只接管 IPv4**，双栈应用可能 选择未接管的 IPv6 路径。是否两次结果不同不是协议保证；用 `-4`/`-6` 与出口 记录确认。」
- **来源报告**：`S1`

### L191-195 · 规则集只有 3 条、一年多没更新、漏 OAuth 域名，导致用一阵掉登录

- **强度**：[社区]（规则内容）+ [官方]（域名用途）+ [推理]（掉登录结果）
- **出处/依据**：同 `layers/4-routing-dns.md` L98-100 条目。
- **原文/取证说明**：见“出处/依据”中的交叉引用；不重复转述。
- **手册怎么说**："规则集只有 3 条、一年多没更新、漏 OAuth 域名，导致用一阵掉登录"
- **是否需改写**：**是** —— 建议保留可核的“3 条、页面标注 2025-06-06、漏 `platform.claude.com`”，把“负责 OAuth 的域名遗漏**会**导致掉登录”改为 “按官方端点用途推得存在 OAuth 刷新失败风险；本次未做掉登录复现”。
- **来源报告**：`S1`

### L215-221 · 并装两套时两个面板正常、客户端全断；流量被 A 劫走按 B 处理

- **强度**：[推理]
- **出处/依据**：同 `layers/3-proxy-stack.md` L17-22 条目。
- **原文/取证说明**：见“出处/依据”中的交叉引用；不重复转述。
- **手册怎么说**："并装两套时两个面板正常、客户端全断；流量被 A 劫走按 B 处理"
- **是否需改写**：**是（保留禁令）** —— 建议把具体症状写成可能例，不写必然；硬约束理由 是防火墙/策略路由所有权重叠且本文未定义共存方案。
- **来源报告**：`S1`

## pitfalls/storage.md
<a id="pitfalls-storage"></a>

### L11-31 · 数据库反复重启几千次；SMART 全绿；盘被搬走后挂载点变成几 MB 临时文件系统；长期异常断电反复损坏

- **强度**：[实测]
- **出处/依据**：锚点 A 的单次事故；已知 x86_64 老笔记本、OpenWrt VM、17 容器、USB 直通盘，缺宿主/数据库/文件系统版本与事故年份。
- **原文/取证说明**：无上游原文；实测环境/元数据：锚点 A 的单次事故；已知 x86_64 老笔记本、OpenWrt VM、17 容器、USB 直通盘，缺宿主/数据库/文件系统版本与事故年份。
- **手册怎么说**："数据库反复重启几千次；SMART 全绿；盘被搬走后挂载点变成几 MB 临时文件系统；长期异常断电反复损坏"
- **是否需改写**：**是** —— 建议整节开头加：「以下是锚点 A 的一次事故复盘，不是 USB 或数据库的普适故障序列（版本/年份未记录）。」具体观察可以保留。
- **来源报告**：`S1`

### L37-38 · 绝大多数服务都支持配置/数据库与媒体拆分；状态数据通常不到 1 GB

- **强度**：[推理]（前半）+ [实测]（后半单一部署）
- **出处/依据**：同 `layers/5-storage.md` L23-27、L131-132 条目；Immich 官方反例为 Postgres 通常 1–3 GB。
- **原文/取证说明**：见“出处/依据”中的交叉引用；不重复转述。
- **手册怎么说**："绝大多数服务都支持配置/数据库与媒体拆分；状态数据通常不到 1 GB"
- **是否需改写**：**是** —— 建议：「逐个核所选服务是否支持拆分；状态数据通常比媒体小， 但容量按服务文档和现场测量，不给统一 `<1 GB`。」
- **来源报告**：`S1`

### L51-56 · 改 uid/gid、改挂载参数、改目录权限，都没用

- **强度**：[官方]（Linux 内核源码；原断言不实）
- **出处/依据**：同 `layers/5-storage.md` L56/L62/L71 的 `fs/exfat/super.c` 五个参数。
- **原文/取证说明**：见“出处/依据”中的交叉引用；不重复转述。
- **手册怎么说**："改 uid/gid、改挂载参数、改目录权限，都没用"
- **是否需改写**：**是** —— 建议：「exFAT 不存逐文件 owner/mode；但 Linux 驱动支持 `uid=`/`gid=` 与 mask，把整卷映射为一个属主与权限外观。它可能满足单一容器的 媒体写入，不能提供逐文件 chown/chmod 或硬链接。」
- **来源报告**：`S1`

### L63-68 · 只有格式化或只读两条路；没有第三条路

- **强度**：[官方]（Linux 内核源码；原二选一不实）
- **出处/依据**：同上。
- **原文/取证说明**：见“出处/依据”中的交叉引用；不重复转述。
- **手册怎么说**："只有格式化或只读两条路；没有第三条路"
- **是否需改写**：**是** —— 建议增加第三条：「按目标容器 UID/GID 和 mask 挂载，先以 非 root 容器身份做小规模写入/重启复验；只用于不要求逐文件 POSIX 语义和硬链接 的媒体目录。」格式化仍必须 `needs_human`，数据库仍不放 exFAT。
- **来源报告**：`S1`

### L80-86 · 晚挂载时服务会重新初始化，把原来的配置覆盖了

- **强度**：[推理]
- **出处/依据**：起点是“服务在挂载前看到的是宿主底层空目录”。未找到服务无关的上游原文； 一般只能推出服务**可能在底层目录新建数据**，重新挂载后该数据会被挂载内容遮住。 是否覆盖远端/原盘旧配置取决于服务和同步行为。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**："晚挂载时服务会重新初始化，把原来的配置覆盖了"
- **是否需改写**：**是** —— 建议：「挂载未就绪时，服务可能把宿主底层空目录当作新安装并 写入一套新数据；真实挂载随后出现时，这套数据会被遮住。是否覆盖原有数据不是 通用结果，需按服务行为核对。」
- **来源报告**：`S1`

## pitfalls/services.md
<a id="pitfalls-services"></a>

### L9-13 · HA…Web 界面完全正常，但自动发现列表是空的，而且不报错

- **强度**：[社区]（取证受限：交叉引用同样未附所述 Docker 社区 issue 链接）+ [实测]
- **出处/依据**：同 home-assistant.md 条目（官方只指令 host 网络，不解释）
- **原文/取证说明**：无上游原文；实测环境/元数据：同 home-assistant.md 条目（官方只指令 host 网络，不解释）
- **手册怎么说**："HA…Web 界面完全正常，但自动发现列表是空的，**而且不报错**"
- **是否需改写**：**是（轻度）** —— 建议在「原因」后补一句限定： "（mDNS/SSDP 不跨 Docker 默认桥接是社区共识经验，HA 文档未解释原因）"
- **来源报告**：`S2`

### L24-26 · 原因：主服务与机器学习服务版本不一致。

- **强度**：[实测]
- **出处/依据**：手册素材来自单次事故；官方文档无此因果表述（核过 install 页与 FAQ）
- **原文/取证说明**：无上游原文；实测环境/元数据：手册素材来自单次事故；官方文档无此因果表述（核过 install 页与 FAQ）
- **手册怎么说**："**原因**：**主服务与机器学习服务版本不一致**。"
- **是否需改写**：**是** —— "原因"写成确定性诊断，依据只有一次事故。建议改为 "已知诱因：版本不一致（我们观察到的一次即如此；官方文档未记载此因果）"。
- **来源报告**：`S2`

### L39-41 · Bitwarden 系客户端依赖浏览器的加密 API，只在安全上下文 （HTTPS）里可用

- **强度**：[官方]
- **出处/依据**：https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API
- **原文/取证说明**："Secure context: This feature is available only in secure contexts (HTTPS), in some or all supporting browsers."
- **手册怎么说**："Bitwarden 系客户端依赖浏览器的加密 API，**只在安全上下文 （HTTPS）里可用**"
- **是否需改写**：否
- **来源报告**：`S2`

### L92-94 · aria2 RPC 默认无认证

- **强度**：[官方]
- **出处/依据**：https://aria2.github.io/manual/en/html/aria2c.html
- **原文/取证说明**："It is strongly recommended to set secret authorization token using --rpc-secret option"；"As of 1.18.4, in addition to HTTP basic authorization, aria2 provides RPC method-level authorization."
- **手册怎么说**：aria2 RPC 默认无认证
- **是否需改写**：否
- **来源报告**：`S2`

### L119-123 · WoL 各条（快速启动实为休眠、魔术包跨不了路由、测关机别测睡眠）

- **强度**：[社区]（取证受限：报告未附至少一个可查出处）/ [推理]
- **出处/依据**：WoL 是链路层魔术包（广播），"跨不了路由"由机制推出；Windows 快速启动=混合休眠是广泛社区常识。本轮未找到单一权威原文。
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**：WoL 各条（快速启动实为休眠、魔术包跨不了路由、测关机别测睡眠）
- **是否需改写**：否 —— 结论都站得住，但落地时建议标注为机制推理。
- **来源报告**：`S2`

### L133-141 · AI CLI 会话被注入 HTTPS_PROXY + 自签证书 MITM

- **强度**：[实测]
- **出处/依据**：手册素材来自单次真实案例；原文已写"真实案例里…"，口吻合规
- **原文/取证说明**：逐字引文已列在“出处/依据”中。
- **手册怎么说**：AI CLI 会话被注入 HTTPS_PROXY + 自签证书 MITM
- **是否需改写**：否
- **来源报告**：`S2`

## 合并说明

- 输入报告宣称共 110 条（S1 61、S2 35、S3 14），但机械计数得到 S3 **15 个断言条目**，
  所以本附录保留 **111 条**，没有为迁就汇总数字而丢弃“Tailscale 子网路由需批准”。
- S3 的“不要固定隧道传输协议”误记为 L100 附近；在基线 `6f593fa` 实际位于 L180-186。
- `services/_deployment.md` 的 S2 结论是“无上游引用型断言”，因此没有建立空章节。
- `.internal` 与 RFC 6598 已补到一手原文。freedesktop.org 的 systemd 渲染页仍无法自动读取，
  但已从 systemd 官方源码仓库的 `man/systemd.service.xml` 取得逐字原文，并保留取证路径差异。
