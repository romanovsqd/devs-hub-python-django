from django import template

register = template.Library()


@register.inclusion_tag("components/deck.html")
def render_deck(deck):
    return {"deck": deck}
