CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(CHARACTERS)


def encode(number: int) -> str:
    """Encode a non-negative integer as a Base62 string."""

    if number < 0:
        raise ValueError("Base62 encoding requires a non-negative integer")

    if number == 0:
        return CHARACTERS[0]

    encoded_characters: list[str] = []
    while number > 0:
        number, remainder = divmod(number, BASE)
        encoded_characters.append(CHARACTERS[remainder])

    return "".join(reversed(encoded_characters))
