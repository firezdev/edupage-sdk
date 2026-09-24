from json import dumps, loads
from pathlib import Path

from platformdirs import user_data_path
from pydantic import BaseModel, Field, field_validator

from edupage.utils import extend_domain


class Profile(BaseModel):
    domain: str
    php_session_id: str
    # hsid: str
    # erfp: str
    # egdid: str
    # edusrs: str

    file: Path = Field(exclude=True)

    def save(self):
        self.file.write_text(dumps(self.model_dump(mode="json")))

    @classmethod
    def get(cls, name: str) -> "Profile | None":
        file = get_file(name)
        if not file.exists():
            return None
        return cls.model_validate({**loads(file.read_text()), "file": file})

    @field_validator("domain", mode="after")
    def validate_domain(cls, domain: str):
        return extend_domain(domain)


def get_file(name: str):
    return user_data_path("edupage_sdk", False, ensure_exists=True) / f"{name}.json"
