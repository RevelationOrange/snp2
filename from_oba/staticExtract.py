import json
import os
import codecs


outputdir=r'data_from_sdump'
dumplocation=r'staticDump.txt'


f=codecs.open(dumplocation , "r" , "UTF-8")
dat=f.read()
f.close()
dump=json.loads(dat)

toextract=["workers" , "character_classes" , "resources" , "customers" , "assets" , "items" , "recipes"]

for key in toextract:
	jsonptr=dump["result"][key]
	dat=json.dumps(jsonptr, sort_keys=True,indent=4, separators=(',', ': '))
	res=codecs.open(os.path.join(outputdir , ("%s.json" % key)) , "w" , "UTF-8")
	res.write(dat)
	res.close()


