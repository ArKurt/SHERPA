#!/usr/bin/env python3
"""校验 layers/ 与 services/ 模块的 frontmatter：
   - 能被解析
   - requires 的键名落在配置向量字段里，取值落在各层枚举里
   - conflicts 双向对称
   - verify 从客户端视角（启发式）
"""
import sys, pathlib, yaml, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
fails = []
def bad(m): fails.append(m); print(f"  \033[31mFAIL\033[0m {m}")
def ok(m):  print(f"  \033[32mok\033[0m  {m}")

# 配置向量的合法字段与取值（与 layers/ 各章保持一致）
VECTOR = {
    "arch":      {"x86_64", "aarch64"},
    "substrate": {"bare-metal", "vm", "container", "none"},
    "gateway":   {"vm-openwrt", "container-macvlan", "dedicated-box", "client-only", "none"},
    "proxy":     {"nikki", "shellcrash", "openclash", "homeproxy", "client-side", "none"},
    "storage":   {"internal", "usb-portable", "das-enclosure", "nas"},
    "ingress":   {"none", "tailscale", "tunnel", "port-forward"},
    "addressing": {"ip-static", "hosts-file", "lan-dns", "mdns"},
}
RISK = {"none", "low", "medium", "high"}
# 多值字段：向量里是列表，requires 的判定是「交集非空」而非「属于」
MULTI = {"substrate", "storage", "addressing"}

def load(p):
    t = p.read_text(encoding="utf-8")
    if not t.startswith("---"):
        return None
    end = t.find("\n---", 3)
    if end < 0:
        bad(f"{p.relative_to(ROOT)}: frontmatter 未闭合")
        return None
    try:
        return yaml.safe_load(t[3:end]) or {}
    except yaml.YAMLError as e:
        bad(f"{p.relative_to(ROOT)}: YAML 解析失败 — {e}")
        return None

# ── 枚举的单一真相源是 layers/：内置 VECTOR 必须与层文件声明的 options 一致 ──
declared = {}
for p in sorted((ROOT / "layers").glob("*.md")):
    fm = load(p)
    if fm is None:
        bad(f"{p.relative_to(ROOT)}: 缺 frontmatter（层文件必须声明它定义的向量字段与枚举）")
        continue
    f, opts = fm.get("field"), fm.get("options")
    if f and opts:
        declared[f] = set(opts)
        if f in VECTOR and declared[f] != VECTOR[f]:
            bad(f"{p.relative_to(ROOT)}: options 与校验器内置 VECTOR['{f}'] 不一致 — "
                f"只在层里有 {sorted(declared[f]-VECTOR[f])}，只在 VECTOR 里有 {sorted(VECTOR[f]-declared[f])}")
for f in VECTOR:
    if f not in declared and f != "arch":
        bad(f"VECTOR['{f}'] 没有任何层文件声明它 — 枚举失去单一真相源")
if not fails: ok("层枚举与向量定义一致")

mods = {}
for d in ("services", "layers", "blueprints"):
    for p in sorted((ROOT / d).glob("*.md")):
        if p.name in ("README.md", "_schema.md"):
            continue
        fm = load(p)
        if fm is None:
            continue
        mid = fm.get("id")
        if not mid:
            bad(f"{p.relative_to(ROOT)}: 缺 id")
            continue
        if mid in mods:
            bad(f"{p.relative_to(ROOT)}: id '{mid}' 与 {mods[mid]['path']} 重复")
        mods[mid] = {"fm": fm, "path": p.relative_to(ROOT)}

if not mods:
    bad("没有找到任何带 frontmatter 的模块")

# requires 键名与取值
for mid, m in mods.items():
    req = m["fm"].get("requires") or {}
    if not isinstance(req, dict):
        bad(f"{m['path']}: requires 应为映射"); continue
    for k, v in req.items():
        if k not in VECTOR:
            bad(f"{m['path']}: requires 的键 '{k}' 不是配置向量字段 {sorted(VECTOR)}")
            continue
        if k in MULTI and not isinstance(v, list):
            bad(f"{m['path']}: requires.{k} 是多值字段，必须写成列表")
        vals = v if isinstance(v, list) else [v]
        for val in vals:
            if val not in VECTOR[k]:
                bad(f"{m['path']}: requires.{k} 的取值 '{val}' 不在枚举 {sorted(VECTOR[k])} 中")
if not fails: ok("requires 键名与取值合法")

# risk / needs_human
n = len(fails)
for mid, m in mods.items():
    fm = m["fm"]
    if "risk" in fm and fm["risk"] not in RISK:
        bad(f"{m['path']}: risk '{fm['risk']}' 不在 {sorted(RISK)} 中")
    if fm.get("risk") == "high" and not fm.get("needs_human"):
        bad(f"{m['path']}: risk=high 必须同时 needs_human=true")
    if fm.get("layer") == "service" and fm.get("install_when") not in ("anytime", "last", None):
        bad(f"{m['path']}: install_when 只能是 anytime / last，见 services/_schema.md")
    if "needs_human" in fm and not isinstance(fm["needs_human"], bool):
        bad(f"{m['path']}: needs_human 应为布尔值")
