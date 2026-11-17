---
label: 8. DML
title: 데이터를 삽입·수정·삭제
---

# INSERT · UPDATE · DELETE

:::goal
- `CREATE TABLE … AS SELECT`로 연습용 사본을 만들고, 사본에서만 DML을 실행할 수 있습니다.
- `INSERT`로 한 행·여러 행·SELECT 결과를 넣고, 컬럼을 뺐을 때와 자주 나는 오류를 설명할 수 있습니다.
- `UPDATE`·`DELETE`로 조건에 맞는 행만 바꾸거나 지우고, 결과 메시지의 **행 수**와 `RETURNING`으로 결과를 확인할 수 있습니다.
- WHERE 누락·`= NULL`·`UPDATE 0`처럼 오류 없이 일어나는 사고를 알아보고, 안전한 DML 순서를 따를 수 있습니다.
:::

:::teacher 단원 구성 (60분)
- 운영안 Day 4 **1H(DML 기초: INSERT, UPDATE, DELETE, 원본 보호(복사 테이블에서 연습) / `CREATE TABLE ... AS SELECT`로 연습용 사본 만들기 후 DML 실습)** 에 해당합니다. 다음 교시 TCL(2H)이 「1교시에서 INSERT·UPDATE·DELETE를 배운 뒤」를 전제로 하므로, 이 단원에서는 `BEGIN`/`COMMIT`/`ROLLBACK`을 쓰지 않고 **자동 커밋의 위험**만 예고합니다(1-3, 5장).
- 기존 교안 `10. DML.pptx` · `10. DML실습문제.txt` · `10. DML실습문제 답안.txt`의 **순서(INSERT → UPDATE → DELETE)와 실습 유형**(부서·직원 입력, 본인 정보 변경, 금액 충전 `MONEY = MONEY + 10000`, 구매 시 두 테이블 UPDATE, 조건 삭제, 전체 삭제, 있으면 UPDATE·없으면 INSERT)을 따릅니다. **본문 예제는 HR 실습 데이터(`hr`)의 직원·부서**로, 각 장의 **확인 문제와 6장 복습 문제는 BOM 실습 데이터(`bom`)의 입고 예정·재고**로 풉니다. 기존 답안의 `SYSDATE`는 `CURRENT_DATE`로 바꿨습니다.
- 원본을 지키기 위해 **연습용 사본 4개**를 `CREATE TABLE … AS SELECT`로 만들어 실습합니다(0장). 본문용 `hr.t_emp`·`hr.t_dept`, 확인 문제·복습용 `bom.t_inventory`·`bom.t_scheduled_receipt`입니다. 0장의 문장은 `DROP TABLE IF EXISTS`로 시작하므로 같은 이름의 사본이 이미 있어도 그대로 실행되고, 다시 실행하면 처음 상태로 돌아갑니다(0-3). 다음 교시 TCL도 같은 방식으로 사본을 다시 만듭니다.
- 원본 `hr.employees`에는 직책(`job_id`)·부서(`department_id`)가 바뀌면 `job_history`에 한 행을 자동으로 넣는 트리거(`update_job_history`)와, 평일 업무 시간 밖의 변경을 막는 트리거(`secure_employees`)가 있습니다. 원본에 UPDATE 하면 `job_history`가 늘어나 다른 단원의 결과까지 달라지므로, **원본 `employees`는 시연에서도 바꾸지 마세요.** CTAS 사본에는 트리거가 복사되지 않습니다(3-5).
- 다음 교시 TCL은 같은 이름의 HR 사본을 `LIKE … INCLUDING ALL`(PK·CHECK까지 복사)로 다시 만듭니다. 이 단원은 운영안대로 **CTAS**를 쓰는데, 2-6의 「사본에는 같은 번호가 두 번 들어간다」(PK가 복사되지 않음)가 CTAS 사본이어야 재현되기 때문입니다. 두 방법의 차이를 TCL 0장에서 다시 짚어 주세요.
- 교안의 모든 SQL과 실행 결과는 `schema_postgres.sql`·`hr_postgres.sql`로 적재한 DB에서 **위에서부터 순서대로 직접 실행한 결과**입니다. 오류 메시지도 실제 출력입니다. 순서를 바꿔 실행하면 행 수가 달라집니다. (검증 환경: PostgreSQL 18.7, psql, `DateStyle = ISO, YMD`)
- 새로 넣는 직원(207~210번)의 이름·날짜·급여와 입고 예정(7~11번)의 날짜·수량·PO 번호는 **실습용 가정 값**입니다. 데이터셋에 있는 값이 아닙니다.
- 이 단원은 1교시(60분) 분량입니다. 같은 SQL을 순서대로 모은 파일은 `DML.sql`입니다.

| 교시 | 시간 | 내용 | 해당 장 | 기존 교안 대응 |
| --- | --- | --- | --- | --- |
| **Day 4 1교시** | 0~5분 | 연습용 사본 만들기(CTAS) | 0 | — |
| | 5~10분 | DML · 결과 메시지 · 자동 커밋 | 1 | `10. DML.pptx` 3~4 |
| | 10~25분 | INSERT · 컬럼 생략 · 여러 행 · 자주 나는 오류 | 2 | `10. DML.pptx` 5~8, 실습문제 1번 |
| | 25~40분 | UPDATE · 계산식 · WHERE 빠뜨림 · 서브쿼리로 최저 급여 적용 | 3 | `10. DML.pptx` 9~10, 실습문제 2·4·5번 |
| | 40~52분 | DELETE · NULL 조건 · 전체 삭제와 복구(INSERT … SELECT) | 4 | `10. DML.pptx` 11, 실습문제 3·7·8번 |
| | 52~60분 | 안전하게 DML 하는 순서 · 복습 문제 안내 | 5~6 | 실습문제 6번 |
:::

## 0. 실습 준비 — 연습용 사본 만들기

### 0-1. 본문용 사본 — HR {keep}

오늘은 데이터를 **넣고, 바꾸고, 지웁니다.** 원본은 4일 내내 쓰는 자료이므로, 원본과 똑같은 데이터를 가진 **사본**을 만들어 연습합니다. 본문 예제는 HR 데이터의 직원·부서 사본으로 실행합니다.

```sql
SET search_path TO hr;

DROP TABLE IF EXISTS t_emp, t_dept;
CREATE TABLE t_emp  AS SELECT * FROM employees;
CREATE TABLE t_dept AS SELECT * FROM departments;
```

```result
DROP TABLE
SELECT 107
SELECT 27
```

- `DROP TABLE IF EXISTS` — 같은 이름의 사본이 **이미 있으면 지웁니다.** 처음 실행할 때는 `NOTICE: table "t_emp" does not exist, skipping`(없어서 건너뜀)이 함께 나옵니다. 오류가 아닙니다.
- 결과의 `SELECT 107`은 「107행을 복사했다」는 뜻입니다.

### 0-1. 확인 문제·복습용 사본 — 생산 {keep}

확인 문제와 복습 문제는 생산 데이터의 **재고**와 **입고 예정** 사본으로 풉니다. 지금 함께 만들어 둡니다.

```sql
SET search_path TO bom;

DROP TABLE IF EXISTS t_inventory, t_scheduled_receipt;
CREATE TABLE t_inventory         AS SELECT * FROM inventory;
CREATE TABLE t_scheduled_receipt AS SELECT * FROM scheduled_receipt;

SET search_path TO hr;      -- 본문은 다시 HR로
```

```result
DROP TABLE
SELECT 53
SELECT 6
```

> 마지막 줄의 `SET search_path TO hr;`을 빠뜨리면 뒤의 본문 쿼리가 `t_emp`를 찾지 못합니다.

### 0-2. 사본 행 수 확인 {keep}

```sql
SELECT 't_emp' AS tbl, COUNT(*) FROM t_emp
UNION ALL SELECT 't_dept',                  COUNT(*) FROM t_dept
UNION ALL SELECT 'bom.t_inventory',         COUNT(*) FROM bom.t_inventory
UNION ALL SELECT 'bom.t_scheduled_receipt', COUNT(*) FROM bom.t_scheduled_receipt;
```

```result
| tbl | count |
| --- | --- |
| t_emp | 107 |
| t_dept | 27 |
| bom.t_inventory | 53 |
| bom.t_scheduled_receipt | 6 |
```

- `CREATE TABLE 새테이블 AS SELECT …` — **SELECT 결과를 그대로 새 테이블로** 만듭니다(줄여서 CTAS).
- 사본 이름 앞의 `t_`는 「연습용(test)」 표시입니다. ==오늘 DML은 모두 `t_`로 시작하는 테이블에만== 실행합니다.
- 지금은 `hr` 상태라 생산 사본은 `bom.`을 붙여 셌습니다(2단원 6-4의 `스키마.테이블`).

### 0-3. 처음 상태로 되돌리기 {keep}

