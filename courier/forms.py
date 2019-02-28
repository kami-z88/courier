from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import widgets, Textarea, TextInput, EmailField
from .models import AddressBook, Address, Country, Province, City


class TrackItemForm(forms.Form):
	tracking_code = forms.CharField(widget=TextInput(
		attrs={
			'class': 'form-control col-md-12',
			'id': 'tracking-textbox',
			'placeholder': 'Enter tracking code here'
		}
	), label=False)


class AddressForm(forms.ModelForm):

	class Meta:
		model = Address
		fields = (
			'city',
			'zip',
			'address1',
			'address2',
			'phone',
			'fax',
			'email'
		)
		widgets = {
			"zip": TextInput(attrs={'placeholder': "zip", 'required': True}),
			"address1": Textarea(attrs={'cols': 80, 'rows': 2, 'required': True, 'placeholder': 'Street address, P.O. box, company name, c/o'}),
			"address2": Textarea(attrs={'cols': 80, 'rows': 2, 'placeholder': 'Apartment, suite , unit, building, floor, etc.'}),
			"phone": TextInput(attrs={'placeholder': "phone"}),
			"fax": TextInput(attrs={'placeholder': "fax"}),
			"email": TextInput(attrs={'placeholder': "email"}),
		}


class AddressBookForm(forms.ModelForm):
	class Meta:
		model = AddressBook
		fields = ('title',)

