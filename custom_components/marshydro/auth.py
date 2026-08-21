"""Authentication helpers for Mars Hydro Legacy.

The Legacy REST API documented by the community accepts a Mars Hydro
email/password login and returns the session token.  Apple Sign-In itself is
handled by the mobile app, so this module intentionally does not collect or
handle an Apple password or Apple credential.
"""

from dataclasses import dataclass


@dataclass
class MarsHydroSession:
    token: str
    user_id: str | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self.token)
