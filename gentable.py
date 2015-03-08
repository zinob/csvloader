#!/usr/bin/env python2
from datetime import datetime
import os.path
import fileprober
import failtype
import csvparse

from sqlalchemy import *


def load_to_table(fd,dbURL,sep=',', tabname=None):
	"""
	fd: a file descriptor pointing to the desired csv-file
	dbURL: an url pointing to the desired database,for example "sqlite:///:memory:"
	tabname: the name of the table to be created, if not provided it will be taken from teh file
	"""
	engine = create_engine(dbURL)
	metadata = MetaData()
	
	csv=csvparse.csvparse(fd,sep=sep)
	typemap={datetime:DateTime, int:Integer, float:Float, unicode:String}
	cols=[]
	assert hasattr(fd,'seek'), "fd has to be seekable"
	assert tabname or hasattr(fd,'name'), "fd needs to have a .name attribute"
	if (tabname ==None):
		tabname=_to_tabname(fd.name)

	for name,t in zip(csv.headers,csv.types):
		if t.type==str:
			newcol=Column(name, String(t.get_extras()['strsize']))
		else:
			newcol=Column(name, typemap[t.type])
		cols.append(newcol)
	table = Table(tabname, metadata, *cols)
	metadata.create_all(engine)

	n=0
	batch=[]
	for l in csv:
		batch.append(l)
		if n>1000:
			ins=table.insert().values(batch)
			engine.connect().execute(ins)
			batch=[]
			n=0
		n+=1
	ins=table.insert().values(batch)
	engine.connect().execute(ins)

def _to_tabname(s):
	"strip direcotry and ext-part of a file name"
	return os.path.splitext(os.path.basename(s))[0]

def _test_singlecol():
   '''
   >>> from StringIO import StringIO as sIO
   >>> fd=sIO("colname"+chr(10)+chr(10).join(str(i) for i in range(100)))
	>>> fd.name="onecol_stringio"
	>>> load_to_table(fd,"sqlite:////tmp/gentable_testtable.sqlite")
	>>> import sqlite3
	>>> db=sqlite3.connect("/tmp/gentable_testtable.sqlite")
	>>> db.execute('select sql from sqlite_master where name=?;',[fd.name]).fetchall()
	[(u'CREATE TABLE ... (\\n\\tcolname INTEGER\\n)',)]
   '''

def _test_multicol():
   '''
   >>> from StringIO import StringIO as sIO
	>>> heads="isint,isfloat,isstr,isdate"
	>>> lines=["%i,%i.%i,foobar,2015-01-%i 10:10:10"%(i,i,i,i+1) for i in range(29)]
   >>> fd=sIO(heads+chr(10)+chr(10).join(lines))
	>>> fd.seek(0)
	>>> fd.name="multicol_stringio"
	>>> load_to_table(fd,"sqlite:////tmp/gentable_testtable.sqlite")
	>>> import sqlite3
	>>> db=sqlite3.connect("/tmp/gentable_testtable.sqlite")
	>>> db.execute('select sql from sqlite_master where name=?;',[fd.name]).fetchall()
	[(u'CREATE TABLE multicol_stringio (\\n\\tisint INTEGER, \\n\\tisfloat FLOAT, \\n\\tisstr VARCHAR(6), \\n\\tisdate DATETIME\\n)',)]
   '''
if __name__ == "__main__":
	import doctest
	doctest.testmod(optionflags=doctest.ELLIPSIS)
