#!/usr/bin/env python
import time
import doctest
import sys
import os

def fileprober(fd,callback,maxrows=10000):
	"""
	Helper function to probe rows of large files.

	It read the first 1% or 4, which ever is the larger of the
		specified maxrows of a file and then attempt to spread
		the reads evenly through out the file. The number is
		somewhat aproximate and might be +- "a few"
	fd: a file descriptor that is to be analyzed
	callback: the callback will be called for every selected row in the file
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
		_full_skipper(fd,callback,maxrows)
	else:
		_head_reader(fd,callback,maxrows)

def _head_reader(fd,callback,maxrows):
	"""
	If the file is not seekable, just read the first few rows...
	"""
	n=0
	for line in fd:
		if n>= maxrows:
			return
		n+=1
		callback(line)

def _full_skipper(fd,callback,maxrows):
	"""
	Read the first few rows,
	then some in the middle
	then the last row
	"""
	n=0
	fsize=os.fstat(fd.fileno()).st_size

	headread=max(4,maxrows/100)
	if (maxrows==4):
		headread=3

	consumed=0
	for line in fd:
		if n>=headread:
			break
		n+=1
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
		callback(line)

	fd.seek(-3,2) #Read the last (or second-to-last line)
	while (fd.read(1)!="\n"):
		fd.seek(-2,1)
		pass
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
	>>> fileprober(f,foo)
	0 22 99
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
	>>> fileprober(f,foo,maxrows=40)
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
	>>> fileprober(f,foo,maxrows=10)
	0 1 2 3 42 51 58 65 74 99
	>>> os.remove(testfile)
	"""

if __name__ == "__main__":
	import doctest
	doctest.testmod()
