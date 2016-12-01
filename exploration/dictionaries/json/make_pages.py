# -*- coding: utf-8 -*-

import json
import codecs

#will need this to start the page and end the page
def html_header(title):
	output = ""
	output += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
	output += '<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">\n'
	output += ' <head>\n'
	output += '  <title>' + title + '</title>\n'
	output += '  <link rel="stylesheet" type="text/css" href="reference.css" />\n'
	output += '  <meta http-equiv="content-type" content="text/html; charset=utf-8" />\n'
	output += '  <meta http-equiv="Content-Language" content="en-gb" />\n'
	output += ' </head>\n'
	output += ' <body>\n'
	output += '  <h1>' + title + '</h1>\n'
	output += '  <div id="mainlist">\n'
	return output

def html_footer():
	output = ""
	output += '  </div>\n'
	output += ' </body>\n'
	output += '</html>'
	return output

#load the data
dictionary_file = codecs.open("dictionary.json", "r", "utf-8")
dictionary = json.load(dictionary_file)
thesaurus_file = codecs.open("thesaurus.json", "r", "utf-8")
thesaurus = json.load(thesaurus_file)

#1) make a dictionary page -- set up the page, then loop through the words, then end up with footer
dictionary_page = codecs.open("html/dictionary.html", "w", "utf-8")
dictionary_page.write(html_header("Dictionary"))

#want the items in alphabetical order
dict_count = 0
for word in sorted(dictionary):
	if ((dict_count % 1000) == 0):
		print("Dictionary: " + str(dict_count + 1) + "/" + str(len(dictionary)))
	#main word as a paragraph, followed by an ordered list, grouped in a div
	dictionary_page.write('  <div id="div_' + str(dict_count) + '">\n')
	dictionary_page.write('    <p id="p_' + str(dict_count) + '">' + word + '</p>\n')
	dictionary_page.write('    <ol id="ol_' + str(dict_count) + '">\n')
	
	#sort the definitions in order too
	definitions = dictionary[word]
	definitions.sort()
	for definition in definitions:
		dictionary_page.write('      <li>' + definition + '</li>\n')
	dictionary_page.write('    </ol>\n')
	dictionary_page.write('  </div>\n')
	dict_count += 1
dictionary_page.write(html_footer())
dictionary_page.close()
dictionary_file.close()
print("Dictionary finished")

#2) make a dictionary page -- set up the page, then loop through the words, then end up with footer
thesaurus_page = codecs.open("html/thesaurus.html", "w", "utf-8")
thesaurus_page.write(html_header("Thesaurus"))

#want the items in alphabetical order
thes_count = 0
for definition in sorted(thesaurus):
	if ((thes_count % 1000) == 0):
		print("Thesaurus: " + str(thes_count + 1) + "/" + str(len(thesaurus)))
	#main word as a paragraph, followed by an ordered list, grouped in a div
	thesaurus_page.write('  <div id="div_' + str(thes_count) + '">\n')
	thesaurus_page.write('    <p id="p_' + str(thes_count) + '">' + definition + '</p>\n')
	thesaurus_page.write('    <ol id="ol_' + str(thes_count) + '">\n')
	
	#sort the definitions in order too
	synonyms = thesaurus[definition]
	synonyms.sort()
	for synonym in synonyms:
		thesaurus_page.write('      <li>' + synonym + '</li>\n')
	thesaurus_page.write('    </ol>\n')
	thesaurus_page.write('  </div>\n')
	thes_count += 1
thesaurus_page.write(html_footer())
thesaurus_page.close()
thesaurus_file.close()
print("Thesaurus finished")