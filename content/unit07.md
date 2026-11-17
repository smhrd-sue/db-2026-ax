---
label: 7. DDL
title: 데이터 구조 만들기
---

# CREATE · 제약조건 · ALTER · DROP

:::goal
- `CREATE TABLE`로 알맞은 PostgreSQL 자료형(CHAR·VARCHAR·TEXT·NUMERIC·DATE·TIMESTAMP)을 골라 테이블을 만들고, NOT NULL과 DEFAULT의 동작을 설명할 수 있습니다.
- 제약조건 다섯 가지(PK·UNIQUE·NOT NULL·CHECK·FK)를 걸고, 오류 메시지로 무엇이 막혔는지 읽을 수 있습니다.
- `ALTER TABLE`로 컬럼·이름·기본값·제약조건을 고치고, DELETE·TRUNCATE·DROP과 CASCADE의 차이를 설명할 수 있습니다.
- 판단 결과(급여 조정 제안)를 기록하는 테이블을 PK·FK·CHECK와 함께 설계할 수 있습니다.
:::

:::teacher 단원 구성 (60분)
- 운영안 Day 4 **3H(기록 테이블 설계: 판단 기록에 필요한 컬럼, PostgreSQL 자료형, PK·FK·CHECK 제약 포함 CREATE TABLE, 기존 이력 테이블 2종과 비교)** 에 해당합니다. Day 4 1H(DML)·2H(TCL) 다음 교시이므로, 1H에서 쓴 `CREATE TABLE ... AS SELECT`(연습용 사본 만들기)를 2-6에서 정식으로 다룹니다.
- 기존 교안 `9. DDL.pptx` · `09.DDL복습문제.txt` · `8. DDL.sql`의 **순서(CREATE → 제약조건 → ALTER → DROP/TRUNCATE)와 실습 유형(직원·부서 테이블, 회원·블로그 테이블, TB_CUST)** 을 따랐습니다. **본문 예제는 HR 실습 데이터(`hr` 스키마)**, **확인 문제·복습 문제는 생산 실습 데이터(`bom` 스키마)** 로 만들었고, 마지막에 **판단 기록 테이블 설계(6장, HR 급여 조정 제안)** 를 붙였습니다.
- 운영안 3H의 생산 시나리오 **결품 경고 기록 테이블 `shortage_alert`**(기존 이력 테이블 2종 `uit_change_history`·`part_status_history`와 비교 포함)는 **7장 복습 5번**으로 옮겼습니다. Day 4 4교시(승인 흐름)·6교시(`check_shortage` 결과 INSERT)가 이 테이블을 쓰므로 **복습 5번은 수업 시간에 함께 실행**하세요.
- 기존 교안의 문법 중 PostgreSQL에서 그대로 쓰지 않는 것은 다음과 같이 바꿨습니다: `VARCHAR2` → `VARCHAR`, `NUMBER` → `INT`/`NUMERIC`, `MODIFY` → `ALTER COLUMN ... TYPE / SET NOT NULL`, `CASCADE CONSTRAINT` → `CASCADE`, 「가변형문자 n**BYTE**」 → PostgreSQL의 `VARCHAR(n)`은 **글자 수** 기준(2-4). `8. DDL.sql`의 한글 테이블·컬럼 이름(`직원`, `부서ID`)은 2-5 이름 규칙에 따라 영문 소문자로 바꿨습니다. 또 `9. DDL.pptx` 31번 「TRUNCATE: 복구 불가능」은 PostgreSQL에서는 맞지 않습니다(5-2).
- INSERT는 **제약조건이 실제로 막는지 확인하는 용도로만** 씁니다. 문법은 1교시 DML 단원에서 배웠습니다.
- 원본(`hr`·`bom`) 보호를 위해 모든 실습 테이블은 **`lab` 스키마**에 만듭니다(1-4). 수업이 끝나면 `DROP SCHEMA lab CASCADE;` 한 줄로 정리됩니다(7장 6번).
- HR 사본 `t_emp`·`t_dept`(2-6)는 DML·TCL 단원이 `hr`에 만든 `hr.t_emp`·`hr.t_dept`(TCL 단원에서는 `LIKE … INCLUDING ALL`로 다시 만들어 PK·CHECK까지 있음)와 **이름은 같지만 `lab`에 새로 만드는 별개의 사본**입니다. DML·TCL 단원에서 바꾼 사본 내용과 상관없이 결과가 같고(새 DB와 DML·TCL 실습 뒤 DB 모두에서 확인), `hr` 쪽 사본과 원본 `employees`는 건드리지 않습니다(원본 `employees`에는 평일 업무 시간 외 변경을 막는 트리거 `secure_employees`도 있습니다). 사본을 지우는 문장은 `lab.t_dept`처럼 스키마를 붙였습니다(스키마 없이 쓰면 `lab`에 없을 때 `hr.t_dept`가 지워집니다 — 5-1).
- 교안의 모든 SQL과 실행 결과는 `schema_postgres.sql`·`hr_postgres.sql`로 적재한 DB에서 **위에서부터 순서대로 직접 실행한 결과**입니다. 오류 메시지도 실제 출력입니다. (검증 환경: PostgreSQL 18, `DateStyle = ISO, YMD`.) 순서를 바꿔 실행하면 일부 결과(행 수, 오류 여부)가 달라집니다. PostgreSQL 18은 NOT NULL도 `pg_constraint`에 기록하므로(3-5), 제약조건 조회 쿼리에는 모두 `contype IN ('p', 'u', 'c', 'f')` 조건을 넣어 16·18 두 버전에서 결과가 같도록 했습니다.
- 2~5장 끝 「확인 문제」(복습 1 + 응용 1)는 기존 교안 실습(회원·블로그)과 생산 실습 데이터(`bom` 스키마)로 만들었고, 답안 결과도 직접 실행한 값입니다(6장은 도전 1문항). 실행 전 `SET search_path TO lab, bom;`이 필요하고, 마친 뒤에는 `SET search_path TO lab, hr;`로 돌아옵니다.
- 이 단원은 1교시(60분) 분량입니다. 확인 문제와 7장 복습 문제는 시간에 따라 일부만 풀고, 나머지는 과제로 활용하세요(복습 5번은 위 설명대로 수업 중 실행).
- 확인 문제는 서로 이어집니다: 2-7(`member`·`bom_wm`) → 3-7(`blog`, `member`·`bom_wm`에 제약조건) → 4-5(`blog`·`bom_wm` 고치기) → 5-4(`member`·`blog` 삭제, `bom_wm` TRUNCATE). 앞 문제를 건너뛰면 뒤 문제도 함께 건너뛰어야 합니다.
- 본문 실습도 앞 결과에 의존합니다. 다음은 건너뛰면 뒤가 막힙니다: 1-4(`lab` 스키마), 2-3(`emp_memo`), 2-6의 사본 3개(`t_emp`·`t_dept`·`emp_ship`)와 중복 INSERT(3-6 ③), 3-3~3-4(`training`과 행 4개 → 4·5장 결과), 3-6 사본 정리, 4-2~4-4(→ 5장), 6-3(`salary_proposal`).

| 교시 | 시간 | 내용 | 해당 장 | 기존 교안 대응 |
| --- | --- | --- | --- | --- |
| **Day 4 3교시** | 0~8분 | SQL 종류 · 이미 본 DDL(hr_postgres.sql) · 구조 확인 · lab 스키마 | 1 | `9. DDL.pptx` 3~4 |
| | 8~20분 | CREATE TABLE · 자료형 · NOT NULL · DEFAULT · 이름 규칙 · CTAS 사본 | 2 | `9. DDL.pptx` 5~9, 20~21 |
| | 20~35분 | 제약조건 5종 · PK/UK/CHECK/FK 동작 · 제약조건으로 이상 데이터 찾기 | 3 | `9. DDL.pptx` 10~19, 22 |
| | 35~42분 | ALTER TABLE: 추가 · 변경 · 이름 변경 · 삭제 | 4 | `9. DDL.pptx` 23~25 |
| | 42~48분 | DROP · CASCADE · TRUNCATE · DELETE/TRUNCATE/DROP 비교 | 5 | `9. DDL.pptx` 26~31 |
| | 48~60분 | 급여 조정 제안 기록 테이블 설계 · 복습 문제 안내(결품 경고 테이블) | 6~7 | `09.DDL복습문제.txt` |
:::

## 1. DDL — 데이터의 「그릇」을 정의하는 SQL

### 1-1. SQL 문장의 종류 {keep}

지금까지 배운 `SELECT`는 이미 있는 데이터를 **꺼내는** 문장이었습니다. 이번 단원의 **DDL(Data Definition Language, 데이터 정의어)** 은 데이터를 담을 **그릇(테이블)** 을 만들고, 고치고, 없애는 문장입니다.

| 종류 | 이름 | 하는 일 | 대표 명령어 |
| --- | --- | --- | --- |
| QUERY | 질의어 | 데이터 검색·조회 | `SELECT` |
| **DDL** | **데이터 정의어** | **테이블 같은 객체를 만들거나 수정·삭제** | **`CREATE`, `ALTER`, `DROP`, `TRUNCATE`** |
| DML | 데이터 조작어 | 행을 넣고 고치고 지움 | `INSERT`, `UPDATE`, `DELETE` |
| DCL | 데이터 제어어 | 권한 부여·회수 | `GRANT`, `REVOKE` |
| TCL | 트랜잭션 제어어 | 작업 묶음 확정·취소 | `BEGIN`, `COMMIT`, `ROLLBACK` |

### 1-1. 이번 단원에서 배우는 DDL {keep}

```icons DDL 명령어
table | CREATE TABLE | 테이블 만들기 (2장) | rose
shield-check | ADD CONSTRAINT | 제약조건(입력 규칙) 걸기 (3장) | plum
pencil | ALTER TABLE | 컬럼·이름·기본값 바꾸기 (4장) | lime
trash-2 | DROP · TRUNCATE | 테이블 삭제 / 데이터만 비우기 (5장) | hot
```

### 1-2. 이미 만나 본 DDL — hr_postgres.sql {keep}

2단원에서 실행한 `hr_postgres.sql`은 대부분이 DDL입니다(생산 데이터의 `schema_postgres.sql`도 마찬가지입니다). 직원 테이블을 만드는 부분을 다시 읽어 봅니다.

```sql hr_postgres.sql — employees
CREATE TABLE employees
    ( employee_id    NUMERIC(6)
    , first_name     VARCHAR(20)
    , last_name      VARCHAR(25)    CONSTRAINT emp_last_name_nn NOT NULL
    , email          VARCHAR(25)    CONSTRAINT emp_email_nn NOT NULL
    , phone_number   VARCHAR(20)
    , hire_date      DATE           CONSTRAINT emp_hire_date_nn NOT NULL
    , job_id         VARCHAR(10)    CONSTRAINT emp_job_nn NOT NULL
    , salary         NUMERIC(8,2)
    , commission_pct NUMERIC(2,2)
    , manager_id     NUMERIC(6)
    , department_id  NUMERIC(4)
    , CONSTRAINT emp_salary_min CHECK (salary > 0)
    , CONSTRAINT emp_email_uk   UNIQUE (email)
    , CONSTRAINT emp_emp_id_pk  PRIMARY KEY (employee_id)
    , CONSTRAINT emp_dept_fk    FOREIGN KEY (department_id) REFERENCES departments (department_id)
    , CONSTRAINT emp_job_fk     FOREIGN KEY (job_id)        REFERENCES jobs (job_id)
    , CONSTRAINT emp_manager_fk FOREIGN KEY (manager_id)    REFERENCES employees (employee_id)
    );
```

### 1-2. 한 줄씩 읽기 {keep}

| 줄 | 읽는 법 | 이번 단원 |
| --- | --- | --- |
| `employee_id NUMERIC(6)` · `PRIMARY KEY (employee_id)` | 사번은 **최대 6자리 숫자**이고, **비어 있을 수 없고 중복될 수 없다** | 2-2, 3-1 |
| `last_name VARCHAR(25) … NOT NULL` | 성은 **최대 25글자** 문자, **반드시 있어야** 한다 | 2-3 |
| `salary NUMERIC(8,2)` · `CHECK (salary > 0)` | 급여는 **소수 둘째 자리까지** 담는 숫자, **0보다 커야** 한다 | 2-2, 3-4 |
| `email … UNIQUE (email)` | 이메일은 **중복될 수 없다** | 3-4 |
| `department_id … REFERENCES departments` | 부서 번호는 **`departments`에 있는 번호만** 넣을 수 있다 | 3-4 |
| `hire_date DATE` | 입사일은 **날짜** | 2-2 |

> 5단원에서 본 HR 테이블의 연결선(조인 키)은 DDL의 `REFERENCES`(외래키)에서 나온 것입니다. ==ERD는 그림, DDL은 그 그림을 DB가 이해하는 문장으로 쓴 것==입니다(1단원 「물리적 모델링」).

### 1-3. 테이블 구조 확인하기 {keep}

> 실행 전: `SET search_path TO hr;` — 이 단원의 본문 예제는 HR 실습 데이터(`hr_postgres.sql`의 `hr` 스키마)로 실행합니다. 1-4부터는 연습 공간 `lab`을 함께 씁니다.

만들어진 테이블의 구조는 **`information_schema.columns`** 를 조회하면 볼 수 있습니다. pgAdmin·psql 어디서나 똑같이 동작합니다.

:::cols
```sql
SELECT column_name
     , data_type
     , character_maximum_length AS max_len
     , is_nullable
     , column_default
  FROM information_schema.columns
 WHERE table_schema = 'hr'
   AND table_name   = 'employees'
 ORDER BY ordinal_position;
```

```result
| column_name | data_type | max_len | is_nullable | column_default |
| --- | --- | --- | --- | --- |
| employee_id | numeric | NULL | NO | NULL |
| first_name | character varying | 20 | YES | NULL |
| last_name | character varying | 25 | NO | NULL |
| email | character varying | 25 | NO | NULL |
| phone_number | character varying | 20 | YES | NULL |
| hire_date | date | NULL | NO | NULL |
| job_id | character varying | 10 | NO | NULL |
| salary | numeric | NULL | YES | NULL |
| commission_pct | numeric | NULL | YES | NULL |
| manager_id | numeric | NULL | YES | NULL |
| department_id | numeric | NULL | YES | NULL |
```
:::

### 1-3. 결과 읽기 {keep}

- `is_nullable = NO`인 컬럼은 `NOT NULL`(또는 PK)이 걸려 있다는 뜻입니다. `employee_id`는 PK, 나머지 넷은 `NOT NULL`입니다.
- `VARCHAR`는 `character varying`으로, `INT`는 `integer`로 표시됩니다. 같은 자료형의 **정식 이름**입니다. `max_len`은 문자 컬럼의 최대 글자 수라 숫자·날짜 컬럼은 NULL입니다.

> **psql을 쓴다면** `\d hr.employees` 한 줄로 컬럼·PK·FK·「이 테이블을 참조하는 테이블」까지 한 번에 볼 수 있습니다. `\d`는 psql 전용 명령이라 pgAdmin Query Tool에서는 동작하지 않습니다.

### 1-4. 연습 공간 만들기 — lab 스키마 ⭐ {keep}

DDL은 **테이블 자체를** 바꾸거나 지웁니다. 실수로 `hr`의 원본 테이블을 건드리면 3~6단원에서 배운 쿼리 결과가 모두 달라집니다. 그래서 연습용 스키마 `lab`을 따로 만들고, 그 안에서만 실습합니다.

```sql
CREATE SCHEMA lab;
SET search_path TO lab, hr;
```

```sql
SELECT current_schemas(false);
```

```result
| current_schemas |
| --- |
| {lab,hr} |
```

### 1-4. search_path — 스키마를 찾아보는 순서 {keep}

- `search_path`는 「스키마 이름을 생략했을 때 찾아볼 순서」입니다. 이제 **새로 만드는 테이블은 맨 앞의 `lab`** 에 생기고, `employees`처럼 이름만 쓰면 `lab`에 없으니 `hr`에서 찾습니다.
- 원본을 가리킬 때는 이 교안처럼 ==`hr.employees`, `hr.departments`로 스키마를 붙여 쓰는 습관==을 들이세요. 어느 테이블을 읽는지 헷갈리지 않습니다.

> `search_path`는 접속할 때마다 초기화됩니다. 다시 접속했다면 `SET search_path TO lab, hr;`부터 다시 실행하세요. (`CREATE SCHEMA lab;`은 처음 한 번만 실행합니다.)

