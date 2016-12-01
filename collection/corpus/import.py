import mysql.connector
import os
import json
import time

#connect to database
connection = mysql.connector.connect(user="root", password="password", host="127.0.0.1", database="guardian_crosswords")
cursor = connection.cursor()

#list of queries
add_bnc_word = ("INSERT INTO bnc_frequencies "
				"(count, word, position) "
				"VALUES (%s, %s, %s)")

add_anc_word = ("INSERT INTO anc_frequencies "
				"(word, position, count) "
				"VALUES (%s, %s, %s)")

#iterate over the
bnc_file = "/Users/tom/Programming/guardiancrosswords/collection/corpus/all.al"
bnc_data = open(bnc_file, 'r')
line_count = 0
unable = []
# for line in bnc_data:
# 	if line_count > 0:
# 		parts = line.strip().split(" ")
# 		if parts[1].isalpha(): #only do it for words that can occur in a crossword
# 			try:
# 				print line_count, parts[1]
# 				bnc_values = (parts[0], parts[1], parts[2])
# 				cursor.execute(add_bnc_word, bnc_values)
# 			except:
# 				print("UNABLE TO PROCESS: " + line)
# 				unable.append(line)
# 	line_count += 1

anc_file = "/Users/tom/Programming/guardiancrosswords/collection/corpus/ANC-all-lemma.txt"
anc_data = open(anc_file, 'r')
for line in anc_data:
	parts = line.strip().split("\t")
	if parts[0].isalpha():
		try:
			print parts[0]
			anc_values = (parts[0], parts[2], parts[3])
			cursor.execute(add_anc_word, anc_values)
		except:
			print("UNABLE TO PROCESS: " + parts[0])
			unable.append(line.strip())

#close things out
connection.commit()
cursor.close()
connection.close()

print "All done except for: "
for u in unable:
	print u
