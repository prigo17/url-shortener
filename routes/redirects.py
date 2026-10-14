from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from redis.exceptions import RedisError
from sqlmodel import Session

from db import get_session
from models import UrlMapping
from services.cache import cache_url, get_cached_url

router = APIRouter(tags=["redirects"])

@router.get("/{short_code}", response_class=RedirectResponse, status_code=302)
def redirect(short_code: str, session: Session = Depends(get_session)):

    try:
        long_url = get_cached_url(short_code)
    
        if long_url is not None:
            return RedirectResponse(status_code=302, url=long_url)

    except RedisError:
        pass

    url_mapping = session.get(UrlMapping, short_code)

    if not url_mapping:
        raise HTTPException(status_code=404, detail="No record exists")

    if url_mapping.expires_at is not None:
        expires_at = url_mapping.expires_at
 
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
 
        if expires_at <= datetime.now(UTC):
            raise HTTPException(status_code=410, detail="Link has expired")

    try:
        cache_url(short_code, url_mapping.long_url, url_mapping.expires_at)
    except RedisError:
        pass

    return RedirectResponse(status_code=302, url=url_mapping.long_url)
