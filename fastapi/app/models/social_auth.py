'''
social auth = maps a user to their OAuth provider identity

- support Google SSO and GitHub SSO
- student may authenticate exclusively via SSO (hashed_password will be null on user)
- teacher are admin created with username/password and dont use SSO
'''

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

'''
A foreign key (FK) is a column or a set of columns in one database table
that refers to the primary key (PK) or a unique key in another table
'''

if TYPE_CHECKING:
    from .user import User

class SocialAuth(Base):
    __tablename__ = "social_auth"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable = False, index = True
    )

    # google / github
    provider: Mapped[str] = mapped_column(String(20), nullable = False)
    
    # the unique id return by the provider
    provider_id: Mapped[str] = mapped_column(String(100), unique = True, nullable = False)

    user: Mapped["User"] = relationship(back_populates = "social_accounts")

    def __repr__(self) -> str:
        return f"<SocialAuth(user_id={self.user_id}, provider='{self.provider}')>"