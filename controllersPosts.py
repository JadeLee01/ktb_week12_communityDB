# controllersPosts.py

from datetime import datetime, timezone
from fastapi import HTTPException
from typing import Optional, Dict, Any, List
from storage import posts, comments, likes, postImages, postSeq, commentSeq
from utils import notFound, forbidden, badRequest
from modelsPosts import listPosts, createPost, getPost, updatePost, deletePost, incView, toggleLike, listComments, createComment, updateComment, deleteComment, putImage, getImage, deleteImage
from ai import check_toxicity

def _requirePost(pid: int) -> Dict[str, Any]:
    p = getPost(pid)

    if not p:
        notFound("게시글을 찾을 수 없습니다.")

    return p

def ctrlListPosts(skip: int, limit: int, q: Optional[str]):
    return listPosts(skip, limit, q)

def ctrlCreatePost(authorId: int, title: str, body: str):
    _ensure_not_toxic(title, field = "title")
    _ensure_not_toxic(body, field = "body")
    
    return createPost(authorId, title, body)

def ctrlGetPost(pid: int):
    return _requirePost(pid)

def ctrlIncView(pid: int) -> int:
    _requirePost(pid)
    return incView(pid)

def ctrlUpdatePost(pid: int, authorId: int, title: str, body: str):
    p = _requirePost(pid)

    if p["authorId"] != authorId:
        forbidden("수정 권한이 없습니다.")

    _ensure_not_toxic(title, field = "title")
    _ensure_not_toxic(body, field = "body")

    return updatePost(pid, title, body)

def ctrlDeletePost(pid: int, authorId: int):
    p = _requirePost(pid)

    if p["authorId"] != authorId:
        forbidden("삭제 권한이 없습니다.")

    return deletePost(pid)

def ctrlListComments(pid: int):
    _requirePost(pid)

    return listComments(pid)

def ctrlCreateComment(pid: int, uid: int, text: str):
    if not text or not text.strip():
        badRequest("*댓글 내용을 입력해주세요.", {"text":"required"})

    _ensure_not_toxic(text, field = "text")

    _requirePost(pid)

    return createComment(pid, uid, text)

def ctrlUpdateComment(pid: int, cid: int, uid: int, text: str):
    _requirePost(pid)
    items = {c["id"]: c for c in listComments(pid)}
    item = items.get(cid)

    if not item:
        notFound("댓글을 찾을 수 없습니다.")

    if item["authorId"] != uid:
        forbidden("수정 권한이 없습니다.")

    _ensure_not_toxic(text, field = "text")

    return updateComment(pid, cid, text)

def ctrlDeleteComment(pid: int, cid: int, uid: int):
    _requirePost(pid)
    items = {c["id"]: c for c in listComments(pid)}
    item = items.get(cid)

    if not item:
        notFound("댓글을 찾을 수 없습니다.")

    if item["authorId"] != uid:
        forbidden("삭제 권한이 없습니다.")

    return deleteComment(pid, cid)

def ctrlUploadImage(pid: int, uid: int, filename: str, content: bytes):
    p = _requirePost(pid)

    if p["authorId"] != uid:
        forbidden("권한이 없습니다.")

    return putImage(pid, filename, content)

def ctrlGetImage(pid: int):
    item = getImage(pid)

    if not item:
        notFound("이미지가 없습니다.")

    return item

def ctrlDeleteImage(pid: int, uid: int):
    p = _requirePost(pid)

    if p["authorId"] != uid:
        forbidden("권한이 없습니다.")

    return deleteImage(pid)

def _ensure_not_toxic(text: str, field: str = "text"):
    result = check_toxicity(text)

    if result["isToxic"]:
        fields = {
            "reason": "toxic_language",
            "score": result["score"],
            "label": result["label"],
            "field": field,
        }
        badRequest("*부적절한 표현이 포함되어 있습니다. 내용을 수정해주세요.", fields)