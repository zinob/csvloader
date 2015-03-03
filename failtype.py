#!/usr/bin/env python
import time
import doctest
import sys
class Failtype(object):
	"""
	Attempts to deduce the most general shared type of a series of strings.
	"""
	def __init__(self,extra_converters=[]):
		"""
		extra_converters: should be a list of functions to convert a string to a given object type. The last converter in the list is considdered the most specific.
		"""
		self._converters=[float,int,_gendate]+extra_converters
		self._converter_result=[]
		for i in self._converters:
			self._converter_result.append(
					{'converter':i,'lasttype':None}
					)
		

	def test(self,example):
		"""
		Takes a string and update the internal type registry.
		"""
		if type(example)==list:
			for i in example:
				self.test(i)

		for c in self._converter_result[:]:
			try:
				c['lasttype']=type(c['converter'](example))
			except:
				self._converter_result.remove(c)
				#print sys.exc_info()
				

def _gendate(s):
	return time.strptime(s,"%Y-%m-%d %H:%M:%S")

def __test_parse_float():
	"""
	>>> f=Failtype()
	>>> f.test("4.3")
	>>> len(f._converter_result)
	1
	>>> len([i for i in f._converter_result if i['converter']==float])
	1
	"""

def __test_parse_int():
	"""
	>>> f=Failtype()
	>>> f.test("4")
	>>> len(f._converter_result)
	2
	>>> len([i for i in f._converter_result if i['converter']==int])
	1
	"""

def __test_parse_string():
	"""
	>>> f=Failtype()
	>>> f.test("asdf")
	>>> len(f._converter_result)
	0
	"""

def __test_parse_date():
	"""
	>>> f=Failtype()
	>>> f.test("2015-03-20 20:50:10")
	>>> len(f._converter_result)
	1
	>>> len([i for i in f._converter_result if i['lasttype']==time.struct_time])
	1
	"""

def __test_parse_int_list():
	"""
	>>> f=Failtype()
	>>> f.test(["4","21","-34","0"])
	>>> len(f._converter_result)
	2
	>>> len([i for i in f._converter_result if i['converter']==int])
	1
	"""

if __name__ == "__main__":
	import doctest
	doctest.testmod()
