from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from accounts.models import Profile
from teams.models import Team
from home.models import Company
from projects.models import Project


@login_required
def search_results(request):
    """
    Universal Search View
    ---------------------
    - Searches across Users (Profiles), Teams, Companies, and Projects.
    - If no query is entered, shows all items.
    - Handles related User fields correctly (user__username, etc.).
    """

    query = request.GET.get("q", "").strip()

    # If query is empty → show all
    if not query:
        users = Profile.objects.all().order_by("id")
        teams = Team.objects.all().order_by("id")
        companies = Company.objects.all().order_by("id")
        projects = Project.objects.all().order_by("id")

    else:
        # ===== Users (Profiles) =====
        users = Profile.objects.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__email__icontains=query)
            | Q(bio__icontains=query)
            | Q(location__icontains=query)
        ).order_by("id")

        # ===== Teams =====
        teams = Team.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by("id")

        # ===== Companies =====
        #companies = Company.objects.filter(
            #Q(name__icontains=query) | Q(description__icontains=query)
        #).order_by("id")

        # ===== Projects =====
        projects = Project.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(lead__user__username__icontains=query)
            | Q(lead__user__first_name__icontains=query)
            | Q(lead__user__last_name__icontains=query)
        ).order_by("id")

    # ===== Context for template =====
    context = {
        "query": query,
        "users": users,
        "teams": teams,
        "companies": companies,
        "projects": projects,
    }

    return render(request, "search/results.html", context)

