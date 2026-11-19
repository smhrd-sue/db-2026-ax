---
label: 11. 미니프로젝트
title: 생산DB × Python 미니프로젝트
---

# 업무 지시를 SQL과 Python으로 보고하기

:::goal
- 말로 받은 업무 지시를 「필요한 테이블·컬럼·계산식」으로 바꿀 수 있습니다.
- SQL로 값을 꺼내고, Python으로 받아 검산하고 그래프로 그릴 수 있습니다.
- 결과를 「결론 1문장 + 근거 수치 + 차트 1개」로 보고할 수 있습니다.
- 수행 과정을 채용 담당자가 읽을 수 있는 포트폴리오(보고서 + 정리된 프로젝트 폴더)로 정리할 수 있습니다.
:::

:::teacher 단원 구성 (4시간)
- 이 페이지는 **훈련생 안내용**입니다. 미션별 검산값과 모범 풀이(노트북·SQL·보고서 가안)는 여기에 싣지 않았습니다. 강사용 검증 기록 `review/03-미니프로젝트-모범답안검증.md`를 참고하세요.
- 실습 자료는 모두 Google Drive 폴더 한 곳에서 받습니다(4-6·5-1의 링크): 적재 스크립트 `14. 생산DB_Python연동.sql`, `양식.zip`(프로젝트 폴더 양식 — 보고서 양식·시작 노트북 포함), `예시.zip`(완성된 미션 3개 예시). 수업 전에 이 파일들이 폴더에 있는지 확인하고, 강사 PC에서 먼저 적재해 4-6의 행 수가 맞는지 확인합니다. 적재 스크립트는 저장소 `csv/` 폴더에 있습니다.
- 브리핑 15분 안에 5-4 연결 셀로 `q()` 결과가 표로 나오는 것까지 시연합니다. 연결이 되면 그 뒤는 배운 pandas 그대로입니다.
- 트랙은 훈련생이 고르고, 관찰한 수준을 바탕으로 조정을 권합니다. 1시간 안에 끝낸 훈련생은 위 트랙 첫 미션, 진도가 늦은 훈련생은 미션 2개를 끝낸 뒤 포트폴리오로 넘어가게 안내합니다.
- 상-1 판정 기준은 훈련생이 정합니다. 막힐 때만 예시 기준을 말로 알려 줍니다.
- 순회할 때 IDE의 AI 기능·에이전트 창이 켜져 있는지 보고, 제출 뒤 1~2명에게 쿼리 한 줄의 의도를 물어봅니다.
- 결과물은 **훈련생 PC의 프로젝트 폴더**로 완성합니다. GitHub 업로드는 선택 사항(11-5)이므로, 제출 방법(압축 파일, 공유 폴더 등)은 수업에서 따로 안내합니다.

| 시간 | 구분 | 내용 | 해당 장 |
| --- | --- | --- | --- |
| 0:00~0:15 | 브리핑 | 시나리오 소개, DB 적재·Python 연결 확인 | 1~5 |
| 0:15~1:45 | 분석 미션 | 트랙 선택 후 미션 3개 | 6~9 |
| 1:45~2:00 | 중간 보고 | 미션 1개를 골라 1분 구두 보고 | 10 |
| 2:00~2:10 | 휴식 | — | — |
| 2:10~3:40 | 포트폴리오 | 폴더 정리, 보고서·README 작성, 마무리 점검 | 11 |
| 3:40~4:00 | 상호 리뷰 | 2인 1조 체크리스트 점검 후 수정 | 12 |
:::

## 1. 프로젝트 한눈에 보기

### 1-1. 무엇을 하나요 {keep}

팀장에게 **말로 받은 지시**를 데이터로 풀어 보고하는 4시간 프로젝트입니다. SQL 수업에서 배운 쿼리와 Python 수업에서 배운 pandas·matplotlib을 처음으로 **한 흐름으로 이어서** 씁니다.

| 항목 | 내용 |
| --- | --- |
| 주제 | 상사 지시 기반 생산·인사 데이터 추출·시각화 보고 |
| 시간 | 총 4시간 = 분석 미션 2시간 + 포트폴리오 정리 2시간 |
| 데이터 | 가상의 가전 조립공장, 2026년 10월 (합성 데이터) — 생산 데이터 + 같은 공장의 인사·근태 데이터 |
| 환경 | PostgreSQL(pgAdmin) + Python(Jupyter, pandas, SQLAlchemy, matplotlib) |
| 방식 | 하·중·상 트랙 중 하나를 골라 미션 3개 수행 (생산 미션 2개 + 인사·근태 미션 1개) |

### 1-2. 최종 산출물 {keep}

```icons 제출하는 것 네 가지
notebook-pen | 분석 노트북 | `notebooks/` 안의 `.ipynb` — 처음부터 다시 실행해도 오류가 없어야 합니다 | rose
database | 미션별 SQL 파일 | `sql/` 폴더 — SQL 역량을 보여 주는 근거 | plum
chart-column | 차트 이미지 | `images/` 폴더의 png — 미션마다 1개 이상 | lime
file-text | 포트폴리오 | `report.html`(본문) + `README.md`(요약) — 내 PC의 프로젝트 폴더에 정리 (GitHub 업로드는 선택) | ivory
```

## 2. AI 활용 규칙 (필수)

### 2-1. 코드는 내가 씁니다 {keep}

이 프로젝트는 ==본인이 직접 SQL과 Python 코드를 작성하는 역량==을 확인합니다. 코드는 모두 본인이 작성하고, AI는 **브라우저 채팅 창에서 개념을 묻는 용도로만** 씁니다.

| 구분 | 허용 | 금지 |
| --- | --- | --- |
| 개념 | "LEFT JOIN과 INNER JOIN 차이가 뭐야?", "파레토 차트가 뭐야?" | — |
| 문법 | "WITH로 만든 결과를 JOIN하는 문법 알려줘", "pandas groupby 사용법" | 미션에 맞춘 쿼리·코드 작성 요청 |
| 오류 | 오류 메시지 문구만 붙여 넣고 "무슨 뜻이야?" | 내 코드 전체를 붙여 넣고 "고쳐줘" |
| 미션 | — | 팀장 지시문·테이블 구조를 붙여 넣고 풀이 요청 |
| 도구 | 브라우저 채팅 창(Claude, ChatGPT 등) | IDE 자동완성(Copilot, Cursor 등), 코딩 에이전트, 노트북 안의 AI 기능 |
| 포트폴리오 | 맞춤법·문장 다듬기 질문 | 보고서·README 본문 작성 요청 |

### 2-2. 헷갈릴 때의 판단 기준 {keep}

```compare 이 질문, 해도 될까요?
ban | 금지 질문 || check | 허용 질문
ban | AI의 답변을 **복사해 그대로 붙여 넣을 수 있다** || check | 답변을 읽고 **내 코드에 맞게 다시 써야 한다**
ban | "production_result로 라인별 불량률 구하는 쿼리 짜줘" || check | "정수끼리 나누면 왜 0이 나와?"
```

상호 리뷰 때 짝에게 미션 1개의 쿼리를 **본인 말로 설명**합니다. ==설명할 수 없는 코드는 본인 코드로 보지 않습니다.==

### 2-3. AI 질문 로그 {keep}

AI에게 한 질문은 노트북 **맨 마지막**의 `AI 질문 로그` 마크다운 셀에 그때그때 적습니다. 양식 노트북 맨 끝에 표가 준비되어 있습니다.

