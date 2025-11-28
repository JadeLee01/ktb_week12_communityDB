# storage.py
from typing import Dict, Any, Set

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