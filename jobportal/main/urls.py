"""
URL configuration for jobportal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name='main'

urlpatterns = [
    path('',views.Homeview.as_view(),name='home'),
    path('signup/',views.Signup.as_view(),name='signup'),
    path('login/',views.Login.as_view(),name='login'),
    path('candidatehome/',views.Candidatehome.as_view(),name='candidate'),
    path('otp-verification/',views.Otpverification.as_view(),name='otpverification'),
    path('logout/',views.Logout.as_view(),name='logout'),
    path('candidate-profile/',views.Candidateprofileview.as_view(),name='canprofile'),
    path('candidate-profile/edit',views.Candidateprofileedit.as_view(),name='editcanprofile'),
    path('candidate-joblist/',views.Candidatejoblist.as_view(),name='canjoblist'),
    path('subscribe/',views.Jobsubscribe.as_view(),name='subscribe'),
    path('applyjob/<int:job_id>/',views.Applyjobview.as_view(),name='apply'),
    path('candidatehome/search/',views.Searchview.as_view(),name='search'),
    path('candidatehome/appliedjobs/',views.Appliedjobview.as_view(),name='applied'),
    path('jobs/category/<str:category>/',views.Categoryjobview.as_view(),name='category'),
    path('candidatehome/jobs/jobdetail/<int:i>/',views.Jobdetailview.as_view(),name='jobdetail'),
    path('contact/',views.Contactview.as_view(),name='contact'),
    path('forgotpassword/',views.Forgotpassword.as_view(),name='forgotpassword'),
    path('resetpassword/<int:user_id>/',views.Resetpassword.as_view(),name='resetpassword'),





######################### COMPANY SIDE ###############################

    path('companyhome/',views.Companyhome.as_view(),name='company'),
    path('company-profile/',views.Companyprofileview.as_view(),name='comprofile'),
    path('company-profile/edit',views.Companyprofileedit.as_view(),name='editcompprofile'),
    path('job-post/',views.Jobform.as_view(),name='jobpost'),
    path('job-list/',views.Jobpostlist.as_view(),name='jobpostlist'),
    path('job-apply-list/',views.Jobapplylist.as_view(),name='jobapplylist'),
    path('companyhome/application/<int:app_id>/',views.Companyapplicationdetail.as_view(),name='company_application_detail'),
    path('companyhome/application/<int:app_id>/status/<str:status>/',views.Updateapplicationstatus.as_view(),name='update_application_status'),
    path('companyhome/applications/shortlisted/',views.Shortlistedapplications.as_view(),name='shortlisted_application'),
    path('companyhome/applications/hired/',views.Hiredapplications.as_view(),name='hired_application'),
    path('companyhome/applications/rejected/',views.Rejectedapplications.as_view(),name='rejected_application'),






]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