:::teacher 강사 확인
- `search_path`는 접속(세션)마다 초기화됩니다. 쉬는 시간 뒤 pgAdmin Query Tool을 새로 열었거나 psql에 다시 접속했다면 `SET search_path TO lab, hr;`부터 다시 실행하게 하세요. 테이블이 `public`에 만들어졌다는 질문이 나오면 대부분 이 원인입니다.
- 앞 교시(DML·TCL)는 `SET search_path TO bom;`으로 끝났을 수 있습니다. 1-3 전에 `hr`로 바꿨는지 확인하세요. 확인 문제는 `lab, bom`으로 바꿔 풀고 다시 `lab, hr`로 돌아옵니다.
:::

## 2. CREATE TABLE — 테이블 만들기

### 2-1. 문법 {keep}

```text CREATE TABLE의 모양
CREATE TABLE 테이블명 (
      컬럼명  자료형  [DEFAULT 기본값]  [NOT NULL]
    , 컬럼명  자료형  [DEFAULT 기본값]  [NOT NULL]
    , ...
);
```

- `[ ]`는 생략할 수 있다는 뜻입니다. 생략하면 기본값은 **NULL**, NULL 입력은 **허용**입니다.
- 컬럼은 쉼표로 구분합니다. 이 교안은 쉼표를 줄 맨 앞에 두는 방식으로 씁니다. 컬럼을 추가·삭제할 때 쉼표 실수를 줄여 줍니다.

### 2-2. PostgreSQL 자료형 — HR 데이터에 쓰인 것부터 {keep}

| 자료형 | 저장하는 값 | HR 데이터 예 |
| --- | --- | --- |
| `CHAR(n)` | **n글자 고정 길이**로 저장하는 문자 (짧은 값도 받아서 뒤를 공백으로 채움) | `countries.country_id CHAR(2)` (`US`, `UK`) |
| `VARCHAR(n)` | **최대 n글자**인 문자 | `first_name VARCHAR(20)`, `jobs.job_title VARCHAR(35)` |
| `TEXT` | 길이 제한 없는 문자 | (6장 `basis TEXT`) |
| `SMALLINT` / `INT` / `BIGINT` | 정수 (작은 / 보통 / 큰) | (2-3 `memo_id INT`, 6장 `proposal_id BIGINT`) |
| `NUMERIC(p, s)` | 전체 p자리, 소수 s자리인 **정확한** 숫자 | `employee_id NUMERIC(6)`, `salary NUMERIC(8,2)`, `commission_pct NUMERIC(2,2)` |
| `DATE` | 날짜 | `hire_date`, `start_date` |
| `TIMESTAMP` | 날짜 + 시각 | (6장 `created_at TIMESTAMP`) |
| `BOOLEAN` | 참/거짓 | — |

- 국가 코드처럼 **길이가 정해진 코드**는 `CHAR(n)`, 이름·직책명처럼 **길이가 제각각인 글**은 `VARCHAR(n)` 또는 `TEXT`를 씁니다.
- 급여·비율은 `NUMERIC`을 씁니다. 수수료율 `0.15` 같은 값을 오차 없이 저장해야 하기 때문입니다. (HR 데이터는 Oracle의 `NUMBER`를 옮겨 와 사번 같은 정수도 `NUMERIC(6)`입니다. 새로 만드는 번호 컬럼은 `INT`로 충분합니다.)

### 2-3. NOT NULL과 DEFAULT — 테이블 만들기 {keep}

직원별 면담 메모를 남기는 테이블을 만들어 봅니다. `country_id`는 희망 근무 국가 코드(`countries`와 같은 2글자)입니다.

```sql
CREATE TABLE emp_memo (
      memo_id      INT          NOT NULL
    , employee_id  INT          NOT NULL
    , country_id   CHAR(2)
    , memo         TEXT
    , writer       VARCHAR(20)  DEFAULT '미지정'
    , memo_date    DATE
);
```

```sql
SELECT table_schema, table_name
  FROM information_schema.tables
 WHERE table_name = 'emp_memo';
```

```result
| table_schema | table_name |
| --- | --- |
| lab | emp_memo |
```

`search_path` 덕분에 `lab` 스키마에 만들어졌습니다.

### 2-3. 값을 안 주면 vs NULL을 주면 {keep}

이제 행을 두 개 넣어 봅니다. (INSERT는 DML 단원에서 배운 문법입니다. 여기서는 「괄호 안 컬럼에 VALUES의 값을 순서대로 넣는다」로만 읽으세요.)

```sql
INSERT INTO emp_memo (memo_id, employee_id, country_id, memo, memo_date)
VALUES (1, 103, 'UK', '영국 지사 근무 희망', '2026-11-16');

INSERT INTO emp_memo (memo_id, employee_id, writer)
VALUES (2, 178, NULL);
```

```sql
SELECT * FROM emp_memo ORDER BY memo_id;
```

```result
| memo_id | employee_id | country_id | memo | writer | memo_date |
| --- | --- | --- | --- | --- | --- |
| 1 | 103 | UK | 영국 지사 근무 희망 | 미지정 | 2026-11-16 |
| 2 | 178 | NULL | NULL | NULL | NULL |
```

- 1번 행은 `writer`를 **아예 적지 않았으므로** 기본값 `'미지정'`이 들어갔습니다.
- 2번 행은 `writer`에 **NULL을 직접 적었으므로** NULL이 들어갔습니다. ==DEFAULT는 「값을 안 줬을 때」만 동작하고, NULL을 명시하면 NULL이 들어갑니다.==

### 2-3. NOT NULL 컬럼을 비우면 {keep}

:::error NOT NULL 컬럼을 비우면
```sql
INSERT INTO emp_memo (memo_id, memo)
VALUES (3, '사번을 빠뜨림');
```

```error
ERROR:  null value in column "employee_id" of relation "emp_memo" violates not-null constraint
DETAIL:  Failing row contains (3, null, null, 사번을 빠뜨림, 미지정, null).
```

`DETAIL`의 괄호는 **들어가려던 행 전체**입니다. 어느 컬럼이 비었는지(`employee_id` 자리가 `null`)를 바로 확인할 수 있습니다.
:::

### 2-4. 자료형의 크기를 넘으면 {keep}

:::error CHAR(n)·VARCHAR(n)보다 긴 값
```sql
INSERT INTO emp_memo (memo_id, employee_id, country_id)
VALUES (3, 103, 'USA');
```

```error
ERROR:  value too long for type character(2)
```

```sql
INSERT INTO emp_memo (memo_id, employee_id, writer)
VALUES (3, 103, 'Public Relations Representative');
```

```error
ERROR:  value too long for type character varying(20)
```

`'Public Relations Representative'`는 `jobs.job_title`에서 가장 긴 값입니다(31글자). 작성자 칸에 직책명을 적기로 했다면 `VARCHAR(20)`으로는 담을 수 없습니다(`hr_postgres.sql`은 `job_title`을 `VARCHAR(35)`로 만들었습니다). ==컬럼 크기는 「지금 떠오르는 값」이 아니라 「들어올 수 있는 가장 긴 값」 기준==으로 정합니다.
:::

### 2-4. CHAR(n)은 짧은 값을 공백으로 채웁니다 {keep}

```sql
INSERT INTO emp_memo (memo_id, employee_id, country_id)
VALUES (3, 103, 'U');
```

```sql
SELECT memo_id, country_id, length(country_id) AS len, octet_length(country_id) AS bytes
  FROM emp_memo
 WHERE memo_id = 3;
```

```result
| memo_id | country_id | len | bytes |
| --- | --- | --- | --- |
| 3 | U  | 1 | 2 |
```

1글자 `'U'`가 **오류 없이** 들어가 뒤에 공백 1칸이 채워졌습니다(저장 2바이트). `CHAR(2)`는 「2글자 이하면 받는다」이지 「2글자여야 한다」가 아닙니다.

### 2-4. 정확히 2글자인지까지 막으려면 — CHECK {keep}

국가 코드가 정확히 2글자인지까지 막으려면 3장의 **CHECK** 제약이 필요합니다.

```sql
CREATE TABLE m ( country_id CHAR(2) CONSTRAINT m_len_ck CHECK (length(country_id) = 2) );
INSERT INTO m VALUES ('U');
```

```error
ERROR:  new row for relation "m" violates check constraint "m_len_ck"
DETAIL:  Failing row contains (U ).
```

확인용 테이블 `m`은 바로 지웁니다.

```sql
DROP TABLE m;
```

### 2-4. VARCHAR(n)의 n은 바이트가 아니라 글자 수 {keep}

```sql
INSERT INTO emp_memo (memo_id, employee_id, writer)
VALUES (4, 178, '인사팀 해외 근무 담당 김부장님');
```

```sql
SELECT memo_id, writer, length(writer) AS len, octet_length(writer) AS bytes
  FROM emp_memo
 WHERE memo_id = 4;
```

```result
| memo_id | writer | len | bytes |
| --- | --- | --- | --- |
| 4 | 인사팀 해외 근무 담당 김부장님 | 17 | 43 |
```

43바이트지만 17글자이므로 `VARCHAR(20)`에 들어갑니다. 한글 이름·사유를 담을 컬럼도 **글자 수로** 크기를 정하면 됩니다.

### 2-4. NUMERIC(p, s)의 자릿수를 넘으면 {keep}

:::error NUMERIC(p, s)의 자릿수를 넘으면
`commission_pct`와 같은 `NUMERIC(2,2)` 컬럼으로 확인합니다.

```sql
CREATE TABLE pct_test ( pct NUMERIC(2,2) );

INSERT INTO pct_test VALUES (0.155);
```

```sql
INSERT INTO pct_test VALUES (1.5);
```

```error
ERROR:  numeric field overflow
DETAIL:  A field with precision 2, scale 2 must round to an absolute value less than 1.
```
:::

### 2-4. 반올림은 오류 없이 조용히 {keep}

```sql
SELECT * FROM pct_test;
```

```result
| pct |
| --- |
| 0.16 |
```

- `NUMERIC(2,2)`는 전체 2자리가 모두 소수 → **정수부는 0자리(0.99)까지**입니다. 수수료율 `1.5`(150%)는 오류입니다.
- 소수 자릿수가 넘치는 `0.155`는 오류 없이 **`0.16`으로 반올림**되어 들어갔습니다. 오류가 안 나는 쪽이 더 조심해야 할 쪽입니다.


### 2-5. 이름 규칙 {keep}

| 규칙 | 예 |
| --- | --- |
| 한 스키마 안에서 **테이블 이름은 중복 불가** | `relation "emp_memo" already exists` |
| 한 테이블 안에서 **컬럼 이름은 중복 불가** | `column "employee_id" specified more than once` |
| 문자(또는 `_`)로 시작, **예약어는 그대로 못 씀** | `order`, `select`, `table` … |
| 따옴표 없이 쓴 이름은 **소문자로 바뀜** | `Job_Info` → `job_info` |

### 2-5. 중복 이름 · 예약어 {keep}

```sql
CREATE TABLE emp_memo ( memo_id INT );
```

```error
ERROR:  relation "emp_memo" already exists
```

```sql
CREATE TABLE dup_col ( employee_id INT, employee_id TEXT );
```

```error
ERROR:  column "employee_id" specified more than once
```

```sql
CREATE TABLE order ( order_id INT );
```

```error
ERROR:  syntax error at or near "order"
LINE 1: CREATE TABLE order ( order_id INT );
                     ^
```

`ORDER BY`의 `ORDER`는 SQL 예약어라 테이블 이름으로 쓸 수 없습니다. 주문 테이블이라면 `orders`, `purchase_order`처럼 바꿉니다.

### 2-5. 대소문자는 소문자로 바뀝니다 {keep}

```sql
CREATE TABLE Job_Info ( Job_Title TEXT );
```

```sql
SELECT table_name, column_name
  FROM information_schema.columns
 WHERE table_schema = 'lab'
   AND table_name   = 'job_info';
```

```result
| table_name | column_name |
| --- | --- |
| job_info | job_title |
```

```sql
SELECT * FROM JOB_INFO;        -- 성공 (job_info로 바뀌어 찾음)
SELECT * FROM "Job_Info";      -- 실패
```

```error
ERROR:  relation "Job_Info" does not exist
LINE 1: SELECT * FROM "Job_Info";
                      ^
```

### 2-5. 큰따옴표 이름은 피합니다 {keep}

큰따옴표로 감싸면 **쓴 그대로**(대소문자, 예약어 포함) 이름이 됩니다. 그 대신 그 테이블을 쓸 때마다 매번 큰따옴표를 붙여야 합니다. ==테이블·컬럼 이름은 영문 소문자와 `_`만으로== 짓는 것이 가장 덜 헷갈립니다. HR 데이터셋(`job_history`, `department_id`)도 이 규칙을 따릅니다.

연습용으로 만든 두 테이블은 지웁니다(DROP은 5장).

```sql
DROP TABLE pct_test;
DROP TABLE job_info;
```

### 2-6. CREATE TABLE ... AS SELECT — 연습용 사본 만들기 ⭐ {keep}

`SELECT` 결과를 그대로 새 테이블로 만들 수 있습니다. 줄여서 **CTAS**라고 부릅니다. DML 단원에서 원본 대신 **사본으로 DML을 연습**할 때 쓴 방법이 이것입니다.

```text CTAS의 모양
CREATE TABLE 새테이블 AS
SELECT ... FROM 원본 [WHERE 조건];
```

```sql
CREATE TABLE t_emp AS
SELECT * FROM hr.employees;

CREATE TABLE t_dept AS
SELECT * FROM hr.departments;
```

```result
SELECT 107
SELECT 27
```

> DML·TCL 단원에서 만든 `hr.t_emp`·`hr.t_dept`와 이름은 같지만, search_path 맨 앞인 **`lab`에 새로 생기는 별개의 사본**입니다. 이제 `t_emp`라고만 쓰면 `lab.t_emp`를 가리킵니다. 그래서 이 단원에서 사본을 **지울 때는 `lab.t_emp`처럼 스키마를 붙입니다.**

### 2-6. 조건으로 고르기 · 컬럼만 고르기 {keep}

```sql
CREATE TABLE emp_ship AS
SELECT employee_id, first_name, last_name, job_id, salary, hire_date
  FROM hr.employees
 WHERE department_id = 50;
```

```sql
SELECT COUNT(*) AS cnt FROM emp_ship;
```

```result
| cnt |
| --- |
| 45 |
```

- `WHERE`로 **부서 50(Shipping)** 직원 45행만 골라 사본을 만들었습니다(4단원 1-2의 부서 50 인원과 같습니다).
- `SELECT` 목록에 적은 **6개 컬럼만** 사본에 생깁니다. 필요한 컬럼만 골라 만들 수 있습니다.

### 2-6. 구조만 복사 — WITH NO DATA {keep}

**구조만** 필요하면 `WITH NO DATA`를 붙입니다.

```sql
CREATE TABLE job_hist_empty AS
SELECT * FROM hr.job_history
WITH NO DATA;
```

```sql
SELECT COUNT(*) AS cnt FROM job_hist_empty;
```

```result
| cnt |
| --- |
| 0 |
```

### 2-6. CTAS는 제약조건을 복사하지 않습니다 ① {keep}

:::error CTAS는 제약조건을 복사하지 않습니다
원본 `employees`와 사본 `t_emp`의 제약조건을 비교합니다. (`pg_constraint`는 3-5에서 자세히 봅니다. `contype`이 p = PK, u = UNIQUE, c = CHECK, f = FK입니다.)

```sql
SELECT conrelid::regclass AS table_name, contype, COUNT(*) AS cnt
  FROM pg_constraint
 WHERE conrelid IN ('hr.employees'::regclass, 'lab.t_emp'::regclass)
   AND contype IN ('p', 'u', 'c', 'f')
 GROUP BY conrelid, contype
 ORDER BY 1, 2;
```

```result
| table_name | contype | cnt |
| --- | --- | --- |
| employees | c | 1 |
| employees | f | 3 |
| employees | p | 1 |
| employees | u | 1 |
```

사본(`t_emp`)의 행이 **하나도 없습니다.** PK도 UNIQUE도 CHECK도 FK도 없다는 뜻입니다.
:::

### 2-6. CTAS는 제약조건을 복사하지 않습니다 ② NOT NULL {keep}

NOT NULL도 따라오지 않습니다.

```sql
SELECT table_schema, table_name, column_name, is_nullable
  FROM information_schema.columns
 WHERE (table_schema, table_name) IN (('hr','employees'), ('lab','t_emp'))
   AND column_name = 'last_name'
 ORDER BY 1;
```

