# modelsPosts.py
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Set
from storage import posts, comments, likes, postImages, postSeq, commentSeq

def listPosts(skip: int, limit: int, q: Optional[str]) -> List[Dict[str, Any]]:
    data = list(posts.values())
    if q:
        key = q.strip().lower()
        data = [p for p in data if key in p["title"].lower() or key in p["body"].lower()]
    data.sort(key=lambda x: x["createdAt"], reverse=True)
    return data[skip: skip + limit]

def createPost(authorId: int, title: str, body: str) -> Dict[str, Any]:
    global postSeq
    postSeq += 1
    pid = postSeq
    now = datetime.now(timezone.utc)
    post = {
        "id": pid, "title": title.strip(), "body": body.strip(),
        "authorId": authorId, "createdAt": now, "updatedAt": now,
        "views": 0, "likesCount": 0, "commentsCount": 0,
    }
    posts[pid] = post
    likes[pid] = set()
    comments[pid] = {}
    return post

def getPost(pid: int) -> Optional[Dict[str, Any]]:
    return posts.get(pid)

def updatePost(pid: int, title: str, body: str) -> Dict[str, Any]:
    p = posts[pid]
    p["title"] = title.strip()
    p["body"]  = body.strip()
    p["updatedAt"] = datetime.now(timezone.utc)
    return p

def deletePost(pid: int) -> bool:
    posts.pop(pid, None)
    comments.pop(pid, None)
    likes.pop(pid, None)
    postImages.pop(pid, None)
    return True

def incView(pid: int) -> int:
    p = posts[pid]
    p["views"] = p.get("views", 0) + 1
    return p["views"]

def toggleLike(pid: int, uid: int) -> Dict[str, Any]:
    s: Set[int] = likes.setdefault(pid, set())
    p = posts[pid]
    if uid in s:
        s.remove(uid)
        p["likesCount"] = max(0, p.get("likesCount", 0) - 1)
        liked = False
    else:
        s.add(uid)
        p["likesCount"] = p.get("likesCount", 0) + 1
        liked = True
    return {"liked": liked, "likesCount": p["likesCount"]}

def listComments(pid: int) -> List[Dict[str, Any]]:
    data = list(comments.get(pid, {}).values())
    data.sort(key=lambda x: x["createdAt"])
    return data

def createComment(pid: int, uid: int, text: str) -> Dict[str, Any]:
    global commentSeq
    commentSeq += 1
    cid = commentSeq
    now = datetime.now(timezone.utc)
    item = {"id": cid, "postId": pid, "authorId": uid,
            "text": text.strip(), "createdAt": now, "updatedAt": now}
    comments.setdefault(pid, {})[cid] = item
    posts[pid]["commentsCount"] = posts[pid].get("commentsCount", 0) + 1
    return item

def updateComment(pid: int, cid: int, text: str) -> Dict[str, Any]:
    item = comments[pid][cid]
    item["text"] = text.strip()
    item["updatedAt"] = datetime.now(timezone.utc)
    return item

def deleteComment(pid: int, cid: int) -> bool:
    if cid in comments.get(pid, {}):
        del comments[pid][cid]
        posts[pid]["commentsCount"] = max(0, posts[pid].get("commentsCount", 0) - 1)
        return True
    return False

def putImage(pid: int, filename: str, content: bytes) -> Dict[str, Any]:
    postImages[pid] = {"filename": filename, "bytes": content}
    return {"ok": True, "filename": filename}

def getImage(pid: int) -> Optional[Dict[str, Any]]:
    return postImages.get(pid)

def deleteImage(pid: int) -> bool:
    postImages.pop(pid, None)
    return True
