from functools import cached_property
from json import loads

from requests import Response, Session
from selectolax.lexbor import LexborHTMLParser

from edupage.models.user import CurrentUser
from edupage.profile import Profile, get_file
from edupage.request import decode_json, request
from edupage.utils import extend_domain


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
        self.__userhome: dict | None = None
        self.__edubar: dict | None = None

    @classmethod
    def login(cls, domain: str, username: str, password: str, name: str | None = None):
        instance: Client = cls.__new__(cls)
        instance.domain = extend_domain(domain)
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

    def _load_user(self):
        html = LexborHTMLParser(self.request("get", "user").text)
        # print(html.html_pretty())

        userhome = html.css_first("div#bar_mainDiv script:last-child")
        if userhome and userhome.text():
            self.__userhome = loads(
                userhome.text()
                .split(").userhome(")[1]
                .rstrip()
                .removesuffix("});")
                .rstrip()
                .removesuffix(");")
            )
        else:
            raise RuntimeError("No userhome found (page user)")

        edubar = html.css_first("div.topDiv script")
        if edubar and edubar.text():
            self.__edubar = loads(
                edubar.text().split(").edubar(")[1].rstrip().removesuffix(");")
            )
        else:
            raise RuntimeError("No edubar found (page user)")

    @property
    def _user_userhome(self):
        if not self.__userhome:
            self._load_user()
        return self.__userhome

    @property
    def _user_edubar(self):
        if not self.__edubar:
            self._load_user()
        return self.__edubar

    @cached_property
    def user(self) -> CurrentUser:
        return CurrentUser.from_html(self)
