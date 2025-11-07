from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Project
from .forms import ProjectForm


@login_required
def project_list(request):
    """Show all projects where the user is a lead or collaborator."""
    projects = Project.objects.filter(
        models.Q(lead=request.user) | models.Q(collaborators=request.user)
    ).distinct()
    return render(request, "projects/project_list.html", {"projects": projects, "title": "My Projects"})


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
            form.save_m2m()
            messages.success(request, "Project created successfully.")
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm(user=request.user)
    return render(request, "projects/project_form.html", {"form": form})


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
    """Show a dedicated dashboard for the project."""
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all() if hasattr(project, "tasks") else []
    return render(request, "projects/project_dashboard.html", {
        "project": project,
        "tasks": tasks,
    })

