from dataclasses import asdict, dataclass


@dataclass
class VerificationState:
    customer_name: str = ""
    pan_verified: bool | None = None
    bank_verified: bool | None = None
    selfie_uploaded: bool | None = None

    def summary(self) -> dict:
        return asdict(self)