```text 형식: 시각 | 질문 요지 | 알게 된 것 | 내 코드에 어떻게 적용했는지
14:20 | 정수끼리 나누면 왜 0이 나오는지 | 정수 ÷ 정수는 몫만 남음 | 비율 계산에 100.0을 곱해 소수로 계산
14:45 | 축 글자를 돌리는 방법 | tick_params의 rotation | 날짜 축 글자를 45도 회전
```

- 이 로그가 보고서의 **트러블슈팅**과 **회고**의 재료가 됩니다.
- 질문을 하나도 하지 않았다면 「질문 없음」이라고 적습니다. 로그가 코드 수준과 맞지 않으면 강사가 따로 물어볼 수 있습니다.

### 2-4. 그대로 복사해도 되는 코드 {keep}

배우지 않은 부분은 강사가 코드를 줍니다. 아래 두 가지는 ==AI 활용 규칙의 예외==로, 그대로 써도 됩니다. DB 연결 셀은 양식 노트북에 이미 들어 있습니다.

| 강사 제공 코드 | 위치 | 직접 써야 하는 부분 |
| --- | --- | --- |
| DB 연결 셀(`q`, `q_file`) | 5-4 | 그 뒤의 분석·시각화 코드 전부 |
| Python에서 한 행 INSERT 하는 문법 | 9-3 (상-1) | 판정 로직, 여러 행 넣기, 재실행 대비 |

## 3. 쓸 수 있는 것

### 3-1. 배운 범위 안에서 모두 풀 수 있습니다 {keep}

| 구분 | 배운 것 | 교안 |
| --- | --- | --- |
| Python | 변수·문자열·리스트·딕셔너리·조건문·반복문·함수·모듈·예외 처리 | ch01~ch09 |
| Python | pandas 기본(행·열 선택, sort_values, value_counts), 정제(isna, fillna, astype, to_datetime) | ch10~ch12 |
| Python | 집계(groupby, agg, nlargest, pivot_table), 결합(merge, how) | ch13~ch14 |
| Python | 시간 데이터(.dt, Timedelta, merge_asof), 시각화(subplots, plot, bar, axhline·axvline, savefig) | ch15~ch18 |
| SQL | SELECT·WHERE·ORDER BY, CASE WHEN, 날짜 연산·`::date` | 3단원 |
| SQL | 집계 함수, GROUP BY, HAVING, ROUND, `100.0`을 곱해 소수 비율 내기 | 4단원 |
| SQL | INNER·LEFT JOIN, 여러 테이블 조인 + 집계 | 5단원 |
| SQL | 서브쿼리, 인라인 뷰, WITH | 6단원 |
| SQL | INSERT·UPDATE·DELETE, BEGIN·COMMIT·ROLLBACK | 8·9단원 |

### 3-2. 배우지 않은 것은 이렇게 대신합니다 {keep}

| 하고 싶은 것 | 배우지 않은 방법 | 이번에 쓰는 방법 |
| --- | --- | --- |
| DB에 접속해 결과 받기 | SQLAlchemy, read_sql, .env | 5-4 강사 제공 코드를 복사 |
| 그룹 안 순위·누적 비율 | 윈도우 함수(`RANK`, `SUM OVER`) | 합계는 WITH·서브쿼리로, 순위·누적은 pandas(nlargest, 반복문)로 |
| NULL을 0으로 | `COALESCE` | pandas `fillna(0)` 또는 SQL `CASE WHEN … IS NULL THEN 0` |
| "고장 6시간 전" 같은 시간 구간 | `INTERVAL` | SQL로는 기록만 꺼내고, 구간은 pandas `Timedelta`로 거르기 |
| 다시 실행해도 오류 없이 기록 | `INSERT … ON CONFLICT` | 한 트랜잭션에서 DELETE 후 INSERT (8·9단원) |
| 단위가 다른 두 값을 한 그래프에 | 보조축 `twinx` | `subplots`로 위아래 그래프를 쌓기(`sharex=True`) 또는 표로 함께 제시 |

> **SQL과 pandas 중 무엇으로 할까요?** 값을 꺼내는 일은 SQL로 하고, 순위·비율·시간 구간 처리는 SQL과 pandas 중 편한 쪽으로 해도 됩니다. 어느 쪽으로 했는지는 보고서에 적습니다.

### 3-3. 미션별 참고 교안 {keep}

| 미션 | Python에서 쓸 기능 | 참고 교안 |
| --- | --- | --- |
| 하-1 | DataFrame 확인, bar | ch11, ch17 |
| 하-2 | DataFrame 확인, subplots, 막대 | ch11, ch17 |
| 하-3 | plot, axhline(계획 기준선) | ch17 |
| 중-1 | pivot_table(라인 × 교대), bar | ch13, ch17 |
| 중-2 | nlargest 또는 groupby + head, 누적 합, bar | ch13, ch17 |
| 중-3 | pivot_table(라인 × 교대), value_counts, 막대 | ch11, ch13, ch17 |
| 상-1 | groupby + mean·std, 함수로 판정, apply | ch07, ch13, ch18 |
| 상-2 | Timestamp·Timedelta, 시간 범위 거르기, axvline | ch15, ch17 |
| 상-3 | merge(how), fillna, groupby, crosstab, subplots(sharex=True) | ch12, ch13, ch14, ch17 |

## 4. 데이터 — 가전 조립공장의 10월

### 4-1. 어떤 공장인가요 {keep}

냉장고·세탁기·에어컨을 조립하는 **가상의 공장**입니다. 2026년 10월 한 달 동안 라인 3개가 주간·야간 2교대로 돌아간 **생산 기록**과, 그 라인에서 일한 현장 직원 70명의 **인사·근태 기록**이 함께 들어 있습니다. 실제 공장 수치가 아닌 ==합성 데이터==입니다.

```stats 데이터 규모
factory | 3 | 라인
wrench | 9 | 설비
users | 70 | 현장 직원
table | 11 | 테이블
clock | 27 | 가동일
```

| 라인 | 제품 | 교대당 계획 |
| --- | --- | --- |
| L1 | 냉장고 | 400대 |
| L2 | 세탁기 | 450대 |
| L3 | 에어컨 | 350대 |

### 4-2. 생산 테이블 8개 {keep}

| 테이블 | 행 수 | 설명 | 주요 컬럼 |
| --- | --- | --- | --- |
| line_master | 3 | 라인 기준정보 | line_code, line_name, product_group, plan_per_shift |
| equipment_master | 9 | 설비 기준정보(라인별 3대) | equip_code, line_code, equip_name, process |
| model_master | 6 | 모델 기준정보 | model_code, model_name, line_code, cycle_sec |
| production_result | 162 | 교대별 생산 실적(일 × 교대 × 라인) | result_id, work_date, shift, line_code, model_code, plan_qty, prod_qty, good_qty, defect_qty, run_min, down_min |
| defect_log | 380 | 실적별 불량 유형 수량 | defect_id, result_id, defect_type, qty |
| downtime_log | 203 | 비가동 기록 | down_id, line_code, equip_code, work_date, shift, start_time, end_time, duration_min, reason |
| sensor_hourly | 5,832 | 설비 센서 1시간 평균 | equip_code, measured_at, temp_c, vibration_mm_s |
| quality_judgment | 0 | Python 판정 결과 기록용(상 트랙에서 채움) | judge_id, work_date, line_code, defect_rate, judgment, judged_by, judged_at |

### 4-3. 인사·근태 테이블 3개 {keep}

같은 공장 **현장 직원**의 데이터입니다. 직원은 10월 한 달 동안 라인과 교대조가 고정되어 있습니다.

