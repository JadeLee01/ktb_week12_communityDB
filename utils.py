# utils.py

import re
from fastapi import HTTPException
from passlib.context import CryptContext

pwdContext = CryptContext(schemes = ["pbkdf2_sha256"], deprecated = "auto")
passwordRe = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^\w\s]).{8,20}$")

def badRequest(message: str, fields: dict | None = None):
    raise HTTPException(400, {"code": "BAD_REQUEST", "message": message, "fields": fields})

def authRequired():
    raise HTTPException(401, {"code": "AUTH_REQUIRED", "message": "토큰이 필요합니다. (Bearer <token>)"})

def invalidToken():
    raise HTTPException(401, {"code": "INVALID_TOKEN", "message": "유효하지 않은 토큰"})

def forbidden(message = "권한이 없습니다."):
    raise HTTPException(403, {"code": "FORBIDDEN", "message": message})

def notFound(message = "리소스를 찾을 수 없습니다."):
    raise HTTPException(404, {"code": "NOT_FOUND", "message": message})

def payloadTooLarge(message = "파일 용량이 허용치를 초과했습니다."):
    raise HTTPException(413, {"code": "PAYLOAD_TOO_LARGE", "message": message})

def normalizeEmail(email: str) -> str:
    e = (email or "").strip().lower()
    
    if not e or "@" not in e or "." not in e.split("@")[-1]:
        badRequest("*올바른 이메일 주소 형식을 입력해주세요. (예: example@example.com)")
    
    return e

def validatePassword(pw: str):
    if not pw:
        badRequest("*비밀번호를 입력해주세요.")
    
    if not passwordRe.match(pw):
        badRequest("*비밀번호는 8자 이상, 20자 이하이며, 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야합니다.")

def validateNickname(nick: str):
    if not nick or not nick.strip():
        badRequest("*닉네임을 입력해주세요.")
    
    if " " in nick:
        badRequest("*띄어쓰기를 없애주세요.")
    
    if len(nick) > 10:
        badRequest("*닉네임은 최대 10자 까지 작성 가능합니다.")