#!/usr/bin/env python
import time
import doctest
import sys
class Failtype(object):
	"""
	Attempts to deduce the most general shared type of a series of strings.
	"""
	def __init__(self,extra_converters=[],sanitize=True):
		"""
		extra_converters: should be a list of functions to convert a string to a given object type. The last converter in the list is considdered the most specific.
		sanitize: bool, if true the data will be .strip()ed and any empty values or
		values called NULL (regardless of case) will be ignored.
		"""
		self._converters=[float,int,_gendate]+extra_converters
		self._converter_result=[]
		for i in self._converters:
			self._converter_result.append({'converter':i,'lasttype':None})
		

	def test(self,example):
		"""
		Takes a string and update the internal type registry.
		"""
		if type(example)==list:
			for i in example:
				self.test(i)
			return

		example=example.strip()
		if(example=="" or example.upper()=="NULL"):
			return
		for c in self._converter_result[:]:
			try:
				c['lasttype']=type(c['converter'](example))
			except:
				self._converter_result.remove(c)
				#print sys.exc_info()
				
	def get_best_type(self):
		"""
		Get the most specific type-candidate.

		returns: (type,converter)
		returns a tupple consisting of the most specific type and its converter-function. 
		"""
		if len(self._converter_result)==0:
			return (str,str)
		best=self._converter_result[-1]

		return (best['converter'],best['lasttype'])

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
	>>> f.test("10")
	>>> len(f._converter_result)
	2
	>>> len([i for i in f._converter_result if i['converter']==int])
	1
	"""

def __test_parse_string():
	"""
	>>> f=Failtype()
	>>> 
	>>> f.test("asdf")
	>>> len(f._converter_result)
	0
	>>> f.test("1911-03-20 11:11:00")
	>>> f.get_best_type() 
	(<type 'str'>, <type 'str'>)
	"""

def __test_parse_date():
	"""
	>>> f=Failtype()
	>>> f.test("2015-03-20 20:50:10")
	>>> len(f._converter_result)
	1
	>>> len([i for i in f._converter_result if i['lasttype']==time.struct_time])
	1
	>>> f.get_best_type()[1]
	<type 'time.struct_time'>
	>>> f.get_best_type()[0] == _gendate
	True
	"""

def __test_parse_int_list():
	"""
	>>> f=Failtype()
	>>> f.test(["4"])
	>>> len(f._converter_result)
	2
	>>> len([i for i in f._converter_result if i['converter']==int])
	1
	>>> f.test(["0","10","314151926","-1","-34","-349435"])
	>>> len([i for i in f._converter_result if i['converter']==int])
	1
	>>> f.get_best_type()
	(<type 'int'>, <type 'int'>)
	"""

def __test_parse_float_list():
	"""
	>>> f=Failtype()
	>>> f.test(["0","2","9"])
	>>> len(f._converter_result)
	2
	>>> f.test(["0.0","30.1","3.1415","-1.31","-34.68","-90435.04693"])
	>>> len(f._converter_result)
	1
	>>> len([i for i in f._converter_result if i['converter']==float])
	1
	>>> f.get_best_type() == (float, float)
	True
	"""

def __test_sanitizer():
	"""
	>>> f=Failtype()
	>>> f.test("0.1")
	>>> f.test("nuLL")
	>>> f.test("   3.1415")
	>>> f.get_best_type()
	(<type 'float'>, <type 'float'>)
	>>> f.test(" -1.31	")
	>>> f.test("-34.68")
	>>> f.test("")
	>>> f.get_best_type()
	(<type 'float'>, <type 'float'>)
	"""
if __name__ == "__main__":
	import doctest
	doctest.testmod()
