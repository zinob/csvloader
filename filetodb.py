#!/usr/bin/python2

import gentable
import argparse

def main():
	parser=argparse.ArgumentParser(description='load one or more files to a database-')

	parser.add_argument('CSVfiles', metavar='filenames', type=str, nargs='+', help='list of CSV-files to parse')

	parser.add_argument('--database', type=str, required=True,  help='The database to uppload the table to, for example sqlite:///mydb.sqlite')

	parser.add_argument('--separator',  nargs='?', default=',',  help='Field separator')

	parser.add_argument('--map', action='append', help='Load a file to antother table name than its file-name')

	parser.add_argument('-v','--verbose', dest='verbose',action='store_true', help='Produce more information about the tables being generated')

	parser.add_argument('--ignore-invalid', dest='continue_on_error',action='store_true', help='Continue parsing despite errors on individual lines, write the exception info to TABLENAME_errors.log')

	parser.add_argument('--full-file', dest='read_full_file',action='store_true', help='Do not use sparse column type-probing  run typer on every single row in the entire file')

	args= parser.parse_args()

	tablemap={}
	if args.map!=None:
		for m in args.map:
			key,value=m.strip().split(":",1)
			tablemap[gentable._to_tabname(key)]=value
			tablemap[key]=value
			try:
				tablemap[key.rsplit("/",1)[1]]=value
			except:
				pass

	dbURL=args.database
	sep=args.separator
	verbose=args.verbose
	continue_on_error=args.continue_on_error

	full_file_probe=args.read_full_file
	if full_file_probe:
		maxrows=False
	else:
		maxrows=10000

	for fname in args.CSVfiles:
		tab=getfuzzy(tablemap,fname)

		log_file=None
		if continue_on_error:
			import datetime
			log_file=open(tab+"_errors.log","a")
			log_file.write(datetime.datetime.now().strftime("----- %Y-%m-%d %H:%M:%S -----\n"))

		gentable.load_to_table(
			open(fname,'r'),
			dbURL,
			sep=sep,
			tabname=tab,
			verbose=verbose,
			continue_on_error=continue_on_error,
			log_file=log_file,
			full_file_probe=full_file_probe,
			maxrows=maxrows
		)
def getfuzzy(map,key):
	keys=[key, gentable._to_tabname(key),key.rsplit("/",1)[-1]]
	for i in keys:
		val=map.get(i,None)
		if val!=None:
			return val
	return None

main()
