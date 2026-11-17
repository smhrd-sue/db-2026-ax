---
label: 9. TCL
title: 데이터 확정·복원
---

# 트랜잭션 · BEGIN · COMMIT · ROLLBACK · LOCK

:::goal
- 트랜잭션이 무엇인지, ACID(원자성·일관성·고립성·지속성)가 무엇을 지켜 주는지 부서장 발령 업무로 설명할 수 있습니다.
- PostgreSQL이 기본으로 자동 커밋한다는 것을 알고, `BEGIN` · `COMMIT` · `ROLLBACK`으로 여러 문장을 한 묶음으로 확정·취소할 수 있습니다.
- 직원 정보 변경과 이력 INSERT를 한 트랜잭션으로 묶고, 오류로 중단된 트랜잭션과 `SAVEPOINT`의 동작을 설명할 수 있습니다. (생산 데이터의 UIT 정정 Q13은 복습 문제에서 풉니다.)
- 두 세션으로 읽기 일관성과 행 잠금(LOCK)을 확인하고, 누가 누구를 기다리는지 찾을 수 있습니다.
:::

:::teacher 단원 구성 (60분)
- 운영안 Day 4 **2H(2교시 — 트랜잭션: BEGIN/COMMIT/ROLLBACK, PostgreSQL 클라이언트는 기본 자동 커밋이라 BEGIN 필수, 마스터 변경 + 이력 INSERT를 한 묶음으로 / Q13 UIT 정정 + uit_change_history INSERT, 일부러 실패시켜 ROLLBACK 확인)** 에 해당합니다. 1교시(DML 기초)에서 INSERT·UPDATE·DELETE를 배운 뒤라는 전제입니다.
- 기존 교안 `11. TCL.pptx` · `11. TCL.txt`의 **순서(SQL 분류 → 트랜잭션 → ACID → COMMIT/ROLLBACK → 세션·읽기 일관성 → LOCK)** 를 따르되, 송금 예제는 HR 데이터의 **부서장 발령(직원 변경 + `job_history` INSERT)** 으로 바꿨습니다. 운영안의 **Q13(UIT 정정 + 이력)** 은 같은 구조의 생산 데이터 문제로 **복습 문제 1·2**에 있습니다. 기존 `.txt`의 「DROP·TRUNCATE는 ROLLBACK 불가」는 PostgreSQL에서는 성립하지 않으므로 4장에서 실제 동작으로 다시 다룹니다.
- 교안의 모든 SQL과 실행 결과는 실습 DB에서 **직접 실행한 결과**입니다. 오류·경고 메시지도 실제 출력입니다. 두 세션 실험(5장)은 psql 2~3개를 동시에 띄워 실행했습니다. (검증 환경: PostgreSQL 18.7, psql)
- HR 본문의 이력은 발령일을 **2026-12-01**로 정하고 날짜를 직접 씁니다. 생산 데이터 문제의 이력 INSERT는 `CURRENT_DATE`를 쓰므로 **실행한 날짜**가 들어갑니다(결과표에는 날짜 컬럼을 넣지 않았습니다).
- 원본 테이블을 지키기 위해 본문은 **HR 사본 3개**(`t_emp`, `t_dept`, `t_job_history`), 확인 문제·복습 문제는 **생산 데이터 사본 3개**(`t_part_master`, `t_part_sourcing`, `t_uit_history`)에서 실습합니다(0장). 사본은 `LIKE … INCLUDING ALL`로 만들어 **PK·CHECK가 그대로 복사**되므로, 3장의 「일부러 실패」(CHECK 위반, PK 중복)가 사본에서도 재현됩니다.
- 원본 `employees`에는 트리거가 2개 있습니다. `update_job_history`(직무·부서를 바꾸면 이전 이력을 `job_history`에 자동 INSERT)와 `secure_employees`(평일 08:00~18:00 밖의 변경을 오류로 거부)입니다. 사본에는 트리거가 복사되지 않으므로 이력은 직접 넣고, 수업 시간대와 상관없이 실습할 수 있습니다.
- 2~5장 끝 「확인 문제」(복습 1 + 응용 1)는 생산 데이터(`bom` 스키마의 사본)로 만들었고, 답안 결과도 직접 실행한 값입니다. 데이터를 바꾸는 문제는 ==모두 ROLLBACK으로 끝나거나 원래 값으로 되돌리는 문장==을 포함했습니다.

| 교시 | 시간 | 내용 | 해당 장 | 기존 교안 대응 |
| --- | --- | --- | --- | --- |
| **Day 4 2교시** | 0~5분 | 연습용 사본 만들기 | 0 | — |
| | 5~12분 | TCL · 트랜잭션 · ACID | 1 | `11. TCL.pptx` 3~9 |
| | 12~22분 | 자동 커밋 · BEGIN / COMMIT / ROLLBACK | 2 | `11. TCL.pptx` 10, `11. TCL.txt` 1~2단 |
| | 22~37분 | 직원 변경 + 이력 INSERT를 한 묶음으로 · 일부러 실패 · SAVEPOINT | 3 | `11. TCL.pptx` 7~8 (송금 → 부서장 발령) |
| | 37~42분 | TRUNCATE · DROP도 트랜잭션 안에서 | 4 | `11. TCL.txt` 「DROP·TRUNCATE」 줄 |
| | 42~55분 | 세션 2개: 읽기 일관성 · LOCK · 대기 확인 | 5 | `11. TCL.pptx` 11~12, `11. TCL.txt` 마지막 단 |
| | 55~60분 | 정리 · 복습 문제 안내 (Q13 UIT 정정 포함) | 6~7 | — |
:::

## 0. 실습 준비 — 연습용 사본 만들기

### 0-1. 본문용 HR 사본 3개 만들기 {keep}

이번 시간에는 데이터를 **바꾸고, 되돌리고, 확정**합니다. 원본(`employees` 등)은 다음 교시에도 쓰므로, 똑같은 구조의 사본을 만들어 연습합니다. 아래 스크립트는 **그대로 실행**만 하면 됩니다.

```sql HR 사본 만들기 (본문 초기화 스크립트)
SET search_path TO hr;

DROP TABLE IF EXISTS t_job_history, t_emp, t_dept;
CREATE TABLE t_emp         (LIKE employees   INCLUDING ALL);
CREATE TABLE t_dept        (LIKE departments INCLUDING ALL);
CREATE TABLE t_job_history (LIKE job_history INCLUDING ALL);
INSERT INTO t_emp         SELECT * FROM employees;
INSERT INTO t_dept        SELECT * FROM departments;
INSERT INTO t_job_history SELECT * FROM job_history;
```

> 이 단원의 실습은 **SQL Shell (psql)** 기준입니다. psql은 `WARNING`, `ROLLBACK` 같은 결과 메시지를 그대로 보여 주고, 창을 2개 띄우면 **세션 2개**가 되어 5장 실습을 바로 할 수 있습니다.

### 0-2. 문제용 생산 데이터 사본 3개 만들기 {keep}

확인 문제와 복습 문제는 생산 데이터로 풉니다. 생산 데이터도 사본 3개를 만들어 둡니다.

```sql 생산 데이터 사본 만들기 (문제 초기화 스크립트)
SET search_path TO bom;

DROP TABLE IF EXISTS t_part_master, t_part_sourcing, t_uit_history;
CREATE TABLE t_part_master   (LIKE part_master        INCLUDING ALL);
CREATE TABLE t_part_sourcing (LIKE part_sourcing      INCLUDING ALL);
CREATE TABLE t_uit_history   (LIKE uit_change_history INCLUDING ALL);
INSERT INTO t_part_master   SELECT * FROM part_master;
INSERT INTO t_part_sourcing SELECT * FROM part_sourcing;
INSERT INTO t_uit_history   SELECT * FROM uit_change_history;
```

### 0-3. 사본 확인 {keep}

> 실행 전: `SET search_path TO hr;` — 1~5장 본문 예제는 HR 사본으로 실행합니다. (0-2 스크립트가 `bom`으로 바꿔 두었으므로 다시 `hr`로 돌아옵니다.)

```sql
SELECT 'hr.t_emp' AS tbl, COUNT(*) FROM hr.t_emp
UNION ALL SELECT 'hr.t_dept',          COUNT(*) FROM hr.t_dept
UNION ALL SELECT 'hr.t_job_history',   COUNT(*) FROM hr.t_job_history
UNION ALL SELECT 'bom.t_part_master',   COUNT(*) FROM bom.t_part_master
UNION ALL SELECT 'bom.t_part_sourcing', COUNT(*) FROM bom.t_part_sourcing
UNION ALL SELECT 'bom.t_uit_history',   COUNT(*) FROM bom.t_uit_history;
```

```result
| tbl | count |
| --- | --- |
| hr.t_emp | 107 |
| hr.t_dept | 27 |
| hr.t_job_history | 10 |
| bom.t_part_master | 68 |
| bom.t_part_sourcing | 52 |
| bom.t_uit_history | 5 |
```

- `LIKE 원본 INCLUDING ALL`은 원본의 **컬럼·NOT NULL·PK·CHECK**까지 복사한 빈 테이블을 만듭니다. `CREATE TABLE … AS SELECT`로 만든 사본에는 PK가 없으므로, 오늘은 제약조건 오류를 일부러 내 보기 위해 이 방법을 씁니다. (FK와 트리거는 복사되지 않습니다.)
- 실습 중 데이터가 꼬이면 ==0-1(HR) 또는 0-2(생산) 스크립트를 다시 실행==하면 사본이 처음 상태로 돌아갑니다.

## 1. TCL과 트랜잭션

### 1-1. SQL 문장의 종류 {keep}