```result
| table_schema | table_name | column_name | is_nullable |
| --- | --- | --- | --- |
| hr | employees | last_name | NO |
| lab | t_emp | last_name | YES |
```

### 2-6. CTAS는 제약조건을 복사하지 않습니다 ③ 중복이 들어감 {keep}

그래서 원본이라면 막혔을 **중복 행**이 사본에는 그냥 들어갑니다.

```sql
INSERT INTO t_emp
SELECT * FROM hr.employees WHERE employee_id = 100;
```

```sql
SELECT employee_id, COUNT(*) AS cnt
  FROM t_emp
 GROUP BY employee_id
HAVING COUNT(*) > 1;
```

```result
| employee_id | cnt |
| --- | --- |
| 100 | 2 |
```

CTAS는 ==데이터와 컬럼(이름·자료형)만 복사==합니다. 사본에도 규칙이 필요하면 3장의 방법으로 제약조건을 다시 걸어야 합니다(3-6에서 이 중복 때문에 PK가 실패하는 것을 봅니다).

### 2-7. 확인 문제 — 회원 테이블 · 생산 데이터 {keep}

> 실행 전: `SET search_path TO lab, bom;` (생산 실습 데이터 `bom` 스키마. 테이블은 `lab`에 만들어집니다.)

:::try
**[복습]** 아래 조건으로 회원 테이블 `member`를 만들고, 이름 없이 회원 한 명(`'kim01'`, 비밀번호 `'pw1234'`)을 넣었을 때 어떤 오류가 나는지 확인하세요. 그다음 `'kim01'`을 이름 `'김생산'`, 성별 `'남'`으로 다시 넣으세요. 이번에는 이름과 성별만 넣습니다(비밀번호는 생략).

| 컬럼 | 자료형 | 조건 |
| --- | --- | --- |
| `member_id` | 가변 문자 15글자 | |
| `member_name` | 가변 문자 12글자 | NULL 불가 |
| `passwd` | 가변 문자 16글자 | |
| `birth_date` | 날짜 | |
| `gender` | 가변 문자 3글자 | |

**[응용]** `bom_structure`에서 **세탁기(`TWM61868701`)** BOM 행만 골라 `bom_wm` 사본을 만드세요. 몇 행인지 확인하고, 원본 `bom_structure`와 사본 `bom_wm` 중 **PK가 있는 테이블**을 `pg_constraint`로 확인하세요.
:::

### 2-7. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
```sql
CREATE TABLE member (
      member_id    VARCHAR(15)
    , member_name  VARCHAR(12)  NOT NULL
    , passwd       VARCHAR(16)
    , birth_date   DATE
    , gender       VARCHAR(3)
);

INSERT INTO member (member_id, passwd) VALUES ('kim01', 'pw1234');
```

```error
ERROR:  null value in column "member_name" of relation "member" violates not-null constraint
DETAIL:  Failing row contains (kim01, null, pw1234, null, null).
```

```sql
INSERT INTO member (member_id, member_name, gender) VALUES ('kim01', '김생산', '남');

SELECT * FROM member;
```

```result
| member_id | member_name | passwd | birth_date | gender |
| --- | --- | --- | --- | --- |
| kim01 | 김생산 | NULL | NULL | 남 |
```

PostgreSQL의 `VARCHAR(12)`는 12바이트가 아니라 **12글자**까지 받습니다(2-4).
:::

### 2-7. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
43행. PK는 원본에만 있습니다.

```sql
CREATE TABLE bom_wm AS
SELECT *
  FROM bom.bom_structure
 WHERE model_part_no = 'TWM61868701';

SELECT COUNT(*) AS cnt FROM bom_wm;
```

```result
| cnt |
| --- |
| 43 |
```

```sql
SELECT conrelid::regclass AS table_name, conname, contype
  FROM pg_constraint
 WHERE conrelid IN ('bom.bom_structure'::regclass, 'lab.bom_wm'::regclass)
   AND contype = 'p';
```

```result
| table_name | conname | contype |
| --- | --- | --- |
| bom_structure | bom_structure_pkey | p |
```
:::

> 확인 문제를 마치면 `SET search_path TO lab, hr;`으로 돌아옵니다.

## 3. 제약조건 — 잘못된 데이터가 들어오지 못하게

### 3-1. 제약조건 다섯 가지 {keep}

**제약조건(constraint)** 은 테이블에 들어올 수 있는 값을 제한하는 **규칙**입니다. 규칙을 어기는 INSERT·UPDATE·DELETE는 DB가 오류로 거부합니다.

| 제약조건 | 규칙 | HR 데이터 예 |
| --- | --- | --- |
| `PRIMARY KEY` (PK) | **NULL 불가 + 중복 불가.** 행을 구별하는 식별자 | `employees.employee_id`, `job_history (employee_id, start_date)` |
| `UNIQUE` (UK) | **중복 불가.** NULL은 허용 | `employees.email` |
| `NOT NULL` | NULL 불가 | `employees.last_name` |
| `CHECK` | **조건식이 참인 값만** 허용 | `employees`의 `salary > 0`, `job_history`의 `end_date > start_date` |
| `FOREIGN KEY` (FK) | **다른 테이블(부모)에 있는 값만** 허용 | `employees.department_id → departments.department_id` |

### 3-1. 무결성 {keep}

제약조건이 지켜 주는 것을 **무결성(integrity)**, 즉 「데이터에 결함이 없는 상태」라고 합니다.

| 무결성 | 뜻 | 지켜 주는 제약조건 |
| --- | --- | --- |
| 개체 무결성 | 기본키는 NULL일 수 없다 (모든 행은 구별될 수 있어야 한다) | PK |
| 참조 무결성 | 외래키는 부모에 없는 값을 가질 수 없다 | FK |

### 3-2. 제약조건을 거는 세 가지 위치 {keep}

```sql
-- ① 컬럼 옆에 (컬럼 레벨)
train_id  INT  CONSTRAINT training_pk PRIMARY KEY

-- ② 컬럼 목록 끝에 (테이블 레벨) — 여러 컬럼을 묶을 때는 이 방법만 가능
, CONSTRAINT training_hours_ck CHECK (total_hours > 0 AND absent_hours BETWEEN 0 AND total_hours)

-- ③ 테이블을 만든 뒤에 (ALTER TABLE)
ALTER TABLE 테이블명 ADD CONSTRAINT 제약조건명 제약조건 (컬럼);
```

- `CONSTRAINT 이름`을 생략하면 PostgreSQL이 이름을 자동으로 붙입니다(`training_pkey`, `training_employee_id_fkey` …). 오류 메시지에는 **제약조건 이름**이 나오므로, 직접 만드는 테이블은 ==「테이블_컬럼_종류」(예: `training_result_ck`)처럼 읽으면 뜻이 보이는 이름==을 붙입니다. PK처럼 테이블에 하나뿐인 것은 컬럼을 생략하기도 합니다(`training_pk`). HR 원본도 `emp_emp_id_pk`, `emp_dept_fk`처럼 이름을 직접 붙였습니다(1-2).
- 이 교안의 접미사: `_pk`(기본키), `_uk`(유니크), `_ck`(체크), `_fk`(외래키)

### 3-3. 교육 이수 테이블 만들기 {keep}

직원의 **사내 교육 이수 결과**를 기록하는 테이블을 만들어 봅니다. 교육을 주관한 부서는 2-6에서 만든 `t_dept`를 참조하도록 했습니다. FK 컬럼은 부모 컬럼과 같은 자료형(`NUMERIC(6)`, `NUMERIC(4)`)으로 만듭니다.

```sql
CREATE TABLE training (
      train_id       INT          CONSTRAINT training_pk PRIMARY KEY
    , cert_no        VARCHAR(20)  CONSTRAINT training_cert_uk UNIQUE
    , employee_id    NUMERIC(6)   NOT NULL
    , department_id  NUMERIC(4)   NOT NULL
    , train_date     DATE         NOT NULL
    , total_hours    INT          NOT NULL
    , absent_hours   INT          NOT NULL DEFAULT 0
    , result         VARCHAR(4)   NOT NULL
    , CONSTRAINT training_emp_fk    FOREIGN KEY (employee_id)   REFERENCES hr.employees (employee_id)
    , CONSTRAINT training_dept_fk   FOREIGN KEY (department_id) REFERENCES t_dept (department_id)
    , CONSTRAINT training_result_ck CHECK (result IN ('PASS', 'FAIL', 'HOLD'))
    , CONSTRAINT training_hours_ck  CHECK (total_hours > 0 AND absent_hours BETWEEN 0 AND total_hours)
);
```

```error
ERROR:  there is no unique constraint matching given keys for referenced table "t_dept"
```

### 3-3. FK는 PK(또는 UNIQUE)를 가리켜야 한다 {keep}

`t_dept`는 CTAS 사본이라 **PK가 없습니다**(2-6). FK가 가리키는 부모 컬럼은 ==PK 또는 UNIQUE여야== 합니다. 부모 값이 중복될 수 있으면 「어느 부모 행을 가리키는지」가 정해지지 않기 때문입니다. 사본에 PK를 먼저 겁니다(위치 ③).

```sql
ALTER TABLE t_dept ADD CONSTRAINT t_dept_pk PRIMARY KEY (department_id);
```

같은 `CREATE TABLE training (...)` 문장을 다시 실행하면 이번에는 성공합니다.

### 3-4. 정상 행 넣기 {keep}

```sql
INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours, absent_hours, result)
VALUES (1, 'C2611-0401', 103, 60, '2026-11-04', 16, 0, 'PASS');

INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours, absent_hours, result)
VALUES (2, 'C2611-0501', 132, 40, '2026-11-05', 8, 2, 'PASS');
```

```sql
SELECT * FROM training ORDER BY train_id;
```

```result
| train_id | cert_no | employee_id | department_id | train_date | total_hours | absent_hours | result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | C2611-0401 | 103 | 60 | 2026-11-04 | 16 | 0 | PASS |
| 2 | C2611-0501 | 132 | 40 | 2026-11-05 | 8 | 2 | PASS |
```

> 사번·부서 번호는 HR 데이터에 실제로 있는 값이고, 수료증 번호·교육 시간은 **연습용으로 만든 값**입니다.

### 3-4. PRIMARY KEY — 중복도, NULL도 안 됨 {keep}

```sql
INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours, result)
VALUES (1, 'C2611-0801', 178, 40, '2026-11-08', 8, 'PASS');
```

```error
ERROR:  duplicate key value violates unique constraint "training_pk"
DETAIL:  Key (train_id)=(1) already exists.
```

```sql
INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours, result)
VALUES (NULL, 'C2611-0801', 178, 40, '2026-11-08', 8, 'PASS');
```

```error
ERROR:  null value in column "train_id" of relation "training" violates not-null constraint
DETAIL:  Failing row contains (null, C2611-0801, 178, 40, 2026-11-08, 8, 0, PASS).
```

`train_id`에 `NOT NULL`을 따로 쓰지 않았는데도 NULL이 거부됐습니다. ==PK = NOT NULL + UNIQUE==이기 때문입니다.

### 3-4. UNIQUE — 중복은 안 되지만 NULL은 여러 개 가능 {keep}

```sql
INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours, result)
VALUES (3, 'C2611-0501', 178, 40, '2026-11-08', 8, 'PASS');
```

```error
ERROR:  duplicate key value violates unique constraint "training_cert_uk"
DETAIL:  Key (cert_no)=(C2611-0501) already exists.
```

```sql
INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours, result)
VALUES (3, NULL, 178, 40, '2026-11-08', 8, 'PASS');

INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours, result)
VALUES (4, NULL, 200, 10, '2026-11-10', 4, 'HOLD');
```

### 3-4. NULL 수료증 번호 두 개가 들어갔습니다 {keep}

```sql
SELECT train_id, cert_no, employee_id, absent_hours, result FROM training ORDER BY train_id;
```

```result
| train_id | cert_no | employee_id | absent_hours | result |
| --- | --- | --- | --- | --- |
| 1 | C2611-0401 | 103 | 0 | PASS |
| 2 | C2611-0501 | 132 | 2 | PASS |
| 3 | NULL | 178 | 0 | PASS |
| 4 | NULL | 200 | 0 | HOLD |
```

- 수료증 번호가 없는(NULL, 아직 발급 전) 행이 두 개 들어갔습니다. NULL은 「값이 없음」이라 서로 **같다고 보지 않기** 때문입니다(3단원 5-1).
- `absent_hours`를 적지 않은 3·4번 행에는 `DEFAULT 0`이 들어갔습니다.

### 3-4. CHECK — 조건식이 참이어야 함 {keep}

```sql
INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours, result)
VALUES (5, 'C2611-1201', 145, 80, '2026-11-12', 12, 'OK');
```

```error
ERROR:  new row for relation "training" violates check constraint "training_result_ck"
DETAIL:  Failing row contains (5, C2611-1201, 145, 80, 2026-11-12, 12, 0, OK).
```

```sql
INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours, absent_hours, result)
VALUES (5, 'C2611-1201', 145, 80, '2026-11-12', 12, 15, 'FAIL');
```

```error
ERROR:  new row for relation "training" violates check constraint "training_hours_ck"
DETAIL:  Failing row contains (5, C2611-1201, 145, 80, 2026-11-12, 12, 15, FAIL).
```

총 12시간 교육에서 결석 15시간은 나올 수 없습니다. `training_hours_ck`처럼 ==컬럼 두 개를 비교하는 규칙==은 테이블 레벨(위치 ②)로 씁니다.

### 3-4. FOREIGN KEY — 부모에 있는 값만 {keep}

```sql
INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours, result)
VALUES (5, 'C2611-1201', 1450, 80, '2026-11-12', 12, 'PASS');
```

```error
ERROR:  insert or update on table "training" violates foreign key constraint "training_emp_fk"
DETAIL:  Key (employee_id)=(1450) is not present in table "employees".
```

```sql
INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours, result)
VALUES (5, 'C2611-1201', 145, 800, '2026-11-12', 12, 'PASS');
```

```error
ERROR:  insert or update on table "training" violates foreign key constraint "training_dept_fk"
DETAIL:  Key (department_id)=(800) is not present in table "t_dept".
```

사번 오타(145 → 1450), 없는 부서 번호(800)가 **기록되는 순간** 막힙니다. 5단원에서 LEFT JOIN으로 찾던 「짝 없는 행」이 처음부터 생기지 않게 하는 것이 FK입니다.

### 3-4. FK는 부모 쪽 삭제도 막습니다 {keep}

```sql
DELETE FROM t_dept WHERE department_id = 40;
```

```error
ERROR:  update or delete on table "t_dept" violates foreign key constraint "training_dept_fk" on table "training"
DETAIL:  Key (department_id)=(40) is still referenced from table "training".
```

교육 기록(자식)이 남아 있는 부서(부모)를 지우면, 그 기록은 「존재하지 않는 부서가 주관한 교육」이 됩니다. 이것이 **참조 무결성**입니다. (`ON DELETE` 옵션을 따로 주지 않았을 때의 기본 동작입니다.)

### 3-5. 걸려 있는 제약조건 조회하기 {keep}

```sql
SELECT conname, contype, pg_get_constraintdef(oid) AS definition
  FROM pg_constraint
 WHERE conrelid = 'lab.training'::regclass
   AND contype IN ('p', 'u', 'c', 'f')
 ORDER BY contype, conname;
```

```result
| conname | contype | definition |
| --- | --- | --- |
| training_hours_ck | c | CHECK (((total_hours > 0) AND ((absent_hours >= 0) AND (absent_hours <= total_hours)))) |
| training_result_ck | c | CHECK (((result)::text = ANY ((ARRAY['PASS'::character varying, 'FAIL'::character varying, 'HOLD'::character varying])::text[]))) |
| training_dept_fk | f | FOREIGN KEY (department_id) REFERENCES t_dept(department_id) |
| training_emp_fk | f | FOREIGN KEY (employee_id) REFERENCES employees(employee_id) |
| training_pk | p | PRIMARY KEY (train_id) |
| training_cert_uk | u | UNIQUE (cert_no) |
```

### 3-5. contype 읽기 {keep}

| `contype` | 뜻 |
| --- | --- |
| `p` | PRIMARY KEY |
| `u` | UNIQUE |
| `c` | CHECK |
| `f` | FOREIGN KEY |

