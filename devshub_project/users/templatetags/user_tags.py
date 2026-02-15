from django import template

register = template.Library()


@register.inclusion_tag("components/user.html")
def render_user(user):
    return {
        "user": user,
    }
