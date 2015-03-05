#!/usr/bin/env python
import doctest
import fileprober
import failtype

class csvparse(object):
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
	[failtype:(<type 'int'>, <type 'int'>)]
   """


if __name__ == "__main__":
	import doctest
	doctest.testmod()
