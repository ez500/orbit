from django import forms
from django.conf import settings
from django.core.mail import send_mail


class ContactForm(forms.Form):
    name = forms.CharField(label="Name", max_length=120)
    email = forms.EmailField(label="Email")
    subject = forms.CharField(label="Subject", max_length=70)
    message = forms.CharField(label="Message", widget=forms.Textarea)

    def get_info(self) -> tuple[str, str]:
        """Formats form information to use in an email.

        Returns:
            (str, str): Strings for the subject and message of an eamil.
        """
        clean_data = super().clean()

        name = clean_data.get("name").strip()
        sender_email = clean_data.get("email")
        subject = clean_data.get("subject")

        msg = f'{name} with email {sender_email} said:\n"{subject}"\n\n{clean_data.get("message")}'

        return subject, msg

    def send(self):
        subject, msg = self.get_info()

        send_mail(
            subject=subject,
            message=msg,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.RECIPIENT_ADDRESS],
        )
