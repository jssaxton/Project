from django import forms
from gradeapp.models import AssignmentFile

class UploadFileForm(forms.ModelForm):

	class Meta:
		model = AssignmentFile