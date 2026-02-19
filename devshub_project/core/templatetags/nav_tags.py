from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_link(context, url_name, css_class="text-blue-600"):
    """
    Возвращает CSS-класс, если текущий url совпадает с url_name.
    """
    request = context["request"]
    if request.resolver_match and request.resolver_match.url_name == url_name:
        return css_class
    return ""
