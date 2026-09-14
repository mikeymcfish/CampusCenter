"""Optional loopback-only player server with byte ranges for MP4 chapter seeks."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import argparse,re
ROOT=Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_head(self):
        self.partial=None;p=Path(self.translate_path(self.path));header=self.headers.get('Range')
        if header and p.is_file():
            m=re.fullmatch(r'bytes=(\d*)-(\d*)',header.strip());size=p.stat().st_size
            if m:
                left,right=m.groups();start=int(left) if left else max(0,size-int(right));end=min(int(right),size-1) if left and right else size-1
                if start>=size or end<start:self.send_error(416,'Range not satisfiable');return None
                f=p.open('rb');f.seek(start);self.partial=end-start+1;self.send_response(206);self.send_header('Content-Type',self.guess_type(str(p)));self.send_header('Content-Length',str(self.partial));self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Accept-Ranges','bytes');self.end_headers();return f
        return super().send_head()
    def copyfile(self,source,outputfile):
        if self.partial is None:return super().copyfile(source,outputfile)
        remaining=self.partial
        while remaining:
            chunk=source.read(min(1024*256,remaining))
            if not chunk:break
            outputfile.write(chunk);remaining-=len(chunk)
    def end_headers(self):self.send_header('Cache-Control','no-cache');super().end_headers()
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=8769);args=ap.parse_args()
    print(f'Open http://127.0.0.1:{args.port}/information/ - Ctrl+C to stop',flush=True)
    try:ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
    except KeyboardInterrupt:pass
