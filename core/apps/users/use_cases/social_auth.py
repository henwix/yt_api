from dataclasses import dataclass


@dataclass
class SocialAuthsUseCase:
    def execute(self): ...
