from django import template

register = template.Library()


@register.inclusion_tag("components/deck_card.html")
def render_deck(deck, user, is_owner=False, studying_decks_ids=None):
    is_author = deck.author == user
    if studying_decks_ids:
        deck.is_studying = deck.id in set(studying_decks_ids)
    return {
        "deck": deck,
        "is_author": is_author,
        "is_owner": is_owner,
    }


@register.inclusion_tag("components/deck_table.html")
def render_deck_as_table(deck, user, is_owner=False, studying_decks_ids=None):
    is_author = deck.author == user
    if studying_decks_ids:
        deck.is_studying = deck.id in set(studying_decks_ids)
    return {
        "deck": deck,
        "is_author": is_author,
        "is_owner": is_owner,
    }
