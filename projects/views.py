from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project
from .forms import ProjectForm
from django.contrib import messages
from django.contrib.auth.models import User


@login_required
def project_list(request):
    projects = Project.objects.filter(
        models.Q(lead=request.user) | models.Q(collaborators=request.user)
    ).distinct()
    return render(request, "projects/project_list.html", {"projects": projects})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, "projects/project_detail.html", {"project": project})

@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.lead = request.user
            project.save()
            form.save_m2m()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, "projects/project_form.html", {"form": form})

@login_required
def add_collaborator(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST" and project.lead == request.user:
        user_id = request.POST.get("user_id")
        project.collaborators.add(user_id)
    return redirect("projects:project_detail", pk=pk)

@login_required
def project_dashboard(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all() if hasattr(project, "tasks") else []
    return render(request, "projects/project_dashboard.html", {
        "project": project,
        "tasks": tasks,
    })

@login_required
def add_collaborator(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Only the project lead can add collaborators
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
