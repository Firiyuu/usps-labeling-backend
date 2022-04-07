from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.sites.shortcuts import get_current_site 
from django.conf import settings

class CustomAllauthAdapter(DefaultAccountAdapter):
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        protocol = 'https' if request.is_secure() else 'http'
        current_site = get_current_site(request)
        activate_url = f'{protocol}://{request.get_host()}/api/accounts/rest-auth/registration/account-confirm-email/{emailconfirmation.key}'
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
        }
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            email_template = 'account/email/email_confirmation'
        self.send_mail(email_template,
                       emailconfirmation.email_address.email,
                       ctx)

    def send_mail(self, template_prefix, email, context):
        msg = self.render_mail(template_prefix, email, context)
        msg.send()
