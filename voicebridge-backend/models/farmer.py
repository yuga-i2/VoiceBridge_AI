"""
VoiceBridge AI — Farmer Profile Model
Data structure for farmer profiles used across all services.
"""

from dataclasses import dataclass, field, asdict


@dataclass
class FarmerProfile:
    """
    Represents a farmer's profile and eligibility information.
    All fields have sensible defaults.
    """
    name: str = "Unknown"
    land_acres: float = 0.0
    state: str = ""
    has_kcc: bool = False
    has_bank_account: bool = True
    phone_number: str = ""
    age: int = 0
    annual_income: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> "FarmerProfile":
        """
        Create FarmerProfile from a dictionary.
        Handles missing keys gracefully with defaults.
        Never raises KeyError.
        """
        return cls(
            name=data.get("name", "Unknown"),
            land_acres=float(data.get("land_acres", 0.0)),
            state=data.get("state", ""),
            has_kcc=bool(data.get("has_kcc", False)),
            has_bank_account=bool(data.get("has_bank_account", True)),
            phone_number=data.get("phone_number", ""),
            age=int(data.get("age", 0)),
            annual_income=float(data.get("annual_income", 0.0))
        )

    def to_dict(self) -> dict:
        """Returns all fields as a dictionary."""
        return asdict(self)

    def is_valid(self) -> bool:
        """
        Returns True only if land_acres > 0 and state is not empty.
        A farmer profile without land size or state cannot be matched to schemes.
        """
        return self.land_acres > 0 and len(self.state.strip()) > 0

    def __str__(self) -> str:
        """Returns human readable summary."""
        kcc_status = "Yes" if self.has_kcc else "No"
        bank_status = "Yes" if self.has_bank_account else "No"
        return f"{self.name} | {self.land_acres} acres | {self.state} | KCC: {kcc_status} | Bank: {bank_status}"