| 분류 | 이름 | 하는 일 | 대표 명령 | 배우는 때 |
| --- | --- | --- | --- | --- |
| QUERY | 질의어 | 데이터 조회 | `SELECT` | Day 1~3 |
| DML | 데이터 조작어 | 행을 넣고 바꾸고 지움 | `INSERT`, `UPDATE`, `DELETE` | Day 4 1교시 |
| **TCL** | **트랜잭션 제어어** | **DML 결과를 확정하거나 취소** | **`BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`** | **이번 시간** |
| DDL | 데이터 정의어 | 테이블 구조를 만들고 바꿈 | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` | Day 4 3교시 |

### 1-2. 트랜잭션 — 「한 번에 다 되거나, 하나도 안 되거나」 {keep}

**트랜잭션(transaction)** 은 데이터베이스 상태를 바꾸는 **최소 작업 단위**입니다. 여러 SQL 문장을 하나로 묶어, ==전부 반영되거나 전부 취소되게== 합니다.

인사 업무의 예로 보겠습니다. 5단원 3-3에서 찾은 직원 없는 부서 16개 중 하나가 **Treasury(120)** 입니다. 재무부(Finance, 100)의 회계 담당 **109번 Daniel Faviet**을 12월 1일자로 Treasury 부서장(직무 `FI_MGR`)으로 발령한다면, DB에서는 **두 가지 일**이 일어나야 합니다.

```text 부서장 발령 업무 (하나의 트랜잭션)
① employees   에서 직무·부서를 FI_MGR·120 으로 바꾼다    UPDATE
② job_history 에 이전 직무(기간·직무·부서)를 남긴다      INSERT
③ 확정한다                                               COMMIT
```

### 1-2. 반쪽만 반영되면 {keep}

①만 되고 ②가 실패하면 어떻게 될까요?

| 상황 | 결과 |
| --- | --- |
| ①만 반영, ② 실패 | 직무·부서는 바뀌었는데 **그전에 어디서 무슨 일을 했는지 기록이 없음** |
| ②만 반영, ① 실패 | 이력에는 「옮겼다」고 남았는데 **실제 직무·부서는 그대로** |
| ①② 모두 반영 | 정상 |
| ①② 모두 취소 | 정상 (아무 일도 없었던 것과 같음) |

반쪽만 반영된 두 경우가 모두 **데이터 불일치**입니다. 그래서 ①과 ②를 한 트랜잭션으로 묶어 「둘 다 되거나, 둘 다 안 되게」 만듭니다. 이번 시간의 목표가 바로 이것입니다. (생산 데이터의 같은 업무 — UIT 정정 + 이력, Q13 — 는 복습 문제에서 풉니다.)

### 1-3. 트랜잭션의 4가지 특성 (ACID) {keep}

| 특성 | 뜻 | 부서장 발령 예에서 |
| --- | --- | --- |
| 원자성 (Atomicity) | 전부 실행되거나 전혀 실행되지 않음 | 직무·부서 UPDATE와 이력 INSERT가 함께 반영되거나 함께 취소 |
| 일관성 (Consistency) | 언제나 규칙(제약조건)에 맞는 상태 유지 | 이력 기간이 거꾸로(종료일 < 시작일)이면 CHECK 제약 위반으로 트랜잭션 전체가 반영되지 않음 |
| 고립성 (Isolation) | 실행 중인 트랜잭션은 다른 트랜잭션의 영향을 받지 않음 | 확정 전의 변경은 다른 사람(세션)에게 보이지 않음 (5장) |
| 지속성 (Durability) | 성공적으로 확정된 결과는 영구히 남음 | `COMMIT` 후에는 `ROLLBACK`으로 되돌릴 수 없음 (2장) |

## 2. 자동 커밋과 BEGIN · COMMIT · ROLLBACK

### 2-1. PostgreSQL은 기본이 「자동 커밋」 {keep}

PostgreSQL은 **모든 SQL 문장을 트랜잭션 안에서** 실행합니다. `BEGIN`을 쓰지 않으면 문장 하나하나를 각각의 트랜잭션으로 보고, 성공하면 **그 자리에서 자동으로 COMMIT**합니다. 이것을 **자동 커밋(auto commit)** 이라고 합니다.

psql에서 지금 설정을 확인합니다.

```sql psql 전용 명령
\echo :AUTOCOMMIT
```

```result
on
```

### 2-1. BEGIN으로 묶기 {keep}

| 쓰는 법 | 트랜잭션 범위 | 확정 시점 |
| --- | --- | --- |
| `BEGIN` 없이 DML 실행 | 문장 1개 | 문장이 성공하는 즉시 (자동) |
| `BEGIN; … COMMIT;` | `BEGIN`부터 `COMMIT`까지 전부 | `COMMIT`을 실행할 때 |

==여러 문장을 한 묶음으로 만들려면 반드시 `BEGIN`으로 시작해야 합니다.== `BEGIN` 없이 실행한 UPDATE는 이미 확정되어 `ROLLBACK`으로 되돌릴 수 없습니다(2-3).

| 명령 | 뜻 |
| --- | --- |
| `BEGIN;` | 트랜잭션 시작 (여기서부터 묶음) |
| `COMMIT;` | 묶음 안의 변경을 **영구 반영(확정)** |
| `ROLLBACK;` | 묶음 안의 변경을 **모두 취소**하고 `BEGIN` 이전 상태로 |

### 2-2. BEGIN 후 UPDATE {keep}

:::cols
```sql ① 109번 직원의 현재 직무
SELECT employee_id, first_name, last_name, job_id
  FROM t_emp
 WHERE employee_id = 109;
```

```result
| employee_id | first_name | last_name | job_id |
| --- | --- | --- | --- |
| 109 | Daniel | Faviet | FI_ACCOUNT |
```
:::

:::cols
```sql ② 트랜잭션을 시작하고 직무를 바꿉니다
BEGIN;

UPDATE t_emp
   SET job_id = 'FI_MGR'
 WHERE employee_id = 109;
```

```result
BEGIN
UPDATE 1
```
:::

### 2-2. 같은 창에서는 바뀐 값이 보입니다 {keep}

```sql
SELECT employee_id, first_name, last_name, job_id
  FROM t_emp
 WHERE employee_id = 109;
```

```result
| employee_id | first_name | last_name | job_id |
| --- | --- | --- | --- |
| 109 | Daniel | Faviet | FI_MGR |
```

### 2-2. ROLLBACK — 바꾸기 전으로 되돌리기 {keep}

이제 취소합니다.

```sql
ROLLBACK;

SELECT employee_id, first_name, last_name, job_id
  FROM t_emp
 WHERE employee_id = 109;
```

```result
ROLLBACK
```

```result
| employee_id | first_name | last_name | job_id |
| --- | --- | --- | --- |
| 109 | Daniel | Faviet | FI_ACCOUNT |
```

- `ROLLBACK`으로 `BEGIN` 이전의 **FI_ACCOUNT**로 돌아왔습니다.
- `BEGIN` 이후의 변경은 **아직 확정되지 않은 상태**입니다. 내 창에서는 보이지만, 다른 사람에게는 보이지 않습니다(5장).

### 2-3. BEGIN 없이 ROLLBACK하면 ⭐ {keep}

:::error BEGIN을 빼먹으면 — 「진행 중인 트랜잭션이 없습니다」
`BEGIN` 없이 UPDATE를 실행하면 자동 커밋으로 **이미 확정**됩니다. 그 뒤의 `ROLLBACK`은 되돌릴 묶음이 없어 경고만 냅니다.

```sql
UPDATE t_emp
   SET job_id = 'FI_MGR'
 WHERE employee_id = 109;

ROLLBACK;
```

```error
UPDATE 1
WARNING:  there is no transaction in progress
ROLLBACK
```
:::

### 2-3. 「ROLLBACK」이라고 찍혔는데 그대로? {keep}

```sql
SELECT employee_id, first_name, last_name, job_id
  FROM t_emp
 WHERE employee_id = 109;
```

```result
| employee_id | first_name | last_name | job_id |
| --- | --- | --- | --- |
| 109 | Daniel | Faviet | FI_MGR |
```

화면에 `ROLLBACK`이라고 찍혔지만 **직무는 FI_MGR 그대로**입니다. ==WARNING 줄을 놓치지 마세요.== 「취소한 줄 알았는데 이미 반영된」 사고가 가장 흔한 실수입니다.

방금 바뀐 값을 원래대로 돌려 둡니다(이것도 자동 커밋으로 바로 확정됩니다).

```sql
UPDATE t_emp
   SET job_id = 'FI_ACCOUNT'
 WHERE employee_id = 109;
```

```result
UPDATE 1
```

### 2-4. COMMIT 후에는 ROLLBACK으로 되돌릴 수 없음 {keep}

```sql
BEGIN;

UPDATE t_emp
   SET salary = 9500
 WHERE employee_id = 109;

COMMIT;

ROLLBACK;
```

```result
BEGIN
UPDATE 1
COMMIT
WARNING:  there is no transaction in progress
ROLLBACK
```

### 2-4. 확정된 값은 남습니다 — 지속성 {keep}

```sql
SELECT employee_id, first_name, salary
  FROM t_emp
 WHERE employee_id = 109;
