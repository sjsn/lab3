from django import forms
from .models import URL

class SearchForm(forms.ModelForm):

	class Meta:
		model = URL
		fields = ('url',)

