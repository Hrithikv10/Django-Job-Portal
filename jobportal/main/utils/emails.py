from django.core.mail import send_mail
from pyexpat.errors import messages


def send_shortlist_email(application):
    send_mail(
        subject="You have been shortlisted",
        message=f"""
    Hello {application.candidate.first_name},
    
    Good news 🎉
    You have been shortlisted for Role:
    {application.job.job_name} at {application.job.company_name}
    
    We will contact you soon.
                
    Regards,
    {application.job.company_name}
    """,
    from_email=None,
    recipient_list=[application.candidate.user_id.email],
    fail_silently=False,
    )

def send_rejection_email(application):
    send_mail(
        subject="You have been rejected",
        message=f"""
        
        Hello {application.candidate.first_name},
        
        Thank you for applying for {application.job.job_name} at {application.job.company_name}.
        Unfortunately, we will not proceed further.
        
        Regards,
        {application.job.company_name}
        """,
        from_email=None,
        recipient_list=[application.candidate.user_id.email],
        fail_silently=False,
    )

def send_hired_email(application):
    send_mail(
        subject="Congratulations! You have been hired",
        message=f"""
        
        Hello {application.candidate.first_name},
        
        Congratulations 🎉
        You have been hired for {application.job.job_name} at {application.job.company_name}.
        
        Regards,
        {application.job.company_name}
        """,
        from_email=None,
        recipient_list=[application.candidate.user_id.email],
        fail_silently=False,
    )