```

```result
| employee_id | first_name | salary |
| --- | --- | --- |
| 109 | Daniel | 9500.00 |
```

`COMMIT`에서 트랜잭션이 끝났으므로 뒤의 `ROLLBACK`은 2-3과 같은 경고만 냅니다. `ROLLBACK`은 ==지금 열려 있는 트랜잭션(`BEGIN` 이후)의 변경만== 되돌립니다. 이미 `COMMIT`된 것, `BEGIN` 없이 실행된 것은 되돌릴 수 없습니다(지속성).

> 원래 급여는 9000이었습니다. 0-1 스크립트를 다시 실행하면 HR 사본 전체가 처음 상태로 돌아갑니다.

### 2-4. BEGIN을 두 번 쓰면? {keep}

트랜잭션 안에서 `BEGIN`을 또 실행해도 새 묶음이 생기지 않고 경고만 나옵니다.

```sql
BEGIN;
BEGIN;
COMMIT;
```

```result
BEGIN
WARNING:  there is already a transaction in progress
BEGIN
COMMIT
```

:::teacher 강사 확인
- **pgAdmin 4 Query Tool**도 기본값이 자동 커밋입니다. pgAdmin 소스의 Query Tool 기본 설정에서 `Auto commit?`은 `True`, `Auto rollback on error?`는 `False`입니다. 두 옵션은 Query Tool의 실행(Execute) 버튼 드롭다운 메뉴에 있습니다.
- pgAdmin에서 이 단원을 진행하려면 수업 PC에서 ① 위 옵션 상태 ② `BEGIN` → UPDATE → `ROLLBACK`을 한 줄씩 실행했을 때 2-2와 같은 결과가 나오는지 미리 확인해 주세요. 이 교안의 결과는 psql에서만 검증했습니다.
- psql에서도 `\set AUTOCOMMIT off`로 자동 커밋을 끌 수 있습니다(이 경우 psql이 첫 문장 앞에 `BEGIN`을 자동으로 붙입니다). 수업에서는 「자동 커밋 on + BEGIN 직접 입력」을 표준으로 통일하는 편이 혼란이 적습니다.
:::

### 2-5. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마 — 0-2에서 만든 사본을 씁니다)

:::try
**[복습]** 태양전장(`vendor_code` = `'V1011'`)에서 사 오는 품목의 단가(`po_price`)를 10% 올렸을 때 업체 단가 합계가 얼마가 되는지 확인하고, **사본은 바뀌지 않게** 되돌리세요. 실행 전·변경 직후·되돌린 후의 합계를 각각 쓰세요.

**[응용]** 아래를 차례로 실행하면 마지막 SELECT 결과는 얼마일까요? 이유를 설명하세요. (확인 후 MOQ를 원래 값 1로 되돌려 두세요.)

```sql
BEGIN;
UPDATE t_part_sourcing SET moq = 600 WHERE part_no = 'EMT73633001';
COMMIT;
UPDATE t_part_sourcing SET moq = 800 WHERE part_no = 'EMT73633001';
ROLLBACK;
SELECT part_no, vendor_code, moq FROM t_part_sourcing WHERE part_no = 'EMT73633001';
```
:::

### 2-5. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
70400 → 77440 → 70400

```sql
SELECT SUM(po_price) AS v1011_total FROM t_part_sourcing WHERE vendor_code = 'V1011';

BEGIN;
UPDATE t_part_sourcing SET po_price = po_price * 1.1 WHERE vendor_code = 'V1011';
SELECT SUM(po_price) AS v1011_total FROM t_part_sourcing WHERE vendor_code = 'V1011';
ROLLBACK;

SELECT SUM(po_price) AS v1011_total FROM t_part_sourcing WHERE vendor_code = 'V1011';
```

```result 실행 전
| v1011_total |
| --- |
| 70400.00 |
```

```result 변경 직후 (UPDATE 8)
| v1011_total |
| --- |
| 77440.00 |
```

```result 되돌린 후
| v1011_total |
| --- |
| 70400.00 |
```

「바꿔 보고 결과만 확인한 뒤 되돌리기」는 실무에서 자주 쓰는 안전한 확인 방법입니다.
:::

### 2-5. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
**800**

```result
COMMIT
UPDATE 1
WARNING:  there is no transaction in progress
ROLLBACK
```

```result
| part_no | vendor_code | moq |
| --- | --- | --- |
| EMT73633001 | V1009 | 800 |
```

600은 `COMMIT`으로 확정되었고, 트랜잭션이 끝난 뒤의 `UPDATE … 800`은 `BEGIN`이 없어 **자동 커밋**되었습니다. 그래서 `ROLLBACK`은 되돌릴 대상이 없어 경고만 냅니다(2-3).

```sql
UPDATE t_part_sourcing SET moq = 1 WHERE part_no = 'EMT73633001';   -- 원래 값으로 복구
```
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 3. 직원 정보 변경 + 이력 INSERT를 한 묶음으로

### 3-1. 이력 테이블 살펴보기 {keep}

```sql
SELECT *
  FROM t_job_history
 ORDER BY employee_id, start_date;
```

```result 총 10행
| employee_id | start_date | end_date | job_id | department_id |
| --- | --- | --- | --- | --- |
| 101 | 1997-09-21 | 2001-10-27 | AC_ACCOUNT | 110 |
| 101 | 2001-10-28 | 2005-03-15 | AC_MGR | 110 |
| 102 | 2001-01-13 | 2006-07-24 | IT_PROG | 60 |
| 114 | 2006-03-24 | 2007-12-31 | ST_CLERK | 50 |
| 122 | 2007-01-01 | 2007-12-31 | ST_CLERK | 50 |
| 176 | 2006-03-24 | 2006-12-31 | SA_REP | 80 |
| 176 | 2007-01-01 | 2007-12-31 | SA_MAN | 80 |
| 200 | 1995-09-17 | 2001-06-17 | AD_ASST | 90 |
| 200 | 2002-07-01 | 2006-12-31 | AC_ACCOUNT | 90 |
| 201 | 2004-02-17 | 2007-12-19 | MK_REP | 20 |
```

### 3-1. 이력 한 행의 뜻과 규칙 {keep}

- 직원이 직무나 부서를 바꾸면 **바꾸기 전**의 직무·부서와 그 기간(`start_date` ~ `end_date`)이 한 행으로 남습니다. 예: 176번은 SA_REP → SA_MAN을 거쳐 2008-01-01부터 지금의 SA_REP입니다.
- PK는 `(employee_id, start_date)` 두 컬럼입니다. ==같은 직원의 같은 시작일 이력은 한 번만== 넣을 수 있습니다.
- `end_date > start_date`라는 CHECK 제약(`jhist_date_interval`)이 있어 **기간이 거꾸로 된 이력**은 들어가지 않습니다.
- 109번은 이력이 없습니다. 입사(2002-08-16) 후 계속 FI_ACCOUNT·재무부(100)였으므로, 이번 발령의 이력은 **2002-08-16 ~ 2026-11-30, FI_ACCOUNT, 100**입니다.

### 3-2. 일부러 실패시키기 — 기간을 거꾸로 넣은 이력 ⭐ {keep}

먼저 **실수한 경우**를 봅니다. 이력의 시작일과 종료일 자리를 **거꾸로** 넣었습니다.

```sql
BEGIN;

UPDATE t_emp
   SET job_id = 'FI_MGR', department_id = 120
 WHERE employee_id = 109;

INSERT INTO t_job_history
VALUES (109, '2026-11-30', '2002-08-16', 'FI_ACCOUNT', 100);
```

```result
BEGIN
UPDATE 1
```

```error
ERROR:  new row for relation "t_job_history" violates check constraint "jhist_date_interval"
DETAIL:  Failing row contains (109, 2026-11-30, 2002-08-16, FI_ACCOUNT, 100).
```

UPDATE는 성공(`UPDATE 1`)했고 INSERT가 CHECK 제약 위반으로 실패했습니다.

### 3-2. 오류가 난 트랜잭션은 「중단(aborted)」 상태 {keep}

:::error 오류가 난 트랜잭션은 「중단(aborted)」 상태
이 상태에서 109번의 직무를 조회해 보면?

```sql
SELECT job_id, department_id FROM t_emp WHERE employee_id = 109;
```

```error
ERROR:  current transaction is aborted, commands ignored until end of transaction block
```

PostgreSQL에서는 트랜잭션 안에서 **문장 하나가 오류를 내면 그 트랜잭션 전체가 중단 상태**가 됩니다. 이후의 문장은 SELECT라도 모두 거부되고, 트랜잭션을 끝내는(`COMMIT` 또는 `ROLLBACK`) 것만 받아들입니다. (저장 지점이 있으면 `ROLLBACK TO SAVEPOINT`도 가능합니다 — 3-6)
:::

### 3-2. 중단된 트랜잭션을 COMMIT하면 {keep}

```sql
COMMIT;
```

```result
ROLLBACK
```

`COMMIT`을 입력했는데 결과는 ==`ROLLBACK`==입니다. 중단된 트랜잭션은 확정할 수 없어 **전부 취소**됩니다.

### 3-2. UPDATE까지 함께 취소 — 원자성 {keep}

```sql
SELECT employee_id, job_id, department_id FROM t_emp WHERE employee_id = 109;

SELECT COUNT(*) AS cnt FROM t_job_history;
```

```result
| employee_id | job_id | department_id |
| --- | --- | --- |
| 109 | FI_ACCOUNT | 100 |
```

```result
| cnt |
| --- |
| 10 |
```

성공했던 UPDATE까지 함께 취소되어 직무는 **FI_ACCOUNT**, 부서는 **100**, 이력도 **10건** 그대로입니다. 「직무·부서는 바뀌었는데 이력은 없는」 반쪽짜리 상태가 생기지 않았습니다. 이것이 **원자성**입니다.

### 3-3. 바르게 실행하기 — 부서장 발령 {keep}

시작일과 종료일을 바로 넣어 다시 실행합니다.

```sql 부서장 발령
BEGIN;

UPDATE t_emp
   SET job_id = 'FI_MGR', department_id = 120
 WHERE employee_id = 109;

INSERT INTO t_job_history
VALUES (109, '2002-08-16', '2026-11-30', 'FI_ACCOUNT', 100);

