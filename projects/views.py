from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from dashboard.models import Task, Event
from .models import Project, ProjectDocument
from .forms import ProjectForm, ProjectDocumentForm, InternalDocumentForm
from dashboard.forms import TaskForm, EventForm
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.http import HttpResponseForbidden
from company.models import CompanyMembership
from teams.models import Team


# --------------------------------------------------------
# Project List
# --------------------------------------------------------
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


# --------------------------------------------------------
# Project Detail
# --------------------------------------------------------
@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, "projects/project_detail.html", {"project": project})


# --------------------------------------------------------
# Project Create
# --------------------------------------------------------
@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.lead = request.user
            project.save()
            form.save_m2m()
            messages.success(request, f"Project '{project.name}' created successfully.")
            return redirect("projects:project_list")
    else:
        form = ProjectForm(user=request.user)

    return render(request, "projects/project_create.html", {"form": form})

# --------------------------------------------------------
# Project delete
# --------------------------------------------------------
@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.lead != request.user:
        messages.error(request, "You do not have permission to delete this project.")
        return redirect("projects:project_detail", pk=pk)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect("projects:project_list")

    return redirect("projects:project_detail", pk=pk)

# --------------------------------------------------------
# Add Collaborator
# --------------------------------------------------------
@login_required
def add_collaborator(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.lead != request.user:
        messages.error(request, "You do not have permission to add collaborators.")
        return redirect("projects:project_detail", pk=pk)

    if request.method == "POST":
        username = request.POST.get("username")
        try:
            collaborator = User.objects.get(username=username)
            if collaborator == project.lead:
                messages.warning(request, "The lead is already part of this project.")
            elif collaborator in project.collaborators.all():
                messages.info(request, f"{collaborator.username} is already a collaborator.")
            else:
                project.collaborators.add(collaborator)
                messages.success(request, f"{collaborator.username} added.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, "projects/add_collaborator.html", {"project": project})


# --------------------------------------------------------
# Project Dashboard
# --------------------------------------------------------
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


# --------------------------------------------------------
# Calendar JSON Endpoint
# --------------------------------------------------------
@require_GET
@login_required
def project_events_json(request, pk):
    project = get_object_or_404(Project, pk=pk)
    combined = []

    for e in project.events.all():
        combined.append({
            "title": f"📅 {e.title}",
            "start": e.start_datetime.isoformat(),
            "end": e.end_datetime.isoformat() if e.end_datetime else e.start_datetime.isoformat(),
            "description": e.content,
            "color": "#0d6efd",
        })

    for t in project.tasks.all():
        if t.deadline:
            combined.append({
                "title": f"📝 {t.title}",
                "start": t.deadline.isoformat(),
                "end": t.deadline.isoformat(),
                "description": t.content or "Task due",
                "color": "#198754" if t.status == "completed" else "#20c997",
            })

    return JsonResponse(combined, safe=False)


# --------------------------------------------------------
# Remove collaborator
# --------------------------------------------------------
@login_required
def remove_collaborator(request, pk, user_id):
    project = get_object_or_404(Project, pk=pk)

    if project.lead != request.user:
        return HttpResponseForbidden("Permission denied.")

    collaborator = get_object_or_404(User, pk=user_id)
    project.collaborators.remove(collaborator)
    messages.success(request, f"{collaborator.username} removed.")

    return redirect("projects:project_detail", pk=pk)


# --------------------------------------------------------
# Remove Task
# --------------------------------------------------------
@login_required
def remove_task(request, pk, task_id):
    project = get_object_or_404(Project, pk=pk)
    task = get_object_or_404(Task, pk=task_id, project=project)

    if project.lead != request.user:
        return HttpResponseForbidden("Permission denied.")

    task.delete()
    messages.success(request, "Task deleted.")
    return redirect("projects:project_dashboard", pk=pk)


# --------------------------------------------------------
# Remove Event
# --------------------------------------------------------
@login_required
def remove_event(request, pk, event_id):
    project = get_object_or_404(Project, pk=pk)
    event = get_object_or_404(Event, pk=event_id, project=project)

    if project.lead != request.user:
        return HttpResponseForbidden("Permission denied.")

    event.delete()
    messages.success(request, "Event deleted.")
    return redirect("projects:project_dashboard", pk=pk)


# --------------------------------------------------------
# Uploaded File Document
# --------------------------------------------------------
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


# --------------------------------------------------------
# Create Internal Document
# --------------------------------------------------------
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

    return render(request, "projects/create_internal_document.html", {
        "form": form,
        "project": project
    })


# --------------------------------------------------------
# Edit Internal Document
# --------------------------------------------------------
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

    return render(request, "projects/edit_internal_document.html", {
        "form": form,
        "doc": doc,
    })


# --------------------------------------------------------
# View Internal Document
# --------------------------------------------------------
@login_required
def view_internal_document(request, doc_id):
    doc = get_object_or_404(ProjectDocument, pk=doc_id, doc_type="internal")

    return render(request, "projects/view_internal_document.html", {
        "doc": doc
    })

@login_required
def view_document(request, pk, doc_id):
    project = get_object_or_404(Project, pk=pk)
    document = get_object_or_404(ProjectDocument, pk=doc_id, project=project)

    # Uploaded files only
    if document.doc_type == "file":
        return render(request, "projects/view_document.html", {
            "project": project,
            "document": document,
        })

    # Internal docs use separate view
    return redirect("projects:view_internal_document", doc_id=document.pk)

# --------------------------------------------------------
# Delete Document (File or Internal)
# --------------------------------------------------------
@login_required
def delete_document(request, pk, doc_id):
    project = get_object_or_404(Project, pk=pk)
    doc = get_object_or_404(ProjectDocument, pk=doc_id, project=project)

    if request.user != project.lead and request.user != doc.uploaded_by:
        messages.error(request, "You do not have permission.")
        return redirect("projects:project_dashboard", pk=pk)

    doc.delete()
    messages.success(request, "Document deleted.")
    return redirect("projects:project_dashboard", pk=pk)
