from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import os,webbrowser,argparse
root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8769);parser.add_argument('--no-open',action='store_true');a=parser.parse_args();os.chdir(root)
class Handler(SimpleHTTPRequestHandler):
 def end_headers(self):
  self.send_header('Cache-Control','no-cache');super().end_headers()
server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler)
url=f'http://127.0.0.1:{a.port}/projection/';print(url,flush=True)
if not a.no_open:webbrowser.open(url)
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()
