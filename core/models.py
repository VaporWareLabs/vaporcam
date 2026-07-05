from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.text import slugify
        
class Project(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    jira_sql = models.TextField(blank=True)
    jira_enabled = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name.split(" - ", 1)[0])
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class WorkItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="work_items")
    phase = models.CharField(max_length=100, blank=True)
    wbs_code = models.CharField(max_length=100, blank=True)
    feature = models.CharField(max_length=200)
    story = models.CharField(max_length=200, blank=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    baseline_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    etc_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    jira_key = models.CharField(max_length=50, blank=True, null=True, unique=True)
    jira_url = models.URLField(blank=True)
    jira_status = models.CharField(max_length=100, blank=True)
    jira_issue_type = models.CharField(max_length=100, blank=True)
    jira_summary = models.CharField(max_length=255, blank=True)
    
    feature_key = models.CharField(max_length=50, blank=True)
    feature_name = models.CharField(max_length=255, blank=True)
    feature_url = models.URLField(blank=True)
    
    charge_code = models.CharField(max_length=255, blank=True, null=True)

    @property
    def eac_hours(self):
        return self.actual_hours + self.etc_hours

    @property
    def variance_hours(self):
        return self.budget_hours - self.eac_hours

    @property
    def percent_complete(self):
        if (self.jira_status or "").lower() == "done" or (self.jira_status or "").lower() == "void":
            return 100
        return 0
        
    def __str__(self):
        return f"{self.wbs_code} - {self.feature}"

class WorkItemMonthlyValue(models.Model):
    work_item = models.ForeignKey(
        WorkItem,
        on_delete=models.CASCADE,
        related_name="monthly_values"
    )

    month = models.DateField()
    budget_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ("work_item", "month")
        ordering = ["month"]

class MonthlyETC(models.Model):
    work_item = models.ForeignKey("WorkItem", on_delete=models.CASCADE, related_name="monthly_etcs")
    month = models.DateField()
    etc_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ("work_item", "month")

class MonthlyETCChange(models.Model):
    work_item = models.ForeignKey(
        WorkItem,
        on_delete=models.CASCADE,
        related_name="etc_changes"
    )

    month = models.DateField(null=True, blank=True)
    
    old_etc_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    new_etc_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.work_item} "
            f"{self.old_etc_hours} → {self.new_etc_hours}"
        )
    
class WorkItemNote(models.Model):
    work_item = models.OneToOneField(
        WorkItem,
        on_delete=models.CASCADE,
        related_name="note"
    )

    note_text = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notes for {self.work_item.jira_key}"