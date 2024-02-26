# filters.py

from django import template

register = template.Library()

@register.filter
def has_unapproved_applications(applications):
    return applications.filter(is_approved=False).exists()