COMMIT;
```

```result
BEGIN
UPDATE 1
INSERT 0 1
COMMIT
```

### 3-3. 직원과 이력이 함께 반영됐는지 확인 {keep}

```sql
SELECT e.employee_id, e.first_name, e.job_id AS now_job, e.department_id AS now_dept
     , h.start_date, h.end_date, h.job_id AS old_job, h.department_id AS old_dept
  FROM t_emp e
  JOIN t_job_history h
    ON h.employee_id = e.employee_id
 WHERE e.employee_id = 109;
```

```result
| employee_id | first_name | now_job | now_dept | start_date | end_date | old_job | old_dept |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 109 | Daniel | FI_MGR | 120 | 2002-08-16 | 2026-11-30 | FI_ACCOUNT | 100 |
```

### 3-4. 생각해 보기 — 「부서장」 발령인데 부서 테이블은? {keep}

:::try 생각해 보기
3-3은 **직원 테이블과 이력**만 바꿨습니다. 부서 테이블(`t_dept`)에서 Treasury의 부서장(`manager_id`)을 확인해 보세요.

```sql
SELECT e.employee_id, e.first_name, e.department_id, d.department_name, d.manager_id
  FROM t_emp e
  JOIN t_dept d
    ON d.department_id = e.department_id
 WHERE e.employee_id = 109;
```

```result
| employee_id | first_name | department_id | department_name | manager_id |
| --- | --- | --- | --- | --- |
| 109 | Daniel | 120 | Treasury | NULL |
```

직원 테이블은 「109번이 Treasury 부서장(FI_MGR)」이라고 하는데, 부서 테이블의 부서장 칸은 아직 비어 있습니다. 이 상태에서 「부서별 부서장 이름」을 조회하면 Treasury는 어떻게 나올까요?
:::

:::teacher 강사 확인
- 직원 테이블과 부서 테이블이 **서로 다른 말을 하는 상태**를 훈련생이 직접 만든 것입니다. `departments.manager_id`로 부서장 이름을 JOIN하는 보고서에서는 Treasury가 여전히 「부서장 없음」으로 나옵니다. 「트랜잭션으로 묶었다고 끝이 아니라, **무엇을 묶느냐**가 중요하다」로 정리하고 3-5 도전 과제로 넘기세요.
- 생산 데이터의 같은 구조(Q13 UIT 정정 + 이력, Line Type 미갱신 A9)는 복습 문제 1·2에서 다룹니다.
:::

### 3-5. 도전 — 세 문장을 한 묶음으로 {keep}

**과제:** 0-1 스크립트로 HR 사본을 처음 상태로 되돌린 뒤, 109번의 **직무·부서 변경 + Treasury 부서장 지정 + 이력**을 한 트랜잭션으로 실행하세요.

```sql
BEGIN;

UPDATE t_emp  SET job_id = 'FI_MGR', department_id = 120 WHERE employee_id = 109;
UPDATE t_dept SET manager_id = 109                       WHERE department_id = 120;

INSERT INTO t_job_history
VALUES (109, '2002-08-16', '2026-11-30', 'FI_ACCOUNT', 100);

COMMIT;
```

```result
BEGIN
UPDATE 1
UPDATE 1
INSERT 0 1
COMMIT
```

### 3-5. 직원 ↔ 부서 짝 확인 {keep}

```sql
SELECT e.employee_id, e.first_name, e.job_id, d.department_name, d.manager_id
     , h.job_id AS old_job, h.end_date
  FROM t_emp e
  JOIN t_dept        d ON d.department_id = e.department_id
  JOIN t_job_history h ON h.employee_id   = e.employee_id
 WHERE e.employee_id = 109;
```

```result
| employee_id | first_name | job_id | department_name | manager_id | old_job | end_date |
| --- | --- | --- | --- | --- | --- | --- |
| 109 | Daniel | FI_MGR | Treasury | 109 | FI_ACCOUNT | 2026-11-30 |
```

직원(FI_MGR, Treasury) ↔ 부서(부서장 109)가 짝이 맞고, 이력도 남았습니다. ==관련된 변경을 모두 한 트랜잭션 안에 넣어야== 「한쪽만 바뀐」 데이터가 생기지 않습니다.

### 3-6. SAVEPOINT — 일부만 되돌리기 {keep}

3-2처럼 이력 하나 때문에 **처음부터 다시** 하기는 번거롭습니다. **`SAVEPOINT`** 는 트랜잭션 중간에 **되돌아올 지점**을 표시합니다.

| 명령 | 뜻 |
| --- | --- |
| `SAVEPOINT 이름;` | 지금 위치를 저장 |
| `ROLLBACK TO SAVEPOINT 이름;` | 저장한 위치 **이후**의 변경만 취소 (앞의 변경은 유지, 트랜잭션은 계속) |

### 3-6. 승진 — 이력의 시작일을 잘못 넣으면 {keep}

**예:** 176번 Jonathon Taylor(영업 사원 SA_REP)를 영업 관리자(SA_MAN)로 승진시킵니다. 3-1에서 본 것처럼 176번은 이력이 이미 2건이라 지금 직무는 **2008-01-01**부터인데, 이력의 시작일에 입사일(**2006-03-24**)을 넣었습니다. (3-5 실행 후 이어서)

```sql
BEGIN;

UPDATE t_emp SET job_id = 'SA_MAN' WHERE employee_id = 176;

SAVEPOINT before_hist;

INSERT INTO t_job_history
VALUES (176, '2006-03-24', '2026-11-30', 'SA_REP', 80);
```

```result
BEGIN
UPDATE 1
SAVEPOINT
```

```error
ERROR:  duplicate key value violates unique constraint "t_job_history_pkey"
DETAIL:  Key (employee_id, start_date)=(176, 2006-03-24) already exists.
```

### 3-6. 저장 지점으로 돌아가 INSERT만 다시 {keep}

```sql
ROLLBACK TO SAVEPOINT before_hist;

INSERT INTO t_job_history
VALUES (176, '2008-01-01', '2026-11-30', 'SA_REP', 80);

COMMIT;
```

```result
ROLLBACK
INSERT 0 1
COMMIT
```

### 3-6. 결과 확인 {keep}

```sql
SELECT e.employee_id, e.first_name, e.job_id AS now_job
     , h.start_date, h.end_date, h.job_id AS old_job
  FROM t_emp e
  JOIN t_job_history h ON h.employee_id = e.employee_id
 WHERE e.employee_id = 176
 ORDER BY h.start_date;
```

```result
| employee_id | first_name | now_job | start_date | end_date | old_job |
| --- | --- | --- | --- | --- | --- |
| 176 | Jonathon | SA_MAN | 2006-03-24 | 2006-12-31 | SA_REP |
| 176 | Jonathon | SA_MAN | 2007-01-01 | 2007-12-31 | SA_MAN |
| 176 | Jonathon | SA_MAN | 2008-01-01 | 2026-11-30 | SA_REP |
```

- `SAVEPOINT` 앞의 UPDATE는 살아 있고, 실패한 INSERT만 취소된 뒤 2008-01-01로 다시 들어갔습니다.
- `ROLLBACK TO SAVEPOINT`는 3-2의 **중단 상태에서 트랜잭션을 되살리는** 방법이기도 합니다. 저장 지점이 없으면 `ROLLBACK`으로 전부 취소하고 처음부터 다시 해야 합니다.

:::teacher 강사 확인
- psql에는 `\set ON_ERROR_ROLLBACK on` 옵션이 있습니다. 켜 두면 psql이 문장마다 저장 지점을 자동으로 만들어, 오류가 나도 트랜잭션이 중단되지 않고 실패한 문장만 취소됩니다(검증: 켜고 PK 중복을 냈을 때 앞의 UPDATE가 유지됨). 편하지만 「오류가 나면 전부 취소」라는 원자성 감각을 익히기 전에는 쓰지 않는 것을 권장합니다.
- 원본 `employees`에서는 직무·부서를 UPDATE하면 트리거(`update_job_history`)가 이전 이력을 자동으로 넣습니다. 이 트리거가 넣은 행도 같은 트랜잭션의 일부라 `ROLLBACK`하면 함께 취소됩니다. 다만 원본에는 근무 시간 밖의 변경을 막는 트리거(`secure_employees`)도 있으니, 시연하려면 평일 08:00~18:00에 `BEGIN` … `ROLLBACK`으로만 하세요.
:::

### 3-7. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마 — 0-2에서 만든 사본을 씁니다)

:::try
**[복습]** 아래를 실행한 뒤 스테이터(`EMT73633001`)의 UIT(`t_part_master`)와 단가(`t_part_sourcing.po_price`)는 각각 무엇일까요? 조회해 확인하고 이유를 설명하세요. (`uit` 컬럼은 한 글자짜리 `char(1)`입니다.)

```sql
BEGIN;
UPDATE t_part_sourcing SET po_price = 30000 WHERE part_no = 'EMT73633001';
UPDATE t_part_master   SET uit = 'DD'       WHERE part_no = 'EMT73633001';
COMMIT;
```

**[응용]** 가스켓(`MGK31172901`)의 리드타임은 지금 10입니다. 저장 지점을 두 개 만든 아래 트랜잭션에서 ①의 결과, ②에서 일어나는 일, ③의 결과를 예측하고 확인하세요.

```sql
BEGIN;
UPDATE t_part_sourcing SET lead_time_days = 20 WHERE part_no = 'MGK31172901';
SAVEPOINT sp_a;
UPDATE t_part_sourcing SET lead_time_days = 30 WHERE part_no = 'MGK31172901';
SAVEPOINT sp_b;
ROLLBACK TO SAVEPOINT sp_a;
SELECT part_no, lead_time_days FROM t_part_sourcing WHERE part_no = 'MGK31172901';   -- ①
ROLLBACK TO SAVEPOINT sp_b;                                                           -- ②
COMMIT;
SELECT part_no, lead_time_days FROM t_part_sourcing WHERE part_no = 'MGK31172901';   -- ③
```
:::

### 3-7. 확인 문제 답 — 복습 ① 둘 다 그대로 {keep}

:::answer [복습] 예시 답안 ①
UIT **G**, 단가 **28000** — **둘 다 그대로**

```result
BEGIN
UPDATE 1
```

```error
ERROR:  value too long for type character(1)
```

```result
ROLLBACK
```

```result
| part_no | uit | po_price |
| --- | --- | --- |
| EMT73633001 | G | 28000.00 |
```

(조회는 답안 ②의 SELECT와 같습니다.) 두 번째 UPDATE가 `char(1)`에 두 글자를 넣으려다 실패해 트랜잭션이 중단되었고, `COMMIT`이 `ROLLBACK`으로 처리되어 첫 번째 UPDATE(단가 30000)도 취소되었습니다(3-2).
:::

### 3-7. 확인 문제 답 — 복습 ② SAVEPOINT로 살리기 {keep}

:::answer [복습] 예시 답안 ②
첫 번째 UPDATE를 살리려면 `SAVEPOINT`를 씁니다. (확인 후 `ROLLBACK`으로 사본을 지킵니다.)

```sql
BEGIN;
UPDATE t_part_sourcing SET po_price = 30000 WHERE part_no = 'EMT73633001';
SAVEPOINT sp1;
UPDATE t_part_master SET uit = 'DD' WHERE part_no = 'EMT73633001';      -- 오류
ROLLBACK TO SAVEPOINT sp1;
SELECT p.part_no, p.uit, s.po_price
  FROM t_part_master p
  JOIN t_part_sourcing s ON s.part_no = p.part_no
 WHERE p.part_no = 'EMT73633001';
