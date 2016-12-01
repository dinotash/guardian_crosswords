# -*- coding: utf-8 -*-

import mysql.connector
import json
import time

#connect to database
connection = mysql.connector.connect(user="root", password="password", host="127.0.0.1", database="guardian_crosswords")
cursor = connection.cursor()

#queries
get_word_list = "SELECT words.solution, crosswords.published, crosswords.type, crosswords.setter FROM words INNER JOIN crosswords ON words.crossword = crosswords.uid"

#store various sorts of counts
bare_frequency = {}
exact_dates = {}
year_counts = {}
month_counts = {}
day_counts = {}
type_counts = {}
setter_counts = {}

#function to maintain our counts
def add_value(word, date, cw_type, setter):
	#bare frequency - just want counts as the value
	if (word in bare_frequency):
		bare_frequency[word] += 1
	else: #if not, add it as a new item
		bare_frequency[word] = 1

	#exact dates - store a list of the dates it appeared
	date_string = date.strftime("%Y-%m-%d")
	if (word in exact_dates):
		exact_dates[word].append(date_string)
	else:
		exact_dates[word] = [date_string]

	#year counts - for each word store dict of year:count
	year = date.year
	if (word in year_counts):
		if (year in year_counts[word]):
			year_counts[word][year] += 1
		else: #add new key with value 1
			year_counts[word][year] = 1
	else: #need to add dict as well as set value to nought
		year_counts[word] = {}
		year_counts[word][year] = 1

	#month counts - as above, but just by month rather than year
	month = date.month
	if (word in month_counts):
		if (month in month_counts[word]):
			month_counts[word][month] += 1
		else: #add new key with value 1
			month_counts[word][month] = 1
	else: #need to add dict as well as set value to nought
		month_counts[word] = {}
		month_counts[word][month] = 1

	#day counts - as above but by weekday
	day = date.strftime("%A")
	if (word in day_counts):
		if (day in day_counts[word]):
			day_counts[word][day] += 1
		else: #add new key with value 1
			day_counts[word][day] = 1
	else: #need to add dict as well as set value to nought
		day_counts[word] = {}
		day_counts[word][day] = 1

	#type counts - how many per type of crossword?
	if (word in type_counts):
		if (cw_type in type_counts[word]):
			type_counts[word][cw_type] += 1
		else: #add new key with value 1
			type_counts[word][cw_type] = 1
	else: #need to add dict as well as set value to nought
		type_counts[word] = {}
		type_counts[word][cw_type] = 1

	#setter types - how many times word used by each setter
	setter_name = "Unknown" #use unless we can find a real resullt
	if (setter is not None):
		if (len(setter) > 0):
			setter_name = setter
	if (word in setter_counts):
		if (setter_name in setter_counts[word]):
			setter_counts[word][setter_name] += 1
		else: #add new key with value 1
			setter_counts[word][setter_name] = 1
	else: #need to add dict as well as set value to nought
		setter_counts[word] = {}
		setter_counts[word][setter_name] = 1

#loop through the distinct clue:solution pairs
cursor_count = 0
cursor.execute(get_word_list)
for (solution, date, cw_type, setter) in cursor:
	if ((cursor_count % 1000) == 0): #monitor progress
		print("Checking word " + str(cursor_count + 1))
	solution = solution.strip()
	if (len(solution) > 0):
		#add to lists
		add_value(solution, date, cw_type, setter)
	cursor_count += 1

#output the result to files
bare_frequency_file = open("./frequencies/bare_frequency.json", "w")
json.dump(bare_frequency, bare_frequency_file)
bare_frequency_file.close()
print("Saved frequency list 1")

exact_dates_file = open("./frequencies/exact_dates.json", "w")
json.dump(exact_dates, exact_dates_file)
exact_dates_file.close()
print("Saved frequency list 2")

year_counts_file = open("./frequencies/year_counts.json", "w")
json.dump(year_counts, year_counts_file)
year_counts_file.close()
print("Saved frequency list 3")

month_counts_file = open("./frequencies/month_counts.json", "w")
json.dump(month_counts, month_counts_file)
month_counts_file.close()
print("Saved frequency list 4")

day_counts_file = open("./frequencies/day_counts.json", "w")
json.dump(day_counts, day_counts_file)
day_counts_file.close()
print("Saved frequency list 5")

type_counts_file = open("./frequencies/type_counts.json", "w")
json.dump(type_counts, type_counts_file)
type_counts_file.close()
print("Saved frequency list 6")

setter_counts_file = open("./frequencies/setter_counts.json", "w")
json.dump(setter_counts, setter_counts_file)
setter_counts_file.close()
print("Saved frequency list 7")

#close things out
connection.commit()
cursor.close()
connection.close()