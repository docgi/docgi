import random
import string


def random_string(max_len=10) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(max_len))


def gen_username(email: str) -> str:
    email = email.lower()
    splits = email.split("@")
    username = f"{splits[0]}-{random_string(max_len=4)}"
    return username


def random_string_number(max_len=6) -> str:
    letters = string.digits
    return ''.join(random.choice(letters) for _ in range(max_len))
