from django.contrib import admin
from .models import Project, WorkItem
from .models import MonthlyETCChange


@admin.register(MonthlyETCChange)
class MonthlyETCChangeAdmin(admin.ModelAdmin):

    list_display = (
        "work_item",
        "old_etc_hours",
        "new_etc_hours",
        "changed_by",
        "changed_at",
    )

    list_filter = (
        "changed_by",
        "changed_at",
    )

    search_fields = (
        "work_item__jira_key",
        "changed_by__username",
        "changed_by__email",
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
  list_display = ("name", "created_at")


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
  list_display = (
      "project",
      "phase",
      "wbs_code",
      "feature",
      "story",
      "assignee",
      "budget_hours",
      "actual_hours",
      "etc_hours",
      "updated_at",
  )
  list_filter = ("project", "phase", "assignee")
  search_fields = ("wbs_code", "feature", "story")

