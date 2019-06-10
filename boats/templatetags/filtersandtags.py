from django import template
from currency_converter import CurrencyConverter, RateNotFoundError
from functools import reduce

register = template.Library()


@register.filter
def get_at_index(_list, index):
    """Доступ к элементу списка по индексу"""
    try:
        return _list[index]
    except IndexError as err:
        return str(err)


@register.filter
def currency_converter(price, curr1="SEK", curr2="EUR"):
    """конвертер валют . Работает медленно"""
    c = CurrencyConverter()
    try:
        return c.convert(price, curr1, curr2)
    except ValueError or RateNotFoundError as err:
        return str(err)


@register.filter
def int_to_str(value):
    """ Конвертирует int в str"""
    return str(value)


@register.filter
def multiplier(line):
    """Перемножает все члены последовательности друг на друга"""
    result = reduce((lambda x, y: int(x) * int(y)), line.split("*"))
    return result

