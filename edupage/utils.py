from re import fullmatch


def _extend_domain(domain: str):
    if fullmatch(r"\w+://(?:\w+.)+\w+", domain):
        return domain
    if fullmatch(r"(?:\w+.)+\w+", domain):
        return f"https://{domain}"
    return f"https://{domain}.edupage.org"
