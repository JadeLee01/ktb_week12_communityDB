# controllersAuth.py

import secrets
from datetime import datetime, timezone
from fastapi import HTTPException
from typing import Dict, Any
from storage import users, emails, nicknames, sessions, userSeq
from utils import normalizeEmail, validatePassword, validateNickname, pwdContext, badRequest, authRequired, notFound
from models.auth import createUser, getUserByEmailNorm, getUser, isEmailTaken, isNicknameTaken, updateNickname, issueToken, deleteUser

def ctrlSignup(email: str, password: str, nickname: str) -> Dict[str, Any]:
    emailNorm = normalizeEmail(email)
    validatePassword(password)
    validateNickname(nickname)

    if isEmailTaken(emailNorm):
        badRequest("*중복된 이메일 입니다.")

    if isNicknameTaken(nickname):
        badRequest("*중복된 닉네임 입니다.")

    passwordHash = pwdContext.hash(password)

    return createUser(emailNorm, passwordHash, nickname)

def ctrlLogin(email: str, password: str) -> str:
    emailNorm = normalizeEmail(email)
    u = getUserByEmailNorm(emailNorm)

    if not u or not pwdContext.verify(password, u["passwordHash"]):
        raise HTTPException(401, {"code": "INVALID_CREDENTIALS", "message": "*아이디 또는 비밀번호를 확인해주세요."})
    
    return issueToken(u["id"])

def ctrlGetUser(uid: int) -> Dict[str, Any]:
    u = getUser(uid)

    if not u:
        notFound("사용자를 찾을 수 없습니다.")

    return u

def ctrlUpdateUser(uid: int, nickname: str) -> Dict[str, Any]:
    validateNickname(nickname)

    if isNicknameTaken(nickname, excludeUid=uid):
        badRequest("*중복된 닉네임 입니다.")
        
    return updateNickname(uid, nickname)

def ctrlDeleteMe(uid: int) -> bool:
    return deleteUser(uid)