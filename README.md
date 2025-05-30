# 오셀로 알고리즘 프로젝트 (Othello Fusion Algorithm)

이 프로젝트는 Minimax, 딥러닝 등의 탐색 기반 또는 인공지능 기반 기법 없이, 순수한 규칙 기반 휴리스틱을 활용하여 가장 높은 승률을 내는 오셀로 알고리즘을 구현하는 것을 목표로 합니다.

총 4명의 팀원이 각각 자신만의 오셀로 알고리즘을 구현하여 브랜치에 올리고, 다양한 상대 알고리즘(랜덤, 그리디, Minimax 등)과 대결을 통해 가장 높은 승률을 기록한 알고리즘을 메인 브랜치(main.py)에 반영하는 방식으로 운영됩니다.

---

## 📁 프로젝트 디렉토리 구조

```
algorithm_othello_project/
├── main.py              # 현재 기준으로 가장 승률이 높은 알고리즘
├── core/
│   ├── evaluator.py     # 점수 계산 로직 모듈
│   └── engine.py        # 게임 규칙, 돌 뒤집기 등의 핵심 로직
├── algorithms/
│   ├── algo_유진영.py        # 유진영의 오셀로 알고리즘
│   ├── algo_우민성.py        # 우민성의 오셀로 알고리즘
│   ├── algo_김도윤.py        # 김도윤의 오셀로 알고리즘
│   └── algo_김지재.py        # 김지재의 오셀로 알고리즘
├── history_log.md       # 알고리즘 변경 이력 및 승률 기록
├── README.md            # 프로젝트 설명
└── requirements.txt     # (필요 시) 의존 패키지 목록 -> 알고리즘 실행 시 특이적을 설치해야 하는 패키지를 적어주세요.
```

---

## ✅ 개발 및 운영 방침

- 각자 본인의 알고리즘을 `feature/algo-이니셜` 브랜치에서 개발합니다.
  - 예: `feature/algo-a`, `feature/algo-b` 등
- 작성한 알고리즘은 상대 알고리즘들과 대전시켜 **승률을 측정**합니다.
- **승률이 가장 높은 버전만 `main.py`에 반영**됩니다.
- 새로운 아이디어로 기존 알고리즘을 개선해 더 나은 승률을 기록하면 다시 `main.py`를 갱신합니다.
- `main.py` 변경 시 반드시 `history_log.md`에 변경 내용을 기록합니다.

---

## 📝 변경 이력 기록 템플릿 (history_log.md)

`main.py`가 수정될 때마다 다음 형식으로 기록합니다:

```
### [날짜: 2025-06-01]
**승률:** 86.4% (vs Minimax v4 기준)
**작성자:** @github_id
**기반 알고리즘:** algo_c.py
**변경 요약:**
- 안정성 점수 가중치 상향 (+200 → +1000)
- mobility penalty 추가
- X-square 회피 전략 적용
```

---

## 🔧 실행 방법

```bash
python main.py
```

또는 특정 알고리즘을 테스트하고 싶을 경우:
```bash
python algorithms/algo_b.py
```

---

## 👨‍👩‍👧‍👦 팀원 (GitHub ID 기준)
- 팀원 A: @github_id
- 팀원 B: @github_id
- 팀원 C: @github_id
- 팀원 D: @github_id
