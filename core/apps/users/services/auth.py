from abc import ABC


class BaseAuthService(ABC):
    def authorization(self): ...

    def confirm(self): ...


class AuthService(BaseAuthService):
    pass
