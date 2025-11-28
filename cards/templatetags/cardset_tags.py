from django import template


register = template.Library()


@register.inclusion_tag('cardsets/components/cardset.html')
def render_cardset(cardset):
    return {'cardset': cardset}
