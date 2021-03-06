#!/usr/bin/env python2
from datetime import datetime
import os.path
import fileprober
import failtype
import csvparse

from sqlalchemy import *


def load_to_table(fd,dbURL,sep=',', tabname=None,verbose=False, continue_on_error=False, log_file=None, full_file_probe=False, maxrows=10000):
	"""
	fd: a file descriptor pointing to the desired csv-file
	dbURL: an url pointing to the desired database,for example "sqlite:///:memory:"
	sep (default ','): The field sepparator, can not be excaped
		in any way in the document.

	tabname (default None): the name of the table to be created, if not
		provided it will be taken from the base-name of the file

	verbose (default False): print more progress info to stdout
	"""
	engine = create_engine(dbURL)
	metadata = MetaData()
	
	assert hasattr(fd,'seek'), "fd has to be seekable"
	assert tabname or hasattr(fd,'name'), "fd needs to have a .name attribute"

	assert (continue_on_error and log_file) or (not continue_on_error), "You must specify a log file if continuing on errors"

	if (tabname ==None):
		tabname=_to_tabname(fd.name)

	if verbose:
		print "Loading file:%s to table:%s"%(fd.name,tabname)
	csv=csvparse.csvparse(
		fd,
		sep=sep,
		maxrows=maxrows,
		verbose=verbose,
		continue_on_error=continue_on_error,
		log_file=log_file
	)
	typemap={datetime:DateTime, int:BigInteger, float:Float, unicode:String}
	cols=[]

	for name,t in zip(csv.headers,csv.types):
		try:
			t.type
		except LookupError as e:
			#If we have read all the file, and received no data, assume it is a short string.. augh..
			if full_file_probe:
				if verbose:
					print "typer %s has not found any data in the entire file, feeding string"%name
				t.test(u"StR  ")	
				t.test(u"xzyX-")	
			else:
				raise LookupError("typer %s threw exception"%name,e)

	for name,t in zip(csv.headers,csv.types):
		if t.type==str or t.type==unicode:
			if (t.get_extras()['strsize']> 50):
				newcol=Column(name, Text)
			else:
				#lets be paranoid..
				if full_file_probe:
					newcol=Column(name, String(t.get_extras()['strsize']+2))
				else:
					newcol=Column(name, String(t.get_extras()['strsize']*2+1))
		else:
			newcol=Column(name, typemap[t.type])
		cols.append(newcol)
	table = Table(tabname, metadata, *cols, mysql_charset='utf8')
	metadata.create_all(engine)

	if verbose:
		from pprint import pprint
		import sys
		print 'generating:', table
		pprint(cols)
	conn=engine.connect()
	trans=conn.begin()
	n=0
	for l in csv:	
		conn.execute(table.insert(), dict(zip(csv.headers,l)))

		if verbose:
			if n>10000:
				sys.stdout.write('.')
				sys.stdout.flush()
				n=0
			n+=1
	trans.commit()
	if verbose:
		sys.stdout.write('\n')
		sys.stdout.flush()
		print "Done loading table:%s"%(tabname)

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
	[(u'CREATE TABLE ... (\\n\\tcolname BIGINT\\n)',)]
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
	[(u'CREATE TABLE multicol_stringio (\\n\\tisint BIGINT, \\n\\tisfloat FLOAT, \\n\\tisstr VARCHAR(13), \\n\\tisdate DATETIME\\n)',)]
   '''

def _test_colfail():
   '''
   >>> from StringIO import StringIO as sIO
	>>> import sqlite3
	>>> db=sqlite3.connect("/tmp/gentable_testtable.sqlite")
	>>> _=db.execute('DROP table failcol;')
	>>> _=db.commit()
	>>> db.close()
	>>> heads="isint,isfloat,isdate"
	>>> lines=["%i,%i.%i,foobar,2015-01-%i 10:10:10"%(i,i,i,i+1) for i in range(29)]
	>>> for i in range(8):
	...	lines.insert(i*3,"%i,foobar,2015-01-%i 10:10:10"%(i,i+1))
	>>> fd=sIO(heads+chr(10)+chr(10).join(lines))
	>>> fd.name="failcol"
	>>> elog=sIO()
	>>> db=sqlite3.connect("/tmp/gentable_testtable.sqlite")
	>>> load_to_table(fd,"sqlite:////tmp/gentable_testtable.sqlite",verbose=False,continue_on_error=True,log_file=elog)
	>>> db.execute('select count(*) from failcol ;').fetchall()[0][0]
	8
   '''


def _test_UTF():
   '''
   >>> from StringIO import StringIO as sIO
	>>> heads="\xef\xbb\xbfisint,isstr"
	>>> lines=[str(i)+",foo"+u'\u2013 \u201d \xc3\xa5\xc3\xa4\xc3\xb6'.encode('utf-8') for i in range(29)]
   >>> fd=sIO(heads+chr(10)+chr(10).join(lines))
	>>> fd.seek(0)
	>>> fd.name="utf_string_io"
	>>> load_to_table(fd,"sqlite:////tmp/gentable_testtable.sqlite")
   '''
if __name__ == "__main__":
	import doctest
	doctest.testmod(optionflags=doctest.ELLIPSIS)
