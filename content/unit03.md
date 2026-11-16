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
message-circle-question | 사람의 질문 | “ECP39799101의 품명과 UIT는?” | ivory
braces | SQL | SELECT … FROM … WHERE … | plum
database | DB | bom_lab | lime
table | 결과 | 컴프레서 · D | hot
```

### 1-1. 질문을 SQL로 바꾸기 {keep}

> 부품 마스터에서 품번이 `ECP39799101`인 부품의 **한글 품명**과 **UIT**를 알려 줘!

```sql
SELECT description_kr, uit
FROM part_master
WHERE part_no = 'ECP39799101';
```

```result
| description_kr | uit |
| --- | --- |
| 컴프레서 | D |
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
| 1 | **대소문자를 구분하지 않습니다.** (키워드·테이블·컬럼 이름) <br>단, 작은따옴표 안의 **값**은 구분합니다(`'D'` ≠ `'d'`). | `SELECT PART_NO FROM PART_MASTER` <br>= `select part_no from part_master` |
| 2 | 문장 끝에는 ==세미콜론 `;`==을 붙입니다. <br>문장이 끝났다는 표시입니다. | `SELECT * FROM vendor;` |
| 3 | 띄어쓰기·줄바꿈은 실행에 영향을 주지 않습니다. <br> → 읽기 좋게 줄을 나눠 씁니다. | 아래 「정석 SQL 문장」 |
| 4 | 주석: 한 줄은 `--`, 여러 줄은 `/* … */` | `-- 이 줄은 실행되지 않습니다` |

### 1-3. 대문자로 써도 결과는 소문자 {keep}

```sql
SELECT PART_NO, DESCRIPTION_KR FROM PART_MASTER WHERE PART_NO = 'ECP39799101';
```

```result
| part_no | description_kr |
| --- | --- |
| ECP39799101 | 컴프레서 |
```

> **결과의 컬럼 이름은 소문자**(`part_no`)로 나옵니다. PostgreSQL은 따옴표 없이 쓴 이름을 **소문자로 바꿔서** 저장·비교하기 때문입니다. 그래서 이 수업은 ==SQL 키워드는 대문자, 테이블·컬럼 이름은 소문자==로 씁니다.

```sql 정석 SQL 문장 — 컬럼마다 한 줄, 쉼표는 앞에
SELECT part_no
     , description_kr
     , uom
     , uit
  FROM part_master;
```

### 1-3. 작은따옴표 vs 큰따옴표 {keep}

:::error
값(문자열)은 ==작은따옴표 `'D'`==, 이름(식별자)은 큰따옴표 `"…"`입니다. 값을 큰따옴표로 감싸면 PostgreSQL은 **컬럼 이름**으로 알아듣습니다.

```sql
SELECT part_no FROM part_master WHERE uit = "D";
```

```error
ERROR:  column "D" does not exist
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
| ① psql 메타 명령 | SQL Shell (psql) | `\d part_master` |
| ② 왼쪽 트리 | pgAdmin | `bom_lab > Schemas > bom > Tables > part_master > Columns` 펼치기 |

> `\d`는 2장에서 배운 **psql 메타 명령**이라 pgAdmin Query Tool에서는 실행되지 않습니다. psql에서 테이블을 찾지 못하면 `\d bom.part_master`처럼 스키마 이름을 붙입니다.

### 1-5. \d part_master 결과 {keep}

```psql
\d part_master
```

```screen 결과 아래쪽에는 PK·FK 목록도 나옵니다(1장 7-4 FK 정리표와 같은 내용).
                     Table "bom.part_master"
     Column      |     Type      | Collation | Nullable | Default
-----------------+---------------+-----------+----------+---------
 part_no         | character(11) |           | not null |
 description     | text          |           | not null |
 description_kr  | text          |           |          |
 class_lv1       | character(1)  |           | not null |
 class_lv2       | character(3)  |           | not null |
 tech_spec       | text          |           |          |
 uom             | character(2)  |           |          |
 uit             | character(1)  |           |          |
 status_code     | smallint      |           |          |
 svc_code        | character(1)  |           |          |
 svc_location_no | text          |           |          |
 created_at      | date          |           |          |
```

### 1-5. 자료형 읽기 {keep}

```rows 이 데이터셋에서 쓰는 자료형
- | 구분 | 자료형 | 예
ruler~plum | 고정 길이 문자 | `character(n)` = `CHAR(n)` | `part_no CHAR(11)`
file-text~lime | 가변 길이 문자 | `text` | `description`
hash~rose | 숫자 | `numeric(p, s)`, `smallint`, `integer` | `po_price NUMERIC(12,2)`, `lead_time_days SMALLINT`
calendar~ivory | 날짜 | `date` | `created_at`
```

### 1-6. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마)

:::try
**[복습]** `employees` 테이블의 구조를 확인한 뒤, 직원ID가 100인 직원의 `employee_id`, `first_name`, `last_name`, `hire_date`를 조회하세요. (1-1 예제처럼 `WHERE employee_id = 100`을 붙입니다.)

**[응용]** 아래 쿼리는 성(`last_name`)이 King인 직원을 찾으려 했지만 오류가 납니다. 오류 메시지를 읽고 원인을 설명한 뒤, 고쳐서 실행하세요. (끝에 `ORDER BY first_name`을 붙이면 이름 순으로 정렬됩니다 — 3절에서 배웁니다.)

```sql
SELECT first_name, last_name FROM employees WHERE last_name = "King";
```
:::

### 1-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
psql에서는 `\d hr.employees`, pgAdmin에서는 `hr > Tables > employees > Columns`로 구조를 확인합니다.

```sql
SELECT employee_id, first_name, last_name, hire_date
  FROM employees
 WHERE employee_id = 100;
```

```result
| employee_id | first_name | last_name | hire_date |
| --- | --- | --- | --- |
| 100 | Steven | King | 2003-06-17 |
```
:::

### 1-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
`ERROR: column "King" does not exist` — 큰따옴표 `"King"`을 **컬럼 이름**으로 읽었기 때문입니다. 값은 작은따옴표로 감쌉니다.

```sql
SELECT first_name, last_name
  FROM employees
 WHERE last_name = 'King'
 ORDER BY first_name;
```

```result
| first_name | last_name |
| --- | --- |
| Janette | King |
| Steven | King |
```
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

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
  "title": "해외 협력사를 이름 순으로 — 실제 실행 순서",
  "code": "SELECT vendor_code, vendor_name\n  FROM vendor\n WHERE country <> 'KR'\n ORDER BY vendor_name;",
  "steps": [
    {"line": 1, "note": "① FROM — vendor 테이블 12행을 모두 가져옵니다.",
     "cols": ["vendor_code", "vendor_name", "country"],
     "rows": [["V1001","한빛정밀(주)","KR"],["V1002","대양화학(주)","KR"],["V1003","세진전자(주)","KR"],["V1004","AsiaComp Co., Ltd.","CN"],["V1005","NanoChip Semiconductor","TW"],["V1006","우성사출(주)","KR"],["V1007","Global Steel Trading","JP"],["V1008","동아포장(주)","KR"],["V1009","Pacific Motor Parts","VN"],["V1010","한성고무(주)","KR"],["V1011","태양전장(주)","KR"],["V1012","LG 사내 부품라인(C1)","KR"]]},
    {"line": 2, "note": "② WHERE — country가 KR인 행은 탈락하고 4행만 남습니다.", "dim": [0,1,2,5,7,9,10,11], "hot": ["country"]},
    {"line": 0, "note": "③ SELECT — 남은 행에서 vendor_code, vendor_name 두 컬럼만 고릅니다.",
     "cols": ["vendor_code", "vendor_name"],
     "rows": [["V1004","AsiaComp Co., Ltd."],["V1005","NanoChip Semiconductor"],["V1007","Global Steel Trading"],["V1009","Pacific Motor Parts"]], "hot": ["vendor_code", "vendor_name"]},
    {"line": 3, "note": "④ ORDER BY — 마지막으로 vendor_name 순으로 정렬합니다.",
     "cols": ["vendor_code", "vendor_name"],
     "rows": [["V1004","AsiaComp Co., Ltd."],["V1007","Global Steel Trading"],["V1005","NanoChip Semiconductor"],["V1009","Pacific Motor Parts"]], "hot": ["vendor_name"]}
  ]
}
```