- `pg_get_constraintdef`는 PostgreSQL이 내부적으로 정리한 형태로 보여 줍니다. `BETWEEN`은 `>= AND <=`로, `IN (...)`은 `= ANY (ARRAY[...])`로 바뀌어 보이지만 뜻은 같습니다.
- `NOT NULL`은 PostgreSQL 16까지는 이 목록에 없고, PostgreSQL 18에서는 `contype = 'n'`으로 함께 나옵니다. 이 교안은 버전에 상관없이 같은 결과가 나오도록 `contype IN ('p', 'u', 'c', 'f')`로 4종만 조회합니다. NOT NULL 여부는 1-3의 `information_schema.columns.is_nullable`로 확인합니다.

### 3-6. 제약조건 = 데이터 품질 규칙 ⭐ {keep}

쿼리로 찾던 「확인이 필요한 데이터」를, 이번에는 **규칙(제약조건)을 걸어서** 찾아봅니다. 원본을 건드리지 않도록 2-6에서 만든 **사본**에 겁니다.

```icons 세 가지 규칙
dollar-sign | ① CHECK | 급여는 2,500 이상이어야 한다 | rose
building-2 | ② NOT NULL | 모든 직원은 부서가 있어야 한다 | plum
key-round | ③ PRIMARY KEY | 사번은 하나여야 한다 | lime
```

### 3-6. ① 급여는 2,500 이상이어야 한다 {keep}

물류 부서 사본 `emp_ship`에 「급여 2,500 이상」(연습용 사내 규정)을 겁니다.

```sql
ALTER TABLE emp_ship ADD CONSTRAINT emp_ship_sal_ck CHECK (salary >= 2500);
```

```error
ERROR:  check constraint "emp_ship_sal_ck" of relation "emp_ship" is violated by some row
```

제약조건을 **나중에** 걸면, PostgreSQL은 이미 들어 있는 행을 모두 검사합니다. 한 행이라도 어기면 제약조건 자체가 만들어지지 않습니다. 어긴 행은 조건을 뒤집어 찾습니다.

### 3-6. ① 규칙을 어기는 직원 찾기 {keep}

```sql
SELECT employee_id, first_name, last_name, job_id, salary
  FROM emp_ship
 WHERE NOT (salary >= 2500)
 ORDER BY salary, employee_id;
```

```result
| employee_id | first_name | last_name | job_id | salary |
| --- | --- | --- | --- | --- |
| 132 | TJ | Olson | ST_CLERK | 2100.00 |
| 128 | Steven | Markle | ST_CLERK | 2200.00 |
| 136 | Hazel | Philtanker | ST_CLERK | 2200.00 |
| 127 | James | Landry | ST_CLERK | 2400.00 |
| 135 | Ki | Gee | ST_CLERK | 2400.00 |
```

창고 사원(ST_CLERK) 5명입니다. `jobs`에 정해진 ST_CLERK 급여 범위(2,008~5,000) 안이라 원본이 틀린 값은 아닙니다. ==규칙 실패는 「확인할 대상을 찾았다」는 뜻이고, 데이터와 규칙 중 무엇을 고칠지는 사람이 판단합니다.== (6장에서 이 판단을 기록합니다.)

### 3-6. ② 모든 직원은 부서가 있어야 한다 {keep}

```sql
ALTER TABLE t_emp ALTER COLUMN department_id SET NOT NULL;
```

```error
ERROR:  column "department_id" of relation "t_emp" contains null values
```

```sql
SELECT employee_id, first_name, last_name, job_id, department_id
  FROM t_emp
 WHERE department_id IS NULL;
```

```result
| employee_id | first_name | last_name | job_id | department_id |
| --- | --- | --- | --- | --- |
| 178 | Kimberely | Grant | SA_REP | NULL |
```

5단원 3-3 ②에서 LEFT JOIN으로 찾은 부서 없는 직원입니다. 원본 `employees`에는 부서 FK(`emp_dept_fk`)가 있는데도 이 행이 들어 있습니다. ==FK는 NULL을 검사하지 않습니다==(「부모를 가리키지 않음」으로 봄). 부서가 반드시 있어야 한다면 `NOT NULL`을 따로 걸어야 합니다.

### 3-6. ③ 사번은 하나여야 한다 {keep}

```sql
ALTER TABLE t_emp ADD CONSTRAINT t_emp_pk PRIMARY KEY (employee_id);
```

```error
ERROR:  could not create unique index "t_emp_pk"
DETAIL:  Key (employee_id)=(100) is duplicated.
```

2-6에서 사본에 일부러 넣은 중복 행(100번 Steven King) 때문입니다. 원본 `employees`에는 PK가 있어 이런 중복이 들어갈 수 없습니다.

### 3-6. 쿼리 점검은 사후에, 제약조건은 들어오는 순간 {keep}

| 원본 `hr`에 이 규칙이 있었다면 | 막혔을 데이터 | 처음 찾은 곳 |
| --- | --- | --- |
| `CHECK (salary >= 2500)` | 급여 2,500 미만 직원 5명 (규칙 자체를 검토할 대상) | 3-6 ① |
| `department_id NOT NULL` | 부서 없는 직원 178 | 5단원 3-3 ② |
| PK `employee_id` | 같은 사번 중복 (원본에는 PK가 있어 없음) | — |

==쿼리로 하는 품질 점검은 「이미 들어온 데이터」를 사후에 찾고, 제약조건은 「들어오는 순간」 막습니다.== 그래서 판단 결과를 기록하는 테이블(6장)을 만들 때는 처음부터 제약조건을 함께 설계합니다.

### 3-6. 사본 정리 — 다시 만들고 PK 걸기 {keep}

중복이 들어간 사본은 지우고 다시 만든 뒤 PK를 겁니다. 지울 때는 스키마를 붙입니다(2-6).

```sql
DROP TABLE lab.t_emp;

CREATE TABLE t_emp AS
SELECT * FROM hr.employees;

ALTER TABLE t_emp
  ADD CONSTRAINT t_emp_pk PRIMARY KEY (employee_id);
```

이번에는 오류 없이 만들어집니다.

### 3-6. 앞으로 들어올 행만 막기 — NOT VALID {keep}

현장 DB에서는 「기존 데이터는 담당 부서가 검토 중이니, 일단 **새로 들어오는 것만** 막자」는 경우가 있습니다. `CHECK`와 `FOREIGN KEY`는 `NOT VALID`를 붙이면 기존 행 검사를 건너뜁니다.

```sql
ALTER TABLE emp_ship ADD CONSTRAINT emp_ship_sal_ck CHECK (salary >= 2500) NOT VALID;
```

```sql
INSERT INTO emp_ship (employee_id, first_name, last_name, job_id, salary, hire_date)
VALUES (300, 'Gildong', 'Hong', 'ST_CLERK', 2000, '2026-12-01');
```

```error
ERROR:  new row for relation "emp_ship" violates check constraint "emp_ship_sal_ck"
DETAIL:  Failing row contains (300, Gildong, Hong, ST_CLERK, 2000.00, 2026-12-01).
```

### 3-6. convalidated와 VALIDATE CONSTRAINT {keep}

```sql
SELECT conname, convalidated FROM pg_constraint WHERE conname = 'emp_ship_sal_ck';
```

```result
| conname | convalidated |
| --- | --- |
| emp_ship_sal_ck | f |
```

- 새 행(급여 2,000)은 막혔습니다. `convalidated = f`는 「기존 행은 아직 검증하지 않았다」는 표시입니다.
- 기존 행 정리가 끝나면 `VALIDATE CONSTRAINT`로 검증을 완료합니다. 아직 급여 2,500 미만인 5명이 남아 있으므로 지금은 실패합니다.

```sql
ALTER TABLE emp_ship VALIDATE CONSTRAINT emp_ship_sal_ck;
```

```error
ERROR:  check constraint "emp_ship_sal_ck" of relation "emp_ship" is violated by some row
```

:::teacher 강사 확인
- ①의 「급여 2,500 이상」은 HR 원본 규칙이 아니라 **연습용 규정**입니다. `jobs`의 ST_CLERK 범위(2,008~5,000) 안이므로 「원본 데이터 오류」라고 말하지 마세요. 「규칙을 걸어 보니 검토할 대상이 나왔다 → 규칙을 고칠지, 급여를 고칠지는 사람이 판단」으로 연결하면 6장(판단 기록)으로 자연스럽게 이어집니다.
- ②의 178번(Kimberely Grant)은 5단원 3-3 ②와 같은 행입니다. FK가 있는데도 NULL이 들어간 이유(FK는 NULL을 검사하지 않음)를 꼭 짚어 주세요.
- `NOT VALID`는 PostgreSQL 16에서는 **CHECK·FK에만** 쓸 수 있습니다. PostgreSQL 18부터는 NOT NULL에도 쓸 수 있습니다(`ALTER TABLE … ADD CONSTRAINT 이름 NOT NULL 컬럼 NOT VALID`, 18.7에서 확인). 이 교안은 두 버전에 공통인 CHECK만 다룹니다.
- 원본 `hr`·`bom` 테이블에 제약조건을 추가하는 것은 이 수업 범위가 아닙니다. 「현장에서는 DBA·담당 부서 승인 후 진행」으로 정리하세요.
:::

### 3-7. 확인 문제 — 블로그 테이블 · 생산 데이터 {keep}

> 실행 전: `SET search_path TO lab, bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** (2-7에서 만든 `member` 테이블과 `'kim01'` 회원이 있어야 합니다.) 블로그 테이블 `blog`를 아래 구조로 만들고, 제약조건 4개를 `ALTER TABLE ... ADD CONSTRAINT`로 추가하세요. 그다음 ① 성별이 `'M'`인 회원 `'lee02'`(이름 `'이품질'`), ② 없는 회원 `'park03'`의 글, ③ `'kim01'`의 글(1번, 제목 `'첫 글'`)을 차례로 넣어 결과를 확인하세요.

| 컬럼 | 자료형 | 조건 |
| --- | --- | --- |
| `blog_no` | 정수 | |
| `title` | 가변 문자 100글자 | NULL 불가 |
| `content` | 가변 문자 4000글자 | |
| `member_id` | 가변 문자 15글자 | |

| 제약조건 이름 | 내용 |
| --- | --- |
| `member_id_pk` | `member.member_id` PK |
| `member_gender_ck` | `member.gender`는 `'남'`, `'여'`만 |
| `blog_no_pk` | `blog.blog_no` PK |
| `blog_member_fk` | `blog.member_id`는 `member.member_id` 참조 |

**[응용]** (2-7 [응용]의 `bom_wm`이 있어야 합니다.) `bom_wm`에 「소요량은 0보다 커야 한다」 CHECK(`bom_wm_qty_ck`)를 추가하세요. 실패한다면 **규칙을 어기는 행**을 찾고, 기존 행은 그대로 둔 채 **새 행부터** 규칙을 적용한 뒤 소요량 0인 행(`bom_id` 999, DD모터 `EMT68237401` 아래 `FSC33042701`, 레벨 3)을 넣어 막히는지 확인하세요. 마지막으로 `bom_id` PK(`bom_wm_pk`)와 `child_part_no` → `bom.part_master` FK(`bom_wm_child_fk`)도 추가하세요.
:::

### 3-7. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
```sql
CREATE TABLE blog (
      blog_no    INT
    , title      VARCHAR(100)  NOT NULL
    , content    VARCHAR(4000)
    , member_id  VARCHAR(15)
);

ALTER TABLE member ADD CONSTRAINT member_id_pk     PRIMARY KEY (member_id);
ALTER TABLE member ADD CONSTRAINT member_gender_ck CHECK (gender IN ('남', '여'));
ALTER TABLE blog   ADD CONSTRAINT blog_no_pk       PRIMARY KEY (blog_no);
ALTER TABLE blog   ADD CONSTRAINT blog_member_fk   FOREIGN KEY (member_id) REFERENCES member (member_id);
```

```sql
INSERT INTO member (member_id, member_name, gender) VALUES ('lee02', '이품질', 'M');
```

```error
ERROR:  new row for relation "member" violates check constraint "member_gender_ck"
DETAIL:  Failing row contains (lee02, 이품질, null, null, M).
```

```sql
INSERT INTO blog (blog_no, title, member_id) VALUES (1, '첫 글', 'park03');
```

```error
ERROR:  insert or update on table "blog" violates foreign key constraint "blog_member_fk"
DETAIL:  Key (member_id)=(park03) is not present in table "member".
```

```sql
INSERT INTO blog (blog_no, title, member_id) VALUES (1, '첫 글', 'kim01');   -- 성공
```
:::

### 3-7. 확인 문제 답 — 응용 ① 규칙을 어기는 행 {keep}

:::answer [응용] 예시 답안 ①
규칙을 어기는 행은 1행입니다.

```sql
ALTER TABLE bom_wm ADD CONSTRAINT bom_wm_qty_ck CHECK (qty_per > 0);
```

```error
ERROR:  check constraint "bom_wm_qty_ck" of relation "bom_wm" is violated by some row
```

```sql
SELECT bom_id, parent_part_no, child_part_no, qty_per
  FROM bom_wm
 WHERE NOT (qty_per > 0);
```

```result
| bom_id | parent_part_no | child_part_no | qty_per |
| --- | --- | --- | --- |
| 70 | EMT68237401 | FSC67181101 | 0.000 |
```

DD모터(`EMT68237401`) 아래 나사 M4(`FSC67181101`)의 소요량이 **0**입니다. Day 1 7교시에 `WHERE qty_per <= 0`으로 찾았던 행입니다.
:::

### 3-7. 확인 문제 답 — 응용 ② 새 행부터 · PK · FK {keep}

:::answer [응용] 예시 답안 ②
```sql
ALTER TABLE bom_wm ADD CONSTRAINT bom_wm_qty_ck CHECK (qty_per > 0) NOT VALID;

INSERT INTO bom_wm (bom_id, model_part_no, parent_part_no, child_part_no, bom_level, qty_per)
VALUES (999, 'TWM61868701', 'EMT68237401', 'FSC33042701', 3, 0);
```

```error
ERROR:  new row for relation "bom_wm" violates check constraint "bom_wm_qty_ck"
DETAIL:  Failing row contains (999, TWM61868701, EMT68237401, FSC33042701, 3, 0.000, null, null, null, null).
```

```sql
ALTER TABLE bom_wm ADD CONSTRAINT bom_wm_pk       PRIMARY KEY (bom_id);
ALTER TABLE bom_wm ADD CONSTRAINT bom_wm_child_fk FOREIGN KEY (child_part_no) REFERENCES bom.part_master (part_no);

SELECT conname, contype, convalidated
  FROM pg_constraint
 WHERE conrelid = 'lab.bom_wm'::regclass
   AND contype IN ('p', 'u', 'c', 'f')
 ORDER BY contype, conname;
