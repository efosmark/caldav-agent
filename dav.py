from typing import Annotated, Any, List, Optional, cast
import caldav
import icalendar
from datetime import datetime
from functools import lru_cache
from langchain_core.tools import InjectedToolArg, tool, BaseTool

import vobject

class CalendarNotFound(Exception):
    """Raised when a calendar is not found by ID."""
    pass

class TaskNotFound(Exception):
    """Raised when a task is not found by UID in a calendar."""
    pass

def serialize_ical_todo(input_todo: icalendar.Todo) -> dict[str, Any]:
    """Serialize an icalendar.Todo object to a dictionary, removing tzinfo and microseconds from datetimes.

    Args:
        input_todo (icalendar.Todo): The iCalendar VTODO object to serialize.

    Returns:
        dict[str, Any]: A dictionary representation of the VTODO.
    """
    result = dict()
    for k, v in input_todo.items():
        if k.startswith('X') or not v:
            continue
        if isinstance(v, icalendar.vText):
            result[k] = str(v)
        elif isinstance(v, icalendar.vDDDTypes):
            dt = cast(datetime, v.dt)
            if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            if hasattr(dt, 'microsecond'):
                dt = dt.replace(microsecond=0)
            result[k] = dt.isoformat(" ") if isinstance(dt, datetime) else dt.isoformat()
        else:
            result[k] = v
    return result

