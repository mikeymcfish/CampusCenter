"""Independent OSC fixture: Python struct / OSC padded ASCII, no app encoder."""
import struct
from pathlib import Path
def s(v):
    b=v.encode('ascii')+b'\0'
    return b+b'\0'*((-len(b))%4)
b=s('/campuscenter/player/v1')+s(',issisfffffiii')+struct.pack('>i',1)
b+=s('campuscenter-r29-p02-sample-1-250-v1')+s('ue-00000000-0000-0000-0000-000000000001')
b+=struct.pack('>i',0)+s('1791295000000')
b+=struct.pack('>fffffiii',-1200,-2895,140,125,90,0,1,1)
p=Path(__file__).resolve().parents[1]/'tests/golden_packet.hex'
p.write_text(b.hex()+'\n')
print('Independent fixture',len(b),'bytes')