> 오늘은 `SELECT` · `FROM` · `WHERE` · `ORDER BY` 네 개를 다룹니다. `GROUP BY` · `HAVING`은 6교시에서 배웁니다. 실행 순서는 2-6 별칭에서 **오류로 직접 확인**합니다.

### 2-2. 전체 컬럼 출력 — `*` {keep}

```sql
SELECT *
  FROM vendor;
```

```result 총 12행 중 일부
| vendor_code | vendor_name | country | is_domestic | main_item |
| --- | --- | --- | --- | --- |
| V1001 | 한빛정밀(주) | KR | Y | 판금·프레스 |
| V1002 | 대양화학(주) | KR | Y | 수지 원료 |
| V1003 | 세진전자(주) | KR | Y | PCB 조립 |
| … | … | … | … | … |
| V1012 | LG 사내 부품라인(C1) | KR | Y | 사내 거래 |
```

- `*`(애스터리스크) = **모든 컬럼**. 실행 순서: ① `vendor` 테이블을 가져와서 ② 모든 컬럼을 출력합니다.
- 실무 테이블은 컬럼이 수십 개라 `*`는 **구조를 처음 볼 때**만 쓰고, 보통은 필요한 컬럼만 적습니다.

### 2-3. 원하는 컬럼만 출력 {keep}

```sql
SELECT part_no
     , description_kr
     , uom
     , uit
  FROM part_master;
```

```result 결과 일부 (순서는 다를 수 있음)
| part_no | description_kr | uom | uit |
| --- | --- | --- | --- |
| FSC67181101 | 나사 M4x12 | EA | G |
| FSC33042701 | 나사 M5x16 | EA | G |
| FTP68745401 | 필라멘트 테이프 | MZ | G |
| RRS44997401 | ABS 수지 | KG | G |
| RPP53183301 | PP 수지 | KG | G |
```

- 컬럼은 **쉼표로 구분**하고, **적은 순서대로** 출력됩니다.
- 컬럼 이름을 모르면 1-5의 `\d` 또는 pgAdmin 트리에서 확인합니다.

### 2-4. 중복 제거 — `DISTINCT` {keep}

`part_master`는 68행입니다. 이 가운데 `uit` 값은 **몇 종류** 쓰이고 있을까요?

:::cols
```sql
SELECT DISTINCT uit
  FROM part_master
 ORDER BY uit;
```

```result
| uit |
| --- |
| D |
| F |
| G |
| P |
| S |
| T |
| X |
```
:::

- 68행 → **7행**. `code_uit`에는 코드가 11개 있지만, 실제 부품에는 7개만 쓰이고 있다는 뜻입니다. (C, Q, M, R은 이 데이터에서 쓰이지 않음)

### 2-4. 여러 컬럼에 DISTINCT {keep}

`DISTINCT` 뒤에 컬럼이 **여러 개**면, 그 **조합**이 같은 행을 하나로 합칩니다.

:::cols
```sql
SELECT DISTINCT class_lv1, uit
  FROM part_master
 ORDER BY class_lv1, uit;
```

```result 앞 6행
| class_lv1 | uit |
| --- | --- |
| A | P |
| A | S |
| A | T |
| E | D |
| E | G |
| E | T |
```
:::

> 정렬 없이 `SELECT DISTINCT uit FROM part_master;`만 실행하면 결과 순서가 섞여 나옵니다(예: X, S, D, P, T, G, F 순). 순서가 필요하면 반드시 `ORDER BY`를 붙입니다.

### 2-5. SELECT 절에서 계산하기 — 산술 연산 {keep}

숫자형·날짜형 컬럼에는 `+ - * /` 연산을 쓸 수 있습니다.

```sql
SELECT part_no
     , po_price
     , moq
     , po_price * moq
     , lead_time_days
     , lead_time_days / 7
  FROM part_sourcing
 WHERE part_no IN ('ECP39799101', 'EIC93178801', 'RSS86949501')
 ORDER BY part_no;
```

```result
| part_no | po_price | moq | ?column? | lead_time_days | ?column? |
| --- | --- | --- | --- | --- | --- |
| ECP39799101 | 48.50 | 200 | 9700.00 | 50 | 7 |
| EIC93178801 | 3.80 | 1000 | 3800.00 | 60 | 8 |
| RSS86949501 | 42.00 | 20 | 840.00 | 45 | 6 |
```

(`WHERE … IN`은 5-2에서 배웁니다. 지금은 “세 품번만 골랐다”고 읽으면 됩니다.)

- 계산한 컬럼은 이름이 없어 `?column?`으로 나옵니다 → 2-6 **별칭**으로 해결합니다.
- 이 세 품번은 통화가 `USD`이므로 `po_price * moq`도 달러 금액입니다.

### 2-5. 정수 ÷ 정수 = 몫만 남습니다 {keep}

:::error
`lead_time_days`(정수) / `7`(정수)은 **소수점 아래를 버립니다.** 50일 ÷ 7 = 7.14…가 아니라 `7`입니다.

```sql
SELECT part_no, lead_time_days
     , lead_time_days / 7   AS a
     , lead_time_days / 7.0 AS b
  FROM part_sourcing
 WHERE part_no = 'ECP39799101';
```

```result
| part_no | lead_time_days | a | b |
| --- | --- | --- | --- |
| ECP39799101 | 50 | 7 | 7.1428571428571429 |
```

한쪽을 `7.0`처럼 소수로 쓰면 소수까지 계산됩니다. Day 3 소요량·재료비 계산에서 다시 만납니다.
:::

### 2-5. 날짜 + 숫자 = 날짜 {keep}

```sql
SELECT part_no, created_at, created_at + 30
  FROM part_master
 WHERE part_no = 'ECP39799101';
```

```result
| part_no | created_at | ?column? |
| --- | --- | --- |
| ECP39799101 | 2025-04-24 | 2025-05-24 |
```

### 2-6. 별칭(Alias) — `AS` {keep}

컬럼에 **다른 이름**을 붙여 출력합니다. 방법은 네 가지입니다.

```sql
SELECT po_price * moq AS min_order_amt       -- ① AS 별칭
     , po_price * moq AS "MinOrderAmt"       -- ② AS "별칭"
     , po_price * moq 최소발주금액            -- ③ 별칭 (AS 생략)
     , po_price * moq "최소 발주 금액"        -- ④ "별칭" (AS 생략)
  FROM part_sourcing
 WHERE part_no = 'ECP39799101';
```

```result
| min_order_amt | MinOrderAmt | 최소발주금액 | 최소 발주 금액 |
| --- | --- | --- | --- |
| 9700.00 | 9700.00 | 9700.00 | 9700.00 |
```

> 별칭에 띄어쓰기를 쓰지 않고 `min_order_amt`처럼 **소문자 + 밑줄**로 쓰면 따옴표가 필요 없습니다.

### 2-6. 큰따옴표가 필요한 경우 {keep}

