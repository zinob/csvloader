# csvloader
Built to parse a specific set of CSV-files corresponding to a specific database.
The format of these files is a bit impractical why this script attempts to do some rudimentary type-inference
and data-massaging. For general purpose you are probably better of using the
[Pandas CSV-reader](http://pandas.pydata.org/pandas-docs/dev/io.html#io-store-in-csv).
But if you need to tweak your own, this reader might be an option.

Usage example
-------

This would read the complete file to guess the column-types  and would just skip lines which contains more or fewer columns than the header.
It would load the ; -sepparated file "foo" to the table "bar_table", several csv-files and --map commands can be supplied.

   filetodb.py -v --database "mysql://user:pass@localhost/test?use_unicode=1charset=utf8" --sep ";" --ignore-invalid --full-file --map "foo.csv:bar_table" foo.csv
   
   If -- is ommitted it will just attempt to read a few thousand lines from the file in order to speed the analysis up. This might lead to poor estimates on line-lenght and some times even wrong types. This option should probbably be inverted and called --sparase-read or something...
