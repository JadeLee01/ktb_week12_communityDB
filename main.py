# main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from routers.auth import router as authRouter
from routers.posts import router as postsRouter
from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from database import Base, engine
import db_models


app = FastAPI(title = "Community API", version = "0.2.0")

Base.metadata.create_all(bind = engine)


origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.include_router(authRouter)
app.include_router(postsRouter)

""" utils.py
pwdContext = CryptContext(schemes = ["pbkdf2_sha256"], deprecated = "auto")
passwordRe = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^\w\s]).{8,20}$")
"""

""" storage.py
users: Dict[int, Dict[str, Any]] = {}
emails: Dict[str, int] = {}
nicknames: Dict[str, int] = {}
sessions: Dict[str, int] = {}
posts: Dict[int, Dict[str, Any]] = {}
userSeq = 0
postSeq = 0
postImages: Dict[int, Dict[str, Any]] = {}
comments: Dict[int, Dict[int, Dict[str, Any]]] = {}
likes: Dict[int, set] = {}
commentSeq = 0
"""

""" utils.py
def normalizeEmail(email: str) -> str:
    e = (email or "").strip().lower()
    
    if not e or "@" not in e or "." not in e.split("@")[-1]:
        raise HTTPException(422, "*올바른 이메일 주소 형식을 입력해주세요. (예: example@example.com)")
    
    return e

def validatePassword(pw: str):
    if not pw:
        raise HTTPException(422, "*비밀번호를 입력해주세요.")
    
    if not passwordRe.match(pw):
        raise HTTPException(422, "*비밀번호는 8자 이상, 20자 이하이며, 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야합니다.")

def validateNickname(nick: str):
    if not nick or not nick.strip():
        raise HTTPException(422, "*닉네임을 입력해주세요.")
    
    if " " in nick:
        raise HTTPException(422, "*띄어쓰기를 없애주세요.")
    
    if len(nick) > 10:
        raise HTTPException(422, "*닉네임은 최대 10자 까지 작성 가능합니다.")
"""

""" deps.py
def getCurrentUser(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "토큰이 필요합니다. (Bearer <token>)")
    
    token = authorization.split(" ", 1)[1].strip()
    uid = sessions.get(token)
    
    if not uid:
        raise HTTPException(401, "유효하지 않은 토큰")
    
    return users[uid]
"""

""" schemas.py
class SignUpIn(BaseModel):
    email: EmailStr
    password: str = Field(minLength = 8, maxLength = 20)
    nickname: str = Field(minLength = 1, maxLength = 10)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    createdAt: datetime

class UserUpdate(BaseModel):
    nickname: str = Field(minLength = 1, maxLength = 10)

class PostCreate(BaseModel):
    title: str = Field(minLength = 1, maxLength = 26)
    body: str  = Field(minLength = 5, maxLength = 20_000)

class PostOut(BaseModel):
    id: int
    title: str
    body: str
    authorId: int
    createdAt: datetime
    updatedAt: datetime
    views: int = 0
    likesCount: int = 0
    commentsCount: int = 0

class CommentCreate(BaseModel):
    text: str = Field(minLength = 1, maxLength = 1000)

class CommentOut(BaseModel):
    id: int
    postId: int
    authorId: int
    text: str
    createdAt: datetime
    updatedAt: datetime

class PasswordChangeIn(BaseModel):
    currentPassword: str
    newPassword: str = Field(minLength = 8, maxLength = 20)
"""

