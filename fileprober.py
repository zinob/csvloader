#!/usr/bin/env python
import time
import doctest
import sys
import os

def fileprober(fd,callback,maxrows=10000):
	"""
	Helper function to probe rows of large files.

	It read the first 1% of the specified max-rows of a file and
		then attempt to spread the reads evenly through out the file
		the spreading will use heuristics depending on weather or
		not the fd supports stat and seek.

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

	if (hasattr(fd,'seek') and fsize != 0):
		_full_skipper(fd,callback,maxrows)
	else:
		_head_reader(fd,callback,maxrows)

def _head_reader(fd,callback,maxrows):
	n=0
	for line in fd:
		if n>= maxrows:
			return
		n+=1
		callback(line)

def _full_skipper(fd,callback,maxrows):
	assert 0,"NOT IMPLEMENTED"
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
	...   if(x.strip() in ("0","22")):
	...      print x.strip(),
	>>> fileprober(f,foo,maxrows=40)
	0 22
	"""
if __name__ == "__main__":
	import doctest
	doctest.testmod()
