from django import forms
from django.conf import settings
from django.core.mail import EmailMessage


class ContactForm(forms.Form):
    name = forms.CharField(label="Name", max_length=120)
    email = forms.EmailField(label="Email")
    subject = forms.CharField(label="Subject", max_length=70)
    message = forms.CharField(label="Message", widget=forms.Textarea)

    def get_info(self):
        """Formats form information to use in an email.

        Returns:
            (str, str, str, str): Strings for the subject and message of an eamil.
        """
        clean_data = self.cleaned_data

        name = clean_data.get("name", "")
        sender_email = clean_data["email"]
        subject = clean_data["subject"]
        msg = clean_data["message"]

        return subject, msg, sender_email, name

    def send(self):
        subject, msg, sender_email, sender_name = self.get_info()
        subject = f"[Contact] {subject}"
        body = f"From: {sender_name} <{sender_email}>\n\n{msg}"

        EmailMessage(
            subject=subject,
            body=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", sender_email),
            to=getattr(settings, "CONTACT_RECIPIENTS", [getattr(settings, "DEFAULT_FROM_EMAIL", sender_email)]),
            reply_to=[sender_email]
        ).send(fail_silently=False)
