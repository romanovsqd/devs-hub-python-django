from django import template

from decks import services

register = template.Library()


@register.inclusion_tag("components/deck_card.html")
def render_deck(deck, user, studying_decks_ids=None, is_owner=None):
    is_author = deck.author == user
    is_saved = services.is_deck_saved_by_user(deck, user)
    return {
        "deck": deck,
        "is_author": is_author,
        "is_saved": is_saved,
        "studying_decks_ids": studying_decks_ids,
        "is_owner": is_owner,
    }


@register.inclusion_tag("components/deck_table.html")
def render_deck_as_table(deck, user, studying_decks_ids=None, is_owner=None):
    is_author = deck.author == user
    is_saved = services.is_deck_saved_by_user(deck, user)
    return {
        "deck": deck,
        "is_author": is_author,
        "is_saved": is_saved,
        "studying_decks_ids": studying_decks_ids,
        "is_owner": is_owner,
    }