:::answer 큰따옴표 `" "` 가 필요한 경우 — 눌러서 보기
| 경우 | 따옴표 없이 | 결과 |
| --- | --- | --- |
| 띄어쓰기·특수문자가 있음 | `AS 최소 발주 금액` | ==오류== `syntax error at or near "발주"` |
| 대문자를 살리고 싶음 | `AS MinOrderAmt` | 컬럼 이름이 `minorderamt`(소문자)로 바뀜 |

```sql
SELECT po_price * moq AS MinOrderAmt
  FROM part_sourcing
 WHERE part_no = 'ECP39799101';
```

```result
| minorderamt |
| --- |
| 9700.00 |
```
:::

### 2-6. 실행 순서 확인 — WHERE에서는 별칭을 못 씁니다 ⭐ {keep}

```sql
SELECT part_no, po_price * moq AS min_order_amt
  FROM part_sourcing
 WHERE min_order_amt >= 10000;
```

```error
ERROR:  column "min_order_amt" does not exist
```

`WHERE`가 `SELECT`보다 **먼저 실행**되므로, `WHERE`를 실행하는 시점에는 별칭이 아직 없습니다. 반대로 `ORDER BY`는 `SELECT` 뒤에 실행되므로 별칭을 쓸 수 있습니다(3-1).

### 2-7. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마)

:::try
**[복습]** `employees`에서 직원들이 맡고 있는 직책(`job_id`)이 **몇 종류**인지 중복 없이, 알파벳 순으로 조회하세요. (2-4 예제처럼 끝에 `ORDER BY job_id`를 붙입니다.)

**[응용]** 부서ID가 60인 직원의 `employee_id`, `first_name`, `salary`와 함께 **연봉**(급여 × 12)과 **10% 인상 후 급여**를 출력하세요. 연봉은 `annual_salary`, 인상 후 급여는 `인상 후 급여`라는 별칭을 사용합니다. (WHERE는 4절에서 배우지만, `WHERE department_id = 60` 한 줄만 붙이면 됩니다.)
:::

### 2-7. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
107행 → **19행**

```sql
SELECT DISTINCT job_id
  FROM employees
 ORDER BY job_id;
```

```result
| job_id |
| --- |
| AC_ACCOUNT |
| AC_MGR |
| AD_ASST |
| … (총 19행) |
| ST_MAN |
```
:::

### 2-7. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
별칭에 띄어쓰기가 있으므로 큰따옴표가 필요합니다.

```sql
SELECT employee_id
     , first_name
     , salary
     , salary * 12  AS annual_salary
     , salary * 1.1 AS "인상 후 급여"
  FROM employees
 WHERE department_id = 60
 ORDER BY employee_id;
```

```result
| employee_id | first_name | salary | annual_salary | 인상 후 급여 |
| --- | --- | --- | --- | --- |
| 103 | Alexander | 9000.00 | 108000.00 | 9900.000 |
| 104 | Bruce | 6000.00 | 72000.00 | 6600.000 |
| 105 | David | 4800.00 | 57600.00 | 5280.000 |
| 106 | Valli | 4800.00 | 57600.00 | 5280.000 |
| 107 | Diana | 4200.00 | 50400.00 | 4620.000 |
```
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

## 3. ORDER BY · LIMIT — 정렬하고, 몇 개만 보기

### 3-1. ORDER BY — 정렬 {keep}

| 방식 | 뜻 | 비고 |
| --- | --- | --- |
| `ASC` (Ascending) | 오름차순 1, 2, 3 … / A → Z / 과거 → 최근 | **기본값** (생략하면 ASC) |
| `DESC` (Descending) | 내림차순 … 3, 2, 1 / Z → A / 최근 → 과거 | |

- `ORDER BY`는 `SELECT … FROM … WHERE` **뒤에 쓰고**, `SELECT`보다 **나중에 실행**됩니다.

```sql
SELECT part_no, description_kr, created_at
  FROM part_master
 ORDER BY created_at DESC, part_no
 LIMIT 5;
```

(`LIMIT 5`는 정렬한 뒤 앞 5행만 남깁니다 — 3-2에서 배웁니다. 등록일이 같으면 품번 순입니다.)

```result
| part_no | description_kr | created_at |
| --- | --- | --- |
| EBA60141001 | 디스플레이 PCB | 2025-12-26 |
| MGL96663301 | 도어 글라스 | 2025-12-25 |
| EMT73633001 | 스테이터 | 2025-12-23 |
| MDR41841501 | 내조 드럼 | 2025-12-14 |
| AHD26818801 | 핸들 조립체 | 2025-12-10 |
```

### 3-1. 여러 컬럼으로 정렬 {keep}

앞 컬럼 값이 같을 때 다음 컬럼으로 정렬합니다.

:::cols
```sql
SELECT part_no, description_kr, uit, created_at
  FROM part_master
 WHERE class_lv1 = 'A'
 ORDER BY uit ASC, created_at DESC;
```

```result
| part_no | description_kr | uit | created_at |
| --- | --- | --- | --- |
| ACP85953101 | 컨트롤 패널 조립체 | P | 2025-09-22 |
| ADR69737101 | 도어 조립체 | P | 2025-06-27 |
| APK23572301 | 포장 조립체 | P | 2025-06-19 |
| APK15762301 | 포장 조립체 | P | 2025-05-17 |
| ADR24872401 | 냉장실 도어 조립체 | P | 2025-03-16 |
| AHD26818801 | 핸들 조립체 | S | 2025-12-10 |
| ACC12625601 | 냉동 사이클 조립체 | T | 2025-10-19 |
| ADU49470801 | 구동부 조립체 | T | 2025-10-11 |
| ACB29328801 | 캐비닛 조립체 | T | 2025-06-20 |
| ATB35230801 | 터브 조립체 | T | 2025-03-26 |
| ACB22943901 | 캐비닛 조립체 | T | 2025-03-04 |
```
:::

### 3-1. 별칭으로 정렬 {keep}

`ORDER BY`는 `SELECT` 다음에 실행되므로 별칭을 쓸 수 있습니다.

:::cols
```sql
SELECT part_no, po_price * moq AS min_order_amt
  FROM part_sourcing
 WHERE currency = 'USD'
 ORDER BY min_order_amt DESC;
```

```result
| part_no | min_order_amt |
| --- | --- |
| ECP39799101 | 9700.00 |
| EIC93178801 | 3800.00 |
| MBR26166001 | 1900.00 |
| RSS86949501 | 840.00 |
| EMT78269001 | 14.00 |
| MGL96663301 | 11.50 |
| EFN66589301 | 6.20 |
```
:::

### 3-2. LIMIT — 앞에서 몇 행만 {keep}

```sql
SELECT part_no, vendor_code, lead_time_days
  FROM part_sourcing
 ORDER BY lead_time_days DESC, part_no
 LIMIT 3;
```

```result
| part_no | vendor_code | lead_time_days |
| --- | --- | --- |
| EIC93178801 | V1005 | 60 |
| ECP39799101 | V1004 | 50 |
| MGL96663301 | V1007 | 45 |
```

- `LIMIT n`은 **정렬이 끝난 뒤** 앞에서 n행만 남깁니다. 그래서 「상위 n개」를 구할 때는 ==`ORDER BY`와 함께== 씁니다.
- `ORDER BY` 없이 `LIMIT`만 쓰면 **아무 n행**이나 나옵니다.

### 3-3. NULL 맛보기 — 값이 비어 있다는 것 {keep}

> **NULL** = 데이터 값이 **완전히 비어 있는** 상태. 값이 존재하지 않거나 아직 정해지지 않은 것.

```icons NULL의 특징 세 가지
circle-help | ① 0 · '' · ' '은 NULL이 아님 | 숫자 `0`, 빈 문자열 `''`, 공백 `' '`은 **값이 있는 것** | ivory | 단가 0원 ≠ 단가 모름
circle-x | ② 연산하면 결과도 NULL | NULL과 무엇을 계산해도 NULL | plum | `NULL * 1 = NULL`
ban | ③ `=`로 비교 불가 | `= NULL`은 0행. `IS NULL`을 씀(5-1) | hot | `WHERE svc_code IS NULL`
```

