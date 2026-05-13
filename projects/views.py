from http import HTTPStatus

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Project
from .forms import ProjectForm


def paginate_queryset(request, queryset, per_page=6):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def project_list(request):
    all_projects = Project.objects.select_related("owner").order_by("-created_at")

    page_obj = paginate_queryset(request, all_projects, 6)

    return render(request, "projects/project_list.html", {"page_obj": page_obj})


@login_required
def favorite_projects(request):
    favorites_list = request.user.favorites.select_related("owner").order_by(
        "-created_at"
    )

    page_obj = paginate_queryset(request, favorites_list, 6)

    return render(request, "projects/favorite_projects.html", {"page_obj": page_obj})


def project_details(request, project_id):
    project = get_object_or_404(Project.objects.select_related("owner"), pk=project_id)
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

        is_favorite = request.user.favorites.filter(id=project.id).exists()

        if is_favorite:
            request.user.favorites.remove(project)
            favorited = False
        else:
            request.user.favorites.add(project)
            favorited = True
        return JsonResponse({"status": "ok", "favorited": favorited})

    return JsonResponse(
        {"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED
    )


@login_required
def complete_project(request, project_id):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=project_id, owner=request.user)

        if project.status == Project.STATUS_OPEN:
            project.status = Project.STATUS_CLOSED
            project.save()
            return JsonResponse({"status": "ok", "project_status": "closed"})

        return JsonResponse(
            {"error": "Project is already closed"}, status=HTTPStatus.BAD_REQUEST
        )

    return JsonResponse(
        {"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED
    )


@login_required
def toggle_participate(request, project_id):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=project_id)

        is_participant = project.participants.filter(id=request.user.id).exists()

        if is_participant:
            project.participants.remove(request.user)
            participant_status = False
        else:
            project.participants.add(request.user)
            participant_status = True

        return JsonResponse({"status": "ok", "participant": participant_status})

    return JsonResponse(
        {"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED
    )
