from django import forms
from django.forms import ModelForm

class ToolForm(ModelForm):
    class Meta:
        model = Tool
        fields = "__all__"