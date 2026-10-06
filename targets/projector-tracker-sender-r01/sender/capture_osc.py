import socket,struct,time,json,sys
from pathlib import Path
root=Path(__file__).parent
def decode(data):
    offset=0
    def string():
        nonlocal offset
        end=data.index(b'\0',offset);s=data[offset:end].decode('utf-8');offset=(end+4)&~3;return s
    address=string();types=string();args=[]
    for typ in types[1:]:
        if typ=='s':args.append(string())
        elif typ in 'if':args.append(struct.unpack_from('>'+typ,data,offset)[0]);offset+=4
        else:raise ValueError('unexpected OSC type '+typ)
    assert offset==len(data)
    return dict(address=address,types=types,args=args)
sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind(('127.0.0.1',9001));sock.settimeout(.25)
rows=[];end=time.monotonic()+float(sys.argv[2] if len(sys.argv)>2 else 100)
(root/'capture-ready.txt').write_text('127.0.0.1:9001 bound to isolated QA collector')
try:
    while time.monotonic()<end:
        try:
            data,source=sock.recvfrom(65535)
            rows.append(dict(monotonic=time.monotonic(),utc_ms=time.time_ns()//1000000,source=source,bytes=len(data),**decode(data)))
        except socket.timeout:pass
finally:
    sock.close();(root/(sys.argv[1] if len(sys.argv)>1 else 'osc-capture.json')).write_text(json.dumps(rows,indent=2))
print(len(rows),'OSC messages captured')