if len(fails) == n: ok("risk / needs_human 合法")

# conflicts 双向对称
n = len(fails)
for mid, m in mods.items():
    for other in (m["fm"].get("conflicts") or []):
        if other not in mods:
            continue  # 引用了本仓库未收录的模块，允许
        back = mods[other]["fm"].get("conflicts") or []
        if mid not in back:
            bad(f"conflicts 不对称: {mid} 声明冲突 {other}，但 {other} 未声明冲突 {mid}")
if len(fails) == n: ok("conflicts 双向对称")

# verify 必须从客户端视角（启发式：要么提到客户端，要么给了非本机地址）
n = len(fails)
for mid, m in mods.items():
    v = m["fm"].get("verify")
    if v is None:
        continue
    if not isinstance(v, str):
        bad(f"{m['path']}: verify 应为字符串块"); continue
    client_hint = ("客户端" in v or "另一台" in v or "外网" in v or "192.0.2." in v
                   or "198.51.100." in v or "example.com" in v)
    # 只看真正的命令行——注释行里提到 127.0.0.1 通常是在警告"别绑本地"，不算违规
    cmd_lines = [l for l in v.split("\n") if l.strip() and not l.strip().startswith("#")]
    localhost   = any(re.search(r'\b(localhost|127\.0\.0\.1)\b', l) for l in cmd_lines)
    if localhost:
        bad(f"{m['path']}: verify 的命令指向 localhost/127.0.0.1 — 必须从客户端视角验证")
    elif not client_hint:
        bad(f"{m['path']}: verify 未体现客户端视角（应注明在客户端/另一台机器执行）")
if len(fails) == n: ok("verify 均为客户端视角")

# 标题不得含 emoji 或圈码 —— 这两类字符在不同 slug 实现间行为不一致，
# 会产生"看起来对但点不到"的锚点。其它标点（：（）· 、/ —）两边都一致剔除，可用。
import re as _re
BADCH = _re.compile(r'[\u2460-\u2473\u24b6-\u24ea]|[\U0001F000-\U0001FAFF]|[\u2600-\u27BF]|\ufe0f')
n = len(fails)
for p in sorted(ROOT.rglob("*.md")):
    # archive/ 是历史原文，不受手册规范约束
    if ".git" in p.parts or "archive" in p.parts or "reviews" in p.parts:
        continue
    infence = False
    for i, ln in enumerate(p.read_text(encoding="utf-8").split("\n"), 1):
        if ln.lstrip().startswith("```"):
            infence = not infence; continue
        if infence:
            continue
        m = re.match(r'^#{1,6}\s+(.*)$', ln)
        if m and BADCH.search(m.group(1)):
            bad(f"{p.relative_to(ROOT)}:{i}: 标题含 emoji/圈码，会产生不稳定锚点 — {m.group(1)!r}")
if len(fails) == n: ok("标题无 emoji/圈码")

# 层的验收写在「## 验收」小节里，不在 frontmatter —— 之前这块完全没被检查过。
# 契约要求所有 verify 都从客户端视角写，层也不例外。
n = len(fails)
for p in sorted((ROOT / "layers").glob("*.md")):
    fm = load(p)
    if not fm or fm.get("layer") in (1,):        # 层 1 是底座选型，没有可验收的动作
        continue
    txt = p.read_text(encoding="utf-8")
    if "## 验收" not in txt:
        bad(f"{p.relative_to(ROOT)}: 缺「## 验收」小节")
        continue
    sec = txt.split("## 验收", 1)[1].split("\n## ", 1)[0]
    if "verify: |" not in sec:
        bad(f"{p.relative_to(ROOT)}: 验收小节里没有 verify 块")
        continue
    if not any(k in sec for k in ("客户端", "另一台", "外网", "真实设备")):
        bad(f"{p.relative_to(ROOT)}: 验收未体现客户端视角")
    if re.search(r'^\s*(curl|nslookup|dig)\b.*\b(localhost|127\.0\.0\.1)',
                 sec, re.M):
        bad(f"{p.relative_to(ROOT)}: 验收命令指向 localhost")
if len(fails) == n: ok("层的验收均为客户端视角")

# 服务菜单必须与目录一一对应 —— 新增服务忘了挂进菜单，读者就永远看不到它
menu = (ROOT / "services" / "README.md").read_text(encoding="utf-8")
svc_ids = {m["fm"]["id"] for m in mods.values() if m["fm"].get("layer") == "service"}
missing = sorted(i for i in svc_ids if f"]({i}.md)" not in menu)
if missing:
    bad(f"services/README.md 漏了：{missing}")
else:
    ok("服务菜单与目录一致")

print(f"\n  共 {len(mods)} 个模块")
sys.exit(1 if fails else 0)
