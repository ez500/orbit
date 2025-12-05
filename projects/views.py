# projects/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponseForbidden

from .models import Project, ProjectDocument, ProjectMembership
from .forms import (
    ProjectForm,
    ProjectDocumentForm,
    InternalDocumentForm,
    AddManagerForm,
    AddMemberForm,
)

from dashboard.forms import TaskForm, EventForm
from dashboard.models import Task, Event
from company.models import CompanyMembership
from teams.models import Team
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Only the lead can delete
    if request.user != project.lead:
        return HttpResponseForbidden("Only the project lead can delete this project.")

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect("projects:project_list")

    return render(request, "projects/confirm_delete.html", {"project": project})

# ------------------------------------------------------------
# EVENTS JSON (for dashboard calendar)
# ------------------------------------------------------------
@require_GET
@login_required
def project_events_json(request, pk):
    project = get_object_or_404(Project, pk=pk)

    events = project.events.all().values(
        "id",
        "title",
        "content",
        "start_datetime",
        "end_datetime",
        "pub_date",
        "team",
        "users",
        "project",
    )

    return JsonResponse(list(events), safe=False)

# ------------------------------------------------------------
# PROJECT LIST
# ------------------------------------------------------------
@login_required
def project_list(request):
    user_teams = Team.objects.filter(members=request.user)
    user_companies = CompanyMembership.objects.filter(user=request.user).values_list("company", flat=True)

    projects = Project.objects.filter(
        models.Q(lead=request.user)
        | models.Q(collaborators=request.user)
        | models.Q(team__in=user_teams)
        | models.Q(companies__in=user_companies)
    ).distinct()

    return render(request, "projects/project_list.html", {"projects": projects, "title": "My Projects"})


# ------------------------------------------------------------
# PROJECT DETAIL PAGE (SHOW ROLES)
# ------------------------------------------------------------
@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    memberships = project.memberships.select_related("user")

    acting_mem = project.memberships.filter(user=request.user).first()
    acting_role = acting_mem.role if acting_mem else ("Lead" if request.user == project.lead else None)

    context = {
        "project": project,
        "lead": project.lead,
        "memberships": memberships,
        "acting_role": acting_role,
    }

    return render(request, "projects/project_detail.html", context)


# ------------------------------------------------------------
# PROJECT CREATE
# ------------------------------------------------------------
@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():

            # ---------------------------------------
            # Create the project with the acting user as Lead
            # ---------------------------------------
            project = form.save(commit=False)
            project.lead = request.user
            project.save()
            form.save_m2m()

            # ---------------------------------------
            # Prepare safe role lists
            # Prevent duplicate membership creation
            # Prevent adding Lead as manager/member
            # ---------------------------------------
            selected_managers = form.cleaned_data.get("managers").exclude(id=request.user.id)
            selected_members = form.cleaned_data.get("members").exclude(id=request.user.id)

            # ---------------------------------------
            # 1. Create or update LEAD membership
            # ---------------------------------------
            lead_mem, created = ProjectMembership.objects.get_or_create(
                user=request.user,
                project=project,
                defaults={"role": "Lead"},
            )
            if not created:
                # ensure role is correct
                lead_mem.role = "Lead"
                lead_mem.save()

            # ---------------------------------------
            # 2. Create or update MANAGER memberships
            # ---------------------------------------
            for user in selected_managers:
                mem, created = ProjectMembership.objects.get_or_create(
                    user=user,
                    project=project,
                    defaults={"role": "Manager"},
                )
                if not created:
                    mem.role = "Manager"  # update if exists
                    mem.save()

            # ---------------------------------------
            # 3. Create or update MEMBER memberships
            # ---------------------------------------
            for user in selected_members:
                mem, created = ProjectMembership.objects.get_or_create(
                    user=user,
                    project=project,
                    defaults={"role": "Member"},
                )
                if not created and mem.role != "Lead":
                    mem.role = "Member"  # update if exists
                    mem.save()

            # ---------------------------------------
            # 4. Auto-sync collaborators
            # Managers + Members must be collaborators
            # Lead must NOT be collaborator (per your rule)
            # ---------------------------------------
            project.sync_roles()

            messages.success(request, f"Project '{project.name}' created successfully.")
            return redirect("projects:project_list")

    else:
        form = ProjectForm(user=request.user)

    return render(request, "projects/project_create.html", {"form": form})

# ------------------------------------------------------------
# ROLE MANAGEMENT HELPERS
# ------------------------------------------------------------

