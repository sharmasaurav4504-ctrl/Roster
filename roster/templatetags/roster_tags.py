from django import template

register = template.Library()

@register.filter
def get_schedule(schedule_map, key):
    """Usage: schedule_map|get_schedule:agent_id will not work directly.
    We need a different approach."""
    return schedule_map.get(key)

@register.simple_tag
def lookup_schedule(schedule_map, agent_id, date_str):
    return schedule_map.get((agent_id, date_str))
