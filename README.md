# DB 강의 교재 · 슬라이드 템플릿

원고(`content/unitXX.md`) 한 벌로 **교재 페이지**와 **강의 슬라이드**를 함께 만듭니다.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # 처음 한 번
.venv/bin/python build.py                                            # dist/ 생성
python3 -m http.server -d dist 8000                                  # http://localhost:8000
```

- `course.json` — 과정 이름과 단원 목록. 원고 파일이 없는 단원은 "준비 중"으로 표시됩니다.
- `content/unit01.md` — 원고 문법 예시를 모두 담은 샘플. 문법 요약은 `build.py` 맨 위 주석에 있습니다.
- `assets/` — 스타일(`style.css`), 공통 동작(`common.js`), 슬라이드 넘기기(`slides.js`).
- `images/` — 삽화. 빌드할 때 `dist/images/`로 복사됩니다.

슬라이드: ←·→ 넘기기(stepper가 있으면 stepper를 먼저 한 단계씩), F 전체 화면, 주소의 `#번호`로 바로 이동.
배포는 `dist/` 폴더를 Vercel·GitHub Pages에 올리면 됩니다.