실습 중 데이터가 꼬이면 아래 **되돌리기**를 실행합니다. 스키마 이름을 붙여 썼으므로 지금 `hr`·`bom` 어느 쪽에 있든 그대로 실행됩니다. 0-1의 두 블록을 다시 실행해도 같습니다.

```sql
-- 되돌리기: 사본 4개를 원본과 같은 처음 상태로
DROP TABLE IF EXISTS hr.t_emp, hr.t_dept, bom.t_inventory, bom.t_scheduled_receipt;
CREATE TABLE hr.t_emp                AS SELECT * FROM hr.employees;
CREATE TABLE hr.t_dept               AS SELECT * FROM hr.departments;
CREATE TABLE bom.t_inventory         AS SELECT * FROM bom.inventory;
CREATE TABLE bom.t_scheduled_receipt AS SELECT * FROM bom.scheduled_receipt;
```

되돌린 뒤에는 `SET search_path TO hr;`을 실행하고 **2장부터 순서대로**(확인 문제 포함) 다시 실행해야 뒤의 결과가 교재와 같아집니다.

> CTAS 사본은 **컬럼·자료형·데이터만** 복사하고, PK 같은 「규칙(제약조건)」은 복사하지 않습니다. 이 차이가 2-6에서 보입니다. 테이블을 만드는 문법(`CREATE TABLE`)과 규칙은 DDL 단원에서 자세히 다룹니다.

## 1. DML — 테이블 안의 데이터를 바꾸는 SQL

### 1-1. SQL 문장의 종류 {keep}

| 분류 | 이름 | 하는 일 | 대표 명령 |
| --- | --- | --- | --- |
| QUERY | 질의어 | 데이터 조회 | `SELECT` |
| **DML** | **데이터 조작어** (Data Manipulation Language) | **테이블에 행을 넣고·바꾸고·지움** | **`INSERT`, `UPDATE`, `DELETE`** |
| TCL | 트랜잭션 제어어 | DML 결과를 확정하거나 취소 | `BEGIN`, `COMMIT`, `ROLLBACK` |
| DDL | 데이터 정의어 | 테이블 구조를 만들고 바꿈 | `CREATE`, `ALTER`, `DROP` |
| DCL | 데이터 제어어 | 권한을 주고 회수 | `GRANT`, `REVOKE` |

### 1-1. 이번 단원에서 배우는 DML {keep}

```icons DML 명령어
plus | INSERT | 새 행을 넣음 — 단위: 행 (2장) | rose
pencil | UPDATE | 이미 있는 행의 값을 바꿈 — 단위: 컬럼 값 (3장) | plum
trash-2 | DELETE | 행을 지움 — 단위: 행 (4장) | hot
```

Day 1~3의 `SELECT`는 데이터를 **읽기만** 했습니다. DML은 데이터를 **바꿉니다.** Day 4의 「판단 결과를 DB에 기록」하는 일이 바로 DML입니다.

### 1-2. 결과 메시지 읽기 {keep}

DML을 실행하면 표 대신 **몇 행이 바뀌었는지**가 나옵니다.

| 메시지 | 뜻 |
| --- | --- |
| `INSERT 0 1` | 1행을 넣음 (가운데 `0`은 신경 쓰지 않아도 됩니다) |
| `INSERT 0 27` | 27행을 넣음 |
| `UPDATE 1` | 1행을 바꿈 |
| `UPDATE 0` | **바뀐 행 없음** — 조건에 맞는 행이 없음 (오류 아님) |
| `DELETE 27` | 27행을 지움 |

==DML을 실행하면 숫자부터 확인==하세요. 1행만 바꾸려 했는데 `UPDATE 27`이 나왔다면 사고입니다(3-4).

### 1-3. 실행하는 즉시 확정됩니다 — 자동 커밋 {keep}

:::error DML은 「저장」 버튼이 따로 없습니다
PostgreSQL(psql·pgAdmin 기본 설정)은 **문장 하나를 실행할 때마다 그 자리에서 확정**합니다. 이것을 **자동 커밋**이라고 합니다. 엑셀처럼 「저장 안 하고 닫기」가 없습니다. 잘못 지운 행은 **되돌리기 버튼이 없습니다.**

그래서 오늘은 ① **사본에서만** 연습하고 ② **실행 전에 같은 조건으로 SELECT** 해 보는 습관(5장)을 들입니다. 여러 문장을 묶어 한꺼번에 확정하거나 취소하는 방법(`BEGIN`, `COMMIT`, `ROLLBACK`)은 다음 교시(TCL)에서 배웁니다.
:::

## 2. INSERT — 새 행 넣기

### 2-1. INSERT의 모양 {keep}

```text INSERT의 모양
INSERT INTO 테이블 (컬럼1, 컬럼2, …)      ← 값을 넣을 컬럼 목록
VALUES (값1, 값2, …);                      ← 컬럼 목록과 같은 순서·같은 개수
```

- 문자·날짜 값은 **작은따옴표** `'…'`, 숫자는 따옴표 없이 씁니다(3단원 1-3).
- 날짜는 `'2026-12-01'`처럼 **연-월-일** 문자로 씁니다.

### 2-1. 지금의 직원 — 사번 206번까지 {keep}

> 실행 전: `SET search_path TO hr;` — 이 단원의 본문 예제는 HR 실습 데이터(`hr` 스키마)의 사본으로 실행합니다(0-1).

```sql
SELECT employee_id, first_name, last_name, hire_date, job_id, salary, department_id
  FROM t_emp
 WHERE employee_id >= 200
 ORDER BY employee_id;
```

```result
| employee_id | first_name | last_name | hire_date | job_id | salary | department_id |
| --- | --- | --- | --- | --- | --- | --- |
| 200 | Jennifer | Whalen | 2003-09-17 | AD_ASST | 4400.00 | 10 |
| 201 | Michael | Hartstein | 2004-02-17 | MK_MAN | 13000.00 | 20 |
| 202 | Pat | Fay | 2005-08-17 | MK_REP | 6000.00 | 20 |
| 203 | Susan | Mavris | 2002-06-07 | HR_REP | 6500.00 | 40 |
| 204 | Hermann | Baer | 2002-06-07 | PR_REP | 10000.00 | 70 |
| 205 | Shelley | Higgins | 2002-06-07 | AC_MGR | 12008.00 | 110 |
| 206 | William | Gietz | 2002-06-07 | AC_ACCOUNT | 8300.00 | 110 |
```

### 2-2. 한 행 넣기 — 신입 사원 207번 {keep}

IT 부서(60)에 프로그래머 한 명이 **12월 1일에 입사**한다고 가정하고, 직원을 한 행 넣습니다. 사번은 마지막 번호 다음인 207입니다.

```sql
INSERT INTO t_emp
       (employee_id, first_name, last_name, email, phone_number, hire_date,
        job_id, salary, commission_pct, manager_id, department_id)
VALUES (207, 'Gildong', 'Hong', 'GHONG', '010-1234-5678', '2026-12-01',
        'IT_PROG', 4800, NULL, 103, 60);
```

```result
INSERT 0 1
```

### 2-2. 넣은 행 확인 {keep}

```sql
SELECT employee_id, first_name, last_name, hire_date, job_id, salary, manager_id
  FROM t_emp
 WHERE department_id = 60
 ORDER BY employee_id;
```

```result
| employee_id | first_name | last_name | hire_date | job_id | salary | manager_id |
| --- | --- | --- | --- | --- | --- | --- |
| 103 | Alexander | Hunold | 2006-01-03 | IT_PROG | 9000.00 | 102 |
| 104 | Bruce | Ernst | 2007-05-21 | IT_PROG | 6000.00 | 103 |
| 105 | David | Austin | 2005-06-25 | IT_PROG | 4800.00 | 103 |
| 106 | Valli | Pataballa | 2006-02-05 | IT_PROG | 4800.00 | 103 |
| 107 | Diana | Lorentz | 2007-02-07 | IT_PROG | 4200.00 | 103 |
| 207 | Gildong | Hong | 2026-12-01 | IT_PROG | 4800.00 | 103 |
```

IT 부서가 6명이 되었습니다. 커미션(`commission_pct`)은 영업 직원 35명만 받으므로(4단원 1-3) 값 자리에 **`NULL`을 직접** 썼습니다. 값이 없다는 것을 이렇게 분명히 적을 수 있습니다.

### 2-3. 컬럼을 빼면 — NULL이 들어갑니다 {keep}

컬럼 목록에서 뺀 컬럼에는 **NULL**이 들어갑니다. (기본값이 정해진 컬럼이면 기본값. 기본값은 DDL 단원에서 다룹니다.) 이번에는 이름·이메일·입사일·직책만 넣습니다.

```sql
INSERT INTO t_emp (employee_id, first_name, last_name, email, hire_date, job_id)
VALUES (208, 'Minji', 'Kim', 'MKIM', CURRENT_DATE, 'IT_PROG');

SELECT employee_id, first_name, last_name, phone_number, salary, manager_id, department_id
  FROM t_emp
 WHERE employee_id = 208;
```

