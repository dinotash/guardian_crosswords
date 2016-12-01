import json
import bs4
from bs4 import BeautifulSoup
import requests
import time
import os.path
import random

#compile a list of child elements recursively
def child_tag_list(element):
	tag_list = []
	for child in element.children:
		if (isinstance(child, bs4.element.Tag)):
			tag_list.append(child)
			child_list = child_tag_list(child)
			tag_list.extend(child_list)
	return tag_list

#info about where we're looking
base_url = "http://www.guardian.co.uk/crosswords/"
default_crossword_list = [ #list of what to scrape -> format: url extension, start number, end number
	["cryptic", 21620, 27053],
	["cryptic", 16176, 16177],
	["cryptic", 12748, 12751],
	["cryptic", 12575, 12584],
	["cryptic", 2545, 2546],
	["cryptic", 783, 784],
	["cryptic", 775, 776],
	["cryptic", 743, 745],
	["cryptic", 591, 592],
	["quick", 9093, 14526],
	["quick", 135, 136],
	["prize", 21622, 27052],
	["prize", 16167, 16168],
	["prize", 12579, 12585],
	["quiptic", 1, 889],
	["speedy", 410, 1105],
	["everyman", 2965, 3660],
]

#container to store finished objects -> one json file per crossword puzzle
results_folder = "./results/"

#main extraction loop -> go through each type of crossword
for crossword_type in default_crossword_list:
	type_count = 0
	type_length = len(xrange(crossword_type[1], crossword_type[2]))
	for crossword_id in xrange(crossword_type[1], crossword_type[2]):
		#mark progress
		type_count += 1
		print(str(type_count) + "/" + str(type_length) + " - " + "Attempting " + crossword_type[0] + " crossword " + str(crossword_id))

		try:
			#check if we already have this file, and skip if so
			result_name = results_folder + crossword_type[0] + "-" + str(crossword_id) + ".json"
			if os.path.exists(result_name):
				print("    Skipping " + crossword_type[0] + " crossword " + str(crossword_id) + " because it's already been done.")
				continue

			#attempt to load the page
			crossword_url = base_url + crossword_type[0] + "/" + str(crossword_id)
			response = requests.get(crossword_url)
			crossword_page = BeautifulSoup(response.content)
			print("    Crossword loaded.")

			#check for a 404 page and skip if necessary
			page_title = crossword_page.find("title")
			if (page_title.string == "404 Page not found"):
				print("    Skipping " + crossword_type[0] + " crossword " + str(crossword_id) + " because 404 page encountered.")
				time_delay = random.uniform(5, 15)
				print("    Sleeping for " + str(time_delay) + " seconds.")
				time.sleep(time_delay)
				continue

			#check for other error message
			if ((page_title.string == "Sorry an error occurred") or (page_title.string == "Sorry we are having an issue")):
				print("    Skipping " + crossword_type[0] + " crossword " + str(crossword_id) + " because an error page encountered.")
				time_delay = random.uniform(5, 15)
				print("    Sleeping for " + str(time_delay) + " seconds.")
				time.sleep(time_delay)
				continue

			#extract the date it was published
			publication_li = crossword_page.find(attrs={"class": "publication"})
			date_string = publication_li.contents[1].strip(",").strip()
			# date_time = time.strptime(date_string, "%A %d %B %Y %H.%M %Z")

			#create an object to store data
			crossword_data = {
				'type': crossword_type[0],
				'url': crossword_url,
				'number': crossword_id,
				'id': crossword_type[0] + "-" + str(crossword_id), #unique reference, as numbers are repeated
				'published': date_string,
				'words': {}, #dict from location (e.g 6-down) to solution
				'intersections': {}, #dict with pairs of intersections -> this tells you the layout
				'joint_clues': [], #show where several words belong to the same clue
				'setter': None, #who set the crossword? By default, it's no one
			}

			#see if there is a byline
			byline_li = crossword_page.find(attrs={"class": "byline"})
			if (isinstance(byline_li, bs4.element.Tag)):
				a_string = byline_li.find("a").string
				if (a_string != None):
					crossword_data["setter"] = a_string

			#find all the script tags -> find all of them which contain the word "solutions", as that's the one with the answers
			crossword_scripts = crossword_page.find_all("script")
			for script_tag in crossword_scripts:
				for script_string in script_tag.stripped_strings:
					if ("solutions" in script_string):
						#extract the lines of text which actually have something on them
						lines = script_string.split("\n")
						for line in lines:
							line_text = line.strip()
							if (len(line_text) > 0):
								if (line_text[:3] == "var"):
									continue
								#extract the location of each letter then combine to make words
								if ("solutions" in line_text):
									#find out which word we have
									first_bracket = line_text.find("[")
									second_bracket = first_bracket + line_text[first_bracket:].find("]")
									letter_location = line_text[(first_bracket + 2):(second_bracket - 1)]
									letter_location_word = "-".join(letter_location.split("-")[0:2])

									#find the letter itself and add to the crossword
									letter = line_text[-3]
									if (letter_location_word in crossword_data['words']): #add onto existing entry
										if ('solution' in crossword_data['words'][letter_location_word]):
											crossword_data['words'][letter_location_word]['solution'] += letter
										else:
											crossword_data['words'][letter_location_word]['solution'] = letter
									else: #add a new entry
										crossword_data['words'][letter_location_word] = {}
										crossword_data['words'][letter_location_word]["solution"] = letter

								#get the intersections, as this will tell you the locations
								if ("intersections" in line_text):
									first_bracket = line_text.find("[")
									second_bracket = first_bracket + line_text[first_bracket:].find("]")
									first_location = line_text[(first_bracket + 2):(second_bracket - 1)]

									next_quotation_mark = second_bracket + 5
									second_location = line_text[next_quotation_mark:-2]

									crossword_data["intersections"][first_location] = second_location

								#maintain list of which words go with which clues
								if ("words_for_clue" in line_text):
									first_bracket = line_text.find("[")
									second_bracket = first_bracket + line_text[first_bracket:].find("]")
									first_location = line_text[(first_bracket + 2):(second_bracket - 1)]

									linked_words = line_text[second_bracket + 5:-2].split(",")
									linked_result = []
									for linked_word in linked_words:
										linked_result.append(linked_word.strip("'"))
									linked_result.sort()

									if ((len(linked_result) > 1) and (linked_result not in crossword_data["joint_clues"])):
										crossword_data["joint_clues"].append(linked_result)

			#get the clues too
			clue_div = crossword_page.find("div", id="clues")
			clue_list = clue_div.find_all("li")
			for clue in clue_list:
				#extract the text
				clue_label = clue.find("label")
				clue_word = clue_label["for"]
				clue_text = clue_label.contents[2].strip()

				clue_brackets_open = clue_text.rfind("(")
				clue_length = clue_text[clue_brackets_open + 1: -1]

				#add to the object
				crossword_data['words'][clue_word]['clue'] = clue_text[:-(len(clue_length)+3)].strip() #leave off the numbers in brackets at the end
				crossword_data['words'][clue_word]['length'] = clue_length

			#store the data overall
			# results_list.append(crossword_data)
			f = open(result_name, "w")
			json.dump(crossword_data, f)
			f.close()
			print("    Crossword saved.")

			#wait before moving on - to avoid overloading server
			time_delay = random.uniform(5, 15)
			print("    Sleeping for " + str(time_delay) + " seconds.")
			time.sleep(time_delay)
		except:
			print("    Skipping " + crossword_type[0] + " crossword " + str(crossword_id) + " because it just hasn't worked.")
			continue

# print(results_list)
print("")
print ("Finished")
