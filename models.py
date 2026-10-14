import re
from datetime import UTC, datetime

from pydantic import HttpUrl, field_validator
from sqlmodel import Field, SQLModel

RESERVED_ALIASES = frozenset({"health", "urls", "docs", "redoc", "openapi"})
ALIAS_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


class UrlMapping(SQLModel, table=True):
    short_code: str = Field(primary_key=True, max_length=30)
    long_url: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = Field(default=None)


class UrlCreate(SQLModel):
    custom_alias: str | None = Field(
        default=None,
        min_length=3,
        max_length=30,
    )
    long_url: HttpUrl
    expires_at: datetime | None = Field(default=None)

    @field_validator("custom_alias")
    @classmethod
    def validate_custom_alias(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not ALIAS_PATTERN.fullmatch(value):
            raise ValueError(
                "custom alias may contain only letters, numbers, hyphens, and underscores"
            )
        if value.casefold() in RESERVED_ALIASES:
            raise ValueError("custom alias is reserved by the service")
        return value


class UrlResponse(SQLModel):
    short_code: str
    short_url: str
    long_url: str
    created_at: datetime
    expires_at: datetime | None