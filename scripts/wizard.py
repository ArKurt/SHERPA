#!/usr/bin/env python3
"""把装机向导跑起来，并把生成的装机清单直接交回调用者。

给 agent 用：
    scripts/wizard.py                  # 起服务、开浏览器、等用户答完、清单打到 stdout
    scripts/wizard.py --out sheet.md   # 同时写到文件
    scripts/wizard.py --no-browser     # 不自动开浏览器，只打印 URL（无头环境）

给人用：直接双击 wizard.html 也行——那种模式下页面显示「复制 / 下载」按钮。

为什么需要这个脚本：file:// 打开的页面源是 null，浏览器不让它写文件、
也基本不让它往本地服务 POST。让调用方自己把页面服起来，就变成同源，
页面可以直接把结果 POST 回来——**用户答完，agent 就拿到了，中间没有手工步骤。**

只用标准库，只监听 127.0.0.1。
"""
import argparse, http.server, json, socket, socketserver, sys, threading, time, webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "wizard.html"

result = {"sheet": None}
done = threading.Event()


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):          # 别把 HTTP 日志混进 stdout——那是清单的通道
        pass

    def _send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html", "/wizard.html"):
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        else:
            self._send(404)

    def do_POST(self):
        if self.path != "/submit":
            return self._send(404)
        n = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, b"bad json")
        result["sheet"] = payload.get("sheet", "")
        self._send(200, b'{"ok":true}', "application/json")
        done.set()


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    ap = argparse.ArgumentParser(description="跑装机向导，把清单交回调用者")
    ap.add_argument("--out", metavar="FILE", help="同时写入这个文件")
    ap.add_argument("--no-browser", action="store_true", help="不自动开浏览器")
    ap.add_argument("--timeout", type=int, default=1800, help="等待秒数，默认 30 分钟")
    args = ap.parse_args()

    if not PAGE.exists():
        print("找不到 wizard.html——先跑 scripts/build-catalog.py", file=sys.stderr)
        return 2

    port = free_port()
    url = f"http://127.0.0.1:{port}/"
    srv = socketserver.TCPServer(("127.0.0.1", port), Handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    # 提示走 stderr，stdout 留给清单本身——这样 agent 可以直接管道接
    print(f"装机向导已启动：{url}", file=sys.stderr)
    print("在浏览器里答完三轮问题，清单会自动回到这里。", file=sys.stderr)
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            print("（打不开浏览器，请手动访问上面的地址）", file=sys.stderr)

    try:
        ok = done.wait(timeout=args.timeout)
    except KeyboardInterrupt:
        print("\n已取消。", file=sys.stderr)
        return 130
    finally:
        srv.shutdown()

    if not ok:
        print(f"等了 {args.timeout} 秒没有收到清单。", file=sys.stderr)
        return 1

    sheet = result["sheet"] or ""
    if args.out:
        Path(args.out).write_text(sheet, encoding="utf-8")
        print(f"已写入 {args.out}", file=sys.stderr)
    print(sheet)                      # ← agent 从 stdout 拿
    return 0


if __name__ == "__main__":
    sys.exit(main())
