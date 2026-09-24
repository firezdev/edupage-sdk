from re import fullmatch


def extend_domain(domain: str):
    if fullmatch(r"\w+://(?:\w+\.)+\w+", domain) is not None:
        return domain
    if fullmatch(r"(?:\w+\.)+\w+", domain) is not None:
        return f"https://{domain}"
    return f"https://{domain}.edupage.org"
