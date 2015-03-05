#!/usr/bin/env python
import doctest
import fileprober
import failtype

class csvparse(object):
	"""
	Class to parse csv-file in to a series of rows with "correctly" typed cells

	instantiate the class with a filedescriptor of a CSV file and then itterate over it.
	"""
	def __init__(self,fd,sep=',',maxrows=1000):
		"""
		fd: A file descriptor pointing to the CSV-file to be parsed,
				must be seekable.
	
		sep: (default:",") the character used to sepparate columns.
				Can not be escaped in the document.

		maxrows: (default:1000) the aproximate number of rows to
				sample from the file to deduce the column types
		"""
		self.types=[]
		assert hasattr(fd,'seek'), "provided file descriptor must be seekable"
		self.fd=fd
		self.maxrows=maxrows
		self.sep=sep

		self.headers=[]
		self.headers=[i.strip() for i in self.splitrow(fd.readline(),nocheck=True) if i.strip()!='']
		self.fd.seek(0)

		self.types=[failtype.failtype() for i in self.headers]
		self.probe(fd)

	def probe(self,fd):
		"""
		Probes the document with a series of classifiers.
		
		Headers: (default:None) a list of colum-headers to use, if none is provided the first row of the document will be used
		"""

		def lineparser(line):
			for typer,col in zip(self.types, self.splitrow(line)):
				typer(col)

		fileprober.fileprober(self.fd,
				lineparser,
				skiphead=True,
				maxrows=self.maxrows
		)


	def splitrow(self,row,nocheck=False):
		"""Naivly splits a row.
		
		row:the row to be splitted
		sep:the character to split on, this can not be quoted in
			the row "foo\\,bar" will do nothing more than create
				bar
		"""
		row=row.strip()
		newrow=row.split(self.sep)
		if (len(newrow) != len(self.headers)) and not nocheck:
			raise ValueError('The row "%s" has a different number of columns %i than the header %i'%(row,len(newrow), len(self.headers)))
		return newrow

	def __iter__(self):
		self.fd.seek(0)
		self.fd.readline()
		def rowitterator():
			for l in self.fd:
				yield [conv.converter(col) for conv,col in zip(self.types,self.splitrow(l))]

		return rowitterator()

	def __str__(self):
		return "csvparser:\n"+"\n".join(
			"  %s: %s"%(h,t.get_best_type()[0]) for h,t in zip(self.headers,self.types)
		)

def _test_rowsplit():
	"""
   >>> from StringIO import StringIO as sIO
	>>> row="foo,bar,mooh,cow"
	>>> csvparse(sIO(row)).splitrow(row)
	['foo', 'bar', 'mooh', 'cow']
	"""

def _test_singlecol():
   """
   >>> from StringIO import StringIO as sIO
   >>> f=sIO("colname"+chr(10)+chr(10).join(str(i) for i in range(100)))
   >>> t=csvparse(f)
	>>> t.types
	[failtype:typeinfo(type=<type 'int'>, converter=<type 'int'>)]
	>>> [i for i in t][::9]
	[[0], [9], [18], [27], [36], [45], [54], [63], [72], [81], [90], [99]]
   """

def _test_multicol():
   """
   >>> from StringIO import StringIO as sIO
   >>> f=sIO("isaint,isafloat"+chr(10)+chr(10).join("%i,%i.%i"%(i,i,i) for i in range(100)))
   >>> t=csvparse(f)
	>>> t.types
	[failtype:typeinfo(type=<type 'int'>, converter=<type 'int'>), failtype:typeinfo(type=<type 'float'>, converter=<type 'float'>)]
	>>> print str(t)
	csvparser:
	  isaint: <type 'int'>
	  isafloat: <type 'float'>
	>>> [i for i in t][::17]
	[[0, 0.0], [17, 17.17], [34, 34.34], [51, 51.51], [68, 68.68], [85, 85.85]]
"""

if __name__ == "__main__":
	import doctest
	doctest.testmod()
