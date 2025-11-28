# routersPosts.py

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
import io, mimetypes, storage
from deps import getCurrentUser
from schemas import PostCreate, PostOut, CommentCreate, CommentOut
from controllersPosts import ctrlListPosts, ctrlCreatePost, ctrlGetPost, ctrlUpdatePost, ctrlDeletePost
from storage import likes, comments, postImages
from typing import Optional, List
from datetime import datetime, timezone
from utils import notFound, forbidden


router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("", response_model = List[PostOut])
def listPosts(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=1000), q: Optional[str] = None,):
    return ctrlListPosts(skip, limit, q)

@router.post("", response_model = PostOut)
def createPost(p: PostCreate, current = Depends(getCurrentUser)):
    return ctrlCreatePost(current["id"], p.title, p.body)

@router.get("/{postId}", response_model = PostOut)
def getPost(postId: int):
    p = ctrlGetPost(postId)
    p["views"] = p.get("views", 0) + 1

    return p

@router.put("/{postId}", response_model = PostOut)
def updatePost(postId: int, p: PostCreate, current = Depends(getCurrentUser)):
    return ctrlUpdatePost(postId, current["id"], p.title, p.body)

@router.post("/{postId}/like")
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


@router.delete("/{postId}")
def deletePost(postId: int, current = Depends(getCurrentUser)):
    ctrlDeletePost(postId, current["id"])
    
    return {"ok": True}

@router.get("/{postId}/comments", response_model = List[CommentOut])
def listComments(postId: int):
    ctrlGetPost(postId)
    data = list(comments.get(postId, {}).values())
    data.sort(key = lambda x: x["createdAt"])

    return data

@router.post("/{postId}/comments", response_model = CommentOut)
def createComment(postId: int, c: CommentCreate, current = Depends(getCurrentUser)):
    p = ctrlGetPost(postId)
    storage.commentSeq += 1
    cid = storage.commentSeq
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

@router.put("/{postId}/comments/{commentId}", response_model = CommentOut)
def updateComment(postId: int, commentId: int, c: CommentCreate, current = Depends(getCurrentUser)):
    ctrlGetPost(postId)
    postComments = comments.get(postId, {})
    item = postComments.get(commentId)
    
    if not item:
        notFound("댓글을 찾을 수 없습니다.")
    
    if item["authorId"] != current["id"]:
        forbidden("수정 권한이 없습니다.")
    
    item["text"] = c.text.strip()
    item["updatedAt"] = datetime.now(timezone.utc)
    
    return item

@router.delete("/{postId}/comments/{commentId}")
def deleteComment(postId: int, commentId: int, current = Depends(getCurrentUser)):
    p = ctrlGetPost(postId)
    postComments = comments.get(postId, {})
    item = postComments.get(commentId)

    if not item:
        notFound("댓글을 찾을 수 없습니다.")
    
    if item["authorId"] != current["id"]:
        forbidden("삭제 권한이 없습니다.")
    
    del postComments[commentId]
    p["commentsCount"] = max(0, p.get("commentsCount", 0) - 1)
    
    return {"ok": True}

@router.post("/{postId}/image")
def uploadPostImage(postId: int, file: UploadFile = File(...), current = Depends(getCurrentUser)):
    p = ctrlGetPost(postId)

    if p["authorId"] != current["id"]:
        forbidden("권한이 없습니다.")
    
    content = file.file.read()
    postImages[postId] = {"filename": file.filename, "bytes": content}

    return {"ok": True, "filename": file.filename}

@router.get("/{postId}/image")
def getPostImage(postId: int):
    item = postImages.get(postId)
    
    if not item:
        notFound("이미지가 없습니다.")
    
    mime, _ = mimetypes.guess_type(item["filename"])
    
    return StreamingResponse(io.BytesIO(item["bytes"]), media_type = mime or "application/octet-stream")

@router.delete("/{postId}/image")
def deletePostImage(postId: int, current = Depends(getCurrentUser)):
    p = ctrlGetPost(postId)
    
    if p["authorId"] != current["id"]:
        forbidden("권한이 없습니다.")
    
    postImages.pop(postId, None)
    
    return {"ok": True}