""" controllersAuth.py
def ctrlSignup(email: str, password: str, nickname: str):
    emailNorm = normalizeEmail(email)
    validatePassword(password)
    validateNickname(nickname)

    if emailNorm in emails:
        raise HTTPException(400, "*중복된 이메일 입니다.")
    
    if nicknames.get(nickname.lower()):
        raise HTTPException(400, "*중복된 닉네임 입니다.")
    
    global userSeq
    userSeq += 1
    uid = userSeq
    users[uid] = {
        "id": uid,
        "email": emailNorm,
        "passwordHash": pwdContext.hash(password),
        "nickname": nickname,
        "createdAt": datetime.now(timezone.utc),
        "avatar": None,
    }
    emails[emailNorm] = uid
    nicknames[nickname.lower()] = uid

    return users[uid]

def ctrlLogin(email: str, password: str):
    emailNorm = normalizeEmail(email)
    uid = emails.get(emailNorm)

    if not uid or not pwdContext.verify(password, users[uid]["passwordHash"]):
        raise HTTPException(401, "*아이디 또는 비밀번호를 확인해주세요.")
    
    token = secrets.token_urlsafe(24)
    sessions[token] = uid

    return token

def ctrlGetUser(uid: int):
    u = users.get(uid)

    if not u:
        raise HTTPException(404, "사용자를 찾을 수 없습니다.")
    
    return u

def ctrlUpdateUser(uid: int, nickname: str):
    validateNickname(nickname)
    u = ctrlGetUser(uid)
    owner = nicknames.get(nickname.lower())
    
    if owner and owner != uid:
        raise HTTPException(400, "*중복된 닉네임 입니다.")
    
    old = u["nickname"]
    
    if old and nicknames.get(old.lower()) == uid:
        del nicknames[old.lower()]
    
    u["nickname"] = nickname
    nicknames[nickname.lower()] = uid
    
    return u
"""

""" controllersPosts.py
def ctrlListPosts(skip: int, limit: int, q: Optional[str]):
    data = list(posts.values())
    
    if q:
        key = q.strip().lower()
        data = [p for p in data if key in p["title"].lower() or key in p["body"].lower()]
    
    data.sort(key=lambda x: x["createdAt"], reverse = True)
    
    return data[skip: skip + limit]

def ctrlCreatePost(authorId: int, title: str, body: str):
    global postSeq
    postSeq += 1
    pid = postSeq
    now = datetime.now(timezone.utc)
    post = {
        "id": pid,
        "title": title.strip(),
        "body": body.strip(),
        "authorId": authorId,
        "createdAt": now,
        "updatedAt": now,
        "views": 0,
        "likesCount": 0,
        "commentsCount": 0,
    }
    posts[pid] = post
    likes[pid] = set()
    comments[pid] = {}

    return post

def ctrlGetPost(pid: int):
    p = posts.get(pid)
    
    if not p:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")
    
    return p

def ctrlUpdatePost(pid: int, authorId: int, title: str, body: str):
    p = ctrlGetPost(pid)
    
    if p["authorId"] != authorId:
        raise HTTPException(403, "수정 권한이 없습니다.")
    
    p["title"] = title.strip()
    p["body"]  = body.strip()
    p["updatedAt"] = datetime.now(timezone.utc)
    
    return p

def ctrlDeletePost(pid: int, authorId: int):
    p = ctrlGetPost(pid)

    if p["authorId"] != authorId:
        raise HTTPException(403, "삭제 권한이 없습니다.")
    
    del posts[pid]

    return True
"""

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

