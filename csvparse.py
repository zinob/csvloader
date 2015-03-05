#!/usr/bin/env python
import doctest

def splitrow(row,sep=","):
	"""Naivly splits a row.
	
	row:the row to be splitted
	sep:the character to split on, this can not be quoted in
	   the row "foo\\,bar" will do nothing more than create
		the splits "foo\\" and "bar"
			bar
	"""
	#silly function? yes, but one might make it smarter later..
	return row.split(sep)

def _test_rowsplit():
	"""
	>>> splitrow("foo,bar,mooh,cow")
	['foo', 'bar', 'mooh', 'cow']
	"""
if __name__ == "__main__":
	import doctest
	doctest.testmod()