### 3-3. NULL과 연산하면 NULL {keep}

```sql
SELECT part_no, po_price, moq, po_price * moq AS min_order_amt
  FROM part_sourcing
 WHERE vendor_code = 'V1010'
 ORDER BY part_no;
```

```result
| part_no | po_price | moq | min_order_amt |
| --- | --- | --- | --- |
| MFT20558801 | 1100.00 | 1 | 1100.00 |
| MFT43979901 | NULL | 1 | NULL |
| MGK25528301 | 4300.00 | 1 | 4300.00 |
| MGK31172901 | 6900.00 | 1 | 6900.00 |
| MHS18920401 | 1900.00 | 1 | 1900.00 |
```

`MFT43979901`(정수 필터)는 단가가 비어 있어 계산 결과도 비었습니다. ==“단가가 0원”이 아니라 “단가를 모른다”==입니다.

:::teacher 강사 확인
- `MFT43979901`의 단가 NULL은 README 4장의 심어 둔 이상 데이터 **A4**입니다. 운영안은 7교시에 「단가 NULL 부품 찾기(A4)」를 실습으로 두고 있으므로, 여기서는 “NULL과 연산하면 NULL”만 보여 주고 원인·영향 해석은 7교시로 넘기세요.
- 결과표의 `NULL`은 설명을 위해 글자로 적은 것입니다. psql에서는 빈칸으로 보이고, pgAdmin에서는 NULL 표시로 보입니다. 수업 PC 화면으로 확인해 주세요.
:::

### 3-4. NULL은 어디로 정렬될까? {keep}

`svc_code`(서비스 구분)는 서비스 부품이 아니면 **비어 있습니다(NULL)**. PostgreSQL은 NULL을 ==가장 큰 값처럼== 취급합니다.

```sql
SELECT part_no, description_kr, svc_code
  FROM part_master
 WHERE class_lv2 IN ('EBA', 'EMT')
 ORDER BY svc_code, part_no;
```

```result
| part_no | description_kr | svc_code |
| --- | --- | --- |
| EBA28941901 | 메인 PCB 조립체 | R |
| EBA56264701 | 메인 PCB 조립체 | R |
| EMT68237401 | DD 모터 | R |
| EBA60141001 | 디스플레이 PCB | NULL |
| EMT73633001 | 스테이터 | NULL |
| EMT78269001 | 로터 | NULL |
```

(`IN`은 5-2에서 배웁니다. 지금은 “EBA·EMT 두 분류만 골랐다”고 읽으면 됩니다.)

### 3-4. NULLS FIRST · NULLS LAST {keep}

| 정렬 | NULL 위치 (기본) | 바꾸려면 |
| --- | --- | --- |
| `ASC` | 맨 뒤 | `ORDER BY svc_code NULLS FIRST` |
| `DESC` | ==맨 앞== | `ORDER BY svc_code DESC NULLS LAST` |

> “서비스 코드가 있는 부품을 위로” 보려고 `DESC`를 쓰면 NULL 3행이 **맨 위**에 옵니다. <br>이때 `DESC NULLS LAST`를 쓰면 R 3행이 위로 올라옵니다(직접 실행해 확인해 보세요).

### 3-5. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마)

:::try
**[복습]** 급여(`salary`)가 가장 높은 직원 **5명**의 `employee_id`, `first_name`, `salary`를 조회하세요. 급여가 같으면 직원ID 순으로 정렬합니다.

**[응용]** 커미션 비율(`commission_pct`)이 가장 높은 직원 **3명**의 `employee_id`, `first_name`, `last_name`, `commission_pct`를 조회하세요. 비율이 같으면 성(`last_name`) 순입니다.
힌트: `ORDER BY commission_pct DESC LIMIT 3`만 쓰면 어떤 행이 나오는지 먼저 실행해 보세요.
:::

### 3-5. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
```sql
SELECT employee_id, first_name, salary
  FROM employees
 ORDER BY salary DESC, employee_id
 LIMIT 5;
```

```result
| employee_id | first_name | salary |
| --- | --- | --- |
| 100 | Steven | 24000.00 |
| 101 | Neena | 17000.00 |
| 102 | Lex | 17000.00 |
| 145 | John | 14000.00 |
| 146 | Karen | 13500.00 |
```
:::

### 3-5. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
`DESC`만 쓰면 커미션이 없는(NULL) 직원이 맨 위로 올라와 NULL 3행이 나옵니다. `NULLS LAST`로 NULL을 뒤로 보냅니다.

```sql
SELECT employee_id, first_name, last_name, commission_pct
  FROM employees
 ORDER BY commission_pct DESC NULLS LAST, last_name
 LIMIT 3;
```

```result
| employee_id | first_name | last_name | commission_pct |
| --- | --- | --- | --- |
| 145 | John | Russell | 0.40 |
| 156 | Janette | King | 0.35 |
| 158 | Allan | McEwen | 0.35 |
```
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

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
SELECT part_no, description, description_kr, uom, uit
  FROM part_master
 WHERE description_kr = '냉장고 세트';
```

```result
| part_no | description | description_kr | uom | uit |
| --- | --- | --- | --- | --- |
| TRF38316001 | Refrigerator,Set | 냉장고 세트 | ST | F |
```

- 문자열과 날짜 값은 ==작은따옴표==로 감쌉니다. 숫자는 그대로 씁니다.
- 문자열 비교는 **대소문자와 띄어쓰기까지 정확히** 같아야 합니다. (`'냉장고세트'`로 쓰면 0행)

### 4-2. 비교 연산자 {keep}

| 연산자 | 뜻 | 예 |
| --- | --- | --- |
| `=` | 같다 | `uit = 'D'` |
| `>` / `>=` | 크다(초과) / 크거나 같다(이상) | `lead_time_days >= 40` |
| `<` / `<=` | 작다(미만) / 작거나 같다(이하) | `po_price < 1000` |
| `<>` / `!=` | 같지 않다 | `country <> 'KR'` |

### 4-2. `=` 같다 {keep}

:::cols
```sql
SELECT part_no, description_kr, uit
  FROM part_master
 WHERE uit = 'D'
 ORDER BY part_no;
```

```result
| part_no | description_kr | uit |
| --- | --- | --- |
| ECP39799101 | 컴프레서 | D |
| EFN66589301 | 팬 모터 | D |
| EIC93178801 | 마이컴 | D |
| EPM57964301 | 배수 펌프 | D |
| MBR26166001 | 볼 베어링 | D |
| MGL96663301 | 도어 글라스 | D |
| RSS86949501 | 스테인리스 강판 | D |
```
:::

> `D`의 뜻은 1·2장에서 본 `code_uit`에 있습니다: **수입 구매품(Imported item)**. 코드표와 함께 읽는 습관을 들이세요.

### 4-2. `>=` 이상 {keep}

:::cols
```sql
SELECT part_no, vendor_code, lead_time_days
  FROM part_sourcing
 WHERE lead_time_days >= 40
 ORDER BY lead_time_days DESC, part_no;
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

### 4-2. 날짜 비교 {keep}

날짜는 `'YYYY-MM-DD'` 형식의 문자로 씁니다.

:::cols
```sql
SELECT part_no, description_kr, created_at
  FROM part_master
 WHERE created_at >= '2025-12-01'
 ORDER BY created_at, part_no;
```

