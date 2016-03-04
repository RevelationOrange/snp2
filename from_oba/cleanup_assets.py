import json
import codecs

path=r'assets.json'

f=open(path, "r")
dat=f.read()
f.close()
jsnptr=json.loads(dat)
res={}
for item in jsnptr:
	res[item['id']]=item['value']
encodedassets=json.dumps(res)
res=codecs.open(r'assets_clean.json' , "w" , "UTF-8")
res.write(encodedassets)
res.close()