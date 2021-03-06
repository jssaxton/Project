##############################
# Imported Items #############
##############################
from __future__ import print_function
from time import strptime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.context_processors import csrf
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms import EmailField
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from gradeapp.models import user_info, MyClass, UserForm, ClassRoster, AuthUser, Assignment, MyInbox, MyOutbox, AssignmentFile, CodeFile #AssignmentFileList, 
#, CodeFileList, CodeFileStorage
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.shortcuts import render_to_response
from gradeapp.forms import UploadFileForm
from django.views.static import serve
from code_grader import *
import sys, os
import datetime
import time
import re

##############################
# Python Code ################
##############################
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
#import fcntl
from xml.dom import minidom
import threading
from threading import Thread
import select

################################
# Begin Code ###################
################################
#Rule to Upload Files
def upload_file(request, number):
	#Check if user is authenticated
	if request.user.is_authenticated():
		try:
				myassignment = Assignment.objects.get(id=number)
		except:
				return HttpResponse("This page does not exist. e1")
	else:
		return redirect('register')

	if datetime.date.today() > myassignment.due_date:
		print(datetime.date.today())
		request.session["grade_result"] = "The assignment due date has passed."
		return HttpResponseRedirect("/gradeapp/classes/"+myassignment.to_class.class_number+"/"+number+"/")
	#Check request method
	if request.method == 'POST':	
		check_extension(request.FILES['datafile'].name)
		retry = AssignmentFile.objects.filter(to_assignment=myassignment).count()
		if retry > myassignment.retry_limit + 9999:
			return HttpResponse("You already uploaded a file for this assignment and have exceeded the retry limit")
		else:
			MyFile = AssignmentFile(upload_number = retry+1, to_assignment = myassignment, my_file = request.FILES['datafile'], date_uploaded =  datetime.date.today())
			MyFile.save()
			myassignment.already_uploaded=True
			myassignment.save()
			
			if request.user.groups.filter(name = 'Student'):
				teacher_file = return_teacher_file(MyFile.my_file.name)
				if len(teacher_file) < 1:
					grade_results = "The assignment was uploaded. No automatic grading was specified for this submission."
				elif ".cpp" in teacher_file[0].my_file.name:
					grade_results = test_u_stuff(request.user.username, MyFile.my_file.name)
				else:
					grade_results = test_stuff(request.user.username, MyFile.my_file.name)
				request.session["grade_result"] = grade_results
			return HttpResponseRedirect("/gradeapp/classes/"+myassignment.to_class.class_number+"/"+number+"/")
	else:
		return redirect('index')

#Return to the Index page
def index_page(request):
	if request.user.is_authenticated():
		return redirect('index')
	else:
		return redirect('register')


#Create Assignment 
def create_assignment(request):
	#Checks user rights
	if not request.user.groups.filter(name='Admin') and not request.user.groups.filter(name = 'Teacher'):
		return HttpResponse("You do not have permission to access this page.")
	#Checks authentication
	elif request.user.is_authenticated():
		if request.method == 'POST':
			myclass_teacher = request.user.username
			myclass = MyClass.objects.get(id=request.POST['pass_class'])
			max_score = request.POST['max_score']
			run_time = request.POST['run_time']
			real_score = 0
			
			
			try:
				if request.FILES['datafile']:
					file_exists = True
			except:
					file_exists = False
			
			try:
				retry = request.POST['retry_limit']
			except:
				retry = 0
				

#			MyFile = AssignmentFile(upload_number = retry+1, to_assignment = myassignment, my_file = request.FILES['datafile'], date_uploaded =  datetime.date.today())
			
			try:
				due_date = datetime.datetime.strptime(request.POST['due_date'], "%B %d, %Y")			
			except:
				try:
					due_date = datetime.datetime.strptime(request.POST['due_date'], "%m-%d-%Y")			
				except:
					try: 
						due_date = datetime.datetime.strptime(request.POST['due_date'], "%m/%d/%Y")			
					except:
						try:
							due_date = datetime.datetime.strptime(request.POST['due_date'], "%b %d, %Y")			
						except:
							return HttpResponse("Please enter the date in MM-DD-YYYY format.")

			create_date = datetime.date.today()
			
			#Checks if Assignment already exists
			if Assignment.objects.filter(assignment_name = request.POST['asg_name']).filter(to_class = myclass):
				return HttpResponse("Already exists.")
				
			#Tries to create assignment
			
				
			try:
				newAssignment = Assignment( is_owner = True, due_date = due_date, assign_date = create_date, assignment_name = request.POST['asg_name'], to_student = user_info.objects.get(username=request.user.username), to_class = myclass, max_score = max_score, real_score = real_score, to_teacher = user_info.objects.get(username=request.user.username), run_time = run_time)
				newAssignment.retry_limit = retry
				newAssignment.save()				
			except:
				message = "Error creating assignment!" 
				return render (request, "create_assignment.html", {"info": user_info.objects.all(), "roster": ClassRoster.objects.all(), "message": message})

			try:
				if file_exists:
					MyFile = AssignmentFile(upload_number = 0, to_assignment = newAssignment, my_file = request.FILES['datafile'], date_uploaded =  datetime.date.today())
					MyFile.save()
			except:
				return HttpResponse("FAIL")
				
			#Adds assignment for each member of the class roster
			for each_roster in ClassRoster.objects.all():
				if each_roster.in_class == myclass:
					for each_student in each_roster.student.all():
						if not each_student.username == request.user.username and each_student.user_type == "ST":
							newAssignment = Assignment( due_date = due_date, assign_date = create_date,assignment_name = request.POST['asg_name'], to_student = each_student, to_class = myclass, max_score = max_score, real_score = real_score, to_teacher = user_info.objects.get(username=request.user.username), run_time = run_time)
							newAssignment.retry_limit = retry
							newAssignment.save()							
			message = "Assignment added!" 
			return render (request, "create_assignment.html", {"info": user_info.objects.all(), "roster": ClassRoster.objects.all(), "message": message})
		else:
			return render (request, "create_assignment.html", {"info": user_info.objects.all(), "roster": ClassRoster.objects.all()})
	else:
		return redirect('register')
		
#Creates a new class
def create_a_class(request):
	#Checks user group rights
	if not request.user.groups.filter(name='Admin') and not request.user.groups.filter(name = 'Teacher'):
		return HttpResponse("You do not have permission to access this page.")
	#Checks authentication
	elif request.user.is_authenticated():
		#If authenticated, checks method type
		if request.method == 'POST':
			myclass_name = request.POST['class_name']
			myclass_number = request.POST['class_number']
			myclass_sem_year = request.POST['year_range']
			myclass_sem_season = request.POST['class_semester']
			myclass_semester = parse_semester(myclass_sem_season, myclass_sem_year)
			creating_teacher = request.user.username

			if MyClass.objects.filter(class_number = myclass_number):
				message = "This class already exists."
				return render(request, "create_a_class.html", {"message": message})

			new_class = MyClass(class_name = myclass_name, class_number = myclass_number, semester = myclass_semester, teacher = creating_teacher, authenticate = True)
			new_class.save()				

			#Tries to create new roster
			try:
				newroster = ClassRoster(in_class = new_class, class_name = new_class.class_name, class_number = new_class.class_number, teacher=request.user.username) 
				newroster.save()
				newroster.student.add(user_info.objects.get(username = request.user.username))
			except Exception as e:
				return HttpResponse(e)

			#Updates teacher profile to add new class
			teacher_update = user_info.objects.get(username=request.user.username)
			teacher_update.class_list.add(new_class)
			teacher_update.save()

			return render (request, "create_a_class.html")			
		else:
			return render (request, "create_a_class.html")
	else:
		return redirect('register')

#Function to manage classes

def delete_assignment(course, teacher, asg_name):
	asg_list = Assignment.objects.filter(to_class = course).filter(to_teacher = teacher).filter(assignment_name = asg_name)
	for each_asg in asg_list:
		each_asg.delete()

def edit_classes(request, string):
	#Check to see is class exists
	if not request.user.groups.filter(name='Admin') and not request.user.groups.filter(name = 'Teacher'):
		return HttpResponse("You do not have permission to access this page.")
	#Checks authentication
	elif request.user.is_authenticated():
		#If authenticated, checks method type
		if request.method == 'POST' and not 'del_me' in request.POST:
			myclass_name = request.POST['class_name']
			myclass_number = request.POST['class_number']
			myclass_sem_year = request.POST['year_range']
			myclass_sem_season = request.POST['class_semester']
			myclass_semester = parse_semester(myclass_sem_season, myclass_sem_year)
			split_semester =  split_semester_string(myclass_semester)


			try:
				edit_class = MyClass.objects.get(class_number = string)
				edit_roster = ClassRoster.objects.get(in_class = edit_class)
			except Exception as e:
				return HttpResponse(e)
			

			if MyClass.objects.filter(class_number = myclass_number) and string != myclass_number:
				
				return render (request, "edit_class.html", {"message": "That class already exists.", "myclass": MyClass.objects.get(class_number = string), "season": split_semester[0], "year": split_semester[1]})

			edit_class.semester = myclass_semester
			edit_class.class_name = myclass_name
			edit_class.class_number = myclass_number
				
			edit_roster.class_name = myclass_name
			edit_roster.class_number = myclass_number

			edit_class.save()
			edit_roster.save()

			return HttpResponseRedirect("/gradeapp/manage_classes/"+myclass_number+"/")

#			return HttpRedirect(request, "edit_class.html", {"myclass": edit_class, "season": split_semester[0], "year": split_semester[1]})

		elif 'del_me' in request.POST:
			try:
				del_class = MyClass.objects.get(class_number = string)
				del_class.authenticate = False
				del_class.save()

				return HttpResponseRedirect("/gradeapp/manage_classes")
			except:
				return HttpResponse("Couldn't delete class.")
			
		else:
			try:
				myclass = MyClass.objects.get(class_number = string)
			except:
				return HttpResponse("Error loading class assignments. Please try again.")
			#If class exists, check authentication then show it
			if myclass.authenticate == False:
				return HttpResponseRedirect("/gradeapp/manage_classes/")
			elif myclass.teacher == request.user.username:
				myuser =  user_info.objects.get(username=request.user.username)
				my_class = MyClass.objects.get(teacher = myuser.username, class_number = string)
				split_semester = split_semester_string(my_class.semester)
				return render (request, "edit_class.html", {"myuser" : myuser, "myclass": myclass, "season": split_semester[0], "year": split_semester[1]})
			else:
				return HttpResponseRedirect("/gradeapp/manage_classes/")
	else:
		return redirect('register')

def split_semester_string(semester):
	split_string = semester.split('-')
	if split_string[0] == "FA":
		split_string[0] = "Fall"
	elif split_string[0] == "WI":
		split_string[0] = "Winter"
	elif split_string[0] == "SP":
		split_string[0] = "Spring"
	else:
		split_string[0] = "Fall"
	return split_string

def manage_classes(request):
	if request.user.is_authenticated() and request.user.groups.filter(name = "Teacher"):
		myuser =  user_info.objects.get(username=request.user.username)
		return render (request, "class_list.html", {"myuser" : myuser, "classes": myuser.class_list.all()})
	else:
		return redirect('register')	

def view_assignment_all(request, string, number):
	#Checks authentication
	if request.user.is_authenticated():
		myuser =  user_info.objects.get(username=request.user.username)
	else:
		return redirect('register')
#		return render (request, "class_list.html", {"myuser" : myuser, "classes": myuser.class_list.all()})
	if request.user.groups.filter != "Teacher" or  request.user.groups.filter != "Admin" or   request.user.groups.filter != "Grader":
		try:
			my_asg = Assignment.objects.get(id=number)
		except:
			return HttpResponseRedirect('/gradeapp/classes/' + string + '/')

		asg_teacher = user_info.objects.get(username = request.user.username)
		cur_class = MyClass.objects.get(class_number = string)
		cur_roster = ClassRoster.objects.get(in_class = cur_class)
		GRADER = False
		if asg_teacher in cur_roster.student.all():
			try:
				auth_check = AuthUser.objects.get(student_name = asg_teacher, class_name = cur_class)
				if auth_check.authorized:
					GRADER = True
					asg_teacher = user_info.objects.get(username = cur_class.teacher)
			except:
				GRADER = False
		if my_asg.to_teacher == asg_teacher or GRADER:
			all_stu_asg = Assignment.objects.filter(to_teacher = asg_teacher, assignment_name = my_asg.assignment_name, to_class = MyClass.objects.get(class_number = string))
			return render (request, "assignment_view_all.html", {"asg_list": all_stu_asg, "asg_name": all_stu_asg[0].assignment_name, "id_num": number})
#			except:
#				return HttpResponseRedirect('/gradeapp/classes/' + string + '/')
#			return HttpResponse(asg_teacher.username + ":" + request.user.username)
#			return redirect('register')
		else:
			return HttpResponseRedirect('/gradeapp/classes/' + string + '/')
	else:
		return redirect('index')

#Function to view classes
def approve_grader(request):
	#Checks authentication
	if request.user.is_authenticated():
		if request.user.groups.filter(name = "Teacher"):
			myuser =  user_info.objects.get(username=request.user.username)
			return render (request, "class_list.html", {"myuser" : myuser, "classes": myuser.class_list.all()})
		else:
			return redirect('index')
	else:
		return redirect('register')
		
#Function to view classes
def classes(request):
	#Checks authentication
	if request.user.is_authenticated():
		myuser =  user_info.objects.get(username=request.user.username)
		class_list = myuser.class_list.all()
		new_list = []
		for a_class in class_list:
			try:
				if  request.user.groups.filter(name = "Teacher"):
					new_list.append(a_class)
				else:
					check_auth = AuthUser.objects.get(class_name = a_class, student_name = myuser)
					if check_auth.authorized:
						new_list.append(a_class)
			except:
				pass
		return render (request, "class_list.html", {"myuser" : myuser, "classes": new_list})
	else:
		return redirect('register')
		
def view_file(request, path):
# {'document_root': 'gradeapp/files/', 'show_indexes': True}
	if request.user.is_authenticated():
		try:
				a_file = AssignmentFile.objects.get(my_file = path)
		except:
#			for ass in AssignmentFile.objects.all():
#			steve.append(ass.my_file)
			return HttpResponse(path)
	#a_file = AssignmentFile.objects.get(my_file = path)
		if a_file.to_assignment.to_student.username == request.user.username or a_file.to_assignment.to_class.teacher == request.user.username:
			#content = a_file.my_file.render_text_content()
			f = open("gradeapp/files/" + a_file.my_file.name, "r")
			content = f.readlines()
			f.close()
			return HttpResponse (content, content_type='text/plain')
#			return serve (request, "gradeapp/files/"+path)
		else:
			return HttpResponse("You don't have access to this file.")
	else:
		return redirect('register')
#Function to view assignments
def view_assignment_name(request, string, number, name):
#	if request.session.__contains__("grade_result"):
#		comment = request.session["grade_result"]
#		del request.session["grade_result"]
#	else:
	request.session['stu_name'] = name
	return HttpResponseRedirect ('/gradeapp/classes/' + string + '/' + number + '/')
# "assignment_view.html", {"files": AssignmentFile.objects.all(), "myfile": send_file, "myuser" : name, "myassignment" : asg_display, "all_assignments": Assignment.objects.filter(to_class=myclass).filter(assignment_name=myassignment.assignment_name), "myclass": myclass, "comment": comment, "glist": g_list, "dir": new_dir, "owner": myassignment.is_owner})	


def view_assignment(request, string, number):
	#Checks authentication
	if request.user.is_authenticated():
		try:
				myclass = MyClass.objects.get(class_number=string)
				myuser =  user_info.objects.get(username=request.user.username)
				myassignment = Assignment.objects.get(id=number)
				cur_roster = ClassRoster.objects.get(in_class = myclass)
		except:
				return HttpResponse("This page does not exist. e122")
	else:
		return redirect('register')

	try:
		roster_check = ClassRoster.objects.get(in_class = myclass)
		if not ClassRoster.objects.filter(student = myuser).exists():
			return redirect('index')
	except Exception as e:
		return HttpResponse(e)

	GRADER = False
	if request.user.groups.filter(name = "Grader"):
		if myuser in cur_roster.student.all():
			try:
				auth_check = AuthUser.objects.get(student_name = myuser, class_name = myclass)
				if auth_check.authorized:
					GRADER = True
				else:
					return redirect('index')
			except:
				return redirect('index')
		else:
			return redirect('index')

	if request.session.__contains__("grade_result"):
		comment = request.session["grade_result"]
		del request.session["grade_result"]
	else:
		comment = "Your information is listed below."
	#Checks method 
	if request.method=='POST' and not 'del_me' in request.POST or request.session.__contains__("stu_name"):	
		#Checks post method for asg_max_score. Absence indicate update of information (not save) only
		if not 'asg_max_score' in request.POST:
			if request.session.__contains__("stu_name"):
				try: 
					temp_name = request.session['stu_name']
					del request.session['stu_name']					
					newuser = user_info.objects.get(username = temp_name)
				except:
					return HttpResponse("This page does not exist. e43")
			else:
				try: 
					newuser = user_info.objects.get(username=request.POST['pass_class'])
				except:
					return HttpResponse("This page does not exist. e42")
			asg_display= Assignment.objects.get(assignment_name = myassignment.assignment_name, to_student = newuser, to_class = 

myclass)			
			try:
					send_file = AssignmentFile.objects.get(to_assignment = asg_display)
			except:
					send_file = None


			g_list = []
			new_dir = ""
			if newuser.username is not request.user.username and request.user.groups.filter(name = 'Teacher'):
				try:
					my_asg = Assignment.objects.get(id = number)
					stu_asg = Assignment.objects.get(assignment_name = my_asg.assignment_name, to_student = newuser, to_class = myclass, to_teacher = myuser)
					g_list = CodeFile.objects.filter(to_assignment = stu_asg)
					dir = g_list[0].data_file.name.split('/')
					del dir[len(dir)-1]
					del dir[len(dir)-1]
					del dir[0]
					del dir[0]

					new_dir = '/'.join(dir) + "/"
				except Exception as e:
					pass
		
			return render (request, "assignment_view.html", {"files": AssignmentFile.objects.all(), "myfile": send_file, "myuser" : newuser, "myassignment" : asg_display, "all_assignments": Assignment.objects.filter(to_class=myclass).filter(assignment_name=myassignment.assignment_name), "myclass": myclass, "comment": comment, "glist": g_list, "dir": new_dir, "owner": myassignment.is_owner})	
		else:
			#Updates for all students
			if request.POST['update_user'] == request.user.username:
				update_query = Assignment.objects.filter(to_class = myclass).filter(assignment_name = myassignment.assignment_name)
				for each_assignment in update_query.all():
					each_assignment.max_score = request.POST['asg_max_score']
					each_assignment.assignment_name = request.POST['asg_name']
					each_assignment.due_date = correct_time(request.POST['due_date'])
					each_assignment.retry_limit = request.POST['retry_limit']
					each_assignment.run_time = request.POST['run_time']
					each_assignment.save()
					update_message = "The assignments have been updated for all stud."
				return redirect ('view_assignment', string, number)
			#Updates for a single student only
			else:
				update_user = user_info.objects.get(username = request.POST['update_user'])
				update_assignment = Assignment.objects.get(to_class = myclass, assignment_name = myassignment.assignment_name, to_student = update_user)
				update_assignment.max_score = request.POST['asg_max_score']
				update_assignment.real_score = request.POST['asg_score']
				update_assignment.due_date = correct_time(request.POST['due_date'])
				update_assignment.retry_limit = request.POST['retry_limit']
				update_assignment.run_time = request.POST['run_time']
				update_assignment.save()
				update_message = "The assignments have been updated for " + update_user.first_name + " " + update_user.last_name + "."
				return redirect ('view_assignment', string, number)
	#If method was not post, generates assignment view 
	else:
		if 'del_me' in request.POST:
			try:
				myassignment = Assignment.objects.get(id=number)
				del_list = Assignment.objects.filter(to_class = myassignment.to_class, assignment_name = myassignment.assignment_name, to_teacher = myassignment.to_teacher)
				for asg in del_list:
					asg.delete()
				return redirect ('classes')
##				AssignmentFile.objects.get(my_file = request.POST['del_me']).delete()
#				comment = "Uploaded file deleted"
#				newuser = user_info.objects.get(username=request.user.username)
			except Exception as e:
				return HttpResponse(e)		
		if Assignment.objects.filter(id=number):
			if myassignment.to_class == myclass and myassignment.to_student.username == myuser.username and myclass.teacher == myuser.username or GRADER:	
				try:
					send_file = AssignmentFile.objects.get(to_assignment = myassignment)
				except:
					send_file = None
					
				return render (request, "assignment_view.html", {"myfile": send_file, "files": AssignmentFile.objects.all(), "myuser" : myuser, "myassignment" : myassignment, "all_assignments": Assignment.objects.filter(to_class=myclass).filter(assignment_name=myassignment.assignment_name), "comment": comment, "myclass": myclass})
			elif myassignment.to_class == myclass and myassignment.to_student.username == myuser.username:
				return render (request, "assignment_view.html", {"files": AssignmentFile.objects.all(), "comment": comment, "myuser" : myuser, "myassignment" : myassignment})
			else:
				return HttpResponse("You do not have permission to access this page.")
		else: 
			return HttpResponse("This page does not exist. e2")

def correct_time(date):
		due_date = re.sub('[.]', '', date)
		try:
			return datetime.datetime.strptime(due_date, "%B %d, %Y")			
		except:
			try:
				return datetime.datetime.strptime(due_date, "%m-%d-%Y")			
			except:
				try: 
					return datetime.datetime.strptime(due_date, "%m/%d/%Y")			
				except:
					try:
						return datetime.datetime.strptime(due_date, "%b %d, %Y")			
					except:
						return datetime.date.today()
			
#Function to edit assignment
def edit_assignment(request, string, number):
	#Checks authentication
	if request.user.is_authenticated():
		#Finds assignment with given id to display
		if Assignment.objects.filter(id=number):
			try:
				myclass = MyClass.objects.get(class_number=string)
				myuser =  user_info.objects.get(username=request.user.username)
				myassignment = Assignment.objects.get(id=number)
			except:
				return HttpResponse("This page does not exist. e112")
			if myassignment.to_class == myclass and myassignment.is_owner:
				return render (request, "assignment_edit.html", {"myuser" : request, "myassignment" : myassignment})
			else:
				return HttpResponse("You do not have permission to access this page.")
		else: 
			return HttpResponse("This page does not exist. e2")
	else:
		return redirect('register')

#Function to generate assignment list		
def class_assignment(request, string):
	#Check to see is class exists
	try:
		myclass = MyClass.objects.get(class_number = string)
		cur_teacher = user_info.objects.get(username = myclass.teacher)
		cur_roster = ClassRoster.objects.get(in_class = myclass)
		myuser =  user_info.objects.get(username=request.user.username)
	except Exception as e:
		return HttpResponse(e)#return redirect('index')
	if not myuser in cur_roster.student.all():
		return redirect('index')
	#If class exists, check authentication then show it
	if request.user.is_authenticated():
		if myclass.authenticate:
			if request.user.groups.filter(name = "Teacher") or request.user.groups.filter(name = "Student"):
				asg_list = Assignment.objects.filter(to_student = myuser, to_teacher = cur_teacher, to_class = myclass) 
				return render (request, "assignment_list.html", {"myuser" : myuser, "myclass": myclass, "assignments": asg_list})
			elif request.user.groups.filter(name = "Grader"):
				try:
					auth_check = AuthUser.objects.get(class_name = myclass, student_name = myuser)
					if auth_check.authorized:
						GRADER = True
					else:
						GRADER = False
				except:
					GRADER = False
				if GRADER:
					asg_list = Assignment.objects.filter(to_student = cur_teacher, to_teacher = cur_teacher, to_class = myclass)
					return render (request, "assignment_list.html", {"myuser" : myuser, "myclass": myclass, "assignments": asg_list})
				else:
					return redirect('index')
			else:
				return HttpResponseRedirect("/gradeapp/classes")
		else:
			return HttpResponseRedirect("/gradeapp/classes")
	else:
		return redirect('register')

#Function view for profile		
def view_profile_self(request):
	if request.user.is_authenticated():
		try:
			return redirect ('view_profile', request.user.username)
		except:
			return HttpResponse("Error: User doesn't exist.")
	else:
		return redirect('register')	

#Function view for inbox
def inbox(request):
	if request.user.is_authenticated():
		try:
			myuser =  user_info.objects.get(username=request.user.username)
			inbox = MyInbox.objects.filter(received_by=myuser)
			outbox = MyOutbox.objects.filter(sent_by=myuser)
			return render (request, 'inbox.html', {"myuser": myuser, "inbox": inbox.all(), "outbox": outbox.all()})
		except:
			return redirect ('index')
	else:
		return redirect('register')	

def outbox_redir(request):
	return redirect ('inbox')	

#Function view for message from inbox
def view_out_message(request, number):
	try:
		req_user = user_info.objects.get(username = request.user.username)
		out_message = MyOutbox.objects.get(id = number)
	except:
		return redirect('index')
	if out_message.sent_by != req_user:
#		return HttpResponse(inbox_message.received_by.username + ":" + req_user.username)
		return HttpResponseRedirect("/gradeapp/inbox/")		
	elif request.user.is_authenticated():
		if request.method == 'POST' and 'del_me' in request.POST:
			out_message.delete()
			return HttpResponseRedirect ("/gradeapp/inbox/")
		else:
			try:
				myuser =  user_info.objects.get(username=request.user.username)
				message = MyOutbox.objects.get(id=number)
				return render (request, 'view_message.html', {"myuser": myuser, "mymessage": message})
			except:
				return HttpResponse(request.user.username)
	else:
		return redirect('register')	
#Function view for message from inbox

def view_message(request, number):
	try:
		req_user = user_info.objects.get(username = request.user.username)
		inbox_message = MyInbox.objects.get(id = number)
	except:
		return redirect('index')
	if inbox_message.received_by != req_user:
#		return HttpResponse(inbox_message.received_by.username + ":" + req_user.username)
		return HttpResponseRedirect("/gradeapp/inbox/")		
	elif request.user.is_authenticated():
		if request.method == 'POST' and 'del_me' in request.POST:
			inbox_message.delete()
			return HttpResponseRedirect ("/gradeapp/inbox/")
		else:
			try:
				myuser =  user_info.objects.get(username=request.user.username)
				message = MyInbox.objects.get(id=number)
				return render (request, 'view_message.html', {"myuser": myuser, "mymessage": message})
			except:
				return HttpResponse(request.user.username)
	else:
		return redirect('register')	

#Function view for sending a message		
def send_message(request):
	if request.user.is_authenticated():
		try:
			myuser =  user_info.objects.get(username=request.user.username)
		except:
			return HttpResponse(request.user.username)
	else:
		return redirect('register')	
	if request.method == 'POST':
		send_to = user_info.objects.get(username=request.POST['send_to'])
		title = request.POST['title']
		message = request.POST['message']
		date =  datetime.date.today()
		
		new_inbox = MyInbox(sent_by = myuser.username, received_by = send_to, date = date, title = title, message = message)
		new_inbox.save()
		
		new_outbox = MyOutbox(sent_by = myuser, received_by = send_to.username, date = date, title = title, message = message)
		new_outbox.save()
		return render (request, 'send_message.html', {"myuser": myuser, "send_message": "Your message has been sent."})
		#except:
		#	return HttpResponse("1")
	else:
		return render (request, 'send_message.html', {"myuser": myuser})

#View for sending a message with given data.
#Probably superfluous, fix later
def send_message_id(request, number):
	if request.user.is_authenticated():
		try:
			myuser =  user_info.objects.get(username=request.user.username)
			message = MyInbox.objects.get(id=number)
		except:
			return HttpResponse(request.user.username)
	else:
		return redirect('register')	
	if request.method == 'POST':
		send_to = user_info.objects.get(username=request.POST['send_to'])
		title = request.POST['title']
		message = request.POST.get("message")
		date =  datetime.date.today()
		
		new_inbox = MyInbox(sent_by = myuser.username, received_by = send_to, date = date, title = title, message = message)
		new_inbox.save()
	
		new_outbox = MyOutbox(sent_by = myuser, received_by = send_to.username, date = date, title = title, message = message)
		new_outbox.save()
		return render (request, 'send_message.html', {"myuser": myuser, "send_message": "Your message has been sent."})
	else:
		return render (request, 'send_message.html', {"myuser": myuser, "message": message})
			
#Function to view profile of a given user of string
def view_profile(request, string):
	if request.user.is_authenticated():
		try:
			myuser =  user_info.objects.get(username=string)
		except:
			return HttpResponse("Error: User doesn't exist.")
	else:
		return redirect('register')	
	if request.user.username == string:
		#Updates information if done through post
		if request.method == 'POST':
			f_name = request.POST['first_name']
			l_name = request.POST['last_name']
			email = request.POST['email']
			update_user = request.POST['update_user']
			update_info = user_info.objects.get(username=update_user)
			update_user = User.objects.get(username=update_user)
			update_info.first_name = f_name
			update_info.last_name = l_name
			update_info.email = email
			update_info.save()
			update_user.first_name = f_name
			update_user.last_name = l_name
			update_user.email_address = email
			update_user.save()
			return redirect ('view_profile', myuser.username)
		else:
			return render (request, "edit_profile.html", {"myuser": myuser, "classes": myuser.class_list.all()})
	else:
		return render(request, "view_profile.html", {"myuser": myuser, "classes": myuser.class_list.all()})

#parse sem
def parse_semester(season, year):
	return season.upper()[0:2] + "-" + year
		
#Function to add a class for a student		
def add_a_class(request):
	if request.user.is_authenticated():
		if request.method == 'POST':
			myclass_name = request.POST['class_name']
			myclass_number = request.POST['class_number']
			myclass_sem_season = request.POST['class_semester']	
			myclass_sem_year = request.POST['year_range']
			myclass_semester = parse_semester(myclass_sem_season, myclass_sem_year)
			#updates class info for original user
			try: 
				new_class = MyClass.objects.get(class_name = myclass_name, class_number = myclass_number, semester = myclass_semester)
			except:
				error_message = "Please check your data and try adding the class again."
				return render (request, "add_a_class.html", {"info": user_info.objects.all(), "message": error_message})			
			
			new_student = user_info.objects.get(username=request.user.username)
			
			#checks if you already tried to add the class
			if AuthUser.objects.filter(class_name = new_class).filter(student_name = new_student):
				error_message = "You have already tried to add this class. Please wait for a teacher response."
				return render (request, "add_a_class.html", {"info": user_info.objects.all(), "message": error_message})			
								
			#updates class roster
			try:	
				newroster = ClassRoster.objects.get(in_class = new_class, class_name = myclass_name, class_number = myclass_number, teacher = new_class.teacher) 
				newroster.student.add(user_info.objects.get(username=request.user.username))
			except Exception as e:
				return HttpResponse(e)
				error_message = "There was an error adsding your to the class. Please try again."
				return render (request, "add_a_class.html", {"info": user_info.objects.all(), "message": error_message})			

			#adds class to user data
			try:
				myuser = user_info.objects.get(username=request.user.username)
				myuser.class_list.add(new_class)
			except:
				error_message = "There was an error adding your to the class. Please try again."
				return render (request, "add_a_class.html", {"info": user_info.objects.all(), "message": error_message})			
			
			myuser.save()
			newroster.save()
			new_auth_ticket = AuthUser(class_name = new_class, student_name = new_student)
			new_auth_ticket.save()

			create_added_student_message(new_class, myuser)
			return render (request, "add_a_class.html", {"info": user_info.objects.all(), "message": "You have added " + myclass_number + ". Please wait for teacher approval before further action."})			
		else:
			return render (request, "add_a_class.html", {"info": user_info.objects.all()})
	else:
		return redirect('register')

#Simple log out function
def log_out(request):
	logout(request)
	return HttpResponse("You have been logged out.")

#Base index view	
def index(request):
	if request.user.is_authenticated():
		return render (request, "index.html", {"info": user_info.objects.all()})
	else:
		return redirect('register')

#Admin function to authorize teacher
def auth_myuser(request):
	if not request.user.groups.filter(name='Admin'):	
		return HttpResponse("You do not have permission to access this page.")
	elif request.user.is_authenticated():
		if request.method == 'POST':
			myaction = request.POST['action']
			myname = request.POST['user']
			edit_user = User.objects.get(username=myname)
			moreinfo = user_info.objects.get(username=myname)
			if myaction == 'remove_teacher':
				mygroup = Group.objects.get(name='Teacher')
				edit_user.groups.remove(mygroup)	
				edit_user.save()
				moreinfo.authenticate = False
				moreinfo.save()
				return render (request, "authenticate.html", {"info": user_info.objects.all()})
			elif myaction == 'add_teacher':
				mygroup = Group.objects.get(name='Teacher')
				edit_user.groups.add(mygroup)	
				edit_user.save()
				moreinfo.authenticate = True
				
				try: 
					check_class = MyClass.objects.get(class_name = moreinfo.init_class_name, class_number = moreinfo.init_class_number, semester = moreinfo.init_class_semester, teacher = moreinfo.username)
#					check_class[0].authenticate = True
#					check_class[0].save()
				except:
					check_class = None
				
				if check_class is None:				
					newclass = MyClass(class_name = moreinfo.init_class_name, class_number = moreinfo.init_class_number, semester = moreinfo.init_class_semester, teacher = moreinfo.username, authenticate = True)
					newclass.save()
					newroster = ClassRoster(in_class = newclass, class_name = newclass.class_name, class_number = newclass.class_number, teacher=moreinfo.username) 
					newroster.save()
					newroster.student.add(moreinfo)
					moreinfo.class_list.add(newclass)
				else:
					check_class.authenticate = True
					check_class.save()

				moreinfo.save()
				
				date = datetime.date.today()
				title = "Account Approved."
				message = "Your account has been approved and is now operable."
				new_inbox = MyInbox(sent_by = "ADMIN", received_by = moreinfo, date = date, title = title, message = message)
				new_inbox.save()


				return render (request, "authenticate.html", {"info": user_info.objects.all()})
			else:
				return HttpResponse("Hi")
		else:
			return render (request, "authenticate.html", {"info": user_info.objects.all()})
	else:
		return redirect('register')

#Teacher function to approve student for class
def approve_student_for_class(request, string):
	if request.user.is_authenticated() and request.user.groups.filter(name = "Teacher"):
		class_num = string
		try:
			myclass = MyClass.objects.get(class_number = class_num, teacher = request.user.username) 
		except:
			return HttpResponse("This page does not exist or you do not have access to this page. Please check your url and try again.")

		cur_roster = ClassRoster.objects.get(in_class = myclass)
		try:
			all_list = cur_roster.student.all()
		except Exception as e:
			return HttpResponse(e)
		stu_list = []
		auth_list = []
		for stu in all_list:
			if stu.user_type == "ST":
				stu_list.append(stu)
				auth_list.append(AuthUser.objects.get(class_name = myclass, student_name = stu))

		if request.method == 'POST':
			myaction = request.POST['action']
			myname = request.POST['user']
			edit_user = User.objects.get(username=myname)
			moreinfo = user_info.objects.get(username=myname)
			auth_user = AuthUser.objects.get(student_name = moreinfo, class_name = myclass)
			
			if myaction == 'remove_student':
				auth_user.authorized = False
				auth_user.delete()
				
				moreinfo.class_list.remove(myclass)
				moreinfo.save()
				
				roster = ClassRoster.objects.get(in_class = myclass)
				roster.student.remove(moreinfo)
				roster.save()
				
				#deletes assignments when student is removed
				for each_assignment in Assignment.objects.all():
					if each_assignment.to_student.username == edit_user.username and each_assignment.to_class == myclass:
						each_assignment.delete()
						
				user_info.objects.get(username = request.user.username)

				date = datetime.date.today()
				title = "Removed from Class " + myclass.class_number
				message = "Your have been removed from " + myclass.class_number + " by the instructor."
				new_inbox = MyInbox(sent_by = "ADMIN", received_by = moreinfo, date = date, title = title, message = message)
				new_inbox.save()

				return HttpResponseRedirect ("/gradeapp/approve_student/" + myclass.class_number)
			elif myaction == 'add_student':
				mygroup = Group.objects.get(name='Student')
				edit_user.groups.add(mygroup)	
				edit_user.save()
				moreinfo.authenticate = True
				auth_user.authorized = True
				moreinfo.class_list.add(myclass)
				moreinfo.save()
				auth_user.save()

				roster_edit = ClassRoster.objects.get(in_class = myclass)
				roster_edit.student.add(moreinfo)
				roster_edit.save()
								
				date = datetime.date.today()
				title = "Account Approved."
				message = "Your have been added to " + myclass.class_number + "."
				new_inbox = MyInbox(sent_by = "ADMIN", received_by = moreinfo, date = date, title = title, message = message)
				new_inbox.save()

				#adds assignments when student is added to class
				for each_assignment in Assignment.objects.all():
					if each_assignment.to_student.username == myclass.teacher and each_assignment.to_class == myclass:
						new_assignment_instance = Assignment(assign_date = each_assignment.assign_date, due_date = each_assignment.due_date, to_student = moreinfo, to_class = myclass, assignment_name = each_assignment.assignment_name, max_score = each_assignment.max_score, real_score = 0, retry_limit = each_assignment.retry_limit, to_teacher = user_info.objects.get(username=request.user.username))
						new_assignment_instance.save()								
						
				return HttpResponseRedirect ("/gradeapp/approve_student/" + myclass.class_number)
			else:
				return HttpResponseRedirect ("/gradeapp/approve_student/" + myclass.class_number)
		else:
				return render (request, "approve_student_for_class.html", {"stu_list": stu_list, "auth_list": auth_list, "instance_class": myclass})
	else:
		return redirect('register')	
		
#Shows class list for instructor for classes he or she may have.
#Class list is to manage students from each of those classes.
def approve_student(request):
	if request.user.is_authenticated():
		if request.user.groups.filter(name = "Teacher"):
			myuser =  user_info.objects.get(username=request.user.username)
			return render (request, "class_list.html", {"myuser" : myuser, "classes": myuser.class_list.all()})

		else:
			return redirect('index')
	else:
		return redirect('register')	

def approve_grader_class(request, string):
	if request.user.is_authenticated():
		cur_user = user_info.objects.get(username = request.user.username)
		cur_class = MyClass.objects.get(class_number = string)
		if cur_class.teacher != cur_user.username:
			return redirect('index')
		else:
			cur_roster = ClassRoster.objects.get(in_class = cur_class)
			try:
				stu_list = cur_roster.student.all()
			except Exception as e:
				return HttpResponse(e)
			gra_list = []
			auth_list = []
			for stu in stu_list:
				if stu.user_type == "GR":
					try:
						gra_list.append(stu)
						auth_list.append(AuthUser.objects.get(class_name = cur_class, student_name = stu))
					except:
						pass
#			return HttpResponse(auth_list)

			if request.method != 'POST':
				return render (request, "approve_graders.html", {"myclass": cur_class, "gra_list":gra_list, "auth_list":auth_list})
			elif request.method == 'POST':
			#cur_class is class
				user = request.POST['user']
				if  request.POST['action'] == "add_student":
					stu = user_info.objects.get(username = user)
					app_stu = AuthUser.objects.get(class_name = cur_class, student_name = stu)
					app_stu.authorized = True
					app_stu.save()
		
					upd_user = User.objects.get(username = user)
					mygroup = Group.objects.get(name='Grader')
					upd_user.groups.add(mygroup)					
					upd_user.save()
				elif request.POST['action'] == "remove_student":
					stu = user_info.objects.get(username = user)
					app_stu = AuthUser.objects.get(class_name = cur_class, student_name = stu)

					stu.class_list.remove(cur_class)
			
					cur_roster.student.remove(stu)

					app_stu.delete()
					stu.save()
					cur_roster.save()					
				else:
					return redirect('index')
				return HttpResponseRedirect ("/gradeapp/approve_grader/" + cur_class.class_number)
			else:
				return redirect('index')
	else:
		return redirect('register')

			
#Login user
#Rename and change other names later for consistency/ease of understanding
def log(request):
	if request.method == 'POST':
		username = request.POST['userlog']
		userpass = request.POST['passlog']
		if login_user(request, username, userpass):
			return redirect('index')
		else:
			return HttpResponse("Your information could not be authenticated. Please try again.")
	else:
		return HttpResponse("Your information could not be authenticated. Please try again.")
		
#Register function to register all new users		
def register(request):
	if request.user.is_authenticated():
		return redirect('index')
	elif request.method == 'POST':
		stuff = request.POST
		username = stuff['userreg']
		password = stuff['passreg']
		first_name = stuff['namereg']
		email = stuff['email']
		user_type = stuff['type']
		lname = stuff["lastname"]
		init_class = stuff['class_name']

		myclass_sem_year = request.POST['year_range']
		myclass_sem_season = request.POST['class_semester']
		init_sem = parse_semester(myclass_sem_season, myclass_sem_year)

		init_num = stuff['class_number']
#		init_sem = stuff['class_semester']
		user = user_info.objects.filter(username=username)
		
		#Checks if Email Address if valid
		if not isEmailAddressValid(email):	
			error_message = "ERROR: Your email " + email + " was not valid. Please enter a valid email and try again."
			return render(request, 'register.html', {"error":error_message})
		#Check if fields are left blank
		if username == "" or first_name=="" or lname =="" or email =="" or password == "":
			error_message = "ERROR: One or more fields were left empty. Please fill out each field and try again."
			return render(request, 'register.html', {"error":error_message})
		#Check if user already exists
		elif user.exists():
			error_message = "ERROR: A user already exists with the given username. Enter a new username and try again."
			return render(request, 'register.html', {"error":error_message})
		#Creates our user 
		elif MyClass.objects.filter(class_name = init_class, class_number = init_num, semester= init_sem) or user_type == "TE":

			#Creates user for user_info table
			cost_obj = user_info(init_class_name = init_class, init_class_number= init_num, init_class_semester = init_sem, username=username, first_name=first_name, last_name=lname, email=email, user_type=user_type)
			cost_obj.save()

			#Creates user for Auth table
			user = User.objects.create_user(username, email, password)
			user.first_name = first_name
			user.last_name = lname
			user.save()

			#Adds student or grader to the class as unauthorized student(teacher needs to be approved before class creation)
			if user_type != "TE":
				find_class = MyClass.objects.get(class_name = init_class, class_number = init_num, semester= init_sem)
				authorize_user = AuthUser(student_name = cost_obj, class_name = find_class)
				authorize_user.save()
				cost_obj.class_list.add(find_class)
				create_added_student_message(find_class, cost_obj)
				find_roster = ClassRoster.objects.get(in_class = find_class)
				find_roster.student.add(cost_obj)
				find_roster.save()

			create_welcome_message(cost_obj)
			if login_user(request, username, password):
				return redirect('index')
			else:
				return redirect('register')
		else:
			error_message = "ERROR: No such class exists. Please check your data again."
			return render(request, 'register.html', {"error":error_message})
	else:
		return TemplateResponse (request, "register.html")

####################
#General Functions #
####################
#Creates an "Student Added Class" message to send to instructor
def create_added_student_message(added_class, student):
	date = datetime.date.today()
	title = "New Student for " + added_class.class_number
	teacher = user_info.objects.get(username=added_class.teacher)
	message = student.first_name + " " + student.last_name + " has added you to " + added_class.class_number + "."
	generate_inbox_message("ADMIN", teacher, date, title, message)

#Creates a welcome message for all new users.	
def create_welcome_message(new_user):
	date = datetime.date.today()
	title = "Welcome to The Grading System!"
	message = "Welcome to the grading system. Before you can use our website in full, you will need to be approved. Until then, you will not have access to your classes or assignments."
	generate_inbox_message("ADMIN", new_user, date, title, message)

#Generates an inbox message when given necessary data
def generate_inbox_message(sent_by, received_by, date, title, message):
	new_inbox = MyInbox(sent_by = sent_by, received_by = received_by, date = date, title = title, message = message)
	new_inbox.save()

#Checks to see if e-mail address if valid
def isEmailAddressValid( email ):
	try:
		EmailField().clean(email)
		return True
	except ValidationError:
		return False

#Function that sees if user can be authenticated and then logs in user. 		
def login_user(request, username, password):
	try:
		myuser = authenticate(username = username, password = password)
		if myuser is not None:
			if myuser.is_active:
				login(request, myuser)
				return True
			else:
				return False
		else:
			return False
	except:
		return False
		
#Check extension
def check_extension(file_name):
	if not file_name.endswith(".cpp") and not file_name.endswith(".py") and not file_name.endswith(".xml"):
		raise ValidationError("Invalid file type. Please upload only cpp, py or xml files.")

#Commpile File
def infer_code_path(grade_file):
	#actual_path = "gradeapp/files/" + path

	#grade_file = AssignmentFile.objects.get(my_file = path)

	teach_name = grade_file.to_assignment.to_class.teacher
	teach_name = re.sub('[ ]', '', teach_name)
	dir_name =  teach_name + "/" 
	class_name = grade_file.to_assignment.to_class.class_name
	class_name = re.sub('[ ]', '', class_name)
	dir_name =  teach_name + "/" + class_name + "/" 
	class_seme = grade_file.to_assignment.to_class.semester
	class_seme = re.sub('[ ]', '', class_seme)
	dir_name =  teach_name + "/" + class_name + "/" + class_seme + "/" 
	hw_name = grade_file.to_assignment.assignment_name
	hw_name = re.sub('[ ]', '', hw_name)
	dir_name =  teach_name + "/" + class_name + "/" + class_seme + "/" + hw_name + "/"
	stu_name = grade_file.to_assignment.to_student.username
	stu_name = re.sub('[ ]', '', stu_name)
	retry_attempt = str(grade_file.upload_number)
	dir_name = "gradeapp/compiled_files/" + dir_name + stu_name + "/"
	dir_name = dir_name + retry_attempt + "/"

	return dir_name

def check_auth(path, user):
	split_path = path.split('/')
	if split_path[0] == user:
		return True
	else:
		return False


def test_upload_stuff(path):
	try:
		split_path = path.split('/')
		teacher = user_info.get(username=split_path[0])
		student = user_info.get(username=split_path[4])
		course = MyClass.get(class_name = "Jojo Class")


		to_assignment = Assignment.objects.get(assignment_name = "Assignment")
		my_file = models.FileField(upload_to='%Y/%m/%d')
		file_comment = models.CharField(max_length=200, blank=True)
		upload_number = models.IntegerField(max_length=10)
		date_uploaded = models.DateField()
		attempt_score = models.IntegerField(max_length = 10, default = 0)
	except:
		pass

def show_file(request, path):
	file = path
	file_list = []
	if request.user.groups.filter(name='Student'):
		for a_file in AssignmentFile.objects.all():
			if a_file.to_assignment.to_student.username == request.user.username and a_file.my_file.name == file:
				file_list.append(a_file.my_file.name)	
	elif request.user.groups.filter(name='Teacher'):
		file_list = []
		for a_file in AssignmentFile.objects.all():
			if a_file.to_assignment.to_student.username == request.user.username and a_file.my_file.name == file:
				file_list.append(a_file.my_file.name)
			elif a_file.to_assignment.to_class.teacher == request.user.username and a_file.my_file.name == file:
				file_list.append(a_file.my_file.name)
	elif request.user.groups.filter(name='Admin'):
		file_list = []
		for a_file in AssignmentFile.objects.all():
			if a_file.my_file.name == file:
				file_list.append(a_file.my_file.name)
	else:
		return HttpResponse("ER")
	if len(file_list) > 1 :
		return HttpResponse("Error Loading File")
	elif len(file_list) == 1:
		actual_path = "gradeapp/files/" + file_list[0]
		f = open(actual_path, "r")
		content = f.readlines()
		f.close()
		return HttpResponse (content, content_type='text/plain')
	else:
		return HttpResponse("NO FILE FOUND")


def show_code_all(request, path):
	if check_auth(path, request.user.username):
		try:
			actual_path = "gradeapp/compiled_files/" + path
			#return HttpResponse(actual_path)
			
			f = open(actual_path, "r")
			content = f.readlines()
			f.close()
			return HttpResponse (content, content_type='text/plain')
		except:
			return HttpResponse("NO FILE FOaUND")
	else:
		return HttpResponse("NO FILE FaaaOUND")


def show_code(request, path):
	if check_auth(path, request.user.username):
		try:
			actual_path = "gradeapp/compiled_files/" + path
			#return HttpResponse(actual_path)
			
			f = open(actual_path, "r")
			content = f.readlines()
			f.close()
			return HttpResponse (content, content_type='text/plain')
		except:
			return HttpResponse("NO FILE FOaUND")
	else:
		return HttpResponse("NO FILE FaaaOUND")



def create_list_from_dir(dir, search):

	list = []
	for file in os.listdir(dir):
		if search in file:
			if ".txt" in file:
				list.append(file)
	return list

def test_u_stuff(username, path):
	try:
		actual_path = "gradeapp/files/" + path

		grade_file = AssignmentFile.objects.get(my_file = path)
		assign_file = grade_file.to_assignment

		file_list = []

		for a_file in AssignmentFile.objects.all():
			if a_file.to_assignment.is_owner and a_file.to_assignment.to_class == grade_file.to_assignment.to_class and a_file.to_assignment.assignment_name == grade_file.to_assignment.assignment_name:
				file_list.append(a_file)

		if len(file_list) < 1:
			return "File was uploaded into the system. No grade file was uploaded by the instructor."

		boost_dir = "gradeapp/files/" + file_list[0].my_file.name

		#f = open(actual_path, "r")
		#content = f.readlines()


		#Now, the directory for the compile file is created if necessary. 
		#The compile files will be stored here and remain private.
		compile_name = path.split('/')
		compile_name = compile_name[(len(compile_name)-1)]
		compile_name = compile_name.split('.')
		compile_name = compile_name[0]


		teach_name = grade_file.to_assignment.to_class.teacher
		teach_name = re.sub('[ ]', '', teach_name)

		dir_name =  teach_name + "/" 
		try:
			os.mkdir('gradeapp/compiled_files/' + dir_name)
		except:
			pass


		class_name = grade_file.to_assignment.to_class.class_name
		class_name = re.sub('[ ]', '', class_name)

		dir_name =  teach_name + "/" + class_name + "/" 
		try:
			os.mkdir('gradeapp/compiled_files/' + dir_name)
		except:
			pass

	
		class_seme = grade_file.to_assignment.to_class.semester
		class_seme = re.sub('[ ]', '', class_seme)


		dir_name = teach_name + "/" +  class_name + "/" + class_seme + "/" 
		try:
			os.mkdir('gradeapp/compiled_files/' + dir_name)
		except:
			pass

		hw_name = grade_file.to_assignment.assignment_name
		hw_name = re.sub('[ ]', '', hw_name)

		dir_name =  teach_name + "/" + class_name + "/" + class_seme + "/" + hw_name + "/"
		try:
			os.mkdir('gradeapp/compiled_files/' + dir_name)
		except:
			pass

		stu_name = grade_file.to_assignment.to_student.username
		stu_name = re.sub('[ ]', '', stu_name)

		retry_attempt = str(grade_file.upload_number)

		dir_name = "gradeapp/compiled_files/" + dir_name + stu_name + "/"
		try:
			os.mkdir(dir_name)
		except:
			pass


		dir_name = dir_name + retry_attempt + "/"
		try:
			os.mkdir(dir_name)
		except:
			pass


		compile_name = dir_name + "boost_compiled"
		boost_with_import = dir_name + "boost.cpp"

		#If the file already exists, delete it so it can be re-compiled.
		if os.path.isfile(compile_name):
			os.remove(compile_name)

		#Now, try to compile the file.


		#actual_path = student code
		#boost_with_import = boost test location
		#boost_compiled = compile name

		c1 = open(actual_path, "r")
		c1_text = c1.readlines()
		c1.close()
		c2 = open(dir_name + "student.cpp", "w")
		for line in c1_text:
			c2.write(line)
		c2.close()

		f1 = open(boost_with_import, "w")
		f1.write('#import "student.cpp"\n')
		f2 = open(boost_dir, "r")
		scores = []
		for line in f2:
			if "//Score" in line:
				scores = re.sub('[//Score|(|)|\n| |]', '', line).split(',')
#				scores = re.sub('[(]', '', scores)
#				scores = re.sub('[)]', '', scores)
#				return HttpResponse(scores)	
			f1.write(line)
		f1.close()
		f2.close()	
		#return HttpResponse(scores[0])

#		return HttpResponse(actual_path)
		results = run_unit_test(scores, boost_with_import, compile_name, dir_name)

		try:
			score = int(results)
		except:
			return results

		assign_file.real_score=(results)
		assign_file.already_graded = True
		assign_file.save()


		if not os.path.isfile(compile_name):
			not_compiled = True
		else:
			not_compiled = False
		return "File compiled."

		#return HttpResponse (content, content_type='text/plain')
	except Exception as e:
		return e
	
	if not_compiled:
		result = "Could not compile"
	else:
		result = "Your program compiled."
	return result

def return_teacher_file(path):
	grade_file = AssignmentFile.objects.get(my_file = path)
	file_list = []
	for a_file in AssignmentFile.objects.all():
		if a_file.to_assignment.is_owner and a_file.to_assignment.to_class == grade_file.to_assignment.to_class and a_file.to_assignment.assignment_name == grade_file.to_assignment.assignment_name:
			file_list.append(a_file)

	return file_list


def test_stuff(username, path):
	try:

#		dirdir = infer_code_path(request, path)
#		c = create_list_from_dir(request, dirdir, "grade_results_")	
#		return HttpResponse(c)
	

		actual_path = "gradeapp/files/" + path

		f = open(actual_path, "r")
		content = f.readlines()


		grade_file = AssignmentFile.objects.get(my_file = path)
		assign_file = grade_file.to_assignment
		#xml_files = AssignmentFile.objects.filter(to_assignment.is_owner = True)

		#A file list is created to get the Teacher xml file used to grade the assignment.
		#A size of one indicates the check was correct, 0 indicates no gradefile was uploaded.

		file_list = []

		for a_file in AssignmentFile.objects.all():
			if a_file.to_assignment.is_owner and a_file.to_assignment.to_class == grade_file.to_assignment.to_class and a_file.to_assignment.assignment_name == grade_file.to_assignment.assignment_name:
				file_list.append(a_file)

		if len(file_list) < 1:
			return "File was uploaded into the system. No grade file was uploaded by the instructor."

		xml_dir = "gradeapp/files/" + file_list[0].my_file.name

		#f = open(actual_path, "r")
		#content = f.readlines()


		#Now, the directory for the compile file is created if necessary. 
		#The compile files will be stored here and remain private.
		compile_name = path.split('/')
		compile_name = compile_name[(len(compile_name)-1)]
		compile_name = compile_name.split('.')
		compile_name = compile_name[0]


		teach_name = grade_file.to_assignment.to_class.teacher
		teach_name = re.sub('[ ]', '', teach_name)

		dir_name =  teach_name + "/" 
		try:
			os.mkdir('gradeapp/compiled_files/' + dir_name)
		except:
			pass


		class_name = grade_file.to_assignment.to_class.class_name
		class_name = re.sub('[ ]', '', class_name)

		dir_name =  teach_name + "/" + class_name + "/" 
		try:
			os.mkdir('gradeapp/compiled_files/' + dir_name)
		except:
			pass

	
		class_seme = grade_file.to_assignment.to_class.semester
		class_seme = re.sub('[ ]', '', class_seme)


		dir_name = teach_name + "/" +  class_name + "/" + class_seme + "/" 
		try:
			os.mkdir('gradeapp/compiled_files/' + dir_name)
		except:
			pass

		hw_name = grade_file.to_assignment.assignment_name
		hw_name = re.sub('[ ]', '', hw_name)

		dir_name =  teach_name + "/" + class_name + "/" + class_seme + "/" + hw_name + "/"
		try:
			os.mkdir('gradeapp/compiled_files/' + dir_name)
		except:
			pass

		stu_name = grade_file.to_assignment.to_student.username
		stu_name = re.sub('[ ]', '', stu_name)

		retry_attempt = str(grade_file.upload_number)


		dir_name = "gradeapp/compiled_files/" + dir_name + stu_name + "/"
		try:
			os.mkdir(dir_name)
		except:
			pass


		dir_name = dir_name + retry_attempt + "/"
		try:
			os.mkdir(dir_name)
		except:
			pass

		compile_name = dir_name + compile_name


		#If the file already exists, delete it so it can be re-compiled.
		if os.path.isfile(compile_name):
			os.remove(compile_name)

		#Now, try to compile the file.
		results = run_for_me(xml_dir, actual_path, compile_name, dir_name)

#		return HttpResponse("A")

		print("DIRK22")

		grade_file.attempt_score = (results[0])
		grade_file.save()
		if assign_file.real_score < (results[0]):
			assign_file.real_score = (results[0])
		assign_file.already_graded = True
		assign_file.save()



		print("DIRK")

		if not os.path.isfile(compile_name):
			not_compiled = True
		else:
			not_compiled = False

		print(dir_name)

		for f in os.listdir(dir_name):
			newCode = CodeFile(data_file = dir_name + f, to_assignment = assign_file, retry = int(retry_attempt))
			newCode.save()

	except Exception as e:
		return e
	
	if not_compiled:
		result = "Could not compile"
	else:
		result = "Your program compiled."
	return result