```result
| part_no | description_kr | created_at |
| --- | --- | --- |
| MCB74311201 | 외함 캐비닛 | 2025-12-08 |
| AHD26818801 | 핸들 조립체 | 2025-12-10 |
| RPP53183301 | PP 수지 | 2025-12-10 |
| MDR41841501 | 내조 드럼 | 2025-12-14 |
| EMT73633001 | 스테이터 | 2025-12-23 |
| MGL96663301 | 도어 글라스 | 2025-12-25 |
| EBA60141001 | 디스플레이 PCB | 2025-12-26 |
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
SELECT vendor_code, vendor_name, country
  FROM vendor
 WHERE country <> 'KR';
```

```result
| vendor_code | vendor_name | country |
| --- | --- | --- |
| V1004 | AsiaComp Co., Ltd. | CN |
| V1005 | NanoChip Semiconductor | TW |
| V1007 | Global Steel Trading | JP |
| V1009 | Pacific Motor Parts | VN |
```
:::

| 부정 연산자 | 설명 |
| --- | --- |
| `<>` | SQL 표준 표기 |
| `!=` | `<>`와 같음 |
| `NOT 조건` | 조건 앞에 붙여 뒤집기. `WHERE NOT is_domestic = 'Y'`는 위와 같은 4행 |

### 4-4. 논리 연산자 — AND, OR {keep}

```compare
link | AND · 그리고 || split | OR · 또는
circle-check | **모든** 조건이 TRUE일 때만 TRUE || circle-check | 조건 중 **하나라도** TRUE이면 TRUE
filter | 조건을 더할수록 결과가 **줄어듦** || layers | 조건을 더할수록 결과가 **늘어남**
```

### 4-4. AND로 좁히기 {keep}

```sql
SELECT part_no, vendor_code, currency, lead_time_days
  FROM part_sourcing
 WHERE currency = 'USD'
   AND lead_time_days >= 45
 ORDER BY part_no;
```

```result
| part_no | vendor_code | currency | lead_time_days |
| --- | --- | --- | --- |
| ECP39799101 | V1004 | USD | 50 |
| EIC93178801 | V1005 | USD | 60 |
| MGL96663301 | V1007 | USD | 45 |
| RSS86949501 | V1007 | USD | 45 |
```

> 이 4건은 **해외에서 오래 걸려 들어오는 부품**입니다. 

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

**질문:** 전자부품(`class_lv1 = 'E'`) 중에서 UIT가 D **또는** G인 부품은?

```sql
SELECT part_no, description_kr, uit, class_lv1
  FROM part_master
 WHERE uit = 'D' OR uit = 'G' AND class_lv1 = 'E';
```

→ **19행**. 그런데 결과에 전자부품이 아닌 것이 섞여 있습니다.

```result 섞여 들어온 행
| part_no | description_kr | uit | class_lv1 |
| --- | --- | --- | --- |
| RSS86949501 | 스테인리스 강판 | D | R |
| MBR26166001 | 볼 베어링 | D | M |
| MGL96663301 | 도어 글라스 | D | M |
```

`uit = 'D' OR (uit = 'G' AND class_lv1 = 'E')`로 계산되어, UIT가 D인 부품은 분류와 상관없이 모두 들어왔습니다.

### 4-5. OR와 AND를 함께 쓸 때는 괄호 {keep}

```sql
SELECT part_no, description_kr, uit, class_lv1
  FROM part_master
 WHERE (uit = 'D' OR uit = 'G')
   AND class_lv1 = 'E';
```

→ **16행**, 모두 `class_lv1 = 'E'`. ==OR와 AND를 함께 쓸 때는 항상 괄호==를 칩니다. (5-2의 `IN`을 쓰면 `uit IN ('D', 'G')`로 더 짧게 쓸 수 있습니다.)

### [직접 해 보기] 4교시 {keep}

> `bom` 스키마의 테이블로 풉니다. 실행 전: `SET search_path TO bom;`

:::try
1. `vendor`에서 **국내 협력사**(`is_domestic = 'Y'`)의 코드·이름·주요 품목을 조회하세요.
2. `part_master`에서 **세트 품번**(`class_lv1 = 'T'`)의 품번·한글 품명·단위·UIT·등록일을 **등록일 순**으로 조회하세요. 세탁기 세트 품번은 무엇인가요?
3. `part_sourcing`에서 **원화(KRW)** 로 사는 소싱 중 **단가가 20,000 이상**인 행을 단가가 높은 순으로 조회하세요. 단가 컬럼은 `단가`라는 별칭으로 출력합니다.
4. `production_plan`에서 **LINE-B**의 계획을 계획일 순으로 **앞 5행만** 조회하세요.
:::

### [직접 해 보기] 4교시 — 예시 답안 {keep}

:::answer
```sql 1
SELECT vendor_code, vendor_name, main_item
  FROM vendor
 WHERE is_domestic = 'Y';
```

```sql 2
SELECT part_no, description_kr, uom, uit, created_at
  FROM part_master
 WHERE class_lv1 = 'T'
 ORDER BY created_at;
```

```result
| part_no | description_kr | uom | uit | created_at |
| --- | --- | --- | --- | --- |
| TRF38316001 | 냉장고 세트 | ST | F | 2025-02-08 |
| TWM61868701 | 세탁기 세트 | ST | F | 2025-09-12 |
```

```sql 3
SELECT part_no, vendor_code, po_price AS 단가
  FROM part_sourcing
 WHERE currency = 'KRW'
   AND po_price >= 20000
 ORDER BY po_price DESC;
```

```sql 4
SELECT plan_date, line_code, model_part_no, plan_qty
  FROM production_plan
 WHERE line_code = 'LINE-B'
 ORDER BY plan_date
 LIMIT 5;
```
:::

### 4-6. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마)

:::try
**[복습]** 부서ID가 50이고 급여가 4000 이상인 직원의 `employee_id`, `first_name`, `salary`를 급여가 높은 순으로 조회하세요.

**[응용]** **2008년 1월 1일 이후** 입사한 직원 중 직책이 `SA_REP` **또는** `ST_CLERK`인 직원의 `employee_id`, `first_name`, `job_id`, `hire_date`를 입사일 순(같으면 직원ID 순)으로 조회하세요.
:::

### 4-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
8행

```sql
SELECT employee_id, first_name, salary
  FROM employees
 WHERE department_id = 50
   AND salary >= 4000
 ORDER BY salary DESC;
```

```result
| employee_id | first_name | salary |
| --- | --- | --- |
| 121 | Adam | 8200.00 |
| 120 | Matthew | 8000.00 |
| 122 | Payam | 7900.00 |
| 123 | Shanta | 6500.00 |
| 124 | Kevin | 5800.00 |
| 184 | Nandita | 4200.00 |
| 185 | Alexis | 4100.00 |
| 192 | Sarah | 4000.00 |
```
:::

### 4-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
8행. 괄호 없이 `… AND job_id = 'SA_REP' OR job_id = 'ST_CLERK'`로 쓰면 **26행**이 나옵니다. 2008년 이전에 입사한 `ST_CLERK`까지 모두 섞이기 때문입니다(4-5 우선순위).

```sql
SELECT employee_id, first_name, job_id, hire_date
  FROM employees
 WHERE hire_date >= '2008-01-01'
   AND (job_id = 'SA_REP' OR job_id = 'ST_CLERK')
 ORDER BY hire_date, employee_id;
```

```result
| employee_id | first_name | job_id | hire_date |
| --- | --- | --- | --- |
| 179 | Charles | SA_REP | 2008-01-04 |
| 164 | Mattea | SA_REP | 2008-01-24 |
| 136 | Hazel | ST_CLERK | 2008-02-06 |
| 165 | David | SA_REP | 2008-02-23 |
| 128 | Steven | ST_CLERK | 2008-03-08 |
| 166 | Sundar | SA_REP | 2008-03-24 |
| 167 | Amit | SA_REP | 2008-04-21 |
| 173 | Sundita | SA_REP | 2008-04-21 |
```
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

