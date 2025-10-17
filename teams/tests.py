from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Team, TeamMembership

User = get_user_model()

class MyTeamsTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user(username="Admin", password="1123456")
        self.t1 = Team.objects.create(name="A")
        self.t2 = Team.objects.create(name="B")
        TeamMembership.objects.create(user=self.u, team=self.t1, role="Member")

    def test_requires_login(self):
        resp = self.client.get(reverse("teams:my_teams"))
        self.assertEqual(resp.status_code, 302)

    def test_lists_only_my_teams(self):
        self.client.login(username="Admin", password="1123456")
        resp = self.client.get(reverse("teams:my_teams"))
        self.assertContains(resp, "A")
        self.assertNotContains(resp, "B")

    def test_search(self):
        self.client.login(username="Admin", password="1123456")
        resp = self.client.get(reverse("teams:my_teams") + "?q=A")
        self.assertContains(resp, "A")
