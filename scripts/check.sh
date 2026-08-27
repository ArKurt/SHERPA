#!/usr/bin/env bash
# anyserver 仓库自检
#   用法: scripts/check.sh [redaction|frontmatter|links|all]
set -uo pipefail
cd "$(dirname "$0")/.."
MODE="${1:-all}"
FAIL=0

hdr() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
ok()  { printf '  \033[32mok\033[0m  %s\n' "$1"; }
bad() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=1; }

# ── 1. 脱敏 ──────────────────────────────────────────────
# 公开仓库不得出现真实内网地址、真实域名或订阅关键词。
# 允许的例外：RFC 5737 文档段、RFC 2606 example.*、Tailscale 的 100.64/10 段本身。
check_redaction() {
  hdr "脱敏"
  local pat='(192\.168\.[0-9]+\.[0-9]+|10\.[0-9]+\.[0-9]+\.[0-9]+|172\.(1[6-9]|2[0-9]|3[01])\.[0-9]+\.[0-9]+)'
  local hits
  # 排除 archive/（历史原文）、redaction.md（其中 192.168.1.1 是故意举的反例）
  # 以及带掩码的 CIDR 写法（10.0.0.0/8 这类是在讲网段，不是真实主机地址）
  hits=$(grep -rEn "$pat" --include='*.md' . 2>/dev/null \
         | grep -v '^\./archive/' | grep -v '^\./appendix/redaction.md' \
         | grep -vE "$pat/[0-9]+" || true)
  [ -z "$hits" ] && ok "无私有网段地址" || { bad "发现私有网段地址（应改用 192.0.2.x）"; echo "$hits" | head -20; }

  # 100.64/10 只允许作为网段写法出现，不允许具体主机地址
  hits=$(grep -rEn '100\.(6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])\.[0-9]+\.[0-9]+' --include='*.md' . 2>/dev/null \
         | grep -v '100\.64\.0\.0/10' | grep -v '100\.100\.100\.100' | grep -v '^\./archive/' || true)
  [ -z "$hits" ] && ok "无具体 CGNAT 主机地址" || { bad "发现具体 CGNAT 地址"; echo "$hits" | head -20; }

  # 真实 MAC（排除全大写占位 AA:BB:CC:DD:EE:FF）
  hits=$(grep -rEn '([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}' --include='*.md' . 2>/dev/null \
         | grep -viE 'AA:BB:CC:DD:EE:FF' || true)
  [ -z "$hits" ] && ok "无真实 MAC" || { bad "发现疑似真实 MAC"; echo "$hits" | head -20; }

  # 订阅 / 凭证关键词
  # 只匹配真的带内容的链接；archive/ 里出现的是格式说明（裸 scheme），不是真链接
  hits=$(grep -rEni '(sub_?token=|subscribe\?token=|\b(ssr?|vmess|vless|trojan)://[A-Za-z0-9+/=_-]{8,})' \
         --include='*.md' . 2>/dev/null | grep -v '^\./archive/' || true)
  [ -z "$hits" ] && ok "无订阅链接痕迹" || { bad "发现疑似订阅/节点链接"; echo "$hits" | head -20; }

  # 外链白名单制：所有 http(s) 链接的域名必须登记在 scripts/allowed-domains.txt。
  # 既防内网域名泄漏，也避免外链无节制蔓延。
  local unknown
  # archive/ 是历史原文，其中的链接保持原样，不纳入白名单管理
  unknown=$(grep -rhoE 'https?://[A-Za-z0-9._-]+' --include='*.md' \
      --exclude-dir=archive . 2>/dev/null \
    | sed -E 's|https?://||' | sort -u \
    | grep -vE '^(192\.0\.2\.|198\.51\.100\.|203\.0\.113\.)' \
    | grep -vE '(^|\.)example\.(com|org|net)$' \
    | grep -vxE 'myserver|<[^>]*>' \
    | grep -vxFf <(grep -vE '^\s*(#|$)' scripts/allowed-domains.txt) || true)
  [ -z "$unknown" ] && ok "外链域名均已登记" || {
    bad "发现未登记的外链域名（确认无误后加进 scripts/allowed-domains.txt）"; echo "$unknown" | sed 's/^/       /'; }

  # 裸写的真实域名（不在 URL 里的），仍按后缀拦
  hits=$(grep -rEn '(^|[^/A-Za-z0-9._-])[a-z0-9-]+\.(uk|xyz|top)\b' --include='*.md' . 2>/dev/null \
         | grep -v '^\./archive/' || true)
  [ -z "$hits" ] && ok "无裸写的可疑域名" || { bad "发现可疑域名"; echo "$hits" | head -20; }
}

# ── 2. frontmatter ───────────────────────────────────────
check_frontmatter() { hdr "frontmatter"; python3 scripts/check_frontmatter.py || FAIL=1; }

# ── 3. 内链 ──────────────────────────────────────────────
check_links() { hdr "内链"; python3 scripts/check_links.py || FAIL=1; }

# ── 4. catalog 同步 ──────────────────────────────────────
# wizard 的数据全部由 frontmatter 生成。改了手册忘了重新生成 → 两份漂移。
check_catalog() { hdr "catalog 同步"; python3 scripts/build-catalog.py --check || FAIL=1; }

case "$MODE" in
  redaction)   check_redaction ;;
  frontmatter) check_frontmatter ;;
  links)       check_links ;;
  catalog)     check_catalog ;;
  all)         check_redaction; check_frontmatter; check_links; check_catalog ;;
  *) echo "用法: $0 [redaction|frontmatter|links|catalog|all]"; exit 2 ;;
esac

echo
if [ "$FAIL" -eq 0 ]; then
  printf '\033[32m全部通过\033[0m\n'
  cat <<'NOTE'

  ⚠️ 「通过」只代表机械检查过了。本脚本查不了：
     · 内容是否自相矛盾（两处对同一件事给出相反结论）
     · 判据是否正确（比如某个服务到底能不能放在某种盘上）
     · verify 命令是否真的可执行、期望值是否正确
     · 导航是否合理（该读到的东西会不会被漏掉）
  这些只能靠人读，或靠一次端到端演练——见 README「怎么验证这本手册」。
NOTE
  exit 0
else
  printf '\033[31m有检查未通过\033[0m\n'; exit 1
fi