ROLLBACK;
```

```result
| part_no | uit | po_price |
| --- | --- | --- |
| EMT73633001 | G | 30000.00 |
```
:::

### 3-7. 확인 문제 답 — 응용 ① 저장 지점 sp_a로 {keep}

:::answer [응용] 예시 답안 ①
① **20**

```result ①
| part_no | lead_time_days |
| --- | --- |
| MGK31172901 | 20 |
```

`ROLLBACK TO SAVEPOINT sp_a`는 sp_a **이후**의 변경(30)을 취소합니다. sp_a 앞의 UPDATE(20)는 남아 있습니다.
:::

### 3-7. 확인 문제 답 — 응용 ② 사라진 sp_b {keep}

:::answer [응용] 예시 답안 ②
② 오류, ③ **10**

```error ②
ERROR:  savepoint "sp_b" does not exist
```

```result COMMIT의 결과
ROLLBACK
```

```result ③
| part_no | lead_time_days |
| --- | --- |
| MGK31172901 | 10 |
```

sp_a로 돌아갈 때 그 **뒤에 만든 저장 지점 sp_b도 함께 없어졌습니다.** 그래서 ②는 오류이고, 오류로 트랜잭션이 중단되어 `COMMIT`이 `ROLLBACK`으로 처리됩니다(3-2). 살아 있던 20까지 모두 취소되어 처음 값 10이 남습니다.
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 4. TRUNCATE · DROP도 트랜잭션 안에서

### 4-1. BEGIN 안의 TRUNCATE는 되돌릴 수 있다 {keep}

`TRUNCATE`(테이블의 모든 행 삭제)와 `DROP TABLE`(테이블 삭제)은 DDL이지만, PostgreSQL에서는 `BEGIN` 안에서 실행하면 **ROLLBACK으로 되돌릴 수 있습니다.**

```sql
BEGIN;
TRUNCATE t_job_history;
SELECT COUNT(*) FROM t_job_history;
ROLLBACK;

SELECT COUNT(*) FROM t_job_history;
```

```result TRUNCATE 직후
| count |
| --- |
| 0 |
```

```result ROLLBACK 후 (TRUNCATE 전과 같은 행 수 — 3-5·3-6까지 실행했다면 12)
| count |
| --- |
| 12 |
```

### 4-1. BEGIN 안의 DROP TABLE도 {keep}

```sql
BEGIN;
DROP TABLE t_job_history;
SELECT COUNT(*) FROM t_job_history;
```

```result
BEGIN
DROP TABLE
```

```error
ERROR:  relation "t_job_history" does not exist
LINE 1: SELECT COUNT(*) FROM t_job_history;
                             ^
```

```sql
ROLLBACK;

SELECT COUNT(*) FROM t_job_history;
```

```result
| count |
| --- |
| 12 |
```

테이블이 삭제된 것처럼 보였지만 `ROLLBACK`으로 12행과 함께 돌아왔습니다. (12행 = 원래 10건 + 3-5의 109번 + 3-6의 176번)

### 4-2. 그래도 주의할 점 ① BEGIN이 없으면 즉시 확정 ⭐ {keep}

:::error BEGIN이 없으면 TRUNCATE도 즉시 확정
2-3과 똑같습니다. `BEGIN` 없이 실행한 `TRUNCATE`는 자동 커밋되어 되돌릴 수 없습니다.

```sql
TRUNCATE t_emp;
ROLLBACK;
SELECT COUNT(*) FROM t_emp;
```

```error
TRUNCATE TABLE
WARNING:  there is no transaction in progress
ROLLBACK
```

```result
| count |
| --- |
| 0 |
```

직원 107명이 모두 사라졌습니다. (사본이므로 0-1 스크립트로 복구하세요.) ==지우거나 구조를 바꾸는 명령은 반드시 `BEGIN` 안에서 먼저 실행해 보고, 확인한 뒤 `COMMIT`== 하는 습관을 들이세요.
:::

### 4-2. 그래도 주의할 점 ② 트랜잭션 안에서 못 쓰는 명령 {keep}

:::error 트랜잭션 안에서 실행할 수 없는 명령도 있음
```sql
BEGIN;
CREATE DATABASE test_db;
```

```error
ERROR:  CREATE DATABASE cannot run inside a transaction block
```

`CREATE DATABASE`처럼 트랜잭션 블록 안에서 거부되는 명령이 있습니다. 「모든 명령이 ROLLBACK된다」가 아니라, ==실행해서 확인한 명령만 믿는다==가 원칙입니다. 위 상태는 중단 상태이므로 `ROLLBACK`으로 끝냅니다.

```sql
ROLLBACK;
```
:::

### 4-3. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** 사본 `t_uit_history`를 `TRUNCATE`한 뒤 행 수를 확인하고, 원래대로 되돌리세요. 되돌린 뒤의 행 수는?

**[응용]** 같은 방법으로 **원본** `part_master`를 `TRUNCATE`해 보세요. 어떤 일이 일어나고, 그 이유는 무엇인가요? (`BEGIN` 안에서 실행하고 `ROLLBACK`으로 끝내세요.)
:::

### 4-3. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
5행 → 0행 → 5행

```sql
BEGIN;
TRUNCATE t_uit_history;
SELECT COUNT(*) AS hist_cnt FROM t_uit_history;
ROLLBACK;
SELECT COUNT(*) AS hist_cnt FROM t_uit_history;
```

```result TRUNCATE 직후
| hist_cnt |
| --- |
| 0 |
```

```result ROLLBACK 후
| hist_cnt |
| --- |
| 5 |
```
:::

### 4-3. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
```sql
BEGIN;
TRUNCATE part_master;
ROLLBACK;
```

```error
ERROR:  cannot truncate a table referenced in a foreign key constraint
DETAIL:  Table "bom_structure" references "part_master".
HINT:  Truncate table "bom_structure" at the same time, or use TRUNCATE ... CASCADE.
```

`bom_structure.child_part_no` 등이 `part_master`를 참조하는 FK라서, 부모 테이블만 비울 수 없습니다(1단원 참조 무결성). 오류에는 하나만 나오지만 `part_sourcing`, `inventory` 등 여러 테이블이 `part_master`를 참조합니다. HINT의 `CASCADE`는 참조하는 테이블까지 함께 비우므로 실습 원본에서는 실행하지 마세요. (사본 `t_part_master`는 FK가 복사되지 않아 이 보호가 없습니다 — 0-3.)
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 5. 세션 · 읽기 일관성 · LOCK

### 5-1. 세션이란 {keep}

**세션(session)** 은 DB에 접속해 있는 **연결 하나**입니다. SQL Shell (psql)을 **2개 띄우면 세션 2개**입니다. 트랜잭션은 세션마다 따로 진행됩니다.

창 2개를 띄우고 각 창에서 실행해 보세요. 숫자가 다르면 서로 다른 세션입니다.

```sql
SET search_path TO hr;
SELECT pg_backend_pid();
```

이 장의 실습은 **아래 순서대로 창을 번갈아** 실행합니다. 대상은 100번 직원 Steven King의 급여(현재 **24000**)입니다. 4-2에서 사본을 비웠다면 0-1 스크립트를 먼저 다시 실행하세요.

### 5-2. 읽기 일관성 — 확정 전의 변경은 남에게 안 보인다 {keep}

| 순서 | 세션 1 (인사 담당) | 세션 2 (급여 담당) |
| --- | --- | --- |
| ① | `BEGIN;` | |
| ② | `UPDATE t_emp SET salary = salary + 1000 WHERE employee_id = 100;` | |
| ③ | `SELECT employee_id, salary FROM t_emp WHERE employee_id = 100;` → **25000** | |
| ④ | | `SELECT employee_id, salary FROM t_emp WHERE employee_id = 100;` → **24000** |

### 5-2. 두 세션의 결과 {keep}

:::cols
```result ③ 세션 1
| employee_id | salary |
| --- | --- |
| 100 | 25000.00 |
```

```result ④ 세션 2
| employee_id | salary |
| --- | --- |
| 100 | 24000.00 |
```
:::

- 세션 1은 자기가 바꾼 **25000**을 보지만, 세션 2는 **확정된 값 24000**을 봅니다.
- 확정되지 않은 변경이 남에게 보이지 않는 것을 **읽기 일관성**이라고 합니다(ACID의 고립성). 세션 1이 결국 `ROLLBACK`할 수도 있는 값을 다른 사람이 보고 판단하면 안 되기 때문입니다.

### 5-2. 기본 격리 수준 — Read Committed {keep}

PostgreSQL의 기본 격리 수준(isolation level — 1-3의 고립성을 어느 정도까지 지킬지 정하는 설정)은 **Read Committed**입니다. 이 수준에서 SELECT는 **쿼리가 시작되기 전에 확정된 데이터만** 봅니다.

```sql
SHOW default_transaction_isolation;
```

```result
| default_transaction_isolation |
| --- |
| read committed |
```

### 5-3. LOCK — 같은 행을 동시에 고치면 기다린다 {keep}

이어서 세션 2도 같은 행을 바꿉니다.

| 순서 | 세션 1 (인사 담당) | 세션 2 (급여 담당) |
| --- | --- | --- |
| ⑤ | | `UPDATE t_emp SET salary = salary + 500 WHERE employee_id = 100;` → **결과가 안 나오고 멈춤** |
| ⑥ | `COMMIT;` | → 그 순간 `UPDATE 1` 출력 |
| ⑦ | | `SELECT …` → **25500** |

```result ⑦ 세션 2
| employee_id | salary |
| --- | --- |
| 100 | 25500.00 |
```

### 5-3. 기다린 쪽은 확정된 값을 기준으로 {keep}

- 세션 1이 UPDATE한 행은 트랜잭션이 끝날 때(`COMMIT`/`ROLLBACK`)까지 **잠겨(LOCK)** 있습니다. 세션 2의 UPDATE는 **오류 없이 기다립니다.**
- 세션 1이 `COMMIT`하면 세션 2는 **확정된 25000을 기준으로** +500을 적용해 25500이 됩니다. 두 사람의 변경(+1000, +500)이 모두 반영되었습니다.
- 세션 1이 `COMMIT` 대신 `ROLLBACK`했다면 세션 2는 **원래 값 24000을 기준으로** 적용해 **24500**이 됩니다.

### 5-3. LOCK은 행 단위, 조회는 막지 않습니다 {keep}

**서로 다른 행이면 기다리지 않습니다.** 세션 1에서 다시 `BEGIN`과 ②의 UPDATE를 실행해 100번 직원의 행을 잡아 둔 상태에서, 다른 세션에서 다른 직원(101번 Neena Kochhar)을 UPDATE하면 바로 `UPDATE 1`이 나옵니다. LOCK은 **행 단위**입니다.

> 행 잠금은 **조회를 막지 않습니다.** ④처럼 세션 1이 잠그고 있는 동안에도 세션 2의 SELECT는 바로 결과가 나옵니다. 막히는 것은 같은 행을 **고치려는** 문장입니다.

### 5-4. 누가 누구를 기다리는지 확인하기 {keep}

세션 1에서 다시 `BEGIN`과 ②의 UPDATE를 실행해 행을 잡아 둔 상태에서, 세션 2가 ⑤의 UPDATE를 다시 실행해 멈춰 있을 때 **세 번째 창**에서 아래를 실행하면 대기 상황이 보입니다.

```sql
SELECT pid
     , pg_blocking_pids(pid) AS blocked_by
     , state
     , wait_event_type
     , left(query, 50)       AS query
  FROM pg_stat_activity
 WHERE datname = current_database()
   AND pid <> pg_backend_pid()
   AND backend_type = 'client backend'
 ORDER BY pid;
