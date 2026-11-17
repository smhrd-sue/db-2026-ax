---
label: 3. SELECT · WHERE
title: 원하는 데이터 꺼내기
---

# SELECT 기본

## 1. SQL 시작하기

### 1-1. SQL이란? {keep}

**SQL**(Structured Query Language) = **구조화된 질의 언어**. 데이터베이스에 “이 데이터를 꺼내 줘”라고 묻는 **표준 언어**입니다.

1장에서 그린 ERD가 **지도**라면, SQL은 그 지도를 보고 **필요한 데이터를 꺼내 오는 방법**입니다.

```flow 사람의 질문 → SQL → 결과
message-circle-question | 사람의 질문 | “100번 직원의 이름과 직책은?” | ivory
braces | SQL | SELECT … FROM … WHERE … | plum
database | DB | bom_lab · hr 스키마 | lime
table | 결과 | Steven King · AD_PRES | hot
```

### 1-1. 질문을 SQL로 바꾸기 {keep}

> 실행 전: `SET search_path TO hr;` — 이 단원의 예제는 HR 실습 데이터(`hr_postgres.sql`의 `hr` 스키마)로 실행합니다.

> 직원 테이블에서 직원ID가 `100`인 직원의 **이름**과 **직책**을 알려 줘!

```sql
SELECT first_name, last_name, job_id
FROM employees
WHERE employee_id = 100;
```

```result
| first_name | last_name | job_id |
| --- | --- | --- |
| Steven | King | AD_PRES |
```

> 1장 1-4에서 본 우아한형제들의 AI 데이터 분석가처럼, AI가 **자연어 질문을 SQL로 바꿔** DB에서 답을 꺼내는 일도 결국 이 문장을 만드는 일입니다. ==SQL을 읽을 줄 알아야 AI가 만든 SQL도 검증할 수 있습니다.==

### 1-2. SQL 문법의 종류 {keep}

```icons SQL 문법 다섯 가지
search | QUERY · 질의어 | 데이터 검색·조회 | hot | `SELECT`
shapes | DDL · 데이터 정의어 | 테이블 같은 구조를 만들고·바꾸고·지움 | plum | `CREATE` `ALTER` `DROP`
pencil | DML · 데이터 조작어 | 데이터를 넣고·고치고·지움 | lime | `INSERT` `UPDATE` `DELETE`
history | TCL · 트랜잭션 제어어 | 작업을 확정하거나 되돌림 | ivory | `COMMIT` `ROLLBACK`
lock | DCL · 데이터 제어어 | 권한을 주고 회수함 | rose | `GRANT` `REVOKE`
```

> **SELECT 문법만 잘 알아도 실무 SQL 쿼리의 대부분을 읽을 수 있습니다.** 오늘은 조회(QUERY)에만 집중합니다.

### 1-3. SQL 작성 규칙 네 가지

| # | 규칙 | 예 |
| --- | --- | --- |
| 1 | **대소문자를 구분하지 않습니다.** (키워드·테이블·컬럼 이름) <br>단, 작은따옴표 안의 **값**은 구분합니다(`'IT_PROG'` ≠ `'it_prog'`). | `SELECT EMPLOYEE_ID FROM EMPLOYEES` <br>= `select employee_id from employees` |
| 2 | 문장 끝에는 ==세미콜론 `;`==을 붙입니다. <br>문장이 끝났다는 표시입니다. | `SELECT * FROM jobs;` |
| 3 | 띄어쓰기·줄바꿈은 실행에 영향을 주지 않습니다. <br> → 읽기 좋게 줄을 나눠 씁니다. | 아래 「정석 SQL 문장」 |
| 4 | 주석: 한 줄은 `--`, 여러 줄은 `/* … */` | `-- 이 줄은 실행되지 않습니다` |

### 1-3. 대문자로 써도 결과는 소문자 {keep}

```sql
SELECT EMPLOYEE_ID, FIRST_NAME FROM EMPLOYEES WHERE EMPLOYEE_ID = 100;
```

```result
| employee_id | first_name |
| --- | --- |
| 100 | Steven |
```

> **결과의 컬럼 이름은 소문자**(`employee_id`)로 나옵니다. PostgreSQL은 따옴표 없이 쓴 이름을 **소문자로 바꿔서** 저장·비교하기 때문입니다. 그래서 이 수업은 ==SQL 키워드는 대문자, 테이블·컬럼 이름은 소문자==로 씁니다.

```sql 정석 SQL 문장 — 컬럼마다 한 줄, 쉼표는 앞에
SELECT employee_id
     , first_name
     , last_name
     , job_id
  FROM employees;
```

### 1-3. 작은따옴표 vs 큰따옴표 {keep}

:::error
값(문자열)은 ==작은따옴표 `'IT_PROG'`==, 이름(식별자)은 큰따옴표 `"…"`입니다. 값을 큰따옴표로 감싸면 PostgreSQL은 **컬럼 이름**으로 알아듣습니다.

```sql
SELECT first_name FROM employees WHERE job_id = "IT_PROG";
```

```error
ERROR:  column "IT_PROG" does not exist
```
:::

### 1-4. pgAdmin에서 실행하기 — 단축키 {keep}

| 하고 싶은 일 | pgAdmin 4 (Windows) |
| --- | --- |
| **커서가 있는 문장 하나** 실행 | **Alt + F5** (Execute query) |
| **스크립트 전체** 또는 **드래그한 부분** 실행 | **F5** (Execute script) |
| 선택한 줄 주석 처리 / 해제 | Ctrl + / |

> Alt + F5가 동작하지 않으면 실행할 문장을 **드래그한 뒤 F5**를 누릅니다.

:::teacher 강사 확인
- 위 단축키는 pgAdmin 최신 문서 기준입니다. 수업 PC에 설치된 pgAdmin 버전에서 Alt + F5가 동작하는지 미리 확인하세요.
- 2장에서는 「F5 또는 ▶」로 안내했습니다. 여러 문장을 한 창에 쓰고 하나씩 실행하는 실습이 많으므로 Alt + F5(또는 드래그 후 F5)를 이 시간에 정리해 주세요.
:::

### 1-5. 테이블 구조 보기 {keep}

쿼리를 쓰기 전에 테이블에 **어떤 컬럼이 있고 자료형이 무엇인지** 먼저 확인합니다. 두 가지 방법이 있습니다.

| 방법 | 어디서 | 하는 법 |
| --- | --- | --- |
| ① psql 메타 명령 | SQL Shell (psql) | `\d employees` |
| ② 왼쪽 트리 | pgAdmin | `bom_lab > Schemas > hr > Tables > employees > Columns` 펼치기 |

> `\d`는 2장에서 배운 **psql 메타 명령**이라 pgAdmin Query Tool에서는 실행되지 않습니다. psql에서 테이블을 찾지 못하면 `\d hr.employees`처럼 스키마 이름을 붙입니다.

### 1-5. \d employees 결과 {keep}

```psql
\d employees
```

```screen 결과 아래쪽에는 인덱스·PK·FK 목록도 나옵니다.
                          Table "hr.employees"
     Column     |         Type          | Collation | Nullable | Default
----------------+-----------------------+-----------+----------+---------
 employee_id    | numeric(6,0)          |           | not null |
 first_name     | character varying(20) |           |          |
 last_name      | character varying(25) |           | not null |
 email          | character varying(25) |           | not null |
 phone_number   | character varying(20) |           |          |
 hire_date      | date                  |           | not null |
 job_id         | character varying(10) |           | not null |
 salary         | numeric(8,2)          |           |          |
 commission_pct | numeric(2,2)          |           |          |
 manager_id     | numeric(6,0)          |           |          |
 department_id  | numeric(4,0)          |           |          |
```

### 1-5. 자료형 읽기 {keep}

```rows HR 데이터에서 쓰는 자료형
- | 구분 | 자료형 | 예
file-text~lime | 가변 길이 문자 | `character varying(n)` = `VARCHAR(n)` | `first_name VARCHAR(20)`, `job_id VARCHAR(10)`
ruler~plum | 고정 길이 문자 | `character(n)` = `CHAR(n)` | `countries.country_id CHAR(2)`
hash~rose | 숫자 | `numeric(p, s)`, `integer` | `salary NUMERIC(8,2)`, `employee_id NUMERIC(6,0)`
calendar~ivory | 날짜 | `date` | `hire_date`
```

### 1-6. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `part_master`(부품 마스터) 테이블의 구조를 확인한 뒤, 품번이 `ECP39799101`인 부품의 `part_no`, `description`, `description_kr`, `uit`를 조회하세요. (1-1 예제처럼 `WHERE`를 붙입니다. 품번은 문자이므로 작은따옴표로 감쌉니다.)

**[응용]** 아래 쿼리는 한글 품명이 「도어 가스켓」인 부품을 찾으려 했지만 오류가 납니다. 오류 메시지를 읽고 원인을 설명한 뒤, 고쳐서 실행하세요. (끝에 `ORDER BY part_no`를 붙이면 품번 순으로 정렬됩니다 — 3절에서 배웁니다.)

```sql
SELECT part_no, description_kr FROM part_master WHERE description_kr = "도어 가스켓";
```
:::

### 1-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
psql에서는 `\d bom.part_master`, pgAdmin에서는 `bom > Tables > part_master > Columns`로 구조를 확인합니다.

```sql
SELECT part_no, description, description_kr, uit
  FROM part_master
 WHERE part_no = 'ECP39799101';
```

```result
| part_no | description | description_kr | uit |
| --- | --- | --- | --- |
| ECP39799101 | Compressor,Reciprocating | 컴프레서 | D |
```
:::

### 1-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
`ERROR: column "도어 가스켓" does not exist` — 큰따옴표 `"도어 가스켓"`을 **컬럼 이름**으로 읽었기 때문입니다. 값은 작은따옴표로 감쌉니다.

