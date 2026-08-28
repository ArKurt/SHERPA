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

只用标准库，默认只监听 127.0.0.1。

⚠️ 这条通道交回的清单是 agent 的开工依据，所以 /submit 必须带令牌：
令牌每次启动随机生成、只注入进本进程服出去的那一份页面。没有它的话，
本机任何进程都能抢先 POST 一份伪造的清单，等于直接给 agent 注入地面真相。
"""
import argparse, hmac, http.server, json, secrets, socketserver, sys, threading, webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "wizard.html"

TOKEN = secrets.token_urlsafe(24)
result = {"sheet": None}
done = threading.Event()


def page_with_token() -> bytes:
    """把令牌注入页面。页面在 file:// 下读不到它，那条分支本来也不 POST。"""
    html = PAGE.read_text(encoding="utf-8")
    inject = '<script>window.WIZARD_TOKEN=%s;</script>' % json.dumps(TOKEN)
    if "</head>" in html:
        html = html.replace("</head>", inject + "</head>", 1)
    else:
        html = inject + html
    return html.encode("utf-8")


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
        if self.path.split("?", 1)[0] in ("/", "/index.html", "/wizard.html"):
            self._send(200, page_with_token(), "text/html; charset=utf-8")
        else:
            self._send(404)

    def do_POST(self):
        if self.path != "/submit":
            return self._send(404)

        # text/plain 是浏览器免预检的 simple request 类型——只收 json，
        # 顺手把那条跨源路径挡掉。
        ctype = (self.headers.get("Content-Type") or "").split(";", 1)[0].strip()
        if ctype != "application/json":
            return self._send(415, b"expected application/json")

        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._send(400, b"bad content-length")
        if n <= 0 or n > 4 * 1024 * 1024:
            return self._send(400, b"bad length")

        try:
            payload = json.loads(self.rfile.read(n))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self._send(400, b"bad json")
        if not isinstance(payload, dict):
            return self._send(400, b"bad json")

        token = payload.get("token") or self.headers.get("X-Wizard-Token") or ""
        if not hmac.compare_digest(str(token), TOKEN):
            return self._send(403, b"bad token")

        sheet = payload.get("sheet")
        # 空清单当失败处理：否则调用方分不清"用户交了空清单"和"一切正常"
        if not isinstance(sheet, str) or not sheet.strip():
            return self._send(400, b"empty sheet")

        result["sheet"] = sheet
        self._send(200, b'{"ok":true}', "application/json")
        done.set()


def main():
    ap = argparse.ArgumentParser(description="跑装机向导，把清单交回调用者")
    ap.add_argument("--out", metavar="FILE", help="同时写入这个文件")
    ap.add_argument("--no-browser", action="store_true", help="不自动开浏览器")
    ap.add_argument("--timeout", type=int, default=1800, help="等待秒数，默认 30 分钟")
    ap.add_argument("--bind", default="127.0.0.1",
                    help="监听地址，默认只监听本机。改成 0.0.0.0 才能让别的机器打开"
                         "（提交要带令牌，但页面内容会对同网段可见）")
    args = ap.parse_args()

    if not PAGE.exists():
        print("找不到 wizard.html——先跑 scripts/build-catalog.py", file=sys.stderr)
        return 2

    # 直接绑 0 号端口，让内核分配——先探再绑会有竞态
    srv = socketserver.TCPServer((args.bind, 0), Handler)
    port = srv.server_address[1]
    host = "127.0.0.1" if args.bind in ("127.0.0.1", "0.0.0.0", "") else args.bind
    url = f"http://{host}:{port}/"
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    # 提示走 stderr，stdout 留给清单本身——这样 agent 可以直接管道接
    print(f"装机向导已启动：{url}", file=sys.stderr)
    print("在浏览器里答完三轮问题，清单会自动回到这里。", file=sys.stderr)
    if args.no_browser and args.bind == "127.0.0.1":
        # 无头机器上这个地址只有本机打得开。用户坐在另一台电脑前的话，
        # 不给转发命令的话结局固定：等满超时、空手而归。
        print(f"⚠ 这个地址只有本机能访问。用户在别的电脑上的话，让他们先跑：",
              file=sys.stderr)
        print(f"    ssh -N -L {port}:127.0.0.1:{port} <这台机器>", file=sys.stderr)
        print(f"  然后在自己电脑的浏览器里打开 {url}", file=sys.stderr)
    if not args.no_browser:
        opened = False
        try:
            opened = webbrowser.open(url)
        except Exception:
            opened = False
        # headless 下 webbrowser.open 是返回 False，不是抛异常
        if not opened:
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
