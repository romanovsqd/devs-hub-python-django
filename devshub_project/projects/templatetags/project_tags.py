from django import template

register = template.Library()


@register.inclusion_tag("components/project_card.html")
def render_project(project, user):
    is_author = project.author == user
    return {
        "project": project,
        "is_author": is_author,
    }


@register.inclusion_tag("components/project_table.html")
def render_project_as_table(project, user):
    is_author = project.author == user
    return {
        "project": project,
        "is_author": is_author,
    }
