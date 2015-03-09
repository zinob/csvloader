#!/usr/bin/env python
from datetime import datetime
import doctest
import sys
import collections 

class failtype(object):
	"""
	Attempts to deduce the most general shared type of a series of strings.
	"""
	typeinfo=collections.namedtuple("typeinfo",["converter","type"])
	def __init__(self,extra_converters=[],sanitize=True, utf=False):
		"""
		extra_converters: should be a list of functions to convert a string to a given object type. The last converter in the list is considdered the most specific.
		sanitize (default True): if true the data will be .strip()ed and any empty values or
				values called NULL (regardless of case) will be ignored.
		utf (default False): Will return a lambda .decode('utf-8') instead of the naive string converter. Yeah that is all... and yes, that is ugly
		"""
		self._converters=[float,int,_gendate,_gendate2]+extra_converters
		self._converter_result=[]
		self._test_performed=False
		self._extras={}
		self._sanitize=sanitize
		self.utf=utf
		for i in self._converters:
			self._converter_result.append({'converter':i,'lasttype':None})
		

	def __call__(self,example):
		"""
		Equivalent to calling the .test(example) method on an object
		"""
		self.test(example)

	def test(self,example):
		"""
		Takes a string and update the internal type registry.
		"""
		if type(example)==list:
			for i in example:
				self.test(i)
			return

		example=example.strip()
		if(self._sanitize and (example=="" or example.upper()=="NULL")):
			return
		for c in self._converter_result[:]:
			try:
				c['lasttype']=type(c['converter'](example))
			except:
				self._converter_result.remove(c)
				#print sys.exc_info()
		if len(self._converter_result)==0:
			newlen=len(example)
			if newlen>self._extras.get("strsize",-1):
				self._extras["strsize"]=len(example)

		self._test_performed=True
				
	def get_extras(self):
		return self._extras
	def get_best_type(self):
		"""
		Get the most specific type-candidate.

		returns: a named tupple consistiong of (type=type,converter=converter)
		returns a tupple consisting of the most specific type and its converter-function. 
		"""
		if not self._test_performed:
			raise LookupError("typer hasnt been fed with data")
		if len(self._converter_result)==0:
			if not self.utf:
				return self.typeinfo(str,str)
			else:
				return self.typeinfo((lambda s: s.decode('utf-8')),unicode)
		best=self._converter_result[-1]

		def nulldecorator(fun):
			def nulldecorated(s):
				if s.lower()=='null' or s=='':
					return None
				else:
					return fun(s)
			return nulldecorated

		if self._sanitize:
			conv=nulldecorator(best['converter'])
			conv.__name__="nullsafe_"+best['converter'].__name__
		else:
			conv=best['converter']

		return self.typeinfo(conv,best['lasttype'])

	@property
	def converter(self):
		return self.get_best_type().converter

	@property
	def type(self):
		return self.get_best_type().type

	def __str__(self):
		return str(self.get_best_type())
	def __repr__(self):
		return "failtype:"+self.__str__()

def _gendate(s):
	return datetime.strptime(s,"%Y-%m-%d %H:%M:%S")

def _gendate2(s):
	return datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f")
	#return time.strptime(s,"%Y-%m-%d %H:%M:%S")

def __test_parse_float():
	"""
	>>> f=failtype()
	>>> f.test("4.3")
	>>> len(f._converter_result)
	1
	>>> len([i for i in f._converter_result if i['converter']==float])
	1
	"""

def __test_call():
	"""
	>>> f=failtype()
	>>> f("4.3")
	>>> len([i for i in f._converter_result if i['converter']==float])
	1
	"""

def __test_parse_int():
	"""
	>>> f=failtype()
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
	>>> f.converter
	<function nullsafe_int at ...>
	"""

def __test_parse_string():
	"""
	>>> f=failtype()
	>>> 
	>>> f.test("asdf")
	>>> len(f._converter_result)
	0
	>>> f.test("1911-03-20 11:11:00")
	>>> f.get_best_type() 
	typeinfo(converter=<type 'str'>, type=<type 'str'>)
	>>> f.get_extras()['strsize'] 
	19
	"""

def __test_parse_date():
	"""
	>>> f=failtype()
	>>> f.test("2015-03-20 20:50:10")
	>>> len(f._converter_result)
	1
	>>> len([i for i in f._converter_result if i['lasttype']==datetime])
	1
	>>> f.get_best_type().type
	<type 'datetime.datetime'>
	>>> f.get_best_type().converter
	<function nullsafe__gendate at ...>
	"""

def __test_parse_int_list():
	"""
	>>> f=failtype()
	>>> f.test(["4"])
	>>> len(f._converter_result)
	2
	>>> len([i for i in f._converter_result if i['converter']==int])
	1
	>>> f.test(["0","10","314151926","-1","-34","-349435"])
	>>> len([i for i in f._converter_result if i['converter']==int])
	1
	>>> f.get_best_type()
	typeinfo(converter=<function nullsafe_int at ...>, type=<type 'int'>)
	"""

def __test_parse_float_list():
	"""
	>>> f=failtype(sanitize=False)
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
	>>> f=failtype()
	>>> f.test("0.1")
	>>> f.test("nuLL")
	>>> f.test("   3.1415")
	>>> f.get_best_type()
	typeinfo(converter=<function nullsafe_float at ...>, type=<type 'float'>)
	>>> f.test(" -1.31	")
	>>> f.test("-34.68")
	>>> f.test("")
	>>> f.get_best_type()
	typeinfo(converter=<function nullsafe_float at ...>, type=<type 'float'>)
	"""

if __name__ == "__main__":
	import doctest
	doctest.testmod(optionflags=doctest.ELLIPSIS)