```

```result
| conname | contype | convalidated |
| --- | --- | --- |
| bom_wm_qty_ck | c | f |
| bom_wm_child_fk | f | t |
| bom_wm_pk | p | t |
```

PK·FK는 바로 성공합니다(`bom_id` 중복 없음, 부모 `part_master.part_no`는 PK — 3-3). CHECK만 `convalidated = f`로 남습니다. `bom_id` 70을 정리해야 `VALIDATE CONSTRAINT`가 통과합니다.
:::

> 확인 문제를 마치면 `SET search_path TO lab, hr;`으로 돌아옵니다.

## 4. ALTER TABLE — 만든 테이블 고치기

### 4-1. 문법 한눈에 보기 {keep}

| 하고 싶은 일 | 문법 |
| --- | --- |
| 컬럼 추가 | `ALTER TABLE 테이블 ADD COLUMN 컬럼 자료형 [DEFAULT …] [NOT NULL];` |
| 컬럼 삭제 | `ALTER TABLE 테이블 DROP COLUMN 컬럼;` |
| 자료형 변경 | `ALTER TABLE 테이블 ALTER COLUMN 컬럼 TYPE 새자료형;` |
| 기본값 설정 / 해제 | `ALTER TABLE 테이블 ALTER COLUMN 컬럼 SET DEFAULT 값;` / `DROP DEFAULT;` |
| NOT NULL 설정 / 해제 | `ALTER TABLE 테이블 ALTER COLUMN 컬럼 SET NOT NULL;` / `DROP NOT NULL;` |
| 컬럼 이름 변경 | `ALTER TABLE 테이블 RENAME COLUMN 옛이름 TO 새이름;` |
| 테이블 이름 변경 | `ALTER TABLE 옛이름 RENAME TO 새이름;` |
| 제약조건 추가 / 삭제 | `ALTER TABLE 테이블 ADD CONSTRAINT 이름 …;` / `DROP CONSTRAINT 이름;` |

### 4-2. 컬럼 추가 {keep}

3장의 `training`에 강사와 판단 주체 컬럼을 추가합니다.

```sql
ALTER TABLE training ADD COLUMN instructor VARCHAR(30);
ALTER TABLE training ADD COLUMN judged_by VARCHAR(5) NOT NULL DEFAULT 'HUMAN';
```

```sql
SELECT train_id, result, instructor, judged_by FROM training ORDER BY train_id;
```

```result
| train_id | result | instructor | judged_by |
| --- | --- | --- | --- |
| 1 | PASS | NULL | HUMAN |
| 2 | PASS | NULL | HUMAN |
| 3 | PASS | NULL | HUMAN |
| 4 | HOLD | NULL | HUMAN |
```

- 기본값 없이 추가한 `instructor`는 기존 행이 모두 **NULL**입니다.
- `DEFAULT 'HUMAN'`과 함께 추가한 `judged_by`는 ==기존 행에도 기본값이 채워졌습니다.== 지금까지의 이수 판정은 사람이 내린 것이라는 뜻으로 남길 수 있습니다.

### 4-2. 기본값 없는 NOT NULL 컬럼 추가 {keep}

:::error 데이터가 있는 테이블에 「기본값 없는 NOT NULL」 컬럼 추가
```sql
ALTER TABLE training ADD COLUMN remark TEXT NOT NULL;
```

```error
ERROR:  column "remark" of relation "training" contains null values
```

새 컬럼은 기존 행에서 NULL로 시작하는데, 동시에 NOT NULL을 요구하니 모순입니다. **`DEFAULT`를 함께 주거나**, NULL 허용으로 추가한 뒤 값을 채우고(DML) 나서 `SET NOT NULL`을 겁니다.
:::

### 4-3. 자료형 변경 — 줄이기와 늘리기 {keep}

:::error 들어 있는 값보다 작게 줄이기
```sql
ALTER TABLE training ALTER COLUMN cert_no TYPE VARCHAR(8);
```

```error
ERROR:  value too long for type character varying(8)
```

수료증 번호 `'C2611-0401'`(10글자)이 들어 있어 8글자로 줄일 수 없습니다. 늘리는 것은 문제없습니다.
:::

```sql
ALTER TABLE training ALTER COLUMN cert_no TYPE VARCHAR(30);
```

### 4-3. 기본값 설정 {keep}

판정을 적지 않으면 `'HOLD'`(보류)로 기록되게 합니다.

```sql
ALTER TABLE training ALTER COLUMN result SET DEFAULT 'HOLD';

INSERT INTO training (train_id, cert_no, employee_id, department_id, train_date, total_hours)
VALUES (5, 'C2611-1201', 145, 80, '2026-11-12', 12);
```

```sql
SELECT train_id, cert_no, result, judged_by FROM training WHERE train_id = 5;
```

```result
| train_id | cert_no | result | judged_by |
| --- | --- | --- | --- |
| 5 | C2611-1201 | HOLD | HUMAN |
```

> 「판정을 안 적으면 이수(PASS)」보다 「판정을 안 적으면 보류」가 안전합니다. ==기본값은 「실수했을 때 덜 위험한 값」== 으로 정합니다.

### 4-3. NOT NULL 설정 / 해제 {keep}

```sql
ALTER TABLE training ALTER COLUMN cert_no SET NOT NULL;
```

```error
ERROR:  column "cert_no" of relation "training" contains null values
```

3-4에서 수료증 번호 없이 넣은 3·4번 행 때문입니다. 3-6 ②(`department_id`)와 같은 오류입니다.

```sql
ALTER TABLE training ALTER COLUMN instructor DROP NOT NULL;
```

`instructor`는 처음부터 NULL 허용이라 바뀌는 것이 없지만, 문법은 이렇게 씁니다.

### 4-4. 컬럼 이름 변경 {keep}

```sql
ALTER TABLE training RENAME COLUMN result TO train_result;
```

```sql
SELECT conname, pg_get_constraintdef(oid) AS definition
  FROM pg_constraint
 WHERE conname = 'training_result_ck';
```

```result
| conname | definition |
| --- | --- |
| training_result_ck | CHECK (((train_result)::text = ANY ((ARRAY['PASS'::character varying, 'FAIL'::character varying, 'HOLD'::character varying])::text[]))) |
```

컬럼 이름을 바꾸면 그 컬럼에 걸린 **CHECK 조건식도 새 이름으로 따라 바뀝니다.** 다만 제약조건 **이름**(`training_result_ck`)은 그대로입니다. 그 컬럼을 쓰던 **SELECT 쿼리는 자동으로 바뀌지 않으므로** 직접 고쳐야 합니다.

### 4-4. 컬럼 삭제 · 테이블 이름 변경 {keep}

```sql
ALTER TABLE training DROP COLUMN instructor;
ALTER TABLE training RENAME TO edu_record;
```

### 4-4. 바뀐 구조 확인 {keep}

```sql
SELECT column_name, data_type, character_maximum_length AS max_len, is_nullable, column_default
  FROM information_schema.columns
 WHERE table_schema = 'lab'
   AND table_name   = 'edu_record'
 ORDER BY ordinal_position;
```

```result
| column_name | data_type | max_len | is_nullable | column_default |
| --- | --- | --- | --- | --- |
| train_id | integer | NULL | NO | NULL |
| cert_no | character varying | 30 | YES | NULL |
| employee_id | numeric | NULL | NO | NULL |
| department_id | numeric | NULL | NO | NULL |
| train_date | date | NULL | NO | NULL |
| total_hours | integer | NULL | NO | NULL |
| absent_hours | integer | NULL | NO | 0 |
| train_result | character varying | 4 | NO | 'HOLD'::character varying |
| judged_by | character varying | 5 | NO | 'HUMAN'::character varying |
```

4장에서 바꾼 것(추가 `judged_by`, 삭제 `instructor`, 길이 `cert_no` 30, 이름 `train_result`, 기본값 `'HOLD'`)이 모두 반영됐습니다.

### 4-4. 제약조건 삭제 {keep}

수료증 번호 중복 허용으로 바꿉니다(재발급 때 같은 번호를 쓰기로 했다고 합시다).

```sql
ALTER TABLE edu_record DROP CONSTRAINT training_cert_uk;
```

```sql
SELECT conname, contype
  FROM pg_constraint
 WHERE conrelid = 'lab.edu_record'::regclass
   AND contype IN ('p', 'u', 'c', 'f')
 ORDER BY contype, conname;
```

```result
| conname | contype |
| --- | --- |
| training_hours_ck | c |
| training_result_ck | c |
| training_dept_fk | f |
| training_emp_fk | f |
| training_pk | p |
```

> 테이블 이름을 `edu_record`로 바꿔도 제약조건 이름은 `training_…`으로 남아 있습니다. 이름 규칙(3-2)을 지키려면 `ALTER TABLE … RENAME CONSTRAINT 옛이름 TO 새이름;`으로 함께 바꿔 줍니다.

### 4-5. 확인 문제 — 블로그 테이블 · 생산 데이터 {keep}

> 실행 전: `SET search_path TO lab, bom;`

:::try
**[복습]** 3-7의 `blog` 테이블을 다음과 같이 고친 뒤, `information_schema.columns`로 결과를 확인하세요.
① 조회수 `view_cnt`(정수, NULL 불가, 기본값 0) 추가 ② `content` → `body`로 이름 변경 ③ `title`을 200글자로 늘리기

**[응용]** 2-7의 `bom_wm`에 손실률 `loss_rate NUMERIC(3,2) NOT NULL`을 추가하려니 오류가 납니다. 이유를 설명하고, **한 문장으로** 추가하는 방법을 쓰세요. 추가 후 43행 모두의 값이 어떻게 되었는지 확인하세요.
:::

### 4-5. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
```sql
ALTER TABLE blog ADD COLUMN view_cnt INT NOT NULL DEFAULT 0;
ALTER TABLE blog RENAME COLUMN content TO body;
ALTER TABLE blog ALTER COLUMN title TYPE VARCHAR(200);

SELECT column_name, data_type, character_maximum_length AS max_len, is_nullable, column_default
  FROM information_schema.columns
 WHERE table_schema = 'lab' AND table_name = 'blog'
 ORDER BY ordinal_position;
```

```result
| column_name | data_type | max_len | is_nullable | column_default |
| --- | --- | --- | --- | --- |
| blog_no | integer | NULL | NO | NULL |
| title | character varying | 200 | NO | NULL |
| body | character varying | 4000 | YES | NULL |
| member_id | character varying | 15 | YES | NULL |
| view_cnt | integer | NULL | NO | 0 |
```

`blog_no`가 `NO`인 것은 PK(`blog_no_pk`) 때문입니다.
:::

### 4-5. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
```sql
ALTER TABLE bom_wm ADD COLUMN loss_rate NUMERIC(3,2) NOT NULL;
```

```error
ERROR:  column "loss_rate" of relation "bom_wm" contains null values
```

이미 43행이 있는데 새 컬럼은 NULL로 시작하므로 NOT NULL을 만족할 수 없습니다(4-2). 기본값을 함께 줍니다.

```sql
ALTER TABLE bom_wm ADD COLUMN loss_rate NUMERIC(3,2) NOT NULL DEFAULT 0;

SELECT COUNT(*) AS cnt, MIN(loss_rate) AS min_rate, MAX(loss_rate) AS max_rate FROM bom_wm;
```

```result
| cnt | min_rate | max_rate |
| --- | --- | --- |
| 43 | 0.00 | 0.00 |
```
:::

> 확인 문제를 마치면 `SET search_path TO lab, hr;`으로 돌아옵니다.

## 5. DROP · TRUNCATE — 지우기

### 5-1. DROP TABLE — 테이블 통째로 삭제 {keep}

```text DROP TABLE의 모양
DROP TABLE [IF EXISTS] 테이블명 [CASCADE];
```

:::error 다른 테이블이 참조하는 테이블은 지울 수 없음
`edu_record`(옛 `training`)의 FK가 `t_dept`를 참조하고 있습니다.

```sql
DROP TABLE lab.t_dept;
```

```error
ERROR:  cannot drop table t_dept because other objects depend on it
DETAIL:  constraint training_dept_fk on table edu_record depends on table t_dept
HINT:  Use DROP ... CASCADE to drop the dependent objects too.
```

`DETAIL`이 **무엇이 이 테이블에 기대고 있는지**(제약조건 `training_dept_fk`)를 알려 줍니다.
:::

### 5-1. CASCADE — 기대고 있는 객체까지 함께 삭제 {keep}

```sql
DROP TABLE lab.t_dept CASCADE;
```

```result
NOTICE:  drop cascades to constraint training_dept_fk on table edu_record
```

```sql
SELECT conname, contype
  FROM pg_constraint
 WHERE conrelid = 'lab.edu_record'::regclass
   AND contype IN ('p', 'u', 'c', 'f')
 ORDER BY contype, conname;
```

```result
| conname | contype |
| --- | --- |
| training_hours_ck | c |
| training_result_ck | c |
| training_emp_fk | f |
| training_pk | p |
```

### 5-1. CASCADE는 규칙을 함께 지웁니다 {keep}

```sql
SELECT COUNT(*) AS cnt FROM edu_record;
```

```result
| cnt |
| --- |
| 5 |
```

- `CASCADE`가 지운 것은 **자식 테이블이 아니라 FK 제약조건**(`training_dept_fk`)입니다. 교육 기록 5행은 그대로 남았습니다.
- 그 대신 이제 `edu_record.department_id`에는 **아무 부서 번호나** 들어갈 수 있습니다. ==CASCADE는 오류를 없애 주는 옵션이 아니라, 규칙을 함께 지우는 옵션==입니다. `NOTICE`에 무엇이 함께 지워졌는지 반드시 읽으세요.

### 5-1. IF EXISTS — 없으면 오류 대신 안내만 {keep}

```sql
DROP TABLE lab.t_dept;
```

```error
ERROR:  table "t_dept" does not exist
```

```sql
DROP TABLE IF EXISTS lab.t_dept;
```

```result
NOTICE:  table "t_dept" does not exist, skipping
```

- `hr_postgres.sql` 맨 위의 `DROP SCHEMA IF EXISTS hr CASCADE;`도 같은 원리입니다. 지울 대상이 아직 없는 첫 실행에서도 오류가 나지 않아, 스크립트를 몇 번이고 다시 실행할 수 있습니다.
- `lab.`을 붙인 이유: DML·TCL 단원의 `hr.t_dept`가 있다면, 스키마 없이 `DROP TABLE t_dept;`를 실행하는 순간 `lab`에 없으니 search_path 다음 순서인 **`hr.t_dept`를 찾아 지웁니다.** ==지우는 문장일수록 스키마를 붙여 씁니다.==

### 5-2. TRUNCATE — 구조는 두고 데이터만 비우기 {keep}

```sql
TRUNCATE TABLE edu_record;
```

```sql
SELECT COUNT(*) AS cnt FROM edu_record;
```

```result
| cnt |
| --- |
| 0 |
```

### 5-2. 그릇은 그대로 남았습니다 {keep}

```sql
SELECT column_name FROM information_schema.columns
 WHERE table_schema = 'lab' AND table_name = 'edu_record'
 ORDER BY ordinal_position;
```

```result
| column_name |
| --- |
| train_id |
| cert_no |
| employee_id |
| department_id |
| train_date |
| total_hours |
| absent_hours |
| train_result |
| judged_by |
```

행은 0개가 됐지만 테이블과 컬럼·제약조건은 그대로입니다.

### 5-2. 참조되는 테이블은 TRUNCATE도 막힘 {keep}

:::error 참조되는 테이블은 TRUNCATE도 막힘
지금은 실행하지 마세요(이미 지운 테이블입니다). 5-1에서 CASCADE 하기 전에 실행했다면 나오는 결과입니다.

```sql
TRUNCATE TABLE lab.t_dept;
```

```error
ERROR:  cannot truncate a table referenced in a foreign key constraint
DETAIL:  Table "edu_record" references "t_dept".
HINT:  Truncate table "edu_record" at the same time, or use TRUNCATE ... CASCADE.
```

`TRUNCATE ... CASCADE`는 참조하는 **자식 테이블의 데이터까지 모두** 비웁니다. 원본 `departments`에 실행하면 `employees`·`job_history`까지 한꺼번에 비워질 수 있으므로 쓰지 않습니다.
:::

### 5-2. PostgreSQL의 TRUNCATE는 되돌릴 수 있습니다 {keep}

```sql
BEGIN;
TRUNCATE TABLE emp_ship;
SELECT COUNT(*) AS cnt_in_tx FROM emp_ship;
ROLLBACK;
```

```result
| cnt_in_tx |
| --- |
| 0 |
```

```sql
SELECT COUNT(*) AS cnt_after_rollback FROM emp_ship;
```

```result
| cnt_after_rollback |
| --- |
| 45 |
```

`BEGIN`으로 시작한 묶음 안에서 비운 데이터는 `ROLLBACK`으로 45행이 그대로 돌아왔습니다. 단, PostgreSQL 클라이언트는 보통 기본 설정이 **자동 커밋**이라 `BEGIN` 없이 실행한 TRUNCATE는 그 즉시 확정됩니다. `BEGIN`·`ROLLBACK`은 TCL 단원에서 배운 그대로입니다.

### 5-3. DELETE · TRUNCATE · DROP 비교 {keep}

| | `DELETE FROM 테이블` | `TRUNCATE TABLE 테이블` | `DROP TABLE 테이블` |
| --- | --- | --- | --- |
| 종류 | DML | DDL | DDL |
| 지우는 것 | 행 (조건으로 **일부만** 가능) | 행 **전부** | 테이블 **자체**(구조·제약조건 포함) |
| `WHERE` | 사용 가능 | 불가 | 불가 |
| 실행 후 테이블 | 남음 | 남음 (0행) | 없음 |
| `BEGIN` 안에서 `ROLLBACK` | 가능 | **가능** | 가능 |
| `BEGIN` 없이 실행 (자동 커밋) | 즉시 확정 | 즉시 확정 | 즉시 확정 |

==되돌릴 수 있는지는 명령어 종류보다 「BEGIN으로 묶었는가」가 결정합니다.== 지우는 명령은 실행 전에 같은 조건의 `SELECT COUNT(*)`로 대상 행 수를 먼저 확인하는 습관을 들이세요.

:::teacher 강사 확인
- 기존 교안 `9. DDL.pptx` 31번은 「TRUNCATE·DROP: 복구 불가능」입니다. PostgreSQL에서는 `BEGIN … ROLLBACK`으로 되돌아오므로 슬라이드를 수정해야 합니다. 5-3 표의 DELETE·DROP 칸도 검증 환경에서 직접 실행해 확인했습니다(`hr.departments` 사본 `t`로 `BEGIN; DROP TABLE t; ROLLBACK;` 후 27행 그대로, `BEGIN; DELETE FROM t; ROLLBACK;` 후 27행 그대로).
- 「되돌릴 수 있다」를 강조하다 보면 훈련생이 BEGIN 없이 실험할 수 있습니다. 자동 커밋이 기본이라는 점을 반드시 같이 말해 주세요.
:::

### 5-4. 확인 문제 — 회원·블로그 · 생산 데이터 {keep}

> 실행 전: `SET search_path TO lab, bom;`

:::try
**[복습]** 2-7에서 만든 `member`와 3-7에서 만든 `blog`를 모두 지우려 합니다. `DROP TABLE member;`부터 실행하면 어떻게 되나요? `CASCADE` 없이 두 테이블을 지우는 순서를 쓰고, 이미 지워졌어도 오류가 나지 않도록 작성하세요.

**[응용]** `bom_wm`을 `BEGIN`으로 묶어 `TRUNCATE`한 뒤, 묶음 안에서 행 수를 확인하고 `ROLLBACK`하세요. 묶음 밖에서 다시 확인한 행 수는?
:::

### 5-4. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
```sql
DROP TABLE member;
```

```error
ERROR:  cannot drop table member because other objects depend on it
DETAIL:  constraint blog_member_fk on table blog depends on table member
HINT:  Use DROP ... CASCADE to drop the dependent objects too.
```

**자식(참조하는 쪽) → 부모(참조되는 쪽)** 순서로 지웁니다.

```sql
DROP TABLE IF EXISTS blog;
DROP TABLE IF EXISTS member;
```
:::

### 5-4. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
묶음 안에서는 0행, ROLLBACK 후에는 43행입니다.

```sql
BEGIN;
TRUNCATE TABLE bom_wm;
SELECT COUNT(*) AS cnt_in_tx FROM bom_wm;
ROLLBACK;
```

```result
| cnt_in_tx |
| --- |
| 0 |
```

```sql
SELECT COUNT(*) AS cnt_after FROM bom_wm;
```

```result
| cnt_after |
| --- |
| 43 |
```
:::

> 확인 문제를 마치면 `SET search_path TO lab, hr;`으로 돌아옵니다.

## 6. 판단 결과 기록 테이블 설계 — 급여 조정 제안

### 6-1. 기존 이력 테이블 — job_history {keep}

HR 데이터셋에는 이미 「변경 기록」 테이블이 하나 있습니다. 직원의 지난 직책을 남기는 `job_history`입니다. psql의 `\d`로 구조를 봅니다.

```screen psql — \d hr.job_history
                         Table "hr.job_history"
    Column     |         Type          | Collation | Nullable | Default 
