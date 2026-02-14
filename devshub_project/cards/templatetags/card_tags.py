from django import template

from cards import services

register = template.Library()


@register.inclusion_tag("components/card.html")
def render_card(card, user):
    is_author = card.author == user
    is_saved = services.is_card_saved_by_user(card=card, user=user)
    return {
        "card": card,
        "is_author": is_author,
        "is_saved": is_saved,
    }
