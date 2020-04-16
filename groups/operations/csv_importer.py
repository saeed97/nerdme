import codecs
import csv
import datetime
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from groups.models import group, groupList

log = logging.getLogger(__name__)


class CSVImporter:
    """Core upsert functionality for CSV import, for re-use by `import_csv` management command, web UI and tests.
    Supplies a detailed log of what was and was not imported at the end. See README for usage notes.
    """

    def __init__(self):
        self.errors = []
        self.upserts = []
        self.summaries = []
        self.line_count = 0
        self.upsert_count = 0

    def upsert(self, fileobj, as_string_obj=False):
        """Expects a file *object*, not a file path. This is important because this has to work for both
        the management command and the web uploader; the web uploader will pass in in-memory file
        with no path!

        Header row is:
        Title, Group, group List, Created Date, Due Date, Completed, Created By, Assigned To, Note, Priority
        """

        if as_string_obj:
            # fileobj comes from mgmt command
            csv_reader = csv.DictReader(fileobj)
        else:
            # fileobj comes from browser upload (in-memory)
            csv_reader = csv.DictReader(codecs.iterdecode(fileobj, "utf-8"))

        # DI check: Do we have expected header row?
        header = csv_reader.fieldnames
        expected = [
            "Title",
            "Group",
            "group List",
            "Created By",
            "Created Date",
            "Due Date",
            "Completed",
            "Assigned To",
            "Note",
            "Priority",
        ]
        if header != expected:
            self.errors.append(
                f"Inbound data does not have expected columns.\nShould be: {expected}"
            )
            return

        for row in csv_reader:
            self.line_count += 1

            newrow = self.validate_row(row)
            if newrow:
                # newrow at this point is fully validated, and all FK relations exist,
                # e.g. `newrow.get("Assigned To")`, is a Django User instance.
                assignee = newrow.get("Assigned To") if newrow.get("Assigned To") else None
                created_date = (
                    newrow.get("Created Date")
                    if newrow.get("Created Date")
                    else datetime.datetime.today()
                )
                due_date = newrow.get("Due Date") if newrow.get("Due Date") else None
                priority = newrow.get("Priority") if newrow.get("Priority") else None

                obj, created = group.objects.update_or_create(
                    created_by=newrow.get("Created By"),
                    group_list=newrow.get("group List"),
                    title=newrow.get("Title"),
                    defaults={
                        "assigned_to": assignee,
                        "completed": newrow.get("Completed"),
                        "created_date": created_date,
                        "due_date": due_date,
                        "note": newrow.get("Note"),
                        "priority": priority,
                    },
                )
                self.upsert_count += 1
                msg = (
                    f'Upserted group {obj.id}: "{obj.title}"'
                    f' in list "{obj.group_list}" (group "{obj.group_list.group}")'
                )
                self.upserts.append(msg)

        self.summaries.append(f"Processed {self.line_count} CSV rows")
        self.summaries.append(f"Upserted {self.upsert_count} rows")
        self.summaries.append(f"Skipped {self.line_count - self.upsert_count} rows")

        return {"summaries": self.summaries, "upserts": self.upserts, "errors": self.errors}

    def validate_row(self, row):
        """Perform data integrity checks and set default values. Returns a valid object for insertion, or False.
        Errors are stored for later display. Intentionally not broken up into separate validator functions because
        there are interdpendencies, such as checking for existing `creator` in one place and then using
        that creator for group membership check in others."""

        row_errors = []

        # #######################
        # group creator must exist
        if not row.get("Created By"):
            msg = f"Missing required group creator."
            row_errors.append(msg)

        creator = get_user_model().objects.filter(username=row.get("Created By")).first()
        if not creator:
            msg = f"Invalid group creator {row.get('Created By')}"
            row_errors.append(msg)

        # #######################
        # If specified, Assignee must exist
        assignee = None  # Perfectly valid
        if row.get("Assigned To"):
            assigned = get_user_model().objects.filter(username=row.get("Assigned To"))
            if assigned.exists():
                assignee = assigned.first()
            else:
                msg = f"Missing or invalid group assignee {row.get('Assigned To')}"
                row_errors.append(msg)

        # #######################
        # Group must exist
        try:
            target_group = Group.objects.get(name=row.get("Group"))
        except Group.DoesNotExist:
            msg = f"Could not find group {row.get('Group')}."
            row_errors.append(msg)
            target_group = None

        # #######################
        # group creator must be in the target group
        if creator and target_group not in creator.groups.all():
            msg = f"{creator} is not in group {target_group}"
            row_errors.append(msg)

        # #######################
        # Assignee must be in the target group
        if assignee and target_group not in assignee.groups.all():
            msg = f"{assignee} is not in group {target_group}"
            row_errors.append(msg)

        # #######################
        # group list must exist in the target group
        try:
            grouplist = groupList.objects.get(name=row.get("group List"), group=target_group)
            row["group List"] = grouplist
        except groupList.DoesNotExist:
            msg = f"group list {row.get('group List')} in group {target_group} does not exist"
            row_errors.append(msg)

        # #######################
        # Validate Dates
        datefields = ["Due Date", "Created Date"]
        for datefield in datefields:
            datestring = row.get(datefield)
            if datestring:
                valid_date = self.validate_date(datestring)
                if valid_date:
                    row[datefield] = valid_date
                else:
                    msg = f"Could not convert {datefield} {datestring} to valid date instance"
                    row_errors.append(msg)

        # #######################
        # Group membership checks have passed
        row["Created By"] = creator
        row["Group"] = target_group
        if assignee:
            row["Assigned To"] = assignee

        # Set Completed
        row["Completed"] = row["Completed"] == "Yes"

        # #######################
        if row_errors:
            self.errors.append({self.line_count: row_errors})
            return False

        # No errors:
        return row

    def validate_date(self, datestring):
        """Inbound date string from CSV translates to a valid python date."""
        try:
            date_obj = datetime.datetime.strptime(datestring, "%Y-%m-%d")
            return date_obj
        except ValueError:
            return False
