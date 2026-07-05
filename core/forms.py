from django import forms
from .models import WorkItem


class WorkItemForm(forms.ModelForm):
    class Meta:
        model = WorkItem
        fields = [
            "etc_hours",
            "actual_hours",
            "budget_hours",
            "story",
        ]