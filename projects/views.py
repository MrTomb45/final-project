from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Project
from .forms import ProjectForm


def paginate_queryset(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def project_list(request):
    all_projects = Project.objects.all().order_by("-created_at")

    paginator = Paginator(all_projects, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        template_name="projects/project_list.html",
        context={"page_obj": page_obj},
    )


@login_required
def favorite_projects(request):
    favorites_list = request.user.favorites.all().order_by("-created_at")

    paginator = Paginator(favorites_list, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "projects/favorite_projects.html", {"page_obj": page_obj})


def project_details(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("project_details", project_id=project.id)
    else:
        form = ProjectForm()
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("project_details", project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": True}
    )


@login_required
def toggle_favorite(request, project_id):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=project_id)
        if project in request.user.favorites.all():
            request.user.favorites.remove(project)
            favorited = False
        else:
            request.user.favorites.add(project)
            favorited = True
        return JsonResponse({"status": "ok", "favorited": favorited})
    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def complete_project(request, project_id):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=project_id, owner=request.user)
        if project.status == "open":
            project.status = "closed"
            project.save()
            return JsonResponse({"status": "ok", "project_status": "closed"})
        return JsonResponse({"error": "Project is already closed"}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def toggle_participate(request, project_id):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=project_id)
        if request.user in project.participants.all():
            project.participants.remove(request.user)
            is_participant = False
        else:
            project.participants.add(request.user)
            is_participant = True
        return JsonResponse({"status": "ok", "participant": is_participant})

    return JsonResponse({"error": "Method not allowed"}, status=405)
