from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    city = forms.CharField(max_length=50)
    pincode = forms.CharField(max_length=10)