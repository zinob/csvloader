#!/usr/bin/env python
import time
import fileprober
import failtype
import csvparse

from sqlalchemy import *


def load_to_table(fd,dbURL):
	"""
	fd: a file descriptor pointing to the desired csv-file
	dbURL: an url pointing to the desired database,for example sqlite:///:memory:
	"""
	engine = create_engine(dbURL)
	metadata = MetaData()
	
	csv=csvparse.csvparse(fd)
	typemap={time.struct_time:DateTime, int:Integer, float:Float}
	cols=[]
	for name,t in zip(csv.headers,csv.types):
		if t==str:
			newcol=Column(name, String(t.get_extras()['strsize']))
		else:
			newcol=Column(name, typemap[t.type])
		cols.append(newcol)
		

	table = Table('user', metadata, *cols)
	print dir(table) 

def _test_singlecol():
   """
   >>> from StringIO import StringIO as sIO
   >>> fd=sIO("colname"+chr(10)+chr(10).join(str(i) for i in range(100)))
	>>> load_to_table(fd,"sqlite:///tmp/gentable_testtable.sqlite")
   """
if __name__ == "__main__":
	import doctest
	doctest.testmod()
