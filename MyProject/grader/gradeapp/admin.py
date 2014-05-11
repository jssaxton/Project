from django.contrib import admin
from gradeapp.models import user_info, MyClass, UserForm, ClassRoster, AuthUser, Assignment, MyInbox, MyOutbox, AssignmentFile, CodeFile #AssignmentFileList, CodeFile, CodeFileList, CodeFileStorage 

# Register your models here.
admin.site.register(user_info)
admin.site.register(MyClass)
admin.site.register(ClassRoster)
admin.site.register(AuthUser)
admin.site.register(MyInbox)
admin.site.register(MyOutbox)
admin.site.register(AssignmentFile)
#admin.site.register(AssignmentFileList)
admin.site.register(Assignment)
admin.site.register(CodeFile)
#admin.site.register(CodeFileList)
#admin.site.register(CodeFileStorage)

