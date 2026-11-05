from clovers_client import Config as BaseConfig


class Config(BaseConfig):
    url: str = "http://127.0.0.1:3000"
    token: str = ""
    admin_groups: list[str] = []
    onwer_groups: list[str] = ["744751179"]