# WHERE(조건 심화)

## 5. SQL 연산자

### 5-1. IS NULL / IS NOT NULL {keep}

NULL은 `=`로 찾을 수 없습니다(3-3 ③).

```sql
SELECT part_no
  FROM part_master
 WHERE svc_code = NULL;
```

→ **0행**. 오류는 나지 않지만 아무것도 나오지 않아 ==틀린 줄도 모르고 지나가기 쉽습니다.==

| 쓰는 법 | 뜻 | `part_master.svc_code` 결과 |
| --- | --- | --- |
| `WHERE svc_code IS NULL` | 값이 비어 있는 행 | 53행 |
| `WHERE svc_code IS NOT NULL` | 값이 있는 행 | 15행 |

### 5-1. IS NULL로 찾기 {keep}

:::cols
```sql
SELECT part_no, description_kr, svc_code
  FROM part_master
 WHERE class_lv1 = 'E'
   AND svc_code IS NULL
 ORDER BY part_no;
```

```result 앞 5행
| part_no | description_kr | svc_code |
| --- | --- | --- |
| EAE71986301 | 세라믹 커패시터 | NULL |
| EBA60141001 | 디스플레이 PCB | NULL |
| EFN66589301 | 팬 모터 | NULL |
| EHN19575601 | 와이어 하네스 | NULL |
| EHN86058201 | 와이어 하네스 | NULL |
```
:::

> `svc_code`가 NULL이면 서비스 부품이 아니라는 뜻입니다.

### 5-2. IN / NOT IN — 여러 값 중 하나 {keep}

| 쓰는 법 | 풀어 쓰면 |
| --- | --- |
| `컬럼 IN (값1, 값2, 값3)` | ==컬럼 = 값1 OR 컬럼 = 값2 OR 컬럼 = 값3== |
| `컬럼 NOT IN (값1, 값2, 값3)` | ==컬럼 <> 값1 AND 컬럼 <> 값2 AND 컬럼 <> 값3== |

:::cols
```sql
SELECT vendor_code, vendor_name, country
  FROM vendor
 WHERE country IN ('CN', 'TW', 'JP')
 ORDER BY vendor_code;
```

```result
| vendor_code | vendor_name | country |
| --- | --- | --- |
| V1004 | AsiaComp Co., Ltd. | CN |
| V1005 | NanoChip Semiconductor | TW |
| V1007 | Global Steel Trading | JP |
```
:::

### 5-2. IN과 NOT IN {keep}

```sql
SELECT part_no, description_kr, uit
  FROM part_master
 WHERE uit IN ('T', 'P')
 ORDER BY uit, part_no;
```

→ **14행** (P 8행, T 6행). `code_uit`에서 T는 「사내 조립품, 재고 관리」, P는 「사내 중간 조립품, 재고 관리 없음(팬텀)」입니다.

:::cols
```sql
SELECT part_no, description_kr, uit
  FROM part_master
 WHERE uit NOT IN ('G', 'D', 'T', 'P')
 ORDER BY uit, part_no;
```

```result
| part_no | description_kr | uit |
| --- | --- | --- |
| TRF38316001 | 냉장고 세트 | F |
| TWM61868701 | 세탁기 세트 | F |
| AHD26818801 | 핸들 조립체 | S |
| MDR41841501 | 내조 드럼 | S |
| MFL37467701 | 사용설명서 | X |
| SAA76541601 | 메인 펌웨어 | X |
```
:::

### 5-2. IN과 NULL — 함정 두 가지 {keep}

> `count(*)`는 **행 수를 세는** 함수입니다(6교시에서 배웁니다). 지금은 “몇 행인지”만 보면 됩니다.

:::error
**① `IN`으로는 NULL을 찾을 수 없습니다.** 목록에 NULL을 넣어도 NULL인 행은 나오지 않습니다.

```sql
SELECT count(*) FROM part_master WHERE svc_code IN ('R', NULL);       -- 9 (R인 행만)
```

NULL도 함께 찾으려면 `WHERE svc_code = 'R' OR svc_code IS NULL`처럼 `IS NULL`을 따로 씁니다.

**② `NOT IN` 목록에 NULL이 하나라도 있으면 결과가 0행이 됩니다.**

```sql
SELECT count(*) FROM part_master WHERE svc_code NOT IN ('R');         -- 6 (Z인 행)
SELECT count(*) FROM part_master WHERE svc_code NOT IN ('R', NULL);   -- 0
```

`NOT IN`은 `<> 'R' AND <> NULL`인데, `<> NULL`은 TRUE가 될 수 없기 때문입니다. <br> 첫 번째 쿼리도 svc_code가 NULL인 53행은 **빠졌다**는 점에 주의하세요.
:::

### 5-3. BETWEEN A AND B — 범위 {keep}

```text
컬럼 BETWEEN A AND B   =   컬럼 >= A AND 컬럼 <= B     (A 이상 B 이하, 양 끝 포함)
```

:::cols
```sql
SELECT part_no, vendor_code, lead_time_days
  FROM part_sourcing
 WHERE lead_time_days BETWEEN 30 AND 45
 ORDER BY lead_time_days, part_no;
```

```result
| part_no | vendor_code | lead_time_days |
| --- | --- | --- |
| EMT73633001 | V1009 | 30 |
| EMT78269001 | V1009 | 30 |
| MBR26166001 | V1009 | 30 |
| EFN66589301 | V1009 | 40 |
| MGL96663301 | V1007 | 45 |
| RSS86949501 | V1007 | 45 |
```
:::

30과 45가 **둘 다 포함**되었습니다.

### 5-3. 날짜 범위 {keep}

:::cols
```sql
SELECT plan_date, line_code, model_part_no, plan_qty
  FROM production_plan
 WHERE plan_date BETWEEN '2026-12-07' AND '2026-12-09'
 ORDER BY plan_date, line_code;
```

```result
| plan_date | line_code | model_part_no | plan_qty |
| --- | --- | --- | --- |
| 2026-12-07 | LINE-A | TWM61868701 | 420 |
| 2026-12-07 | LINE-B | TRF38316001 | 340 |
| 2026-12-08 | LINE-A | TWM61868701 | 480 |
| 2026-12-08 | LINE-B | TRF38316001 | 320 |
| 2026-12-09 | LINE-A | TWM61868701 | 420 |
| 2026-12-09 | LINE-B | TRF38316001 | 360 |
```
:::

:::error 작은 값을 앞에
`BETWEEN 45 AND 30`처럼 순서를 바꾸면 오류 없이 **0행**이 나옵니다. 반드시 `BETWEEN 최솟값 AND 최댓값`.
:::

> 이 데이터의 날짜 컬럼은 모두 `date`(시각 없음)라 양 끝 날짜가 그대로 포함됩니다. 시각까지 있는 `timestamp` 컬럼은 Day 4 기록 테이블에서 다룹니다.

### 5-4. LIKE — 일부 문자로 찾기 {keep}

| 와일드카드 | 뜻 | 예 | 찾는 것 |
| --- | --- | --- | --- |
| `%` | 길이와 상관없이 **아무 글자들** (0글자 포함) | `'EMT%'` | EMT로 **시작** |
| | | `'%,Door'` | `,Door`로 **끝남** |
| | | `'%Assembly%'` | Assembly를 **포함** |
| `_` | 아무 글자 **딱 한 개** | `'_0_A'` | 4글자, 둘째가 0, 넷째가 A |

### 5-4. ① 분류코드 접두어로 찾기 {keep}

품번 11자리 중 앞 3자리가 분류코드입니다(README 1장).

