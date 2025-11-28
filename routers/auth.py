# routersAuth.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from schemas import SignUpIn, LoginIn, UserOut, UserUpdate, PasswordChangeIn
from deps import getCurrentUser
from utils import validatePassword, pwdContext, normalizeEmail, validateNickname, badRequest
from controllers.auth import ctrlSignup, ctrlLogin, ctrlUpdateUser
from storage import emails, nicknames, users, sessions

router = APIRouter(prefix = "/auth", tags = ["auth"])
usersRouter = APIRouter(prefix = "/users", tags = ["users"])

@router.post("/signup", response_model = UserOut, status_code = status.HTTP_201_CREATED)
def signup(payload: SignUpIn):
    u = ctrlSignup(payload.email, payload.password, payload.nickname)

    return {k: u[k] for k in ["id", "email", "nickname", "createdAt"]}

@router.post("/login")
def login(payload: LoginIn):
    token = ctrlLogin(payload.email, payload.password)

    return {"accessToken": token, "tokenType": "bearer"}

@router.get("/check", response_model = UserOut)
def authCheck(current = Depends(getCurrentUser)):
    return {k: current[k] for k in ["id", "email", "nickname", "createdAt"]}

@router.get("/check-email")
def checkEmail(email: str):
    try:
        e = normalizeEmail(email)
    except HTTPException as ex:
        msg = ex.detail["message"] if isinstance(ex.detail, dict) else ex.detail

        return {"available": False, "message": msg}
    
    if e in emails:
        return {"available": False, "message": "*중복된 이메일 입니다."}
    
    return {"available": True, "message": ""}

@router.get("/check-nickname")
def checkNickname(nickname: str):
    try:
        validateNickname(nickname)
    except HTTPException as ex:
        msg = ex.detail["message"] if isinstance(ex.detail, dict) else ex.detail

        return {"available": False, "message": ex.detail}
    
    if not nickname or not nickname.strip():
        return {"available": False, "message": "*닉네임을 입력해주세요."}
    
    if " " in nickname:
        return {"available": False, "message": "*띄어쓰기를 없애주세요."}
    
    if len(nickname) > 10:
        return {"available": False, "message": "*닉네임은 최대 10자 까지 작성 가능합니다."}
    
    if nicknames.get(nickname.lower()):
        return {"available": False, "message": "*중복된 닉네임 입니다."}
    
    return {"available": True, "message": ""}
    
    return {"available": True, "message": ""}

@usersRouter.get("/users/me", response_model = UserOut)
def getMe(current = Depends(getCurrentUser)):
    return {k: current[k] for k in ["id", "email", "nickname", "createdAt"]}

@usersRouter.put("/me", response_model = UserOut)
def updateMe(update: UserUpdate, current = Depends(getCurrentUser)):
    u = ctrlUpdateUser(current["id"], update.nickname)
    
    return {k: u[k] for k in ["id", "email", "nickname", "createdAt"]}

@usersRouter.post("/me/avatar")
def uploadAvatar(file: UploadFile = File(...), current = Depends(getCurrentUser)):
    content = file.file.read()
    current["avatar"] = {"filename": file.filename, "bytes": content}
    
    return {"ok": True, "filename": file.filename}

@usersRouter.delete("/me/avatar")
def deleteAvatar(current = Depends(getCurrentUser)):
    current["avatar"] = None
    
    return {"ok": True}

@usersRouter.post("/me/change-password")
def changePassword(body: PasswordChangeIn, current = Depends(getCurrentUser)):
    
    if not pwdContext.verify(body.currentPassword, current["passwordHash"]):
        badRequest("*비밀번호 확인과 다릅니다.")
    
    validatePassword(body.newPassword)
    current["passwordHash"] = pwdContext.hash(body.newPassword)
    
    return {"ok": True}

@usersRouter.delete("/me")
def deleteMe(current = Depends(getCurrentUser)):
    uid = current["id"]

    for t, u in list(sessions.items()):
        if u == uid:
            del sessions[t]

    emails.pop(current["email"], None)
    nicknames.pop(current["nickname"].lower(), None)
    users.pop(uid, None)

    return {"ok": True}

router.include_router(usersRouter)