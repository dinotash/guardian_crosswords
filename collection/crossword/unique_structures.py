import mysql.connector
import os
import json
import time

#connect to database
connection = mysql.connector.connect(user="root", password="password", host="127.0.0.1", database="guardian_crosswords")
cursor = connection.cursor()

#queries
get_structure = "SELECT uid FROM structures WHERE list=%s"

add_structure = "INSERT INTO structures (list) VALUES(%s)"

get_crossword = "SELECT uid FROM crosswords WHERE id=%s"

update_crossword = "UPDATE crosswords SET structure=%s WHERE uid=%s"

#iterate over the 
results_dir = "/Users/tom/Programming/guardiancrosswords/results/"
results_list = [f for f in os.listdir(results_dir) if ".json" in f]
for f in results_list:
	print("Loading " + f + " (" + str(results_list.index(f) + 1) + "/" + str(len(results_list)) + ")")
	result = open(results_dir + f, 'r')
	crossword = json.loads(result.read())

	#get the main details for the CROSSWORDS table
	crossword_id = crossword['id']
	
	#combine structures into standardised form
	intersections = crossword['intersections']
	structure = []
	for word1, word2 in intersections.items():
		pair = [word1, word2]
		pair.sort()
		if (pair not in structure):
			structure.append(pair)
	structure.sort()
	structure_string = str(structure)

	#check if we already have this structure - add it if not
	structure_uid = None
	cursor.execute(get_structure, (structure_string, ))
	for (uid, ) in cursor:
		structure_uid = uid
	if (structure_uid == None):
		cursor.execute(add_structure, (structure_string, ))
		structure_uid = cursor.lastrowid

	#update the crossword table
	crossword_uid = None
	cursor.execute(get_crossword, (crossword_id, ))
	for (uid, ) in cursor:
		crossword_uid = uid
	if (crossword_uid != None):
		update_values = (structure_uid, crossword_uid)
		cursor.execute(update_crossword, update_values)

#close things out
connection.commit()
cursor.close()
connection.close()