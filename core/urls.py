from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.work_item_list, name="work_item_list"),
    path("projects/<slug:project_slug>/", views.work_item_list, name="work_item_list_project"),
    path("users/", views.user_list, name="user_list"),
    path("monthly-etc/save/", views.save_monthly_etc, name="save_monthly_etc"),
    path("audit-log/", views.audit_log, name="audit_log"),
    path("baseline/", views.update_baseline, name="update_baseline"),
    path("export-excel/", views.export_excel, name="export_excel"),
    path("save-note/", views.save_note, name="save_note"),
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="core/password_change.html",
            success_url="/password-change/done/"
        ),
        name="password_change"
    ),
    path(
        "password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="core/password_change_done.html"
        ),
        name="password_change_done"
    ),
]