""" routersAuth.py
@app2.post("/auth/signup", response_model = UserOut)
def signup(payload: SignUpIn):
    u = ctrlSignup(payload.email, payload.password, payload.nickname)

    return {k: u[k] for k in ["id", "email", "nickname", "createdAt"]}

@app2.post("/auth/login")
def login(payload: LoginIn):
    token = ctrlLogin(payload.email, payload.password)

    return {"access_token": token, "token_type": "bearer"}

@app2.get("/auth/check", response_model = UserOut)
def authCheck(current = Depends(getCurrentUser)):
    return {k: current[k] for k in ["id", "email", "nickname", "createdAt"]}

@app2.get("/auth/check-email")
def checkEmail(email: str):
    try:
        e = normalizeEmail(email)
    except HTTPException as ex:
        return {"available": False, "message": ex.detail}
    
    if e in emails:
        return {"available": False, "message": "*중복된 이메일 입니다."}
    
    return {"available": True, "message": ""}

@app2.get("/auth/check-nickname")
def checkNickname(nickname: str):
    try:
        validateNickname(nickname)
    except HTTPException as ex:
        return {"available": False, "message": ex.detail}
    
    if nicknames.get(nickname.lower()):
        return {"available": False, "message": "*중복된 닉네임 입니다."}
    
    return {"available": True, "message": ""}

@app2.get("/users/me", response_model = UserOut)
def getMe(current = Depends(getCurrentUser)):
    return {k: current[k] for k in ["id", "email", "nickname", "createdAt"]}

@app2.put("/users/me", response_model = UserOut)
def updateMe(update: UserUpdate, current = Depends(getCurrentUser)):
    u = ctrlUpdateUser(current["id"], update.nickname)
    
    return {k: u[k] for k in ["id", "email", "nickname", "createdAt"]}

@app2.post("/users/me/avatar")
def uploadAvatar(file: UploadFile = File(...), current = Depends(getCurrentUser)):
    content = file.file.read()
    current["avatar"] = {"filename": file.filename, "bytes": content}
    
    return {"ok": True, "filename": file.filename}

@app2.delete("/users/me/avatar")
def deleteAvatar(current = Depends(getCurrentUser)):
    current["avatar"] = None
    
    return {"ok": True}

@app2.post("/auth/change-password")
def changePassword(body: PasswordChangeIn, current = Depends(getCurrentUser)):
    
    if not pwdContext.verify(body.currentPassword, current["passwordHash"]):
        raise HTTPException(400, "*비밀번호 확인과 다릅니다.")
    
    validatePassword(body.newPassword)
    current["passwordHash"] = pwdContext.hash(body.newPassword)
    
    return {"ok": True}

@app2.delete("/users/me")
def deleteMe(current = Depends(getCurrentUser)):
    uid = current["id"]

    for t, u in list(sessions.items()):
        if u == uid:
            del sessions[t]

    emails.pop(current["email"], None)
    nicknames.pop(current["nickname"].lower(), None)
    users.pop(uid, None)

    return {"ok": True}
"""

