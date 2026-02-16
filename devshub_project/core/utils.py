import bleach

ALLOWED_TAGS = [
    "b",
    "i",
    "u",
    "p",
    "br",
    "ul",
    "ol",
    "li",
    "a",
    "strong",
    "em",
    "pre",
    "code",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "div",
    "span",
    "small",
    "mark",
    "del",
    "ins",
    "samp",
    "kbd",
    "div",
]


def clean_html(user_html):
    """
    Очищает HTML от опасных тегов, чтобы избежать xss атак.
    """
    return bleach.clean(user_html, tags=ALLOWED_TAGS, strip=True)
