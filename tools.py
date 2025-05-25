from langchain_core.tools import tool, BaseTool
from dav import TaskDAVClient

def get_taskdav_tools(client: 'TaskDAVClient') -> list[BaseTool]:
    """Return all LangChain tools for the given TaskDAVClient instance."""
    return [
        tool(client.task_get_by_id, parse_docstring=True),
        tool(client.task_list_by_calendar, parse_docstring=True),
        tool(client.task_list_overdue, parse_docstring=True),
        tool(client.calendar_list_ids, parse_docstring=True),
        tool(client.task_add_to_calendar, parse_docstring=True),
        tool(client.task_mark_complete, parse_docstring=True),
        tool(client.task_mark_incomplete, parse_docstring=True),
        tool(client.task_update_summary, parse_docstring=True),
        tool(client.task_update_priority, parse_docstring=True),
        tool(client.task_update_due_date, parse_docstring=True),
        tool(client.task_update_description, parse_docstring=True),
        tool(client.task_update_start_date, parse_docstring=True),
        tool(client.task_update_end_date, parse_docstring=True),
    ]