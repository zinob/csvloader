#!/usr/bin/env python
import doctest
import sys
import os

def fileprober(fd,callback,skiphead=True,maxrows=10000):
	"""
	Helper function to probe rows of large files.

	fd: a file descriptor that is to be analyzed
	callback: the callback will be called for every selected row in the file
	skiphead (default True: Skip the first line (as it probbably contains column headers)
	maxrows (default 10000): the aproximate number of rows to sample fo the file.
		It read the first 1% or 4 rows, which ever is the larger of the
		specified maxrows of a file and then attempt to spread the reads
		evenly through out the file. The number is somewhat aproximate and
		might be +- "a few"
	"""

	fsize=0
	try:
		fsize=os.fstat(fd.fileno())
	except:
		pass
	#if filesize >= 0:  #Might be implemented in the future
	#	_naive_skipper(fd,callback,maxrows)
	#	return

	if (hasattr(fd,'seek') and hasattr(fd,'tell') and fsize != 0):
		_full_skipper(fd,callback,skiphead,maxrows)
	else:
		_head_reader(fd,callback,skiphead,maxrows)

def _head_reader(fd,callback,skiphead,maxrows):
	"""
	If the file is not seekable, just read the first rows...
	"""
	if skiphead==True:
		fd.readline()
	n=0
	for line in fd:
		if n>= maxrows:
			return
		n+=1
		callback(line)

def _full_skipper(fd,callback,skiphead,maxrows):
	"""
	Read the first few rows,
	then some in the middle
	then the last row
	"""
	n=0
	if skiphead==True:
		fd.readline()
		n=1
		maxrows+=1
	fsize=os.fstat(fd.fileno()).st_size

	headread=max(4,maxrows/100)
	if (maxrows==4):
		headread=3

	consumed=0
	for line in fd:
		if n>=headread:
			break
		n+=1
		#print n
		consumed+=len(line)
		callback(line)
	remaining_size=fsize-consumed
	remaining_rows=maxrows-n
	avg_rowlen=(consumed/n)
	
	jumplen=(remaining_size/avg_rowlen)/remaining_rows
	jumplen=max(jumplen,consumed/n+2) ##skip through file and read lines
	fd.seek(consumed)
	while (n<(maxrows-1) and fd.tell() < (fsize-jumplen*2)):
		n+=1
		fd.seek(n*jumplen)
		while (fd.read(1)!="\n" and fd.read(1)!=''):
			pass
		line=fd.readline()[:-1]
		if line.strip()=='':
			break
		callback(line)

	fd.seek(-4,2) #Read the last (or second-to-last line)
	seekcount=0
	while (fd.read(1)!="\n" and seekcount<100):
		fd.seek(-2,1)
		pass
	if seekcount>=100:
		return #prevent deadlock in multi-byte UTF-streams
	line=fd.readline()[:-1]
	callback(line)

def _test_head_reader():
	"""
	>>> from StringIO import StringIO as sIO
	>>> f=sIO()
	>>> _=[f.write(str(i)+chr(10)) for i in range(100)]
	>>> f.seek(0)
	>>> def foo(x):
	...   if(x.strip() in ("0","22","99")):
	...      print x.strip(),
	>>> fileprober(f,foo,skiphead=False)
	0 22 99
	"""

def _test_head_readerskip():
	"""
	>>> from StringIO import StringIO as sIO
	>>> f=sIO((chr(10)).join([str(i) for i in range(100)]))
	>>> f.seek(0)
	>>> def foo(x):
	...   if(x.strip() in ("0","22","99")):
	...      print x.strip(),
	>>> fileprober(f,foo,skiphead=True)
	22 99
	"""
def _test_head_reader():
	"""
	>>> from StringIO import StringIO as sIO
	>>> f=sIO()
	>>> _=[f.write(str(i)+chr(10)) for i in range(100)]
	>>> f.seek(0)
	>>> def foo(x):
	...   if(x.strip() in ("0","22","99")):
	...      print x.strip(),
	>>> fileprober(f,foo,skiphead=False,maxrows=40)
	0 22
	"""

def _test_seek_reader():
	"""
	>>> testfile="/tmp/seektest"
	>>> f=open(testfile,"w")
	>>> _=[f.write(""+str(i)+chr(10)) for i in range(100)]
	>>> f.write(chr(10)) #extra blank line at file end
	>>> f=open(testfile,"r")
	>>> def foo(x):
	...      print x.strip(),
	>>> fileprober(f,foo,skiphead=False,maxrows=10)
	0 1 2 3 42 51 58 65 74 99
	>>> os.remove(testfile)
	"""

def _test_with_typer():
	"""
	>>> from failtype import failtype
	>>> from StringIO import StringIO as sIO
	>>> f=sIO("colname"+chr(10)+chr(10).join(str(i) for i in range(100)))
	>>> t=failtype()
	>>> fileprober(f,t.test,skiphead=True,maxrows=40)
	>>> t.get_best_type()
	typeinfo(converter=<function nullsafe_int at ...>, type=<type 'int'>)
	>>> f.seek(0)
	>>> t=failtype()
	>>> fileprober(f,t,skiphead=False,maxrows=40)
	>>> t.get_best_type()
	typeinfo(converter=<type 'str'>, type=<type 'str'>)
	"""

if __name__ == "__main__":
	import doctest
	doctest.testmod(optionflags=doctest.ELLIPSIS)
