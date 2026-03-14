import json
from functools import lru_cache
from pathlib import Path


CATALOG_PATH = Path(__file__).resolve().parents[2] / 'frontend-analytics' / 'src' / 'config' / 'toolCatalog.json'


@lru_cache(maxsize=1)
def load_tool_catalog():
    with CATALOG_PATH.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def get_tool_by_slug(slug):
    return next((tool for tool in load_tool_catalog() if tool.get('slug') == slug), None)


def get_related_tools(slug, limit=None):
    tool = get_tool_by_slug(slug)
    if not tool:
        return []

    related_slugs = tool.get('related_tools') or []
    related_tools = [get_tool_by_slug(related_slug) for related_slug in related_slugs]
    filtered_tools = [related_tool for related_tool in related_tools if related_tool]

    if limit is None:
        return filtered_tools
    return filtered_tools[:limit]