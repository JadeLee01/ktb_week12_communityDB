# deps.py

from typing import Any, Dict, Optional
from fastapi import Header, HTTPException
from storage import users, sessions
from utils import authRequired, invalidToken

def getCurrentUser(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        authRequired()
    
    token = authorization.split(" ", 1)[1].strip()
    uid = sessions.get(token)
    
    if not uid:
        invalidToken()
    
    return users[uid]