from django import template

register = template.Library()


@register.filter
def times(number: int) -> range:
    """

    :param number:
    :return:
    """
    return range(1, int(number) + 1)