```result INSERT 0 1
| employee_id | first_name | last_name | phone_number | salary | manager_id | department_id |
| --- | --- | --- | --- | --- | --- | --- |
| 208 | Minji | Kim | NULL | NULL | NULL | NULL |
```

**전화번호도, 급여도, 매니저도, 부서도 없는** 직원이 만들어졌습니다. 오류는 나지 않았습니다. Day 1 7교시에 「무엇이 비어 있는가」로 찾던 빈 칸이 **바로 이렇게 생깁니다.** 이 행은 4-3에서 찾아 지웁니다.

> `CURRENT_DATE`는 「오늘 날짜」입니다. 입사일에는 **실행한 날짜**가 들어가므로, 날마다 달라지는 `hire_date`는 위 결과에서 뺐습니다.

### 2-4. 여러 행을 한 번에 {keep}

`VALUES` 뒤에 괄호를 쉼표로 이어 쓰면 여러 행을 한 문장으로 넣습니다. 배송 부서(50)에 재고 담당(`ST_CLERK`) 두 명이 함께 입사합니다.

```sql
INSERT INTO t_emp
       (employee_id, first_name, last_name, email, hire_date,
        job_id, salary, manager_id, department_id)
VALUES (209, 'Jiho',    'Lee',  'JLEE',  '2026-12-01', 'ST_CLERK', 2500, 124, 50),
       (210, 'Seoyeon', 'Choi', 'SCHOI', '2026-12-01', 'ST_CLERK', 2400, 124, 50);
```

```result
INSERT 0 2
```

### 2-5. INSERT에서 자주 나는 오류 ① 컬럼 순서 {keep}

:::error 컬럼 목록을 생략했는데 순서가 틀림
컬럼 목록을 생략하면 **테이블의 컬럼 순서대로** 값이 들어갑니다. `t_emp`의 순서는 `…, phone_number, hire_date, job_id, …`인데 직책과 입사일을 바꿔 썼습니다.

```sql
INSERT INTO t_emp
VALUES (211, 'Minsu', 'Kang', 'MKANG', '010-2222-3333',
        'IT_PROG', '2026-12-01', 4800, NULL, 103, 60);
```

```error
ERROR:  invalid input syntax for type date: "IT_PROG"
LINE 3:         'IT_PROG', '2026-12-01', 4800, NULL, 103, 60);
                ^
```

`'IT_PROG'`가 날짜 칸(`hire_date`)에 들어가려다 거부되었습니다. 이번에는 자료형 덕분에 막혔지만, `first_name`과 `last_name`처럼 **자료형이 같은 컬럼끼리 순서가 바뀌면 오류 없이 엉뚱한 칸에 들어갑니다.** ==컬럼 목록은 생략하지 말고 항상 적으세요.==
:::

### 2-5. INSERT에서 자주 나는 오류 ② 컬럼 수와 값 수 {keep}

:::error 컬럼 수와 값 수가 다름
```sql
INSERT INTO t_emp (employee_id, first_name, last_name)
VALUES (211, 'Minsu', 'Kang', 'MKANG');
```

```error
ERROR:  INSERT has more expressions than target columns
LINE 2: VALUES (211, 'Minsu', 'Kang', 'MKANG');
                                      ^
```

컬럼은 3개인데 값이 4개입니다. `^` 표시가 남는 값(`'MKANG'`)을 가리킵니다.
:::

### 2-5. INSERT에서 자주 나는 오류 ③ 자료형 — 길이 · 날짜 {keep}

:::error 자료형에 맞지 않는 값
```sql
INSERT INTO t_emp (employee_id, last_name, hire_date, job_id)
VALUES (211, 'Kang', '2026-12-01', 'IT_PROGRAMMER');
```

```error
ERROR:  value too long for type character varying(10)
```

```sql
INSERT INTO t_emp (employee_id, last_name, hire_date, job_id)
VALUES (211, 'Kang', '2026-12-32', 'IT_PROG');
```

```error
ERROR:  date/time field value out of range: "2026-12-32"
LINE 2: VALUES (211, 'Kang', '2026-12-32', 'IT_PROG');
                             ^
HINT:  Perhaps you need a different "DateStyle" setting.
```
:::

### 2-5. INSERT에서 자주 나는 오류 ③ 자료형 — 숫자 {keep}

:::error 자료형에 맞지 않는 값
```sql
INSERT INTO t_emp (employee_id, last_name, hire_date, salary)
VALUES (211, 'Kang', '2026-12-01', '사천팔백');
```

```error
ERROR:  invalid input syntax for type numeric: "사천팔백"
LINE 2: VALUES (211, 'Kang', '2026-12-01', '사천팔백');
                                           ^
```

10자를 넘는 직책 ID(`job_id`는 10자까지), 존재하지 않는 날짜(12월 32일), 숫자가 아닌 급여는 **자료형** 단계에서 막힙니다. 오류가 난 문장은 **한 행도 들어가지 않습니다.**
:::

### 2-6. 사본에는 「같은 번호」가 두 번 들어갑니다 {keep}

이미 있는 207번으로 한 행을 더 넣어 봅니다.

```sql
INSERT INTO t_emp (employee_id, first_name, last_name, email, hire_date, job_id)
VALUES (207, 'Minsu', 'Kang', 'MKANG', '2026-12-01', 'IT_PROG');

SELECT employee_id, COUNT(*) AS cnt FROM t_emp GROUP BY employee_id HAVING COUNT(*) > 1;
```

```result INSERT 0 1
| employee_id | cnt |
| --- | --- |
| 207 | 2 |
```

**207번이 두 명**이 되었습니다. 원본 `employees`의 `employee_id`는 **PK**라서 같은 번호를 막지만, CTAS 사본에는 PK가 복사되지 않았기 때문입니다(0장).

### 2-6. 잘못 넣은 행 지우기 {keep}

잘못 넣은 행은 지워 둡니다(DELETE는 4장). `employee_id = 207`만 쓰면 2-2에서 넣은 207번까지 지워지므로, 성(`last_name`) 조건을 하나 더 붙였습니다.

```sql
DELETE FROM t_emp WHERE employee_id = 207 AND last_name = 'Kang';
```

```result
DELETE 1
```

> 「잘못된 값을 DB가 막아 주느냐」는 **테이블을 만들 때 정한 규칙(제약조건)** 에 달려 있습니다. DML은 규칙이 허락하는 것은 무엇이든 넣습니다. 규칙을 만드는 방법은 DDL 단원에서 배웁니다.

> 이 DELETE를 건너뛰면 뒤(3-2, 3-3)의 행 수가 달라집니다. `DELETE 1`을 꼭 확인하세요.

:::teacher 강사 확인
- 원본에서는 실제로 막히는지 강사 시연으로만 보여 주세요. 원본 `employees`에는 평일 업무 시간 밖의 변경을 막는 트리거(`secure_employees`)가 걸려 있을 수 있어 결과가 시각에 따라 달라지므로, 트리거가 없는 **원본 `departments`** 로 보여 줍니다. 이미 있는 60번(IT)을 한 번 더 넣으면 PK가 막습니다. 오류로 끝나므로 원본이 바뀌지 않습니다.

```sql
INSERT INTO departments (department_id, department_name)
VALUES (60, 'IT');
```

```error
ERROR:  duplicate key value violates unique constraint "dept_id_pk"
DETAIL:  Key (department_id)=(60) already exists.
```

- 훈련생에게는 원본(`t_`가 없는 테이블)에 DML을 실행하지 않도록 한 번 더 강조하세요. 원본에 성공한 INSERT는 자동 커밋으로 즉시 확정됩니다.
:::

### 2-7. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (0-1에서 만든 생산 사본 `t_scheduled_receipt` 사용)

:::try
**[복습]** Day 3에서 컴프레서(`ECP39799101`)는 **12/4에 결품**이 예상되었고, 첫 입고(12/8)로는 늦었습니다(README **A7**). 구매 담당이 협력사에 추가 발주한 아래 입고 예정을 `t_scheduled_receipt`에 넣고, 컴프레서의 입고 예정을 도착일 순으로 조회하세요.

| receipt_id | site_code | part_no | vendor_code | eta_date | qty | po_no | receipt_type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | CW | ECP39799101 | V1004 | 2026-12-03 | 400 | PO26-1107 | Planned |

**[응용]** 아래 세 건을 넣으세요. 8번은 업체·PO 번호·입고 구분이 아직 없으므로 **그 세 컬럼을 빼고** 넣고, 9·10번은 **한 문장으로** 넣습니다. 넣은 뒤 `receipt_id`가 7 이상인 행을 번호 순으로 조회합니다.

| receipt_id | site_code | part_no | vendor_code | eta_date | qty | po_no | receipt_type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | CW | MGL96663301 | | 2026-12-09 | 500 | | |
| 9 | CW | RSS86949501 | V1007 | 2026-12-16 | 300 | PO26-1108 | Planned |
| 10 | CW | EIC93178801 | V1005 | 2026-12-17 | 3000 | PO26-1109 | Planned |
:::

