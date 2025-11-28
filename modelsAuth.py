# modelsAuth.py
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from storage import users, emails, nicknames, sessions, userSeq

def createUser(emailNorm: str, passwordHash: str, nickname: str) -> Dict[str, Any]:
    global userSeq
    userSeq += 1
    uid = userSeq
    user = {
        "id": uid,
        "email": emailNorm,
        "passwordHash": passwordHash,
        "nickname": nickname,
        "createdAt": datetime.now(timezone.utc),
        "avatar": None,
    }
    users[uid] = user
    emails[emailNorm] = uid
    nicknames[nickname.lower()] = uid
    return user

def getUserByEmailNorm(emailNorm: str) -> Optional[Dict[str, Any]]:
    uid = emails.get(emailNorm)
    return users.get(uid) if uid else None

def getUser(uid: int) -> Optional[Dict[str, Any]]:
    return users.get(uid)

def isEmailTaken(emailNorm: str) -> bool:
    return emailNorm in emails

def isNicknameTaken(nickname: str, excludeUid: Optional[int] = None) -> bool:
    owner = nicknames.get(nickname.lower())
    return bool(owner and owner != excludeUid)

def updateNickname(uid: int, nickname: str) -> Dict[str, Any]:
    u = users[uid]
    old = u.get("nickname")
    if old and nicknames.get(old.lower()) == uid:
        del nicknames[old.lower()]
    u["nickname"] = nickname
    nicknames[nickname.lower()] = uid
    return u

def issueToken(uid: int) -> str:
    import secrets
    token = secrets.token_urlsafe(24)
    sessions[token] = uid
    return token

def deleteUser(uid: int) -> bool:
    # 세션 정리
    for t, u in list(sessions.items()):
        if u == uid:
            del sessions[t]
    user = users.get(uid)
    if user:
        emails.pop(user["email"], None)
        if user.get("nickname"):
            nicknames.pop(user["nickname"].lower(), None)
    users.pop(uid, None)
    return True