```

```result pid 숫자는 실행할 때마다 다릅니다 · query는 그 세션이 마지막으로 실행한 문장입니다
| pid | blocked_by | state | wait_event_type | query |
| --- | --- | --- | --- | --- |
| 444 | {} | idle in transaction | Client | UPDATE t_emp SET salary = salary + 1000 WHERE empl |
| 445 | {444} | active | Lock | UPDATE t_emp SET salary = salary + 500 WHERE emplo |
```

### 5-4. 결과 읽기 — idle in transaction {keep}

- 세션 1(444)은 **`idle in transaction`** — 트랜잭션을 열어 둔 채 아무것도 하지 않는 상태입니다.
- 세션 2(445)는 `wait_event_type = Lock`, `blocked_by = {444}` — **444 때문에 기다리는 중**입니다.
- `query`는 그 세션이 **마지막으로 실행한 문장**입니다. 세션 1이 UPDATE 뒤에 SELECT를 실행했다면 그 SELECT가 보입니다.

==`BEGIN`을 열어 놓고 자리를 비우면 다른 사람의 작업이 멈춥니다.== 트랜잭션은 짧게, 확인이 끝나면 바로 `COMMIT` 또는 `ROLLBACK`으로 닫으세요.

### 5-4. 무한정 기다리지 않게 하기 — lock_timeout {keep}

세션에 `lock_timeout`을 걸면 지정한 시간만 기다리고 오류를 냅니다.

```sql
SET lock_timeout = '1s';

