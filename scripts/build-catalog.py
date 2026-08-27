#!/usr/bin/env python3
"""从 markdown frontmatter 生成服务目录，并把它内联进 wizard.html。

单一真相源纪律：wizard 里的服务列表、依赖、冲突关系【绝不手写】，
全部由本脚本从 services/*.md 与 layers/*.md 抽取。
手册改了、忘了重新生成 → scripts/check.sh 会报不同步。

用法:
    scripts/build-catalog.py            # 生成 data/catalog.json 与 wizard.html
    scripts/build-catalog.py --check    # 只校验是否与源同步，不写文件
"""
import json, pathlib, sys, subprocess, hashlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "data" / "catalog.json"
TEMPLATE = ROOT / "wizard.template.html"
OUT_HTML = ROOT / "wizard.html"
MARKER = "/*__CATALOG__*/"


def frontmatter(path):
    t = path.read_text(encoding="utf-8")
    if not t.startswith("---"):
        return None
    end = t.find("\n---", 3)
    if end < 0:
        return None
    return yaml.safe_load(t[3:end]) or {}


def build():
    services, goals, categories = [], {}, set()
    for p in sorted((ROOT / "services").glob("*.md")):
        if p.name in ("README.md", "_schema.md", "_deployment.md"):
            continue
        fm = frontmatter(p)
        if not fm:
            continue
        entry = {
            "id": fm["id"],
            "name": fm.get("name", fm["id"]),
            "category": fm.get("category", "tools"),
            "goals": fm.get("goals", []),
            "summary": fm.get("summary", ""),
            "blurb": (fm.get("blurb") or "").strip(),
            "priority": fm.get("priority", "P2"),
            "requires": fm.get("requires") or {},
            "conflicts": fm.get("conflicts") or [],
            "risk": fm.get("risk", "none"),
            "needs_human": bool(fm.get("needs_human")),
            "docs": fm.get("docs") or [],
            "doc": f"services/{p.name}",
        }
        services.append(entry)
        categories.add(entry["category"])
        for g in entry["goals"]:
            goals.setdefault(g, []).append(entry["id"])

    layers = []
    for p in sorted((ROOT / "layers").glob("*.md")):
        fm = frontmatter(p)
        if not fm or not fm.get("field"):
            continue
        layers.append({
            "layer": fm["layer"],
            "field": fm["field"],
            "multi": bool(fm.get("multi")),
            "optional": bool(fm.get("optional")),
            "goals": fm.get("goals") or [],
            "options": fm.get("options") or [],
            "doc": f"layers/{p.name}",
        })
        for g in (fm.get("goals") or []):
            goals.setdefault(g, [])

    chapters = []
    for p in sorted((ROOT / "advanced").glob("*.md")):
        fm = frontmatter(p)
        if not fm:
            continue
        chapters.append({
            "id": fm["id"], "name": fm.get("name", fm["id"]),
            "goals": fm.get("goals") or [], "doc": f"advanced/{p.name}",
        })
        for g in (fm.get("goals") or []):
            goals.setdefault(g, [])

    blueprints = []
    for p in sorted((ROOT / "blueprints").glob("*.md")):
        fm = frontmatter(p)
        if not fm:
            continue
        blueprints.append({
            "id": fm["id"],
            "name": fm.get("name", fm["id"]),
            "status": fm.get("status", ""),
            "doc": f"blueprints/{p.name}",
        })

    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"

    return {
        "commit": commit,
        "goals": sorted(goals),
        "categories": sorted(categories),
        "layers": sorted(layers, key=lambda x: x["layer"]),
        "services": services,
        "chapters": chapters,
        "blueprints": blueprints,
    }


def render_html(catalog):
    if not TEMPLATE.exists():
        return None
    tpl = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in tpl:
        print(f"  模板里找不到 {MARKER}", file=sys.stderr)
        return None
    # 内联进 HTML —— 双击打开时 fetch() 本地 JSON 会被浏览器拦，必须内联
    return tpl.replace(MARKER, "const CATALOG = " + json.dumps(
        catalog, ensure_ascii=False, indent=2) + ";")


def main():
    check = "--check" in sys.argv
    cat = build()
    blob = json.dumps(cat, ensure_ascii=False, indent=2) + "\n"

    if check:
        fails = []
        if not OUT_JSON.exists():
            fails.append("data/catalog.json 不存在——先跑 scripts/build-catalog.py")
        else:
            cur = json.loads(OUT_JSON.read_text(encoding="utf-8"))
            a = {k: v for k, v in cur.items() if k != "commit"}
            b = {k: v for k, v in cat.items() if k != "commit"}
            if a != b:
                fails.append("data/catalog.json 与 markdown 源不同步——重新生成")
        html = render_html(cat)
        if html is not None and OUT_HTML.exists() and OUT_HTML.read_text(encoding="utf-8") != html:
            fails.append("wizard.html 与源不同步——重新生成")
        for f in fails:
            print(f"  \033[31mFAIL\033[0m {f}")
        if not fails:
            print(f"  \033[32mok\033[0m  catalog 与源同步（{len(cat['services'])} 个服务）")
        return 1 if fails else 0

    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(blob, encoding="utf-8")
    print(f"  写入 {OUT_JSON.relative_to(ROOT)}"
          f"（{len(cat['services'])} 服务 / {len(cat['layers'])} 层 / {len(cat['goals'])} 目标）")
    html = render_html(cat)
    if html is not None:
        OUT_HTML.write_text(html, encoding="utf-8")
        print(f"  写入 {OUT_HTML.relative_to(ROOT)}")
    else:
        print("  （尚无 wizard.template.html，跳过 HTML 生成）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