| 테이블 | 행 수 | 설명 | 주요 컬럼 |
| --- | --- | --- | --- |
| employee_master | 70 | 현장 직원 기준정보(라인 × 교대조) | emp_no, emp_name, line_code, shift, job_role, hire_date, skill_grade |
| attendance_log | 1,890 | 일별 근태(직원 70명 × 가동일 27일) | att_id, emp_no, work_date, status |
| training_log | 91 | 교육 이수 기록 | training_id, emp_no, course_name, completed_date |

- `skill_grade`(숙련등급): **A** 숙련 · **B** 일반 · **C** 수습(입사 1년 미만)
- `status`(근태): 출근 · 지각 · 결근 · 휴가. 직원마다 가동일 하루에 한 행입니다.
- `course_name`(교육 과목): 정기 안전교육 · 신입 입문교육 · 지게차 운전 안전
- ==`training_log`에는 교육을 **이수한 사람만** 행이 있습니다.== 받지 않은 사람은 행 자체가 없습니다.

### 4-4. 테이블은 이 컬럼으로 이어집니다 {keep}

| 이 테이블의 | 이 컬럼이 | 가리키는 곳 |
| --- | --- | --- |
| equipment_master · model_master | line_code | line_master |
| production_result | line_code | line_master |
| production_result | model_code | model_master |
| defect_log | result_id | production_result |
| downtime_log | line_code | line_master |
| downtime_log | equip_code | equipment_master |
| sensor_hourly | equip_code | equipment_master |
| quality_judgment | line_code | line_master |
| employee_master | line_code | line_master |
| attendance_log | emp_no | employee_master |
| training_log | emp_no | employee_master |

`production_result` 한 행은 「어느 날, 어느 교대, 어느 라인」의 실적 한 건입니다. 162행 = 가동일 27일 × 교대 2 × 라인 3. 이 「날짜 × 교대 × 라인」 한 칸을 **근무조**라고 부릅니다. 생산 데이터와 인사 데이터는 날짜·교대·라인으로 이어 볼 수 있습니다.

### 4-5. 분석 전에 꼭 확인할 데이터 규칙 {keep}

- 기간은 2026-10-01 ~ 10-31, **일요일 휴무**(가동일 27일)입니다.
- 교대는 주간 08:00~20:00, 야간 20:00~다음 날 08:00이고 **교대당 720분**입니다.
- `prod_qty = good_qty + defect_qty` (생산 = 양품 + 불량)
- `run_min + down_min = 720` (가동 + 비가동 = 교대 시간)
- 같은 `result_id`의 `defect_log.qty` 합계 = `production_result.defect_qty`
- 불량 유형 8가지: 냉매누설, 발포불량, 브레이징불량, 소음불량, 외관불량, 용접불량, 전장불량, 체결불량
- 비가동 사유 5가지: 모델교체, 설비고장, 자재대기, 작업자부족, 품질점검. ==설비와 무관한 사유는 `equip_code`가 NULL==입니다.
- 센서가 누락된 시간은 `temp_c`가 NULL입니다.
- `attendance_log` 행 수 = 직원 70명 × 가동일 27일 = 1,890. `attendance_log`에는 라인·교대가 없습니다(직원 기준정보에 있음).

> 이 규칙들은 미션마다 하는 **검산**의 기준이 됩니다. 결과가 규칙과 맞지 않으면 쿼리를 먼저 의심하세요.

### 4-6. 적재하기 {keep}

