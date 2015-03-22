#!/usr/bin/env python
import doctest
import fileprober
import failtype
import sys
class csvparse(object):
	"""
	Class to parse csv-file in to a series of rows with "correctly" typed cells

	instantiate the class with a filedescriptor of a CSV file and then itterate over it.
	"""
	def __init__(self,fd,sep=',',maxrows=1000,verbose=False,continue_on_error=False,log_file=None):
		"""
		fd: A file descriptor pointing to the CSV-file to be parsed,
				must be seekable.
	
		sep: (default:",") the character used to sepparate columns.
				Can not be escaped in the document.

		maxrows (default:1000): the aproximate number of rows to
				sample from the file to deduce the column types

		verbose (default False): print extra debugging information

		continue_on_error (default False): attempt to ignore errorous lines and just keep reading.
				If you use this option it is neccesary to allso specify a logfile.
		
		log_file: a file-like object to which any error messages supressed
				via the continue_on_error should be logged.
		"""
		self.types=[]
		assert hasattr(fd,'seek'), "provided file descriptor must be seekable"
		assert (continue_on_error and log_file) or (not continue_on_error), "You must specify a log target if continuing on errors"
		self.fd=fd
		self.maxrows=maxrows
		self.sep=sep
		self.verbose=verbose
		self._continue_on_error=continue_on_error
		self._log_file=log_file

		self.utf=False
		if fd.read(3)=="\xef\xbb\xbf":
			self.utf=True

		self.fd.seek(3 if self.utf else 0)
		self.headers=[]
		self.headers=[i.strip() for i in self.splitrow(fd.readline(),nocheck=True) if i.strip()!='']
		self.fd.seek(3 if self.utf else 0)

		self.types=[failtype.failtype(utf=self.utf) for i in self.headers]
		if self.verbose:
			print "Starting file probe"
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
				maxrows=self.maxrows,
				ignore_exceptions=True,
				verbose=self.verbose
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
		self.fd.seek(3 if self.utf else 0)
		self.fd.readline()
		def rowitterator():
			failed=False
			for l in self.fd:
				try:
					yield tuple(conv.converter(col) for conv,col in zip(self.types,self.splitrow(l)))
				except ValueError as e:
					if self._continue_on_error:
						self._log_file.write(repr(e)+"\n----------\n")
					else:
						failed=sys.exc_info()[1] #hope that we are on the last line,delay raising of error
				except Exception as e:
					if self._continue_on_error:
						self._log_file.write(repr(e)+"\n----------\n")
					else:
						raise
				else:
					if failed!=False:
						raise failed
					
	

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
	[failtype:typeinfo(converter=<function nullsafe_int ...>, type=<type 'int'>)]
	>>> [i for i in t][::9]
	[(0,), (9,), (18,), (27,), (36,), (45,), (54,), (63,), (72,), (81,), (90,), (99,)]
   """

def _test_multicol():
   """
   >>> from StringIO import StringIO as sIO
   >>> f=sIO("isaint,isafloat"+chr(10)+chr(10).join("%i,%i.%i"%(i,i,i) for i in range(100)))
   >>> t=csvparse(f)
	>>> t.types
	[failtype:typeinfo(converter=<function nullsafe_int ...>, type=<type 'int'>), failtype:typeinfo(converter=<function nullsafe_float ...>, type=<type 'float'>)]
	>>> print str(t)
	csvparser:
	  isaint: <function nullsafe_int ...>
	  isafloat: <function nullsafe_float ...>
	>>> [i for i in t][::17]
	[(0, 0.0), (17, 17.17), (34, 34.34), (51, 51.51), (68, 68.68), (85, 85.85)]
"""

def _test_hardcore():
	"""
   >>> from StringIO import StringIO as sIO
	>>> heads="isint,isfloat,isstr,isdate"
	>>> lines=["%i,%i.%i,foobar,2015-01-%02i 10:10:10"%(i,i,i,i+1) for i in range(30)]
   >>> fd=sIO(heads+chr(10)+chr(10).join(lines))
   >>> t=csvparse(fd)
	>>> [i.type for i in t.types]
	[<type 'int'>, <type 'float'>, <type 'str'>, <type 'datetime.datetime'>]
	"""

def _test_trailing_lf():
   """
   >>> from StringIO import StringIO as sIO
   >>> f=sIO("colA,colB"+chr(10)+chr(10).join(str(i)+","+str(i) for i in range(10))+(chr(10)*2))
	>>> log=sIO()
   >>> t=csvparse(f,continue_on_error=True,log_file=log)
	>>> _=[i for i in t]
	>>> log.seek(0)
	>>> len(log.readlines())
	2
"""

def test_continuation():
	"""
   >>> from StringIO import StringIO as sIO
	>>> heads="isint,isfloat,isdate"
	>>> lines=["%i,%i.%i,foobar,2015-01-%i 10:10:10"%(i,i,i,i+1) for i in range(29)]
	>>> for i in range(8):
	...	lines.insert(i*3,"%i,foobar,2015-01-%i 10:10:10"%(i,i+1))
	>>> f=sIO(heads+chr(10)+chr(10).join(lines))
	>>> log=sIO()
	>>> t=csvparse(f,continue_on_error=True,log_file=log)
	>>> len([i for i in t])
	8
	>>> log.seek(0)
	>>> len([i for i in log.readlines() if "different number" in i ])
	29
	"""
def _test_col_nummer_fail():
   """
   >>> from StringIO import StringIO as sIO
   >>> f=sIO("colA,colB"+chr(10)+chr(10).join(str(i)+","+str(i) for i in range(10))+(chr(10)*2)+("1,2"+chr(10))*2)
   >>> t=csvparse(f)
	>>> _=[i for i in t]
	Exception raised:
		Traceback (most recent call last):
		...
		ValueError: ...
"""

if __name__ == "__main__":
	import doctest
	doctest.testmod(optionflags=doctest.ELLIPSIS)