UPDATE t_emp SET salary = salary + 1 WHERE employee_id = 100;
```

```error 다른 세션이 같은 행을 잡고 있을 때
SET
ERROR:  canceling statement due to lock timeout
```

확인이 끝나면 설정을 기본값으로 되돌립니다. 되돌리지 않으면 이 창에서는 이후의 잠금 대기가 모두 1초 뒤 오류로 끝납니다.

```sql
RESET lock_timeout;
```

> 실습이 끝나면 세션 1에서 `ROLLBACK;`으로 트랜잭션을 닫습니다.

:::teacher 강사 확인
- 기존 `11. TCL.txt`의 「SQL Developer 2개 연결」 실습을 「SQL Shell (psql) 2개」로 바꾼 것입니다. pgAdmin에서 Query Tool 창 2개로 진행하려면 수업 PC에서 두 창의 `SELECT pg_backend_pid();` 값이 다른지 먼저 확인하세요(같으면 같은 세션이라 실습이 성립하지 않습니다).
- 수업 중 누군가 `BEGIN`을 열어 둔 채 다른 실습으로 넘어가면 옆 사람의 UPDATE가 멈춥니다. 「멈췄다」는 질문이 나오면 5-4 쿼리로 `idle in transaction` 세션을 찾아 그 창에서 `ROLLBACK;`을 실행하게 하세요.
- 두 트랜잭션이 서로의 행을 기다리면(교착 상태, deadlock) PostgreSQL이 이를 감지해 한쪽 트랜잭션을 중단시킵니다. 이 교안에서는 실습하지 않았으며, 질문이 나오면 「여러 행을 고칠 때는 모두 같은 순서로 고친다」로 답하세요.
:::

### 5-5. 확인 문제 — 생산 데이터 {keep}

> 실행 전: 두 창 모두 `SET search_path TO bom;`

:::try
**[복습]** 도어 가스켓(`MGK25528301`)의 리드타임은 10입니다. 아래 순서로 실행할 때, ②의 결과와 ⑤의 최종 리드타임을 예측하고 직접 확인하세요. (확인 후 `UPDATE t_part_sourcing SET lead_time_days = 10 WHERE part_no = 'MGK25528301';`으로 되돌립니다.)

| 순서 | 세션 1 (자재 담당) | 세션 2 (구매 담당) |
| --- | --- | --- |
| ① | `BEGIN;` `UPDATE t_part_sourcing SET lead_time_days = lead_time_days + 5 WHERE part_no = 'MGK25528301';` | |
| ② | | `SELECT part_no, lead_time_days FROM t_part_sourcing WHERE part_no = 'MGK25528301';` |
| ③ | | `UPDATE t_part_sourcing SET lead_time_days = lead_time_days + 10 WHERE part_no = 'MGK25528301';` |
| ④ | `COMMIT;` | |
| ⑤ | | `SELECT part_no, lead_time_days FROM t_part_sourcing WHERE part_no = 'MGK25528301';` |

**[응용]** (복습을 마치고 리드타임을 10으로 되돌린 뒤 ①부터 다시 실행합니다. 확인 후 다시 10으로 되돌립니다.) ③을 `UPDATE t_part_sourcing SET lead_time_days = 20 WHERE part_no = 'MGK25528301';`(② 화면에서 본 10에 10을 직접 더한 값)으로 바꾸면 ⑤의 결과는 어떻게 될까요? 무엇이 문제인지 설명하세요.
:::

### 5-5. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
② **10**, ⑤ **25**

```result ② 세션 2
| part_no | lead_time_days |
| --- | --- |
| MGK25528301 | 10 |
```

```result ⑤ 세션 2
| part_no | lead_time_days |
| --- | --- |
| MGK25528301 | 25 |
```

②에서는 세션 1의 +5가 확정 전이라 보이지 않습니다(5-2). ③은 세션 1의 잠금 때문에 기다리다가, ④ `COMMIT` 직후 **확정된 15를 기준으로** +10이 적용됩니다(5-3).
:::

### 5-5. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
⑤ = **20**. 세션 1의 +5가 **사라집니다.** (본문의 HR 예로 바꾸면: 세션 1이 24000 → +1000, 세션 2가 화면에서 본 24000에 500을 더해 `SET salary = 24500` → 최종 **24500**, 세션 1의 +1000 유실)

`SET lead_time_days = 20`은 「지금 값에 10을 더하라」가 아니라 「20으로 덮어써라」이므로, 기다린 뒤에도 세션 1이 만든 15를 무시하고 덮어씁니다. ==화면에서 본 값으로 계산해 넣지 말고, `lead_time_days = lead_time_days + 10`처럼 SQL 안에서 계산==해야 동시에 고쳐도 변경이 유실되지 않습니다.
:::

> 확인 문제를 마치면 **두 창 모두** `SET search_path TO hr;`으로 돌아옵니다.

## 6. 복습 문제

### 6-0. 복습 문제 안내 {keep}

> 범위: 트랜잭션 전체(BEGIN · COMMIT · ROLLBACK · 중단 상태 · SAVEPOINT · TRUNCATE · 세션과 LOCK). **0-2 스크립트로 생산 데이터 사본을 처음 상태로 되돌린 뒤** `bom` 스키마의 사본 테이블로 풀어 주세요(실행 전: `SET search_path TO bom;`).

```icons 일곱 문항
history | 1 · BEGIN · COMMIT (Q13) | 스테이터 UIT 정정 + 이력 | rose
link | 2 · 도전 | UIT · Line Type · 이력 한 묶음 | plum
history | 3 · BEGIN · COMMIT | 로터 UIT 정정 + 이력 | lime
refresh-cw | 4 · 자동 커밋 | ROLLBACK은 어디까지? | ivory
git-branch | 5 · 중단 · SAVEPOINT | 이력 번호 실수 바로잡기 | plum
lock | 6 · (심화) 두 세션 | LOCK 후 ROLLBACK | ivory
trash-2 | 7 · (심화) TRUNCATE | BEGIN 안에서 먼저 | hot
```

### 6-1. 복습 1 (Q13) {keep}

**1.** Day 2 5교시(Q5)에서 찾은 **스테이터(`EMT73633001`)** 는 해외 업체(V1009)에서 들여오는데 UIT가 G(국내 구매품)입니다. UIT를 D(수입 구매품)로 정정하고 이력을 `t_uit_history`에 남기는 작업을 한 트랜잭션으로 실행한 뒤, 마스터와 이력을 JOIN해 확인하세요. 이어서 스테이터의 Line Type(`t_part_sourcing.line_type`)을 조회하고, 이력의 `line_type_updated` = N이 무엇을 남긴 것인지 설명하세요.

- 이력 값: `change_id` 6 (지금 5건, 1~5 사용 중), `old_uit` `'G'`, `new_uit` `'D'`, `changed_by_dept` `'Procurement'`, `change_reason` `'해외 벤더 조달 확인, UIT 정정'`, `changed_at` `CURRENT_DATE`, `line_type_updated` `'N'`
- `code_line_type`에서 D는 「Domestic (UIT G)」, I는 「Import (UIT D)」입니다.

:::cols
```result 마스터 + 이력
| part_no | description_kr | now_uit | change_id | old_uit | new_uit | line_type_updated |
| --- | --- | --- | --- | --- | --- | --- |
| EMT73633001 | 스테이터 | D | 6 | G | D | N |
```

```result Line Type
| part_no | uit | vendor_code | line_type |
| --- | --- | --- | --- |
| EMT73633001 | D | V1009 | D |
```
:::

### 6-2. 복습 2 (도전) {keep}

**2.** (도전) 0-2 스크립트로 다시 초기화한 뒤, 스테이터의 **UIT 정정(G → D) + Line Type 정정(D → I) + 이력(Y)** 을 한 트랜잭션으로 실행하고, 마스터·소싱·이력을 JOIN해 짝을 확인하세요.

- 이력 값: 1번과 같고, `change_reason`만 `'해외 벤더 조달 확인, UIT·Line Type 정정'`, `line_type_updated`는 `'Y'`

```result 출력 결과 (총 1행)
| part_no | uit | line_type | change_id | line_type_updated |
| --- | --- | --- | --- | --- |
| EMT73633001 | D | I | 6 | Y |
```

### 6-3. 복습 3 {keep}

**3.** 2번에 이어서, 로터(`EMT78269001`)의 UIT를 G → D로 정정하고, 이력을 `t_uit_history`에 남기는 작업을 한 트랜잭션으로 실행한 뒤, 마스터·소싱·이력을 JOIN해 확인하세요.

- 이력 값: `change_id` 7, `old_uit` `'G'`, `new_uit` `'D'`, `changed_by_dept` `'Procurement'`, `change_reason` `'수입 조달 확인, UIT 정정'`, `changed_at` `CURRENT_DATE`, `line_type_updated` `'Y'`
- (로터의 Line Type은 이미 I이므로 Y로 기록합니다.)
- (이력 번호는 2번의 6번 다음인 7번을 씁니다.)

```result 출력 결과 (총 1행)
| part_no | description_kr | uit | line_type | change_id | old_uit | new_uit | line_type_updated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EMT78269001 | 로터 | D | I | 7 | G | D | Y |
```

### 6-4. 복습 4 {keep}

**4.** 아래를 차례로 실행하면 ①과 ②의 SELECT 결과는 각각 얼마일까요? (실행 전 리드타임 10)

```sql
BEGIN;
UPDATE t_part_sourcing SET lead_time_days = 12 WHERE part_no = 'MGK25528301';
ROLLBACK;
UPDATE t_part_sourcing SET lead_time_days = 14 WHERE part_no = 'MGK25528301';
BEGIN;
UPDATE t_part_sourcing SET lead_time_days = 16 WHERE part_no = 'MGK25528301';
SELECT part_no, lead_time_days FROM t_part_sourcing WHERE part_no = 'MGK25528301';   -- ①
ROLLBACK;
SELECT part_no, lead_time_days FROM t_part_sourcing WHERE part_no = 'MGK25528301';   -- ②
```

```result 출력 결과
| 순서 | part_no | lead_time_days |
| --- | --- | --- |
| ① | MGK25528301 | 16 |
| ② | MGK25528301 | 14 |
```

### 6-5. 복습 5 {keep}

**5.** (0-2 스크립트로 다시 초기화) 3번 작업에서 이력 번호를 **3**으로 잘못 넣고 `COMMIT`하면 로터의 UIT와 로터 이력 건수는 어떻게 될까요? 이어서, `SAVEPOINT`를 써서 UPDATE는 살리고 이력만 7번으로 다시 넣는 트랜잭션을 작성하세요.

:::cols
```result 잘못 넣고 COMMIT한 뒤
| part_no | uit | cnt (로터 이력 건수) |
| --- | --- | --- |
| EMT78269001 | G | 0 |
```

```result SAVEPOINT로 고친 뒤
| part_no | uit | change_id |
| --- | --- | --- |
| EMT78269001 | D | 7 |
```
:::

### 6-6. 복습 6 (심화) {keep}

**6.** (심화) 두 세션으로 실행합니다. 두 창 모두 `SET search_path TO bom;`을 먼저 실행하세요. 도어 가스켓(`MGK25528301`)의 리드타임은 10입니다. ①의 결과, ②에서 일어나는 일, ③의 결과를 쓰세요.

```text 실행 순서
세션 1: BEGIN; UPDATE … SET lead_time_days = lead_time_days + 5 …;
세션 2: SELECT …;                                              -- ①
세션 2: UPDATE … SET lead_time_days = lead_time_days + 10 …;   -- ②
세션 1: ROLLBACK;
세션 2: SELECT …;                                              -- ③
```

```result 출력 결과
①  10
②  세션 1이 끝날 때까지 기다림 (세션 1 ROLLBACK 직후 UPDATE 1)
③  20
```

### 6-7. 복습 7 (심화) {keep}

**7.** (심화) 아래 두 문장 중 「`BEGIN` 없이 실행하면 안 되는」 것을 고르고, 안전하게 실행하는 순서를 SQL로 쓰세요. 실행 후 결과를 확인하고 되돌리는 것까지 포함합니다.

- (가) `SELECT COUNT(*) FROM t_part_sourcing;`
- (나) `TRUNCATE t_part_sourcing;`

```result 출력 결과
TRUNCATE 직후 count 0  →  ROLLBACK 후 count 52
```

### 6-8. 복습 1 답 {keep}

:::answer 복습 1 예시 답안
```sql 1
BEGIN;
UPDATE t_part_master
   SET uit = 'D'
 WHERE part_no = 'EMT73633001';
INSERT INTO t_uit_history
VALUES (6, 'EMT73633001', 'G', 'D', 'Procurement', '해외 벤더 조달 확인, UIT 정정', CURRENT_DATE, 'N');
COMMIT;

SELECT p.part_no, p.description_kr, p.uit AS now_uit
     , h.change_id, h.old_uit, h.new_uit, h.line_type_updated
  FROM t_part_master p
  JOIN t_uit_history h ON h.part_no = p.part_no
 WHERE p.part_no = 'EMT73633001';

SELECT p.part_no, p.uit, s.vendor_code, s.line_type
  FROM t_part_master p
  JOIN t_part_sourcing s ON s.part_no = p.part_no
 WHERE p.part_no = 'EMT73633001';
```

- UIT는 D(수입)가 되었는데 Line Type은 아직 D(국내)입니다. 이력의 N은 「Line Type은 갱신하지 않았다」는 정직한 기록이고, 이 모양이 Day 2에서 진단한 **A9**(UIT 변경 후 Line Type 미갱신 → A1의 원인)입니다.
:::

### 6-9. 복습 2 답 {keep}

:::answer 복습 2 예시 답안
```sql 2
BEGIN;

UPDATE t_part_master   SET uit = 'D'       WHERE part_no = 'EMT73633001';
UPDATE t_part_sourcing SET line_type = 'I' WHERE part_no = 'EMT73633001';

INSERT INTO t_uit_history
VALUES (6, 'EMT73633001', 'G', 'D', 'Procurement', '해외 벤더 조달 확인, UIT·Line Type 정정', CURRENT_DATE, 'Y');

