from django import template
from menu import menu_registry, Menu

register = template.Library()

@register.assignment_tag(takes_context=True)
def menu(context, name):
    items = Menu(menu_registry[name])
    return items.calculate(context)