### 2-7. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
```sql
INSERT INTO t_scheduled_receipt
       (receipt_id, site_code, part_no, vendor_code, eta_date, qty, po_no, receipt_type)
VALUES (7, 'CW', 'ECP39799101', 'V1004', '2026-12-03', 400, 'PO26-1107', 'Planned');

SELECT receipt_id, part_no, eta_date, qty, po_no, receipt_type
  FROM t_scheduled_receipt
 WHERE part_no = 'ECP39799101'
 ORDER BY eta_date;
```

```result INSERT 0 1
| receipt_id | part_no | eta_date | qty | po_no | receipt_type |
| --- | --- | --- | --- | --- | --- |
| 7 | ECP39799101 | 2026-12-03 | 400.00 | PO26-1107 | Planned |
| 1 | ECP39799101 | 2026-12-08 | 800.00 | PO26-1101 | Scheduled |
| 2 | ECP39799101 | 2026-12-15 | 1600.00 | PO26-1102 | Planned |
```

`receipt_type`은 README 1장(자재 Capa 제약)의 구분입니다. `Scheduled`는 발주가 나간 **확정 입고**, `Planned`는 **계획 입고**입니다. 7번은 아직 협력사 확정 전이라 `Planned`입니다.
:::

### 2-7. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
```sql
INSERT INTO t_scheduled_receipt (receipt_id, site_code, part_no, eta_date, qty)
VALUES (8, 'CW', 'MGL96663301', '2026-12-09', 500);

INSERT INTO t_scheduled_receipt
       (receipt_id, site_code, part_no, vendor_code, eta_date, qty, po_no, receipt_type)
VALUES (9,  'CW', 'RSS86949501', 'V1007', '2026-12-16',  300, 'PO26-1108', 'Planned'),
       (10, 'CW', 'EIC93178801', 'V1005', '2026-12-17', 3000, 'PO26-1109', 'Planned');

SELECT receipt_id, part_no, vendor_code, eta_date, qty, po_no, receipt_type
  FROM t_scheduled_receipt
 WHERE receipt_id >= 7
 ORDER BY receipt_id;
```

```result INSERT 0 1 → INSERT 0 2
| receipt_id | part_no | vendor_code | eta_date | qty | po_no | receipt_type |
| --- | --- | --- | --- | --- | --- | --- |
| 7 | ECP39799101 | V1004 | 2026-12-03 | 400.00 | PO26-1107 | Planned |
| 8 | MGL96663301 | NULL | 2026-12-09 | 500.00 | NULL | NULL |
| 9 | RSS86949501 | V1007 | 2026-12-16 | 300.00 | PO26-1108 | Planned |
| 10 | EIC93178801 | V1005 | 2026-12-17 | 3000.00 | PO26-1109 | Planned |
```

8번은 업체·PO 번호·입고 구분이 NULL입니다(2-3). 이 행은 4-5에서 찾아 지웁니다.
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 3. UPDATE — 이미 있는 값 바꾸기

### 3-1. UPDATE의 모양 {keep}

```text UPDATE의 모양
UPDATE 테이블
   SET 컬럼1 = 새값1
     , 컬럼2 = 새값2          ← 여러 컬럼은 쉼표로
 WHERE 바꿀 행의 조건;          ← 빠뜨리면 모든 행이 바뀜 (3-4)
```

`WHERE`는 3단원에서 배운 조건과 똑같습니다. ==UPDATE는 「어떤 행을(WHERE) 어떻게(SET)」 두 가지를 정하는 문장==입니다.

### 3-2. 입사일 미루기 — 바꾸기 전 확인 {keep}

2-2에서 넣은 207번의 입사일이 **12/1 → 12/15**로 미뤄졌다고 가정합니다. 바꾸기 전에 대상 행을 먼저 확인합니다.

```sql
SELECT employee_id, first_name, last_name, hire_date, job_id, salary
  FROM t_emp
 WHERE employee_id = 207;
```

```result
| employee_id | first_name | last_name | hire_date | job_id | salary |
| --- | --- | --- | --- | --- | --- |
| 207 | Gildong | Hong | 2026-12-01 | IT_PROG | 4800.00 |
```

### 3-2. 입사일 미루기 — UPDATE {keep}

```sql
UPDATE t_emp
   SET hire_date = '2026-12-15'
 WHERE employee_id = 207;

SELECT employee_id, first_name, last_name, hire_date, job_id, salary
  FROM t_emp
 WHERE employee_id = 207;
```

```result UPDATE 1
| employee_id | first_name | last_name | hire_date | job_id | salary |
| --- | --- | --- | --- | --- | --- |
| 207 | Gildong | Hong | 2026-12-15 | IT_PROG | 4800.00 |
```

`UPDATE 1` — 1행이 바뀌었고, 다른 컬럼(`job_id`, `salary`)은 그대로입니다.

### 3-3. 여러 컬럼 · 계산식 · RETURNING {keep}

입사 조건을 다시 협의해 207번의 급여를 **500 올리고**, 신입 교육을 맡을 매니저를 103번에서 **104번(Bruce Ernst)** 으로 바꿨다고 가정합니다. 급여는 **지금 값에 500을 더합니다.**

```sql
UPDATE t_emp
   SET salary     = salary + 500
     , manager_id = 104
 WHERE employee_id = 207
RETURNING employee_id, first_name, hire_date, salary, manager_id;
```

```result UPDATE 1
| employee_id | first_name | hire_date | salary | manager_id |
| --- | --- | --- | --- | --- |
| 207 | Gildong | 2026-12-15 | 5300.00 | 104 |
```

### 3-3. 계산식과 RETURNING 읽기 {keep}

- `salary = salary + 500` — 오른쪽 `salary`는 **바꾸기 전의 값(4800)** 입니다.
- **`RETURNING 컬럼, …`** — 바뀐 행을 **바로 보여 줍니다.** 3-2처럼 UPDATE 후 SELECT를 따로 하지 않아도 됩니다. INSERT·DELETE에도 쓸 수 있습니다(4장).

> 화면에서 본 값으로 계산해 `SET salary = 5300`이라고 쓰지 말고, `salary = salary + 500`처럼 **SQL 안에서 계산**하세요. 여러 사람이 동시에 같은 행을 고칠 때 왜 이 방법이 안전한지는 다음 교시(TCL 5장)에서 확인합니다.

### 3-3. 조건에 맞는 행이 없으면 · 자료형이 틀리면 {keep}

```sql
UPDATE t_emp
   SET salary = salary + 500
 WHERE employee_id = 2070;
```

```result
UPDATE 0
```

207을 2070으로 잘못 썼습니다. **오류가 아니라 `UPDATE 0`** 입니다. 화면에 빨간 글씨가 없으니 「바뀌었겠지」 하고 넘어가기 쉽습니다. ==숫자가 0인지 꼭 확인==하세요(서브쿼리 단원 1-4의 「결과 0행」과 같은 함정).

**자료형에 맞지 않는 값** — INSERT와 똑같이 막힙니다.

```sql
UPDATE t_emp
   SET salary = '많이'
 WHERE employee_id = 207;
```

```error
ERROR:  invalid input syntax for type numeric: "많이"
LINE 2:    SET salary = '많이'
                        ^
```

### 3-4. WHERE를 빠뜨리면 ⭐ {keep}

부서 27개는 위치(`location_id`) 7곳에 나뉘어 있습니다. 시애틀(1700)에 21개, 나머지 6곳에 1개씩입니다.

:::cols
```sql
SELECT location_id, COUNT(*) AS cnt
  FROM t_dept
 GROUP BY location_id
 ORDER BY location_id;
```

```result
| location_id | cnt |
| --- | --- |
| 1400 | 1 |
| 1500 | 1 |
| 1700 | 21 |
| 1800 | 1 |
| 2400 | 1 |
| 2500 | 1 |
| 2700 | 1 |
```
:::

:::error 모든 행이 바뀝니다
런던(2400)의 인사부(40) 한 부서를 시애틀(1700)로 옮기려다 `WHERE`를 빠뜨렸습니다.

```sql
UPDATE t_dept
   SET location_id = 1700;
```

```result
UPDATE 27
```
:::

### 3-4. 27개 부서가 모두 시애틀이 되었습니다 {keep}

:::error 오류도 경고도 없습니다
```sql
SELECT location_id, COUNT(*) AS cnt FROM t_dept GROUP BY location_id ORDER BY location_id;
```

```result
| location_id | cnt |
| --- | --- |
| 1700 | 27 |
```

**27개 부서 모두 시애틀**이 되었습니다. 오류도 경고도 없습니다. 런던의 인사부, 토론토(1800)의 마케팅부, 옥스퍼드(2500)의 영업부가 이제 모두 시애틀에 있습니다. 이 상태로 직원 → 부서 → 위치를 이어 근무 도시를 구하면(5단원 2-5) 부서가 있는 직원은 **모두 Seattle**로 나옵니다.
:::

