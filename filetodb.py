#!/usr/bin/python

import gentable
import argparse

parser=argparse.ArgumentParser(description='load one or more files to a database-')

parser.add_argument('CSVfiles', metavar='filenames', type=str, nargs='+', help='list of CSV-files to parse')

parser.add_argument('--database', type=str, required=True,  help='The database to uppload the table to, for example sqlite:///mydb.sqlite')

parser.add_argument('--separator',  nargs='?', default=',',  help='Field separator')

parser.add_argument('--map', action='append', help='Load a file to antother table name than its file-name')

args= parser.parse_args()

tablemap={}
if args.map!=None:
	tablemap=dict(i.strip().split(":",1) for i in args.map)

dbURL=args.database
sep=args.separator
for fname in args.CSVfiles:
	tab=tablemap.get(fname,None)
	gentable.load_to_table(open(fname,'r'),dbURL, sep=sep, tabname=tab, verbose=True)

