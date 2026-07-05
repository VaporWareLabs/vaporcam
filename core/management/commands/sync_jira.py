import os

import requests
from dotenv import load_dotenv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from core.models import Project, WorkItem


class Command(BaseCommand):
    help = "Sync Jira stories/tasks into WorkItem records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--project",
            help="Project slug to sync, example: ba0999",
        )

    def handle(self, *args, **options):
        load_dotenv()

        base_url = os.getenv("JIRA_BASE_URL", "").rstrip("/")
        pat = os.getenv("JIRA_PAT")

        if not all([base_url, pat]):
            raise CommandError("Missing JIRA_BASE_URL or JIRA_PAT in .env")

        project_slug = options.get("project")

        projects = Project.objects.filter(jira_enabled=True)

        if project_slug:
            projects = projects.filter(slug=project_slug)

        if not projects.exists():
            raise CommandError("No Jira-enabled projects found.")

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {pat}",
        }

        for project in projects:
            if not project.jira_sql:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {project.name}: no jira_jql configured."
                    )
                )
                continue

            self.sync_project(base_url, headers, project)

    def sync_project(self, base_url, headers, project):
        jql = project.jira_sql

        url = f"{base_url}/rest/api/2/search"

        fields = [
            "summary",
            "status",
            "issuetype",
            "assignee",
            "customfield_10006",
            "customfield_10002",
            "customfield_10101",
        ]

        start_at = 0
        max_results = 100

        created_count = 0
        updated_count = 0
        deleted_count = 0
        imported_keys = set()

        self.stdout.write(f"Syncing {project.name}...")

        while True:
            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results,
                "fields": ",".join(fields),
            }

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=30,
            )

            if response.status_code != 200:
                raise CommandError(
                    f"Jira request failed for {project.name}: "
                    f"{response.status_code} {response.text}"
                )

            data = response.json()
            issues = data.get("issues", [])
            total = data.get("total", 0)

            if not issues:
                break

            for issue in issues:
                key = issue["key"]
                fields_data = issue["fields"]

                story_points = fields_data.get("customfield_10002") or 0
                charge_code = fields_data.get("customfield_10101") or ""
                imported_keys.add(key)

                summary = fields_data.get("summary", "")
                status = fields_data.get("status", {}).get("name", "")
                issue_type = fields_data.get("issuetype", {}).get("name", "")
                assignee_data = fields_data.get("assignee")

                feature_key = self.get_feature_key(fields_data)

                if feature_key:
                    feature_summary = self.get_issue_summary(
                        base_url,
                        headers,
                        feature_key,
                    )
                    feature_name = feature_summary or feature_key
                    feature_url = f"{base_url}/browse/{feature_key}"
                else:
                    feature_name = "Unassigned Feature"
                    feature_url = ""

                assignee = None
                if assignee_data:
                    display_name = assignee_data.get("displayName", "")
                    email_address = assignee_data.get("emailAddress", "")
                    username = email_address or display_name or key

                    assignee, _ = User.objects.get_or_create(
                        username=username,
                        defaults={
                            "first_name": display_name,
                            "email": email_address,
                        },
                    )

                _, created = WorkItem.objects.update_or_create(
                    jira_key=key,
                    defaults={
                        "project": project,
                        "wbs_code": key,
                        "feature": feature_name,
                        "story": summary,
                        "assignee": assignee,
                        "jira_url": f"{base_url}/browse/{key}",
                        "jira_status": status,
                        "jira_issue_type": issue_type,
                        "jira_summary": summary,
                        "feature_key": feature_key,
                        "feature_name": feature_name,
                        "feature_url": feature_url,
                        "budget_hours": story_points,
                        "charge_code": charge_code,
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            start_at += max_results

            if start_at >= total:
                break

        if imported_keys:
            deleted_count, _ = (
                WorkItem.objects
                .filter(project=project, jira_key__isnull=False)
                .exclude(jira_key__in=imported_keys)
                .delete()
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"{project.name} sync complete. "
                f"Created: {created_count}, "
                f"Updated: {updated_count}, "
                f"Deleted: {deleted_count}"
            )
        )

    def get_issue_summary(self, base_url, headers, issue_key):
        url = f"{base_url}/rest/api/2/issue/{issue_key}"
        params = {"fields": "summary"}

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("fields", {}).get("summary", "")

    def get_feature_key(self, fields_data):
        feature_data = fields_data.get("customfield_10006")

        if isinstance(feature_data, str) and feature_data.strip():
            return feature_data.strip()

        if isinstance(feature_data, dict):
            key = feature_data.get("key")
            if isinstance(key, str) and key.strip():
                return key.strip()

        return ""