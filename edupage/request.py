from base64 import b64decode, b64encode
from hashlib import sha1
from json import dumps, loads
from urllib.parse import urlencode
from zlib import compressobj

from requests import Response, Session


def _compress(data: bytes) -> bytes:
    compressor = compressobj(wbits=-15)
    compressor.compress(data)
    return compressor.flush()


def _base64_encode(data: bytes) -> str:
    return b64encode(data).decode()


def _base64_decode(data: str) -> dict:
    return loads(b64decode(data))


def encode_json(json: dict):
    encoded_data = urlencode(json)
    encoded_data = _base64_encode(_compress(encoded_data.encode()))
    eqap = f"dz:{encoded_data}"

    return urlencode(
        {"eqap": eqap, "eqacs": sha1(eqap.encode()).hexdigest(), "eqaz": "1"}
    )


def decode_json(response: str) -> dict:
    if response.startswith("eqwd:"):  # failure
        return _base64_decode(response[5:])

    if not response.startswith("eqz:"):  # success (not compressed)
        return loads(response)

    return _base64_decode(response[4:])


def request(
    session: Session, method: str, domain: str, path: str, data: dict | None = None
) -> Response:
    return session.request(
        method,
        f"{domain}/{path}",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=encode_json({"rpcparams": dumps(data)}) if data else None
    )