def can_manage_roles(project, acting_user):
    """Lead can manage all. Managers can manage all except the Lead."""
    if acting_user == project.lead:
        return "Lead"
    mem = project.memberships.filter(user=acting_user).first()
    return mem.role if mem else None


def is_manager(project, user):
    mem = project.memberships.filter(user=user).first()
    return mem and mem.role == "Manager"


def is_member(project, user):
    mem = project.memberships.filter(user=user).first()
    return mem and mem.role == "Member"


# ------------------------------------------------------------
# ADD MANAGER
# ------------------------------------------------------------
@login_required
def add_manager(request, pk):
    project = get_object_or_404(Project, pk=pk)
    acting_role = can_manage_roles(project, request.user)

    if acting_role not in ["Lead", "Manager"]:
        return HttpResponseForbidden("You do not have permission.")

    if request.method == "POST":
        form = AddManagerForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]

            # Block changing Lead
            if user == project.lead:
                messages.error(request, "Cannot modify the Lead.")
                return redirect("projects:project_detail", pk=pk)

            # Promote or create membership
            mem = project.memberships.filter(user=user).first()
            if mem:
                mem.role = "Manager"
                mem.save()
            else:
                ProjectMembership.objects.create(user=user, project=project, role="Manager")

            project.sync_roles()
            messages.success(request, f"{user.username} promoted to Manager.")
            return redirect("projects:project_detail", pk=pk)
    else:
        form = AddManagerForm()

    return render(request, "projects/add_manager.html", {"form": form, "project": project})


# ------------------------------------------------------------
# ADD MEMBER
# ------------------------------------------------------------
@login_required
def add_member(request, pk):
    project = get_object_or_404(Project, pk=pk)
    acting_role = can_manage_roles(project, request.user)

    if acting_role not in ["Lead", "Manager"]:
        return HttpResponseForbidden("You do not have permission.")

    if request.method == "POST":
        form = AddMemberForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]

            if user == project.lead:
                messages.error(request, "Lead cannot be added as Member.")
                return redirect("projects:project_detail", pk=pk)

            mem = project.memberships.filter(user=user).first()
            if mem:
                mem.role = "Member"
                mem.save()
            else:
                ProjectMembership.objects.create(user=user, project=project, role="Member")

            project.sync_roles()
            messages.success(request, f"{user.username} added as Member.")
            return redirect("projects:project_detail", pk=pk)
    else:
        form = AddMemberForm()

    return render(request, "projects/add_member.html", {"form": form, "project": project})


# ------------------------------------------------------------
# PROMOTE (Member → Manager)
# ------------------------------------------------------------
@login_required
def promote_member(request, pk, user_id):
    project = get_object_or_404(Project, pk=pk)
    target = get_object_or_404(User, pk=user_id)

    acting_role = project.get_user_role(request.user)
    target_role = project.get_user_role(target)

    # Manager/Lead can promote
    if acting_role not in ["Lead", "Manager"]:
        messages.error(request, "You do not have permission to promote users.")
        return redirect("projects:project_detail", pk=pk)

    # Cannot promote Lead
    if target_role == "Lead":
        messages.error(request, "Lead cannot be promoted.")
        return redirect("projects:project_detail", pk=pk)

    membership = ProjectMembership.objects.get(project=project, user=target)
    membership.role = "Manager"
    membership.save()

    project.sync_roles()

    messages.success(request, f"{target.username} is now a Manager.")
    return redirect("projects:project_detail", pk=pk)

# ------------------------------------------------------------
# DEMOTE (Manager → Member)
# ------------------------------------------------------------
@login_required
def demote_manager(request, pk, user_id):
    project = get_object_or_404(Project, pk=pk)
    target = get_object_or_404(User, pk=user_id)

    acting_role = project.get_user_role(request.user)  
    target_role = project.get_user_role(target)

    # ------------------------------
    # BLOCK SELF-DEMOTION
    # ------------------------------
    if request.user.id == target.id:
        messages.error(request, "You cannot demote yourself.")
        return redirect("projects:project_detail", pk=pk)

    # ------------------------------
    # Only Lead can demote Managers
    # ------------------------------
    if acting_role != "Lead":
        messages.error(request, "Only the project lead can demote a manager.")
        return redirect("projects:project_detail", pk=pk)

    # ------------------------------
    # Lead cannot be demoted
    # ------------------------------
    if target_role == "Lead":
        messages.error(request, "The project lead cannot be demoted.")
        return redirect("projects:project_detail", pk=pk)

    # ------------------------------
    # Perform Demotion → Manager → Member
    # ------------------------------
    membership = ProjectMembership.objects.get(project=project, user=target)
    membership.role = "Member"
    membership.save()

    project.sync_roles()

    messages.success(request, f"{target.username} has been demoted to Member.")
    return redirect("projects:project_detail", pk=pk)