### 3-4. 사본이니까 복구할 수 있습니다 {keep}

원본의 값을 다시 가져옵니다. 서브쿼리 단원 4장의 **스칼라 서브쿼리**를 `SET`에 쓴 모양입니다.

```sql
UPDATE t_dept t
   SET location_id = (SELECT d.location_id
                        FROM departments d
                       WHERE d.department_id = t.department_id);

SELECT location_id, COUNT(*) AS cnt FROM t_dept GROUP BY location_id ORDER BY location_id;
```

```result UPDATE 27
| location_id | cnt |
| --- | --- |
| 1400 | 1 |
| 1500 | 1 |
| 1700 | 21 |
| 1800 | 1 |
| 2400 | 1 |
| 2500 | 1 |
| 2700 | 1 |
```

### 3-4. 복구 쿼리 읽기 {keep}

- 「사본 한 행(t)마다, 같은 부서 번호의 **원본 위치**를 가져와 넣는다」로 읽습니다. 원본의 PK가 `department_id`라서 부서 번호만 맞추면 정확히 1행이 됩니다.
- 이 복구가 가능했던 것은 **원본이 따로 있었기 때문**입니다. 원본에서 같은 실수를 했다면 되돌릴 곳이 없습니다. 이것이 0장에서 사본을 만든 이유입니다.

### 3-5. 다른 테이블의 값으로 바꾸기 — 승진과 최저 급여 {keep}

재고 담당(`ST_CLERK`)인 141번 Trenna Rajs가 **재고 관리자(`ST_MAN`)로 승진**했습니다. 급여는 새 직책의 **최저 급여**로 올립니다. 먼저 직책 테이블과 직원을 확인합니다.

```sql
SELECT job_id, job_title, min_salary, max_salary
  FROM jobs
 WHERE job_id IN ('ST_CLERK', 'ST_MAN')
 ORDER BY job_id;
SELECT employee_id, first_name, last_name, job_id, salary
  FROM t_emp
 WHERE employee_id = 141;
```

:::cols
```result
| job_id | job_title | min_salary | max_salary |
| --- | --- | --- | --- |
| ST_CLERK | Stock Clerk | 2008 | 5000 |
| ST_MAN | Stock Manager | 5500 | 8500 |
```

```result
| employee_id | first_name | last_name | job_id | salary |
| --- | --- | --- | --- | --- |
| 141 | Trenna | Rajs | ST_CLERK | 3500.00 |
```
:::

### 3-5. 최저 급여는 직책 테이블에서 {keep}

급여를 숫자로 적어 넣는 대신, **직책 테이블(`jobs`)에서 가져옵니다.**

```sql
UPDATE t_emp
   SET job_id = 'ST_MAN'
     , salary = (SELECT min_salary
                   FROM jobs
                  WHERE job_id = 'ST_MAN')
 WHERE employee_id = 141
RETURNING employee_id, first_name, job_id, salary;
```

```result UPDATE 1
| employee_id | first_name | job_id | salary |
| --- | --- | --- | --- |
| 141 | Trenna | ST_MAN | 5500.00 |
```

3,500 → **5,500**. 그런데 일이 끝난 것이 아닙니다. HR 원본은 직책이 바뀌면 **이전 직책을 `job_history`에 한 행으로 남깁니다.** 122번 Payam Kaufling의 `ST_CLERK` 기록(2007년)이 그렇게 남은 행입니다. 이렇게 **한 업무가 두 테이블을 바꾸는** 경우가 있습니다.

:::teacher 강사 확인
- 「직책 UPDATE는 성공했는데 `job_history` INSERT를 잊거나 실패하면?」 → 141번이 언제까지 재고 담당이었는지 기록이 사라집니다. 반대로 이력만 들어가고 UPDATE가 실패해도 기록과 실제가 어긋납니다. 이 질문을 던져 두고 다음 교시(TCL)의 「두 문장을 한 묶음으로」로 연결하세요.
- 원본 `employees`에는 이 INSERT를 자동으로 해 주는 트리거(`update_job_history`)가 있습니다. CTAS 사본 `t_emp`에는 트리거가 복사되지 않으므로 오늘은 기록이 생기지 않습니다. 원본에 UPDATE 하면 `job_history`에 행이 쌓여 다른 단원의 결과(직무 이력 10행)가 달라지니 원본으로 시연하지 마세요.
:::

### 3-6. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (2-7에서 넣은 7번이 있어야 합니다.)

:::try
**[복습]** 협력사 V1004가 컴프레서 1번 입고를 **12/8 → 12/5**로 당겨 주기로 했고, 2-7에서 넣은 7번 긴급 발주는 **200개 늘려 확정(`Scheduled`)** 했습니다. 두 행을 바꾸고 각각 `RETURNING`으로 확인하세요. 7번의 수량은 **지금 값에 200을 더하는** 식으로 씁니다.

**[응용]** 12/4에 메인 PCB 조립체(`EBA56264701`)의 입고 예정 6번이 들어왔습니다. `t_inventory`의 창원(`CW`) 재고에 6번의 수량을 더하고 `RETURNING`으로 확인하세요. 수량은 숫자로 적지 말고 `t_scheduled_receipt`에서 서브쿼리로 가져옵니다.
:::

### 3-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
```sql
UPDATE t_scheduled_receipt
   SET eta_date = '2026-12-05'
 WHERE receipt_id = 1
RETURNING receipt_id, part_no, eta_date, qty, receipt_type;
```

```result UPDATE 1
| receipt_id | part_no | eta_date | qty | receipt_type |
| --- | --- | --- | --- | --- |
| 1 | ECP39799101 | 2026-12-05 | 800.00 | Scheduled |
```

```sql
UPDATE t_scheduled_receipt
   SET qty          = qty + 200
     , receipt_type = 'Scheduled'
 WHERE receipt_id = 7
RETURNING receipt_id, part_no, eta_date, qty, receipt_type;
```

```result UPDATE 1
| receipt_id | part_no | eta_date | qty | receipt_type |
| --- | --- | --- | --- | --- |
| 7 | ECP39799101 | 2026-12-03 | 600.00 | Scheduled |
```

`qty + 200`의 `qty`는 바꾸기 전 값(400)입니다(3-3).
:::

### 3-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
5,970 + 2,000 = **7,970**

```sql
UPDATE t_inventory
   SET on_hand_qty = on_hand_qty + (SELECT qty
                                      FROM t_scheduled_receipt
                                     WHERE receipt_id = 6)
 WHERE site_code = 'CW'
   AND part_no   = 'EBA56264701'
RETURNING site_code, part_no, on_hand_qty;
```

```result UPDATE 1
| site_code | part_no | on_hand_qty |
| --- | --- | --- |
| CW | EBA56264701 | 7970.00 |
```

입고가 끝났으니 6번 입고 예정은 지워야 합니다(4-5). 재고 UPDATE와 입고 예정 DELETE 중 하나만 하면 같은 2,000개가 재고와 입고 예정에 **두 번 잡혀** Day 3 결품 계산이 틀어집니다. 3-5의 「직책 + 이력」과 같은 구조입니다.
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 4. DELETE — 행 지우기

### 4-1. DELETE의 모양 {keep}

```text DELETE의 모양
DELETE FROM 테이블
 WHERE 지울 행의 조건;          ← 빠뜨리면 모든 행이 지워짐 (4-4)
```

DELETE는 **행 단위**로 지웁니다. 한 행의 일부 컬럼만 비우려면 DELETE가 아니라 `UPDATE … SET 컬럼 = NULL`입니다.

### 4-2. 입사가 취소된 직원 지우기 {keep}

2-4에서 넣은 209번의 **입사가 취소**되었습니다. **지우기 전에 같은 조건으로 SELECT** 합니다.

```sql
SELECT employee_id, first_name, last_name, hire_date, job_id FROM t_emp WHERE employee_id = 209;
```

```result
| employee_id | first_name | last_name | hire_date | job_id |
| --- | --- | --- | --- | --- |
| 209 | Jiho | Lee | 2026-12-01 | ST_CLERK |
```

### 4-2. SELECT를 DELETE로 바꿔 실행 {keep}

확인한 SELECT의 `SELECT … FROM`을 `DELETE FROM`으로 바꾸고 `RETURNING`을 붙입니다.

```sql
DELETE FROM t_emp
 WHERE employee_id = 209
RETURNING employee_id, first_name, last_name;
```

```result DELETE 1
| employee_id | first_name | last_name |
| --- | --- | --- |
| 209 | Jiho | Lee |
```

`RETURNING`이 **방금 지운 행**을 보여 줍니다. 무엇이 지워졌는지 화면에 남는 셈입니다.

### 4-3. NULL인 행 지우기 — `= NULL`은 0행 ⭐ {keep}

2-3에서 급여·부서 없이 넣은 208번처럼, **급여가 비어 있는 직원** 행을 정리합니다.

