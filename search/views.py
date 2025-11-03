from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render

from accounts.models import Profile
from teams.models import Team
from company.models import Company
from projects.models import Project


@login_required
def search_results(request):
    query = request.GET.get("q", "").strip()

    # === USERS (Profiles) ===
    if not query:
        users = Profile.objects.all().order_by("id")
    else:
        # Step 1: Find matching users in the User model
        user_matches = User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        ).values_list("id", flat=True)

        # Step 2: Find matching profiles
        users = Profile.objects.filter(
            Q(user_id__in=user_matches)
            | Q(bio__icontains=query)
            | Q(location__icontains=query)
        ).order_by("id")

    # === TEAMS ===
    if not query:
        teams = Team.objects.all().order_by("id")
    else:
        teams = Team.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
        ).order_by("id")

    # === COMPANIES ===
    if not query:
        companies = Company.objects.all().order_by("id")
    else:
        companies = Company.objects.filter(
            Q(name__icontains=query)
            | Q(address__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
        ).order_by("id")

    # === PROJECTS ===
    if not query:
        projects = Project.objects.all().order_by("id")
    else:
        # Reuse user_matches/profile_matches from above
        user_matches = User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        ).values_list("id", flat=True)

        profile_matches = Profile.objects.filter(
            user_id__in=user_matches
        ).values_list("id", flat=True)

        projects = Project.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(lead_id__in=profile_matches)
            | Q(collaborators__in=profile_matches)
        ).distinct().order_by("id")

    # === Combine results for pagination ===
    queryset = list(users) + list(teams) + list(projects) #companies awaiting to be added
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "query": query,
        "users": users,
        "teams": teams,
        "companies": companies,
        "projects": projects,
        "page_obj": page_obj,
    }

    return render(request, "search/results.html", context)
