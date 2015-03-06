#!/usr/bin/env python
import time
import os.path
import fileprober
import failtype
import csvparse

from sqlalchemy import *


def load_to_table(fd,dbURL):
	"""
	fd: a file descriptor pointing to the desired csv-file
	dbURL: an url pointing to the desired database,for example "sqlite:///:memory:"
	"""
	engine = create_engine(dbURL)
	metadata = MetaData()
	
	csv=csvparse.csvparse(fd)
	typemap={time.struct_time:DateTime, int:Integer, float:Float}
	cols=[]
	assert hasattr(fd,'seek'), "fd has to be seekable"
	assert hasattr(fd,'name'), "fd needs to have a .name attribute"
	for name,t in zip(csv.headers,csv.types):
		if t.type==str:
			newcol=Column(name, String(t.get_extras()['strsize']))
		else:
			newcol=Column(name, typemap[t.type])
		cols.append(newcol)
	table = Table(_to_tabname(fd.name), metadata, *cols)


	metadata.create_all(engine)

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
	>>> lines=["%i,%i.%i,foobar,2015-01-%i 10:10:10"%(i,i,i,i) for i in range(30)]
	>>> print lines
   >>> fd=sIO(heads+chr(10)+chr(10).join(lines))
	>>> fd.seek(0)
	>>> fd.name="multicol_stringio"
	>>> load_to_table(fd,"sqlite:////tmp/gentable_testtable.sqlite")
	>>> import sqlite3
	>>> db=sqlite3.connect("/tmp/gentable_testtable.sqlite")
	>>> db.execute('select sql from sqlite_master where name=?;',[fd.name]).fetchall()
	[(u'CREATE TABLE multicol_stringio (\\n\tisint INTEGER(2), \\n\\tisfloat FLOAT(5), \\n\\tisstr VARCHAR(6), \\n\\tisdate DATE(19)\\n)',)]
   '''
if __name__ == "__main__":
	import doctest
	doctest.testmod(optionflags=doctest.ELLIPSIS)