```sql
DELETE FROM t_emp
 WHERE salary = NULL;
```

```result
DELETE 0
```

```sql
DELETE FROM t_emp
 WHERE salary IS NULL
RETURNING employee_id, first_name, last_name, salary, department_id;
```

```result DELETE 1
| employee_id | first_name | last_name | salary | department_id |
| --- | --- | --- | --- | --- |
| 208 | Minji | Kim | NULL | NULL |
```

3단원 5-1의 규칙이 DML에도 그대로 적용됩니다. `= NULL`은 어떤 행에서도 참이 되지 않아 **오류 없이 0행**을 지웁니다. NULL은 ==`IS NULL`== 로 찾습니다. UPDATE의 `WHERE`도 마찬가지입니다.

### 4-3. 지금까지 바꾼 직원 {keep}

```sql
SELECT employee_id, first_name, last_name, hire_date, job_id, salary, manager_id, department_id
  FROM t_emp
 WHERE employee_id >= 200
 ORDER BY employee_id;
```

```result
| employee_id | first_name | last_name | hire_date | job_id | salary | manager_id | department_id |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 200 | Jennifer | Whalen | 2003-09-17 | AD_ASST | 4400.00 | 101 | 10 |
| 201 | Michael | Hartstein | 2004-02-17 | MK_MAN | 13000.00 | 100 | 20 |
| 202 | Pat | Fay | 2005-08-17 | MK_REP | 6000.00 | 201 | 20 |
| 203 | Susan | Mavris | 2002-06-07 | HR_REP | 6500.00 | 101 | 40 |
| 204 | Hermann | Baer | 2002-06-07 | PR_REP | 10000.00 | 101 | 70 |
| 205 | Shelley | Higgins | 2002-06-07 | AC_MGR | 12008.00 | 101 | 110 |
| 206 | William | Gietz | 2002-06-07 | AC_ACCOUNT | 8300.00 | 205 | 110 |
| 207 | Gildong | Hong | 2026-12-15 | IT_PROG | 5300.00 | 104 | 60 |
| 210 | Seoyeon | Choi | 2026-12-01 | ST_CLERK | 2400.00 | 124 | 50 |
```

- 207번(입사일 12/15, 급여 5,300, 매니저 104)과 210번이 새로 들어왔고, 208번(급여 없음)과 209번(입사 취소)은 사라졌습니다. 3-5의 141번 승진도 사본에만 남아 있습니다.
- 원본 `employees`는 그대로 107명입니다. 바뀐 것은 사본뿐입니다.

### 4-4. WHERE 없는 DELETE {keep}

:::error 모든 행이 지워집니다
```sql
DELETE FROM t_dept;

SELECT COUNT(*) FROM t_dept;
```

```result DELETE 27
| count |
| --- |
| 0 |
```

「모든 행을 지워라」가 정말 의도라면 맞는 문장입니다. 의도가 아니었다면 3-4와 같은 사고입니다.
:::

:::teacher 강사 확인
- 원본 `departments`에 같은 문장을 실행하면 **거부**됩니다. 직원이 소속된 부서를 지우지 못하게 하는 규칙(FK)이 있기 때문입니다. 아래는 오류로 끝나므로 원본이 바뀌지 않습니다. 강사 시연으로만 보여 주세요.

```sql
DELETE FROM departments;
```

```error
ERROR:  update or delete on table "departments" violates foreign key constraint "emp_dept_fk" on table "employees"
DETAIL:  Key (department_id)=(10) is still referenced from table "employees".
```

- CTAS 사본에는 PK(2-6)와 마찬가지로 FK도 복사되지 않아 27행이 모두 지워졌습니다. 이런 규칙은 DDL 단원(참조 무결성)에서 다룹니다.
:::

### 4-4. INSERT … SELECT로 복구 {keep}

**INSERT … SELECT** — `VALUES` 대신 **SELECT 결과를 통째로** 넣을 수 있습니다. 원본에서 다시 가져옵니다.

```sql
INSERT INTO t_dept
SELECT * FROM departments;

SELECT COUNT(*) FROM t_dept;
```

```result INSERT 0 27
| count |
| --- |
| 27 |
```

### 4-4. INSERT … SELECT의 모양 {keep}

```text INSERT … SELECT의 모양
INSERT INTO 테이블 [(컬럼, …)]
SELECT 컬럼, …                ← VALUES 대신 SELECT
  FROM 다른테이블
 WHERE 조건;                  ← 조건으로 일부만 넣을 수도 있음
```

- SELECT 결과의 컬럼 수·순서가 넣을 테이블과 맞아야 합니다. 여기서는 사본이 원본을 그대로 복사한 구조라 `SELECT *`로 맞았습니다.
- 0장의 `CREATE TABLE … AS SELECT`는 **테이블을 새로 만들면서** 채우고, `INSERT … SELECT`는 **이미 있는 테이블에** 채웁니다.

> 테이블의 행을 모두 비우는 방법에는 `DELETE` 말고도 `TRUNCATE`(DDL)가 있고, 테이블 자체를 없애는 `DROP`도 있습니다. 세 명령의 차이는 DDL 단원에서 비교합니다.

### 4-5. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (2-7·3-6을 푼 상태에서 이어서 풉니다.)

:::try
**[복습]** 3-6 [응용]에서 재고에 반영한 **6번 입고 예정**을 지우세요. 지우기 전에 같은 조건으로 SELECT 하고, `RETURNING`으로 지운 행을 확인합니다.

**[응용]** 2-7 [응용]에서 넣은 8번처럼 **PO 번호가 비어 있는** 입고 예정을 지우려고 합니다. 아래 두 문장을 **위에서부터 순서대로** 실행해 결과 메시지와 `RETURNING` 결과를 비교하고, 어느 쪽이 맞는지 설명하세요.

```sql
DELETE FROM t_scheduled_receipt WHERE po_no = NULL
RETURNING receipt_id, part_no, vendor_code, po_no;

DELETE FROM t_scheduled_receipt WHERE po_no IS NULL
RETURNING receipt_id, part_no, vendor_code, po_no;
```
:::

### 4-5. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
```sql
SELECT receipt_id, part_no, eta_date, qty FROM t_scheduled_receipt WHERE receipt_id = 6;
```

```result
| receipt_id | part_no | eta_date | qty |
| --- | --- | --- | --- |
| 6 | EBA56264701 | 2026-12-04 | 2000.00 |
```

```sql
DELETE FROM t_scheduled_receipt
 WHERE receipt_id = 6
RETURNING receipt_id, part_no, qty;
```

```result DELETE 1
| receipt_id | part_no | qty |
| --- | --- | --- |
| 6 | EBA56264701 | 2000.00 |
```

SELECT의 `SELECT … FROM`만 `DELETE FROM`으로 바꿨습니다(4-2). 이제 6번의 2,000개는 재고(3-6)에만 있습니다.
:::

### 4-5. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
첫 문장은 `DELETE 0`(돌려준 행 없음), 두 번째 문장이 맞습니다.

```result 첫 문장 (= NULL)
DELETE 0
```

```result 두 번째 문장 (IS NULL) — DELETE 1
| receipt_id | part_no | vendor_code | po_no |
| --- | --- | --- | --- |
| 8 | MGL96663301 | NULL | NULL |
```

`= NULL`은 어떤 행에서도 참이 되지 않아 0행을 지웁니다(4-3). PO 번호가 빈 행은 2-7에서 넣은 8번 하나였습니다.
:::

### 4-5. 지금까지 바꾼 입고 예정 {keep}

```sql
SELECT receipt_id, part_no, eta_date, qty, po_no, receipt_type
  FROM t_scheduled_receipt
 ORDER BY eta_date, receipt_id;
```

```result
| receipt_id | part_no | eta_date | qty | po_no | receipt_type |
| --- | --- | --- | --- | --- | --- |
| 7 | ECP39799101 | 2026-12-03 | 600.00 | PO26-1107 | Scheduled |
| 1 | ECP39799101 | 2026-12-05 | 800.00 | PO26-1101 | Scheduled |
| 3 | MGL96663301 | 2026-12-05 | 1500.00 | PO26-1103 | Scheduled |
| 4 | EIC93178801 | 2026-12-10 | 6000.00 | PO26-1104 | Scheduled |
| 5 | RSS86949501 | 2026-12-12 | 800.00 | PO26-1105 | Planned |
| 2 | ECP39799101 | 2026-12-15 | 1600.00 | PO26-1102 | Planned |
| 9 | RSS86949501 | 2026-12-16 | 300.00 | PO26-1108 | Planned |
| 10 | EIC93178801 | 2026-12-17 | 3000.00 | PO26-1109 | Planned |
```

- 처음 6건에서 7번(12/3, 600개)·9번·10번이 새로 들어왔고, 1번은 12/8 → 12/5로 앞당겨졌으며, 6번(입고 완료)과 8번(PO 없음)이 사라졌습니다. 이 8행이 복습 문제(6장)의 출발 상태입니다.
- 컴프레서는 이제 12/3 600개 + 12/5 800개가 들어옵니다. 이 변경으로 12/4 결품이 해결되는지는 Day 3의 컴프레서 결품일 쿼리(Q11)를 **사본 기준으로** 다시 돌려 보면 알 수 있습니다.

