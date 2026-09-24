from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from edupage.client import Client


class CurrentUser(BaseModel):
    id: int
    type: str
    name: str
    login: str

    @classmethod
    def from_html(cls, client: "Client"):
        return cls(
            id=client._user_edubar["loggedUser"].split("-")[1],
            type=client._user_edubar["erid"].split(";")[3],
            name=client._user_edubar["loggedUserName"],
            login=client._user_edubar["erid"].split(";")[2]
        )