class TaskDAVClient(caldav.DAVClient):
    """A DAV client for managing tasks in CalDAV calendars."""

    def update_field(self, task:caldav.Todo, field_name, field_value):
        v = cast(vobject.base.Component, task.vobject_instance)
        if field_value is None:
            if hasattr(v.vtodo, field_name):
                delattr(v.vtodo, field_name)
        else:
            getattr(v.vtodo, field_name).value = field_value

    @lru_cache()
    def get_calendars_by_id(self) -> dict[str, caldav.Calendar]:
        """Return a dictionary of calendars by their ID.

        Returns:
            dict[str, caldav.Calendar]: A dictionary mapping calendar IDs to Calendar objects.
        """
        return dict(
            (c.id, c)
            for c in self.principal().calendars()
            if c.id is not None
        )

    def get_calendar_by_id(self, calendar_id: str) -> caldav.Calendar:
        """Get a calendar by its ID or raise CalendarNotFound.

        Args:
            calendar_id: The ID of the calendar to retrieve.

        Returns:
            caldav.Calendar: The calendar associated with the ID.

        Raises:
            CalendarNotFound: If the calendar ID is not found.
        """
        all_calendars = self.get_calendars_by_id()
        if calendar_id in all_calendars:
            return all_calendars[calendar_id]
        raise CalendarNotFound(f"Argument `calendar_id` must be one of: {', '.join(all_calendars.keys())}")

    def task_get_by_id(self: Annotated['TaskDAVClient', InjectedToolArg], calendar_id: str, task_id: str) -> caldav.Todo:
        """Retrieve a task from a calendar by its UID.

        Args:
            calendar_id: The ID of the calendar to search.
            task_id: The UID of the task to retrieve.

        Returns:
            caldav.Todo: The requested task object.

        Raises:
            TaskNotFound: If no task with the given ID exists in the calendar.
        """
        calendar = self.get_calendar_by_id(calendar_id)
        try:
            return cast(caldav.Todo, calendar.todo_by_uid(task_id))
        except caldav.error.NotFoundError:
            raise TaskNotFound(f"No task exists with ID {task_id} inside calendar with ID {calendar_id}.")

    def calendar_list_ids(self: Annotated['TaskDAVClient', InjectedToolArg]) -> List[str]:
        """List all accessible calendar IDs.

        Args:
            None

        Returns:
            List[str]: A list of calendar identifiers.
        """
        return [*self.get_calendars_by_id().keys()]

    def task_add_to_calendar(self: Annotated['TaskDAVClient', InjectedToolArg], calendar_id: str, summary: str, priority: Optional[int] = 5, due: Optional[datetime] = None) -> dict[str, Any]:
        """Add a new task (VTODO component) to the specified calendar.

        Args:
            calendar_id: The name of the calendar.
            summary: The summary/title of the task.
            priority: The priority of the task (default 5).
            due: The due date/time for the task.

        Returns:
            dict[str, Any]: The serialized task.
        """
        calendar = self.get_calendar_by_id(calendar_id)
        todo = icalendar.Todo()
        todo.add('summary', summary)
        if priority is not None:
            todo.add('priority', priority)
        if due:
            todo.add('due', due)
        calendar.add_todo(todo.to_ical().decode())
        return serialize_ical_todo(todo)

    def task_mark_complete(self: Annotated['TaskDAVClient', InjectedToolArg], calendar_id: str, task_id: str) -> None:
        """Mark the task as complete.

        Args:
            calendar_id: Calendar ID.
            task_id: Task ID (uid).

        Returns:
            None
        """
        task = self.task_get_by_id(calendar_id, task_id)
        task.complete()
        task.save()

    def task_mark_incomplete(self: Annotated['TaskDAVClient', InjectedToolArg], calendar_id: str, task_id: str) -> None:
        """Mark a previously completed task as incomplete.

        Args:
            calendar_id: Calendar ID.
            task_id: Task ID (uid).

        Returns:
            None
        """
        task = self.task_get_by_id(calendar_id, task_id)
        task.uncomplete()
        task.save()

    def task_update_summary(self: Annotated['TaskDAVClient', InjectedToolArg], calendar_id: str, task_id: str, summary: str) -> None:
        """Set the summary (title) of the task.

        Args:
            calendar_id: Calendar ID.
            task_id: Task ID (uid).
            summary: The summarized description of the task.

        Returns:
            None
        """
        task = self.task_get_by_id(calendar_id, task_id)
        self.update_field(task, 'summary', summary)
        task.save()

    def task_update_priority(self: Annotated['TaskDAVClient', InjectedToolArg], calendar_id: str, task_id: str, priority: Optional[int]) -> None:
        """Set the priority of the task.

        Args:
            calendar_id: Calendar ID.
            task_id: Task ID (uid).
            priority: The numeric priority. If set to None, the task is marked as unprioritized.

        Returns:
            None
        """
        task = self.task_get_by_id(calendar_id, task_id)
        self.update_field(task, 'priority', priority)
        task.save()

    def task_update_due_date(self: Annotated['TaskDAVClient', InjectedToolArg], calendar_id: str, task_id: str, due_date: Optional[datetime]) -> None:
        """Set the due date of the task.

        Args:
            calendar_id: Calendar ID.
            task_id: Task ID (uid).
            due_date: The due-date. If None is specified, the due date is removed.

        Returns:
            None
        """
        task = self.task_get_by_id(calendar_id, task_id)
        self.update_field(task, 'due_date', due_date)
        task.save()

    def task_update_description(self: Annotated['TaskDAVClient', InjectedToolArg], calendar_id: str, task_id: str, description: Optional[str]) -> None:
        """Set the task description.

        Args:
            calendar_id: Calendar ID.
            task_id: Task ID (uid).
            description: The description to the task.

        Returns:
            None
        """
        task = self.task_get_by_id(calendar_id, task_id)
        self.update_field(task, 'description', description)
        task.save()

    def task_update_start_date(self: Annotated['TaskDAVClient', InjectedToolArg], calendar_id: str, task_id: str, dtstart: Optional[datetime]) -> None:
        """Set when the task started.

        Args:
            calendar_id: Calendar ID.
            task_id: Task ID (uid).
            dtstart: The starting date and time for the task.

        Returns:
            None
        """
        task = self.task_get_by_id(calendar_id, task_id)
        
        self.update_field(task, 'dtstart', dtstart)
        task.save()

    def task_update_end_date(self: Annotated['TaskDAVClient', InjectedToolArg], calendar_id: str, task_id: str, dtend: Optional[datetime]) -> None:
        """Set when the task ends.

        Args:
            calendar_id: Calendar ID.
            task_id: Task ID (uid).
            dtend: The ending date and time for the task.

        Returns:
            None
        """
        task = self.task_get_by_id(calendar_id, task_id)
        self.update_field(task, 'dtend', dtend)
        task.save()

    def task_list_by_calendar(self, calendar_id: str) -> list[dict[str, Any]]:
        """List all tasks within a specific calendar.

        Args:
            calendar_id: The ID of the calendar.

        Returns:
            list[dict[str, Any]]: A list of serialized task data.
        """
        calendar = self.get_calendar_by_id(calendar_id)
        return [
            serialize_ical_todo(t.icalendar_component)
            for t in calendar.todos()
        ]

    def task_list_overdue(self, calendar_id: str) -> list[dict[str, Any]]:
        """List all tasks within a specific calendar that are overdue.

        Args:
            calendar_id: The ID of the calendar.

        Returns:
            list[dict[str, Any]]: A list of serialized task data.
        """
        calendar = self.get_calendar_by_id(calendar_id)
        now = datetime.now()
        overdue_tasks = []
        for t in calendar.todos():
            comp = t.icalendar_component
            due = comp.get("DUE")
            completed = comp.get("COMPLETED")
            due_dt = None

            if due:
                due_val = due.dt if hasattr(due, "dt") else due
                if isinstance(due_val, datetime):
                    due_dt = due_val
                else:
                    try:
                        due_dt = datetime.fromisoformat(str(due_val))
                    except Exception:
                        continue

            # Make both due_dt and now timezone-naive for comparison
            if due_dt is not None and hasattr(due_dt, "tzinfo") and due_dt.tzinfo is not None:
                due_dt = due_dt.replace(tzinfo=None)
            now_naive = now.replace(tzinfo=None) if now.tzinfo is not None else now

            if due_dt and due_dt < now_naive and not completed:
                overdue_tasks.append(serialize_ical_todo(comp))
        return overdue_tasks
