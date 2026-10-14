from fastapi import APIRouter, Depends, HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from config import PUBLIC_BASE_URL
from db import get_session
from models import UrlCreate, UrlMapping, UrlResponse
from services.base62 import encode
from services.counter import get_next_id

MAX_GENERATION_ATTEMPTS = 5

router = APIRouter(prefix="/urls", tags=["urls"])


@router.post("", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
def create_url(payload: UrlCreate, session: Session = Depends(get_session)) -> UrlResponse:
    if payload.custom_alias is not None:
        try:
            url_mapping = _insert_mapping(
                session=session,
                payload=payload,
                short_code=payload.custom_alias,
            )
        except IntegrityError as error:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Custom alias is already in use",
            ) from error
        return _to_response(url_mapping)

    for _ in range(MAX_GENERATION_ATTEMPTS):
        try:
            short_code = encode(get_next_id())
            url_mapping = _insert_mapping(
                session=session,
                payload=payload,
                short_code=short_code,
            )
            return _to_response(url_mapping)
        except RedisError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Short-code generator is unavailable",
            ) from error
        except IntegrityError:
            session.rollback()

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Could not allocate a unique short code",
    )


def _insert_mapping(*, session: Session, payload: UrlCreate, short_code: str) -> UrlMapping:
    url_mapping = UrlMapping(
        short_code=short_code,
        long_url=str(payload.long_url),
        expires_at=payload.expires_at,
    )
    session.add(url_mapping)
    session.commit()
    session.refresh(url_mapping)
    return url_mapping


def _to_response(url_mapping: UrlMapping) -> UrlResponse:
    return UrlResponse(
        short_code=url_mapping.short_code,
        short_url=f"{PUBLIC_BASE_URL}/{url_mapping.short_code}",
        long_url=url_mapping.long_url,
        created_at=url_mapping.created_at,
        expires_at=url_mapping.expires_at,
    )
