from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Project, Task, Event, ProjectDocument
from .forms import ProjectForm, TaskForm, EventForm, ProjectDocumentForm
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.http import HttpResponseForbidden

@login_required
def project_list(request):
    """Show all projects where the user is a lead or collaborator."""
    projects = Project.objects.filter(
        models.Q(lead=request.user) | models.Q(collaborators=request.user)
    ).distinct()
    return render(request, "projects/project_list.html", {"projects": projects})


@login_required
def project_detail(request, pk):
    """Display detailed view of a single project."""
    project = get_object_or_404(Project, pk=pk)
    return render(request, "projects/project_detail.html", {"project": project})


@login_required
def project_create(request):
    """Create a new project belonging to one or more of the user's companies."""
    if request.method == "POST":
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.lead = request.user
            project.save()
            form.save_m2m()  # ✅ Save M2M fields (collaborators, companies)
            messages.success(request, f"Project '{project.name}' created successfully.")
            return redirect("projects:project_list")
    else:
        form = ProjectForm(user=request.user)
    return render(request, "projects/project_create.html", {"form": form})

@login_required
def add_collaborator(request, pk):
    """Allow the project lead to add collaborators."""
    project = get_object_or_404(Project, pk=pk)

    if project.lead != request.user:
        messages.error(request, "You do not have permission to add collaborators.")
        return redirect("projects:project_detail", pk=pk)

    if request.method == "POST":
        username = request.POST.get("username")
        try:
            collaborator = User.objects.get(username=username)
            if collaborator == project.lead:
                messages.warning(request, "The project lead is already part of this project.")
            elif collaborator in project.collaborators.all():
                messages.info(request, f"{collaborator.username} is already a collaborator.")
            else:
                project.collaborators.add(collaborator)
                messages.success(request, f"{collaborator.username} has been added to the project.")
        except User.DoesNotExist:
            messages.error(request, "No user found with that username.")
        return redirect("projects:project_detail", pk=pk)

    return render(request, "projects/add_collaborator.html", {"project": project})


@login_required
def project_dashboard(request, pk):
    """Show a dedicated dashboard for the project with tasks and events."""
    project = get_object_or_404(Project, pk=pk)

    # Handle new Task submission
    if request.method == "POST":
        if "add_task" in request.POST:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                new_task = task_form.save(commit=False)
                new_task.project = project
                new_task.save()
        elif "add_event" in request.POST:
            event_form = EventForm(request.POST)
            if event_form.is_valid():
                new_event = event_form.save(commit=False)
                new_event.project = project
                new_event.save()
        return redirect("projects:project_dashboard", pk=project.pk)

    # Display data
    task_form = TaskForm()
    event_form = EventForm()
    tasks = project.tasks.order_by("completed", "due_date")
    events = project.events.order_by("start_date")

    return render(request, "projects/project_dashboard.html", {
        "project": project,
        "tasks": tasks,
        "events": events,
        "task_form": task_form,
        "event_form": event_form,
    })


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
            "start": e.start_date.isoformat(),
            "end": e.end_date.isoformat() if e.end_date else e.start_date.isoformat(),
            "description": e.description,
            "color": "#0d6efd",  # blue for events
        })

    # --- Tasks ---
    for t in project.tasks.all():
        if t.due_date:
            combined.append({
                "title": f"📝 {t.title}",
                "start": t.due_date.isoformat(),
                "end": t.due_date.isoformat(),
                "description": t.description or "Task due",
                "color": "#20c997" if not t.completed else "#198754",  # green when done
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

@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Only the lead can delete the project
    if project.lead != request.user:
        messages.error(request, "You do not have permission to delete this project.")
        return redirect("projects:project_detail", pk=pk)

    if request.method == "POST":
        project.delete()
        messages.success(request, f"Project '{project.name}' has been deleted successfully.")
        return redirect("projects:project_list")

    # Optional: render confirmation page if you want one
    return redirect("projects:project_detail", pk=pk)

@login_required
def add_document(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ProjectDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.project = project
            document.uploaded_by = request.user
            document.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect("projects:project_dashboard", pk=project.pk)
    else:
        form = ProjectDocumentForm()
    return render(request, "projects/add_document.html", {"form": form, "project": project})


@login_required
def delete_document(request, pk, doc_id):
    project = get_object_or_404(Project, pk=pk)
    document = get_object_or_404(ProjectDocument, pk=doc_id, project=project)

    if request.user == project.lead or request.user == document.uploaded_by:
        document.delete()
        messages.success(request, "Document deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this document.")

    return redirect("projects:project_dashboard", pk=project.pk)


@login_required
def view_document(request, pk, doc_id):
    project = get_object_or_404(Project, pk=pk)
    document = get_object_or_404(ProjectDocument, pk=doc_id, project=project)
    return render(request, "projects/view_document.html", {"project": project, "document": document})
