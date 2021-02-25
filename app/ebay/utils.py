import hashlib


def generate_hash(string: str) -> str:
    return str(hashlib.md5(string.encode("utf-8")).hexdigest())
