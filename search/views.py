from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from accounts.models import Profile
from home.models import Company, Project
from teams.models import Team

from .forms import SearchForm

VISIBLE_PUBLIC = "PUBLIC"


@login_required
def search_view(request):
    form = SearchForm(request.GET or None)

    q = ""
    team_filter = None
    company_filter = None
    project_filter = None

    if form.is_valid():
        q = form.cleaned_data.get("q") or ""
        team_filter = form.cleaned_data.get("team")
        company_filter = form.cleaned_data.get("company")
        project_filter = form.cleaned_data.get("project")

    text_q_users = Q()
    text_q_profiles = Q()
    text_q_teams = Q()
    text_q_companies = Q()
    text_q_projects = Q()

    if q:
        text_q_users = (
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
        )
        text_q_profiles = Q(bio__icontains=q) | Q(location__icontains=q) | Q(website__icontains=q)
        text_q_teams = Q(name__icontains=q) | Q(description__icontains=q)
        text_q_companies = Q(name__icontains=q) | Q(address__icontains=q)
        text_q_projects = Q(name__icontains=q) | Q(description__icontains=q)

    base_profiles = Profile.objects.select_related("user").all()
    visible_profiles = base_profiles.filter(Q(visibility=VISIBLE_PUBLIC) | Q(user=request.user))

    if team_filter:
        visible_profiles = visible_profiles.filter(teams__id=team_filter.id)
    if company_filter:
        visible_profiles = visible_profiles.filter(companies__id=company_filter.id)
    if project_filter:
        visible_profiles = visible_profiles.filter(projects__id=project_filter.id)

    profiles_qs = visible_profiles.filter(text_q_profiles | Q(user__in=User.objects.filter(text_q_users))).distinct()

    teams_qs = Team.objects.filter(text_q_teams)
    if company_filter:
        teams_qs = teams_qs.filter(members__profile__companies__id=company_filter.id)
    if project_filter:
        teams_qs = teams_qs.filter(members__profile__projects__id=project_filter.id)
    if team_filter:
        teams_qs = teams_qs.filter(id=team_filter.id)
    teams_qs = teams_qs.distinct()

    companies_qs = Company.objects.filter(text_q_companies)
    if team_filter:
        companies_qs = companies_qs.filter(users__overlap=list(User.objects.filter(teams__id=team_filter.id).values_list("id", flat=True)))
    if project_filter:
        companies_qs = companies_qs.filter(id=project_filter.company)
    companies_qs = companies_qs.distinct()

    projects_qs = Project.objects.filter(text_q_projects)
    if company_filter:
        projects_qs = projects_qs.filter(company=company_filter.id)
    if team_filter:
        projects_qs = projects_qs.filter(users__overlap=list(User.objects.filter(teams__id=team_filter.id).values_list("id", flat=True)))
    if project_filter:
        projects_qs = projects_qs.filter(id=project_filter.id)
    projects_qs = projects_qs.distinct()

    def paginate(queryset, key, per_page=10):
        paginator = Paginator(queryset, per_page)
        page_num = request.GET.get(f"page_{key}")
        return paginator.get_page(page_num)

    context = {
        "form": form,
        "q": q,
        "profiles_page": paginate(profiles_qs, "profiles"),
        "teams_page": paginate(teams_qs, "teams"),
        "companies_page": paginate(companies_qs, "companies"),
        "projects_page": paginate(projects_qs, "projects"),
    }

    return render(request, "search/results.html", context)