```sql
SELECT part_no, description_kr
  FROM part_master
 WHERE description_kr = '도어 가스켓'
 ORDER BY part_no;
```

```result
| part_no | description_kr |
| --- | --- |
| MGK25528301 | 도어 가스켓 |
| MGK31172901 | 도어 가스켓 |
```
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 2. SELECT — 원하는 열(컬럼) 꺼내기

### 2-1. SQL 문장의 실행 순서 ⭐ {keep}

SQL은 **쓰는 순서**와 **실행되는 순서**가 다릅니다.

| 쓰는 순서 | 절 | 하는 일 | 실행 순서 |
| --- | --- | --- | --- |
| 1 | `SELECT` | 출력할 컬럼 | ==5== |
| 2 | `FROM` | 데이터를 가져올 테이블 | ==1== |
| 3 | `WHERE` | 원하는 행만 고르는 조건 | ==2== |
| 4 | `GROUP BY` | 특정 컬럼 기준으로 그룹화 | 3 |
| 5 | `HAVING` | 그룹에 조건 지정 | 4 |
| 6 | `ORDER BY` | 정렬 | ==6== |

```flow 실행되는 순서
table | FROM | 테이블 가져오기 | lime
filter | WHERE | 행 고르기 | lime
layers | GROUP BY | 묶기 | ivory
list-checks | HAVING | 그룹 고르기 | ivory
columns-3 | SELECT | 열 고르기 | plum
list | ORDER BY | 정렬 | hot
```

### 2-1. 실행 순서 따라가기 {keep}

```stepper
{
  "title": "영업부(80)가 아닌 직무 이력을 시작일 순으로 — 실제 실행 순서",
  "code": "SELECT employee_id, job_id, start_date\n  FROM job_history\n WHERE department_id <> 80\n ORDER BY start_date;",
  "steps": [
    {"line": 1, "note": "① FROM — job_history(직무 이력) 테이블 10행을 모두 가져옵니다.",
     "cols": ["employee_id", "job_id", "start_date", "department_id"],
     "rows": [["102","IT_PROG","2001-01-13","60"],["101","AC_ACCOUNT","1997-09-21","110"],["101","AC_MGR","2001-10-28","110"],["201","MK_REP","2004-02-17","20"],["114","ST_CLERK","2006-03-24","50"],["122","ST_CLERK","2007-01-01","50"],["200","AD_ASST","1995-09-17","90"],["176","SA_REP","2006-03-24","80"],["176","SA_MAN","2007-01-01","80"],["200","AC_ACCOUNT","2002-07-01","90"]]},
    {"line": 2, "note": "② WHERE — department_id가 80인 행(영업부 이력 2건)은 탈락하고 8행만 남습니다.", "dim": [7,8], "hot": ["department_id"]},
    {"line": 0, "note": "③ SELECT — 남은 행에서 employee_id, job_id, start_date 세 컬럼만 고릅니다.",
     "cols": ["employee_id", "job_id", "start_date"],
     "rows": [["102","IT_PROG","2001-01-13"],["101","AC_ACCOUNT","1997-09-21"],["101","AC_MGR","2001-10-28"],["201","MK_REP","2004-02-17"],["114","ST_CLERK","2006-03-24"],["122","ST_CLERK","2007-01-01"],["200","AD_ASST","1995-09-17"],["200","AC_ACCOUNT","2002-07-01"]], "hot": ["employee_id", "job_id", "start_date"]},
    {"line": 3, "note": "④ ORDER BY — 마지막으로 start_date(시작일) 순으로 정렬합니다.",
     "cols": ["employee_id", "job_id", "start_date"],
     "rows": [["200","AD_ASST","1995-09-17"],["101","AC_ACCOUNT","1997-09-21"],["102","IT_PROG","2001-01-13"],["101","AC_MGR","2001-10-28"],["200","AC_ACCOUNT","2002-07-01"],["201","MK_REP","2004-02-17"],["114","ST_CLERK","2006-03-24"],["122","ST_CLERK","2007-01-01"]], "hot": ["start_date"]}
  ]
}
```

> 오늘은 `SELECT` · `FROM` · `WHERE` · `ORDER BY` 네 개를 다룹니다. `GROUP BY` · `HAVING`은 6교시에서 배웁니다. 실행 순서는 2-6 별칭에서 **오류로 직접 확인**합니다.

### 2-2. 전체 컬럼 출력 — `*` {keep}

```sql
SELECT *
  FROM departments;
```

```result 총 27행 중 일부
| department_id | department_name | manager_id | location_id |
| --- | --- | --- | --- |
| 10 | Administration | 200 | 1700 |
| 20 | Marketing | 201 | 1800 |
| 30 | Purchasing | 114 | 1700 |
| … | … | … | … |
| 270 | Payroll | NULL | 1700 |
```

- `*`(애스터리스크) = **모든 컬럼**. 실행 순서: ① `departments` 테이블을 가져와서 ② 모든 컬럼을 출력합니다.
- 실무 테이블은 컬럼이 수십 개라 `*`는 **구조를 처음 볼 때**만 쓰고, 보통은 필요한 컬럼만 적습니다.

### 2-3. 원하는 컬럼만 출력 {keep}

```sql
SELECT employee_id
     , first_name
     , last_name
     , job_id
  FROM employees;
```

```result 결과 일부 (순서는 다를 수 있음)
| employee_id | first_name | last_name | job_id |
| --- | --- | --- | --- |
| 100 | Steven | King | AD_PRES |
| 101 | Neena | Kochhar | AD_VP |
| 102 | Lex | De Haan | AD_VP |
| 103 | Alexander | Hunold | IT_PROG |
| 104 | Bruce | Ernst | IT_PROG |
```

- 컬럼은 **쉼표로 구분**하고, **적은 순서대로** 출력됩니다.
- 컬럼 이름을 모르면 1-5의 `\d` 또는 pgAdmin 트리에서 확인합니다.

### 2-4. 중복 제거 — `DISTINCT` {keep}

`employees`는 107행입니다. 직원들이 소속된 부서(`department_id`)는 **몇 종류**일까요?

:::cols
```sql
SELECT DISTINCT department_id
  FROM employees
 ORDER BY department_id;
```

```result 총 12행
| department_id |
| --- |
| 10 |
| 20 |
| 30 |
| … |
| 100 |
| 110 |
| NULL |
```
:::

- 107행 → **12행**. `departments`에는 부서가 27개 있지만, 직원이 있는 부서는 11개뿐이라는 뜻입니다. 마지막 `NULL`은 **부서가 정해지지 않은 직원**이 있다는 표시입니다(NULL은 3-3에서 배웁니다).

### 2-4. 여러 컬럼에 DISTINCT {keep}

`DISTINCT` 뒤에 컬럼이 **여러 개**면, 그 **조합**이 같은 행을 하나로 합칩니다.

:::cols
```sql
SELECT DISTINCT department_id, job_id
  FROM employees
 ORDER BY department_id, job_id;
```

```result 앞 6행
| department_id | job_id |
| --- | --- |
| 10 | AD_ASST |
| 20 | MK_MAN |
| 20 | MK_REP |
| 30 | PU_CLERK |
| 30 | PU_MAN |
| 40 | HR_REP |
```
:::

> 정렬 없이 `SELECT DISTINCT department_id FROM employees;`만 실행하면 결과 순서가 섞여 나옵니다(예: 20, 50, 30, 110, 70 … 순). 순서가 필요하면 반드시 `ORDER BY`를 붙입니다.

### 2-5. SELECT 절에서 계산하기 — 산술 연산 {keep}

숫자형·날짜형 컬럼에는 `+ - * /` 연산을 쓸 수 있습니다.

```sql
SELECT employee_id
     , first_name
     , salary
     , salary * 12
     , salary + 500
  FROM employees
 WHERE department_id = 90
 ORDER BY employee_id;
```

```result
| employee_id | first_name | salary | ?column? | ?column? |
| --- | --- | --- | --- | --- |
| 100 | Steven | 24000.00 | 288000.00 | 24500.00 |
| 101 | Neena | 17000.00 | 204000.00 | 17500.00 |
| 102 | Lex | 17000.00 | 204000.00 | 17500.00 |
```

(`WHERE`는 4절, `ORDER BY`는 3절에서 배웁니다. 지금은 “부서 90 직원만 골라 직원ID 순으로 보였다”고 읽으면 됩니다.)

- 계산한 컬럼은 이름이 없어 `?column?`으로 나옵니다 → 2-6 **별칭**으로 해결합니다.
- `salary * 12`는 연봉, `salary + 500`은 월급을 500 올린 금액입니다.

### 2-5. 정수 ÷ 정수 = 몫만 남습니다 {keep}

:::error
날짜끼리 빼면 **일수(정수, `integer`)** 가 나옵니다. 정수 ÷ 정수(`365`)는 **소수점 아래를 버립니다.** 1497일 ÷ 365 = 4.10…이 아니라 `4`입니다.

```sql
SELECT employee_id, start_date, end_date
     , end_date - start_date           AS days
     , (end_date - start_date) / 365   AS a
     , (end_date - start_date) / 365.0 AS b
  FROM job_history
 WHERE employee_id = 101;
```

```result
| employee_id | start_date | end_date | days | a | b |
| --- | --- | --- | --- | --- | --- |
| 101 | 1997-09-21 | 2001-10-27 | 1497 | 4 | 4.1013698630136986 |
| 101 | 2001-10-28 | 2005-03-15 | 1234 | 3 | 3.3808219178082192 |
```

한쪽을 `365.0`처럼 소수로 쓰면 소수까지 계산됩니다. Day 3 소요량·재료비 계산에서 다시 만납니다.
:::

### 2-5. 날짜 + 숫자 = 날짜 {keep}

```sql
SELECT employee_id, hire_date, hire_date + 90
  FROM employees
 WHERE employee_id = 100;
```

```result
| employee_id | hire_date | ?column? |
| --- | --- | --- |
| 100 | 2003-06-17 | 2003-09-15 |
```

입사일에 90을 더하면 **90일 뒤 날짜**(예: 수습 기간이 끝나는 날)가 됩니다.

### 2-6. 별칭(Alias) — `AS` {keep}

컬럼에 **다른 이름**을 붙여 출력합니다. 방법은 네 가지입니다.

```sql
SELECT salary * 12 AS annual_salary       -- ① AS 별칭
     , salary * 12 AS "AnnualSalary"      -- ② AS "별칭"
     , salary * 12 연봉                    -- ③ 별칭 (AS 생략)
     , salary * 12 "연간 급여"             -- ④ "별칭" (AS 생략)
  FROM employees
 WHERE employee_id = 100;
```

```result
| annual_salary | AnnualSalary | 연봉 | 연간 급여 |
| --- | --- | --- | --- |
| 288000.00 | 288000.00 | 288000.00 | 288000.00 |
```

> 별칭에 띄어쓰기를 쓰지 않고 `annual_salary`처럼 **소문자 + 밑줄**로 쓰면 따옴표가 필요 없습니다.

### 2-6. 큰따옴표가 필요한 경우 {keep}

:::answer 큰따옴표 `" "` 가 필요한 경우 — 눌러서 보기
| 경우 | 따옴표 없이 | 결과 |
| --- | --- | --- |
| 띄어쓰기·특수문자가 있음 | `AS 연간 급여` | ==오류== `syntax error at or near "급여"` |
| 대문자를 살리고 싶음 | `AS AnnualSalary` | 컬럼 이름이 `annualsalary`(소문자)로 바뀜 |

```sql
SELECT salary * 12 AS AnnualSalary
  FROM employees
 WHERE employee_id = 100;
```

```result
| annualsalary |
| --- |
| 288000.00 |
```
:::

### 2-6. 실행 순서 확인 — WHERE에서는 별칭을 못 씁니다 ⭐ {keep}

```sql
SELECT employee_id, salary * 12 AS annual_salary
  FROM employees
 WHERE annual_salary >= 100000;
```

```error
ERROR:  column "annual_salary" does not exist
```

`WHERE`가 `SELECT`보다 **먼저 실행**되므로, `WHERE`를 실행하는 시점에는 별칭이 아직 없습니다. 반대로 `ORDER BY`는 `SELECT` 뒤에 실행되므로 별칭을 쓸 수 있습니다(3-1).

### 2-7. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `part_master`에서 부품의 단위(`uom`)가 **몇 종류** 쓰이고 있는지 중복 없이, 알파벳 순으로 조회하세요. (2-4 예제처럼 끝에 `ORDER BY uom`을 붙입니다.)

**[응용]** 달러(USD)로 사는 소싱(`part_sourcing`)의 `part_no`, `po_price`(단가), `moq`(최소 발주 수량)와 함께 **최소 발주 금액**(단가 × 최소 발주 수량)과 **10% 인상 후 단가**를 품번 순으로 출력하세요. 최소 발주 금액은 `min_order_amt`, 인상 후 단가는 `인상 후 단가`라는 별칭을 사용합니다. (WHERE는 4절에서 배우지만, `WHERE currency = 'USD'` 한 줄만 붙이면 됩니다. 정렬은 `ORDER BY part_no`.)
:::

### 2-7. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
68행 → **5행**. 단위 코드표 `code_uom`에는 단위가 7개 있지만, 실제 부품에는 5개만 쓰이고 있습니다(GR, LI는 쓰이지 않음).

```sql
SELECT DISTINCT uom
  FROM part_master
 ORDER BY uom;
```

```result
| uom |
| --- |
| EA |
| KG |
| MZ |
| SH |
| ST |
```
:::

### 2-7. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
별칭에 띄어쓰기가 있으므로 큰따옴표가 필요합니다. 통화가 `USD`이므로 금액도 모두 달러입니다.

```sql
SELECT part_no
     , po_price
     , moq
     , po_price * moq AS min_order_amt
     , po_price * 1.1 AS "인상 후 단가"
  FROM part_sourcing
 WHERE currency = 'USD'
 ORDER BY part_no;
```

```result
| part_no | po_price | moq | min_order_amt | 인상 후 단가 |
| --- | --- | --- | --- | --- |
| ECP39799101 | 48.50 | 200 | 9700.00 | 53.350 |
| EFN66589301 | 6.20 | 1 | 6.20 | 6.820 |
| EIC93178801 | 3.80 | 1000 | 3800.00 | 4.180 |
| EMT78269001 | 14.00 | 1 | 14.00 | 15.400 |
| MBR26166001 | 1.90 | 1000 | 1900.00 | 2.090 |
| MGL96663301 | 11.50 | 1 | 11.50 | 12.650 |
| RSS86949501 | 42.00 | 20 | 840.00 | 46.200 |
```
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 3. ORDER BY · LIMIT — 정렬하고, 몇 개만 보기

### 3-1. ORDER BY — 정렬 {keep}

| 방식 | 뜻 | 비고 |
| --- | --- | --- |
| `ASC` (Ascending) | 오름차순 1, 2, 3 … / A → Z / 과거 → 최근 | **기본값** (생략하면 ASC) |
| `DESC` (Descending) | 내림차순 … 3, 2, 1 / Z → A / 최근 → 과거 | |

- `ORDER BY`는 `SELECT … FROM … WHERE` **뒤에 쓰고**, `SELECT`보다 **나중에 실행**됩니다.

```sql
SELECT employee_id, first_name, hire_date
  FROM employees
 ORDER BY hire_date DESC, employee_id
 LIMIT 5;
```

(`LIMIT 5`는 정렬한 뒤 앞 5행만 남깁니다 — 3-2에서 배웁니다. 입사일이 같으면 직원ID 순입니다.)

```result
| employee_id | first_name | hire_date |
| --- | --- | --- |
| 167 | Amit | 2008-04-21 |
| 173 | Sundita | 2008-04-21 |
| 166 | Sundar | 2008-03-24 |
| 128 | Steven | 2008-03-08 |
| 165 | David | 2008-02-23 |
```

### 3-1. 여러 컬럼으로 정렬 {keep}

앞 컬럼 값이 같을 때 다음 컬럼으로 정렬합니다.

:::cols
```sql
SELECT employee_id, first_name, job_id, hire_date
  FROM employees
 WHERE department_id = 30
 ORDER BY job_id ASC, hire_date DESC;
```

```result
| employee_id | first_name | job_id | hire_date |
| --- | --- | --- | --- |
| 119 | Karen | PU_CLERK | 2007-08-10 |
| 118 | Guy | PU_CLERK | 2006-11-15 |
| 116 | Shelli | PU_CLERK | 2005-12-24 |
| 117 | Sigal | PU_CLERK | 2005-07-24 |
| 115 | Alexander | PU_CLERK | 2003-05-18 |
| 114 | Den | PU_MAN | 2002-12-07 |
```
:::

### 3-1. 별칭으로 정렬 {keep}

`ORDER BY`는 `SELECT` 다음에 실행되므로 별칭을 쓸 수 있습니다.

:::cols
```sql
SELECT employee_id, first_name, salary * 12 AS annual_salary
  FROM employees
 WHERE department_id = 100
 ORDER BY annual_salary DESC;
```

```result
| employee_id | first_name | annual_salary |
| --- | --- | --- |
| 108 | Nancy | 144096.00 |
| 109 | Daniel | 108000.00 |
| 110 | John | 98400.00 |
| 112 | Jose Manuel | 93600.00 |
| 111 | Ismael | 92400.00 |
| 113 | Luis | 82800.00 |
```
:::

### 3-2. LIMIT — 앞에서 몇 행만 {keep}

```sql
SELECT employee_id, first_name, salary
  FROM employees
 ORDER BY salary DESC, employee_id
 LIMIT 3;
```

```result
| employee_id | first_name | salary |
| --- | --- | --- |
| 100 | Steven | 24000.00 |
| 101 | Neena | 17000.00 |
| 102 | Lex | 17000.00 |
```

- `LIMIT n`은 **정렬이 끝난 뒤** 앞에서 n행만 남깁니다. 그래서 「상위 n개」를 구할 때는 ==`ORDER BY`와 함께== 씁니다.
- `ORDER BY` 없이 `LIMIT`만 쓰면 **아무 n행**이나 나옵니다.

### 3-3. NULL 맛보기 — 값이 비어 있다는 것 {keep}

> **NULL** = 데이터 값이 **완전히 비어 있는** 상태. 값이 존재하지 않거나 아직 정해지지 않은 것.

```icons NULL의 특징 세 가지
circle-help | ① 0 · '' · ' '은 NULL이 아님 | 숫자 `0`, 빈 문자열 `''`, 공백 `' '`은 **값이 있는 것** | ivory | 커미션 0% ≠ 커미션 없음
circle-x | ② 연산하면 결과도 NULL | NULL과 무엇을 계산해도 NULL | plum | `NULL * 1 = NULL`
ban | ③ `=`로 비교 불가 | `= NULL`은 0행. `IS NULL`을 씀(5-1) | hot | `WHERE commission_pct IS NULL`
```

### 3-3. NULL과 연산하면 NULL {keep}

```sql
SELECT employee_id, first_name, salary, commission_pct
     , salary * commission_pct AS commission
  FROM employees
 WHERE salary >= 13000
 ORDER BY employee_id;
```

```result
| employee_id | first_name | salary | commission_pct | commission |
| --- | --- | --- | --- | --- |
| 100 | Steven | 24000.00 | NULL | NULL |
| 101 | Neena | 17000.00 | NULL | NULL |
| 102 | Lex | 17000.00 | NULL | NULL |
| 145 | John | 14000.00 | 0.40 | 5600.0000 |
| 146 | Karen | 13500.00 | 0.30 | 4050.0000 |
| 201 | Michael | 13000.00 | NULL | NULL |
```

(급여 13000 이상만 골랐습니다 — `>=`는 4-2) 커미션 비율이 비어 있으면 계산 결과도 비었습니다. ==“커미션 0%”가 아니라 “값이 없다”==입니다.

:::teacher 강사 확인
- HR 데이터에서 `commission_pct`는 영업 조직(`SA_MAN`·`SA_REP`) 35명에게만 값이 있고, 나머지 72명은 NULL입니다. 여기서는 “NULL과 연산하면 NULL”만 보여 주세요. 생산 데이터의 **단가 NULL(심어 둔 이상 데이터 A4, `MFT43979901`)** 은 3-5 확인 문제 [응용]에서 만나고, 원인·영향 해석은 7교시 「단가 NULL 부품 찾기(A4)」 실습으로 넘깁니다.
- 결과표의 `NULL`은 설명을 위해 글자로 적은 것입니다. psql에서는 빈칸으로 보이고, pgAdmin에서는 NULL 표시로 보입니다. 수업 PC 화면으로 확인해 주세요.
:::

### 3-4. NULL은 어디로 정렬될까? {keep}

`commission_pct`(커미션 비율)는 영업 조직이 아니면 **비어 있습니다(NULL)**. PostgreSQL은 NULL을 ==가장 큰 값처럼== 취급합니다.

```sql
SELECT employee_id, first_name, commission_pct
  FROM employees
 WHERE salary >= 13000
 ORDER BY commission_pct, employee_id;
```

```result
| employee_id | first_name | commission_pct |
| --- | --- | --- |
| 146 | Karen | 0.30 |
| 145 | John | 0.40 |
| 100 | Steven | NULL |
| 101 | Neena | NULL |
| 102 | Lex | NULL |
| 201 | Michael | NULL |
```

### 3-4. NULLS FIRST · NULLS LAST {keep}

| 정렬 | NULL 위치 (기본) | 바꾸려면 |
| --- | --- | --- |
| `ASC` | 맨 뒤 | `ORDER BY commission_pct NULLS FIRST` |
| `DESC` | ==맨 앞== | `ORDER BY commission_pct DESC NULLS LAST` |

> “커미션 비율이 높은 직원을 위로” 보려고 `DESC`를 쓰면 NULL 4행이 **맨 위**에 옵니다. <br>이때 `DESC NULLS LAST`를 쓰면 John(0.40)·Karen(0.30)이 위로 올라옵니다(직접 실행해 확인해 보세요).

### 3-5. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `part_sourcing`에서 리드타임(`lead_time_days`)이 가장 긴 소싱 **5건**의 `part_no`, `vendor_code`, `lead_time_days`를 조회하세요. 리드타임이 같으면 품번 순으로 정렬합니다.

**[응용]** 원화(KRW)로 사는 소싱 중 단가(`po_price`)가 가장 높은 **3건**의 `part_no`, `vendor_code`, `po_price`를 조회하세요. 단가가 같으면 품번 순입니다. (`WHERE currency = 'KRW'` 한 줄을 붙입니다.)
힌트: `ORDER BY po_price DESC LIMIT 3`만 쓰면 어떤 행이 나오는지 먼저 실행해 보세요.
:::

### 3-5. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
```sql
SELECT part_no, vendor_code, lead_time_days
  FROM part_sourcing
 ORDER BY lead_time_days DESC, part_no
 LIMIT 5;
```

```result
| part_no | vendor_code | lead_time_days |
| --- | --- | --- |
| EIC93178801 | V1005 | 60 |
| ECP39799101 | V1004 | 50 |
| MGL96663301 | V1007 | 45 |
| RSS86949501 | V1007 | 45 |
| EFN66589301 | V1009 | 40 |
```
:::

### 3-5. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
`DESC`만 쓰면 단가가 비어 있는(NULL) `MFT43979901`(정수 필터)이 맨 위로 올라옵니다. `NULLS LAST`로 NULL을 뒤로 보냅니다.

```sql
SELECT part_no, vendor_code, po_price
  FROM part_sourcing
 WHERE currency = 'KRW'
 ORDER BY po_price DESC NULLS LAST, part_no
 LIMIT 3;
```

```result
| part_no | vendor_code | po_price |
| --- | --- | --- |
| MDR41841501 | V1001 | 61000.00 |
| EBA28941901 | V1003 | 41000.00 |
| EBA56264701 | V1003 | 38000.00 |
```
:::

:::teacher 강사 확인
- `MFT43979901`의 단가 NULL은 README 4장의 심어 둔 이상 데이터 **A4**입니다. 여기서는 “NULL이 DESC에서 맨 위로 온다”만 확인하고, 원인·영향 해석은 7교시 「단가 NULL 부품 찾기(A4)」로 넘기세요.
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 4. WHERE — 원하는 행(로우) 고르기

### 4-1. WHERE 절의 모양 {keep}

```text
SELECT   출력할 컬럼      ③
  FROM   테이블           ①
 WHERE   조건식           ②  ← 조건이 TRUE인 행만 남깁니다
```

```compare 행마다 조건을 검사합니다
circle-check | 조건이 TRUE || circle-x | 조건이 FALSE (또는 NULL)
filter | 결과에 **남음** || ban | 결과에서 **탈락**
```

### 4-1. 문자열 값으로 찾기 {keep}

```sql
SELECT employee_id, first_name, last_name, job_id
  FROM employees
 WHERE last_name = 'De Haan';
```

```result
| employee_id | first_name | last_name | job_id |
| --- | --- | --- | --- |
| 102 | Lex | De Haan | AD_VP |
```

- 문자열과 날짜 값은 ==작은따옴표==로 감쌉니다. 숫자는 그대로 씁니다.
- 문자열 비교는 **대소문자와 띄어쓰기까지 정확히** 같아야 합니다. (`'DeHaan'`으로 쓰면 0행)

### 4-2. 비교 연산자 {keep}

| 연산자 | 뜻 | 예 |
| --- | --- | --- |
| `=` | 같다 | `job_id = 'IT_PROG'` |
| `>` / `>=` | 크다(초과) / 크거나 같다(이상) | `salary >= 12000` |
| `<` / `<=` | 작다(미만) / 작거나 같다(이하) | `salary < 3000` |
| `<>` / `!=` | 같지 않다 | `location_id <> 1700` |

### 4-2. `=` 같다 {keep}

:::cols
```sql
SELECT employee_id, first_name, last_name, job_id
  FROM employees
 WHERE job_id = 'IT_PROG'
 ORDER BY employee_id;
```

```result
| employee_id | first_name | last_name | job_id |
| --- | --- | --- | --- |
| 103 | Alexander | Hunold | IT_PROG |
| 104 | Bruce | Ernst | IT_PROG |
| 105 | David | Austin | IT_PROG |
| 106 | Valli | Pataballa | IT_PROG |
| 107 | Diana | Lorentz | IT_PROG |
```
:::

> `IT_PROG`의 뜻은 `jobs` 테이블에 있습니다: **Programmer**. 코드 값은 그 뜻을 적어 둔 테이블과 함께 읽는 습관을 들이세요.

### 4-2. `>=` 이상 {keep}

:::cols
```sql
SELECT employee_id, first_name, salary
  FROM employees
 WHERE salary >= 12000
 ORDER BY salary DESC, employee_id;
```

```result
| employee_id | first_name | salary |
| --- | --- | --- |
| 100 | Steven | 24000.00 |
| 101 | Neena | 17000.00 |
| 102 | Lex | 17000.00 |
| 145 | John | 14000.00 |
| 146 | Karen | 13500.00 |
| 201 | Michael | 13000.00 |
| 108 | Nancy | 12008.00 |
| 205 | Shelley | 12008.00 |
| 147 | Alberto | 12000.00 |
```
:::

### 4-2. 날짜 비교 {keep}

날짜는 `'YYYY-MM-DD'` 형식의 문자로 씁니다.

:::cols
```sql
SELECT employee_id, first_name, hire_date
  FROM employees
 WHERE hire_date >= '2008-02-01'
 ORDER BY hire_date, employee_id;
```

```result
| employee_id | first_name | hire_date |
| --- | --- | --- |
| 183 | Girard | 2008-02-03 |
| 136 | Hazel | 2008-02-06 |
| 165 | David | 2008-02-23 |
| 128 | Steven | 2008-03-08 |
| 166 | Sundar | 2008-03-24 |
| 167 | Amit | 2008-04-21 |
| 173 | Sundita | 2008-04-21 |
```
:::

### 4-2. 날짜는 꼭 '연-월-일' 순서로 {keep}

:::error
`'05/12/31'`처럼 연도를 두 자리로 짧게 쓰면 **서버 설정에 따라 다른 날짜**로 읽힙니다. 우리 PC는 연/월/일 순서로 읽어 2005-12-31이 나오지만, 미국식(월/일/연) 설정 서버에서는 결과가 달라집니다.

```sql
SET datestyle TO 'ISO, MDY';    -- 미국식(월/일/연) 서버 흉내
SELECT '05/12/31'::date AS d;   -- ::date = 날짜로 바꾸기
RESET datestyle;                -- 원래 설정으로
```

```result
| d |
| --- |
| 2031-05-12 |
```

같은 글자가 **2031년 5월 12일**이 되었습니다. ==날짜는 항상 `'2005-12-31'`처럼 연-월-일 4자리 연도로== 쓰면 어떤 서버에서도 같은 날짜입니다.
:::

:::teacher 강사 확인
- 한국어 Windows에 기본값(Default locale)으로 설치한 PostgreSQL 18은 `SHOW datestyle;` = `ISO, YMD`이고, `SELECT '05/12/31'::date;`만 실행하면 **2005-12-31**이 나옵니다(검증 PC 기준). 먼저 이것을 보여 준 뒤 위 쿼리로 같은 글자가 2031-05-12로 바뀌는 것을 보여 주세요.
:::

### 4-3. 같지 않다 — 부정 비교 {keep}

:::cols
```sql
SELECT department_id, department_name, location_id
  FROM departments
 WHERE location_id <> 1700;
```

```result
| department_id | department_name | location_id |
| --- | --- | --- |
| 20 | Marketing | 1800 |
| 40 | Human Resources | 2400 |
| 50 | Shipping | 1500 |
| 60 | IT | 1400 |
| 70 | Public Relations | 2700 |
| 80 | Sales | 2500 |
```
:::

`location_id` 1700은 시애틀 본사입니다. 본사가 아닌 곳에 있는 부서 6개가 나왔습니다.

| 부정 연산자 | 설명 |
| --- | --- |
| `<>` | SQL 표준 표기 |
| `!=` | `<>`와 같음 |
| `NOT 조건` | 조건 앞에 붙여 뒤집기. `WHERE NOT location_id = 1700`은 위와 같은 6행 |

### 4-4. 논리 연산자 — AND, OR {keep}

```compare
link | AND · 그리고 || split | OR · 또는
circle-check | **모든** 조건이 TRUE일 때만 TRUE || circle-check | 조건 중 **하나라도** TRUE이면 TRUE
filter | 조건을 더할수록 결과가 **줄어듦** || layers | 조건을 더할수록 결과가 **늘어남**
```

### 4-4. AND로 좁히기 {keep}

```sql
SELECT employee_id, first_name, job_id, salary
  FROM employees
 WHERE job_id = 'SA_REP'
   AND salary >= 10000
 ORDER BY employee_id;
```

```result
| employee_id | first_name | job_id | salary |
| --- | --- | --- | --- |
| 150 | Peter | SA_REP | 10000.00 |
| 156 | Janette | SA_REP | 10000.00 |
| 162 | Clara | SA_REP | 10500.00 |
| 168 | Lisa | SA_REP | 11500.00 |
| 169 | Harrison | SA_REP | 10000.00 |
| 174 | Ellen | SA_REP | 11000.00 |
```

> 영업 사원(`SA_REP`) 30명 중 **급여가 10000 이상인 6명**만 남았습니다. 

### 4-5. 연산자 우선순위 — AND가 OR보다 먼저 ⭐ {keep}

수학에서 `1 + 2 * 3`은 곱셈을 먼저 하듯, SQL에서는 ==`AND`를 `OR`보다 먼저== 계산합니다.

| 순위 | 연산자 |
| --- | --- |
| 1 | `( )` 괄호 |
| 2 | 비교 연산자, SQL 연산자(`IN`, `BETWEEN`, `LIKE`, `IS NULL`) |
| 3 | `NOT` |
| 4 | `AND` |
| 5 | `OR` |

### 4-5. 괄호 없이 쓰면? {keep}

**질문:** 급여가 8000 이상인 직원 중에서 직책이 `IT_PROG` **또는** `FI_ACCOUNT`인 직원은?

```sql
SELECT employee_id, first_name, job_id, salary
  FROM employees
 WHERE job_id = 'IT_PROG' OR job_id = 'FI_ACCOUNT' AND salary >= 8000;
```

→ **7행**. 그런데 결과에 급여가 8000 미만인 직원이 섞여 있습니다.

```result 섞여 들어온 행
| employee_id | first_name | job_id | salary |
| --- | --- | --- | --- |
| 104 | Bruce | IT_PROG | 6000.00 |
| 105 | David | IT_PROG | 4800.00 |
| 106 | Valli | IT_PROG | 4800.00 |
| 107 | Diana | IT_PROG | 4200.00 |
```

`job_id = 'IT_PROG' OR (job_id = 'FI_ACCOUNT' AND salary >= 8000)`로 계산되어, `IT_PROG`인 직원은 급여와 상관없이 모두 들어왔습니다.

### 4-5. OR와 AND를 함께 쓸 때는 괄호 {keep}

```sql
SELECT employee_id, first_name, job_id, salary
  FROM employees
 WHERE (job_id = 'IT_PROG' OR job_id = 'FI_ACCOUNT')
   AND salary >= 8000;
```

→ **3행**, 모두 급여 8000 이상. ==OR와 AND를 함께 쓸 때는 항상 괄호==를 칩니다. (5-2의 `IN`을 쓰면 `job_id IN ('IT_PROG', 'FI_ACCOUNT')`로 더 짧게 쓸 수 있습니다.)

### [직접 해 보기] 4교시 {keep}

> `hr` 스키마의 테이블로 풉니다. 실행 전: `SET search_path TO hr;`

:::try
1. `locations`에서 **미국(US)에 있는 사무소**(`country_id = 'US'`)의 위치ID·도시·주(`state_province`)를 조회하세요.
2. `employees`에서 **재고 관리자**(`job_id = 'ST_MAN'`)의 직원ID·이름·성·급여·입사일을 **입사일 순**으로 조회하세요. 가장 먼저 입사한 재고 관리자는 누구인가요?
3. `employees`에서 **부서 80** 직원 중 **급여가 11,000 이상**인 직원을 급여가 높은 순(같으면 직원ID 순)으로 조회하세요. 급여 컬럼은 `급여`라는 별칭으로 출력합니다.
4. `job_history`에서 직무 이력을 **시작일 순**으로 **앞 5행만** 조회하세요.
:::

### [직접 해 보기] 4교시 — 예시 답안 {keep}

:::answer
```sql 1
SELECT location_id, city, state_province
  FROM locations
 WHERE country_id = 'US';
```

```sql 2
SELECT employee_id, first_name, last_name, salary, hire_date
  FROM employees
 WHERE job_id = 'ST_MAN'
 ORDER BY hire_date;
```

```result
| employee_id | first_name | last_name | salary | hire_date |
| --- | --- | --- | --- | --- |
| 122 | Payam | Kaufling | 7900.00 | 2003-05-01 |
| 120 | Matthew | Weiss | 8000.00 | 2004-07-18 |
| 121 | Adam | Fripp | 8200.00 | 2005-04-10 |
| 123 | Shanta | Vollman | 6500.00 | 2005-10-10 |
| 124 | Kevin | Mourgos | 5800.00 | 2007-11-16 |
```

```sql 3
SELECT employee_id, first_name, salary AS 급여
  FROM employees
 WHERE department_id = 80
   AND salary >= 11000
 ORDER BY salary DESC, employee_id;
```

```sql 4
SELECT employee_id, start_date, end_date, job_id
  FROM job_history
 ORDER BY start_date
 LIMIT 5;
```
:::

### 4-6. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `part_sourcing`에서 달러(`currency = 'USD'`)로 사고 리드타임이 45일 이상인 소싱의 `part_no`, `vendor_code`, `currency`, `lead_time_days`를 리드타임이 긴 순(같으면 품번 순)으로 조회하세요.

**[응용]** `part_master`에서 **2025년 7월 1일 이후** 등록된(`created_at`) 부품 중 UIT가 `T` **또는** `P`인(사내 조립품) 부품의 `part_no`, `description_kr`, `uit`, `created_at`을 등록일 순(같으면 품번 순)으로 조회하세요.
:::

### 4-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
4행. **해외에서 오래 걸려 들어오는 부품**입니다.

```sql
SELECT part_no, vendor_code, currency, lead_time_days
  FROM part_sourcing
 WHERE currency = 'USD'
   AND lead_time_days >= 45
 ORDER BY lead_time_days DESC, part_no;
```

```result
| part_no | vendor_code | currency | lead_time_days |
| --- | --- | --- | --- |
| EIC93178801 | V1005 | USD | 60 |
| ECP39799101 | V1004 | USD | 50 |
| MGL96663301 | V1007 | USD | 45 |
| RSS86949501 | V1007 | USD | 45 |
```
:::

### 4-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
5행. 괄호 없이 `… AND uit = 'T' OR uit = 'P'`로 쓰면 **10행**이 나옵니다. 7월 이전에 등록된 `P` 부품까지 모두 섞이기 때문입니다(4-5 우선순위).

```sql
SELECT part_no, description_kr, uit, created_at
  FROM part_master
 WHERE created_at >= '2025-07-01'
   AND (uit = 'T' OR uit = 'P')
 ORDER BY created_at, part_no;
```

```result
| part_no | description_kr | uit | created_at |
| --- | --- | --- | --- |
| ACP85953101 | 컨트롤 패널 조립체 | P | 2025-09-22 |
| ADU49470801 | 구동부 조립체 | T | 2025-10-11 |
| ACC12625601 | 냉동 사이클 조립체 | T | 2025-10-19 |
| MLN40306101 | 내상 라이너 | P | 2025-11-06 |
| MCB74311201 | 외함 캐비닛 | P | 2025-12-08 |
```
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

# WHERE(조건 심화)

## 5. SQL 연산자

### 5-1. IS NULL / IS NOT NULL {keep}

NULL은 `=`로 찾을 수 없습니다(3-3 ③).

```sql
SELECT employee_id
  FROM employees
 WHERE commission_pct = NULL;
```

→ **0행**. 오류는 나지 않지만 아무것도 나오지 않아 ==틀린 줄도 모르고 지나가기 쉽습니다.==

| 쓰는 법 | 뜻 | `employees.commission_pct` 결과 |
| --- | --- | --- |
| `WHERE commission_pct IS NULL` | 값이 비어 있는 행 | 72행 |
| `WHERE commission_pct IS NOT NULL` | 값이 있는 행 | 35행 |

### 5-1. IS NULL로 찾기 {keep}

:::cols
```sql
SELECT department_id, department_name, manager_id
  FROM departments
 WHERE manager_id IS NULL
 ORDER BY department_id;
```

```result 앞 5행 (총 16행)
| department_id | department_name | manager_id |
| --- | --- | --- |
| 120 | Treasury | NULL |
| 130 | Corporate Tax | NULL |
| 140 | Control And Credit | NULL |
| 150 | Shareholder Services | NULL |
| 160 | Benefits | NULL |
```
:::

> 부서장(`manager_id`)이 NULL이면 **부서장이 정해지지 않은 부서**라는 뜻입니다. 이 16개 부서에는 소속 직원도 없습니다(2-4: 직원이 있는 부서는 11개).

### 5-2. IN / NOT IN — 여러 값 중 하나 {keep}

| 쓰는 법 | 풀어 쓰면 |
| --- | --- |
| `컬럼 IN (값1, 값2, 값3)` | ==컬럼 = 값1 OR 컬럼 = 값2 OR 컬럼 = 값3== |
| `컬럼 NOT IN (값1, 값2, 값3)` | ==컬럼 <> 값1 AND 컬럼 <> 값2 AND 컬럼 <> 값3== |

:::cols
```sql
SELECT location_id, city, country_id
  FROM locations
 WHERE country_id IN ('JP', 'CN', 'IN')
 ORDER BY location_id;
```

```result
| location_id | city | country_id |
| --- | --- | --- |
| 1200 | Tokyo | JP |
| 1300 | Hiroshima | JP |
| 2000 | Beijing | CN |
| 2100 | Bombay | IN |
```
:::

### 5-2. IN과 NOT IN {keep}

```sql
SELECT employee_id, first_name, department_id
  FROM employees
 WHERE department_id IN (60, 90);
```

→ **8행** (60 IT 5명, 90 Executive 3명).

:::cols
```sql
SELECT employee_id, first_name, department_id
  FROM employees
 WHERE department_id NOT IN (30, 50, 60, 80, 90, 100)
 ORDER BY department_id, employee_id;
```

```result
| employee_id | first_name | department_id |
| --- | --- | --- |
| 200 | Jennifer | 10 |
| 201 | Michael | 20 |
| 202 | Pat | 20 |
| 203 | Susan | 40 |
| 204 | Hermann | 70 |
| 205 | Shelley | 110 |
| 206 | William | 110 |
```
:::

> 큰 여섯 부서를 뺀 나머지입니다. 그런데 부서가 없는(NULL) 178번 직원은 나오지 않습니다 → 다음 장.

### 5-2. IN과 NULL — 함정 두 가지 {keep}

> `count(*)`는 **행 수를 세는** 함수입니다(6교시에서 배웁니다). 지금은 “몇 행인지”만 보면 됩니다.

:::error
**① `IN`으로는 NULL을 찾을 수 없습니다.** 목록에 NULL을 넣어도 NULL인 행은 나오지 않습니다.

```sql
SELECT count(*) FROM employees WHERE department_id IN (90, NULL);       -- 3 (90인 행만)
```

NULL도 함께 찾으려면 `WHERE department_id = 90 OR department_id IS NULL`처럼 `IS NULL`을 따로 씁니다.

**② `NOT IN` 목록에 NULL이 하나라도 있으면 결과가 0행이 됩니다.**

```sql
SELECT count(*) FROM employees WHERE department_id NOT IN (50, 80);         -- 27
SELECT count(*) FROM employees WHERE department_id NOT IN (50, 80, NULL);   -- 0
```

`NOT IN`은 `<> 50 AND <> 80 AND <> NULL`인데, `<> NULL`은 TRUE가 될 수 없기 때문입니다. <br> 첫 번째 쿼리도 107 − 45(부서 50) − 34(부서 80) = 28이 아니라 27입니다. 부서가 NULL인 178번 직원이 **빠졌다**는 점에 주의하세요.
:::

### 5-3. BETWEEN A AND B — 범위 {keep}

```text
컬럼 BETWEEN A AND B   =   컬럼 >= A AND 컬럼 <= B     (A 이상 B 이하, 양 끝 포함)
```

:::cols
```sql
SELECT employee_id, first_name, salary
  FROM employees
 WHERE salary BETWEEN 11000 AND 12000
 ORDER BY salary, employee_id;
```

```result
| employee_id | first_name | salary |
| --- | --- | --- |
| 114 | Den | 11000.00 |
| 148 | Gerald | 11000.00 |
| 174 | Ellen | 11000.00 |
| 168 | Lisa | 11500.00 |
| 147 | Alberto | 12000.00 |
```
:::

11000과 12000이 **둘 다 포함**되었습니다.

### 5-3. 날짜 범위 {keep}

:::cols
```sql
SELECT employee_id, first_name, hire_date
  FROM employees
 WHERE hire_date BETWEEN '2008-01-01' AND '2008-01-31'
 ORDER BY hire_date, employee_id;
```

```result
| employee_id | first_name | hire_date |
| --- | --- | --- |
| 179 | Charles | 2008-01-04 |
| 199 | Douglas | 2008-01-13 |
| 164 | Mattea | 2008-01-24 |
| 149 | Eleni | 2008-01-29 |
```
:::

:::error 작은 값을 앞에
`BETWEEN 12000 AND 11000`처럼 순서를 바꾸면 오류 없이 **0행**이 나옵니다. 반드시 `BETWEEN 최솟값 AND 최댓값`.
:::

> HR 데이터의 날짜 컬럼(`hire_date`, `start_date`, `end_date`)은 모두 `date`(시각 없음)라 양 끝 날짜가 그대로 포함됩니다. 시각까지 있는 `timestamp` 컬럼은 Day 4 기록 테이블에서 다룹니다.

### 5-4. LIKE — 일부 문자로 찾기 {keep}

| 와일드카드 | 뜻 | 예 | 찾는 것 |
| --- | --- | --- | --- |
| `%` | 길이와 상관없이 **아무 글자들** (0글자 포함) | `'AD%'` | AD로 **시작** |
| | | `'%Manager'` | Manager로 **끝남** |
| | | `'%Account%'` | Account를 **포함** |
| `_` | 아무 글자 **딱 한 개** | `'___.___.____'` | 3자리.3자리.4자리 모양 |

### 5-4. ① 직책 코드 접두어로 찾기 {keep}

`job_id`는 `부서약어_직무` 형식입니다(AD = Administration, SA = Sales, ST = Stock …).

:::cols
```sql
SELECT employee_id, first_name, last_name, job_id
  FROM employees
 WHERE job_id LIKE 'AD%'
 ORDER BY employee_id;
```

```result
| employee_id | first_name | last_name | job_id |
| --- | --- | --- | --- |
| 100 | Steven | King | AD_PRES |
| 101 | Neena | Kochhar | AD_VP |
| 102 | Lex | De Haan | AD_VP |
| 200 | Jennifer | Whalen | AD_ASST |
```
:::

:::teacher 강사 확인
- `'AD_%'`로 써도 이 데이터에서는 같은 4행이 나옵니다. 다만 `_`는 와일드카드(아무 글자 한 개)라서 밑줄 문자 자체를 뜻하지 않습니다. 질문이 나오면 “`_`는 자리 하나”라는 것만 짚어 주세요(밑줄 자체를 찾는 `ESCAPE`는 다루지 않습니다).
:::

### 5-4. ② 직책명(job_title)으로 찾기 {keep}

`jobs` 테이블의 `job_title`은 영문 직책명입니다.

:::cols
```sql
SELECT job_id, job_title
  FROM jobs
 WHERE job_title LIKE '%Manager'
 ORDER BY job_id;
```

```result
| job_id | job_title |
| --- | --- |
| AC_MGR | Accounting Manager |
| FI_MGR | Finance Manager |
| MK_MAN | Marketing Manager |
| PU_MAN | Purchasing Manager |
| SA_MAN | Sales Manager |
| ST_MAN | Stock Manager |
```
:::

:::cols
```sql
SELECT job_id, job_title
  FROM jobs
 WHERE job_title LIKE '%Account%'
 ORDER BY job_id;
```

```result
| job_id | job_title |
| --- | --- |
| AC_ACCOUNT | Public Accountant |
| AC_MGR | Accounting Manager |
| FI_ACCOUNT | Accountant |
```
:::

### 5-4. ③ `_`로 자리 맞추기 · ④ NOT LIKE {keep}

```sql
SELECT employee_id, phone_number
  FROM employees
 WHERE phone_number LIKE '___.___.____';
```

→ **72행**. `515.123.4567` 모양만 나오고, 영업 조직 35명의 `011.44.1344.429268` 같은 국제 번호는 빠집니다.

`NOT LIKE`는 패턴에 **맞지 않는** 행을 고릅니다. (부서 50에서 사원 `…CLERK`이 아닌 직원)

:::cols
```sql
SELECT employee_id, first_name, job_id
  FROM employees
 WHERE department_id = 50
   AND job_id NOT LIKE '%CLERK'
 ORDER BY employee_id;
```

```result
| employee_id | first_name | job_id |
| --- | --- | --- |
| 120 | Matthew | ST_MAN |
| 121 | Adam | ST_MAN |
| 122 | Payam | ST_MAN |
| 123 | Shanta | ST_MAN |
| 124 | Kevin | ST_MAN |
```
:::

### 5-4. LIKE는 대소문자를 구분합니다 → ILIKE {keep}

:::error
```sql
SELECT count(*) FROM jobs WHERE job_title LIKE  '%manager%';   -- 0
SELECT count(*) FROM jobs WHERE job_title ILIKE '%manager%';   -- 6
```

데이터에는 `Manager`(대문자 M)로 저장되어 있어 `LIKE '%manager%'`는 0행입니다. PostgreSQL의 ==`ILIKE`는 대소문자를 무시==하고 찾습니다. (`ILIKE`는 PostgreSQL 전용 문법입니다.)
:::

:::try 생각해 보기
`job_title LIKE '%Manager'`(6행)로 찾은 직책만 “관리자”일까요? `WHERE manager_id = 103`을 실행해 보세요. 103번 Alexander의 직책은 `IT_PROG`(Programmer)이지만 직원 4명의 매니저입니다. “이름에 Manager가 있다”와 “실제로 관리한다”는 같은 말이 아닙니다. → 생산 데이터에도 같은 함정이 있습니다. 7절 복습 문제 6번(7-3)에서 확인합니다.
:::

### 5-5. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `part_sourcing`에서 품번이 `E`로 시작하고(전자부품) 단가(`po_price`)가 5,000 ~ 30,000 사이인 소싱의 `part_no`, `vendor_code`, `po_price`를 단가가 높은 순(같으면 품번 순)으로 조회하세요.

**[응용]** 서비스팀이 “서비스 전용 부품(`svc_code = 'R'`)이 **아닌** 부품 수”를 물었습니다. 아래 두 쿼리를 실행해 결과가 왜 다른지 설명하고, 서비스팀 질문에 맞는 쿼리는 어느 쪽인지 고르세요.

```sql
SELECT count(*) FROM part_master WHERE svc_code NOT IN ('R');
SELECT count(*) FROM part_master WHERE svc_code NOT IN ('R') OR svc_code IS NULL;
```
:::

### 5-5. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
6행

```sql
SELECT part_no, vendor_code, po_price
  FROM part_sourcing
 WHERE part_no LIKE 'E%'
   AND po_price BETWEEN 5000 AND 30000
 ORDER BY po_price DESC, part_no;
```

```result
| part_no | vendor_code | po_price |
| --- | --- | --- |
| EMT73633001 | V1009 | 28000.00 |
| EHN86058201 | V1011 | 10200.00 |
| EBA60141001 | V1003 | 9800.00 |
| EPM57964301 | V1011 | 9500.00 |
| EHN19575601 | V1011 | 8900.00 |
| EVL87758401 | V1011 | 6500.00 |
```
:::

### 5-5. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
첫 번째는 **6**(svc_code가 Z인 부품), 두 번째는 **59**입니다. 서비스 코드가 비어 있는(`svc_code`가 NULL, 서비스 부품이 아닌) 53개가 `NOT IN`에서는 빠지기 때문입니다(5-2). 이 53개도 “R이 아닌 부품”이므로 **두 번째 쿼리**가 질문에 맞습니다.

```sql
SELECT count(*)
  FROM part_master
 WHERE svc_code IS NULL;
```

```result
| count |
| --- |
| 53 |
```
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 6. CASE WHEN — 조건에 따라 라벨 붙이기

### 6-0. WHERE와 CASE는 무엇이 다를까? {keep}

`WHERE`는 **행을 고르는** 것이고, `CASE`는 행마다 **새 값을 만들어** 컬럼으로 붙이는 것입니다.

```text
CASE WHEN 조건1 THEN 값1
     WHEN 조건2 THEN 값2
     ELSE 그 밖의 값
END
```

- 위에서부터 차례로 검사해 **처음 TRUE가 된 THEN 값**을 씁니다.
- 어느 조건에도 맞지 않고 `ELSE`도 없으면 **NULL**이 됩니다.

### 6-1. 직책 → 직군 라벨 {keep}

HR 데이터에는 직군 컬럼이 없습니다. 직책 코드(`job_id`)를 보고 세 그룹으로 나눠 보겠습니다.

```icons 직책(job_id) → 직군
tag | 영업 | 고객에게 파는 일 | ivory | SA_MAN, SA_REP
warehouse | 물류 | 재고 관리·배송 | lime | ST_MAN, ST_CLERK, SH_CLERK
building | 사무 | 그 밖의 직책 | plum | AD_…, FI_…, IT_PROG …
```

### 6-1. CASE로 직군 붙이기 {keep}

:::cols
```sql
SELECT employee_id
     , first_name
     , job_id
     , CASE WHEN job_id IN ('SA_MAN', 'SA_REP')               THEN '영업'
            WHEN job_id IN ('ST_MAN', 'ST_CLERK', 'SH_CLERK') THEN '물류'
            ELSE '사무'
       END AS job_group
  FROM employees
 WHERE employee_id IN (100, 103, 121, 145, 150, 184, 206)
 ORDER BY employee_id;
```

```result
| employee_id | first_name | job_id | job_group |
| --- | --- | --- | --- |
| 100 | Steven | AD_PRES | 사무 |
| 103 | Alexander | IT_PROG | 사무 |
| 121 | Adam | ST_MAN | 물류 |
| 145 | John | SA_MAN | 영업 |
| 150 | Peter | SA_REP | 영업 |
| 184 | Nandita | SH_CLERK | 물류 |
| 206 | William | AC_ACCOUNT | 사무 |
```
:::

> Day 2에서는 `jobs`와 **JOIN**해 직책명(`job_title`)을 직접 가져오는 방법을 배웁니다. 지금은 직군 기준을 CASE에 직접 적은 것입니다.

### 6-2. 지역 번호 → 지역 이름 {keep}

:::cols
```sql
SELECT country_id
     , country_name
     , region_id
     , CASE region_id WHEN 1 THEN '유럽'
                      WHEN 2 THEN '미주'
                      WHEN 3 THEN '아시아'
                      WHEN 4 THEN '중동·아프리카'
                      ELSE '기타'
       END AS 지역
  FROM countries
 ORDER BY country_id;
```

```result 앞 6행
| country_id | country_name | region_id | 지역 |
| --- | --- | --- | --- |
| AR | Argentina | 2 | 미주 |
| AU | Australia | 3 | 아시아 |
| BE | Belgium | 1 | 유럽 |
| BR | Brazil | 2 | 미주 |
| CA | Canada | 2 | 미주 |
| CH | Switzerland | 1 | 유럽 |
```
:::

→ 25행: 유럽 8 · 미주 5 · 아시아 6 · 중동·아프리카 6.

:::teacher 강사 확인
- `region_id`의 영문 이름은 `regions` 테이블(1 Europe, 2 Americas, 3 Asia, 4 Middle East and Africa)에 있습니다. 여기서는 한글 이름을 CASE로 직접 붙였습니다. Day 2에서 `regions`와 JOIN하면 이름을 직접 가져올 수 있습니다.
- `ELSE '기타'`는 지금 데이터에서는 나오지 않습니다. 새 지역 코드가 생겼을 때 NULL 대신 「기타」가 나오도록 둔 것입니다.
:::

### 6-3. 커미션 대상 / 미대상 라벨 {keep}

```sql
SELECT employee_id
     , first_name
     , commission_pct
     , CASE WHEN commission_pct IS NULL THEN '미대상' ELSE '대상' END AS 커미션
  FROM employees
 ORDER BY employee_id;
```

→ 107행: 대상 35 · 미대상 72. CASE 안에서도 NULL은 `= NULL`이 아니라 `IS NULL`로 검사합니다. 6교시에서 이 라벨로 `GROUP BY`하면 커미션 대상/미대상 인원을 바로 구할 수 있습니다.

### 6-4. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `part_master`에서 분류(`class_lv2`)가 `EBA`(PCB 조립체)·`EMT`(모터류)인 부품의 `part_no`, `description_kr`, `svc_code`와, 서비스 코드가 있으면 `서비스`, 없으면 `일반`인 `svc_yn` 컬럼을 품번 순으로 출력하세요.

**[응용]** 협력사 `V1006`(우성사출)에서 사는 소싱(`part_sourcing`)에 단가 등급을 붙이려 합니다. 단가 20,000 이상은 `A`, 5,000 이상은 `B`, 나머지는 `C`입니다. `part_no`, `po_price`, `grade`를 단가가 높은 순으로 출력하세요.
:::

### 6-4. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
6행 (서비스 3 · 일반 3). 서비스 코드가 없다는 것은 NULL이므로 `IS NULL`로 검사합니다.

```sql
SELECT part_no
     , description_kr
     , svc_code
     , CASE WHEN svc_code IS NULL THEN '일반' ELSE '서비스' END AS svc_yn
  FROM part_master
 WHERE class_lv2 IN ('EBA', 'EMT')
 ORDER BY part_no;
```

```result
| part_no | description_kr | svc_code | svc_yn |
| --- | --- | --- | --- |
| EBA28941901 | 메인 PCB 조립체 | R | 서비스 |
| EBA56264701 | 메인 PCB 조립체 | R | 서비스 |
| EBA60141001 | 디스플레이 PCB | NULL | 일반 |
| EMT68237401 | DD 모터 | R | 서비스 |
| EMT73633001 | 스테이터 | NULL | 일반 |
| EMT78269001 | 로터 | NULL | 일반 |
```
:::

### 6-4. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
6행. 위에서부터 검사하므로 **큰 기준부터** 씁니다. 순서를 `>= 5000`부터 쓰면 23000도 `B`가 됩니다.

```sql
SELECT part_no
     , po_price
     , CASE WHEN po_price >= 20000 THEN 'A'
            WHEN po_price >= 5000  THEN 'B'
            ELSE 'C'
       END AS grade
  FROM part_sourcing
 WHERE vendor_code = 'V1006'
 ORDER BY po_price DESC;
```

```result
| part_no | po_price | grade |
| --- | --- | --- |
| MTB81885601 | 23000.00 | A |
| AHD26818801 | 9800.00 | B |
| MCK37745101 | 5600.00 | B |
| MSH53664101 | 5400.00 | B |
| MDM76541901 | 3900.00 | C |
| MCK18701201 | 1200.00 | C |
```
:::

> 이어지는 7절 복습 문제도 `bom` 스키마로 풉니다.

## 7. 복습 문제

### 7-0. 복습 문제 안내 {keep}

> 범위: SELECT · ORDER BY · LIMIT · WHERE 전체 · CASE. `bom` 스키마의 테이블로 풀어 주세요(실행 전: `SET search_path TO bom;`). (출력 순서는 `ORDER BY` 기준)

```icons 여섯 문항
search | 1 · LIKE + AND | M으로 시작하는 수입 구매품 | rose
circle-help | 2 · IS NOT NULL | 서비스 코드가 정해진 기구부품 | plum
ruler | 3 · BETWEEN | 원화·리드타임 10~14일·단가 1만 이상 | lime
globe | 4 · IN | CN·TW·VN 협력사 | ivory
calendar | 5 · (심화) 날짜 범위 | LINE-A 계획 450 이상 | plum
tag | 6 · (심화) LIKE·괄호·CASE | 이름은 Assembly인데 구매품 | hot
```

### 7-1. 복습 1 · 2 {keep}

**1.** `part_master`에서 품번이 대문자 M으로 시작하면서 UIT가 D인 부품의 `part_no`, `description_kr`, `uit`를 품번 순으로 출력하세요. [힌트: LIKE, AND]

```result 출력 결과 (총 2행)
| part_no | description_kr | uit |
| --- | --- | --- |
| MBR26166001 | 볼 베어링 | D |
| MGL96663301 | 도어 글라스 | D |
```

**2.** `part_master`에서 기구부품(`class_lv1 = 'M'`) 중 서비스 코드(`svc_code`)가 정해진 부품의 `part_no`, `description_kr`, `svc_code`, `svc_location_no`를 품번 순으로 출력하세요. [힌트: IS NULL / IS NOT NULL]

```result 출력 결과 (총 7행)
| part_no | description_kr | svc_code | svc_location_no |
| --- | --- | --- | --- |
| MDM76541901 | 댐퍼 | R | 602A |
| MFT20558801 | 린트 필터 | Z | 903A |
| MFT43979901 | 정수 필터 | Z | 502A |
| … | | | |
| MSH53664101 | 선반 | Z | 501A |
```

### 7-2. 복습 3 · 4 {keep}

**3.** `part_sourcing`에서 원화(KRW)로 사고, 리드타임이 10~14일이며, 단가가 10,000 이상인 행의 `part_no`, `vendor_code`, `po_price`, `lead_time_days`를 단가가 높은 순으로 출력하세요. [힌트: BETWEEN]

```result 출력 결과 (총 5행)
| part_no | vendor_code | po_price | lead_time_days |
| --- | --- | --- | --- |
| MTB81885601 | V1006 | 23000.00 | 14 |
| MCK79020001 | V1001 | 21000.00 | 14 |
| MEV24806601 | V1011 | 17500.00 | 14 |
| MCD80603101 | V1011 | 12800.00 | 14 |
| EHN86058201 | V1011 | 10200.00 | 14 |
```

**4.** `vendor`에서 국가가 CN, TW, VN인 협력사의 `vendor_code`, `vendor_name`, `country`, `main_item`을 협력사 코드 순으로 출력하세요. [힌트: IN]

```result 출력 결과 (총 3행)
| vendor_code | vendor_name | country | main_item |
| --- | --- | --- | --- |
| V1004 | AsiaComp Co., Ltd. | CN | 컴프레서 |
| V1005 | NanoChip Semiconductor | TW | 반도체 |
| V1009 | Pacific Motor Parts | VN | 모터 부품·베어링 |
```

### 7-3. 복습 5 · 6 (심화) {keep}

**5.** (심화) `production_plan`에서 LINE-A의 2026-12-08 ~ 2026-12-11 계획 중 계획 수량이 450 이상인 날의 `plan_date`, `line_code`, `plan_qty`를 계획일 순으로 출력하세요.

```result 출력 결과 (총 2행)
| plan_date | line_code | plan_qty |
| --- | --- | --- |
| 2026-12-08 | LINE-A | 480 |
| 2026-12-11 | LINE-A | 460 |
```

**6.** (심화) `part_master`에서 영문 품명(`description`)에 'Assembly'가 들어가는데 UIT가 G 또는 D인(국내·수입 구매품) 부품의 `part_no`, `description`, `uit`와 CASE로 만든 `make_buy` 라벨을 품번 순으로 출력하세요. `make_buy`는 `code_uit`의 `classification` 기준으로 T·P·S·M·R이면 `Make`, G·D·X이면 `Buy`, 그 밖은 `완제품`입니다. [힌트: LIKE, 괄호, CASE]

```result 출력 결과 (총 8행)
| part_no | description | uit | make_buy |
| --- | --- | --- | --- |
| EBA28941901 | PCB Assembly,Main | G | Buy |
| EBA56264701 | PCB Assembly,Main | G | Buy |
| EBA60141001 | PCB Assembly,Display | G | Buy |
| … | | | |
| MSH53664101 | Shelf Assembly | G | Buy |
```

### 7-4. 복습 1 · 2 답 {keep}

:::answer 복습 1 · 2 예시 답안
```sql 1
SELECT part_no, description_kr, uit
  FROM part_master
 WHERE part_no LIKE 'M%'
   AND uit = 'D'
 ORDER BY part_no;
```

```sql 2
SELECT part_no, description_kr, svc_code, svc_location_no
  FROM part_master
 WHERE class_lv1 = 'M'
   AND svc_code IS NOT NULL
 ORDER BY part_no;
```
:::

### 7-5. 복습 3 · 4 답 {keep}

:::answer 복습 3 · 4 예시 답안
```sql 3
SELECT part_no, vendor_code, po_price, lead_time_days
  FROM part_sourcing
 WHERE currency = 'KRW'
   AND lead_time_days BETWEEN 10 AND 14
   AND po_price >= 10000
 ORDER BY po_price DESC;
```

```sql 4
SELECT vendor_code, vendor_name, country, main_item
  FROM vendor
 WHERE country IN ('CN', 'TW', 'VN')
 ORDER BY vendor_code;
```
:::

### 7-6. 복습 5 · 6 답 {keep}

:::answer 복습 5 · 6 예시 답안
```sql 5
SELECT plan_date, line_code, plan_qty
  FROM production_plan
 WHERE line_code = 'LINE-A'
   AND plan_date BETWEEN '2026-12-08' AND '2026-12-11'
   AND plan_qty >= 450
 ORDER BY plan_date;
```

```sql 6
SELECT part_no
     , description
     , uit
     , CASE WHEN uit IN ('T', 'P', 'S', 'M', 'R') THEN 'Make'
            WHEN uit IN ('G', 'D', 'X')           THEN 'Buy'
            ELSE '완제품'
       END AS make_buy
  FROM part_master
 WHERE description LIKE '%Assembly%'
   AND (uit = 'G' OR uit = 'D')
 ORDER BY part_no;
```

- 6번에서 괄호를 빼고 `… AND uit = 'G' OR uit = 'D'`로 쓰면 **15행**이 나옵니다. 이름에 Assembly가 없는 UIT D 부품 7개가 섞이기 때문입니다(4-5 우선순위).
- 6번 결과의 의미: 이름은 **조립체(Assembly)** 지만 사내에서 만들지 않고 **사 오는** 부품이 8개 있습니다. 이름만 보고 판단하지 말고 ==UIT 코드로 확인==해야 하는 이유입니다(5-4 「생각해 보기」의 직책명과 같은 이야기).
:::

## 8. 정리

### 8-1. 오늘 배운 것 {keep}

:::summary
- **SQL 실행 순서**: `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY`. 그래서 `WHERE`에서는 별칭을 못 쓰고, `ORDER BY`에서는 쓸 수 있습니다.
- **SELECT**: `*` 전체 / 컬럼 나열 / `DISTINCT` 중복 제거 / 산술 연산(정수 ÷ 정수는 몫만) / 별칭 `AS`(띄어쓰기·대문자는 `" "`).
- **ORDER BY**: 기본 ASC. PostgreSQL에서 NULL은 가장 큰 값 → `NULLS FIRST / LAST`로 조정. **LIMIT**은 `ORDER BY`와 함께.
- **WHERE**: 비교(`= <> > >= < <=`), 논리(`AND`가 `OR`보다 먼저 → 괄호), `IS NULL`, `IN`, `BETWEEN`(양 끝 포함), `LIKE`(`%`, `_`) / `ILIKE`.
- **NULL**: `= NULL`은 0행, `IS NULL`로 찾기. `IN`·`NOT IN`과 함께 쓸 때 주의.
- **CASE WHEN**: 조건에 따라 직군(영업/물류/사무), 지역 이름, 커미션 대상/미대상 같은 **라벨 컬럼**을 만듭니다.
- 예제는 **HR 데이터**(`hr`)로 익히고, 확인·복습 문제는 **생산 데이터**(`bom`)로 같은 문법을 다시 써 봤습니다.
:::

### 8-2. 마무리 퀴즈

:::quiz
Q. `SELECT employee_id, salary * 12 AS annual FROM employees WHERE annual > 100000;`이 오류가 나는 이유는?
A. `WHERE`가 `SELECT`보다 먼저 실행되어, `WHERE` 시점에는 별칭 `annual`이 아직 없기 때문입니다. `WHERE salary * 12 > 100000`으로 씁니다.

Q. `WHERE commission_pct = NULL`의 결과는? 어떻게 고쳐야 하나요?
A. 오류 없이 0행이 나옵니다. NULL은 `=`로 비교할 수 없으므로 `WHERE commission_pct IS NULL`로 씁니다.

Q. `WHERE job_id = 'IT_PROG' OR job_id = 'FI_ACCOUNT' AND salary >= 8000`은 어떤 순서로 계산되나요?
A. `AND`를 먼저 계산해 `job_id = 'IT_PROG' OR (job_id = 'FI_ACCOUNT' AND salary >= 8000)`이 됩니다. 의도가 “급여 8000 이상 중 IT_PROG 또는 FI_ACCOUNT”라면 `(job_id = 'IT_PROG' OR job_id = 'FI_ACCOUNT') AND salary >= 8000`처럼 괄호를 칩니다.

Q. `(end_date - start_date) / 365`가 1497일에 대해 4를 돌려주는 이유와, 소수까지 구하는 방법은?
A. 날짜끼리 뺀 일수(정수) ÷ 정수라 몫만 남기 때문입니다. `(end_date - start_date) / 365.0`처럼 한쪽을 소수로 씁니다.

Q. 직책명(`job_title`)에 `manager`가 들어간 직책을 대소문자와 상관없이 찾으려면?
A. `WHERE job_title ILIKE '%manager%'` (PostgreSQL의 `ILIKE`)
:::
