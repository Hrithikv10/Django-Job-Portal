from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from django.utils.timezone import now
from datetime import timedelta

from django.contrib.auth.models import BaseUserManager

class UserMasterManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class UserMaster(AbstractUser):
    username = None
    email=models.EmailField(unique=True)
    otp=models.CharField(max_length=10,null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    role=models.CharField(max_length=20,null=True)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_created=models.DateTimeField(auto_now_add=True)
    is_updated=models.DateTimeField(auto_now=True)

    def generate_otp(self):
        #for creating otp for a user object
        otp=str(random.randint(1000,9999))+str(self.id)
        self.otp=otp
        self.otp_created_at=now()
        self.save()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserMasterManager()

    def __str__(self):
        return self.email

class Candidate(models.Model):
    user_id=models.OneToOneField(UserMaster,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=20)
    contact=models.CharField(max_length=15, blank=True)
    state=models.CharField(max_length=30,null=True)
    city=models.CharField(max_length=30)
    address=models.TextField()
    dob=models.CharField(max_length=40)
    gender=models.CharField(max_length=30)
    min_salary=models.BigIntegerField(default=0)
    max_salary=models.BigIntegerField(default=0)
    job_type=models.CharField(max_length=150,default="")
    job_category=models.CharField(max_length=150,default="")
    country=models.CharField(max_length=150,default="")
    highest_education=models.CharField(max_length=150,default="")
    experience=models.CharField(max_length=150,default="")
    website=models.URLField(blank=True)
    shift=models.CharField(max_length=150,default="")
    profile_summary=models.CharField(max_length=500,default="")
    skills=models.CharField(max_length=150,default="")
    profile_picture=models.ImageField(upload_to='candiate')

    def is_profile_complete(self):
        required_fields = [self.first_name,self.last_name,self.contact,self.city,self.highest_education,self.experience,]
        return all(required_fields)

    def save(self, *args, **kwargs):
        if self.user_id.role != 'candidate':
            raise ValueError("Only candidate users can have Candidate profile")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name

class Company(models.Model):
    user_id = models.OneToOneField(UserMaster, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=20)
    company_name=models.CharField(max_length=80)
    state=models.CharField(max_length=40)
    city = models.CharField(max_length=30)
    company_address = models.TextField(blank=True)
    company_contact=models.CharField(max_length=15, blank=True,null=True)
    company_website = models.URLField(blank=True)
    description=models.CharField(max_length=500,default="")
    logo=models.ImageField(upload_to='company',blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.user_id.role != 'company':
            raise ValueError("Only company users can have Company profile")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name


class Jobdetails(models.Model):
    JOB_TYPE_CHOICES = (('full time', 'Full Time'),('part time', 'Part Time'),('remote', 'Remote'))
    JOB_CATEGORY_CHOICES=(('technology_it','Technology & IT'),('software_development','Software Development'),('data_analytics','Data & Analytics'),('ux_design','UI / UX & Design'),('accounting_finance','Accounting & Finance'),('sales_marketing','Sales & Marketing'),('human_resources','Human Resources'),('customer_support','Customer Support'))

    user_id = models.ForeignKey(UserMaster, on_delete=models.CASCADE,null=True,blank=True,limit_choices_to={'role': 'company'})
    job_name=models.CharField(max_length=200)
    company_name=models.CharField(max_length=250)
    company_address=models.CharField(max_length=250)
    job_description=models.TextField(max_length=500)
    qualification=models.CharField(max_length=250)
    responsibilities=models.CharField(max_length=250)
    job_category = models.CharField(max_length=200,choices=JOB_CATEGORY_CHOICES,default='software_development')
    job_type=models.CharField(max_length=200,choices=JOB_TYPE_CHOICES,default='full time')
    location=models.CharField(max_length=250)
    company_website=models.URLField(blank=True)
    email=models.EmailField(blank=True)
    company_contact=models.CharField(max_length=15, blank=True,null=True)
    salary_package=models.CharField(max_length=250)
    experience=models.CharField(max_length=200,blank=True)
    logo=models.ImageField(upload_to='jobpost',blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_name

class Applyjob(models.Model):
    candidate=models.ForeignKey(Candidate,on_delete=models.CASCADE)
    job=models.ForeignKey(Jobdetails,on_delete=models.CASCADE)
    education=models.CharField(max_length=200)
    experience=models.CharField(max_length=200)
    website=models.URLField(blank=True)
    min_salary=models.CharField(max_length=200)
    max_salary = models.CharField(max_length=200)
    status=models.CharField(max_length=20,choices=(('applied','Applied'),('shortlisted','Shortlisted'),('rejected','Rejected'),('hired','Hired')),default='applied')
    resume=models.FileField(upload_to='resume')
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate', 'job')

    def __str__(self):
        return self.candidate.first_name + " " + self.candidate.last_name + " applied for " + self.job.job_name


class JobSubscription(models.Model):
    email=models.EmailField(unique=True)
    subscribed_at=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.email

class ForgotpasswordOTP(models.Model):
    user=models.ForeignKey(UserMaster,on_delete=models.CASCADE)
    otp=models.CharField(max_length=10)

    def __str__(self):
        return self.user.email