---------------+-----------------------+-----------+----------+---------
 employee_id   | numeric(6,0)          |           | not null | 
 start_date    | date                  |           | not null | 
 end_date      | date                  |           | not null | 
 job_id        | character varying(10) |           | not null | 
 department_id | numeric(4,0)          |           |          | 
Indexes:
    "jhist_emp_id_st_date_pk" PRIMARY KEY, btree (employee_id, start_date)
    "jhist_department_ix" btree (department_id)
    "jhist_employee_ix" btree (employee_id)
    "jhist_job_ix" btree (job_id)
Check constraints:
    "jhist_date_interval" CHECK (end_date > start_date)
Foreign-key constraints:
    "jhist_dept_fk" FOREIGN KEY (department_id) REFERENCES hr.departments(department_id)
    "jhist_emp_fk" FOREIGN KEY (employee_id) REFERENCES hr.employees(employee_id)
    "jhist_job_fk" FOREIGN KEY (job_id) REFERENCES hr.jobs(job_id)
```

### 6-1. 이력 테이블 점검 {keep}

| 점검 항목 | `job_history` |
| --- | --- |
| 기록을 구별하는 PK | `(employee_id, start_date)` 있음 |
| 대상이 실제로 있는지 (FK) | 있음 — 직원·직책·부서 |
| 필수 값 (NOT NULL) | 사번·시작일·종료일·직책 있음, 부서는 없음 |
| 값의 범위 (CHECK) | 종료일 > 시작일 있음 |
| 기록 시각 | `DATE`(날짜만) |
| **왜** 바뀌었나 · **누가** 결정했나 | **없음** |

:::try 생각해 보기
`job_history`는 규칙이 잘 갖춰진 테이블이지만 「왜」 직책이 바뀌었는지, 「누가」 결정했는지는 남지 않습니다. 몇 년 뒤 「이 직원은 왜 직책이 바뀌었나?」를 물으면 무엇으로 답할 수 있을까요?
:::

### 6-2. 요구사항 → 컬럼 {keep}

3-6 ①에서 급여 2,500 미만 직원 5명을 찾았습니다. AI가 이들의 **급여 인상을 제안**하고, 인사 담당자가 승인·반려한다고 합시다. 이 판단을 「누가·언제·왜·무엇을」과 함께 남기는 테이블을 설계합니다. (생산 데이터의 결품 경고 테이블도 같은 방식으로 만듭니다 — 7장 복습 5.)

| 기록할 것 | 컬럼 | 자료형 | 규칙 |
| --- | --- | --- | --- |
| 기록 번호 | `proposal_id` | `BIGINT` 자동 번호 | PK |
| 어느 직원 | `employee_id` | `NUMERIC(6)` | NOT NULL, `employees` FK |
| 지금 급여, 제안 급여 | `current_salary`, `proposed_salary` | `NUMERIC(8,2)` | NOT NULL, 제안 급여 > 0 |
| 왜 (근거) | `basis` | `TEXT` | NOT NULL — 근거 없는 판단은 기록 불가 |
| 누가 판단 | `judged_by` | `VARCHAR(5)` | `'AI'` 또는 `'HUMAN'`만 |
| 처리 상태 | `status` | `VARCHAR(10)` | `'PENDING'`(대기) / `'APPROVED'`(승인) / `'REJECTED'`(반려), 기본값 대기 |
| 언제 기록 | `created_at` | `TIMESTAMP` | NOT NULL, 기본값 현재 시각 |
| 누가·언제 승인/반려 | `reviewed_by`, `reviewed_at` | `VARCHAR(30)`, `TIMESTAMP` | 대기가 아니면 둘 다 있어야 함 |

### 6-3. CREATE TABLE {keep}

```sql
SET search_path TO lab, hr;

CREATE TABLE salary_proposal (
      proposal_id     BIGINT        GENERATED ALWAYS AS IDENTITY
    , employee_id     NUMERIC(6)    NOT NULL
    , current_salary  NUMERIC(8,2)  NOT NULL
    , proposed_salary NUMERIC(8,2)  NOT NULL
    , basis           TEXT          NOT NULL
    , judged_by       VARCHAR(5)    NOT NULL
    , status          VARCHAR(10)   NOT NULL DEFAULT 'PENDING'
    , created_at      TIMESTAMP     NOT NULL DEFAULT now()
    , reviewed_by     VARCHAR(30)
    , reviewed_at     TIMESTAMP
    , CONSTRAINT salary_proposal_pk        PRIMARY KEY (proposal_id)
    , CONSTRAINT salary_proposal_emp_fk    FOREIGN KEY (employee_id) REFERENCES hr.employees (employee_id)
    , CONSTRAINT salary_proposal_amt_ck    CHECK (proposed_salary > 0)
    , CONSTRAINT salary_proposal_judged_ck CHECK (judged_by IN ('AI', 'HUMAN'))
    , CONSTRAINT salary_proposal_status_ck CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED'))
    , CONSTRAINT salary_proposal_review_ck CHECK (status = 'PENDING' OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL))
);
```

### 6-3. 새로 나온 두 가지 — IDENTITY · now() {keep}

- **`GENERATED ALWAYS AS IDENTITY`** — 행을 넣을 때마다 1, 2, 3 … 번호를 **DB가 자동으로** 매깁니다. 사람이나 프로그램이 번호를 직접 정하다가 겹치는 일이 없습니다. (`hr_postgres.sql`의 `employees_seq` 같은 시퀀스를 컬럼에 붙여 둔 것과 같습니다.)
- **`now()`** — 현재 날짜·시각을 돌려주는 함수입니다. `DEFAULT now()`이므로 기록 시각을 따로 적지 않아도 INSERT한 시각이 남습니다.

### 6-4. 동작 확인 — AI 판단 기록하기 {keep}

3-6 ①에서 찾은 132번 TJ Olson(급여 2,100)의 인상 제안을 AI 판단으로 기록합니다. 근거에는 판단 이유를 적습니다.

```sql
INSERT INTO salary_proposal (employee_id, current_salary, proposed_salary, basis, judged_by)
VALUES (132, 2100, 2500, '급여 2100 < 사내 최저 급여 기준 2500 (3-6 ① 규칙)', 'AI');
```

```sql
SELECT proposal_id, employee_id, current_salary, proposed_salary, judged_by, status,
       created_at IS NOT NULL AS has_created_at, reviewed_by
  FROM salary_proposal;
```

```result
| proposal_id | employee_id | current_salary | proposed_salary | judged_by | status | has_created_at | reviewed_by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 132 | 2100.00 | 2500.00 | AI | PENDING | t | NULL |
```

번호(1), 상태(`PENDING`), 기록 시각이 **적지 않아도** 채워졌습니다. (`created_at`은 실행할 때마다 값이 달라 `IS NOT NULL`로만 확인했습니다.)

### 6-4. 이 테이블이 막아 주는 것 ① · ② {keep}

:::error ① 번호를 직접 정하면
```sql
INSERT INTO salary_proposal (proposal_id, employee_id, current_salary, proposed_salary, basis, judged_by)
VALUES (100, 132, 2100, 2500, '수동 입력', 'HUMAN');
```

```error
ERROR:  cannot insert a non-DEFAULT value into column "proposal_id"
DETAIL:  Column "proposal_id" is an identity column defined as GENERATED ALWAYS.
HINT:  Use OVERRIDING SYSTEM VALUE to override.
```
:::

:::error ② 판단 주체가 정해진 값이 아니면
(`DETAIL`의 시각은 실행 시각이라 매번 다릅니다)

```sql
INSERT INTO salary_proposal (employee_id, current_salary, proposed_salary, basis, judged_by)
VALUES (128, 2200, 2500, '테스트', 'GPT');
```

```error
ERROR:  new row for relation "salary_proposal" violates check constraint "salary_proposal_judged_ck"
DETAIL:  Failing row contains (2, 128, 2200.00, 2500.00, 테스트, GPT, PENDING, 2026-11-17 21:07:49.028715, null, null).
```
:::

### 6-4. 이 테이블이 막아 주는 것 ③ · ④ {keep}

:::error ③ 승인자 없이 「승인」으로 기록하면
```sql
INSERT INTO salary_proposal (employee_id, current_salary, proposed_salary, basis, judged_by, status)
VALUES (128, 2200, 2500, '테스트', 'AI', 'APPROVED');
```

```error
ERROR:  new row for relation "salary_proposal" violates check constraint "salary_proposal_review_ck"
DETAIL:  Failing row contains (3, 128, 2200.00, 2500.00, 테스트, AI, APPROVED, 2026-11-17 21:07:49.092168, null, null).
```
:::

:::error ④ 제안 급여가 0이면
```sql
INSERT INTO salary_proposal (employee_id, current_salary, proposed_salary, basis, judged_by)
VALUES (128, 2200, 0, '테스트', 'AI');
```

```error
ERROR:  new row for relation "salary_proposal" violates check constraint "salary_proposal_amt_ck"
DETAIL:  Failing row contains (4, 128, 2200.00, 0.00, 테스트, AI, PENDING, 2026-11-17 21:07:49.156255, null, null).
```
:::

특히 ③은 「AI가 혼자 승인까지 끝낸 기록」을 DB 차원에서 막습니다. ==사람 승인 없이는 승인 상태가 될 수 없다는 업무 규칙을 CHECK 하나로 강제==한 것입니다.

### 6-4. 실패한 INSERT도 번호를 하나씩 씁니다 {keep}

```sql
INSERT INTO salary_proposal (employee_id, current_salary, proposed_salary, basis, judged_by)
VALUES (136, 2200, 2500, '연습 입력', 'HUMAN');
```

```sql
SELECT proposal_id, employee_id, judged_by, status FROM salary_proposal ORDER BY proposal_id;
```

```result
| proposal_id | employee_id | judged_by | status |
| --- | --- | --- | --- |
| 1 | 132 | AI | PENDING |
| 5 | 136 | HUMAN | PENDING |
```

②~④의 `DETAIL`에 보였던 2, 3, 4번이 실패와 함께 버려져 다음 번호는 5입니다. 자동 번호는 ==겹치지 않는 것만 보장하고, 빈칸 없이 이어지는 것은 보장하지 않습니다.== 「기록이 몇 건인가」는 번호가 아니라 `COUNT(*)`로 셉니다.

### 6-4. 기존 이력 테이블과 비교 {keep}

```sql
SELECT conrelid::regclass AS table_name, contype, COUNT(*) AS cnt
  FROM pg_constraint
 WHERE conrelid IN ('hr.job_history'::regclass, 'lab.salary_proposal'::regclass)
   AND contype IN ('p', 'u', 'c', 'f')
 GROUP BY conrelid, contype
 ORDER BY 1, 2;
```

```result
| table_name | contype | cnt |
| --- | --- | --- |
| job_history | c | 1 |
| job_history | f | 3 |
| job_history | p | 1 |
| salary_proposal | c | 4 |
| salary_proposal | f | 1 |
| salary_proposal | p | 1 |
```

규칙의 개수는 비슷하지만, `salary_proposal`은 `job_history`에 없던 **근거(`basis`)·판단 주체(`judged_by`)·처리 상태·기록 시각(`TIMESTAMP`)·승인자** 를 컬럼으로 두고, 그 값까지 CHECK로 지킵니다.

> 승인(`PENDING` → `APPROVED`)은 행을 새로 넣는 것이 아니라 **기존 행의 상태를 바꾸는** 작업(UPDATE)입니다. 반려된 제안도 지우지 않고 `REJECTED`로 남겨 「AI가 무엇을 틀렸는지」를 기록으로 쌓습니다. 이 흐름은 Day 4 4교시(결품 경고 승인)에서 이어집니다.

:::teacher 강사 확인
- 6-4의 2,100 → 2,500은 3-6 ①의 연습용 급여 규정(2,500 이상) 기준입니다. 실제 인사 규정이 아니라는 점을 말해 주세요.
- `salary_proposal_review_ck`의 `OR` 조건식이 어렵다면 「대기(PENDING)이거나, 아니면 승인자와 승인 시각이 둘 다 있어야 한다」로 읽어 주세요. 3단원 `AND`·`OR` 우선순위 때문에 괄호가 필요하다는 점도 짚어 주세요.
- 운영안 3H의 생산 시나리오(결품 경고 `shortage_alert`, 기존 이력 테이블 2종 비교)는 **7장 복습 5번**에 있습니다. Day 4 4교시·6교시가 `lab.shortage_alert`를 쓰므로, 6장을 마친 뒤 복습 5번을 함께 실행하세요(구조는 `salary_proposal`과 같습니다).
:::

### 6-5. 확인 문제 — 품질 판단 테이블 (도전) {keep}

> 실행 전: `SET search_path TO lab, bom;`

:::try
**[응용 · 도전]** 품질 점검 판단을 **AI 판단**과 **사람 최종 판단**으로 나눠 기록하는 `quality_judgment` 테이블을 만드세요. 표에 자료형이 없는 컬럼은 직접 정하세요(2-2 참고).

| 컬럼 | 조건 |
| --- | --- |
| `judgment_id` | 자동 번호, PK |
| `part_no` | NOT NULL, `bom.part_master` FK |
| `check_item` | 점검 항목, 가변 문자 30글자, NOT NULL |
| `ai_decision` | NOT NULL, `'OK'`·`'NG'`·`'REVIEW'`만 |
| `human_decision` | `'OK'`·`'NG'`만 (아직 판단 전이면 NULL) |
| `judged_at` | NOT NULL, 기본값 현재 시각 |

아래 3건을 넣고, **사람 판단이 있으면서 AI 판단과 다른** 건만 조회하세요.

| part_no | check_item | ai_decision | human_decision |
| --- | --- | --- | --- |
| `MFT43979901` | `PO_PRICE` | `NG` | `NG` |
| `EMT73633001` | `UIT_LINE_TYPE` | `REVIEW` | `NG` |
| `ECP39799101` | `SHORTAGE` | `NG` | (넣지 않음) |
:::

### 6-5. 확인 문제 답 ① 테이블 만들고 넣기 {keep}

:::answer [응용 · 도전] 예시 답안 ①
```sql
CREATE TABLE quality_judgment (
      judgment_id     BIGINT       GENERATED ALWAYS AS IDENTITY
    , part_no         CHAR(11)     NOT NULL
    , check_item      VARCHAR(30)  NOT NULL
    , ai_decision     VARCHAR(10)  NOT NULL
    , human_decision  VARCHAR(10)
    , judged_at       TIMESTAMP    NOT NULL DEFAULT now()
    , CONSTRAINT quality_judgment_pk      PRIMARY KEY (judgment_id)
    , CONSTRAINT quality_judgment_part_fk FOREIGN KEY (part_no) REFERENCES bom.part_master (part_no)
    , CONSTRAINT quality_judgment_ai_ck   CHECK (ai_decision    IN ('OK', 'NG', 'REVIEW'))
    , CONSTRAINT quality_judgment_hu_ck   CHECK (human_decision IN ('OK', 'NG'))
);

