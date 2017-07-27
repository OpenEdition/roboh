USAGE:
=====
For any script you can get more details options with:
$python3 <script.py> -h



*******************
set_tag.py 
*******************

Resume:
------
This script is dedicated to import full text from solr or from a directory.
In solr case, you get two output.
	Output 1: Full text.
	Output 2: Text enhanced by :
			- a named entity recognition
			- an analysis sentiment sentence by sentence.
In text case only the output 2 is given.

settings :
---------
You need to specify datasource (-d text or solr).
text case specifiy: 	-corpus directory (-c).
			-output directory (-o)

solr case specify: 	-corpus directory (-c).
			-output directory (-o)
			-platform and site name (-p and -s)).
			-solr url in the settings.py

runnning :
---------
	For running this script you need ABSOLUTELY to launch in the echo virtual env:
		-(echovirtualenv) morban@morban:path_to/roboh/echosocket:python analysisrunner.py 
	Then you can run (not in echo virtualenv of course):
		$python3 set_tag.py -option.....

Files generated:
--------------
	In the output directory, you get all the files (each file keep his filename).Each file is divided by:
		- One line is the naked text
		- second line is the text with xml tag corresponding to the name entitities
		- third line is a list of polarity (negative, neutre, positive) associated at each sentence of the thext.

Exemple:
-------
To annotate all the text in a /tmp/test/CR/ directory and keep enhancement annotatetd in /tmp/tag, do:  
$python3 set_tag.py -d text -c /tmp/test/CR/ -o /tmp/tag/

To annotate all the text from zilsel in hypotheses. To keep naked_text in /tmp/solrtext/CR/ directory and keep enhancement annotated in /tmp/tagsolr, do:
./set_tag.py -d solr -p HO -s zilsel -c /tmp/solrtext/CR/ -o /tmp/tagsolr

Note:
----
Only french is supported for query solr (It should be modified soon).
Note that for annotated Named Entities, only french, english and german are supported.

*******************
Full pipeline
*******************
Resume:
-----
A full pipeline could be:

