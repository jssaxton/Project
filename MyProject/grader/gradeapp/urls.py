########################
#urls.py               #
########################
from django.conf.urls import patterns, url
from gradeapp import views
from gradeapp.models import user_info, MyClass, UserForm, ClassRoster, AuthUser, Assignment, MyInbox, MyOutbox, AssignmentFile
#, CodeFile, CodeFileList, CodeFileStorage

urlpatterns = patterns('',

	#Index Views
    url(r'^$', views.index_page, name='index'),
	url(r'^index/$', views.index, name='index'),
	
	#Register/Logging Views
	url(r'^register/$', views.register, name='register'),
	url(r'^log/$', views.log, name='log'),
	url(r'^log_out/$', views.log_out, name='log_out'),
	
	#Approve Users Views
	url(r'^authenticate/$', views.auth_myuser, name='auth_myuser'),
	url(r'^approve_student/$', views.approve_student, name='approve_student'),
	url(r'^approve_student/(?P<string>[\w\-]+)/$', views.approve_student_for_class, name='approve_student_for_class'),
	url(r'^approve_grader/$', views.approve_grader, name='approve_grader'),
	url(r'^approve_grader/(?P<string>[\w\-]+)/$', views.approve_grader_class, name='approve_grader_class'),

	#Upload Views
	url(r'^upload_file/(?P<number>\d+)/$', views.upload_file, name='upload_file'),

	#Inbox Views
	url(r'^outbox/$', views.outbox_redir, name='outbox_redir'),
	url(r'^inbox/$', views.inbox, name='inbox'),
	url(r'^inbox/(?P<number>\d+)/$', views.view_message, name='view_message'),
	url(r'^outbox/(?P<number>\d+)/$', views.view_message, name='view_out_message'),
	url(r'^send_message/$', views.send_message, name='send'),
	url(r'^send_message/(?P<number>\d+)/$', views.send_message_id, name='send_id'),

	#Classroom Views
	url(r'^classes/(?P<string>[\w\-]+)/$', views.class_assignment, name='classes'),
	url(r'^classes/(?P<string>[\w\-]+)/(?P<number>\d+)/$', views.view_assignment, name='view_assignment'),
	url(r'^classes/(?P<string>[\w\-]+)/(?P<number>\d+)/all$', views.view_assignment_all, name='view_assignment_all'),
	url(r'^classes/(?P<string>[\w\-]+)/(?P<number>\d+)/(?P<name>[\w\-]+)$', views.view_assignment_name, name='view_assignment_all'),
	url(r'^classes/$', views.classes, name='classes'),
	url(r'^create_a_class/$', views.create_a_class, name='create_class'),
	url(r'^add_a_class/$', views.add_a_class, name='add_a_class'),
	url(r'^create_assignment/$', views.create_assignment, name='create_assignment'),

	#Profile Views
	url(r'^profile/$', views.view_profile_self, name='view_profile_self'),
	url(r'^profile/(?P<string>[\w\-]+)/$', views.view_profile, name='view_profile'),
	
	#Image Views
#	url(r'^files/(?P<path>.*)$', views.view_file, name = "view_file"),
	#url(r'^file/(?P<string>[\w\.\-\/]+)/$', views.view_file, name='view_file'),
	#url(r'^file/$', views.view_file, name='view_file'),

	url(r'^manage_classes/$', views.manage_classes, name = "manage_classes"),	
	url(r'^manage_classes/(?P<string>[\w\-]+)/$', views.edit_classes, name = "edit_classes"),	

	#Testing stuff
	url(r'^test/(?P<path>.*)$', views.test_upload_stuff, name = "test_stuff"),	
	url(r'^file/(?P<path>.*)$', views.show_file, name = "show_file"),	
	url(r'^files/(?P<path>.*)$', views.show_file, name = "show_file"),	
	url(r'^code/(?P<path>.*)$', views.show_code, name = "show_ce"),	
	url(r'^compiled_files/(?P<path>.*)$', views.show_code_all, name = "show_ca"),	
#	2014/05/05/vlcsnap-2012-01-27-22h10m29s171.png
)
