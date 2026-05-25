CONVERSION_RATES = {
    "INR": 1,
    "USD": 83,
    "EUR": 90,
}

SUPPORTED_CURRENCIES = list(CONVERSION_RATES.keys())


def convert_to_inr(amount, currency):
    currency = currency.upper()
    if currency not in CONVERSION_RATES:
        raise ValueError(f"Unsupported currency: {currency}")
    return round(amount * CONVERSION_RATES[currency], 2)


def get_rate(currency):
    currency = currency.upper()
    return CONVERSION_RATES.get(currency, None)