INSERT INTO quality_judgment (part_no, check_item, ai_decision, human_decision)
VALUES ('MFT43979901', 'PO_PRICE', 'NG', 'NG');

INSERT INTO quality_judgment (part_no, check_item, ai_decision, human_decision)
VALUES ('EMT73633001', 'UIT_LINE_TYPE', 'REVIEW', 'NG');

INSERT INTO quality_judgment (part_no, check_item, ai_decision)
VALUES ('ECP39799101', 'SHORTAGE', 'NG');
```
:::

### 6-5. 확인 문제 답 ② 조회하기 · CHECK와 NULL {keep}

:::answer [응용 · 도전] 예시 답안 ②
```sql
SELECT judgment_id, part_no, check_item, ai_decision, human_decision
  FROM quality_judgment
 WHERE human_decision IS NOT NULL
   AND ai_decision <> human_decision
 ORDER BY judgment_id;
```

```result
| judgment_id | part_no | check_item | ai_decision | human_decision |
| --- | --- | --- | --- | --- |
| 2 | EMT73633001 | UIT_LINE_TYPE | REVIEW | NG |
```

- 3번째 행은 `human_decision`이 NULL인데도 CHECK를 통과했습니다. ==CHECK는 조건식이 「거짓」일 때만 거부하고, NULL(알 수 없음)이면 통과시킵니다.== 「아직 사람 판단 전」을 NULL로 남길 수 있는 이유입니다.
- 사람 판단에 `'REVIEW'`를 넣으면 거부됩니다. 사람은 최종 판단(OK/NG)을 내려야 한다는 규칙입니다.

```sql
INSERT INTO quality_judgment (part_no, check_item, ai_decision, human_decision)
VALUES ('ECP39799101', 'SHORTAGE', 'NG', 'REVIEW');
```

```error
ERROR:  new row for relation "quality_judgment" violates check constraint "quality_judgment_hu_ck"
DETAIL:  Failing row contains (4, ECP39799101, SHORTAGE, NG, REVIEW, 2026-11-17 21:07:49.763524).
```
:::

> 확인 문제를 마치면 `SET search_path TO lab, hr;`으로 돌아옵니다.

## 7. 복습 문제

### 7-0. 복습 문제 안내 {keep}

> 범위: DDL 전체(CREATE · 자료형 · 제약조건 · ALTER · DROP · TRUNCATE · CTAS). 1번은 회원정보 테이블, 2~6번은 생산 데이터(`bom`)입니다. 실행 전 `SET search_path TO lab, bom;` **5번 `shortage_alert`는 Day 4 4교시·6교시에서 이어서 쓰므로 수업 시간에 함께 실행**합니다. 6번은 `lab` 스키마를 통째로 지우므로 **Day 4 실습이 모두 끝난 뒤에 실행**합니다.

```icons 여섯 문항
users | 1 · CREATE · PK | 회원정보 테이블 TB_CUST | rose
refrigerator | 2 · CTAS · 제약조건 | 냉장고 BOM 사본 bom_rf | plum
pencil | 3 · ALTER TABLE | bom_rf 고치기 | lime
clipboard-list | 4 · (심화) 설계 | 품질 이상 기록 quality_issue | ivory
triangle-alert | 5 · (심화) 판단 기록 | 결품 경고 shortage_alert | rose
trash-2 | 6 · DROP SCHEMA | lab 스키마 정리 | hot
```

### 7-1. 복습 1 {keep}

**1.** 회원정보 테이블 `TB_CUST`를 만드세요.

- 컬럼: `CUST_ID`(가변 문자 20글자), `PASSWD`(가변 문자 300글자), `CUST_NAME`(가변 문자 50글자)
- `CUST_ID`, `PASSWD`는 NULL 불가, `CUST_NAME`은 NULL 가능
- `CUST_NAME`을 입력하지 않으면 `'????'`가 자동 입력
- `CUST_ID`는 PRIMARY KEY (제약조건 이름: `PK_TEST`, ALTER TABLE로 추가)

다음 3건을 차례로 넣어 확인하세요. (2)는 들어가면 안 됩니다.

(1) `{ CUST_ID : 'C0001', PASSWD : 'pass111' }`
(2) `{ CUST_ID : 'C0001', PASSWD : 'pass222', CUST_NAME : 'pk설정했나' }`
(3) `{ CUST_ID : 'C0002', PASSWD : 'pass222', CUST_NAME : '고객2' }`

```result 출력 결과 — SELECT * FROM tb_cust ORDER BY cust_id; (총 2행)
| cust_id | passwd | cust_name |
| --- | --- | --- |
| C0001 | pass111 | ???? |
| C0002 | pass222 | 고객2 |
```

### 7-2. 복습 2 {keep}

**2.** 냉장고(`TRF38316001`) BOM만 `bom_rf` 사본으로 만들고, 다음 제약조건 3개를 추가하세요.

- `bom_rf_pk` : `bom_id` PK
- `bom_rf_qty_ck` : `qty_per > 0`
- `bom_rf_child_fk` : `child_part_no` → `bom.part_master(part_no)`

3-7 확인 문제에서 세탁기 사본(`bom_wm`)은 같은 CHECK가 실패했습니다. 냉장고 사본은 어떻게 되나요? 이유는?

```result 출력 결과 — 사본 행 수 39, 제약조건 조회 (총 3행)
| conname | contype |
| --- | --- |
| bom_rf_qty_ck | c |
| bom_rf_child_fk | f |
| bom_rf_pk | p |
```

### 7-3. 복습 3 {keep}

**3.** `bom_rf`를 다음과 같이 고치세요.
① 비고 `remark`(TEXT) 추가 ② `qty_per` → `qty`로 이름 변경 ③ `bom_level` NOT NULL 설정 ④ `supply_type` 기본값 `'Assembly Pull'`
그 뒤 `bom_rf_qty_ck`의 조건식이 어떻게 바뀌었는지 확인하세요.

```result 출력 결과 — information_schema.columns (총 11행)
| column_name | data_type | is_nullable | column_default |
| --- | --- | --- | --- |
| bom_id | integer | NO | NULL |
| model_part_no | character | YES | NULL |
| parent_part_no | character | YES | NULL |
| child_part_no | character | YES | NULL |
| bom_level | smallint | NO | NULL |
| qty | numeric | YES | NULL |
| uom | character | YES | NULL |
| supply_type | text | YES | 'Assembly Pull'::text |
| c_osp_flag | character | YES | NULL |
| effective_from | date | YES | NULL |
| remark | text | YES | NULL |
```

```result 출력 결과 — bom_rf_qty_ck 조건식
CHECK ((qty > (0)::numeric))
```

### 7-4. 복습 4 (심화) {keep}

**4.** (심화) Day 2 품질 진단 리포트의 이상 항목을 기록할 `quality_issue` 테이블을 설계하세요. 자료형은 직접 정하세요(2-2 참고).

| 컬럼 | 조건 |
| --- | --- |
| `issue_id` | 자동 번호, PK |
| `part_no` | NOT NULL, `bom.part_master` FK |
| `issue_type` | NOT NULL, `'MISSING_VALUE'`(값 누락) / `'ATTR_MISMATCH'`(속성 불일치) / `'RULE_VIOLATION'`(규칙 위반)만 |
| `detail` | NOT NULL (근거) |
| `owner_dept` | NOT NULL, `'R&D'` / `'자재'` / `'구매'`만 |
| `status` | NOT NULL, `'OPEN'` / `'CLOSED'`만, 기본값 `'OPEN'` |
| `found_at` | NOT NULL, 기본값 오늘 날짜 (`CURRENT_DATE`) |

아래 두 건을 기록하고, `issue_type`에 목록에 없는 `'ZERO_QTY'`를 넣으면 어떻게 되는지 확인하세요.
(1) 단가가 빈 소싱 행(3단원 3-5·4단원 1-6 확인 문제): `MFT43979901` / `MISSING_VALUE` / `'part_sourcing.po_price가 NULL'` / 구매
(2) 소요량 0인 BOM 행(3-7 확인 문제): `FSC67181101` / `RULE_VIOLATION` / `'bom_id 70 qty_per = 0'` / R&D

```result 출력 결과 (총 2행, today는 found_at = CURRENT_DATE 결과)
| issue_id | part_no | issue_type | owner_dept | status | today |
| --- | --- | --- | --- | --- | --- |
| 1 | MFT43979901 | MISSING_VALUE | 구매 | OPEN | t |
| 2 | FSC67181101 | RULE_VIOLATION | R&D | OPEN | t |
```

### 7-5. 복습 5 (심화) ① 요구사항 {keep}

**5.** (심화) Day 3 7교시에 컴프레서(`ECP39799101`)가 **12/4에 결품**된다는 것을 계산했습니다. 이 판단을 「누가·언제·왜·무엇을」과 함께 남기는 결품 경고 테이블 `shortage_alert`를 아래 요구사항대로 만드세요(6장 `salary_proposal`과 같은 방식). 이 테이블은 Day 4 4교시(승인 흐름)와 6교시(`check_shortage` 함수의 결과 INSERT)에서 그대로 쓰므로 컬럼·제약조건 이름을 그대로 따르세요.

| 기록할 것 | 컬럼 | 자료형 | 규칙 (제약조건 이름) |
| --- | --- | --- | --- |
| 기록 번호 | `alert_id` | `BIGINT` 자동 번호 | PK (`shortage_alert_pk`) |
| 어느 사이트, 어떤 품번 | `site_code`, `part_no` | `CHAR(2)`, `CHAR(11)` | NOT NULL, 품번은 `bom.part_master` FK (`shortage_alert_part_fk`) |
| 언제, 얼마나 부족 | `shortage_date`, `shortage_qty` | `DATE`, `NUMERIC(12,2)` | NOT NULL, 부족 수량 > 0 (`shortage_alert_qty_ck`) |
| 왜 (근거) | `basis` | `TEXT` | NOT NULL |
| 누가 판단 | `judged_by` | `VARCHAR(5)` | `'AI'`·`'HUMAN'`만 (`shortage_alert_judged_ck`) |
| 처리 상태 | `status` | `VARCHAR(10)` | `PENDING`/`APPROVED`/`REJECTED`, 기본값 `PENDING` (`shortage_alert_status_ck`) |
| 언제 기록 | `created_at` | `TIMESTAMP` | NOT NULL, 기본값 현재 시각 |
| 누가·언제 승인/반려 | `reviewed_by`, `reviewed_at` | `VARCHAR(30)`, `TIMESTAMP` | 대기가 아니면 둘 다 (`shortage_alert_review_ck`) |

### 7-5. 복습 5 (심화) ② 기록하고 확인하기 {keep}

① AI 판단 1건을 기록하고 조회하세요. 사이트 `'CW'`, 결품일 `'2026-12-04'`, 부족 수량 250, 근거 `'11/30 재고 1150 - 12/1~12/4 냉장고 계획 누적 1400 = -250'`(11/30 재고 1,150 − 12/1~12/4 냉장고 계획 380 + 320 + 380 + 320 = 1,400 → 12/4에 250 부족).
② 판단 주체 `'GPT'`, 승인자 없는 `'APPROVED'`, 부족 수량 0을 각각 넣어 어느 제약조건에 막히는지 확인하세요.
③ 기존 이력 테이블 `bom.uit_change_history`·`bom.part_status_history`와 제약조건 수를 비교하세요.

```result 출력 결과 — ① 조회 (총 1행, has_created_at은 created_at IS NOT NULL 결과)
| alert_id | part_no | shortage_date | shortage_qty | judged_by | status | has_created_at | reviewed_by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ECP39799101 | 2026-12-04 | 250.00 | AI | PENDING | t | NULL |
```

```result 출력 결과 — ③ 제약조건 비교 (총 6행)
| table_name | contype | cnt |
| --- | --- | --- |
| uit_change_history | f | 1 |
| uit_change_history | p | 1 |
| part_status_history | f | 1 |
| shortage_alert | c | 4 |
| shortage_alert | f | 1 |
| shortage_alert | p | 1 |
```

### 7-6. 복습 6 {keep}

**6.** **Day 4 실습이 모두 끝난 뒤에 실행하세요.** (5번 `shortage_alert`는 Day 4 4교시·6교시에서 계속 씁니다.) 실습을 마치고 `lab` 스키마에 만든 테이블을 확인한 뒤, `lab` 스키마를 통째로 지우세요. 원본 `bom` 스키마의 테이블(DML·TCL 단원의 사본 `t_…` 제외)이 17개 그대로인지 확인합니다. [힌트: `information_schema.tables`, `DROP SCHEMA ... CASCADE`, `NOT LIKE 't\_%'`]

```result 출력 결과 — lab 스키마 테이블 (본문·확인 문제·복습 1~5를 모두 순서대로 실행했다면 총 12행. 건너뛴 문제에 따라 달라집니다)
bom_rf, bom_wm, edu_record, emp_memo, emp_ship, job_hist_empty,
quality_issue, quality_judgment, salary_proposal, shortage_alert, t_emp, tb_cust
```

```result 출력 결과 — 삭제 후 bom 스키마 원본 테이블 수
| bom_tables |
| --- |
| 17 |
```

### 7-7. 복습 1 · 2 답 {keep}

:::answer 복습 1 · 2 예시 답안
```sql 1
CREATE TABLE tb_cust (
      cust_id    VARCHAR(20)   NOT NULL
    , passwd     VARCHAR(300)  NOT NULL
    , cust_name  VARCHAR(50)   DEFAULT '????'
);

ALTER TABLE tb_cust ADD CONSTRAINT pk_test PRIMARY KEY (cust_id);

INSERT INTO tb_cust (cust_id, passwd) VALUES ('C0001', 'pass111');
```

```sql
INSERT INTO tb_cust (cust_id, passwd, cust_name) VALUES ('C0001', 'pass222', 'pk설정했나');   -- 오류가 나야 정상
```

```error
ERROR:  duplicate key value violates unique constraint "pk_test"
DETAIL:  Key (cust_id)=(C0001) already exists.
```

```sql
INSERT INTO tb_cust (cust_id, passwd, cust_name) VALUES ('C0002', 'pass222', '고객2');

SELECT * FROM tb_cust ORDER BY cust_id;
```

```sql 2
CREATE TABLE bom_rf AS
SELECT *
  FROM bom.bom_structure
 WHERE model_part_no = 'TRF38316001';

ALTER TABLE bom_rf ADD CONSTRAINT bom_rf_pk       PRIMARY KEY (bom_id);
ALTER TABLE bom_rf ADD CONSTRAINT bom_rf_qty_ck   CHECK (qty_per > 0);
ALTER TABLE bom_rf ADD CONSTRAINT bom_rf_child_fk FOREIGN KEY (child_part_no) REFERENCES bom.part_master (part_no);

SELECT conname, contype
  FROM pg_constraint
 WHERE conrelid = 'lab.bom_rf'::regclass
   AND contype IN ('p', 'u', 'c', 'f')
 ORDER BY contype, conname;
