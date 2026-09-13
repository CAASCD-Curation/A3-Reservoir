from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import webbrowser

root = Path(__file__).resolve().parent.parent / 'dist'
if not (root / 'index.html').exists():
    raise SystemExit('缺少 dist 构建结果，请先运行 pnpm build。')
handler = partial(SimpleHTTPRequestHandler, directory=str(root))
try:
    server = ThreadingHTTPServer(('127.0.0.1', 8088), handler)
except OSError:
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
url = f'http://127.0.0.1:{server.server_port}'
print(f'RESERVOIR OPERATING SYSTEM\n{url}\n保持此窗口开启。按 Control-C 停止服务。', flush=True)
webbrowser.open(url)
try:
    server.serve_forever()
except KeyboardInterrupt:
    server.server_close()
