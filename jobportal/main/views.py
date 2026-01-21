import random

from django.contrib import messages as dj_messages
from django.contrib.auth.hashers import make_password
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from django.shortcuts import render, redirect
from django.views import View
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.urls import reverse
from django.db.models import Q
from django.utils.timezone import now
from datetime import timedelta
from .utils.emails import send_rejection_email,send_shortlist_email,send_hired_email


def get_dashboard_counts():
    job_categories = Jobdetails.objects.values('job_category').annotate(total=Count('id'))
    category_counts = {item['job_category']: item['total'] for item in job_categories}

    return {
        'category_counts': category_counts,
        'company_count': Company.objects.count(),
        'application_count': Applyjob.objects.count(),
        'job_count': Jobdetails.objects.count(),
        'member_count': UserMaster.objects.filter(is_active=True).count()
    }


class Homeview(View):
    def get(self, request):

        if request.user.is_superuser:
            return redirect('/admin/')
        if request.user.is_authenticated:
            if request.user.role == 'candidate':
                return redirect('main:candidate')
            elif request.user.role == 'company':
                return redirect('main:company')

        selected_type = request.GET.get('type')  # ← key part

        jobs = Jobdetails.objects.order_by('-created_at')

        if selected_type in ['full time', 'part time', 'remote']:
            jobs = jobs.filter(job_type=selected_type)
        context = get_dashboard_counts()
        context.update({  # to update the existing with new values
            'recent_jobs': jobs, 'selected_type': selected_type})
        return render(request, 'home.html', context)


class Jobsubscribe(View):
    def post(self, request):
        email = request.POST.get('email')

        if not email:
            dj_messages.error(request, 'Email is required')
            return redirect('main:candidate')  # reverse() converts the name of the view to a URL's name

        subscription, created = JobSubscription.objects.get_or_create(email=email)

        if created:
            send_mail(
                subject='Thanks for subscribing to job alerts',
                message=('Thank you for subscribing!\n\n '
                         'You will be notified whenever new jobs are posted\n\n'
                         ' - Team Jobya'
                         ),
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            ),
            dj_messages.error(request, 'You have successfully subscribed. Check your email.')
        else:
            dj_messages.error(request, 'You are already subscribed.')
        return redirect(reverse('main:candidate') + '#subscribe')


class Signup(View):
    def get(self, request):
        if request.user.is_authenticated:
            # Redirect based on role
            if request.user.role == 'candidate':
                return redirect('main:candidate')
            elif request.user.role == 'company':
                return redirect('main:company')
            elif request.user.is_superuser:
                return redirect('/admin/')

        form_instance = Signupform()
        return render(request, 'signup.html', {'form': form_instance})

    def post(self, request):
        if request.user.is_authenticated:
            # Redirect based on role
            if request.user.role == 'candidate':
                return redirect('main:candidate')
            elif request.user.role == 'company':
                return redirect('main:company')
            elif request.user.is_superuser:
                return redirect('/admin/')
        form_instance = Signupform(request.POST)
        if form_instance.is_valid():
            dj_messages.error(request,'Enter the OTP. OTP will expire in 5 minutes.')
            u = form_instance.save(commit=False)
            u.is_active = False
            u.save()
            u.generate_otp()
            send_mail(
                subject="Your OTP for Account Verification",
                message=f"""Hello,\n
                         Your One-Time Password (OTP) for account verification is:
                         OTP : {u.otp}   \n
                        OTP will expire in 5 minutes.\n
                        Please do not share this code with anyone.\n 
                        Thanks,\n
                        "Job Portal Team""",
                from_email=None,
                recipient_list=[u.email],
                fail_silently=False,
            )
            return redirect('main:otpverification')
        else:
            dj_messages.error(request, 'Please correct the errors below.')
            return render(request, 'signup.html', {'form': form_instance})


class Otpverification(View):
    def get(self, request):
        return render(request, 'otpverification.html')

    def post(self, request):
        o = request.POST['o']
        if not o:
            dj_messages.error(request, 'OTP is required')
            return redirect(request.path)
        u = UserMaster.objects.filter(otp=o).first()
        if not u:
            dj_messages.error(request, 'INVALID OTP')
            return redirect(request.path)
        
        if not u.otp_created_at or now() > u.otp_created_at + timedelta(minutes=5):
            u.delete()
            dj_messages.error(request, 'OTP expired. Please register again.')
            return redirect('main:signup')

        u.is_verified = True
        u.is_active = True
        u.otp = None
        u.otp_created_at=None
        u.save()
        dj_messages.error(request, 'OTP verified successfully. Please login.')
        return redirect('main:login')


