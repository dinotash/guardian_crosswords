import mysql.connector
import os
import json
import time

#connect to database
connection = mysql.connector.connect(user="root", password="password", host="127.0.0.1", database="guardian_crosswords")
cursor = connection.cursor()

#list of queries
add_crossword = ("INSERT INTO crosswords "
				"(setter, published, type, number, id, url) "
				"VALUES (%s, %s, %s, %s, %s, %s)")

get_crossword_id = ("SELECT uid FROM crosswords "
					"WHERE id = %s")

add_word = ("INSERT INTO words "
			"(crossword, location, length, solution, clue) "
			"VALUES (%s, %s, %s, %s, %s)")

get_word_id = ("SELECT uid FROM words "
				"WHERE crossword=%s AND location=%s AND length=%s AND solution=%s AND clue=%s")

add_joint_clues = ("INSERT INTO joint_clues "
					"(crossword, list) "
					"VALUES (%s, %s)")

get_joint_clues = ("SELECT uid FROM joint_clues "
					"WHERE crossword=%s AND list=%s")

get_word_from_location = ("SELECT uid FROM words "
						  "WHERE crossword=%s AND location=%s")

add_intersection = ("INSERT INTO intersections "
					"(crossword, word1, letter1, word2, letter2) "
					"VALUES(%s, %s, %s, %s, %s)")

get_intersection = ("SELECT uid FROM intersections "
					"WHERE crossword=%s AND word1=%s AND letter1=%s AND word2=%s AND letter2=%s")

#iterate over the 
results_dir = "/Users/tom/Programming/guardiancrosswords/results/"
results_list = [f for f in os.listdir(results_dir) if ".json" in f]
for f in results_list:
	print("Loading " + f + " (" + str(results_list.index(f) + 1) + "/" + str(len(results_list)) + ")")
	result = open(results_dir + f, 'r')
	crossword = json.loads(result.read())

	#get the main details for the CROSSWORDS table
	crossword_id = crossword['id']
	setter = crossword['setter']
	
	#convert date to database format. example: "Friday 7 October 1932 00.00 GMT"
	published_string = crossword['published']
	published = time.strptime(published_string, "%A %d %B %Y %H.%M %Z")

	number = crossword['number']
	crossword_type = crossword['type']
	url = crossword['url']

	#if this crossword already exists in the database then get the uid
	crossword_uid = None
	cursor.execute(get_crossword_id, (crossword_id, ))
	for (uid, ) in cursor:
		crossword_uid = uid

	#otherwise add it
	if (crossword_uid == None):
		crossword_values = (setter, published, crossword_type, number, crossword_id, url)
		cursor.execute(add_crossword, crossword_values)
		crossword_uid = cursor.lastrowid

	#now add the words one-by-one
	for location, word in crossword['words'].items():
		#form what we're going to add
		word_values = (crossword_uid, location, word['length'], word['solution'], word['clue'])
		
		#check we don't have it already
		word_uid = None
		cursor.execute(get_word_id, word_values)
		for (uid, ) in cursor:
			word_uid = uid
		
		#only add the word if it's new
		if (word_uid == None):
			cursor.execute(add_word, word_values)

	#then add the joint-clues -- again, check whether it's actually new
	for joint_clue_list in crossword['joint_clues']:
		#make a comma-separated list of the UIDs for the words we want
		joint_clue_uids = []
		for clue in joint_clue_list:
			clue_values = (crossword_uid, clue)
			cursor.execute(get_word_from_location, clue_values)
			for (uid, ) in cursor:
				joint_clue_uids.append(str(uid))
		joint_clue_string = ",".join(joint_clue_uids)
		
		#check we don't already have this combination, and add it if not
		joint_clue_values = (crossword_uid, joint_clue_string)
		joint_clue_uid = None
		cursor.execute(get_joint_clues, joint_clue_values)
		for (uid, ) in cursor:
			joint_clue_uid = uid
		if (joint_clue_uid == None):
			cursor.execute(add_joint_clues, joint_clue_values)

	#then add the intersections
	for location1, location2 in crossword['intersections'].items():
		#split the location into word/letters
		location1parts = location1.split("-")
		word1 = "-".join(location1parts[0:2])
		letter1 = location1parts[2]
		location2parts = location2.split("-")
		word2 = "-".join(location2parts[0:2])
		letter2 = location2parts[2]

		#get the uids for the words
		cursor.execute(get_word_from_location, (crossword_uid, word1))
		for (uid, ) in cursor:
			word1_uid = uid
		cursor.execute(get_word_from_location, (crossword_uid, word2))
		for (uid, ) in cursor:
			word2_uid = uid

		#make our values for the intersection, check if we already have it and add it if not
		intersection_values = (crossword_uid, word1_uid, letter1, word2_uid, letter2)
		intersection_uid = None
		cursor.execute(get_intersection, intersection_values)
		for (uid, ) in cursor:
			intersection_uid = uid
		if (intersection_uid == None):
			cursor.execute(add_intersection, intersection_values)

#close things out
connection.commit()
cursor.close()
connection.close()