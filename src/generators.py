import random
import string


def generate_password(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """Generate a random password with specified options."""
    chars = ""
    if use_upper:
        chars += string.ascii_uppercase
    if use_lower:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"

    if not chars:
        chars = string.ascii_letters + string.digits

    password = "".join(random.SystemRandom().choice(chars) for _ in range(length))
    return password


def generate_username(style: str = "random_word") -> str:
    """Generate a random username.

    Styles:
    - random_word: adjective + noun + number (e.g., SwiftFox_42)
    - random_string: random alphanumeric (e.g., x7k9m2p)
    - email_style: word + number (e.g., user8472)
    """
    adjectives = [
        "Swift", "Bright", "Calm", "Dark", "Eager", "Fast", "Gentle",
        "Happy", "Icy", "Jolly", "Kind", "Lucky", "Mighty", "Noble",
        "Quiet", "Rapid", "Silly", "Tough", "Wild", "Zesty", "Brave",
        "Cool", "Deep", "Fair", "Grand", "Hot", "Just", "Keen", "Lean",
    ]
    nouns = [
        "Fox", "Wolf", "Bear", "Eagle", "Hawk", "Lion", "Tiger",
        "Shark", "Whale", "Crane", "Deer", "Dove", "Frog", "Goat",
        "Lynx", "Mule", "Owl", "Raven", "Seal", "Swan", "Wren",
        "Storm", "Blaze", "Cloud", "Frost", "Spark", "Wave", "Rock",
    ]

    if style == "random_word":
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        num = random.randint(10, 9999)
        return f"{adj}{noun}_{num}"
    elif style == "email_style":
        words = [
            "user", "person", "member", "contact", "admin", "guest",
            "player", "agent", "chief", "hero",
        ]
        word = random.choice(words)
        num = random.randint(1000, 9999)
        return f"{word}{num}"
    else:  # random_string
        return "".join(
            random.SystemRandom().choice(string.ascii_lowercase + string.digits)
            for _ in range(8)
        )