class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.role == 'candidate':
                return redirect('main:candidate')
            elif request.user.role == 'company':
                return redirect('main:company')
            elif request.user.is_superuser:
                return redirect('/admin/')

        form_instance = Loginform()
        return render(request, 'login.html', {'form': form_instance})

    def post(self, request):
        if request.user.is_authenticated:
            if request.user.role == 'candidate':
                return redirect('main:candidate')
            elif request.user.role == 'company':
                return redirect('main:company')
            elif request.user.is_superuser:
                return redirect('/admin/')

        form_instance = Loginform(request.POST)
        if form_instance.is_valid():
            e = form_instance.cleaned_data['email']
            p = form_instance.cleaned_data['password']
            user = authenticate(request, email=e, password=p)
            if not user:
                dj_messages.error(request, 'Invalid email or password.')
            elif not user.is_verified:
                dj_messages.error(request, 'Please verify your email first.')
            elif not user.is_active:
                dj_messages.error(request, 'Account inactive.')
            elif user.role == 'candidate':
                login(request, user)
                dj_messages.error(request, 'Login Successful.')
                return redirect('main:candidate')
            elif user.role == 'company':
                login(request, user)
                dj_messages.error(request, 'Login Successful.')
                return redirect('main:company')
            else:
                dj_messages.error(request, 'User role not assigned.')
                return render(request, 'login.html', {'form': form_instance})
        else:
            dj_messages.error(request, 'Please correct the errors below.')

        return render(request, 'login.html', {'form': form_instance})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('main:login')


class Candidatehome(View):
    def get(self, request):
        if request.user.is_superuser:
            return redirect('/admin/')
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'candidate':
            return redirect('main:company')
        selected_type = request.GET.get('type')  # ← key part

        jobs = Jobdetails.objects.order_by('-created_at')

        if selected_type in ['full time', 'part time', 'remote']:
            jobs = jobs.filter(job_type=selected_type)

        context = get_dashboard_counts()
        context.update({  # to update the existing with new values
            'recent_jobs': jobs,
            'selected_type': selected_type})
        return render(request, 'home.html', context)


class Companyhome(View):
    def get(self, request):
        if request.user.is_superuser:
            return redirect('/admin/')
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'company':
            return redirect('main:candidate')
        jobs=Jobdetails.objects.filter(user_id=request.user)
        applications=Applyjob.objects.filter(job__in=jobs,status='applied').select_related('candidate','job')
        today=now().date()
        today_applications=applications.filter(job__created_at__date=today).count()
        recent_applications=applications.select_related('candidate','job').order_by('-id')[:5]
        context={'total_jobs':jobs.count(),'total_applications':applications.count(),'today_applications':today_applications,'recent_applications':recent_applications}

        return render(request, 'companyhome.html',context)


