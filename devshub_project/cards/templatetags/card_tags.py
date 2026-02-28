from django import template

register = template.Library()


@register.inclusion_tag("components/card_card.html")
def render_card(card, user):
    is_author = card.author == user
    return {
        "card": card,
        "is_author": is_author,
    }


@register.inclusion_tag("components/card_table.html")
def render_card_as_table(card, user):
    is_author = card.author == user
    return {
        "card": card,
        "is_author": is_author,
    }