COMMIT;

SELECT p.part_no, p.uit, s.line_type, h.change_id, h.line_type_updated
  FROM t_part_master p
  JOIN t_part_sourcing s ON s.part_no = p.part_no
  JOIN t_uit_history   h ON h.part_no = p.part_no
 WHERE p.part_no = 'EMT73633001';
```

- UIT(D) ↔ Line Type(I)이 짝이 맞고 이력에도 Y가 남았습니다. 본문 3-5(부서장 발령 + 부서 테이블)와 같은 원리입니다.
:::

:::teacher 강사 확인
- 1번은 README 4장 **A9**(UIT 변경 후 Line Type 미갱신, `line_type_updated = 'N'` → A1의 원인 서사)과 같은 상태를 **훈련생이 직접 만드는** 문제입니다. 「이력은 정직하게 N을 남겼지만, UIT와 Line Type이 다시 어긋났다」로 정리하고 2번으로 넘기세요.
- Q13 원 정답(`exercises_mysql.sql`)은 `START TRANSACTION`(MySQL)이며, PostgreSQL에서는 `BEGIN`으로 씁니다. 1번의 이력 INSERT 값은 원 정답과 같습니다.
:::

### 6-10. 복습 3 · 4 답 {keep}

:::answer 복습 3 · 4 예시 답안
```sql 3
BEGIN;
UPDATE t_part_master SET uit = 'D' WHERE part_no = 'EMT78269001';
INSERT INTO t_uit_history
VALUES (7, 'EMT78269001', 'G', 'D', 'Procurement', '수입 조달 확인, UIT 정정', CURRENT_DATE, 'Y');
COMMIT;

SELECT p.part_no, p.description_kr, p.uit, s.line_type
     , h.change_id, h.old_uit, h.new_uit, h.line_type_updated
  FROM t_part_master p
  JOIN t_part_sourcing s ON s.part_no = p.part_no
  JOIN t_uit_history   h ON h.part_no = p.part_no
 WHERE p.part_no = 'EMT78269001';
```

- 4번: 첫 `ROLLBACK`은 12를 취소, `BEGIN` 없는 14는 자동 커밋, 두 번째 `ROLLBACK`은 16만 취소합니다(2-2, 2-3).
:::

### 6-11. 복습 5 답 {keep}

:::answer 복습 5 예시 답안
```sql 5 — 잘못 넣은 경우
BEGIN;
UPDATE t_part_master SET uit = 'D' WHERE part_no = 'EMT78269001';
INSERT INTO t_uit_history
VALUES (3, 'EMT78269001', 'G', 'D', 'Procurement', '수입 조달 확인, UIT 정정', CURRENT_DATE, 'Y');
COMMIT;                                     -- 결과: ROLLBACK

SELECT part_no, uit FROM t_part_master WHERE part_no = 'EMT78269001';
SELECT COUNT(*) AS cnt FROM t_uit_history WHERE part_no = 'EMT78269001';
```

```sql 5 — SAVEPOINT로 고친 경우
BEGIN;
UPDATE t_part_master SET uit = 'D' WHERE part_no = 'EMT78269001';
SAVEPOINT before_hist;
INSERT INTO t_uit_history
VALUES (3, 'EMT78269001', 'G', 'D', 'Procurement', '수입 조달 확인, UIT 정정', CURRENT_DATE, 'Y');   -- 오류
ROLLBACK TO SAVEPOINT before_hist;
INSERT INTO t_uit_history
VALUES (7, 'EMT78269001', 'G', 'D', 'Procurement', '수입 조달 확인, UIT 정정', CURRENT_DATE, 'Y');
COMMIT;

SELECT p.part_no, p.uit, h.change_id
  FROM t_part_master p
  JOIN t_uit_history h ON h.part_no = p.part_no
 WHERE p.part_no = 'EMT78269001';
```

- 5번: PK 중복으로 트랜잭션이 중단되어 `COMMIT`이 `ROLLBACK`으로 처리되고 UPDATE까지 취소됩니다(3-2). `SAVEPOINT`를 두면 실패한 INSERT만 되돌릴 수 있습니다(3-6).
:::

### 6-12. 복습 6 · 7 답 {keep}

:::answer 복습 6 · 7 예시 답안
```sql 7 — (나) TRUNCATE
BEGIN;
TRUNCATE t_part_sourcing;
SELECT COUNT(*) FROM t_part_sourcing;       -- 0
ROLLBACK;
SELECT COUNT(*) FROM t_part_sourcing;       -- 52
```

- 6번: 세션 1이 `ROLLBACK`했으므로 세션 2의 +10은 **원래 값 10**에 적용됩니다(5-3).
- 7번: `SELECT`는 데이터를 바꾸지 않으므로 묶을 필요가 없습니다. `TRUNCATE`는 `BEGIN` 없이 실행하면 즉시 확정됩니다(4-2).
:::

:::teacher 강사 확인
- 3번은 README 4장 **A1**(로터: UIT G, Line I)을 바로잡는 작업입니다. 1·2번(스테이터)과 함께, Day 2 품질 진단 리포트에서 찾은 이상을 「한 트랜잭션 + 이력」으로 고치는 흐름으로 정리하세요. 다음 교시(기록 테이블 설계)와 4교시(승인 흐름)에서 이 구조를 결품 경고 기록으로 확장합니다.
- 6번은 두 세션이 필요하므로 짝 활동으로 진행하세요. 끝난 뒤 0-2 스크립트로 초기화하게 합니다.
:::

## 7. 정리

### 7-1. 오늘 배운 것 {keep}

:::summary
- **트랜잭션**: 여러 SQL 문장을 「전부 반영 또는 전부 취소」로 묶는 최소 작업 단위. 특성은 ACID(원자성·일관성·고립성·지속성).
- **자동 커밋**: PostgreSQL(psql·pgAdmin 기본값)은 `BEGIN`이 없으면 문장마다 즉시 확정합니다. ==묶으려면 반드시 `BEGIN`.==
- **COMMIT / ROLLBACK**: `COMMIT`은 영구 반영, `ROLLBACK`은 `BEGIN` 이후 변경 전부 취소. `BEGIN` 없이 `ROLLBACK`하면 `WARNING: there is no transaction in progress` — 이미 확정된 것입니다.
- **중단 상태**: 트랜잭션 안에서 오류가 나면 이후 문장은 거부되고, `COMMIT`해도 `ROLLBACK`으로 처리됩니다. 반쪽 반영이 생기지 않습니다.
- **SAVEPOINT**: `ROLLBACK TO SAVEPOINT 이름`으로 저장 지점 이후만 취소하고 트랜잭션을 이어 갑니다.
- **변경 + 이력 INSERT**: 관련된 변경(직원·부서·이력 / 생산 데이터에서는 UIT·Line Type·이력, Q13)을 모두 한 트랜잭션에 넣어야 「한쪽만 바뀐」 불일치가 생기지 않습니다.
- **TRUNCATE · DROP**: `BEGIN` 안에서는 되돌릴 수 있지만, `BEGIN` 없이 실행하면 즉시 확정. `CREATE DATABASE`처럼 트랜잭션 안에서 실행할 수 없는 명령도 있습니다.
- **읽기 일관성**: 확정 전의 변경은 다른 세션에 보이지 않습니다(기본 격리 수준 Read Committed).
- **LOCK**: 같은 행을 고치려는 다른 세션은 앞 트랜잭션이 끝날 때까지 기다립니다. 행 단위이며 조회는 막지 않습니다. 트랜잭션은 짧게, `idle in transaction`을 남기지 않습니다.
- **변경 유실 방지**: 화면에서 본 값으로 덮어쓰지 말고 `컬럼 = 컬럼 + 값`처럼 SQL 안에서 계산합니다.
:::

### 7-2. 마무리 퀴즈

:::quiz
Q. psql에서 `UPDATE` 후 `ROLLBACK`했더니 `WARNING: there is no transaction in progress`가 나왔습니다. 데이터는 어떤 상태이고, 원인은 무엇인가요?
A. UPDATE가 이미 확정된 상태입니다. `BEGIN` 없이 실행해 자동 커밋되었기 때문에 되돌릴 트랜잭션이 없습니다.

Q. `BEGIN` → `UPDATE`(성공) → `INSERT`(제약조건 위반 오류) → `COMMIT` 순서로 실행하면 UPDATE는 반영되나요?
A. 반영되지 않습니다. 오류로 트랜잭션이 중단되어 `COMMIT`이 `ROLLBACK`으로 처리되고, 성공했던 UPDATE까지 함께 취소됩니다.

Q. 위 상황에서 UPDATE는 살리고 INSERT만 다시 하려면 어떻게 해야 하나요?
A. UPDATE 뒤에 `SAVEPOINT 이름;`을 두고, 오류가 나면 `ROLLBACK TO SAVEPOINT 이름;`으로 돌아가 INSERT를 다시 실행한 뒤 `COMMIT`합니다.

Q. 109번을 Treasury 부서장으로 발령하면서 `t_emp`의 직무·부서와 이력만 바꾸고 `COMMIT`했습니다. 어떤 문제가 남나요?
A. 부서 테이블(`t_dept`)의 Treasury 부서장(`manager_id`)이 비어 있어 직원 테이블과 어긋납니다. 부서장 UPDATE까지 같은 트랜잭션에 넣어야 합니다.

Q. 세션 1이 `BEGIN` 후 어떤 행을 UPDATE하고 그대로 두었습니다. 세션 2에서 같은 행을 SELECT하면? UPDATE하면?
A. SELECT는 바로 실행되고 확정된(변경 전) 값을 보여 줍니다. UPDATE는 세션 1이 `COMMIT` 또는 `ROLLBACK`할 때까지 기다립니다.
:::