:::cols
```sql
SELECT part_no, description, description_kr
  FROM part_master
 WHERE part_no LIKE 'EMT%'
 ORDER BY part_no;
```

```result
| part_no | description | description_kr |
| --- | --- | --- |
| EMT68237401 | Motor,DD | DD 모터 |
| EMT73633001 | Stator Assembly | 스테이터 |
| EMT78269001 | Rotor Assembly | 로터 |
```
:::

> 이 데이터에서는 `class_lv2` 값이 품번 앞 3자리와 모두 같습니다. 그래서 `WHERE class_lv2 = 'EMT'`로도 같은 결과가 나옵니다.

### 5-4. ② Description 규칙으로 찾기 {keep}

Description은 `Main Function,Sub` 형식입니다.

:::cols
```sql
SELECT part_no, description_kr
  FROM part_master
 WHERE description LIKE '%,Door'
 ORDER BY part_no;
```

```result
| part_no | description_kr |
| --- | --- |
| MGK25528301 | 도어 가스켓 |
| MGK31172901 | 도어 가스켓 |
| MGL96663301 | 도어 글라스 |
| MHG51215701 | 도어 힌지(구형) |
| MHG91254002 | 도어 힌지 |
```
:::

:::cols
```sql
SELECT part_no, description_kr
  FROM part_master
 WHERE description_kr LIKE '%필터%'
 ORDER BY part_no;
```

```result
| part_no | description_kr |
| --- | --- |
| MFT20558801 | 린트 필터 |
| MFT43979901 | 정수 필터 |
```
:::

### 5-4. ③ `_`로 자리 맞추기 · ④ 끝 2자리 = 시리즈 {keep}

```sql
SELECT part_no, description_kr, svc_location_no
  FROM part_master
 WHERE svc_location_no LIKE '_0_A'
 ORDER BY svc_location_no;
```

→ **14행**. 서비스 위치번호가 있는 15개 중 `202B`(핸들 조립체) 하나만 빠집니다(끝 글자가 B).

품번 끝 2자리는 시리즈입니다(README 1장).

```sql
SELECT part_no, description_kr
  FROM part_master
 WHERE part_no NOT LIKE '%01'
 ORDER BY part_no;
```

```result
| part_no | description_kr |
| --- | --- |
| MHG91254002 | 도어 힌지 |
```

### 5-4. LIKE는 대소문자를 구분합니다 → ILIKE {keep}

:::error
```sql
SELECT count(*) FROM part_master WHERE description LIKE  '%assembly%';   -- 0
SELECT count(*) FROM part_master WHERE description ILIKE '%assembly%';   -- 19
```

데이터에는 `Assembly`(대문자 A)로 저장되어 있어 `LIKE '%assembly%'`는 0행입니다. PostgreSQL의 ==`ILIKE`는 대소문자를 무시==하고 찾습니다. (`ILIKE`는 PostgreSQL 전용 문법입니다.)
:::

:::try 생각해 보기
`description LIKE '%Assembly%'`(19행)에는 `Stator Assembly`(스테이터), `Shelf Assembly`(선반)처럼 이름은 Assembly지만 **UIT가 G(국내 구매품)** 인 부품도 섞여 있습니다. “이름에 Assembly가 있다”와 “사내에서 조립한다”는 같은 말일까요? → 7절 복습 문제 6번(7-3)에서 확인합니다.
:::

### 5-5. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마)

:::try
**[복습]** 전화번호(`phone_number`)가 `515`로 시작하고 급여가 10000 ~ 20000 사이인 직원의 `employee_id`, `first_name`, `phone_number`, `salary`를 급여가 높은 순(같으면 직원ID 순)으로 조회하세요.

**[응용]** 인사팀이 “부서 50(Shipping)·80(Sales)이 **아닌** 직원 수”를 물었습니다. 아래 두 쿼리를 실행해 결과가 왜 다른지 설명하고, 인사팀 질문에 맞는 쿼리는 어느 쪽인지 고르세요.

```sql
SELECT count(*) FROM employees WHERE department_id NOT IN (50, 80);
SELECT count(*) FROM employees WHERE department_id NOT IN (50, 80) OR department_id IS NULL;
```
:::

### 5-5. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
7행

```sql
SELECT employee_id, first_name, phone_number, salary
  FROM employees
 WHERE phone_number LIKE '515%'
   AND salary BETWEEN 10000 AND 20000
 ORDER BY salary DESC, employee_id;
```

```result
| employee_id | first_name | phone_number | salary |
| --- | --- | --- | --- |
| 101 | Neena | 515.123.4568 | 17000.00 |
| 102 | Lex | 515.123.4569 | 17000.00 |
| 201 | Michael | 515.123.5555 | 13000.00 |
| 108 | Nancy | 515.124.4569 | 12008.00 |
| 205 | Shelley | 515.123.8080 | 12008.00 |
| 114 | Den | 515.127.4561 | 11000.00 |
| 204 | Hermann | 515.123.8888 | 10000.00 |
```
:::

### 5-5. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
첫 번째는 **27**, 두 번째는 **28**입니다. 부서가 정해지지 않은(`department_id`가 NULL) 직원 1명(178 Kimberely Grant)이 `NOT IN`에서는 빠지기 때문입니다(5-2). 이 직원도 “부서 50·80이 아닌 직원”이므로 **두 번째 쿼리**가 질문에 맞습니다.

```sql
SELECT employee_id, first_name, last_name, department_id
  FROM employees
 WHERE department_id IS NULL;
```

```result
| employee_id | first_name | last_name | department_id |
| --- | --- | --- | --- |
| 178 | Kimberely | Grant | NULL |
```
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

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

### 6-1. UIT → Make / Buy 라벨 {keep}

`code_uit`의 `classification` 컬럼은 UIT를 세 그룹으로 나눕니다.

```icons code_uit.classification
package | Finished product | 완제품 | ivory | F, C, Q
factory | Make item | 사내에서 만드는 것 | lime | T, P, S, M, R
shopping-cart | Buy item | 사 오는 것 | plum | G, D, X
```

### 6-1. CASE로 Make / Buy 붙이기 {keep}

:::cols
```sql
SELECT part_no
     , description_kr
     , uit
     , CASE WHEN uit IN ('T', 'P', 'S', 'M', 'R') THEN 'Make'
            WHEN uit IN ('G', 'D', 'X')           THEN 'Buy'
            ELSE '완제품'
       END AS make_buy
  FROM part_master
 WHERE part_no IN ('TRF38316001', 'ACB22943901', 'MCB45577701', 'AHD26818801',
                   'ECP39799101', 'FSC67181101', 'MFL37467701')
 ORDER BY part_no;
```

```result
| part_no | description_kr | uit | make_buy |
| --- | --- | --- | --- |
| ACB22943901 | 캐비닛 조립체 | T | Make |
| AHD26818801 | 핸들 조립체 | S | Make |
| ECP39799101 | 컴프레서 | D | Buy |
| FSC67181101 | 나사 M4x12 | G | Buy |
| MCB45577701 | 외함 캐비닛 | P | Make |
| MFL37467701 | 사용설명서 | X | Buy |
| TRF38316001 | 냉장고 세트 | F | 완제품 |
```
:::

> Day 2에서는 `code_uit`와 **JOIN**해 `classification`을 직접 가져오는 방법을 배웁니다. 지금은 코드표를 보고 CASE로 직접 옮겨 적은 것입니다.

### 6-2. 분류 E / M → 전자부품 / 기구부품 {keep}

:::cols
```sql
SELECT part_no
     , description_kr
     , class_lv1
     , CASE class_lv1 WHEN 'E' THEN '전자부품'
                      WHEN 'M' THEN '기구부품'
                      ELSE '기타'
       END AS 부품구분
  FROM part_master
 ORDER BY part_no;
```

