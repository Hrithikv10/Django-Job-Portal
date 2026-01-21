from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *


class Signupform(UserCreationForm):
    role_choice=(('', 'Select Role'),('candidate','Candidate'),('company','Company'))
    role=forms.ChoiceField(choices=role_choice)
    class Meta:
        model=UserMaster
        fields=['first_name','last_name','email','password1','password2','role']


        widgets={
            'first_name':forms.TextInput(attrs={'placeholder':'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder':'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
            }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # ensures unique username per user
        if commit:
            user.save()
        return user

class Loginform(forms.Form):
        email = forms.CharField(
            widget=forms.EmailInput(attrs={'placeholder': 'Email','class': 'form-control'
            })
        )
        password = forms.CharField(
            widget=forms.PasswordInput(attrs={'placeholder': 'Password','class': 'form-control'
            })
        )


EXPERIENCE_CHOICES = (('fresher', 'Fresher'),('0-2', '0–2 Years'),('2-5', '2–5 Years'),('5+', '5+ Years'),)

class Candidateform(forms.ModelForm):
    email = forms.EmailField(disabled=True,required=False,widget=forms.EmailInput(attrs={'class': 'form-control'}))
    shift = forms.ChoiceField(choices=(('','Select Shift'),('day', 'Day'),('night', 'Night'),('rotational', 'Rotational')))
    experience = forms.ChoiceField(choices=EXPERIENCE_CHOICES,widget=forms.RadioSelect)
    gender = forms.ChoiceField(choices=(('male', 'Male'), ('female', 'Female'),('other','Other')),widget=forms.Select())
    job_type=forms.ChoiceField(choices=(('','Select Job Type'),('full_time', 'Full Time'),('part_time', 'Part Time'),('remote','Remote')))

    class Meta:
        model=Candidate
        fields=['first_name','last_name','contact','email','country','state','city','address','dob','gender','min_salary','max_salary','job_type','job_category','highest_education','experience','website','shift','profile_summary','skills','profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'e.g. Rahul'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'e.g. Sharma'}),
            'contact': forms.NumberInput(attrs={'placeholder': 'e.g. 9876543210'}),
            'country':forms.TextInput(attrs={'placeholder':'e.g. India'}),
            'city': forms.TextInput(attrs={'placeholder': 'e.g. Kochi'}),
            'address': forms.Textarea(attrs={'placeholder': 'e.g. Flat No 12, MG Road, Near Metro Station','rows': 3}),
            'dob': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),
            'min_salary': forms.NumberInput(attrs={'placeholder': 'e.g. 20000'}),
            'max_salary': forms.NumberInput(attrs={'placeholder': 'e.g. 50000'}),
            'job_category': forms.TextInput(attrs={'placeholder': 'e.g. Software Developer'}),
            'highest_education': forms.TextInput(attrs={'placeholder': 'e.g. B.Tech Computer Science'}),
            'website': forms.TextInput(attrs={'placeholder': 'e.g. https://portfolio.me'}),
            'profile_summary': forms.Textarea(attrs={'placeholder': 'e.g. I am a Python developer with Django experience','rows': 5}),
            'skills': forms.TextInput(attrs={'placeholder': 'e.g. Python, Django, React'}),
            'profile_picture': forms.FileInput(),
        }


class Companyform(forms.ModelForm):
    email = forms.EmailField(disabled=True, required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    class Meta:
        model=Company
        fields=['first_name','last_name','email','company_name','state','city','company_address','company_contact','company_website','description','logo']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'e.g. Rahul'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'e.g. Sharma'}),
            'company_name':forms.TextInput(attrs={'placeholder': 'e.g. ABC Private Limited'}),
            'company_contact': forms.NumberInput(attrs={'placeholder': 'e.g. 9876543210'}),
            'state': forms.TextInput(attrs={'placeholder': 'e.g. India'}),
            'city': forms.TextInput(attrs={'placeholder': 'e.g. Kochi'}),
            'company_address': forms.Textarea(attrs={'placeholder': 'e.g. Flat No 12, MG Road, Near Metro Station', 'rows': 3}),
            'company_website': forms.TextInput(attrs={'placeholder': 'e.g. https://portfolio.me'}),
            'description': forms.Textarea(attrs={'placeholder': 'e.g. We are a leading company in the field of software development', 'rows': 5}),
            'logo': forms.FileInput(),
        }


class Jobpostform(forms.ModelForm):
    email = forms.EmailField(disabled=True, required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    class Meta:
        model=Jobdetails
        fields=['email','job_name','company_name','company_address','job_description','qualification','responsibilities','job_type','job_category','location','company_website','company_contact','salary_package','experience','logo']
        labels = {
            'email': 'Company Email',
        }
        widgets={
            'job_name':forms.TextInput(attrs={'placeholder': 'e.g. Python Developer'}),
            'company_name':forms.TextInput(attrs={'placeholder':'e.g. ABC Private Limited'}),
            'company_address': forms.Textarea(attrs={'placeholder': 'e.g. Flat No 12, MG Road, Near Metro Station','rows':3}),
            'job_description': forms.Textarea(attrs={'placeholder': 'e.g. We are looking for a Python developer with Django experience','rows':4}),
            'qualification': forms.TextInput(attrs={'placeholder': 'e.g. B.Tech Computer Science'}),
            'responsibilities': forms.TextInput(attrs={'placeholder': 'e.g. Developing web applications using Django'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. Hyderabad, Telangana'}),
            'company_website': forms.TextInput(attrs={'placeholder': 'e.g. ABC Private Limited'}),
            'company_contact': forms.NumberInput(attrs={'placeholder': 'e.g. 9876543210'}),
            'salary_package':forms.TextInput(attrs={'placeholder': 'e.g. 20000'}),
            'experience':forms.TextInput(attrs={'placeholder':'e.g. 2'}),
            'logo': forms.FileInput(),
        }

class Applyform(forms.ModelForm):
    class Meta:
        model=Applyjob
        fields=['education','experience','website','min_salary','max_salary','resume']

class Forgotpasswordform(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email','class': 'form-control'}))

