# controllersPosts.py

from datetime import datetime, timezone
from fastapi import HTTPException
from typing import Optional, Dict, Any, List
from storage import posts, comments, likes, postImages, postSeq, commentSeq
from utils import notFound, forbidden, badRequest
from models.posts import listPosts, createPost, getPost, updatePost, deletePost, incView
from ai import check_toxicity
from sqlalchemy.orm import Session

def _requirePost(db: Session, pid: int) -> Dict[str, Any]:
    p = getPost(db, pid)

    if not p:
        notFound("게시글을 찾을 수 없습니다.")

    return p


def ctrlListPosts(db: Session, skip: int, limit: int, q: Optional[str]):
    return listPosts(db, skip, limit, q)


def ctrlCreatePost(db: Session, authorId: int, title: str, body: str):
    _ensure_not_toxic(body, field="body")

    return createPost(db, authorId, title, body)

def ctrlGetPost(db: Session, pid: int):
    try:
        views = incView(db, pid)
    except KeyError:
        notFound("게시글을 찾을 수 없습니다.")

    p = getPost(db, pid)
    
    if not p:
        notFound("게시글을 찾을 수 없습니다.")

    p["views"] = views
    
    return p

def ctrlIncView(pid: int) -> int:
    _requirePost(pid)
    return incView(pid)

def ctrlUpdatePost(db: Session, pid: int, authorId: int, title: str, body: str):
    p = _requirePost(db, pid)

    if p["authorId"] != authorId:
        forbidden("수정 권한이 없습니다.")

    _ensure_not_toxic(body, field="body")

    return updatePost(db, pid, title, body)

def ctrlDeletePost(db: Session, pid: int, authorId: int):
    p = _requirePost(db, pid)

    if p["authorId"] != authorId:
        forbidden("삭제 권한이 없습니다.")

    return deletePost(db, pid)

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