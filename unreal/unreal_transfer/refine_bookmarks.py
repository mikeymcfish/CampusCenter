import pathlib,json,math
r=pathlib.Path(__file__).parent;route=json.loads((r/'source/walkthrough_route.json').read_text())['keys'];rooms=[]
for i in [0,3,7,8,29,48,70,83,85]:
 k=route[i];p=k['p'];look=k.get('look') or route[min(i+1,len(route)-1)]['p'];d=[look[j]-p[j] for j in range(3)]
 if i==83:d=[5-p[0],25-p[1],1.8-p[2]]
 rooms.append({'name':k['label'],'p':[p[0]*100,-p[1]*100,p[2]*100],'dir':[d[0],-d[1],d[2]]})
(r/'exports/rooms.json').write_text(json.dumps(rooms,indent=2))
