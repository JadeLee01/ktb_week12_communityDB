# FastAPI Community Backend with Database Integration

기존 FastAPI 커뮤니티 백엔드에서 메모리 기반 저장 방식을
SQLite 데이터베이스 기반으로 확장한 프로젝트입니다.

## Features
- 게시글 CRUD (SQLite)
- 조회수 증가 DB 반영
- SQLAlchemy ORM 사용
- AI 유해 표현 검사 연동 유지
- 전 API 공통 예외 처리 구조 적용

## Tech Stack
- FastAPI
- SQLite
- SQLAlchemy
- PyTorch
- HuggingFace Transformers
- Postman

## Notes
- 데이터베이스 파일(.db)은 GitHub에 포함하지 않았습니다.
- 모든 API는 Postman 요청 시 정상/비정상 케이스에 대한 예외 처리가 구현되어 있습니다.
