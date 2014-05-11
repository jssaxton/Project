import re
from xml.etree.ElementTree import XMLParser
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import io
import xml.parsers.expat
import subprocess
import time
import os
import datetime
import signal
import sys
import fcntl
from xml.dom import minidom
import threading
from threading import Thread
import select
	
def compile_file(file_name, compile_name):
#	my_file = file_name
#	compile_file = file_name.split('.')[0]

	myerror = ""
	try:
		p = subprocess.Popen([r"/usr/bin/clang++", "-Wall", "-o", compile_file, file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		myerror = p.stderr.read()
		print(myerror)
		p.communicate()
	except:
		print("Couldn't compile. x1")
	if myerror.__len__() > 0:
		print("Couldn't compile. x2")

def compile_unit_test(file_name):
	my_file = file_name
	compile_file = file_name.split('.')[0]
	myerror = ""
	try:
		p = subprocess.Popen([r"/usr/bin/clang++", "-Wall", "-o", compile_file, my_file, "-lboost_unit_test_framework"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		myerror = p.stderr.read()
		print(myerror)
		p.communicate()
	except Exception as e:
		print("Couldn't compile. x1")
		print(e)
	if myerror.__len__() > 0:
		print("Couldn't compile. x2")


#Takes a list that has the input needed, then runs it based on the file_name compile_file 
def run_file(input, file_name, output_name):
	my_file = file_name
	compile_file = file_name
	myinput = input
	try:
		output=""
		start_time = time.time()
		START = 1	
		#Set maximum time limit for execution
		END = 100
	
		p = subprocess.Popen(["./" + compile_file, '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		#p.communicate()
		#setNonBlocking(p.stdout)
		#setNonBlocking(p.stdin)


		output_name = output_name + ".txt"
		f= open(output_name, "w")
		#f1 = open("mygradefile.txt")
		
		while time.time() - start_time < END:
			time.sleep(0.001)	
			if p.poll() is not None:
				break
			else:
				#enter = "9\n"
				if len(myinput) > 0:
					enter = myinput[0]+'\n'
					#print(enter)
					del myinput[0]
					p.stdin.write(enter.encode('utf-8'))
					sys.stdin.flush()
				else:
					pass
				time.sleep(0.001)
				while select.select([p.stdout,],[],[],0.0)[0]:
					output =  p.stdout.readline()
					if output.decode('utf-8') == '':
						break
					else:
						f.write(output.decode('utf-8'))
						sys.stdout.flush()							
				time.sleep(0.001)	
		if time.time() - start_time > END:
			print("Ran too long")
			mystatus = "Error: Infinite Loop"
		else:
			print("Success")


		mystatus = "NO ERROR"
	except Exception as e:
		print(e)

def run_unit_test(file_name):
	compile_file = file_name
	output_list = []
	try:
		start_time = time.time()
		START = 1	
		#Set maximum time limit for execution
		END = 100
	
		p = subprocess.Popen(["./" + compile_file, '--log_level=all'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		#p.communicate()
		#setNonBlocking(p.stdout)
		#setNonBlocking(p.stdin)


		
		#f= open(output_name, "w")
		#f1 = open("mygradefile.txt")
		
		while time.time() - start_time < END:
			if p.poll() is not None:
				while select.select([p.stdout,],[],[],0.0)[0]:
					output =  p.stdout.readline()
					if output.decode('utf-8') == '':
						break
					else:
						output_list.append(output.decode('utf-8'))
						sys.stdout.flush()	
				break
			else:
#				print("AA")
				time.sleep(0.01)	
		if time.time() - start_time > END:
			print("Ran too long")
			mystatus = "Error: Infinite Loop"
		else:
			print("Success")



		mystatus = "NO ERROR"
	except Exception as e:
		print(e)

	#print(output_list)
	return output_list


def modify_output(output_list, read_as_is, skip_until_string, read_only_string, numbers_only):
	edited_output_list = output_list
	if not read_as_is:
		if skip_until_string is not None:
			temp_list = edited_output_list
			edited_output_list = []
			start_appending = False
			for element in temp_list:
				if skip_until_string in element and not start_appending:
					start_appending = True
				if start_appending:
					edited_output_list.append(element)
					
	
		if read_only_string is not None:
			temp_list = edited_output_list
			edited_output_list = []
			for element in temp_list:
				if read_only_string in element:
					edited_output_list.append(element)
	
		if numbers_only:
			temp_list = edited_output_list
			edited_output_list = []
			numbers_list=[]
			for element in temp_list:
				my_split_string = split_my_string(element)
				#print(my_split_string)
				#for value in my_split_string:
				#	numbers_list.append(value)
				
				numbers_list = remove_text(my_split_string)
				numbers_list = ' '.join(numbers_list)
				
				#print(numbers_list)
				if numbers_list is not '':
					edited_output_list.append(numbers_list)
			#print(edited_output_list)
	return edited_output_list

def split_my_string(my_string):
	return_list = []
	try:
		return_list = re.split(';|,|:|\*|\n| |',my_string)
		return return_list
	except:
		return return_list
		
def split_my_string_plus_min_list(my_string):
	return_list = []
	try:
		return_list = re.split(';|:|\*|\n| |',my_string)
		return return_list
	except:
		return return_list


def remove_text(split_string):
	numbers_list = []

	for element in split_string:
		try:
			float(element)
			is_number = True
		except ValueError:
			is_number = False
	
		if is_number:
			numbers_list.append(element)

	return numbers_list
	
def remove_text_line(a_string):

	numbers_list = []
	split_string = split_my_string(a_string)

	for element in split_string:
		try:
			float(element)
			is_number = True
		except ValueError:
			is_number = False
	
		if is_number:
			numbers_list.append(element)
	return numbers_list

def parse_xml(grade_file):
	tree = ET.parse(grade_file)
	solution = tree.getroot()
	all_cases = []

	for each_case in solution.findall('case'):
		mydata=[]
		mydata.append(each_case.attrib)
		case_input = each_case.find('input')
		case_output = each_case.find('output')
		case_range = each_case.find('plusminus')

		if case_input is not None:		
			#print(case_input.tag, case_input.attrib)
			mydata.append(case_input.text) #1
			mydata.append(case_input.attrib) #2
		else:
			mydata.append("ERR:NO_INPUT")
			mydata.append("ERR:NO_INPUT_ATTRIB")
		if case_output is not None:
			#print(case_output.tag, case_output.attrib)
			mydata.append(case_output.text) #3
			mydata.append(case_output.attrib) #4
		else:
			mydata.append("ERR:NO_OUTPUT")
			mydata.append("ERR:NO_OUTPUT_ATTRIB")
		if case_range is not None:
			#print(case_range.tag, case_range.attrib)
			mydata.append(case_range.text) #5
			mydata.append(case_range.attrib)#6
		else:
			mydata.append("ERR:NO_PLUS") 
			mydata.append("ERR:NO_PLUS_ATTRIB")	
		#print("===")
		all_cases.append(mydata)
	return all_cases
#	for each_case in solution:
#		mydata.append(each_case.attrib)
#		all_cases.append(mydata)	
#	return all_cases

def create_expected_output(xml_attrib, xml_text):
	output_exceptions = [xml_attrib.get('skip'), xml_attrib.get('skip_until'), xml_attrib.get('read_only'), xml_attrib.get('numbers_only'), xml_attrib.get('read_as_is')]
	#print(output_exceptions)

	try:		
		skip_list = output_exceptions[0].split(',')
	except:
		skip_list = []	

	to_skip = []
	
	for element in skip_list:
		stripped_line = element.strip()
		stripped_line = stripped_line.split('-')

		if len(stripped_line) > 1:
			for i in range(int(stripped_line[0]), int(stripped_line[1])+1):
				to_skip.append(i)
		else:
			to_skip.append(int(stripped_line[0]))

	#expected_text = xml_text.strip()	
	#expected_text = xml_text.split('\n')

	to_skip.sort()
	to_skip = set(to_skip)
	to_skip = list(to_skip)

	expected_text = strip_my_string(xml_text)

	expected_output_list = ["[ignore]"]*(len(expected_text)+len(to_skip))
	#print(expected_output_list)
	#print("TO SKIP: ", to_skip)
	#print("expected_text)

	for i in range(0, len(expected_output_list)):
		if len(to_skip) > 0 and i+1 == to_skip[0]:
			del to_skip[0]
		else:
			expected_output_list[i] = expected_text[0]

			del expected_text[0]
	print("TEST:", expected_output_list)
	return expected_output_list
	#print(expected_output_list)


def strip_my_string(mystring):
	new_list = mystring.split('\n')
	output_list = []
	for line in new_list:
		newline = line.strip()
		if newline == "":
			pass
		else:
			output_list.append(newline)

	return output_list

def create_list_from_text_file(filename):
	myfile = open(filename, "r")
	mylist = []
	mystring = ""
	for each_line in myfile:
		mystring = mystring + each_line
	mylist = strip_my_string(mystring)
	return mylist
		



#output_file = open("myoutput.txt", "r")

#for each_line in output_file:
#	split_line = each_line
#	split_line = split_my_string(split_line)
#	numbers_line = remove_text(split_line)

def run_for_me(xml_file_name, compile_file_name, actual_file_name):
#xml_file_name = "mygradefile.xml"
#compile_file_name = "helloworld.cpp"

	grade_file = open(xml_file_name, "r")
	grading_data = parse_xml(grade_file)

	compile_file(actual_file_name, compile_file_name)

	case = 1
	point_total = 0
	student_total = 0

	for each_case in grading_data:

		skip_until_string = each_case[4].get('skip_until')
		read_only_string = each_case[4].get('read_lines_with')
		read_as_is = each_case[4].get('read_as_is')
		numbers_only = each_case[4].get('numbers_only')
	
		if read_as_is is None:
			read_as_is = False
		elif read_as_is.upper() == "TRUE" or read_as_is.upper() == "YES":
			read_as_is = True
		else:
			read_as_is = False
		
		if numbers_only is None:
			numbers_only = False
		elif numbers_only.upper() == "TRUE" or numbers_only.upper() == "YES":
			numbers_only = True
		else:
			numbers_only = False
	
		input_text = strip_my_string(each_case[1])
		run_file(input_text, compile_file_name, str(case))
	
		expected_output = create_expected_output(each_case[4], each_case[3])
		output_list = create_list_from_text_file(str(case) + ".txt")
		modified_output_list = modify_output(output_list, read_as_is, skip_until_string, read_only_string, numbers_only)
		
		range_same = each_case[6].get('same')
		only_for = each_case[6].get('only_for')
		skip = each_case[6].get('skip')
	
		if range_same is not None:
			if range_same.upper() == "TRUE" or range_same.upper() == "YES":
				range_same = True
			else:
				range_same = False
		else:
			range_same = False
		
	
		#print(skip)
	
		try:		
			range_list = skip.split(',')
		except:
			range_list = []	
	
		to_skip = []
	
		#print("LIST:",range_list)
		
		for element in range_list:
			stripped_line = element.strip()
			stripped_line = stripped_line.split('-')
	
			if len(stripped_line) > 1:
				for i in range(int(stripped_line[0]), int(stripped_line[1])+1):
					to_skip.append(i)
			else:
				to_skip.append(int(stripped_line[0]))
	
		to_skip = set(to_skip)
		to_skip = list(to_skip)
		to_skip.sort()	
	
	#make new function
	#only_for list
		try:		
			only_list = only_for.split(',')
		except:
			only_list = []	
	
		only_for_list = []
	
		for element in only_list:
			stripped_line = element.strip()
			stripped_line = stripped_line.split('-')
	
			if len(stripped_line) > 1:
				for i in range(int(stripped_line[0]), int(stripped_line[1])+1):
					only_for_list.append(i)
			else:
				only_for_list.append(int(stripped_line[0]))
	
		only_for_list = set(only_for_list)
		only_for_list = list(only_for_list)
		only_for_list.sort()	
	###
	
		#print(each_case[5])
		#print("SKIP:" , to_skip)
		
		
		unedited_range_values = strip_my_string(each_case[5])
		#print("RANGE:", unedited_range_values)
	
	
		#print(unedited_range_values[0])
		
		if range_same:
			range_values = list(expected_output)
			for x in range(0, len(range_values)):
				if range_values[x] != '[ignore]' and len(unedited_range_values) > 0:
					range_values[x] = unedited_range_values[0]
					del unedited_range_values[0]
				elif len(unedited_range_values) == 0:
					range_values[x] == '[ignore]'
		elif skip is not None:
			#print(to_skip)
			range_values = ["[ignore]"]*len(expected_output)
			for x in range(0, len(range_values)):
				if len(to_skip) > 0 and x+1 == to_skip[0]:
					del to_skip[0]
				elif len(unedited_range_values) > 0:
					range_values[x] = unedited_range_values[0]
					del unedited_range_values[0]
		elif only_for_list is not None:
			range_values = ["[ignore]"]*len(expected_output)
			for x in range(0, len(range_values)):
				if len(only_for_list) > 0 and len(unedited_range_values) > 0 and x+1 == only_for_list[0]:
					range_values[x] = unedited_range_values[0]
					#print("LLL", x+1, unedited_range_values[0], range_values[x])
					del unedited_range_values[0]
					del only_for_list[0]
		else:
			range_values = ["[ignore]"]*len(expected_output)
	
		print("RANGE:",range_values)	
		
		#print("EXPECTED", expected_output)
	
		grading_output = []
	
		wrong = 0
		#print(modified_output_list)
		for i in range(0, len(expected_output)):
			if i+1 > len(modified_output_list):
				grading_output.append("Line " + str(i+1) + " does not exist for the output file.")
				wrong = wrong +1			
			elif expected_output[i] == modified_output_list[i]:
				grading_output.append("Line " + str(i+1) + " matched.")
			elif expected_output[i] == "[ignore]":
				grading_output.append("Line " + str(i+1) + " was ignored.")
			elif not read_as_is:
				expected_line_no_numbers = remove_text_line(expected_output[i])
				actual_line_no_numbers = remove_text_line(modified_output_list[i])
				plus_minus = split_my_string_plus_min_list(range_values[i])
				print(plus_minus)
	#		print(plus_minus)
				if len(expected_line_no_numbers) == 0:
					grading_output.append("Line " + str(i+1) + " did not match. No numbers to check.")
					wrong = wrong + 1
				else:
					is_wrong = False;
					for n in range(0, len(expected_line_no_numbers)):
						if n >= len(actual_line_no_numbers):
							grading_output.append("Line " + str(i+1) + " did not match. It contained too few 	numbers.")						
							wrong = wrong + 1
						elif expected_line_no_numbers[n] == actual_line_no_numbers[n]:
							grading_output.append("Number " + str(n+1) + " in line " + str(i+1) + " matched. 	Literal string did not.")
						elif n < len(plus_minus):
							check_if_ignore = plus_minus[n]
							plus_min_range = plus_minus[n].split(',')
							plus_min_range  = remove_text(plus_min_range)
							my_value = float(actual_line_no_numbers[n])
							if len(plus_min_range) < 2:
								if check_if_ignore == "[ignore]":
									grading_output.append("Numbers in line " + str(i+1) + " did not 	match.")
								else:
									grading_output.append("Numbers in line " + str(i+1) + " did not match. 	Range was invalid.")
								wrong = wrong + 1
							elif my_value >= float(plus_min_range[0]) and my_value <= float(plus_min_range[1]):
								grading_output.append("Number "  + str(n+1) + " in line " + str(i+1) + " did 	not match exactly, but fell within range.")
							else:
								grading_output.append("Number " + str(n+1) + " in line " + str(i+1) + " did 	not match exactly, and did not fall within 	range.")												
								wrong = wrong + 1
						else:
							if not is_wrong:
								grading_output.append("Number " + str(n+1) + " in line " + str(i+1) + " did 	not match.")
								wrong = wrong + 1
					
			else:
				grading_output.append("Line " + str(i+1) + " did not match.")
		print(grading_output)			
		if wrong > 0:
			print("FAIL!")
		else:
			student_total = student_total + int(each_case[0].get('points'))
		try:
			point_total = point_total + int(each_case[0].get('points'))
		except:
			point_total = point_total
		case = case+1
	
	print (student_total, point_total)
	
	#print(len(grading_data))
#	output_list = create_list_from_text_file("myoutput.txt")	
#
###########UNIT TEST
#	compile_unit_test("baster.cpp")
#	time.sleep(0.1)
#	case_output = run_unit_test("baster")
#	
#	size = len(case_output) -1
#	
#	fatal_error_count = 0
#	error_count = 0
#	
#	print(case_output)
#	
#	for line in case_output:
#		if "fatal error in" in line:
#			if "failed\n" in line:
#				fatal_error_count = fatal_error_count + 1
#		elif "error in" in line:
#			if "failed\n" in line:
#				error_count = error_count + 1
#	
#	print("There were ", fatal_error_count, " fatal errors in the program.")
#	print("There were ", error_count, " non-fatal errors in the program.")
#	print("There were ", error_count + fatal_error_count, " total errors in the program.")
#	
#	#print(case_output)
#	print("AAAAAAA")
	
	for p in sys.path: print(p)