[{{ic:download}} 실습 자료 내려받기 (Google Drive)](https://drive.google.com/drive/folders/1md9-Ybhp6Eh4BXdxjP8rpDK9AETG-u9W?usp=drive_link)에서 적재 스크립트 `14. 생산DB_Python연동.sql`을 받아 pgAdmin에서 실행합니다.

1. pgAdmin 왼쪽에서 **Servers → PostgreSQL 18 → Databases → postgres**를 선택합니다.
2. 위쪽 메뉴 **Tools → Query Tool**을 엽니다.
3. Query Tool의 **파일 열기** 버튼으로 `14. 생산DB_Python연동.sql`을 엽니다.
4. **실행(F5)** 을 눌러 전체를 실행합니다. 여러 번 실행해도 됩니다(맨 앞에서 테이블을 지우고 다시 만듭니다).

### 4-6. 적재가 끝났는지 확인하기 {keep}

스크립트 맨 끝에 행 수를 세는 쿼리가 들어 있어, 실행이 끝나면 아래 결과가 나옵니다. ==열한 줄이 모두 같으면== 적재가 끝난 것입니다.

```result
| table_name | row_count |
| --- | --- |
| line_master | 3 |
| equipment_master | 9 |
| model_master | 6 |
| production_result | 162 |
| defect_log | 380 |
| downtime_log | 203 |
| sensor_hourly | 5832 |
| quality_judgment | 0 |
| employee_master | 70 |
| attendance_log | 1890 |
| training_log | 91 |
```

### 4-7. 적재가 안 될 때 {keep}

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| 결과 표의 숫자가 다르거나 중간에 오류가 남 | 파일의 일부만 선택한 채 실행함 | 선택을 풀고(빈 곳 클릭) 전체를 다시 실행 |
| psql에서 `\i`로 실행했더니 `(인코딩: "UHC") … "UTF8" 인코딩에는 없습니다` 오류가 나고 테이블이 안 생김 | 한국어 Windows의 psql이 파일을 UHC로 읽음 | 2단원 6-2처럼 `\encoding UTF8`을 먼저 입력한 뒤 실행 |
| pgAdmin에는 테이블이 보이는데 Python에서는 없다고 함 | 적재한 데이터베이스와 접속한 데이터베이스가 다름 | 5-3의 `.env`에서 `PG_DB`를 적재한 데이터베이스 이름으로 변경 |

## 5. 준비 — 프로젝트 폴더와 DB 연결

### 5-1. 양식 폴더로 시작하기 {keep}

[{{ic:download}} 실습 자료 내려받기 (Google Drive)](https://drive.google.com/drive/folders/1md9-Ybhp6Eh4BXdxjP8rpDK9AETG-u9W?usp=drive_link)에서 `양식.zip`을 내려받아 압축을 풉니다. 그 안의 `production-db-analysis` 폴더를 **내 PC의 원하는 위치**(예: `C:\`)로 옮기면 그대로 프로젝트 폴더가 됩니다. 오늘 작업은 모두 이 폴더 안에서 하고, 이 폴더가 그대로 결과물이 됩니다. GitHub에 올리는 것은 ==선택 사항==입니다(11-5).

```text 프로젝트 폴더 (예: C:\production-db-analysis)
production-db-analysis/
├─ report.html          ← 보고서 양식 (대괄호 자리에 직접 작성)
├─ README.md            ← 프로젝트 요약 (직접 작성)
├─ requirements.txt     ← 설치할 패키지 목록
├─ .env                 ← DB 접속 정보 (내 PC에만 두는 파일) ※ 양식에 없음, 5-3에서 직접 만듦
├─ .env.example         ← 접속 정보 양식 (비밀번호 없이)
├─ sql/                 ← 미션별 SQL 파일 저장할 곳
├─ notebooks/           ← 시작 노트북 트랙_분석.ipynb (수행한 트랙 이름으로 바꿔 쓰기, 예: 하트랙_분석.ipynb)
└─ images/              ← 미션별 차트 png 저장할 곳
```

`.env`만 직접 만들고(5-3), 나머지는 양식에 들어 있습니다. `sql/`과 `images/` 안의 `_안내.txt`는 파일 이름 규칙을 적어 둔 것으로, 지워도 됩니다.

### 5-2. 패키지 설치 {keep}

양식의 `requirements.txt`에는 아래 여섯 줄이 적혀 있습니다. 프로젝트 폴더에서 한 번에 설치합니다.

```text requirements.txt
pandas
sqlalchemy
psycopg2-binary
matplotlib
python-dotenv
jupyter
```

```bash 프로젝트 폴더에서 실행
pip install -r requirements.txt
```

### 5-3. 접속 정보는 .env에 {keep}

비밀번호를 노트북에 직접 쓰면 노트북을 제출하거나 공유할 때 비밀번호도 함께 나갑니다. 그래서 접속 정보는 `.env` 파일에 따로 두고, ==이 파일은 제출·공유하지 않습니다.==

:::cols
```text .env (내 PC에만)
PG_USER=postgres
PG_PASSWORD=설치할 때 정한 비밀번호
PG_HOST=localhost
PG_PORT=5432
PG_DB=postgres
```

```text .env.example (제출·공유용)
PG_USER=postgres
PG_PASSWORD=
PG_HOST=localhost
PG_PORT=5432
PG_DB=postgres
```
:::

양식의 `.env.example`을 **복사해 이름을 `.env`로 바꾸고**, `PG_PASSWORD`에 비밀번호를 적습니다. `.env.example`은 비밀번호 없이 그대로 남겨 둡니다. 다른 사람이 폴더를 받아 실행할 때 무엇을 채워야 하는지 알려 주는 파일입니다.

### 5-4. 연결 셀 — 강사 제공 코드 {keep}

`notebooks/트랙_분석.ipynb`의 이름을 수행할 트랙에 맞게 바꾸고(`하트랙_분석.ipynb` 등) 엽니다. 첫 셀에 아래 코드가 **이미 들어 있으니 그대로 실행**합니다.

```python 노트북 첫 셀 (강사 제공 코드)
# ===== 강사 제공 코드: 그대로 복사해서 사용합니다 =====
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()
engine = create_engine(URL.create(
    "postgresql+psycopg2",
    username=os.getenv("PG_USER", "postgres"), password=os.getenv("PG_PASSWORD") or None,
    host=os.getenv("PG_HOST", "localhost"), port=int(os.getenv("PG_PORT", "5432")),
    database=os.getenv("PG_DB", "postgres"),
))

def q(sql, **params):        # SELECT 문을 실행하고 결과를 DataFrame으로 돌려줍니다
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)

def q_file(name):            # ../sql 폴더의 SQL 파일을 읽어 실행합니다
    return q(Path("../sql", name).read_text(encoding="utf-8"))
# ===== 강사 제공 코드 끝 =====
```

### 5-5. 두 함수만 기억하면 됩니다 {keep}

| 함수 | 하는 일 | 쓰는 모양 |
| --- | --- | --- |
| `q("SELECT …")` | SQL 문장을 실행해 결과를 DataFrame으로 받음 | 짧은 확인용 쿼리 |
| `q_file("파일이름.sql")` | `sql/` 폴더의 파일을 읽어 실행해 DataFrame으로 받음 | 미션 쿼리 |

==DataFrame으로 받은 뒤부터는 Python 수업에서 배운 pandas 그대로입니다.==

### 5-6. 연결 확인 {keep}

둘째 셀도 양식에 들어 있습니다. 한글 글꼴을 정하고 기준정보 테이블을 조회합니다.

```python 둘째 셀
# 한글 글꼴 (Windows: Malgun Gothic / macOS: AppleGothic)
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

q("SELECT line_code, line_name, plan_per_shift FROM line_master")
```

```result
| | line_code | line_name | plan_per_shift |
| --- | --- | --- | --- |
| 0 | L1 | 냉장고 조립라인 | 400 |
| 1 | L2 | 세탁기 조립라인 | 450 |
| 2 | L3 | 에어컨 조립라인 | 350 |
```

이 표가 나오면 준비가 끝났습니다. **이 셀의 실행 결과가 브리핑 시간의 산출물**입니다.

### 5-7. 연결이 안 될 때 {keep}

| 오류 메시지에 보이는 말 | 원인 | 확인할 것 |
| --- | --- | --- |
| `password authentication failed` | 비밀번호가 다름 | `.env`의 `PG_PASSWORD`를 pgAdmin 접속 비밀번호와 비교 |
| `Connection refused` | 포트가 다르거나 서버가 꺼져 있음 | `.env`의 `PG_PORT`, pgAdmin 접속 여부 |
| `relation "line_master" does not exist` | 테이블이 없는 데이터베이스에 접속함 | 적재한 데이터베이스 이름과 `.env`의 `PG_DB` |
| `No module named …` | 패키지가 설치되지 않음 | 5-2의 설치 명령 |
| `.env`를 고쳤는데 그대로임 | 노트북이 예전 값을 기억함 | 커널을 다시 시작하고 첫 셀부터 실행 |

## 6. 미션 진행 방법

### 6-1. 트랙 고르기 {keep}

같은 데이터로 **하·중·상 3개 트랙**을 운영합니다. 본인 수준에 맞는 트랙 하나를 골라 미션 3개를 수행합니다. 트랙이 올라갈수록 필요한 기술이 넓어지고, 이 페이지가 주는 힌트는 줄어듭니다.

| 트랙 | 이런 분께 권합니다 | SQL 범위 | Python 범위 | 힌트 |
| --- | --- | --- | --- | --- |
| 하 | SELECT·GROUP BY가 아직 불안하다 | 단일 테이블, WHERE, GROUP BY, SUM·COUNT, ORDER BY | DataFrame 받기, 기본 막대·꺾은선 | 테이블·컬럼·함수 제시 |
| 중 | 기본 집계는 혼자 할 수 있다 | JOIN, 비율 계산(100.0 곱하기), WITH·서브쿼리, NULL 처리 | 피벗, 막대 + 누적 비율 표 | 테이블만 제시 |
| 상 | JOIN·서브쿼리까지 자신 있다 | WITH·서브쿼리, DELETE + INSERT를 한 트랜잭션으로 | 판정 로직, DB 기록, 위아래 여러 칸 그래프 | 지시문만 제시 |

### 6-2. 트랙 운영 규칙 {keep}

- 트랙은 시작 전에 **본인이 고릅니다.** 강사가 수업 중 관찰한 수준을 바탕으로 조정을 권할 수 있습니다.
- 트랙 미션 3개를 **1시간 안에** 끝내면 바로 위 트랙의 첫 미션에 도전할 수 있습니다.
- 시간이 모자라면 미션 2개를 끝낸 뒤 포트폴리오로 넘어갑니다. ==3개를 반쯤 한 것보다 2개를 끝까지 한 것==이 좋은 포트폴리오입니다.
- 포트폴리오에는 수행한 트랙을 적습니다.

### 6-3. 미션마다 반복하는 일곱 단계 {keep}

| 단계 | 하는 일 | 어디서 |
| --- | --- | --- |
| 1. 지시 해석 | 무엇을 보고해야 하는지 **한 줄로 다시 씁니다** | 노트북 마크다운 셀 |
| 2. 설계 | 필요한 테이블·컬럼·계산식을 적습니다 | 노트북 마크다운 셀 |
| 3. SQL 작성 | 먼저 실행해 결과를 눈으로 확인합니다 | pgAdmin |
| 4. Python 수신 | 쿼리를 `sql/` 파일로 저장하고 `q_file`로 받습니다 | 노트북 |
| 5. 검산 | 합계·건수를 **다른 방법으로 한 번 더** 확인합니다 | 노트북 |
| 6. 시각화 | 지시에 맞는 차트 1개를 만들어 `images/`에 저장합니다 | 노트북 |
| 7. 보고 문장 | 결론 1문장 + 근거 수치를 씁니다 | 노트북 마크다운 셀 |

> 양식 노트북에는 미션 3개의 틀(지시 해석 → 설계 → SQL → 검산 → 차트 → 보고)이 들어 있습니다. 위에서부터 빈칸을 채워 나가면 일곱 단계를 그대로 따르게 됩니다. 다 채운 모습이 궁금하면 실습 자료의 `예시.zip`을 열어 보세요(완성된 미션 3개 예시이며, 이번 미션과는 다른 지시문입니다).

### 6-4. 파일 이름 규칙 {keep}

파일 이름은 ==한글로, 이름만 봐도 무엇인지 알 수 있게== 짓습니다. **미션번호_내용** 순서로 쓰고, 띄어쓰기 대신 밑줄(`_`)을 씁니다.

| 미션 | SQL 파일 (`sql/` 폴더) | 차트 이미지 (`images/` 폴더) |
| --- | --- | --- |
| 하-1 | `하1_라인별_생산수량.sql` | `하1_라인별_생산수량.png` |
| 중-2 | `중2_불량유형_상위3개.sql` | `중2_불량유형_상위3개.png` |
| 상-3 | `상3_근무조별_결원.sql` | `상3_결원_작업자부족.png` |

- 노트북은 수행한 트랙 이름으로 저장합니다: `하트랙_분석.ipynb`, `중트랙_분석.ipynb`, `상트랙_분석.ipynb`
- SQL 파일과 그 결과로 그린 차트는 **같은 이름**을 씁니다. 짝을 찾기 쉽습니다.
- 한 미션에 쿼리가 여러 개면 `중1_교대별_불량률.sql`처럼 파일을 나눕니다. SQL 파일 첫 줄에는 주석으로 무엇을 구하는 쿼리인지 적습니다.
- `README.md`, `report.html`, `requirements.txt`, `.env`와 폴더 이름(`sql`, `notebooks`, `images`)은 바꾸지 않습니다. 코드가 이 이름으로 파일을 찾습니다.

### 6-5. 연습 — 일곱 단계를 한 번 따라 해 봅니다

미션이 아닌 쉬운 지시로 흐름을 먼저 익힙니다.

> "설비가 라인별로 몇 대씩 있는지 알려줘."

**1~2단계.** 보고할 것: 라인별 설비 수. 필요한 것: `equipment_master`의 `line_code`, `COUNT(*)`.

**3~4단계.** pgAdmin에서 실행해 본 쿼리를 파일로 저장하고 노트북에서 받습니다.

```sql sql/연습_라인별_설비수.sql
-- 연습. 라인별 설비 수
SELECT line_code,
       COUNT(*) AS equip_cnt
  FROM equipment_master
 GROUP BY line_code
 ORDER BY line_code;
```

```python 노트북
demo = q_file("연습_라인별_설비수.sql")
demo
```

```result
| | line_code | equip_cnt |
| --- | --- | --- |
| 0 | L1 | 3 |
| 1 | L2 | 3 |
| 2 | L3 | 3 |
```

### 6-6. 연습 — 검산·차트·보고 문장

**5단계 검산.** 라인별 설비 수를 모두 더하면 `equipment_master` 전체 행 수(9)와 같아야 합니다.

```python 검산
print("라인별 합계:", demo["equip_cnt"].sum())
print("전체 행 수:", q("SELECT COUNT(*) AS cnt FROM equipment_master")["cnt"][0])
```

```result
라인별 합계: 9
전체 행 수: 9
```

**6단계 시각화.** 제목에는 결론을, 축에는 이름과 단위를 씁니다.

```python 차트
fig, ax = plt.subplots(figsize=(5, 3))
ax.bar(demo["line_code"], demo["equip_cnt"], color="#c4c9d0")
ax.set_title("설비는 세 라인 모두 3대씩")
ax.set_xlabel("라인")
ax.set_ylabel("설비 수 (대)")
fig.savefig("../images/연습_라인별_설비수.png", dpi=150, bbox_inches="tight")
plt.show()
```

**7단계 보고 문장.**

> **[결론]** 설비는 세 라인 모두 3대씩입니다. **[근거]** 설비 기준정보 9대 = L1 3대 + L2 3대 + L3 3대.

## 7. 하 트랙 — 단일 테이블 집계

### 7-1. 하-1. 라인별 생산 수량 {keep}

> "10월에 라인별로 몇 대 만들었는지, 그중 양품이랑 불량이 각각 몇 개인지 뽑아줘."

| 항목 | 힌트 |
| --- | --- |
| 사용 테이블·컬럼 | production_result / line_code, prod_qty, good_qty, defect_qty |
| 사용 함수 | SUM, GROUP BY, ORDER BY |
| 권장 차트 | 라인별 막대(양품·불량) |
| 체크포인트 | 결과에서 생산 = 양품 + 불량이 맞는지 직접 확인 |

### 7-2. 하-2. 교대조별·숙련등급별 인원 {keep}

> "우리 현장 인원이 교대조별로 몇 명인지, 숙련등급별로 나눠서 정리해줘."

| 항목 | 힌트 |
| --- | --- |
| 사용 테이블·컬럼 | employee_master / shift, skill_grade |
| 사용 함수 | COUNT(*), GROUP BY shift, skill_grade, ORDER BY |
| 권장 차트 | 주간·야간 두 칸 막대(등급별 인원) |
| 체크포인트 | 등급별 인원 합계가 employee_master 전체 행 수와 같은지 확인 / 수습(C등급)이 어느 교대조에 많은지 보고 문장에 포함 |

### 7-3. 하-3. L1 일별 생산 추이 {keep}

> "냉장고 라인(L1) 하루 생산량이 날마다 어땠는지 그래프로 보여줘."

| 항목 | 힌트 |
| --- | --- |
| 사용 테이블·컬럼 | production_result / work_date, line_code, prod_qty |
| 사용 함수 | WHERE line_code = 'L1', SUM, GROUP BY work_date (주간·야간 합산) |
| 권장 차트 | 꺾은선 + 일 계획 800대(교대당 400대 × 2) 기준선 |
| 체크포인트 | 일요일 휴무라 27일치가 나와야 함 / 가장 적게·많이 만든 날을 보고 문장에 포함 |

## 8. 중 트랙 — JOIN · 비율 · 서브쿼리

### 8-1. 중-1. 라인별 계획 달성률·불량률 {keep}

> "10월 라인별로 계획 대비 얼마나 만들었는지, 불량률은 몇 %인지 정리해서 줘. 주간·야간 차이도 있으면 같이."

| 항목 | 힌트 |
| --- | --- |
| 사용 테이블 | production_result, line_master |
| 추출 값 | 라인별 달성률(생산 ÷ 계획), 불량률(불량 ÷ 생산), 교대별 비교 |
| 권장 차트 | 라인별 달성률 막대 + 교대별 불량률 묶은 막대 |
| 체크포인트 | 정수끼리 나누면 소수점이 버려짐 → 100.0을 곱해 소수를 섞기(4단원 2-8) |

### 8-2. 중-2. 라인별 불량 유형 상위 3개 {keep}

> "불량이 제일 많이 나오는 유형이 뭐야? 라인별로 상위 3개만 뽑아줘."

| 항목 | 힌트 |
| --- | --- |
| 사용 테이블 | defect_log, production_result |
| 추출 값 | 라인별·유형별 불량 수량, 라인 안에서의 순위·비율 |
| 권장 차트 | 유형별 막대(많은 순) + 누적 비율 표 |
| 체크포인트 | defect_log에는 라인 정보가 없음 / 라인 안 비율은 라인 합계를 WITH로 따로 구해 JOIN / 상위 3개는 pandas nlargest로 처리 |

### 8-3. 중-3. 결근율과 안전교육 미이수자 {keep}

> "지난달 결근이 라인별로 얼마나 됐는지 비율로 보고, 안전교육 아직 안 받은 사람이 누군지 짚어줘."

| 항목 | 힌트 |
| --- | --- |
| 사용 테이블 | attendance_log, employee_master, training_log |
| 추출 값 | 라인·교대별 결근율(결근 건수 ÷ 근태 기록 수), 정기 안전교육 미이수자 명단, 라인·교대별 이수율 |
| 권장 차트 | 라인·교대별 결근율 묶은 막대 / 이수율 묶은 막대 |
| 체크포인트 | training_log에는 이수한 사람만 있음 → 어떤 JOIN을 쓰느냐에 따라 미이수자가 사라짐 / 교육 과목이 여러 개이므로 '정기 안전교육'만 추릴 것 |

## 9. 상 트랙 — 판정 · 기록 · 데이터 연결

### 9-1. 상 트랙은 설계부터 직접 합니다 {keep}

상 트랙은 **사용 테이블을 알려 주지 않습니다.** 지시문과 산출물 요건만 보고 어떤 테이블에서 무엇을 꺼낼지부터 정합니다.

```icons 상 트랙 미션 세 개
clipboard-check | 상-1 · 판정 후 기록 | 기준을 정해 판정하고 DB에 남기기 | rose
gauge | 상-2 · 고장 전 신호 | 고장 직전과 평상시의 센서값 비교 | plum
layers | 상-3 · 데이터 연결 | 근태와 비가동 데이터를 한 장으로 | lime
```

### 9-2. 상-1. 일별 품질 판정 후 DB 기록 {keep}

> "일별로 불량률 추이 보고, 기준 넘는 날은 '주의'나 '이상'으로 판정해서 시스템에 남겨둬."

| 항목 | 요건 |
| --- | --- |
| 산출물 | 판정 기준(근거 포함), quality_judgment 입력 결과, 라인별 일별 불량률 차트(기준선 표시) |
| 요건 | 노트북을 **다시 실행해도 오류 없이** 기록돼야 함 |
| 테이블 규칙 | `judgment`에는 '정상'·'주의'·'이상'만 들어가고, 같은 날짜·라인은 한 행만 들어감 |

판정 기준은 정답이 없습니다. ==왜 그 기준인지 숫자로 설명할 수 있으면== 됩니다.

### 9-3. 상-1. Python에서 한 행 넣기 — 강사 제공 코드 {keep}

Python에서 DB에 INSERT 하는 문법은 배우지 않았으므로 **한 행 넣는 예시**를 드립니다. 판정 로직과 여러 행을 넣는 반복, 재실행 대비는 직접 작성합니다.

```python 한 행 INSERT (강사 제공 코드)
insert_sql = text("""
INSERT INTO quality_judgment (work_date, line_code, defect_rate, judgment)
VALUES (:work_date, :line_code, :defect_rate, :judgment)
""")

with engine.begin() as conn:   # 블록이 끝나면 COMMIT, 중간에 오류가 나면 ROLLBACK
    conn.execute(insert_sql, {"work_date": "2026-10-01", "line_code": "L1",
                              "defect_rate": 1.53, "judgment": "정상"})

q("SELECT work_date, line_code, defect_rate, judgment FROM quality_judgment")
```

- `:work_date`처럼 콜론이 붙은 이름 자리에, 뒤의 딕셔너리 값이 들어갑니다.
- `with engine.begin()` 블록 하나가 **트랜잭션 하나**입니다(9단원). 블록 안에서 `conn.execute`를 여러 번 부르면 모두 한 묶음으로 확정되거나 취소됩니다.
- 이 셀을 한 번 더 실행하면 `UniqueViolation`(중복된 키) 오류가 납니다. 같은 날짜·라인은 한 행만 들어갈 수 있기 때문입니다. **다시 실행해도 오류가 나지 않게 하는 것이 미션의 요건**입니다(3-2 표 참고).

### 9-4. 상-2. 고장 전 센서 신호 확인 {keep}

> "설비고장 나기 전에 온도나 진동에 이상 신호가 있었는지 확인해봐."

| 항목 | 요건 |
| --- | --- |
| 산출물 | 설비별 「고장 직전 vs 평상시」 비교표, 대표 고장 1건의 시간축 차트(고장 시점 표시) |
| 요건 | 비교 구간 길이와 센서 누락값 처리 방식을 보고서에 명시 |

### 9-5. 상-3. 근태·비가동 데이터 연결 보고 {keep}

> "작업자부족으로 라인 멈춘 날이 꽤 있던데, 그날 실제로 사람이 비었던 건지 근태랑 비가동 데이터 엮어서 한 장으로 보고해."

| 항목 | 요건 |
| --- | --- |
| 산출물 | '작업자부족' 비가동이 기록된 근무조와 그렇지 않은 근무조의 결원 인원 비교표, 일별 결원 인원과 작업자부족 비가동 시간을 **날짜 축을 공유하는 위아래 그래프**(`subplots`, `sharex=True`)로 묶은 보고 |
| 요건 | 두 데이터를 무엇으로 연결했는지, 결원을 무엇으로 셌는지(결근만 / 휴가 포함) 적을 것 / 맞지 않는 경우도 함께 보고할 것 / 인과가 아닌 ==「같은 시기에 함께 나타남」==으로 표현할 것 |

## 10. 시각화·보고 가이드

### 10-1. 보고 목적에 맞는 차트 {keep}

| 보고 목적 | 권장 차트 | 피할 것 |
| --- | --- | --- |
| 항목 간 크기 비교(라인, 사유) | 막대 | 3D 막대 |
| 시간에 따른 변화(일별 불량률) | 꺾은선 | 막대 27개 나열 |
| 원인 우선순위(불량 유형) | 많은 순 막대 + 누적 비율 표 | 항목 많은 원그래프 |
| 두 그룹 비교(주간·야간) | 묶은 막대 | 누적 막대 |

### 10-2. 차트 필수 요소 {keep}

- **제목에 결론**을 씁니다. 「L1 일별 생산량」이 아니라 「L1은 27일 모두 계획 미달」처럼 씁니다. 단, ==수치로 확인한 것만== 단정형으로 씁니다.
- **축 이름과 단위**(%, 분, 개, 대)를 표시합니다.
- **강조할 항목 1개만** 색을 다르게, 나머지는 회색 계열로 둡니다.
- 아래 한 줄로 저장합니다.

```python 차트 저장
fig.savefig("../images/하1_라인별_생산수량.png", dpi=150, bbox_inches="tight")
```

### 10-3. 보고 문장 형식 {keep}

==결론 1문장 + 근거 수치 + (있다면) 제안==의 순서로 씁니다.

> **[결론]** ○○라인의 10월 달성률이 가장 낮습니다.
> **[근거]** 계획 ○○개 대비 ○○개 생산(○○%), 주요 원인은 ○○ 비가동 ○○분입니다.
> **[제안]** ○○ 점검을 우선 검토하겠습니다.

- 수치는 **노트북 출력값 그대로** 옮깁니다.
- 데이터로 확인하지 못한 원인은 추정으로 쓰지 말고 「**추가 확인 필요**」라고 적습니다.

### 10-4. 중간 보고 — 1분 {keep}

1:45에 미션 1개를 골라 **1분 동안 말로** 보고합니다. 순서는 결론 → 수치 → 차트입니다.

```flow 1분 보고 순서
target | 결론 | 한 문장 | hot
gauge | 수치 | 근거 두세 개
chart-column | 차트 | 화면에 띄워 가리키기
```

## 11. 포트폴리오 정리 (2시간)

### 11-1. 보고서 report.html {keep}

`report.html`이 **포트폴리오 본문**입니다. 양식 폴더에 들어 있는 이 파일을 메모장이나 VS Code로 열어 `[대괄호]` 자리를 본인 내용으로 바꿉니다. 브라우저로 열면 결과를 바로 볼 수 있습니다.

| 양식의 장 | 채울 내용 |
| --- | --- |
| 표지 | 작성자, 작성일, 수행 트랙, 저장소 주소(GitHub에 올렸을 때만) |
| 1. 핵심 요약 | 미션별 결론 1문장씩 |
| 2. 데이터 개요 | 테이블 요약표(채워져 있음) + 직접 검산한 데이터 규칙 |
| 3. 미션별 분석 | 지시문 → 지시 해석 → 접근 방법 → 핵심 SQL → 결과 표 → 차트 → 보고 |
| 4. 트러블슈팅 | 실제로 겪은 문제 · 원인 · 해결 |
| 5. AI 활용 내역 | 질문 요지 · 알게 된 것 · 내 코드에 적용한 방법 (2~3건) |
| 6. 회고 및 확장 방향 | 배운 점 · 아쉬운 점 · 다음에 공부해서 적용할 것 |

차트는 양식의 `images/mission_1.png` 자리를 본인 파일 이름(예: `images/하1_라인별_생산수량.png`)으로 바꾸면 들어갑니다.

### 11-2. README.md {keep}

`README.md`는 프로젝트 폴더를 받은 사람이 **가장 먼저 읽는 요약**입니다. 30초 안에 무슨 프로젝트인지 알 수 있게 짧게 씁니다. 양식 폴더의 `README.md`를 메모장이나 VS Code로 열어 고칩니다.

```text README.md 양식
# 가전 조립공장 생산 데이터 분석 — 업무 지시 기반 SQL × Python 보고

> 가상의 가전 조립공장(냉장고·세탁기·에어컨 3개 라인) 2026년 10월 합성 데이터를 사용했습니다.

## 프로젝트 개요
- 기간 / 인원 / 역할 / 수행 트랙
- 목적: 현업 지시를 SQL 추출 → Python 시각화 → 보고까지 수행
- 기술: PostgreSQL, Python(pandas, SQLAlchemy, matplotlib), Jupyter

## 핵심 결과
- (미션 1 결론 1문장)
- (미션 2 결론 1문장)
- (미션 3 결론 1문장)
![대표 차트](images/하1_라인별_생산수량.png)

## 보고서
- 전체 보고서: report.html (브라우저로 열기) · SQL: sql/ 폴더 · 노트북: notebooks/ 폴더

## AI 활용 내역
코드는 직접 작성했으며, AI는 채팅으로 개념·문법 질문에만 활용했습니다. (대표 질문은 보고서 5장)
```

### 11-3. 작성 원칙 {keep}

- **지시 → 접근 → 결과** 순서로 씁니다. 채용 담당자는 「무엇을 요청받아 어떻게 풀었는지」를 봅니다.
- 수치는 노트북 출력값 그대로 옮깁니다. 확인하지 않은 원인 추정은 「**추가 확인 필요**」로 표시합니다.
- 핵심 SQL은 미션마다 1~2개만 발췌하고, 전체는 `sql/` 폴더로 연결합니다.
- 트러블슈팅에는 **실제로 겪은 문제**를 씁니다. 예: 정수 나눗셈으로 불량률이 0으로 나옴, NULL인 equip_code가 JOIN에서 빠짐, 한글 글꼴이 깨짐.
- 합성 데이터임을 맨 위에 밝힙니다.
- ==`.env`(DB 비밀번호)는 제출·공유하는 폴더에 넣지 않습니다.==

### 11-4. 마무리 점검 {keep}

내 PC의 프로젝트 폴더가 그대로 결과물입니다. 아래 네 가지를 확인하면 끝입니다.

1. 노트북을 **커널 다시 시작 후 처음부터 끝까지** 실행해 오류가 없는지 확인하고 저장합니다.
2. `report.html`을 **브라우저로 열어** 차트 이미지와 표가 모두 보이는지 확인합니다. 이미지가 안 보이면 파일 이름과 `images/` 경로를 봅니다.
3. 폴더 구조가 5-1과 같은지, `sql/`·`images/`의 파일 이름이 6-4의 규칙을 따르는지 봅니다.
4. 폴더를 다른 사람에게 넘길 때(제출·공유)는 **`.env`를 빼고** 넘깁니다. `.env.example`은 남겨 둡니다.

### 11-5. (선택) GitHub에 올리기 {keep}

==하지 않아도 됩니다.== 포트폴리오를 온라인 주소로 보여 주고 싶은 분만, 11-4까지 끝낸 뒤에 진행합니다.

1. 프로젝트 폴더에 `.gitignore` 파일을 만들고 아래 세 줄을 적습니다. `.env`가 올라가지 않게 막는 파일입니다.
2. GitHub에서 `production-db-analysis` 저장소를 만들고 프로젝트 폴더를 올립니다. 올리기 전에 `git status`에 `.env`가 **보이지 않는지** 확인합니다.
3. GitHub는 HTML 파일을 화면이 아니라 코드로 보여 줍니다. 보고서를 화면으로 보여 주려면 저장소의 **Settings → Pages**에서 `main` 브랜치를 선택해 저장합니다. 1~2분 뒤 `https://내아이디.github.io/production-db-analysis/report.html`로 보고서가 열립니다.
4. 이 주소를 `README.md`와 보고서 표지에 적습니다.

```text .gitignore
.env
__pycache__/
.ipynb_checkpoints/
```

## 12. 평가와 상호 리뷰

### 12-1. 평가 체크리스트 {keep}

| 영역 | 기준 | 배점 |
| --- | --- | --- |
| 추출 정확성 | 선택한 트랙 미션 결과가 검산값과 일치 | 30 |
| SQL 품질 | JOIN·집계·소수 계산(100.0)·NULL 처리가 적절하고 파일로 관리됨 | 20 |
| 시각화 | 지시에 맞는 차트 유형, 제목·축·단위 표기 | 20 |
| 보고 | 결론 1문장 + 근거 수치 형식 준수 | 10 |
| 포트폴리오 | 보고서·README 구조, 차트 캡션, 폴더 정리, 비밀번호 미노출 | 20 |

### 12-2. 상호 리뷰 — 2인 1조 {keep}

3:40부터 짝의 프로젝트 폴더를 함께 열어 아래를 점검하고, 지적받은 것을 고칩니다.

- README만 읽고 프로젝트 목적을 **30초 안에** 이해할 수 있다.
- 미션마다 지시·접근·결과가 모두 있다.
- 모든 차트에 제목·축 단위·캡션이 있다.
- 노트북을 처음부터 다시 실행해도 오류가 없다.
- 넘겨줄 폴더(제출·공유용)에 `.env`가 들어 있지 않다.
- 짝이 미션 1개의 쿼리를 **본인 말로** 설명할 수 있다.

## 13. 심화 학습 가이드 (선택)

### 13-1. 언제 쓰나요 {keep}

배운 범위만으로 모든 미션을 풀 수 있습니다. 아래는 결과물을 한 단계 올리고 싶을 때 **스스로 공부해** 적용하는 목록입니다.

- ==트랙 미션을 모두 끝낸 뒤에만== 적용합니다. 쓰지 않아도 감점은 없습니다.
- AI에게는 **개념과 일반 예시만** 묻고, 내 데이터에 맞는 코드는 직접 씁니다(2장).
- 적용했다면 보고서의 「AI 활용 내역」과 「다음에 공부해서 적용할 것」에 적습니다.

### 13-2. Python 심화 {keep}

| 기능 | 쓰면 좋아지는 점 | 적용 미션 | AI에게 할 질문 예시 |
| --- | --- | --- | --- |
| `ax.twinx()` 보조 y축 | 단위가 다른 두 값을 한 그래프에. 파레토 차트의 핵심 | 중-2, 상-3 | "matplotlib에서 왼쪽·오른쪽 y축을 따로 쓰는 원리를 알려줘" |
| `ax.barh()` 가로 막대 | 설비명처럼 긴 이름을 돌리지 않고 표시 | 하-2, 중-3 | "bar와 barh는 어떤 경우에 구분해서 쓰는 게 좋아?" |
| `DateFormatter` | 날짜 축 간격·모양(예: 10/14)을 직접 지정 | 하-3, 상-2 | "matplotlib 날짜 축 서식을 바꾸는 방법의 개념을 알려줘" |
| `ax.text()`, `ax.annotate()` | 「고장」「최저」 같은 설명을 그래프 위에 직접 표시 | 하-3, 상-2, 상-3 | "annotate와 text의 차이는 뭐야?" |
| pandas `cumsum()` | 누적 합·누적 비율을 함수 하나로 계산 | 중-2 | "누적 합계를 구하는 pandas 함수는 뭐야?" |
| pandas `rank()` | 그룹 안 순위를 pandas에서 계산 | 중-2 | "pandas rank의 method 옵션 차이를 알려줘" |
| `merge_asof` 복습(ch15) | 고장 시각마다 직전 센서값 붙이기 | 상-2 | "merge_asof의 direction 옵션은 각각 어떻게 동작해?" |

### 13-3. SQL 심화 {keep}

| 기능 | 쓰면 좋아지는 점 | 적용 미션 | AI에게 할 질문 예시 |
| --- | --- | --- | --- |
| 윈도우 함수 `RANK() OVER (PARTITION BY …)`, `SUM() OVER (ORDER BY …)` | 그룹 안 순위·누적 합을 SQL 한 번으로 계산 | 중-2, 중-3 | "GROUP BY와 윈도우 함수의 차이가 뭐야?" |
| `COALESCE` | NULL을 0 같은 값으로 SQL에서 바로 바꿈 | 상-3 | "COALESCE는 어떤 상황에서 쓰는 함수야?" |
| `INTERVAL` | 「6시간 전」 같은 시간 구간을 SQL에서 바로 계산 | 상-2 | "PostgreSQL에서 날짜·시각에 시간을 더하고 빼는 방법의 개념을 알려줘" |
| `INSERT … ON CONFLICT … DO UPDATE` | 「있으면 고치고 없으면 넣기」를 한 문장으로 | 상-1 | "UPSERT가 무엇이고 DELETE 후 INSERT와 뭐가 다르지?" |

> 공식 문서에서 찾아볼 말 — PostgreSQL: Window Functions, COALESCE, Date/Time Functions and Operators, INSERT ON CONFLICT / matplotlib: Axes.twinx, Axes.barh, Axes.annotate, matplotlib.dates / pandas: Series.cumsum, Series.rank, merge_asof

## 14. 막혔을 때

### 14-1. 자주 막히는 지점 {keep}

| 증상 | 원인 | 확인할 것 |
| --- | --- | --- |
| 불량률·달성률이 0으로 나옴 | 정수끼리 나눠 소수점이 버려짐 | 4단원 2-8 — 나누기 전에 `100.0`을 곱했는지 |
| 안전교육 미이수자가 한 명도 안 나옴 | training_log에는 이수자만 있어 JOIN에서 미이수자가 빠짐 | JOIN 종류(5단원) — 짝이 없는 행을 남기는 JOIN인지 |
| 이수 인원이 직원 수보다 많게 나옴 | 교육 과목이 여러 개라 한 사람이 여러 행 | 과목 조건을 어디에 썼는지 |
| 근무조별 결과가 162행이 아님 | 결원·비가동이 없는 근무조는 집계 결과에 행이 없음 | 기준이 되는 표에 붙였는지(merge의 how), 빈칸 처리 |
| 차트 한글이 □로 보임 | 글꼴을 정하지 않음 | 5-6의 `rcParams` 두 줄 |
| 다시 실행하면 `UniqueViolation`(중복된 키) 오류 | 같은 날짜·라인을 또 INSERT | 3-2 표 — 한 트랜잭션에서 지우고 다시 넣기 |
| INSERT에서 `CheckViolation` 오류 | `judgment`에 정상·주의·이상이 아닌 값이 들어감 | 판정 함수가 돌려주는 글자 |
| `q_file`이 파일을 못 찾음 | 노트북이 `notebooks/` 폴더 밖에 있음 | 노트북 위치, `sql/` 폴더의 파일 이름 |
| 일별 결과가 27행이 아님 | 교대별로 나뉘었거나 조건이 빠짐 | GROUP BY 기준 컬럼, WHERE 조건 |

### 14-2. 그래도 안 풀리면 {keep}

1. 오류 메시지의 **마지막 줄**을 먼저 읽습니다. 대부분 원인이 거기에 있습니다.
2. 쿼리를 pgAdmin에서 **한 부분씩** 실행해 어디서부터 결과가 달라지는지 봅니다.
3. 4-5의 **데이터 규칙**으로 검산합니다. 규칙과 다르면 쿼리 문제입니다.
4. AI에게는 **오류 메시지 문구만** 붙여 넣고 뜻을 묻습니다(2장). 코드 전체를 붙여 넣지 않습니다.
5. 10분 넘게 같은 자리라면 강사에게 손을 듭니다. 막힌 과정을 적어 두면 **트러블슈팅** 항목이 됩니다.

:::summary
- **목표**: 말로 받은 지시 → 테이블·컬럼·계산식 → SQL 추출 → Python 검산·시각화 → 「결론 1문장 + 근거 수치 + 차트 1개」 보고.
- **AI 규칙**: 코드는 직접 작성. AI는 브라우저 채팅에서 개념·문법·오류 뜻만 묻고, 질문은 노트북 마지막 `AI 질문 로그`에 기록. 복사해도 되는 것은 연결 셀과 한 행 INSERT 예시뿐.
- **트랙**: 하(단일 테이블 집계) · 중(JOIN·비율·서브쿼리) · 상(판정·기록·데이터 연결) 중 하나를 골라 미션 3개.
- **일곱 단계**: 지시 해석 → 설계 → SQL 작성 → Python 수신 → 검산 → 시각화 → 보고 문장.
- **데이터**: 같은 공장의 생산 테이블 8개 + 인사·근태 테이블 3개. 날짜·교대·라인으로 이어 볼 수 있음.
- **검산**: 생산 = 양품 + 불량, 가동 + 비가동 = 720분, 유형별 불량 합계 = 실적 불량 수량, 근태 기록 = 직원 70명 × 27일. 결과가 규칙과 다르면 쿼리를 먼저 의심.
- **차트**: 제목에 결론, 축에 이름과 단위, 강조는 1개만.
- **포트폴리오**: 내 PC의 프로젝트 폴더에 `report.html`(본문) + `README.md`(요약) + `sql/` + `notebooks/` + `images/`. 합성 데이터임을 밝히고, `.env`는 제출·공유하지 않음. GitHub 업로드는 선택.
:::
