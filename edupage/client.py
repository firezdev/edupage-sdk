from requests import Response, Session

from edupage.profile import Profile, get_file
from edupage.request import decode_json, request


class Client:
    def __init__(self, name: str):
        self.session = Session()
        self._profile = Profile.get(name)
        if not self._profile:
            raise FileNotFoundError("Profile not found")

        self.domain = self._profile.domain
        self.session.cookies.set(
            "PHPSESSID",
            self._profile.php_session_id,
            domain=self._profile.domain.removeprefix("https://")
        )
        # for cookie in ["hsid", "erfp", "egdid", "edusrs"]:
        #     self.session.cookies.set(
        #         cookie,
        #         getattr(self._profile, cookie),
        #         domain=self._profile.domain.removeprefix("https://")
        #     )

    @classmethod
    def login(cls, domain: str, username: str, password: str, name: str | None = None):
        instance: Client = cls.__new__(cls)
        instance.domain = domain
        instance.session = Session()

        token_res = instance.request(
            "post", "login/?cmd=MainLogin&akcia=getToken", {"username": username}
        )
        login_res = instance.request(
            "post",
            "login/?cmd=MainLogin&akcia=login",
            {
                "username": username,
                "password": password,
                "userToken": decode_json(token_res.text)["token"]
            }
        )
        sid = login_res.cookies["PHPSESSID"]
        assert sid, "PHP session is none"
        instance._profile = Profile(
            domain=domain, php_session_id=sid, file=get_file(name or username)
        )
        instance._profile.save()
        return instance

    def request(self, method: str, path: str, data: dict | None = None) -> Response:
        return request(self.session, method, self.domain, path, data)