```

- 1번: Oracle의 `VARCHAR2`는 PostgreSQL에서 `VARCHAR`로 씁니다. 중복 오류 메시지에는 ==직접 붙인 제약조건 이름 `pk_test`가 그대로 나옵니다.== 이름을 붙이는 이유입니다(3-2). (대문자로 적은 `PK_TEST`도 소문자 `pk_test`로 바뀝니다 — 2-5.)
- 2번: 소요량 0인 행(bom_id 70)은 **세탁기** BOM(DD모터 → 나사 M4)에만 있어서, 냉장고 사본에는 CHECK가 바로 걸립니다. 「규칙을 걸 수 있는가」로 데이터 범위별 품질을 비교할 수 있습니다.
:::

### 7-8. 복습 3 답 {keep}

:::answer 복습 3 예시 답안
```sql 3
ALTER TABLE bom_rf ADD COLUMN remark TEXT;
ALTER TABLE bom_rf RENAME COLUMN qty_per TO qty;
ALTER TABLE bom_rf ALTER COLUMN bom_level SET NOT NULL;
ALTER TABLE bom_rf ALTER COLUMN supply_type SET DEFAULT 'Assembly Pull';

SELECT column_name, data_type, is_nullable, column_default
  FROM information_schema.columns
 WHERE table_schema = 'lab' AND table_name = 'bom_rf'
 ORDER BY ordinal_position;

SELECT pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE conname = 'bom_rf_qty_ck';
```

- 3번: 컬럼 이름을 바꾸면 CHECK 조건식도 `qty`로 따라 바뀝니다(4-4).
:::

### 7-9. 복습 4 답 {keep}

:::answer 복습 4 예시 답안
```sql 4
CREATE TABLE quality_issue (
      issue_id    BIGINT       GENERATED ALWAYS AS IDENTITY
    , part_no     CHAR(11)     NOT NULL
    , issue_type  VARCHAR(20)  NOT NULL
    , detail      TEXT         NOT NULL
    , owner_dept  VARCHAR(10)  NOT NULL
    , status      VARCHAR(10)  NOT NULL DEFAULT 'OPEN'
    , found_at    DATE         NOT NULL DEFAULT CURRENT_DATE
    , CONSTRAINT quality_issue_pk      PRIMARY KEY (issue_id)
    , CONSTRAINT quality_issue_part_fk FOREIGN KEY (part_no) REFERENCES bom.part_master (part_no)
    , CONSTRAINT quality_issue_type_ck CHECK (issue_type IN ('MISSING_VALUE', 'ATTR_MISMATCH', 'RULE_VIOLATION'))
    , CONSTRAINT quality_issue_dept_ck CHECK (owner_dept IN ('R&D', '자재', '구매'))
    , CONSTRAINT quality_issue_stat_ck CHECK (status IN ('OPEN', 'CLOSED'))
);

INSERT INTO quality_issue (part_no, issue_type, detail, owner_dept)
VALUES ('MFT43979901', 'MISSING_VALUE', 'part_sourcing.po_price가 NULL', '구매');

INSERT INTO quality_issue (part_no, issue_type, detail, owner_dept)
VALUES ('FSC67181101', 'RULE_VIOLATION', 'bom_id 70 qty_per = 0', 'R&D');
```

```sql
INSERT INTO quality_issue (part_no, issue_type, detail, owner_dept)
VALUES ('FSC67181101', 'ZERO_QTY', 'bom_id 70 qty_per = 0', 'R&D');   -- 오류
```

```error
ERROR:  new row for relation "quality_issue" violates check constraint "quality_issue_type_ck"
DETAIL:  Failing row contains (3, FSC67181101, ZERO_QTY, bom_id 70 qty_per = 0, R&D, OPEN, 2026-11-17).
```

```sql
SELECT issue_id, part_no, issue_type, owner_dept, status, found_at = CURRENT_DATE AS today
  FROM quality_issue
 ORDER BY issue_id;
```

- 4번: `issue_type`처럼 값의 종류가 정해진 컬럼에 CHECK를 걸면, 사람마다 `'ZERO_QTY'`, `'zero qty'`, `'소요량0'`처럼 제각각 적어 **집계가 안 되는** 문제를 막을 수 있습니다(4단원 GROUP BY).
:::

### 7-10. 복습 5 답 ① 테이블 만들기 {keep}

:::answer 복습 5 예시 답안 ①
```sql 5
CREATE TABLE shortage_alert (
      alert_id      BIGINT        GENERATED ALWAYS AS IDENTITY
    , site_code     CHAR(2)       NOT NULL
    , part_no       CHAR(11)      NOT NULL
    , shortage_date DATE          NOT NULL
    , shortage_qty  NUMERIC(12,2) NOT NULL
    , basis         TEXT          NOT NULL
    , judged_by     VARCHAR(5)    NOT NULL
    , status        VARCHAR(10)   NOT NULL DEFAULT 'PENDING'
    , created_at    TIMESTAMP     NOT NULL DEFAULT now()
    , reviewed_by   VARCHAR(30)
    , reviewed_at   TIMESTAMP
    , CONSTRAINT shortage_alert_pk        PRIMARY KEY (alert_id)
    , CONSTRAINT shortage_alert_part_fk   FOREIGN KEY (part_no) REFERENCES bom.part_master (part_no)
    , CONSTRAINT shortage_alert_qty_ck    CHECK (shortage_qty > 0)
    , CONSTRAINT shortage_alert_judged_ck CHECK (judged_by IN ('AI', 'HUMAN'))
    , CONSTRAINT shortage_alert_status_ck CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED'))
    , CONSTRAINT shortage_alert_review_ck CHECK (status = 'PENDING' OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL))
);
```

- 6장 `salary_proposal`과 같은 뼈대입니다: 자동 번호 PK, 대상 FK, 근거 NOT NULL, 판단 주체·상태 CHECK, 기본값 `'PENDING'`·`now()`, 그리고 「대기가 아니면 승인자·승인 시각 필수」 CHECK.
:::

### 7-10. 복습 5 답 ② 기록하기 · 막히는지 확인 {keep}

:::answer 복습 5 예시 답안 ②
```sql
INSERT INTO shortage_alert (site_code, part_no, shortage_date, shortage_qty, basis, judged_by)
VALUES ('CW', 'ECP39799101', '2026-12-04', 250,
        '11/30 재고 1150 - 12/1~12/4 냉장고 계획 누적 1400 = -250', 'AI');

SELECT alert_id, part_no, shortage_date, shortage_qty, judged_by, status,
       created_at IS NOT NULL AS has_created_at, reviewed_by
  FROM shortage_alert;
```

```sql
INSERT INTO shortage_alert (site_code, part_no, shortage_date, shortage_qty, basis, judged_by)
VALUES ('CW', 'EIC93178801', '2026-12-10', 100, '테스트', 'GPT');                  -- shortage_alert_judged_ck

INSERT INTO shortage_alert (site_code, part_no, shortage_date, shortage_qty, basis, judged_by, status)
VALUES ('CW', 'EIC93178801', '2026-12-10', 100, '테스트', 'AI', 'APPROVED');       -- shortage_alert_review_ck

INSERT INTO shortage_alert (site_code, part_no, shortage_date, shortage_qty, basis, judged_by)
VALUES ('CW', 'EIC93178801', '2026-12-10', 0, '테스트', 'AI');                     -- shortage_alert_qty_ck
```

```error
ERROR:  new row for relation "shortage_alert" violates check constraint "shortage_alert_judged_ck"
ERROR:  new row for relation "shortage_alert" violates check constraint "shortage_alert_review_ck"
ERROR:  new row for relation "shortage_alert" violates check constraint "shortage_alert_qty_ck"
```

세 문장 모두 거부됩니다(`DETAIL` 줄은 생략). 특히 두 번째는 「AI가 사람 승인 없이 결품 경고를 확정한 기록」을 DB가 막는 것입니다.
:::

### 7-10. 복습 5 답 ③ 기존 이력 테이블과 비교 {keep}

:::answer 복습 5 예시 답안 ③
```sql
SELECT conrelid::regclass AS table_name, contype, COUNT(*) AS cnt
  FROM pg_constraint
 WHERE conrelid IN ('bom.uit_change_history'::regclass,
                    'bom.part_status_history'::regclass,
                    'lab.shortage_alert'::regclass)
   AND contype IN ('p', 'u', 'c', 'f')
 GROUP BY conrelid, contype
 ORDER BY 1, 2;
```

- `part_status_history`에는 **PK가 없습니다.** 같은 품번·같은 날짜·같은 상태 변경이 실수로 두 번 들어가도 막지 못하고, 「몇 건이 변경되었나」를 세는 쿼리가 부풀려집니다.
- 두 이력 테이블 모두 CHECK가 없고 기록 시각이 `DATE`(날짜만)입니다. `shortage_alert`는 판단 주체·상태·승인 조건을 CHECK로 지키고, 시각까지 `TIMESTAMP`로 남깁니다.
- 승인(`PENDING` → `APPROVED`)은 UPDATE로 상태를 바꾸는 작업입니다. 이 흐름은 Day 4 4교시에서 이어집니다.
:::

### 7-11. 복습 6 답 {keep}

:::answer 복습 6 예시 답안
```sql 6
SELECT table_name
  FROM information_schema.tables
 WHERE table_schema = 'lab'
 ORDER BY table_name;

DROP SCHEMA lab CASCADE;

SELECT COUNT(*) AS bom_tables
  FROM information_schema.tables
 WHERE table_schema = 'bom'
   AND table_name NOT LIKE 't\_%';
```

```result
NOTICE:  drop cascades to 12 other objects
DETAIL:  drop cascades to table emp_memo
drop cascades to table emp_ship
drop cascades to table job_hist_empty
drop cascades to table bom_wm
drop cascades to table edu_record
drop cascades to table t_emp
drop cascades to table salary_proposal
drop cascades to table quality_judgment
drop cascades to table tb_cust
drop cascades to table bom_rf
drop cascades to table quality_issue
drop cascades to table shortage_alert
```

- 6번: `DROP SCHEMA … CASCADE`는 스키마 안의 **모든** 테이블을 지웁니다. 반드시 `lab`인지 확인하고 실행하세요. `bom`이나 `hr`에 실행하면 원본이 모두 사라지고 `schema_postgres.sql`·`hr_postgres.sql`을 다시 적재해야 합니다.
- `NOT LIKE 't\_%'`는 DML·TCL 단원에서 `bom`에 만든 사본(`t_part_sourcing` 등)을 빼고 원본만 세는 조건입니다(`\_`는 「글자 그대로의 `_`」).
:::

:::teacher 강사 확인
- 6번 결과 12행은 본문(HR 사본 `t_emp`·`emp_ship` 등)·확인 문제·복습 1~5를 모두 실행했다는 전제입니다. 건너뛴 문제가 있으면 행 수가 12와 다릅니다(5-4 복습을 건너뛰면 `member`·`blog`가 남아 더 많습니다).
- DML·TCL 단원의 HR 사본(`hr.t_emp`, `hr.t_dept`, `hr.t_job_history`)과 생산 사본(`bom.t_…`)은 `lab`이 아니므로 `DROP SCHEMA lab`으로 지워지지 않습니다. 정리하려면 `DROP TABLE IF EXISTS hr.t_job_history, hr.t_emp, hr.t_dept;`처럼 스키마를 붙여 지웁니다.
- 4번의 두 건은 README 4장 **A4**·**A5**입니다. 실제 Day 4 7교시 종합 미니 과제에서 이 테이블 구조를 그대로 써도 됩니다.
- 5번의 12/4·250개는 README 4장 **A7**(컴프레서 on-hand 1,150, 12/4 결품)과 `production_plan`의 냉장고 12/1~12/4 계획(380·320·380·320)으로 계산한 값입니다. Day 3 Q11 결과표의 12/4 행과 같은지 수업 전 대조하세요.
:::

## 8. 정리

### 8-1. 오늘 배운 것 {keep}

:::summary
- **DDL**: 데이터를 담을 그릇(테이블)을 만들고(`CREATE`), 고치고(`ALTER`), 지우는(`DROP`, `TRUNCATE`) SQL입니다. 원본을 보호하려고 실습은 `lab` 스키마에서 합니다.
- **자료형**: 고정 길이 코드 `CHAR(n)`, 가변 길이 글 `VARCHAR(n)`/`TEXT`, 급여·비율 `NUMERIC(p,s)`, 날짜 `DATE`, 날짜+시각 `TIMESTAMP`. `VARCHAR(n)`은 **글자 수** 기준입니다.
- **NOT NULL / DEFAULT**: DEFAULT는 「값을 안 줬을 때」만 동작합니다. NULL을 직접 적으면 NULL이 들어갑니다.
- **이름 규칙**: 따옴표 없는 이름은 소문자로 바뀝니다. 영문 소문자와 `_`만 쓰고, 예약어는 피합니다.
- **CTAS**: `CREATE TABLE … AS SELECT`는 데이터와 컬럼만 복사하고 **제약조건은 복사하지 않습니다.**
- **제약조건**: PK(NULL·중복 불가), UNIQUE(중복 불가, NULL 허용), NOT NULL, CHECK(조건식이 거짓이면 거부, NULL이면 통과), FK(부모에 있는 값만, 부모 삭제도 막음, NULL은 검사하지 않음). FK가 가리키는 부모 컬럼은 PK 또는 UNIQUE여야 합니다.
- **제약조건 = 품질 규칙**: 나중에 거는 제약조건은 기존 행을 모두 검사하므로, 실패하면 그 자체가 확인할 데이터 발견입니다. `NOT VALID`로 새 행부터 막을 수 있습니다.
- **ALTER TABLE**: `ADD COLUMN`, `DROP COLUMN`, `ALTER COLUMN … TYPE / SET DEFAULT / SET NOT NULL`, `RENAME COLUMN`, `RENAME TO`, `ADD/DROP CONSTRAINT`.
- **DROP · TRUNCATE**: 참조되는 테이블은 지울 수도 비울 수도 없습니다. `CASCADE`는 규칙(FK)까지 함께 지웁니다. PostgreSQL의 TRUNCATE는 `BEGIN … ROLLBACK`으로 되돌릴 수 있습니다. 지우는 문장은 스키마를 붙여 씁니다.
- **판단 기록 테이블**: 대상·판단값·근거·판단 주체·시각·상태를 컬럼으로 두고, 자동 번호(`IDENTITY`), 기본값(`now()`, `'PENDING'`), CHECK(판단 주체·상태·승인 조건)로 업무 규칙을 DB에 새깁니다.
:::

### 8-2. 한 줄 퀴즈

:::quiz
Q. `writer VARCHAR(20) DEFAULT '미지정'` 컬럼에 `INSERT … (writer) VALUES (NULL)`을 실행하면 무엇이 저장되나요?
A. NULL입니다. DEFAULT는 컬럼 값을 아예 주지 않았을 때만 동작합니다.

Q. `CREATE TABLE t_emp AS SELECT * FROM hr.employees;`로 만든 사본에 같은 직원 행을 한 번 더 넣으면 어떻게 되나요?
A. 오류 없이 들어갑니다. CTAS는 PK 같은 제약조건을 복사하지 않기 때문입니다. 필요하면 `ALTER TABLE … ADD CONSTRAINT … PRIMARY KEY`로 다시 겁니다.

Q. `UNIQUE`가 걸린 `cert_no`에 NULL을 두 번 넣으면? PK라면?
A. UNIQUE는 NULL을 서로 같다고 보지 않아 두 번 다 들어갑니다. PK는 NOT NULL이 포함되어 있어 NULL 자체가 거부됩니다.

Q. 사본 `emp_ship`에 `CHECK (salary >= 2500)`을 추가하려는데 「violated by some row」 오류가 납니다. 다음에 할 일은?
A. `WHERE NOT (salary >= 2500)`으로 규칙을 어기는 행을 찾아 확인합니다(급여 2,100~2,400인 5명). 기존 행 검토 전에 새 행부터 막으려면 `NOT VALID`를 붙여 추가합니다.

Q. `DROP TABLE lab.t_dept CASCADE;` 실행 후 `edu_record` 테이블은 어떻게 되나요?
A. 테이블과 데이터는 남고, `t_dept`를 가리키던 FK 제약조건만 삭제됩니다. 그 결과 부서 번호에 아무 값이나 들어갈 수 있게 됩니다.

Q. `salary_proposal`에 `status = 'APPROVED'`인데 `reviewed_by`가 없는 행을 넣으면 어떻게 되나요? 왜 이런 제약조건을 두나요?
A. `salary_proposal_review_ck` 위반으로 거부됩니다. 사람(승인자)·승인 시각 없이 승인 상태가 되는 것, 즉 AI 판단이 사람 승인 없이 확정되는 것을 DB 차원에서 막기 위해서입니다.
:::
