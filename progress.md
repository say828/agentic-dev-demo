# Progress

> 이 저장소의 데모들은 **정답지(answer key)** 역할을 한다. 각 데모는 별도 브랜치에서
> 완성되며, **나중에 PR 형태로 합칠** 예정이다(현 시점 미병합).

## cyworld — 싸이월드 미니홈피 (백엔드-온리 · 로컬 · SDD)
- **성격: 정답지.** 강의 단계별 완성 기준이 되는 레퍼런스 구현.
- **병합 계획: PR로 추후 병합.** 브랜치 `cyworld` (← `main` 분기). 아직 main 미병합.
- 폴더: `cyworld/` (`auth` 형제). SDD 풀 스캐폴드(00_sources→05_operate + 99_toolchain).
- 도메인 핵심: 도토리 경제(충전·구매·잔액부족·이중결제 멱등) / 일촌 신청→수락 양방향 /
  투데이 멱등 집계 / 미니홈피 화면 parity / 방명록(회귀).
- 게이트(녹색): build OK · `proof` 16/16 PASS · `ui_parity` 1/1 (exit 0).
- rollout: 미수행(배포 미요청).
- PR 시 유의: `cyworld/.claude`·`.codex`는 `auth`에서 복사한 SDD 스킬 사본 — 리뷰 시 중복 여부 확인.

## pinterest — 핀터레스트 보드 (참고: 다른 브랜치)
- 브랜치 `pinterest`. 폴더 `pinterest/`. 게이트: proof 13/13 · ui_parity 1/1.
- 역시 정답지 성격이며 별도 PR 대상.

## 공통 환경 경계 (정직)
브라우저·Docker·CI 비가용 → 백엔드 로직은 결정적 pytest, 화면은 HTML 스냅샷 parity,
배포는 로컬 스텁/미수행으로 대체(슬라이드 명시 경계).
