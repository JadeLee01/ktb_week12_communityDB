# modelsPosts.py

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from db_models import Post


def post_to_dict(post: Post) -> Dict[str, Any]:
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "authorId": post.authorId,
        "createdAt": post.createdAt,
        "updatedAt": post.updatedAt,
        "views": post.views or 0,
        "likesCount": post.likesCount or 0,
        "commentsCount": post.commentsCount or 0,
    }


def listPosts(db: Session, skip: int, limit: int, q: Optional[str]) -> List[Dict[str, Any]]:
    query = db.query(Post)
    if q:
        key = f"%{q.strip().lower()}%"
        query = query.filter(
            (Post.title.ilike(key)) | (Post.body.ilike(key))
        )

    posts = (
        query.order_by(Post.createdAt.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [post_to_dict(p) for p in posts]


def createPost(db: Session, authorId: int, title: str, body: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    post = Post(
        title=title.strip(),
        body=body.strip(),
        authorId=authorId,
        createdAt=now,
        updatedAt=now,
        views=0,
        likesCount=0,
        commentsCount=0,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post_to_dict(post)


def getPost(db: Session, pid: int) -> Optional[Dict[str, Any]]:
    post = db.query(Post).filter(Post.id == pid).first()
    return post_to_dict(post) if post else None


def updatePost(db: Session, pid: int, title: str, body: str) -> Dict[str, Any]:
    post = db.query(Post).filter(Post.id == pid).first()
    if not post:
        raise KeyError("Post not found")

    post.title = title.strip()
    post.body = body.strip()
    post.updatedAt = datetime.now(timezone.utc)

    db.commit()
    db.refresh(post)
    return post_to_dict(post)


def deletePost(db: Session, pid: int) -> bool:
    post = db.query(Post).filter(Post.id == pid).first()
    if not post:
        return False

    db.delete(post)
    db.commit()
    return True


def incView(db: Session, pid: int) -> int:
    post = db.query(Post).filter(Post.id == pid).first()
    if not post:
        raise KeyError("Post not found")

    post.views = (post.views or 0) + 1
    db.commit()
    db.refresh(post)
    return post.views
