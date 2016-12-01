# -*- coding: utf-8 -*-

import mysql.connector
import json
import time

#connect to database
connection = mysql.connector.connect(user="root", password="password", host="127.0.0.1", database="guardian_crosswords")
cursor = connection.cursor()

#queries
get_word_list = "SELECT DISTINCT clue, solution FROM words"

#store results in two dicts - each a reverse look up of the other
dictionary = {} #key: solution, value: list of clues (ie. how do you define this word)
thesaurus = {} #key: clue, value: list of solutions (ie. what words mean the same thing)

#functions to add values to list
def add_value(key, value, book):
	#if it already exists, add it to the list
	if (key in book):
		book[key].append(value)
	else: #if not, add it as a new list
		book[key] = [value]

#handy aliases
def add_definition(clue, solution):
	add_value(solution, clue, dictionary)

def add_synonym(clue, solution):
	add_value(clue, solution, thesaurus)

#loop through the distinct clue:solution pairs
cursor_count = 1
cursor.execute(get_word_list)
for (clue, solution) in cursor:
	if ((cursor_count % 1000) == 1): #monitor progress
		print("Checking pair " + str(cursor_count))
	clue = clue.strip()
	solution = solution.strip()
	if (solution.isalpha()) and (len(clue) > 0) and (len(solution) > 0):
		#add this pair to the books
		add_definition(clue, solution)
		add_synonym(clue, solution)
	cursor_count += 1

#output the result to files
dictionary_file = open("dictionary.json", "w")
json.dump(dictionary, dictionary_file)
dictionary_file.close()
print("Saved dictionary")

thesaurus_file = open("thesaurus.json", "w")
json.dump(thesaurus, thesaurus_file)
thesaurus_file.close()
print("Saved thesaurus")

#close things out
connection.commit()
cursor.close()
connection.close()