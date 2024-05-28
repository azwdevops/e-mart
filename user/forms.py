from django import forms

from .models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Enter password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Confirm password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name',
                  'phone_number', 'email', 'password', 'confirm_password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs[
                'placeholder'] = f"Enter {field.title().lower().replace('_', ' ')}"

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        if cleaned_data.get('password') != self.cleaned_data['confirm_password']:
            raise forms.ValidationError("Passwords don't match")


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'Invalid': {
                                       'Image files only'}}, widget=forms.FileInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number',
                  'address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