:::teacher 강사 확인
- 도전 과제(시간이 남으면): Day 3 7교시의 Q11(컴프레서 결품일) 쿼리에서 `scheduled_receipt`를 `t_scheduled_receipt`로, `inventory`를 `t_inventory`로 바꿔 실행해 위 변경(12/3 600개, 12/5 800개)으로 결품일이 어떻게 바뀌는지 확인하게 하세요. 이 교안에서는 결과를 검증하지 않았습니다. 도전 과제는 복습 문제(6장)를 풀기 **전에** 실행하세요. 복습 4·6까지 풀면 재고에는 3번·6번 입고가 이미 더해진 채로 입고 예정이 원본으로 되돌아가, 같은 수량이 두 번 잡힙니다.
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 5. 안전하게 DML 하는 순서

### 5-1. 다섯 단계 습관 ⭐ {keep}

오늘 실습에서 나온 사고(`UPDATE 27`, `DELETE 27`, `UPDATE 0`, `DELETE 0`)는 모두 **오류 메시지 없이** 일어났습니다. DML은 아래 순서를 습관으로 만드세요.

```flow 안전한 DML 순서
search | ① 같은 WHERE로 SELECT | 행 수·값 확인 (3-2, 4-2) | ivory
pencil | ② 앞부분만 바꿔 실행 | UPDATE … SET / DELETE (4-2) | plum
hash | ③ 결과 숫자 확인 | ①의 행 수와 같은가 | hot
list-checks | ④ 결과 확인 | RETURNING 또는 SELECT (3-3, 3-5) | lime
copy | ⑤ 연습은 사본에서 | t_ 테이블만 (0장) | rose
```

> 이 순서에도 한계가 있습니다. ③에서 숫자가 틀린 것을 알아채도 **이미 확정된 뒤**입니다(1-3). 「실행해 보고, 확인한 뒤, 확정하거나 취소」하는 방법이 다음 교시의 `BEGIN` / `COMMIT` / `ROLLBACK`입니다.

:::teacher 강사 확인
- 운영안 Day 4 4H(승인 흐름과 이력 원칙)에는 「**DELETE 대신 상태 변경**, 이력 덮어쓰기 금지」가 있습니다. 오늘 4-2에서 입사가 취소된 직원을 DELETE로 지웠지만, 실무 기록 테이블에서는 행을 지우지 않고 상태를 바꿔 「언제 무엇이 있었는지」를 남기는 경우가 많다는 점을 예고해 두세요. HR 원본이 직책이 바뀔 때 옛 직책을 `job_history`에 남기는 것(3-5)도 같은 원칙입니다.
:::

## 6. 복습 문제

### 6-0. 복습 문제 안내 {keep}

> 범위: INSERT · UPDATE · DELETE 전체. 생산 데이터의 **사본(`t_`) 테이블에만** 풀어 주세요(실행 전: `SET search_path TO bom;`). 확인 문제(2-7, 3-6, 4-5)를 순서대로 푼 뒤의 상태(4-5의 입고 예정 8행)에서 이어서 풉니다. (출력 순서는 `ORDER BY` 기준)

```icons 여섯 문항
plus | 1 · INSERT | 정수 필터 입고 예정 넣기 | rose
pencil | 2 · UPDATE 계산식 | 재고 실사 +50 | plum
trash-2 | 3 · DELETE 조건 두 개 | 마이컴 계획 입고 취소 | lime
arrow-right-left | 4 · 두 테이블 | 입고 → 재고 반영 + 예정 삭제 | ivory
git-merge | 5 · 있으면 UPDATE, 없으면 INSERT | 재고 실사 결과 반영 | plum
history | 6 · 전체 삭제 + 복구 | INSERT … SELECT | hot
```

### 6-1. 복습 1 {keep}

**1.** 정수 필터(`MFT43979901`)의 입고 예정을 `t_scheduled_receipt`에 넣고 확인하세요.
`receipt_id` 11, 사이트 `CW`, 업체 `V1010`, 도착일 2026-12-10, 수량 500, PO `'PO26-1110'`, 구분 `'Planned'`

```result 출력 결과 — INSERT 0 1
| receipt_id | part_no | vendor_code | eta_date | qty | po_no | receipt_type |
| --- | --- | --- | --- | --- | --- | --- |
| 11 | MFT43979901 | V1010 | 2026-12-10 | 500.00 | PO26-1110 | Planned |
```

### 6-2. 복습 2 {keep}

**2.** 재고 실사 결과, 창원(CW) 컴프레서(`ECP39799101`) 재고가 시스템보다 50개 많았습니다. `t_inventory`의 재고를 지금 값보다 50 늘리고, `RETURNING`으로 확인하세요.
[힌트: 지금 값 1150에 50을 더한 1200을 직접 쓰지 말고 `on_hand_qty + 50`]

```result 출력 결과 — UPDATE 1
| site_code | part_no | on_hand_qty | location |
| --- | --- | --- | --- |
| CW | ECP39799101 | 1200.00 | WH-A |
```

### 6-3. 복습 3 {keep}

**3.** 마이컴(`EIC93178801`)의 입고 예정 중 「계획 입고(Planned)」만 취소되었습니다. 해당 행만 지우고 `RETURNING`으로 확인하세요. 확정 입고(Scheduled) 4번은 남아야 합니다.

```result 출력 결과 — DELETE 1
| receipt_id | part_no | eta_date | qty | receipt_type |
| --- | --- | --- | --- | --- |
| 10 | EIC93178801 | 2026-12-17 | 3000.00 | Planned |
```

### 6-4. 복습 4 {keep}

**4.** 도어 글라스(`MGL96663301`) 입고 예정 3번이 입고되었습니다.
① 3번의 수량만큼 `t_inventory`의 CW 재고를 늘리고 ② 3번 입고 예정을 지우세요.
[힌트: 3-6 [응용] — 수량은 서브쿼리로 가져옵니다.]

:::cols
```result ① UPDATE 1
| part_no | on_hand_qty |
| --- | --- |
| MGL96663301 | 4100.00 |
```

```result ② DELETE 1
| receipt_id | part_no | qty |
| --- | --- | --- |
| 3 | MGL96663301 | 1500.00 |
```
:::

### 6-5. 복습 5 {keep}

**5.** 재고 실사 결과가 아래처럼 들어왔습니다. `t_inventory`에 이미 있는 행(사이트·품번·위치가 같은 행)이면 UPDATE, 없으면 INSERT 하세요.

- CW, `EMT68237401`(DD 모터), 위치 `WH-C1` : 950개
- CW, `ECP39799101`(컴프레서), 위치 `WH-B` : 100개 (기준일 2026-11-30)

[힌트: 먼저 두 품번의 재고 행을 SELECT로 확인합니다.]

:::cols
```result 확인용 SELECT 결과
| site_code | part_no | on_hand_qty | location |
| --- | --- | --- | --- |
| CW | ECP39799101 | 1200.00 | WH-A |
| CW | EMT68237401 | 900.00 | WH-C1 |
```

```result 출력 결과
| site_code | part_no | on_hand_qty | as_of_date | location |
| --- | --- | --- | --- | --- |
| CW | ECP39799101 | 1200.00 | 2026-11-30 | WH-A |
| CW | ECP39799101 | 100.00 | 2026-11-30 | WH-B |
| CW | EMT68237401 | 950.00 | 2026-11-30 | WH-C1 |
```
:::

### 6-6. 복습 6 {keep}

**6.** `t_scheduled_receipt`의 모든 행을 지운 뒤, 원본 `scheduled_receipt`의 데이터로 다시 채우세요. 지운 행 수와 다시 채운 뒤의 행 수를 확인합니다.

```result 출력 결과 — DELETE 7 → INSERT 0 6
| count |
| --- |
| 6 |
```

### 6-7. 복습 1~3 답 {keep}

:::answer 복습 1~3 예시 답안
```sql 1
INSERT INTO t_scheduled_receipt
       (receipt_id, site_code, part_no, vendor_code, eta_date, qty, po_no, receipt_type)
VALUES (11, 'CW', 'MFT43979901', 'V1010', '2026-12-10', 500, 'PO26-1110', 'Planned');

SELECT receipt_id, part_no, vendor_code, eta_date, qty, po_no, receipt_type
  FROM t_scheduled_receipt WHERE receipt_id = 11;
```

```sql 2
UPDATE t_inventory
   SET on_hand_qty = on_hand_qty + 50
 WHERE site_code = 'CW'
   AND part_no   = 'ECP39799101'
RETURNING site_code, part_no, on_hand_qty, location;
```

