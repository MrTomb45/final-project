from django.urls import path

from . import views

urlpatterns = [
    path("list/", views.project_list, name="project_list"),
    path("favorites/", views.favorite_projects, name="favorite_projects"),
    path("create-project/", views.create_project, name="create_project"),
    path("<int:project_id>/", views.project_details, name="project_details"),
    path("<int:project_id>/edit/", views.edit_project, name="edit_project"),
    path(
        "<int:project_id>/toggle-favorite/",
        views.toggle_favorite,
        name="toggle_favorite",
    ),
    path("<int:project_id>/complete/", views.complete_project, name="complete_project"),
    path(
        "<int:project_id>/toggle-participate/",
        views.toggle_participate,
        name="toggle_participate",
    ),
]
