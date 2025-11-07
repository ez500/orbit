from django.test import TestCase
from django.core.mail import send_mail


# Create your tests here.
class EmailTest(TestCase):
    def test_email_sending(self):
        response = send_mail(
            subject="Test Subject",
            message="Test Message",
            from_email="from@example.com",
            recipient_list=["to@example.com"],
        )
        self.assertEqual(response, 1)
