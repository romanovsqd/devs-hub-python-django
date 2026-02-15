from django import template

register = template.Library()


@register.inclusion_tag("components/project.html")
def render_project(project, user):
    is_author = project.author == user
    return {
        "project": project,
        "is_author": is_author,
    }
