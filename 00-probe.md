# 00 · 探针：先搞清楚用户有什么

> 读这个仓库的第一站。产出一个**配置向量**，后续所有选型都基于它。
> 字段定义见 [`services/_schema.md`](services/_schema.md#配置向量)。

探针分两类，**不要混**：

- **机器能查的** —— 直接跑命令，别问用户
- **必须问用户的** —— 探测不到，或答案取决于用户意愿而非硬件

问用户能查到的东西是浪费对方时间；替用户猜必须问的东西会出事。

---

## 一、机器能查的

### 1. 架构与平台

```sh
uname -srm
```

| 输出含 | 平台 | 往下走 |
|---|---|---|
| `Darwin ... arm64` | Apple Silicon Mac | §2a |
| `Darwin ... x86_64` | Intel Mac | §2a |
| `Linux ... x86_64` | 通用 x86 机器 / 软路由盒子 | §2b |
| `Linux ... aarch64` | ARM 单板 / 部分 NAS | §2b |

NAS 另外确认厂商系统（QNAP QTS/QuTS、群晖 DSM、unRAID、TrueNAS）——它们的虚拟化与容器
是厂商套件，不是通用方案。

**架构决定的事**：容器镜像要有对应 arch 的构建。绝大多数主流服务都发 multi-arch，
但**动手前逐个查一遍 manifest**，别假设。查法：

```sh
docker manifest inspect <image>:<tag> | grep -A2 architecture
```

### 2a. 虚拟化能力：macOS

```sh
sysctl kern.hv_support        # 1 = 支持硬件加速虚拟化
which qemu-system-aarch64 qemu-system-x86_64 2>/dev/null
```

`kern.hv_support: 1` 意味着可以用 hvf 加速，VM 性能接近原生。

### 2b. 虚拟化能力：Linux

```sh
grep -cE 'vmx|svm' /proc/cpuinfo    # >0 = CPU 支持
ls -l /dev/kvm 2>/dev/null          # 存在且可读写 = KVM 可用
```

`/dev/kvm` 不存在通常是 BIOS 里没开 VT-x/AMD-V，**这要用户去 BIOS 开，属于问人的事**。

### 2c. 虚拟化能力：NAS

厂商套件是否已安装并可用（QNAP 的 Virtualization Station / Container Station、
群晖的 Virtual Machine Manager / Container Manager）。查不到就当没有，别猜型号支持情况。

### 3. 内存与存储

```sh
# Linux
free -h; lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT,TRAN
# macOS
sysctl hw.memsize; diskutil list; mount | grep -E '^/dev'
```

要记下的是每块盘的：**容量、文件系统、是不是外接、走什么总线（USB / 内置 / 网络挂载）**。
文件系统与总线直接决定它能不能承载数据库——见 [`layers/5-storage.md`](layers/5-storage.md)。

### 4. 网卡

```sh
# Linux
ip -br link
# macOS
networksetup -listallhardwareports
```

**数一下有几个可用网口。** 这不是凑数：桥接操作会短暂中断被桥接的那张网卡，
**有第二条路（另一张网卡 / Wi-Fi）才能在出问题时不失联**。只有一个网口时，
高风险操作必须在物理接触得到机器的场合做。

### 5. 现有网络位置

```sh
# Linux
ip route | grep default; cat /etc/resolv.conf
# macOS
route -n get default; scutil --dns | grep nameserver | head
```

记下当前网关与 DNS。**如果发现默认网关指向一台已经不存在的设备，先解决这个**——
残留路由会造成"有的进程能连、有的连不上"这类极难诊断的间歇故障，且症状不指向真凶。

---

## 二、必须问用户的

以下探测不到，或答案取决于意愿。**逐条问清楚，不要替用户决定。**

### Q1. 主路由能不能给设备绑定固定 IP？

旁路由必须有稳定地址，否则客户端指过去的网关随时会失效。

- **能** → 让用户在主路由上绑定（**告诉他怎么做，不要代劳** —— 铁律①）
- **不能 / 不确定** → 旁路由内部配静态 IP，并提醒用户该地址可能与主路由的 DHCP 池冲突，
  需要把它排除在池外或选一个池外地址

### Q2a. 需不需要代理？

**先问这个，不要跳过。** 本手册的旁路由章节全部围绕透明代理展开，
但**"想要一台家庭服务器"和"想要代理"是两个独立的需求**，很多用户只要前者。

| 答案 | 结论 |
|---|---|
| **不需要** | `gateway: none`、`proxy: none`。**层 2、层 3、层 4 整片跳过**，直接去挑服务 |
| 需要 | 继续 Q2b |
| 不确定 / 没提过 | ⚠️ **当作"不需要"，并明确告诉用户你跳过了这部分。** 不要替用户假设 |

⚠️ **用户没主动提代理、订阅、机场、翻墙，就不要主动引入。** 装一套透明代理会
显著增加故障面和维护量，而且它是"全屋断网"这个风险的主要来源。
硬塞给一个只想备份照片的人，是帮倒忙。

### Q2b. 有装不了客户端代理的设备吗？

这个问题决定要不要做旁路由，比任何技术对比都重要。
**旁路由唯一不可替代的场景，就是"这台设备本身装不了代理"。**

| 你的设备 | `gateway` 取值方向 |
|---|---|
| **有**电视 / 游戏机 / 投影 / IoT 要走代理 | 需要旁路由 |
| 只有电脑和手机（都能自己装客户端） | `client-only`——更简单，也没有单点故障 |

→ 详见 [层 2](layers/2-gateway.md)。

### Q2c. 接管范围多大？

| 答案 | 说明 |
|---|---|
| 几台指定设备手动指网关 | **推荐的起步形态**，影响面可控 |
| 全屋默认（主路由下发网关） | `risk: high`，必须分步走，必须问清楚 |

**不要默认用户想要全屋接管。** 全屋接管意味着旁路由变成单点故障——
它一挂，全家断网，包括根本不在乎代理的人。

⚠️ 用户说"我自己的电脑和电视能用就行"时，**这句话通常是在说"别影响家里其他人"**，
即接管范围的问题，不是"要不要旁路由"的问题。两件事分开确认。

工作室 / 微型企业尤其要问清楚：**断网即停工**。那里更该用"指定设备走"。

### Q3. 要不要从外网访问？

- **不要** → [`layers/6-ingress.md`](layers/6-ingress.md) **整层跳过**。省掉域名、证书、
  隧道账号一堆事，攻击面也小。
- **只有自己/同事要访问** → 优先 Tailscale，零公网暴露
- **要给外人访问（分享媒体、公开站点）** → 才需要隧道或端口转发

### Q4. 想跑哪些服务？

给用户看 [`services/`](services/) 的清单让他挑，不要预设。挑完再回头核对每个服务的
`requires`——尤其**存储要求**，这会反过来影响 Q5。

### Q5. 现有存储怎么用？

用 §3 查到的盘况，问用户每块盘的**用途意愿**。四种形态的能力边界见
[`layers/5-storage.md`](layers/5-storage.md)——那里不推荐任何一种，但每种都标了
"绝不能承载什么"。**先确认数据库类服务有合格的落点，再谈别的。**

### Q5b. 家里有哪些"难伺候"的客户端？

决定 [层 7 · 内网寻址](layers/7-lan-addressing.md) 怎么选。**问具体设备，别问抽象需求。**

| 有没有 | 影响 |
|---|---|
| 电视 / 机顶盒 | ❌ 基本不支持 `.local` 自动发现 → 需要 `lan-dns` |
| Android 手机 | ⚠️ mDNS 支持不完整，很多 App 解析不了 |
| 只有 Mac 和 iPhone | ✅ `.local` 开箱可用，可以先不折腾 DNS |

⚠️ **顺便问一句：有没有自己的域名？** 有的话，内网用它的子域是最省事的选择——
既不会和公网冲突，又能签真证书。这个问题在配 HTTPS 时才暴露，那时返工很烦。

### Q6. 这台机器会关机或睡眠吗？

决定要不要做开机自恢复（[`ops/boot-persistence.md`](ops/boot-persistence.md)）。

⚠️ **就算不做旁路由，睡眠也有后果**，而且容易被忽略：

- 手机的照片自动备份 → 机器睡着时传不上去，得等它醒
- 电视上点开影音库 → 要先等机器唤醒，或者干脆看不到服务
- 定时任务（备份、清理）→ **不会补跑**，那一次就是没跑

⚠️ 如果这台机器**同时**要当旁路由又会睡眠，那更是硬矛盾：它睡了，
指着它的客户端直接断网。

笔记本尤其要问：**合盖会不会睡？** 很多人默认合盖=收起来，
而那正好是它该干活的时候。

---

## 三、产出配置向量

把上面的结论填成：

```yaml
# 单值
arch:       x86_64 | aarch64
gateway:    none | vm-openwrt | container-macvlan | dedicated-box | client-only
proxy:      none | nikki | shellcrash | openclash | homeproxy | client-side
ingress:    none | tailscale | tunnel | port-forward

# 多值（写成列表）
substrate:  [bare-metal, vm, container]
storage:    [internal, usb-portable, das-enclosure, nas]
addressing: [ip-static, hosts-file, lan-dns, mdns]
services:   [...]
```

## 四、先对锚点

**拿向量去 [`blueprints/`](blueprints/) 对三条已验证路径**：

| 锚点 | 大致向量 |
|---|---|
| [A · 老笔记本一肩挑](blueprints/a-single-laptop.md) | `x86_64` + `vm` + `vm-openwrt`，服务栈也塞在同一个 VM 里 |
| [B · 混合](blueprints/b-hybrid-mini.md) | 服务栈原生跑，旁路由单独一个轻量 VM |
| [C · NAS 底座](blueprints/c-nas.md) | 厂商虚拟化套件 + 单臂旁路由（**未落地验证**） |

- **对得上** → 走那条，只读它引用的层，省掉逐层求解
- **对不上** → 进 [`layers/`](layers/)，从 [1-substrate](layers/1-substrate.md) 顺着往下

对不上是常态，不是异常。锚点是加速器，不是选项清单。