```sql 3
DELETE FROM t_scheduled_receipt
 WHERE part_no      = 'EIC93178801'
   AND receipt_type = 'Planned'
RETURNING receipt_id, part_no, eta_date, qty, receipt_type;
```

- 2번: 재고 실사 결과는 「50개 많다」는 **차이**입니다. 1150을 보고 `SET on_hand_qty = 1200`이라고 쓰면, 그 사이 다른 사람이 재고를 바꿨을 때 그 변경을 덮어씁니다(3-3).
- 3번: `part_no` 조건만 쓰면 확정 입고 4번(6,000개)까지 지워집니다. 조건이 두 개 필요한 이유를 확인하세요.
:::

### 6-8. 복습 4 답 {keep}

:::answer 복습 4 예시 답안
```sql 4
UPDATE t_inventory
   SET on_hand_qty = on_hand_qty + (SELECT qty FROM t_scheduled_receipt WHERE receipt_id = 3)
 WHERE site_code = 'CW'
   AND part_no   = 'MGL96663301'
RETURNING part_no, on_hand_qty;

DELETE FROM t_scheduled_receipt
 WHERE receipt_id = 3
RETURNING receipt_id, part_no, qty;
```

- 4번: ①과 ②의 **순서**가 중요합니다. ②를 먼저 하면 ①의 서브쿼리가 3번 입고를 찾지 못해 NULL을 더하게 됩니다(`on_hand_qty + NULL` = NULL). 그리고 ①만 하고 ②를 빠뜨리면 같은 1,500개가 재고와 입고 예정에 동시에 남아, 결품 계산에서 두 번 더해집니다(3-6 [응용]).
:::

### 6-9. 복습 5 답 {keep}

:::answer 복습 5 예시 답안
```sql 5
SELECT site_code, part_no, on_hand_qty, location
  FROM t_inventory
 WHERE part_no IN ('EMT68237401', 'ECP39799101')
 ORDER BY part_no, location;

UPDATE t_inventory                       -- WH-C1 행이 있으므로 UPDATE
   SET on_hand_qty = 950
 WHERE site_code = 'CW'
   AND part_no   = 'EMT68237401'
   AND location  = 'WH-C1';

INSERT INTO t_inventory (site_code, part_no, on_hand_qty, as_of_date, location)   -- WH-B 행이 없으므로 INSERT
VALUES ('CW', 'ECP39799101', 100, '2026-11-30', 'WH-B');

SELECT site_code, part_no, on_hand_qty, as_of_date, location
  FROM t_inventory
 WHERE part_no IN ('EMT68237401', 'ECP39799101')
 ORDER BY part_no, location;
```

- 5번: DD 모터는 사내 부품라인 창고(`WH-C1`)에 있습니다. 같은 컴프레서라도 **위치(`location`)가 다르면 다른 행**입니다(`inventory`의 PK가 `site_code, part_no, location`). 컴프레서는 이제 재고 행이 2개라, 재고를 스칼라 서브쿼리로 가져오면 오류가 납니다 — `SUM`으로 감싸야 합니다.
:::

### 6-10. 복습 6 답 {keep}

:::answer 복습 6 예시 답안
```sql 6
DELETE FROM t_scheduled_receipt;

INSERT INTO t_scheduled_receipt
SELECT * FROM scheduled_receipt;

SELECT COUNT(*) FROM t_scheduled_receipt;
```

- 6번: 지운 행이 7개인 이유 — 확인 문제를 마친 상태 8행 + 1번 INSERT 1행 − 3번 DELETE 1행 − 4번 DELETE 1행 = 7행입니다. 원본은 6행이므로 6행으로 돌아옵니다.
:::

:::teacher 강사 확인
- 확인 문제와 복습 문제까지 순서대로 풀면 생산 사본 행 수는 `t_inventory` **54**(5번 INSERT 1행 추가), `t_scheduled_receipt` 6입니다. 원본은 53 / 6 그대로입니다. 본문을 끝낸 HR 사본은 `t_emp` 109행(207·210 추가), `t_dept` 27행입니다(검증 완료).
- 기존 실습문제 5번(`MONEY = 0`인 회원 일괄 변경)·7번(`LIKE '%.png'` 조건 삭제) 유형은 본문 3-4·4-3(조건으로 여러 행)에 녹였습니다. 따로 내려면 예: 「`t_emp`에서 직책이 `ST_CLERK`인 직원의 급여를 일괄 100 올리기 — 먼저 같은 WHERE로 SELECT 해 행 수를 확인」처럼 조건 UPDATE를 내 주세요.
- 다음 교시 TCL 단원 0장은 필요한 사본을 `DROP TABLE IF EXISTS` 뒤 다시 만듭니다. 오늘 바꾼 사본 내용이 TCL 실습에 남지 않으니 따로 정리하지 않아도 됩니다. 정리하려면 0-3의 `DROP TABLE IF EXISTS` 줄만 실행합니다(`DROP`은 DDL 단원).
:::

## 7. 정리

### 7-1. 오늘 배운 것 {keep}

:::summary
- **DML**: 테이블 안의 데이터를 바꾸는 SQL — `INSERT`(행 추가), `UPDATE`(값 변경), `DELETE`(행 삭제). 결과는 `INSERT 0 1`, `UPDATE 27`, `DELETE 0`처럼 **바뀐 행 수**로 나옵니다.
- **자동 커밋**: PostgreSQL은 문장마다 즉시 확정합니다. 연습은 **사본**(`CREATE TABLE t_… AS SELECT …`)에서 합니다.
- **INSERT**: `INSERT INTO 테이블 (컬럼, …) VALUES (값, …);` 컬럼 목록은 생략하지 않습니다. 뺀 컬럼은 NULL. `VALUES (…), (…)`로 여러 행, `INSERT INTO … SELECT …`로 SELECT 결과를 통째로.
- **UPDATE**: `UPDATE 테이블 SET 컬럼 = 값, … WHERE 조건;` 계산은 `salary = salary + 500`처럼 SQL 안에서. 다른 테이블의 값은 서브쿼리로 가져옵니다.
- **DELETE**: `DELETE FROM 테이블 WHERE 조건;` 행 단위로 지웁니다.
- **WHERE를 빠뜨리면** UPDATE·DELETE는 **모든 행**에 적용되고, 오류는 나지 않습니다. 조건이 틀리면 `UPDATE 0`/`DELETE 0`으로 조용히 지나갑니다. NULL 조건은 `IS NULL`.
- **RETURNING**: 바뀌거나 지워진 행을 그 자리에서 보여 줍니다.
- **안전한 순서**: 같은 WHERE로 SELECT → DML 실행 → 행 수 확인 → 결과 확인, 그리고 연습은 사본에서. 확정 전에 되돌리는 방법은 다음 교시(TCL).
:::

### 7-2. 확인 문제

:::quiz
Q. `UPDATE t_dept SET location_id = 1700;`을 실행했더니 `UPDATE 27`이 나왔습니다. 무엇이 잘못되었고, 원본이 있다면 어떻게 복구하나요?
A. `WHERE`가 없어 27개 부서 모두의 위치가 1700으로 바뀌었습니다. 원본 `departments`에서 같은 부서 번호의 위치를 스칼라 서브쿼리로 가져와 `UPDATE … SET location_id = (SELECT …)`로 되돌립니다.

Q. `DELETE FROM t_emp WHERE salary = NULL;`의 결과가 `DELETE 0`입니다. 왜 그런가요? 어떻게 고치나요?
A. NULL과의 `=` 비교는 참이 되지 않아 어떤 행도 조건에 맞지 않습니다. `WHERE salary IS NULL`로 씁니다.

Q. 컬럼 목록 없이 `INSERT INTO t_emp VALUES (…)`를 쓰면 어떤 위험이 있나요?
A. 값이 테이블의 컬럼 순서대로 들어가므로, 순서를 착각하면 엉뚱한 컬럼에 값이 들어갑니다. `first_name`과 `last_name`처럼 자료형이 같은 컬럼끼리 바뀌면 오류도 나지 않습니다. 컬럼 목록을 항상 적습니다.

Q. 승진한 직원의 급여를 바꿀 때 `SET salary = 5500`이 아니라 `SET salary = (SELECT min_salary FROM jobs WHERE …)`로 쓰는 이유는?
A. 기준 값(직책의 최저 급여)은 직책 테이블에 있습니다. 화면에서 보고 옮겨 적으면 잘못 적을 수 있고, 기준이 바뀐 뒤에도 옛 숫자를 쓰게 됩니다. 값을 가진 테이블에서 SQL 안으로 가져와야 정확합니다.

Q. 직원의 직책 UPDATE는 했는데 `job_history` INSERT를 하지 않으면 어떤 문제가 생기나요?
A. 직책은 바뀌었는데 이전 직책의 기록이 남지 않아, 그 직원이 언제까지 무슨 일을 했는지 알 수 없게 됩니다. 두 문장은 함께 성공하거나 함께 취소되어야 하며, 그 방법을 다음 교시(TCL)에서 배웁니다.
:::
