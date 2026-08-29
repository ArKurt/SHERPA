#!/usr/bin/env python3
"""检查所有 markdown 相对链接指向存在的文件，以及带 #锚点 的目标标题存在。"""
import sys, pathlib, re, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')
fails = []

def slug(text):
    """GitHub 风格锚点：小写、去标点、空格转连字符。

    标题里不应出现 emoji / 圈码 / 间隔号 / 全角括号 —— 那些字符在不同 slug 实现
    之间处理不一致，会产生"看起来对但点不到"的锚点。scripts/check.sh 会拦。
    """
    # 与 GitHub 一致：小写 → 去掉非 [\w- ] 字符 → 每个空格换一个连字符。
    # 注意是「每个」——连续空格会变成连续连字符，不折叠。这一点必须和 GitHub 相同，
    # 否则本地检查通过、线上锚点点不到。
    t = text.strip().lower()
    t = re.sub(r'[`*_\[\]]', '', t)
    t = re.sub(r'[^\w\- ]', '', t, flags=re.UNICODE)
    return t.replace(' ', '-')

# 收集每个文件的锚点
anchors = {}
for p in ROOT.rglob("*.md"):
    if ".git" in p.parts:
        continue
    s = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            s.add(slug(m.group(2)))
        # 显式锚点：<a id="x"></a> / <a name="x"></a>。GitHub 认这种写法，
        # 用它可以让锚点在标题改写后仍然稳定——appendix/sources.md 就靠它。
        for a in re.findall(r'<a\s[^>]*\b(?:id|name)\s*=\s*["\']([^"\']+)["\']', line):
            s.add(a)
    anchors[p.resolve()] = s

def outside_code(text):
    """去掉围栏代码块——里面的链接是示例，不该当成真链接检查。"""
    out, fence = [], False
    for ln in text.split("\n"):
        if ln.lstrip().startswith("```"):
            fence = not fence
            continue
        if not fence:
            out.append(ln)
    return "\n".join(out)

# archive/ 是历史原文，不改，也不参与内链检查。
SKIP_DIRS = {"archive"}

for p in sorted(ROOT.rglob("*.md")):
    if ".git" in p.parts or SKIP_DIRS & set(p.parts):
        continue
    for target in LINK.findall(outside_code(p.read_text(encoding="utf-8"))):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        path_part, _, frag = target.partition("#")
        dest = (p.parent / path_part).resolve() if path_part else p.resolve()
        if not dest.exists():
            fails.append(f"{p.relative_to(ROOT)} → {target} （文件不存在）")
            continue
        if frag and dest.is_file():
            if frag not in anchors.get(dest, set()):
                fails.append(f"{p.relative_to(ROOT)} → {target} （锚点不存在）")

for f in fails:
    print(f"  \033[31mFAIL\033[0m {f}")
if not fails:
    print(f"  \033[32mok\033[0m  所有内链有效")
sys.exit(1 if fails else 0)
