from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator

from .models import User
from .forms import UserRegistrationForm, UserLoginForm, UserEditForm

FILTER_FAVORITE_AUTHORS = "favorite_project_authors"
FILTER_COLLABORATORS = "project_collaborators"
FILTER_MY_PROJECT_FANS = "my_project_fans"
FILTER_MY_PROJECT_PARTICIPANTS = "my_project_participants"


def get_paginated_page(request, queryset, items_per_page=4):
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("project_list")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user = authenticate(email=email, password=form.cleaned_data.get("password"))
            if user:
                login(request, user)
                return redirect("project_list")
    else:
        form = UserLoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("project_list")


def user_details(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:user_details", user_id=request.user.id)
    else:
        form = UserEditForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


def user_list(request):
    participants_list = User.objects.all().order_by("id")
    active_filter = request.GET.get("filter")

    if active_filter and request.user.is_authenticated:
        if active_filter == FILTER_FAVORITE_AUTHORS:
            participants_list = participants_list.filter(
                owned_projects__in=request.user.favorites.all()
            ).distinct()
        elif active_filter == FILTER_COLLABORATORS:
            participants_list = participants_list.filter(
                owned_projects__participants=request.user
            ).distinct()
        elif active_filter == FILTER_MY_PROJECT_FANS:
            participants_list = participants_list.filter(
                favorites__in=request.user.owned_projects.all()
            ).distinct()
        elif active_filter == FILTER_MY_PROJECT_PARTICIPANTS:
            participants_list = participants_list.filter(
                participated_projects__owner=request.user
            ).distinct()

    page_obj = get_paginated_page(request, participants_list)

    return render(
        request,
        "users/participants.html",
        {"page_obj": page_obj, "active_filter": active_filter},
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:user_details", user_id=request.user.id)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "users/change_password.html", {"form": form})
