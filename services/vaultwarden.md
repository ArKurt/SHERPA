---
id: vaultwarden
name: Vaultwarden
layer: service
install_when: anytime
category: privacy
goals: [密码与隐私]
summary: 自托管的密码库
blurb: |
  所有账号密码存在你自己家里的机器上，浏览器插件和手机 App 自动填充。
  和主流商业密码管理器用同一套客户端，体验一样，但**数据不在别人手上**。
  ⚠️ 它存的是你的全部密码——这是本手册里安全要求最高的服务，别草率上。
docs:
  - type: official
    title: Vaultwarden Wiki（部署与配置）
    url: https://github.com/dani-garcia/vaultwarden/wiki
requires:
  arch: [x86_64, aarch64]
  substrate: [bare-metal, vm, container]
  storage: [internal, das-enclosure]
conflicts: []
risk: medium
needs_human: true          # 存的是全部密码，暴露策略必须用户拍板
verify: |
  # 从【另一台设备】，必须走 HTTPS
  curl -s -o /dev/null -w '%{http_code}\n' https://vault.example.com/alive
  # 期望: 200
  # ★ 真正的验收：浏览器扩展能登录并解锁。见下
rollback: |
  docker compose down    # 先确认已有可恢复的备份
---

# Vaultwarden

Bitwarden 的轻量自托管实现。**这是本手册里安全要求最高的服务——它存着用户的全部密码。**

## 三件事必须先想清楚（`needs_human` 的理由）

### 暴露策略

| 方案 | 评价 |
|---|---|
| **只走组网工具（Tailscale 等）** | **风险最低**。密码库不需要给不特定的人访问 |
| 隧道 + 强认证 | 可行，但要认真做认证层 |
| 端口转发直接暴露 | **不要**。密码库是最高价值目标 |

默认应当是第一种。→ [层 6](../layers/6-ingress.md#tailscale--组网工具)

### 必须是 HTTPS

Bitwarden 客户端依赖浏览器的加密 API，**只在安全上下文里可用**。
纯 HTTP 访问（localhost 除外）时，客户端会无法解锁，且报错很难懂。

组网工具方案下也要处理证书——用它提供的证书功能，或自建 CA。

### 备份

**没有备份的密码库比没有密码库更危险**——你会把所有密码都换成只存在那里的强随机串，
然后某天它没了。

⚠️ **不要在服务运行时直接 `cp db.sqlite3`。** 可能复制到一个写入进行到一半的文件——
拷的时候不报错，等到要恢复才发现副本是坏的。上游给了两条正确做法：

```sh
# 首选：Vaultwarden 1.32.1+ 自带的备份命令
docker compose exec vaultwarden /vaultwarden backup

# 或用 SQLite 的 Online Backup API（服务不必停），在宿主上对数据目录跑
sqlite3 <数据目录>/db.sqlite3 ".backup '<备份目录>/db.sqlite3'"
```

数据库之外还要一并带走：`attachments/`、`sends/`、`rsa_key.pem`、`config.json`。

- 备份放到**另一块物理盘**
- **试一次恢复。** 没验证过的备份不算备份
- ⚠️ **备份整体不是加密的。** 保险库条目由各用户的主密码加密，
  但数据目录里还有明文的敏感内容——`config.json` 就含 admin token、SMTP 凭证。
  上游因此建议**对备份再加一层加密**
  （*Adding an extra layer of encryption on your backups would generally be a good idea*）。
  **放上 NAS 或云盘之前先加密**，别把它当成"反正已经加密过了"。

## 存储

数据库是 SQLite，小但苛刻。放本地原生文件系统，**不要 exFAT、不要网络挂载**——
理由同 [层 5](../layers/5-storage.md)。

## 建议关掉注册

自用的话把开放注册关掉，只留邀请。否则任何能访问到的人都能建账号。

## 真正的验收

```
1. 浏览器扩展指向你的地址 → 能登录
2. 能解锁保险库（这一步才验证 HTTPS/加密上下文是对的）
3. 手机 App 也连一次
4. ★ 断开服务，从备份恢复一次，确认数据完整
```

第 4 条是这个服务唯一真正重要的验收。

## 架构

官方发 multi-arch。

---

> 📎 **本页断言的出处与强度**：[`appendix/sources.md`](../appendix/sources.md#services-vaultwarden)
