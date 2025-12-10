from django.db.models import Q

from dashboard.forms import TaskForm, EventForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET

from company.models import CompanyMembership
from dashboard.models import Task, Event
from teams.models import Team
from .forms import (
    ProjectForm,
    ProjectDocumentForm,
    InternalDocumentForm,
    AddManagerForm,
    AddMemberForm,
)
from .models import Project, ProjectDocument, ProjectMembership


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
@login_required
def project_events_json(request, pk):
    project = get_object_or_404(Project, pk=pk)

    combined = []

    # Events
    for e in project.events.all():
        combined.append({
            "title": f"📅 {e.title}",
            "start": e.start_datetime.isoformat(),
            "end": e.end_datetime.isoformat() if e.end_datetime else e.start_datetime.isoformat(),
            "description": e.content,
            "color": "#0d6efd",
        })

    # Tasks
    for t in project.tasks.all():
        if t.deadline:
            combined.append({
                "title": f"📝 {t.title}",
                "start": t.deadline.isoformat(),
                "end": t.deadline.isoformat(),
                "description": t.content,
                "color": "#198754" if t.status == "completed" else "#20c997",
            })

    return JsonResponse(combined, safe=False)


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
                    mem.role = "Manager"
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
                    mem.role = "Member"
                    mem.save()

            # ---------------------------------------
            # 4. Auto-add team members as collaborators (NEW)
            # ---------------------------------------
            if form.cleaned_data.get("auto_add_team_members") and project.team:

                for tm in project.team.memberships.all():

                    # Skip project lead
                    if tm.user == project.lead:
                        continue

                    # Map team → project roles
                    if tm.role == "Lead":
                        proj_role = "Manager"  # team lead becomes project manager
                    elif tm.role == "Manager":
                        proj_role = "Manager"
                    else:
                        proj_role = "Member"

                    mem, created = ProjectMembership.objects.get_or_create(
                        user=tm.user,
                        project=project,
                        defaults={"role": proj_role},
                    )

                    if not created:
                        mem.role = proj_role
                        mem.save()

            # ---------------------------------------
            # 5. Sync collaborators (unchanged)
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
        if "add_task" in request.POST:
            task_form = TaskForm(request.POST, user=request.user, project=project)
            if task_form.is_valid():
                new_task = task_form.save(commit=False)
                new_task.project = project
                new_task.save()
                task_form.save_m2m()
                messages.success(request, f"Task '{new_task.title}' created successfully.")
                return redirect("projects:project_dashboard", pk=project.pk)

        elif "add_event" in request.POST:
            event_form = EventForm(request.POST, user=request.user, project=project)
            if event_form.is_valid():
                new_event = event_form.save(commit=False)
                new_event.project = project
                new_event.save()
                event_form.save_m2m()
                messages.success(request, f"Event '{new_event.title}' created successfully.")
                return redirect("projects:project_dashboard", pk=project.pk)

    task_form = TaskForm(user=request.user, project=project)
    event_form = EventForm(user=request.user, project=project)

    # Display data
    tasks = project.tasks.order_by("deadline")
    events = project.events.order_by("start_datetime")

    return render(request, "projects/project_dashboard.html", {
        "title": f'{project.name} Dashboard',
        "project": project,
        "tasks": tasks,
        "events": events,
        "task_form": task_form,
        "event_form": event_form,
    })


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
    """Show a dedicated dashboard for the project."""
    project = get_object_or_404(Project, pk=pk)

    user_projects = Project.objects.filter(
        Q(lead=request.user) | Q(collaborators=request.user)
    ).distinct()

    task_form = TaskForm()
    event_form = EventForm()

    if request.method == "POST":
        if "add_task" in request.POST:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                t = task_form.save(commit=False)
                t.project = project
                t.save()
                return redirect("projects:project_dashboard", pk=pk)

        if "add_event" in request.POST:
            event_form = EventForm(request.POST)
            if event_form.is_valid():
                e = event_form.save(commit=False)
                e.project = project
                e.save()
                return redirect("projects:project_dashboard", pk=pk)

    return render(request, "projects/project_dashboard.html", {
        "project": project,
        "user_projects": user_projects,
        "project_tasks": project.tasks.order_by("deadline"),
        "project_events": project.events.order_by("start_datetime"),
        "project_documents": project.documents.order_by("-uploaded_at"),
        "task_form": task_form,
        "event_form": event_form
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


@login_required
def delete_project_task(request, project_pk, task_pk):
    project = get_object_or_404(Project, pk=project_pk)

    # Ensure the user belongs to the project
    if request.user not in project.collaborators.all() and request.user != project.lead:
        return HttpResponseForbidden("You are not allowed to delete tasks from this project.")

    task = get_object_or_404(Task, pk=task_pk, project=project)

    task.delete()
    return redirect("projects:project_dashboard", pk=project_pk)


@login_required
def delete_project_event(request, project_pk, event_pk):
    project = get_object_or_404(Project, pk=project_pk)

    # Ensure the user belongs to the project
    if request.user not in project.collaborators.all() and request.user != project.lead:
        return HttpResponseForbidden("You are not allowed to delete events from this project.")

    event = get_object_or_404(Event, pk=event_pk, project=project)

    event.delete()
    return redirect("projects:project_dashboard", pk=project_pk)


@require_GET
@login_required
def project_events_json(request, pk):
    """Return combined project events and task deadlines for calendar widget."""
    project = get_object_or_404(Project, pk=pk)

    combined = []

    # --- Events ---
    for e in project.events.all():
        combined.append({
            "title": f"📅 {e.title}",
            "start": e.start_datetime.isoformat(),
            "end": e.end_datetime.isoformat() if e.end_datetime else e.start_datetime.isoformat(),
            "description": e.content,
            "color": "#0d6efd",  # blue for events
        })

    # --- Tasks ---
    for t in project.tasks.all():
        if t.deadline:
            combined.append({
                "title": f"📝 {t.title}",
                "start": t.deadline.isoformat(),
                "end": t.deadline.isoformat(),
                "description": t.content or "Task due",
                "color": "#198754" if t.status == 'completed' else "#20c997",  # green when done
            })

    return JsonResponse(combined, safe=False)


@login_required
def remove_collaborator(request, pk, user_id):
    """Allow the project lead to remove collaborators from their project."""
    project = get_object_or_404(Project, pk=pk)

    # Permission check — only the project lead can remove collaborators
    if project.lead != request.user:
        messages.error(request, "You do not have permission to remove collaborators.")
        return redirect("projects:project_detail", pk=pk)

    try:
        collaborator = User.objects.get(pk=user_id)
        if collaborator not in project.collaborators.all():
            messages.warning(request, f"{collaborator.username} is not a collaborator in this project.")
        else:
            project.collaborators.remove(collaborator)
            messages.success(request, f"{collaborator.username} has been removed from the project.")
    except User.DoesNotExist:
        messages.error(request, "Collaborator not found.")

    return redirect("projects:project_detail", pk=pk)


@login_required
def remove_task(request, pk, task_id):
    """Allow project lead to delete a specific task."""
    project = get_object_or_404(Project, pk=pk)
    task = get_object_or_404(Task, pk=task_id, project=project)

    # Permission check — only the project lead can delete tasks
    if project.lead != request.user:
        messages.error(request, "You do not have permission to delete tasks.")
        return HttpResponseForbidden("Permission denied")

    task.delete()
    messages.success(request, f"Task '{task.title}' was deleted successfully.")
    return redirect("projects:project_dashboard", pk=pk)


@login_required
def remove_event(request, pk, event_id):
    """Allow project lead to delete a specific event."""
    project = get_object_or_404(Project, pk=pk)
    event = get_object_or_404(Event, pk=event_id, project=project)

    # Permission check — only project lead can delete events
    if project.lead != request.user:
        messages.error(request, "You do not have permission to delete events.")
        return HttpResponseForbidden("Permission denied")

    event.delete()
    messages.success(request, f"Event '{event.title}' was deleted successfully.")
    return redirect("projects:project_dashboard", pk=pk)
