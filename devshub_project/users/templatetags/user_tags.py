from django import template

register = template.Library()


@register.inclusion_tag("components/user_card.html")
def render_user(user):
    return {
        "user": user,
    }


@register.inclusion_tag("components/user_table.html")
def render_user_as_table(user):
    return {
        "user": user,
    }