```result 앞 6행
| part_no | description_kr | class_lv1 | 부품구분 |
| --- | --- | --- | --- |
| ACB22943901 | 캐비닛 조립체 | A | 기타 |
| ACB29328801 | 캐비닛 조립체 | A | 기타 |
| ACC12625601 | 냉동 사이클 조립체 | A | 기타 |
| ACP85953101 | 컨트롤 패널 조립체 | A | 기타 |
| ADR24872401 | 냉장실 도어 조립체 | A | 기타 |
| ADR69737101 | 도어 조립체 | A | 기타 |
```
:::

→ 68행: 전자부품 17 · 기구부품 29 · 기타 22.

:::teacher 강사 확인
- `class_lv1`에는 A·E·F·M·R·S·T 7개 값이 있습니다. E = 전자부품, M = 기구부품은 운영안 5H 기준입니다. 나머지 값의 공식 의미는 제공 자료(README·코드표)에 정의되어 있지 않아 「기타」로 묶었습니다. 데이터셋 제공처(랩포디엑스) 정의가 있으면 CASE에 추가하세요.
- 위 결과표 앞 6행이 모두 「기타」라 단조로우면 `WHERE class_lv1 IN ('E', 'M')`을 붙여 보여 주세요.
:::

### 6-3. 국내 / 해외 라벨 {keep}

```sql
SELECT vendor_code
     , vendor_name
     , is_domestic
     , CASE WHEN is_domestic = 'Y' THEN '국내' ELSE '해외' END AS 구분
  FROM vendor
 ORDER BY vendor_code;
```

→ 12행: 국내 8 · 해외 4. 6교시에서 이 라벨로 `GROUP BY`하면 국내/해외 협력사 비율을 바로 구할 수 있습니다.

### 6-4. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마)

:::try
**[복습]** 매니저ID가 100인 직원의 `employee_id`, `first_name`, `commission_pct`와, 커미션이 있으면 `대상`, 없으면 `미대상`인 `commission_yn` 컬럼을 직원ID 순으로 출력하세요.

**[응용]** 부서 90·100 직원에게 급여 등급을 붙이려 합니다. 급여 15000 이상은 `A`, 8000 이상은 `B`, 나머지는 `C`입니다. `employee_id`, `first_name`, `salary`, `grade`를 급여가 높은 순(같으면 직원ID 순)으로 출력하세요.
:::

### 6-4. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
14행 (대상 5 · 미대상 9). 커미션이 없다는 것은 NULL이므로 `IS NULL`로 검사합니다.

```sql
SELECT employee_id
     , first_name
     , commission_pct
     , CASE WHEN commission_pct IS NULL THEN '미대상' ELSE '대상' END AS commission_yn
  FROM employees
 WHERE manager_id = 100
 ORDER BY employee_id;
```

```result
| employee_id | first_name | commission_pct | commission_yn |
| --- | --- | --- | --- |
| 101 | Neena | NULL | 미대상 |
| 102 | Lex | NULL | 미대상 |
| … | | | |
| 145 | John | 0.40 | 대상 |
| 146 | Karen | 0.30 | 대상 |
| … (총 14행) | | | |
```
:::

### 6-4. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
9행. 위에서부터 검사하므로 **큰 기준부터** 씁니다. 순서를 `>= 8000`부터 쓰면 24000도 `B`가 됩니다.

```sql
SELECT employee_id
     , first_name
     , salary
     , CASE WHEN salary >= 15000 THEN 'A'
            WHEN salary >= 8000  THEN 'B'
            ELSE 'C'
       END AS grade
  FROM employees
 WHERE department_id IN (90, 100)
 ORDER BY salary DESC, employee_id;
```

```result
| employee_id | first_name | salary | grade |
| --- | --- | --- | --- |
| 100 | Steven | 24000.00 | A |
| 101 | Neena | 17000.00 | A |
| 102 | Lex | 17000.00 | A |
| 108 | Nancy | 12008.00 | B |
| 109 | Daniel | 9000.00 | B |
| 110 | John | 8200.00 | B |
| 112 | Jose Manuel | 7800.00 | C |
| 111 | Ismael | 7700.00 | C |
| 113 | Luis | 6900.00 | C |
```
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

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

**6.** (심화) `part_master`에서 영문 품명(`description`)에 'Assembly'가 들어가는데 UIT가 G 또는 D인(국내·수입 구매품) 부품의 `part_no`, `description`, `uit`와 CASE로 만든 `make_buy` 라벨을 품번 순으로 출력하세요. [힌트: LIKE, 괄호, CASE]

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
- 6번 결과의 의미: 이름은 **조립체(Assembly)** 지만 사내에서 만들지 않고 **사 오는** 부품이 8개 있습니다. 이름만 보고 판단하지 말고 ==UIT 코드로 확인==해야 하는 이유입니다.
:::

## 8. 정리

### 8-1. 오늘 배운 것 {keep}

:::summary
- **SQL 실행 순서**: `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY`. 그래서 `WHERE`에서는 별칭을 못 쓰고, `ORDER BY`에서는 쓸 수 있습니다.
- **SELECT**: `*` 전체 / 컬럼 나열 / `DISTINCT` 중복 제거 / 산술 연산(정수 ÷ 정수는 몫만) / 별칭 `AS`(띄어쓰기·대문자는 `" "`).
- **ORDER BY**: 기본 ASC. PostgreSQL에서 NULL은 가장 큰 값 → `NULLS FIRST / LAST`로 조정. **LIMIT**은 `ORDER BY`와 함께.
- **WHERE**: 비교(`= <> > >= < <=`), 논리(`AND`가 `OR`보다 먼저 → 괄호), `IS NULL`, `IN`, `BETWEEN`(양 끝 포함), `LIKE`(`%`, `_`) / `ILIKE`.
- **NULL**: `= NULL`은 0행, `IS NULL`로 찾기. `IN`·`NOT IN`과 함께 쓸 때 주의.
- **CASE WHEN**: 조건에 따라 Make/Buy, 전자/기구, 국내/해외 같은 **라벨 컬럼**을 만듭니다.
:::

### 8-2. 마무리 퀴즈

:::quiz
Q. `SELECT part_no, po_price * moq AS amt FROM part_sourcing WHERE amt > 1000;`이 오류가 나는 이유는?
A. `WHERE`가 `SELECT`보다 먼저 실행되어, `WHERE` 시점에는 별칭 `amt`가 아직 없기 때문입니다. `WHERE po_price * moq > 1000`으로 씁니다.

Q. `WHERE svc_code = NULL`의 결과는? 어떻게 고쳐야 하나요?
A. 오류 없이 0행이 나옵니다. NULL은 `=`로 비교할 수 없으므로 `WHERE svc_code IS NULL`로 씁니다.

Q. `WHERE uit = 'D' OR uit = 'G' AND class_lv1 = 'E'`는 어떤 순서로 계산되나요?
A. `AND`를 먼저 계산해 `uit = 'D' OR (uit = 'G' AND class_lv1 = 'E')`가 됩니다. 의도가 “전자부품 중 D 또는 G”라면 `(uit = 'D' OR uit = 'G') AND class_lv1 = 'E'`처럼 괄호를 칩니다.

Q. `lead_time_days / 7`이 50일에 대해 7을 돌려주는 이유와, 소수까지 구하는 방법은?
A. 정수 ÷ 정수라 몫만 남기 때문입니다. `lead_time_days / 7.0`처럼 한쪽을 소수로 씁니다.

Q. 영문 품명에 `assembly`가 들어간 부품을 대소문자와 상관없이 찾으려면?
A. `WHERE description ILIKE '%assembly%'` (PostgreSQL의 `ILIKE`)
:::