""" routersPosts.py
@app2.get("/posts", response_model = List[PostOut])
def listPosts(skip: int = 0, limit: int = 20, q: Optional[str] = None):
    return ctrlListPosts(skip, limit, q)

@app2.post("/posts", response_model = PostOut)
def createPost(p: PostCreate, current = Depends(getCurrentUser)):
    return ctrlCreatePost(current["id"], p.title, p.body)

@app2.get("/posts/{postId}", response_model = PostOut)
def getPost(postId: int):
    p = ctrlGetPost(postId)
    p["views"] = p.get("views", 0) + 1

    return p

@app2.put("/posts/{postId}", response_model = PostOut)
def updatePost(postId: int, p: PostCreate, current = Depends(getCurrentUser)):
    return ctrlUpdatePost(postId, current["id"], p.title, p.body)

@app2.post("/posts/{postId}/like")
def toggleLike(postId: int, current = Depends(getCurrentUser)):
    p = ctrlGetPost(postId)
    uid = current["id"]
    s = likes.setdefault(postId, set())
    
    if uid in s:
        s.remove(uid)
        p["likesCount"] = max(0, p.get("likesCount", 0) - 1)
        liked = False
    else:
        s.add(uid)
        p["likesCount"] = p.get("likesCount", 0) + 1
        liked = True
    
    return {"liked": liked, "likesCount": p["likesCount"]}


@app2.delete("/posts/{postId}")
def deletePost(postId: int, current = Depends(getCurrentUser)):
    ctrlDeletePost(postId, current["id"])
    
    return {"ok": True}

@app2.get("/posts/{postId}/comments", response_model = List[CommentOut])
def listComments(postId: int):
    ctrlGetPost(postId)
    data = list(comments.get(postId, {}).values())
    data.sort(key = lambda x: x["createdAt"])

    return data

@app2.post("/posts/{postId}/comments", response_model = CommentOut)
def createComment(postId: int, c: CommentCreate, current = Depends(getCurrentUser)):
    p = ctrlGetPost(postId)
    global commentSeq
    commentSeq += 1
    cid = commentSeq
    now = datetime.now(timezone.utc)
    item = {
        "id": cid,
        "postId": postId,
        "authorId": current["id"],
        "text": c.text.strip(),
        "createdAt": now,
        "updatedAt": now,
    }
    comments.setdefault(postId, {})[cid] = item
    p["commentsCount"] = p.get("commentsCount", 0) + 1

    return item

@app2.put("/posts/{postId}/comments/{commentId}", response_model = CommentOut)
def updateComment(postId: int, commentId: int, c: CommentCreate, current = Depends(getCurrentUser)):
    ctrlGetPost(postId)
    postComments = comments.get(postId, {})
    item = postComments.get(commentId)
    
    if not item:
        raise HTTPException(404, "댓글을 찾을 수 없습니다.")
    
    if item["authorId"] != current["id"]:
        raise HTTPException(403, "수정 권한이 없습니다.")
    
    item["text"] = c.text.strip()
    item["updatedAt"] = datetime.now(timezone.utc)
    
    return item

@app2.delete("/posts/{postId}/comments/{commentId}")
def deleteComment(postId: int, commentId: int, current = Depends(getCurrentUser)):
    p = ctrlGetPost(postId)
    postComments = comments.get(postId, {})
    item = postComments.get(commentId)

    if not item:
        raise HTTPException(404, "댓글을 찾을 수 없습니다.")
    
    if item["authorId"] != current["id"]:
        raise HTTPException(403, "삭제 권한이 없습니다.")
    
    del postComments[commentId]
    p["commentsCount"] = max(0, p.get("commentsCount", 0) - 1)
    
    return {"ok": True}

@app2.post("/posts/{postId}/image")
def uploadPostImage(postId: int, file: UploadFile = File(...), current = Depends(getCurrentUser)):
    p = ctrlGetPost(postId)

    if p["authorId"] != current["id"]:
        raise HTTPException(403, "권한이 없습니다.")
    
    content = file.file.read()
    postImages[postId] = {"filename": file.filename, "bytes": content}

    return {"ok": True, "filename": file.filename}

@app2.get("/posts/{postId}/image")
def getPostImage(postId: int):
    item = postImages.get(postId)
    
    if not item:
        raise HTTPException(404, "이미지가 없습니다.")
    
    mime, _ = mimetypes.guess_type(item["filename"])
    
    return StreamingResponse(io.BytesIO(item["bytes"]), media_type = mime or "application/octet-stream")

@app2.delete("/posts/{postId}/image")
def deletePostImage(postId: int, current = Depends(getCurrentUser)):
    p = ctrlGetPost(postId)
    
    if p["authorId"] != current["id"]:
        raise HTTPException(403, "권한이 없습니다.")
    
    postImages.pop(postId, None)
    
    return {"ok": True}
"""

def errorPayload(code: str, message: str, fields: dict | None = None):
    body = {"ok": False, "error": {"code": code, "message": message}}
    
    if fields:
        body["error"]["fields"] = fields
    
    return body

@app.exception_handler(HTTPException)
async def httpExceptionHandler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "HTTP_ERROR")
        message = exc.detail.get("message", "요청 처리 중 오류가 발생했습니다.")
        fields = exc.detail.get("fields")
    else:
        code = "HTTP_ERROR"
        message = str(exc.detail) if exc.detail else "요청 처리 중 오류가 발생했습니다."
        fields = None
    
    return JSONResponse(status_code = exc.status_code, content = errorPayload(code, message, fields))

@app.exception_handler(RequestValidationError)
async def validationExceptionHandler(request: Request, exc: RequestValidationError):
    fields = {}
    
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []) if x != "body")
        fields[loc or "body"] = err.get("msg", "유효하지 않은 값입니다.")
    
    return JSONResponse(
        status_code = 422,
        content = errorPayload("VALIDATION_ERROR", "입력값을 확인해주세요.", fields),
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code = 500,
        content = errorPayload("INTERNAL_ERROR", "서버 내부 오류가 발생했습니다."),
    )

def customOpenapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapiSchema = get_openapi(title = app.title, version = app.version, routes = app.routes)
    openapiSchema.setdefault("components", {}).setdefault("securitySchemes", {})
    openapiSchema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http", "scheme": "bearer", "bearerFormat": "JWT",
    }
    openapiSchema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapiSchema
    return app.openapi_schema

app.openapi = customOpenapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host = "0.0.0.0", port = 8006, reload = True)