# ------------------------------------------------------------
# REMOVE USER FROM PROJECT
# ------------------------------------------------------------
@login_required
def remove_user(request, pk, user_id):
    project = get_object_or_404(Project, pk=pk)
    acting_role = can_manage_roles(project, request.user)

    if acting_role not in ["Lead", "Manager"]:
        return HttpResponseForbidden("No permission.")

    target_user = get_object_or_404(User, pk=user_id)

    if target_user == project.lead:
        messages.error(request, "Cannot remove the Lead.")
        return redirect("projects:project_detail", pk=pk)

    membership = project.memberships.filter(user=target_user).first()
    if membership:
        membership.delete()

    project.sync_roles()
    messages.success(request, f"{target_user.username} removed from project.")
    return redirect("projects:project_detail", pk=pk)


# ------------------------------------------------------------
# DASHBOARD & OTHER EXISTING LOGIC BELOW (unchanged)
# ------------------------------------------------------------

@login_required
def project_dashboard(request, pk):
    project = get_object_or_404(Project, pk=pk)

    user_teams = Team.objects.filter(members=request.user)
    user_companies = CompanyMembership.objects.filter(user=request.user).values_list("company", flat=True)

    user_projects = Project.objects.filter(
        models.Q(lead=request.user)
        | models.Q(collaborators=request.user)
        | models.Q(team__in=user_teams)
        | models.Q(companies__in=user_companies)
    ).distinct()

    if request.method == "POST":
        if "add_task" in request.POST:
            form = TaskForm(request.POST)
            if form.is_valid():
                t = form.save(commit=False)
                t.project = project
                t.save()

        elif "add_event" in request.POST:
            form = EventForm(request.POST)
            if form.is_valid():
                e = form.save(commit=False)
                e.project = project
                e.save()

        return redirect("projects:project_dashboard", pk=project.pk)

    task_form = TaskForm()
    event_form = EventForm()

    return render(request, "projects/project_dashboard.html", {
        "project": project,
        "tasks": project.tasks.order_by("status", "deadline"),
        "events": project.events.order_by("start_datetime"),
        "task_form": task_form,
        "event_form": event_form,
        "user_projects": user_projects,
    })


# ------------------------------------------------------------
# DOCUMENT VIEWS (unchanged)
# ------------------------------------------------------------

@login_required
def add_document(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ProjectDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.project = project
            doc.uploaded_by = request.user
            doc.doc_type = "file"
            doc.save()

            messages.success(request, "File uploaded.")
            return redirect("projects:project_dashboard", pk=pk)
    else:
        form = ProjectDocumentForm()

    return render(request, "projects/add_document.html", {"form": form, "project": project})


@login_required
def create_internal_document(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = InternalDocumentForm(request.POST)
        if form.is_valid():
            new_doc = form.save(commit=False)
            new_doc.project = project
            new_doc.uploaded_by = request.user
            new_doc.doc_type = "internal"
            new_doc.save()

            messages.success(request, "Document created.")
            return redirect("projects:edit_internal_document", doc_id=new_doc.pk)
    else:
        form = InternalDocumentForm()

    return render(request, "projects/create_internal_document.html", {"form": form, "project": project})


@login_required
def edit_internal_document(request, doc_id):
    doc = get_object_or_404(ProjectDocument, pk=doc_id, doc_type="internal")

    if request.method == "POST":
        form = InternalDocumentForm(request.POST, instance=doc)
        if form.is_valid():
            form.save()
            messages.success(request, "Document saved.")
    else:
        form = InternalDocumentForm(instance=doc)

    return render(request, "projects/edit_internal_document.html", {"form": form, "doc": doc})


@login_required
def view_internal_document(request, doc_id):
    doc = get_object_or_404(ProjectDocument, pk=doc_id, doc_type="internal")
    return render(request, "projects/view_internal_document.html", {"doc": doc})


@login_required
def view_document(request, pk, doc_id):
    project = get_object_or_404(Project, pk=pk)
    document = get_object_or_404(ProjectDocument, pk=doc_id, project=project)

    if document.doc_type == "file":
        return render(request, "projects/view_document.html", {"project": project, "document": document})

    return redirect("projects:view_internal_document", doc_id=document.pk)