class Candidateprofileview(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'candidate':
            return redirect('main:company')
        # Ensure candidate profile exists
        candidate, _ = Candidate.objects.get_or_create(
            user_id=request.user,
            defaults={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        )
        skills_list = []
        if candidate.skills:
            skills_list = [s.strip() for s in candidate.skills.split(',')]
        return render(request, 'canprofile.html',
                      {'candidate': candidate, 'email': request.user.email, 'skills': skills_list})


class Candidateprofileedit(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'candidate':
            return redirect('main:company')
        try:
            candidate= Candidate.objects.get(user_id=request.user)
        except Candidate.DoesNotExist:
            dj_messages.error(request,"Please complete your profile first.")
            return redirect('main:canprofile')
        form_instance = Candidateform(instance=candidate)
        form_instance.fields['email'].initial = request.user.email
        context = {'form': form_instance}
        return render(request, 'editcanprofile.html', context)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'candidate':
            return redirect('main:company')
        try:
            candidate = Candidate.objects.get(user_id=request.user)
        except Candidate.DoesNotExist:
            dj_messages.error(request, "Please complete your profile first.")
            return redirect('main:canprofile')

        form_instance = Candidateform(request.POST, request.FILES, instance=candidate)
        form_instance.fields['email'].initial = request.user.email
        if form_instance.is_valid():
            form_instance.save()
            dj_messages.error(request, 'Profile updated successfully.')
            return redirect('main:canprofile')
        else:
            dj_messages.error(request, 'Please correct the errors below.')
            return render(request, 'editcanprofile.html', {'form': form_instance})


class Companyprofileedit(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'company':
            return redirect('main:candidate')

        company, _ = Company.objects.get_or_create(
            user_id=request.user,
            defaults={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            })
        form_instance = Companyform(instance=company)
        form_instance.fields['email'].initial = request.user.email
        return render(request, 'editcomprofile.html', {'form': form_instance})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'company':
            return redirect('main:candidate')

        company, _ = Company.objects.get_or_create(user_id=request.user)
        form_instance = Companyform(request.POST, request.FILES, instance=company)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('main:comprofile')
        else:
            dj_messages.error(request, 'Please correct the errors below.')
            return render(request, 'editcomprofile.html', {'form': form_instance})


class Companyprofileview(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'company':
            return redirect('main:candidate')

        company, _ = Company.objects.get_or_create(user_id=request.user,
                                                   defaults={
                                                       'first_name': request.user.first_name,
                                                       'last_name': request.user.last_name,
                                                   }
                                                   )
        return render(request, 'comprofile.html', {'company': company})


class Jobform(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'company':
            return redirect('main:candidate')
        form_instance = Jobpostform()
        context = {'form': form_instance}
        form_instance.fields['email'].initial = request.user.email
        return render(request, 'jobpostform.html', context)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'company':
            return redirect('main:candidate')
        company, _ = Company.objects.get_or_create(user_id=request.user)
        form_instance = Jobpostform(request.POST, request.FILES)
        if form_instance.is_valid():
            job = form_instance.save(commit=False)
            job.user_id = request.user
            job.email = request.user.email
            job.save()
            dj_messages.error(request, 'Job posted successfully.')
            return redirect('main:company')
        else:
            dj_messages.error(request, 'Please correct the errors below.')
            return render(request, 'jobpostform.html', {'form': form_instance})


class Jobpostlist(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'company':
            return redirect('main:candidate ')
        job_list = Jobdetails.objects.filter(user_id=request.user)
        context = {'joblist': job_list}
        return render(request, 'jobpostlist.html', context)


class Candidatejoblist(View):
    def get(self, request):
        if not request.user.is_authenticated:
            dj_messages.error(request, "Please login to apply for jobs.")
            return redirect('main:login')
        if request.user.role != 'candidate':
            return redirect('main:company')
        try:
            candidate = Candidate.objects.get(user_id=request.user)
        except Candidate.DoesNotExist:
            dj_messages.error(request, "Please complete your profile first.")
            return redirect('main:canprofile')

        job_list = Jobdetails.objects.all()

        # Getting all job IDs that candidate has already applied for
        applied_job=[]
        application=Applyjob.objects.filter(candidate=candidate)
        for i in application:
            applied_job.append(i.job_id)

        context = {'joblist': job_list,'applied_job':applied_job}
        return render(request, 'candidatejoblist.html', context)


class Jobapplylist(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('main:login')
        if request.user.role != 'company':
            return redirect('main:candidate')
        job_list = Applyjob.objects.filter(job__user_id=request.user)
        context = {'joblist': job_list}
        return render(request, 'applyjoblist.html', context)


class Applyjobview(View):
    def get(self, request,job_id):
        if not request.user.is_authenticated:
            return redirect('main:login')

        if request.user.role!= 'candidate':
            return redirect('main:company')

        try:
            candidate = Candidate.objects.get(user_id=request.user)
        except Candidate.DoesNotExist:
            dj_messages.error(request, 'Please complete your profile before applying for a job.')
            return redirect('main:canprofile')

        if not candidate.is_profile_complete():
            dj_messages.error(request, 'Please complete your profile before applying for a job.')
            return redirect('main:canprofile')

        job=Jobdetails.objects.filter(id=job_id).first()
        if not job:
            dj_messages.error(request,'Job Not Found.')
            return redirect('main:canjoblist')

        if Applyjob.objects.filter(candidate=candidate,job=job).exists():
            dj_messages.error(request, 'You have already applied for this job.')
            return redirect('main:canjoblist')

        form_instance=Applyform(initial={'education':candidate.highest_education,'experience':candidate.experience,'website':candidate.website,'min_salary':candidate.min_salary,'max_salary':candidate.max_salary})
        context={'form':form_instance,'job':job}
        return render(request,'apply.html',context)

    def post(self,request,job_id):
        if not request.user.is_authenticated:
            return redirect('main:login')

        if request.user.role!= 'candidate':
            return redirect('main:company')

        try:
            candidate=Candidate.objects.get(user_id=request.user)
        except Candidate.DoesNotExist:
            dj_messages.error(request, 'Please complete your profile before applying for a job.')
            return redirect('main:canprofile')

        if not candidate.is_profile_complete():
            dj_messages.error(request, 'Please complete your profile before applying for a job.')
            return redirect('main:canprofile')

        job=Jobdetails.objects.filter(id=job_id).first()
        if not job:
            dj_messages.error(request,'Job Not Found.')
            return redirect('main:canjoblist')

        form_instance=Applyform(request.POST,request.FILES)
        if form_instance.is_valid():
            application=form_instance.save(commit=False)
            application.candidate=candidate
            application.job=job
            application.save()
            dj_messages.error(request, 'Job applied successfully.')
            return redirect('main:canjoblist')
        else:
            dj_messages.error(request, 'Please correct the errors below.')
            return render(request, 'apply.html', {'form': form_instance, 'job': job})


class Searchview(View):
    def get(self, request):
        if not request.user.is_authenticated:
            dj_messages.error(request, "Please login to search.")
            return redirect('main:login')
        query = request.GET.get('s', '').strip()  # removes leading or trailing spaces.
        j = Jobdetails.objects.none()
        if query:
            j = Jobdetails.objects.filter(
                Q(job_name__icontains=query) | Q(company_name__icontains=query) | Q(location__icontains=query))

        try:
            candidate = Candidate.objects.get(user_id=request.user)
        except Candidate.DoesNotExist:
            dj_messages.error(request, "Please complete your profile first.")
            return redirect('main:canprofile')

        job_list = Jobdetails.objects.all()

        # Getting all job IDs that candidate has already applied for
        applied_job=[]
        application=Applyjob.objects.filter(candidate=candidate)
        for i in application:
            applied_job.append(i.job_id)

        context = {'jobsearch': j, 'query': query,'applied_job':applied_job}
        return render(request, 'search.html', context)

class Appliedjobview(View):
    def get(self,request):
        if not request.user.is_authenticated:
            dj_messages.error(request, "Please login First.")
            return redirect('main:login')
        if request.user.role!= 'candidate':
            return redirect('main:company')
        candidate = Candidate.objects.get(user_id=request.user)


        # Getting all job IDs that candidate has already applied for
        applied_job = Applyjob.objects.select_related('job').filter(candidate=candidate)

        context = {'applied_job': applied_job}
        return render(request, 'applied_job.html', context)

class Categoryjobview(View):
    def get(self,request,category):
        if not request.user.is_authenticated:
            dj_messages.error(request,'Please Login First')
            return redirect('main:login')
        if request.user.role!='candidate':
            return redirect('main:company')
        try:
            candidate = Candidate.objects.get(user_id=request.user)
        except Candidate.DoesNotExist:
            dj_messages.error(request, 'Please complete your profile first.')
            return redirect('main:canprofile')

        jobs=Jobdetails.objects.filter(job_category=category).order_by('-created_at')

        applied_job = []
        applications = Applyjob.objects.filter(candidate=candidate)
        for i in applications:
            applied_job.append(i.job_id)

        context={'jobs':jobs,'category':category.replace('_',' ').title(),'applied_job': applied_job}
        return render(request,'category_job.html',context)

class Jobdetailview(View):
    def get(self,request,i):
        if not request.user.is_authenticated:
            dj_messages.error(request,'Please Login First')
            return redirect('main:login')
        if request.user.role!= 'candidate':
            return redirect('main:company')
        try:
            candidate = Candidate.objects.get(user_id=request.user)
        except Candidate.DoesNotExist:
            dj_messages.error(request, 'Please complete your profile first.')
            return redirect('main:canprofile')

        if not candidate.is_profile_complete():
            dj_messages.error(request, 'Please complete your profile before applying for a job.')
            return redirect('main:canprofile')

        job = Jobdetails.objects.filter(id=i).first()
        has_applied=Applyjob.objects.filter(candidate=candidate,job=job).exists()

        if not job:
            dj_messages.error(request, 'Job Not Found.')
            return redirect('main:canjoblist')


        job_url = request.build_absolute_uri()

        context={'job':job,'job_url':job_url,'has_applied':has_applied}
        return render(request,'jobdetail.html',context)

class Contactview(View):
    def get(self,request):
        return render(request,'cancontact.html')

class Companyapplicationdetail(View):
    def get(self,request,app_id):
        if not request.user.is_authenticated:
            dj_messages.error(request, "Please login First.")
            return redirect('main:login')

        if request.user.role!= 'company':
            return redirect('main:candidate')

        application=Applyjob.objects.select_related('candidate','job').filter(id=app_id,job__user_id=request.user).first()

        if not application:
            dj_messages.error(request,'Application Not Found')
            return redirect('main:company')
        return render(request,'company_application_detail.html',{'application':application})

class Updateapplicationstatus(View):
    def get(self,request,app_id,status):
        if not request.user.is_authenticated:
            dj_messages.error(request, "Please login First.")
            return redirect('main:login')
        if request.user.role!= 'company':
            return redirect('main:candidate')

        application=Applyjob.objects.filter(id=app_id,job__user_id=request.user).first()

        if not application:
            dj_messages.error(request,'Application Not Found')
            return redirect('main:company')

        allowed_status={
            'applied':['shortlisted','rejected'],
            'shortlisted':['hired','rejected'], }

        if status not in allowed_status.get(application.status,[]):
            dj_messages.error(request,'Invalid Status')
            return redirect('main:company_application_detail',app_id=app_id)
        application.status=status
        application.save()

        if status== 'shortlisted':
            send_shortlist_email(application)

        elif status== 'rejected':
            send_rejection_email(application)

        elif status== 'hired':
            send_hired_email(application)

        dj_messages.error(request,f"Application status updated to {status.title()}")
        return redirect('main:company_application_detail',app_id=app_id)


class Shortlistedapplications(View):
    def get(self,request):
        if not request.user.is_authenticated:
            dj_messages.error(request, "Please login First.")
            return redirect('main:login')
        if request.user.role!= 'company':
            return redirect('main:candidate')
        applications=Applyjob.objects.filter(job__user_id=request.user,status='shortlisted').select_related('candidate','job')
        context={'applications':applications}
        return render(request,'shortlisted_application.html',context)


class Hiredapplications(View):
    def get(self,request):
        if not request.user.is_authenticated:
            dj_messages.error(request, "Please login First.")
            return redirect('main:login')
        if request.user.role!= 'company':
            return redirect('main:candidate')
        applications=Applyjob.objects.filter(job__user_id=request.user,status='hired').select_related('candidate','job')
        context={'applications':applications}
        return render(request,'hired_application.html',context)


class Rejectedapplications(View):
    def get(self,request):
        if not request.user.is_authenticated:
            dj_messages.error(request, "Please login First.")
            return redirect('main:login')
        if request.user.role!= 'company':
            return redirect('main:candidate')
        applications=Applyjob.objects.filter(job__user_id=request.user,status='rejected').select_related('candidate','job')
        context={'applications':applications}
        return render(request,'rejected_application.html',context)

class Forgotpassword(View):
    def get(self,request):
        form_instance=Forgotpasswordform()
        return render(request,'forgot_password.html',{'form':form_instance})
    def post(self,request):
        form_instance=Forgotpasswordform(request.POST)
        if not form_instance.is_valid():
            dj_messages.error(request, 'Please enter a valid email')
            return render(request,'forgot_password.html',{'form':form_instance})

        email=form_instance.cleaned_data['email']
        user=UserMaster.objects.filter(email=email).first()
        if  not user:
            dj_messages.error(request, 'No account found with this email')
            return render(request,'forgotpassword.html',{'form':form_instance})

        otp=str(random.randint(100000,999999))

        ForgotpasswordOTP.objects.filter(user=user).delete()

        ForgotpasswordOTP.objects.create(user=user,otp=otp)

        send_mail(
            subject="Your OTP for Password Reset",
            message=f"""Hello,\n
                     Your One-Time Password (OTP) for password reset is:\n
                     OTP : {otp}   \n
                    Please do not share this code with anyone.\n 
                    Thanks,\n
                    "Job Portal Team""",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
        dj_messages.error(request,'OTP sent to your email.')
        return redirect('main:resetpassword',user_id=user.id)


class Resetpassword(View):
    def get(self,request,user_id):
        return render(request,'reset_password.html',{'user_id':user_id})

    def post(self,request,user_id):
        otp=request.POST.get('otp')
        password=request.POST.get('password')
        user=UserMaster.objects.filter(id=user_id).first()
        if not user:
            dj_messages.error(request,'User not found')
            return redirect('main:forgotpassword')

        otp_record=ForgotpasswordOTP.objects.filter(user=user,otp=otp).first()
        if not otp_record:
            dj_messages.error(request,'Invalid OTP')
            return redirect(request.path)

        user.password=make_password(password)
        user.save()
        otp_record.delete()
        dj_messages.error(request,'Password reset successful. Please login.')
        return redirect('main:login')











