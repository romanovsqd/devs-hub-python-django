from django import template

register = template.Library()


@register.inclusion_tag("components/card.html")
def render_card(card):
    return {"card": card}
