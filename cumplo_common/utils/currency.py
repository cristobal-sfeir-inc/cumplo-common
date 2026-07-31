"""Currency formatting utilities."""

import babel.numbers

from cumplo_common.models import Currency


def format_currency(amount: int, currency: Currency = Currency.CLP) -> str:
    """
    Format an amount of money in CLP.

    Args:
        amount (int): The amount of money to be formatted
        currency (Currency, optional): The currency to be used. Defaults to Currency.CLP.

    Returns:
        str: The formatted amount of money

    """
    return babel.numbers.format_currency(amount, currency=currency, locale="es_CL")
