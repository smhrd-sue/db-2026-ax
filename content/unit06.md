---
label: 6. 서브쿼리
title: 쿼리 안의 쿼리
---

# 서브쿼리 · WITH

:::goal
- 서브쿼리를 「값을 구하는 방법」을 넣는 것으로 읽고, 위치(WHERE·SELECT·FROM·WITH)에 따라 이름을 구분할 수 있습니다.
- 단일행·다중행(IN, ANY, ALL, EXISTS)·다중열 서브쿼리를 골라 쓰고, 여러 행 오류와 NOT IN의 NULL 함정을 피할 수 있습니다.
- 스칼라 서브쿼리와 인라인 뷰로 컬럼·가상 테이블을 만들고, 1 : N 테이블은 「집계 먼저, 조인 나중」으로 합계를 낼 수 있습니다.
- WITH로 서브쿼리에 이름을 붙여 단계를 나눌 수 있습니다.
:::

:::teacher 단원 구성 (60분)
- 운영안 Day 3 **1H(서브쿼리·CTE: 서브쿼리 위치 SELECT/FROM/WHERE, WITH 절로 단계 나누기)** 에 해당합니다. 5단원(JOIN)에서 INNER/LEFT JOIN·안티 조인을 배운 뒤라는 전제로 작성했고(5단원 3-4에서 「서브쿼리는 Day 3 1교시에서 자세히」라고 예고한 내용을 2-5에서 이어받습니다), 6장 WITH는 2교시 재귀 CTE로 넘어가기 위한 맛보기입니다.
- 기존 교안 `8. 서브쿼리.pptx` · `8. 서브쿼리 복습문제.txt`의 **순서(서브쿼리 → 단일행 → 다중행 → 다중열 → 인라인 뷰 → 스칼라)와 예제 유형**을 따르되, 스칼라 서브쿼리를 인라인 뷰 앞에 두어 「WHERE → SELECT → FROM → WITH」 순으로 위치가 넓어지도록 바꿨습니다.
- **본문 예제는 HR 실습 데이터(`hr_postgres.sql`, `hr` 스키마)** 입니다. 기존 교안 SQL(`reference/10. 서브쿼리.sql`)의 예제 — Shelli보다 급여가 낮은 직원, 평균 급여보다 많이 받는 직원, David처럼 이름이 겹치는 직원, 부서별 최고 급여 직원(다중열·인라인 뷰), 부서 이름 스칼라 서브쿼리 — 를 PostgreSQL 문법으로 옮겨 썼습니다.
- 각 장 끝 「확인 문제」(복습 1 + 응용 1, 6장은 응용 1문항)와 7장 복습 문제는 **생산 실습 데이터(`bom` 스키마)** 로 풉니다. 확인 문제 실행 전 `SET search_path TO bom;`, 마친 뒤 `SET search_path TO hr;`가 필요합니다.
- 교안의 모든 SQL과 실행 결과는 실습 DB에서 **직접 실행한 결과**입니다. 오류 메시지도 실제 출력입니다. (검증 환경: PostgreSQL 18, `DateStyle = ISO, YMD`)
- 이 단원은 1교시(60분) 분량입니다. 확인 문제와 7장 복습 문제는 시간에 따라 일부만 풀고, 나머지는 과제로 활용하세요.

| 교시 | 시간 | 내용 | 해당 장 | 기존 교안 대응 |
| --- | --- | --- | --- | --- |
| **1교시** | 0~12분 | 서브쿼리 개념 · 단일행 서브쿼리 · 여러 행 오류 · 0행이면 NULL | 1 | `8. 서브쿼리.pptx` 3~7 |
| | 12~27분 | 다중행: IN · NOT IN과 NULL · ANY/ALL · EXISTS(상관 서브쿼리) | 2 | `8. 서브쿼리.pptx` 8~13 |
| | 27~33분 | 다중열 서브쿼리 · 단일열 IN과의 차이 | 3 | `8. 서브쿼리.pptx` 14~16 |
| | 33~43분 | 스칼라 서브쿼리(SELECT절) · NULL과 오류 | 4 | `8. 서브쿼리 복습문제.txt` 1번 |
| | 43~53분 | 인라인 뷰(FROM절) · 「집계 먼저, 조인 나중」 | 5 | `8. 서브쿼리.pptx` 17~18, 복습문제 2번 |
| | 53~60분 | WITH로 단계 나누기 · 복습 문제 안내 · 정리 | 6~8 | — |
:::

## 1. 서브쿼리 — SQL 안의 SELECT

### 1-1. 서브쿼리란 {keep}

**서브쿼리(subquery)** 는 SQL 문장 **안에 들어 있는 SELECT 문**입니다. 바깥 쿼리를 **메인쿼리**, 괄호 안의 쿼리를 **서브쿼리**라고 부릅니다.

```text 서브쿼리의 모양
SELECT 컬럼                         ← 메인쿼리
  FROM 테이블
 WHERE 컬럼 > ( SELECT 컬럼          ← 서브쿼리 (괄호 안)
                  FROM 테이블
                 WHERE 조건 );
```

### 1-1. 위치에 따라 이름이 달라집니다 {keep}

| 위치 | 이름 | 하는 일 | 해당 장 |
| --- | --- | --- | --- |
| `WHERE` / `HAVING` | (일반) 서브쿼리 | 비교할 **값**을 만들어 줌 | 1~3 |
| `SELECT` | 스칼라 서브쿼리 | 행마다 **컬럼 하나**를 만들어 줌 | 4 |
| `FROM` | 인라인 뷰 | **가상의 테이블**을 만들어 줌 | 5 |
| 쿼리 맨 위 `WITH` | CTE | 서브쿼리에 **이름**을 붙여 단계를 나눔 | 6 |

### 1-2. 쿼리 두 번 — ① Shelli의 급여 {keep}

> 실행 전: `SET search_path TO hr;` — 이 단원의 예제는 HR 실습 데이터(`hr_postgres.sql`의 `hr` 스키마)로 실행합니다.

**질문:** 이름이 Shelli인 직원보다 급여가 **낮은** 직원은?

이 질문은 두 단계로 풀 수 있습니다.

:::cols
```sql ① Shelli의 급여를 먼저 조회
SELECT salary
  FROM employees
 WHERE first_name = 'Shelli';
```

```result
| salary |
| --- |
| 2900.00 |
```
:::

:::cols
```sql ② 그 값(2900)을 조건에 넣어 다시 조회
SELECT first_name, salary
  FROM employees
 WHERE salary < 2900
 ORDER BY salary DESC, first_name;
```

```result 앞 3행 (총 21행)
| first_name | salary |
| --- | --- |
| Girard | 2800.00 |
| Mozhe | 2800.00 |
| Sigal | 2800.00 |
```
:::

### 1-2. 쿼리 두 번 → 한 번으로 {keep}

①의 결과를 손으로 옮겨 적는 대신, **① 쿼리를 ②의 자리에 그대로 넣은 것**이 서브쿼리입니다.

:::cols
```sql
SELECT first_name, salary
  FROM employees
 WHERE salary < (SELECT salary
                   FROM employees
                  WHERE first_name = 'Shelli')
 ORDER BY salary DESC, first_name;
```

```result 앞 3행 (총 21행)
| first_name | salary |
| --- | --- |
| Girard | 2800.00 |
| Mozhe | 2800.00 |
| Sigal | 2800.00 |
```
:::

- 괄호 안이 **먼저 실행되어 값(2900)이 되고**, 그 값으로 메인쿼리가 실행된다고 읽으면 됩니다.
- Shelli의 급여가 바뀌어도 쿼리를 고칠 필요가 없습니다. ==값을 적어 넣지 않고 「값을 구하는 방법」을 적어 넣는 것==이 서브쿼리의 장점입니다.

### 1-3. 단일행 서브쿼리와 단일행 연산자 {keep}

1-2의 서브쿼리는 결과가 **1행 1열(값 하나)** 입니다. 이런 서브쿼리를 **단일행 서브쿼리**라고 하고, 비교에는 **단일행 연산자**를 씁니다.

| 단일행 연산자 | 의미 |
| --- | --- |
| `=` | 같다 |
| `<>`, `!=` | 같지 않다 |
| `>`, `>=` | 크다, 크거나 같다 |
| `<`, `<=` | 작다, 작거나 같다 |

**집계 함수와 함께** — 4단원의 집계 함수는 `GROUP BY` 없이 쓰면 결과가 항상 1행이므로 단일행 서브쿼리에 잘 어울립니다.

### 1-3. 평균보다 급여가 많은 직원 {keep}

**질문:** 전체 평균 급여보다 많이 받는 직원은?

:::answer 예시 답안 — 눌러서 보기
```sql 평균 급여
SELECT ROUND(AVG(salary), 1) AS avg_sal
  FROM employees;
```

```result
| avg_sal |
| --- |
| 6461.8 |
```

```sql
SELECT first_name, salary
  FROM employees
 WHERE salary > (SELECT AVG(salary)
                   FROM employees)
 ORDER BY salary, first_name;
```

```result 앞 8행 (총 51행)
| first_name | salary |
| --- | --- |
| Shanta | 6500.00 |
| Susan | 6500.00 |
| David | 6800.00 |
| Luis | 6900.00 |
| Kimberely | 7000.00 |
| Oliver | 7000.00 |
| Sarath | 7000.00 |
| Mattea | 7200.00 |
```

> 4단원 3-2에서 `WHERE`에는 집계 함수를 쓸 수 없다고 했습니다. `WHERE salary > AVG(salary)`는 오류지만, ==집계 함수를 서브쿼리 안에 넣으면== 서브쿼리가 먼저 값(6461.8…)으로 바뀌므로 `WHERE`에서 비교할 수 있습니다.
:::

### 1-3. 가장 최근에 입사한 직원 {keep}

**질문:** 가장 최근에 입사한 직원은?

:::answer 예시 답안 — 눌러서 보기
```sql
SELECT employee_id, first_name, last_name, hire_date
  FROM employees
 WHERE hire_date = (SELECT MAX(hire_date)
                      FROM employees);
```

```result
| employee_id | first_name | last_name | hire_date |
| --- | --- | --- | --- |
| 167 | Amit | Banda | 2008-04-21 |
| 173 | Sundita | Kumar | 2008-04-21 |
```

`MAX(hire_date)`는 값 하나(2008-04-21)지만, 그 날짜에 입사한 직원은 **2명**입니다. 「최댓값을 가진 행」은 여러 개일 수 있습니다.
:::

### 1-4. 주의 ① 서브쿼리 결과가 여러 행이면 ⭐ {keep}

:::error 서브쿼리 결과가 여러 행이면 — 단일행 연산자 오류
이름이 David인 직원은 Austin(4800), Bernstein(9500), Lee(6800) **3명**이라 급여도 3개입니다. 값 3개와 `>` 하나로 비교할 수는 없습니다.

```sql
SELECT first_name, salary
  FROM employees
 WHERE salary > (SELECT salary
                   FROM employees
                  WHERE first_name = 'David');
```

```error
ERROR:  more than one row returned by a subquery used as an expression
```

서브쿼리 결과가 여러 행이면 ==다중행 연산자(IN, ANY, ALL)== 를 써야 합니다(2장). 한 사람만 비교하려면 `employee_id = 151`처럼 **PK로** 찾습니다.
:::

### 1-4. 주의 ② 서브쿼리 결과가 0행이면 {keep}

:::error 서브쿼리 결과가 0행이면 — 오류 없이 0행
이름을 소문자로 적어(`'shelli'`) 서브쿼리가 아무 행도 찾지 못하면, 서브쿼리 값은 **NULL**이 됩니다. 작은따옴표 안의 값은 대소문자를 구분합니다(3단원 4-1). (아래는 그 값을 눈으로 확인하려고 서브쿼리를 `SELECT` 절에 넣어 본 것입니다. 이 자리의 서브쿼리는 4장에서 배웁니다.)

```sql
SELECT (SELECT salary
          FROM employees
         WHERE first_name = 'shelli') AS sub_result;
```

```result
| sub_result |
| --- |
| NULL |
```

`salary < NULL`은 참이 아니므로(3단원 5-1) 메인쿼리 결과는 **0행**입니다. 오류 메시지가 없어서 「조건에 맞는 직원이 없다」로 오해하기 쉽습니다. ==결과가 0행이면 서브쿼리만 따로 실행해 값이 나오는지 먼저 확인==하세요.
:::

### 1-5. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `part_sourcing`에서 전체 평균 리드타임보다 **오래 걸리는** 소싱 품목의 품번, 업체 코드, 구매 조건(`line_type`), 리드타임을 리드타임이 긴 순(같으면 품번 순)으로 출력하세요.

**[응용]** 아래 쿼리는 오류가 납니다. 오류의 원인을 설명하고, 도어 가스켓 **`MGK25528301`** 보다 나중에 등록된 부품 **수**를 구하는 쿼리로 고치세요.

```sql
SELECT part_no, description_kr, created_at
  FROM part_master
 WHERE created_at > (SELECT created_at
                       FROM part_master
                      WHERE description_kr = '도어 가스켓');
```
:::

### 1-5. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
13행. 평균 리드타임은 16.8일입니다(`SELECT ROUND(AVG(lead_time_days), 1) FROM part_sourcing`).

```sql
SELECT part_no, vendor_code, line_type, lead_time_days
  FROM part_sourcing
 WHERE lead_time_days > (SELECT AVG(lead_time_days)
                           FROM part_sourcing)
 ORDER BY lead_time_days DESC, part_no;
```

```result
| part_no | vendor_code | line_type | lead_time_days |
| --- | --- | --- | --- |
| EIC93178801 | V1005 | I | 60 |
| ECP39799101 | V1004 | I | 50 |
| MGL96663301 | V1007 | I | 45 |
| RSS86949501 | V1007 | I | 45 |
| EFN66589301 | V1009 | I | 40 |
| EMT73633001 | V1009 | D | 30 |
| EMT78269001 | V1009 | I | 30 |
| MBR26166001 | V1009 | I | 30 |
| EBA28941901 | V1003 | D | 21 |
| EBA56264701 | V1003 | D | 21 |
| EBA60141001 | V1003 | D | 21 |
| MDR41841501 | V1001 | S | 21 |
| RST13919601 | V1001 | D | 21 |
```
:::

### 1-5. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
```error
ERROR:  more than one row returned by a subquery used as an expression
```

「도어 가스켓」이라는 품명의 부품이 `MGK25528301`(2025-07-15 등록)과 `MGK31172901`(2025-01-28 등록) **2개**라 서브쿼리가 2행을 돌려주기 때문입니다. 품명 대신 품번으로 찾아 1행으로 만듭니다.

```sql
SELECT COUNT(*) AS cnt
  FROM part_master
 WHERE created_at > (SELECT created_at
                       FROM part_master
                      WHERE part_no = 'MGK25528301');
```

```result
| cnt |
| --- |
| 26 |
```

품명은 겹칠 수 있습니다. 4단원 복습 8 「조회와 기록은 항상 품번으로」와 같은 원리로, 서브쿼리도 ==PK(품번)로 조회==하는 것이 가장 안전합니다.
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 2. 다중행 서브쿼리 — 결과가 여러 행일 때

### 2-1. 다중행 연산자 {keep}

서브쿼리 결과가 **여러 행**이면 단일행 연산자 대신 **다중행 연산자**를 씁니다.

| 다중행 연산자 | 참이 되는 경우 |
| --- | --- |
| `IN` | 서브쿼리 결과 중 **하나라도 같으면** |
| `비교연산자 ANY` (= `SOME`) | 서브쿼리 결과 중 **하나라도** 비교 결과가 참이면 |
| `비교연산자 ALL` | 서브쿼리 결과 **모두**와 비교 결과가 참이면 |
| `EXISTS` | 서브쿼리 결과가 **1행이라도 있으면** |

### 2-2. IN — 영국에 있는 근무지 {keep}

**질문:** 영국(`UK`)에 있는 부서는?

나라는 `locations`(근무지)에, 부서는 `departments`에 있습니다. 먼저 영국 근무지 번호를 봅니다.

:::cols
```sql
SELECT location_id, city
  FROM locations
 WHERE country_id = 'UK'
 ORDER BY location_id;
```

```result
| location_id | city |
| --- | --- |
| 2400 | London |
| 2500 | Oxford |
| 2600 | Stretford |
```
:::

이 3개 번호를 `IN (2400, 2500, 2600)`으로 적어 넣는 대신 **서브쿼리로** 넣습니다.

### 2-2. IN — 목록 중 하나와 같으면 {keep}

:::cols
```sql
SELECT department_id, department_name, location_id
  FROM departments
 WHERE location_id IN (SELECT location_id
                         FROM locations
                        WHERE country_id = 'UK')
 ORDER BY department_id;
```

```result
| department_id | department_name | location_id |
| --- | --- | --- |
| 40 | Human Resources | 2400 |
| 80 | Sales | 2500 |
```
:::

서브쿼리가 근무지 번호 3개를 돌려주고, 메인쿼리는 `location_id`가 그 3개 중 하나와 같은 부서만 남깁니다.

### 2-2. 서브쿼리 안에 서브쿼리 {keep}

이번에는 영국 부서의 **부서장**(`departments.manager_id`)이 누구인지 봅니다. 서브쿼리는 여러 겹으로 넣을 수 있고, **가장 안쪽부터** 읽습니다.

:::cols
```sql
SELECT employee_id, first_name, last_name, job_id, department_id
  FROM employees
 WHERE employee_id IN (SELECT manager_id              -- ② 그 근무지 부서의 부서장
                         FROM departments
                        WHERE location_id IN (SELECT location_id  -- ① 영국 근무지
                                                FROM locations
                                               WHERE country_id = 'UK'))
 ORDER BY employee_id;
```

```result
| employee_id | first_name | last_name | job_id | department_id |
| --- | --- | --- | --- | --- |
| 145 | John | Russell | SA_MAN | 80 |
| 203 | Susan | Mavris | HR_REP | 40 |
```
:::

`departments.manager_id`와 `employees.employee_id`는 이름은 달라도 같은 값(직원 번호)입니다(5단원 1-2).

### 2-2. 생각해 보기 — 근무지는 3곳인데 부서는 2개? {keep}

:::try 생각해 보기 — 근무지는 3곳인데 부서는 2개?
영국 근무지는 London·Oxford·Stretford **3곳**인데, `IN`으로 찾은 부서는 **2개**입니다. 나머지 한 근무지에는 무엇이 있을까요? 어떤 쿼리로 확인할 수 있을까요?
:::

:::teacher 강사 확인
- Stretford(2600)에는 부서가 하나도 없습니다. `IN`은 목록 값과 **같은 행만** 남기므로, 짝이 없는 근무지는 결과에 나오지 않습니다.
- 「짝이 없는 쪽」을 찾는 질문은 바로 다음 2-3 `NOT IN`으로 이어집니다. 5단원의 안티 조인(LEFT JOIN + IS NULL)으로도 찾을 수 있다는 점을 짚어 주세요.
:::

### 2-3. NOT IN — 목록의 어느 것과도 같지 않으면 {keep}

**질문:** 영국 근무지 중 **부서가 하나도 없는** 곳은?

:::cols
```sql
SELECT location_id, city
  FROM locations
 WHERE country_id = 'UK'
   AND location_id NOT IN (SELECT location_id
                             FROM departments);
```

```result
| location_id | city |
| --- | --- |
| 2600 | Stretford |
```
:::

서브쿼리는 부서가 있는 근무지 번호 목록이고, `NOT IN`은 그 목록의 **어느 것과도 같지 않은** 근무지만 남깁니다. 2-2의 질문에 대한 답이 Stretford입니다.

### 2-3. NOT IN과 NULL 함정 ⭐ {keep}

:::error NOT IN 목록에 NULL이 하나라도 있으면 → 결과 0행
`NOT IN (A, B)`는 `<> A AND <> B`와 같습니다. 목록에 NULL이 끼면 `<> NULL`이 **참도 거짓도 아닌 값(NULL)** 이 되어, `AND`로 묶인 전체가 참이 될 수 없습니다.

```sql
SELECT COUNT(*) AS cnt FROM departments WHERE department_id NOT IN (10);        -- 26
SELECT COUNT(*) AS cnt FROM departments WHERE department_id NOT IN (10, NULL);  -- 0
SELECT COUNT(*) AS cnt FROM departments WHERE department_id IN     (10, NULL);  -- 1
```

- 첫 줄은 **26**(부서 27개 중 10번만 빠짐), NULL을 넣은 둘째 줄은 **0**입니다.
- 반면 `IN`은 `= A OR = B`라서 NULL이 섞여도 같은 값이 하나 있으면 참입니다(셋째 줄 **1**).

서브쿼리도 똑같습니다. ==NOT IN 서브쿼리의 컬럼에 NULL이 있을 수 있으면==, 서브쿼리 안에 `WHERE 컬럼 IS NOT NULL`을 붙이거나 2-5의 `NOT EXISTS`를 씁니다. (2-5에서 실제 데이터로 확인합니다.)
:::

> 위 예제의 `departments.location_id`에는 지금 NULL이 없어서 결과가 정상으로 나왔습니다. 하지만 **지금 NULL이 없다고 앞으로도 없는 것은 아닙니다.** `CREATE TABLE`에 `NOT NULL` 제약이 있는지 확인해 보세요(Day 4). 이 컬럼에는 `NOT NULL`이 없습니다.

### 2-4. ANY와 ALL — IT 프로그래머의 급여 {keep}

`ANY`와 `ALL`은 `>`, `<`, `=` 같은 **비교 연산자 뒤에** 붙여 씁니다. IT 프로그래머(`job_id = 'IT_PROG'`)의 급여는 다음 5개입니다.

:::cols
```sql
SELECT salary
  FROM employees
 WHERE job_id = 'IT_PROG'
 ORDER BY salary;
```

```result
| salary |
| --- |
| 4200.00 |
| 4800.00 |
| 4800.00 |
| 6000.00 |
| 9000.00 |
```
:::

### 2-4. >= ANY — 하나라도 크거나 같으면 {keep}

**`>= ANY`** — 하나라도 「크거나 같으면」 참 → 사실상 **최솟값(4200) 이상**

**질문:** 배송 부서(50번) 직원 중 급여가 **IT 프로그래머 수준**(IT 프로그래머 급여 중 어느 하나 이상)인 직원은?

:::cols
```sql
SELECT employee_id, first_name, job_id, salary
  FROM employees
 WHERE department_id = 50
   AND salary >= ANY (SELECT salary
                        FROM employees
                       WHERE job_id = 'IT_PROG')
 ORDER BY salary DESC, employee_id;
```

```result
| employee_id | first_name | job_id | salary |
| --- | --- | --- | --- |
| 121 | Adam | ST_MAN | 8200.00 |
| 120 | Matthew | ST_MAN | 8000.00 |
| 122 | Payam | ST_MAN | 7900.00 |
| 123 | Shanta | ST_MAN | 6500.00 |
| 124 | Kevin | ST_MAN | 5800.00 |
| 184 | Nandita | SH_CLERK | 4200.00 |
```
:::

배송 부서 45명 중 관리자(`ST_MAN`) 5명과, IT 프로그래머 최저 급여(4200)와 같은 Nandita가 나왔습니다.

### 2-4. > ALL — 전부보다 크면 {keep}

**`> ALL`** — 전부보다 「커야」 참 → 사실상 **최댓값보다 큼**. 영업 관리자(`SA_MAN`)의 최고 급여는 14000입니다(`SELECT MAX(salary) FROM employees WHERE job_id = 'SA_MAN'` → 14000).

**질문:** **모든** 영업 관리자보다 급여가 많은 직원은?

:::cols
```sql
SELECT employee_id, first_name, job_id, salary
  FROM employees
 WHERE salary > ALL (SELECT salary
                       FROM employees
                      WHERE job_id = 'SA_MAN')
 ORDER BY salary DESC, employee_id;
```

```result
| employee_id | first_name | job_id | salary |
| --- | --- | --- | --- |
| 100 | Steven | AD_PRES | 24000.00 |
| 101 | Neena | AD_VP | 17000.00 |
| 102 | Lex | AD_VP | 17000.00 |
```
:::

### 2-4. ANY · ALL 정리 {keep}

| 쓰는 법 | 같은 뜻 | 판정 |
| --- | --- | --- |
| `> ANY (서브쿼리)` | `> (서브쿼리의 MIN)` | 하나라도 T면 T |
| `> ALL (서브쿼리)` | `> (서브쿼리의 MAX)` | 전부 T여야 T |
| `= ANY (서브쿼리)` | `IN (서브쿼리)` | — |

> `ANY`·`ALL`은 `MIN`·`MAX` 서브쿼리로 바꿔 쓸 수 있는 경우가 많습니다(서브쿼리가 0행이거나 NULL이 섞이면 결과가 달라질 수 있습니다). 읽는 사람이 바로 이해할 수 있는 쪽을 고르세요. 이 교안에서는 `IN`·`EXISTS`를 주로 씁니다.

### 2-5. EXISTS — 짝이 있는가 (상관 서브쿼리) {keep}

`EXISTS`는 서브쿼리 결과가 **1행이라도 있으면 참**입니다. 값을 비교하지 않고 **있는지 없는지만** 봅니다.

**질문:** 직무 이력(`job_history`)이 있는 직원은? (직무나 부서를 바꾼 적이 있는 직원)

:::cols
```sql
SELECT e.employee_id, e.first_name, e.last_name, e.job_id
  FROM employees e
 WHERE EXISTS (SELECT 1
                 FROM job_history h
                WHERE h.employee_id = e.employee_id)
 ORDER BY e.employee_id;
```

```result
| employee_id | first_name | last_name | job_id |
| --- | --- | --- | --- |
| 101 | Neena | Kochhar | AD_VP |
| 102 | Lex | De Haan | AD_VP |
| 114 | Den | Raphaely | PU_MAN |
| 122 | Payam | Kaufling | ST_MAN |
| 176 | Jonathon | Taylor | SA_REP |
| 200 | Jennifer | Whalen | AD_ASST |
| 201 | Michael | Hartstein | MK_MAN |
```
:::

### 2-5. 상관 서브쿼리 읽는 법 {keep}

- 서브쿼리 안의 `h.employee_id = e.employee_id`에서 `e`는 **메인쿼리의 테이블**입니다. 이렇게 메인쿼리의 컬럼을 참조하는 서브쿼리를 **상관(correlated) 서브쿼리**라고 합니다.
- 읽는 법: 「`employees`의 **한 행(e)마다**, 그 직원 번호로 직무 이력이 있는지 찾아보고, 있으면 남긴다.」
- `job_history`는 10행이지만 결과는 **7명**입니다. 101·176·200번은 이력이 2행씩 있어도 **한 번만** 나옵니다. `EXISTS`는 짝이 몇 개인지가 아니라 있는지만 보기 때문입니다(JOIN이었다면 행이 늘어납니다).
- `SELECT 1`의 `1`에는 의미가 없습니다. `EXISTS`는 **행이 있는지**만 보므로 무엇을 SELECT해도 결과가 같습니다.

### 2-5. NOT EXISTS — 짝이 없는 행 {keep}

**질문:** 직원이 한 명도 **없는** 부서는? (5단원 3-3 ① 안티 조인)

```sql
SELECT d.department_id, d.department_name
  FROM departments d
 WHERE NOT EXISTS (SELECT 1
                     FROM employees e
                    WHERE e.department_id = d.department_id)
 ORDER BY d.department_id;
```

- 27개 부서 중 **16개**입니다. 5단원 3-3 ①에서 `LEFT JOIN … WHERE e.employee_id IS NULL`로 찾은 바로 그 16개 부서를 `NOT EXISTS`로 찾은 것입니다.
- `NOT EXISTS`는 **행이 있는지만 보기 때문에** 2-3의 NOT IN NULL 함정이 없습니다.

### 2-5. NOT EXISTS 실행 결과 {keep}

```result 16행
| department_id | department_name |
| --- | --- |
| 120 | Treasury |
| 130 | Corporate Tax |
| 140 | Control And Credit |
| 150 | Shareholder Services |
| 160 | Benefits |
| 170 | Manufacturing |
| 180 | Construction |
| 190 | Contracting |
| 200 | Operations |
| 210 | IT Support |
| 220 | NOC |
| 230 | IT Helpdesk |
| 240 | Government Sales |
| 250 | Retail Sales |
| 260 | Recruiting |
| 270 | Payroll |
```

### 2-5. 생각해 보기 — 같은 질문을 NOT IN으로 쓰면? {keep}

:::try 생각해 보기 — 같은 질문을 NOT IN으로 쓰면?
아래처럼 `NOT IN`으로 직원이 없는 부서 수를 세면 몇 개가 나올까요? 16이 아니라면 왜일까요?

```sql
SELECT COUNT(*) AS cnt
  FROM departments
 WHERE department_id NOT IN (SELECT department_id
                               FROM employees);
```
:::

### 2-5. NOT IN으로 쓰면 — 결과와 고친 쿼리 {keep}

:::answer 결과와 고친 쿼리
```result
| cnt |
| --- |
| 0 |
```

`employees.department_id`에는 부서가 없는 직원 1명(178 Kimberely Grant)의 **NULL**이 있습니다(5단원 3-3 ②). 서브쿼리 목록에 NULL이 섞여 `NOT IN`이 어떤 부서에서도 참이 되지 못했습니다(2-3). 서브쿼리에서 NULL을 빼면 16이 나옵니다.

```sql
SELECT COUNT(*) AS cnt
  FROM departments
 WHERE department_id NOT IN (SELECT department_id
                               FROM employees
                              WHERE department_id IS NOT NULL);
```

```result
| cnt |
| --- |
| 16 |
```
:::

### 2-6. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** 해외 업체(`vendor.is_domestic = 'N'`)에서 사 오는 부품의 품번, 한글 품명, UIT를 UIT 순(같으면 품번 순)으로 출력하세요. 해외 업체 코드는 `vendor`에, 소싱 품목은 `part_sourcing`에, 품명과 UIT는 `part_master`에 있습니다. (`IN` 서브쿼리를 두 겹으로 사용)

**[응용]** 국내 구매 조건(`line_type = 'D'`)인데 리드타임이 **수입품 수준**(수입 `line_type = 'I'` 소싱의 리드타임 중 어느 하나 이상)인 소싱의 품번, 업체 코드, 구매 조건, 리드타임을 `>= ANY`로 구하세요. 같은 조건을 `MIN` 서브쿼리로 바꿔 써서 결과가 같은지도 확인합니다.
:::

### 2-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
8행

```sql
SELECT part_no, description_kr, uit
  FROM part_master
 WHERE part_no IN (SELECT part_no                 -- ② 해외 업체의 소싱 품번
                     FROM part_sourcing
                    WHERE vendor_code IN (SELECT vendor_code  -- ① 해외 업체 코드
                                            FROM vendor
                                           WHERE is_domestic = 'N'))
 ORDER BY uit, part_no;
```

```result
| part_no | description_kr | uit |
| --- | --- | --- |
| ECP39799101 | 컴프레서 | D |
| EFN66589301 | 팬 모터 | D |
| EIC93178801 | 마이컴 | D |
| MBR26166001 | 볼 베어링 | D |
| MGL96663301 | 도어 글라스 | D |
| RSS86949501 | 스테인리스 강판 | D |
| EMT73633001 | 스테이터 | G |
| EMT78269001 | 로터 | G |
```

생각해 보기: `code_uit`에서 G는 **국내 구매품**, D는 **수입 구매품**입니다. 해외 업체에서 사 오는데 UIT가 G인 스테이터·로터는 맞는 데이터일까요?
:::

:::teacher 강사 확인
- `EMT73633001`(스테이터)·`EMT78269001`(로터)는 README 4장 이상 데이터 **A1**(수입 벤더인데 UIT G)에 포함된 품번입니다. Day 2 품질 진단 시간(Q5)에서 다룬 내용이므로 「Day 2에서 JOIN으로 찾은 것을 서브쿼리로도 찾을 수 있다」 정도로 연결하세요.
- 원인 추적(A9, `uit_change_history.line_type_updated = 'N'`)은 Day 2에서 이미 다뤘으므로 여기서는 반복하지 않습니다.
:::

### 2-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
수입 소싱의 리드타임은 30, 30, 40, 45, 45, 50, 60(최솟값 30)입니다.

```sql >= ANY
SELECT part_no, vendor_code, line_type, lead_time_days
  FROM part_sourcing
 WHERE line_type = 'D'
   AND lead_time_days >= ANY (SELECT lead_time_days
                                FROM part_sourcing
                               WHERE line_type = 'I');
```

```sql MIN 서브쿼리
SELECT part_no, vendor_code, line_type, lead_time_days
  FROM part_sourcing
 WHERE line_type = 'D'
   AND lead_time_days >= (SELECT MIN(lead_time_days)
                            FROM part_sourcing
                           WHERE line_type = 'I');
```

```result 두 쿼리 모두
| part_no | vendor_code | line_type | lead_time_days |
| --- | --- | --- | --- |
| EMT73633001 | V1009 | D | 30 |
```

[복습]에서 본 스테이터가 또 나왔습니다. 국내 구매 조건인데 해외 업체(V1009)에서, 수입품만큼 오래 걸려 들어오는 품목입니다.

> `line_type`의 `D`는 국내 구매 조건, `I`는 수입입니다. UIT의 `D`(수입 구매품)와 글자는 같지만 **다른 코드**이니 헷갈리지 마세요.
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 3. 다중열 서브쿼리 — 두 컬럼을 짝으로 비교

### 3-1. (컬럼1, 컬럼2) IN (서브쿼리) {keep}

서브쿼리가 **컬럼 여러 개**를 돌려주면, 메인쿼리도 **같은 개수·같은 순서**로 괄호에 묶어 비교합니다. 주로 `IN`과 함께 씁니다.

**질문:** **부서별로 가장 많이 받는** 직원은?

:::cols
```sql
SELECT department_id, first_name, salary
  FROM employees
 WHERE (department_id, salary) IN (SELECT department_id, MAX(salary)
                                     FROM employees
                                    GROUP BY department_id)
 ORDER BY department_id;
```

```result 총 11행
| department_id | first_name | salary |
| --- | --- | --- |
| 10 | Jennifer | 4400.00 |
| 20 | Michael | 13000.00 |
| 30 | Den | 11000.00 |
| 40 | Susan | 6500.00 |
| 50 | Adam | 8200.00 |
| … | … | … |
| 110 | Shelley | 12008.00 |
```
:::

- 서브쿼리는 「부서 번호 + 그 부서의 최고 급여」 **짝**을 돌려줍니다. 메인쿼리의 `(department_id, salary)`가 그 짝 중 하나와 **둘 다** 같아야 남습니다.
- 4단원에서 `GROUP BY`를 쓰면 `SELECT`에 일반 컬럼(`first_name`)을 쓸 수 없었습니다. ==「그룹의 최댓값을 가진 행 전체」== 를 보고 싶을 때 다중열 서브쿼리를 씁니다.

> 서브쿼리에는 부서가 없는 그룹의 짝 `(NULL, 7000)`도 있지만, 부서가 없는 Kimberely는 결과에 나오지 않습니다. NULL은 `=`로 비교하면 참이 되지 않기 때문입니다(3단원 5-1). 그래서 12개 그룹 중 11행입니다.

### 3-2. 부서별 최저 급여 {keep}

**질문:** 부서별로 급여가 **가장 적은** 직원은? (같은 부서 안에서 최저 급여가 같으면 모두 출력)

:::cols
```sql
SELECT department_id, MIN(salary) AS min_sal
  FROM employees
 GROUP BY department_id
 ORDER BY department_id;
```

```result
| department_id | min_sal |
| --- | --- |
| 10 | 4400.00 |
| 20 | 6000.00 |
| 30 | 2500.00 |
| 40 | 6500.00 |
| 50 | 2100.00 |
| 60 | 4200.00 |
| 70 | 10000.00 |
| 80 | 6100.00 |
| 90 | 17000.00 |
| 100 | 6900.00 |
| 110 | 8300.00 |
| NULL | 7000.00 |
```
:::

부서 번호는 빼고 **급여만** 비교하면 어떻게 될까요?

### 3-2. 단일열 IN으로 쓰면 안 되는 이유 {keep}

두 방식의 결과 행 수를 비교합니다.

:::cols
```sql 다중열 — 부서와 짝으로
SELECT COUNT(*) AS cnt
  FROM employees
 WHERE (department_id, salary) IN (SELECT department_id, MIN(salary)
                                     FROM employees
                                    GROUP BY department_id);
```

```result
| cnt |
| --- |
| 12 |
```
:::

:::cols
```sql 단일열 — 급여만
SELECT COUNT(*) AS cnt
  FROM employees
 WHERE salary IN (SELECT MIN(salary)
                    FROM employees
                   GROUP BY department_id);
```

```result
| cnt |
| --- |
| 26 |
```
:::

### 3-2. 14행이 더 나온 이유 {keep}

- 단일열 쪽이 **14행 더** 나왔습니다. 예를 들어 50번 부서의 Joshua(2500)는 50번의 최저(2100)가 아닌데도 나옵니다. 2500이 **30번 부서의 최저 급여**라 목록 `(4400, 6000, 2500, 6500, 2100, 4200, 10000, 6100, 17000, 6900, 8300, 7000)` 안에 있기 때문입니다.
- ==「부서별」 최솟값은 부서와 짝을 지어야 의미가 있습니다.== 기준 컬럼(`department_id`)까지 함께 비교하세요.

> 같은 부서 안에서 최저 급여가 같은 직원이 여럿이면(예: 90번 Neena·Lex 17000) 모두 나옵니다. 그래서 부서는 11개인데 12행입니다. 1행만 고르는 방법은 Day 3 6교시 `ROW_NUMBER`에서 다룹니다.

### 3-3. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** 원화(`currency = 'KRW'`) 소싱 기준, **업체별로 가장 비싼** 품목의 업체 코드, 품번, 단가(`po_price`)를 업체 코드 순으로 출력하세요. (다중열 서브쿼리 사용)

**[응용]** 업체별로 리드타임이 **가장 긴** 소싱 품목을 찾으려고 합니다. ① `(vendor_code, lead_time_days) IN (…)` 다중열 서브쿼리와 ② `lead_time_days IN (SELECT MAX(lead_time_days) … GROUP BY vendor_code)` 단일열 서브쿼리로 각각 행 수를 세어 비교하고, ②가 왜 늘어나는지 예를 하나 들어 설명하세요.
:::

### 3-3. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
9행

```sql
SELECT vendor_code, part_no, po_price
  FROM part_sourcing
 WHERE (vendor_code, po_price) IN (SELECT vendor_code, MAX(po_price)
                                     FROM part_sourcing
                                    WHERE currency = 'KRW'
                                    GROUP BY vendor_code)
 ORDER BY vendor_code;
```

```result
| vendor_code | part_no | po_price |
| --- | --- | --- |
| V1001 | MDR41841501 | 61000.00 |
| V1002 | RPU53256801 | 6800.00 |
| V1003 | EBA28941901 | 41000.00 |
| V1006 | MTB81885601 | 23000.00 |
| V1008 | MCT60769101 | 6100.00 |
| V1009 | EMT73633001 | 28000.00 |
| V1010 | MGK31172901 | 6900.00 |
| V1011 | MEV24806601 | 17500.00 |
| V1012 | EMT68237401 | 0.00 |
```

통화 조건(`currency = 'KRW'`)은 서브쿼리 안에만 있습니다. 같은 업체에 단가 숫자가 같은 다른 통화 행이 있으면 함께 나올 수 있으므로, 실무에서는 메인쿼리에도 같은 조건을 넣는 편이 안전합니다.
:::

### 3-3. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
① **35행**, ② **49행**(14행 증가)

```sql ① 다중열 — 업체와 짝으로
SELECT COUNT(*) AS cnt
  FROM part_sourcing
 WHERE (vendor_code, lead_time_days) IN (SELECT vendor_code, MAX(lead_time_days)
                                           FROM part_sourcing
                                          GROUP BY vendor_code);
```

```sql ② 단일열 — 리드타임만
SELECT COUNT(*) AS cnt
  FROM part_sourcing
 WHERE lead_time_days IN (SELECT MAX(lead_time_days)
                            FROM part_sourcing
                           GROUP BY vendor_code);
```

예: `V1001`의 나사 `FSC33042701`(7일)은 V1001의 최장(21일)이 아닌데도 ②에 나옵니다. 7일이 **`V1008`의 최장 리드타임**이라 목록 안에 있기 때문입니다. ①이 업체가 12개인데 35행인 것은, 같은 업체 안에서 최장 리드타임이 같은 품목이 여럿이기 때문입니다(예: V1006은 6품목 모두 14일).
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

:::teacher 강사 확인
- 기존 교안 `reference/10. 서브쿼리.sql`의 IN 예제(`SALARY IN (SELECT MAX(SALARY) … GROUP BY DEPARTMENT_ID)`)도 단일열이라 같은 이유로 「부서별 최고 연봉 직원」보다 많은 행이 나옵니다(이 데이터에서 24행, 3-1 다중열은 11행). 3-1의 다중열 방식과 비교해서 보여 주세요.
:::

## 4. 스칼라 서브쿼리 — SELECT절에서 컬럼 하나 만들기

### 4-1. 행마다 값 하나를 가져오기 {keep}

`SELECT` 절에 쓰는 서브쿼리를 **스칼라(scalar) 서브쿼리**라고 합니다. 「스칼라」는 **값 하나**라는 뜻이고, 메인쿼리의 **행마다 1행 1열**을 돌려줘 컬럼 하나가 됩니다. 대부분 2-5의 **상관 서브쿼리** 모양입니다.

**질문:** 급여가 12000 이상인 직원을 부서 **이름**과 함께 보여 주세요.

```sql
SELECT e.employee_id
     , e.first_name
     , e.salary
     , e.department_id
     , (SELECT d.department_name
          FROM departments d
         WHERE d.department_id = e.department_id) AS department_name
  FROM employees e
 WHERE e.salary >= 12000
 ORDER BY e.salary DESC, e.employee_id;
```

### 4-1. 실행 결과 {keep}

```result
| employee_id | first_name | salary | department_id | department_name |
| --- | --- | --- | --- | --- |
| 100 | Steven | 24000.00 | 90 | Executive |
| 101 | Neena | 17000.00 | 90 | Executive |
| 102 | Lex | 17000.00 | 90 | Executive |
| 145 | John | 14000.00 | 80 | Sales |
| 146 | Karen | 13500.00 | 80 | Sales |
| 201 | Michael | 13000.00 | 20 | Marketing |
| 108 | Nancy | 12008.00 | 100 | Finance |
| 205 | Shelley | 12008.00 | 110 | Accounting |
| 147 | Alberto | 12000.00 | 80 | Sales |
```

읽는 법: 「직원 한 행(e)마다, 그 부서 번호로 `departments`에서 이름을 찾아 옆에 붙인다.」 5단원 2-2(직원 정보에 부서 이름 붙이기)의 JOIN과 같은 결과를 **컬럼 단위로** 만드는 방법입니다.

### 4-2. 짝이 없으면 NULL {keep}

**질문:** 급여가 7000~7500인 직원의 부서 이름과 직무 이름을 함께 보여 주세요.

```sql
SELECT e.employee_id
     , e.first_name
     , e.salary
     , (SELECT d.department_name
          FROM departments d
         WHERE d.department_id = e.department_id) AS department_name
     , (SELECT j.job_title
          FROM jobs j
         WHERE j.job_id = e.job_id)               AS job_title
  FROM employees e
 WHERE e.salary BETWEEN 7000 AND 7500
 ORDER BY e.salary, e.employee_id;
```

### 4-2. 실행 결과 {keep}

```result
| employee_id | first_name | salary | department_name | job_title |
| --- | --- | --- | --- | --- |
| 155 | Oliver | 7000.00 | Sales | Sales Representative |
| 161 | Sarath | 7000.00 | Sales | Sales Representative |
| 178 | Kimberely | 7000.00 | NULL | Sales Representative |
| 164 | Mattea | 7200.00 | Sales | Sales Representative |
| 172 | Elizabeth | 7300.00 | Sales | Sales Representative |
| 171 | William | 7400.00 | Sales | Sales Representative |
| 154 | Nanette | 7500.00 | Sales | Sales Representative |
| 160 | Louise | 7500.00 | Sales | Sales Representative |
```

- 부서가 없는 Kimberely(178)는 `department_name`이 **NULL**입니다. 행이 사라지지 않고 NULL로 남는다는 점이 **LEFT JOIN과 같습니다**(5단원 3-2의 107행과 비교해 보세요).
- 직무는 모든 직원에게 있으므로 `job_title`은 빈칸 없이 채워졌습니다. 스칼라 서브쿼리는 **컬럼마다 따로** 짝을 찾습니다.

### 4-2. 집계 함수와 함께 {keep}

스칼라 서브쿼리 안에서 집계하면 행마다 「개수」, 「최댓값」을 붙일 수 있습니다.

**질문:** 90~130번 부서마다 직원 수와 최고 급여를 보여 주세요.

:::cols
```sql
SELECT d.department_id
     , d.department_name
     , (SELECT COUNT(*)
          FROM employees e
         WHERE e.department_id = d.department_id) AS emp_cnt
     , (SELECT MAX(e.salary)
          FROM employees e
         WHERE e.department_id = d.department_id) AS max_sal
  FROM departments d
 WHERE d.department_id BETWEEN 90 AND 130
 ORDER BY d.department_id;
```

```result
| department_id | department_name | emp_cnt | max_sal |
| --- | --- | --- | --- |
| 90 | Executive | 3 | 24000.00 |
| 100 | Finance | 6 | 12008.00 |
| 110 | Accounting | 2 | 12008.00 |
| 120 | Treasury | 0 | NULL |
| 130 | Corporate Tax | 0 | NULL |
```
:::

4단원 2-2의 「부서별 직원 수」(`GROUP BY`)에는 직원이 있는 부서만 나왔습니다. **부서 테이블을 기준으로** 스칼라 서브쿼리를 붙이면 빈 부서(120·130)도 나오고, 대상 행이 없을 때 `COUNT`는 **0**, `MAX`는 **NULL**을 돌려줍니다.

### 4-3. 주의 ① 행마다 「1행」이 아니면 오류 {keep}

:::error 행마다 「1행」이 아니면 오류
20번 부서(Marketing)는 직원이 **2명**입니다. 부서마다 직원 이름을 스칼라 서브쿼리로 가져오면 오류가 납니다.

```sql
SELECT d.department_id
     , d.department_name
     , (SELECT e.first_name
          FROM employees e
         WHERE e.department_id = d.department_id) AS emp_name
  FROM departments d
 WHERE d.department_id IN (10, 20);
```

```error
ERROR:  more than one row returned by a subquery used as an expression
```

직원이 1명뿐인 10번 부서(`WHERE d.department_id = 10`)만 조회하면 오류 없이 `Jennifer`가 나옵니다. 하지만 ==지금 데이터에서 오류가 안 난다고 안전한 것이 아닙니다.== 10번 부서에 내일 직원이 한 명 더 들어오면 같은 쿼리가 오류로 바뀝니다. 여러 직원을 모두 봐야 하는 질문은 **JOIN**으로 풉니다(5단원).
:::

### 4-3. 주의 ② 컬럼이 2개여도 오류 {keep}

:::error 컬럼이 2개여도 오류
```sql
SELECT e.employee_id
     , (SELECT d.department_name, d.location_id
          FROM departments d
         WHERE d.department_id = e.department_id)
  FROM employees e
 LIMIT 1;
```

```error
ERROR:  subquery must return only one column
```

스칼라 서브쿼리는 **1행 1열**입니다. 컬럼이 두 개 필요하면 스칼라 서브쿼리를 두 개 쓰거나 JOIN을 씁니다.
:::

:::teacher 강사 확인
- 4-1·4-2의 부서 이름 서브쿼리는 `departments`의 **PK(`department_id`)** 로 찾으므로 1행을 넘을 수 없어 안전합니다. 4-3 ①처럼 PK가 아닌 컬럼으로 찾으면 데이터가 늘어날 때 오류가 날 수 있습니다. 질문이 나오면 「`MAX`·`SUM` 같은 집계 함수로 감싸면 1행이 보장된다」로 답하세요(7장 복습 6번).
:::

### 4-4. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `part_sourcing`에는 업체 코드만 있고, 업체 이름은 `vendor`에 있습니다. 스칼라 서브쿼리로 업체 이름(`vendor_name`)을 붙여, 수입(`line_type = 'I'`) 소싱 품목의 품번, 업체 코드, 업체 이름, 리드타임을 리드타임이 긴 순(같으면 품번 순)으로 출력하세요.

**[응용]** 체결 부품(`class_lv1 = 'F'`)마다 BOM에 **자식으로 쓰인 횟수**(`used_cnt`)와 **쓰인 모델 수**(`model_cnt`)를 스칼라 서브쿼리로 붙여 품번 순으로 출력하세요. 이어서 부모 품번(`parent_part_no`)도 스칼라 서브쿼리로 붙이면 어떻게 되는지 확인하고 이유를 설명하세요.
:::

### 4-4. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
7행

```sql
SELECT s.part_no
     , s.vendor_code
     , (SELECT v.vendor_name
          FROM vendor v
         WHERE v.vendor_code = s.vendor_code) AS vendor_name
     , s.lead_time_days
  FROM part_sourcing s
 WHERE s.line_type = 'I'
 ORDER BY s.lead_time_days DESC, s.part_no;
```

```result
| part_no | vendor_code | vendor_name | lead_time_days |
| --- | --- | --- | --- |
| EIC93178801 | V1005 | NanoChip Semiconductor | 60 |
| ECP39799101 | V1004 | AsiaComp Co., Ltd. | 50 |
| MGL96663301 | V1007 | Global Steel Trading | 45 |
| RSS86949501 | V1007 | Global Steel Trading | 45 |
| EFN66589301 | V1009 | Pacific Motor Parts | 40 |
| EMT78269001 | V1009 | Pacific Motor Parts | 30 |
| MBR26166001 | V1009 | Pacific Motor Parts | 30 |
```

5단원 2-6 확인 문제(소싱 정보에 업체 이름 붙이기)의 JOIN과 같은 결과를 컬럼 단위로 만든 것입니다.
:::

### 4-4. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
3행

```sql
SELECT p.part_no
     , p.description_kr
     , (SELECT COUNT(*)
          FROM bom_structure b
         WHERE b.child_part_no = p.part_no) AS used_cnt
     , (SELECT COUNT(DISTINCT b.model_part_no)
          FROM bom_structure b
         WHERE b.child_part_no = p.part_no) AS model_cnt
  FROM part_master p
 WHERE p.class_lv1 = 'F'
 ORDER BY p.part_no;
```

```result
| part_no | description_kr | used_cnt | model_cnt |
| --- | --- | --- | --- |
| FSC33042701 | 나사 M5x16 | 3 | 1 |
| FSC67181101 | 나사 M4x12 | 3 | 2 |
| FTP68745401 | 필라멘트 테이프 | 3 | 2 |
```

나사 M4x12와 필라멘트 테이프는 두 모델에 모두 쓰이는 공용 부품입니다(4단원 복습 7). 부모 품번을 붙이면 오류가 납니다.

```sql
SELECT p.part_no
     , (SELECT b.parent_part_no
          FROM bom_structure b
         WHERE b.child_part_no = p.part_no) AS parent
  FROM part_master p
 WHERE p.class_lv1 = 'F';
```

```error
ERROR:  more than one row returned by a subquery used as an expression
```

세 부품 모두 BOM에 3번씩 쓰여 **부모 행이 3개**라, 행마다 1행이어야 하는 스칼라 서브쿼리 규칙(4-3 ①)에 어긋납니다. 여러 부모를 모두 봐야 하는 질문(Where-Used)은 JOIN으로 풉니다(Day 2).
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 5. 인라인 뷰 — FROM절의 가상 테이블

### 5-1. 집계 결과를 테이블처럼 쓰기 {keep}

`FROM` 절에 쓰는 서브쿼리를 **인라인 뷰(inline view)** 라고 합니다. 서브쿼리의 결과표를 **임시 테이블처럼** 놓고, 다른 테이블과 JOIN하거나 그 컬럼으로 조건을 걸 수 있습니다.

**질문:** 직원이 5명 이상인 부서의 **이름**, 근무지, 직원 수, 최고 급여는?

```sql
SELECT d.department_id
     , d.department_name
     , d.location_id
     , s.emp_cnt
     , s.max_sal
  FROM departments d
  JOIN (SELECT department_id
             , COUNT(*)    AS emp_cnt
             , MAX(salary) AS max_sal
          FROM employees
         GROUP BY department_id) s
    ON s.department_id = d.department_id
 WHERE s.emp_cnt >= 5
 ORDER BY s.emp_cnt DESC, d.department_id;
```

### 5-1. 실행 결과 {keep}

```result
| department_id | department_name | location_id | emp_cnt | max_sal |
| --- | --- | --- | --- | --- |
| 50 | Shipping | 1500 | 45 | 8200.00 |
| 80 | Sales | 2500 | 34 | 14000.00 |
| 30 | Purchasing | 1700 | 6 | 11000.00 |
| 100 | Finance | 1700 | 6 | 12008.00 |
| 60 | IT | 1400 | 5 | 9000.00 |
```

- 괄호 안은 4단원 2-2의 「부서별 직원 수」 쿼리에 최고 급여를 더한 것입니다. 그 결과표에 `s`라는 이름을 붙여 `departments`와 JOIN했습니다.
- 4단원 3-1(직원 5명 이상인 직책)에서 `HAVING COUNT(*) >= 5`로 걸렀던 조건을, 인라인 뷰 밖에서는 **일반 컬럼처럼** `WHERE s.emp_cnt >= 5`로 씁니다. 인라인 뷰 안에서 만든 **별칭(`emp_cnt`)은 바깥에서 컬럼 이름**이 됩니다.

> 인라인 뷰에는 `s`처럼 **별칭을 붙이는 습관**을 들이세요. PostgreSQL 16부터는 별칭을 생략해도 실행되지만, 별칭이 없으면 바깥에서 `s.emp_cnt`처럼 어느 결과표의 컬럼인지 적을 수 없습니다.

### 5-2. 그룹의 최댓값 행 찾기 — 다중열 서브쿼리와 비교 {keep}

3-1의 「부서별 최고 급여 직원」을 인라인 뷰 + JOIN으로 풀 수도 있습니다.

:::cols
```sql
SELECT e.department_id, e.first_name, e.salary
  FROM employees e
  JOIN (SELECT department_id
             , MAX(salary) AS max_sal
          FROM employees
         GROUP BY department_id) m
    ON m.department_id = e.department_id
   AND m.max_sal       = e.salary
 ORDER BY e.department_id;
```

```result
| department_id | first_name | salary |
| --- | --- | --- |
| 10 | Jennifer | 4400.00 |
| 20 | Michael | 13000.00 |
| 30 | Den | 11000.00 |
| 40 | Susan | 6500.00 |
| 50 | Adam | 8200.00 |
| 60 | Alexander | 9000.00 |
| 70 | Hermann | 10000.00 |
| 80 | John | 14000.00 |
| 90 | Steven | 24000.00 |
| 100 | Nancy | 12008.00 |
| 110 | Shelley | 12008.00 |
```
:::

| | 다중열 서브쿼리 (3-1) | 인라인 뷰 + JOIN (5-2) |
| --- | --- | --- |
| 서브쿼리 위치 | `WHERE` | `FROM` |
| 결과 | 같음 (11행) | 같음 (11행) |
| 서브쿼리의 다른 집계 값(예: 직원 수)을 SELECT에 | 쓸 수 없음 | 인라인 뷰 컬럼으로 **쓸 수 있음** |

### 5-3. 먼저 JOIN하고 집계하면 ⭐ {keep}

**질문:** 50번·80번 부서의 급여 합계와 직무 이력(`job_history`) 건수를 한 표로 보여 주세요.

4단원 2-5에서 급여 합계는 50번 **156,400**, 80번 **304,500**이었고, 직무 이력은 두 부서 모두 **2건**입니다. 직원과 직무 이력을 부서 번호로 먼저 JOIN하고 집계하면 어떻게 될까요?

:::cols
```sql
SELECT e.department_id
     , SUM(e.salary) AS total_sal
     , COUNT(*)      AS hist_cnt
  FROM employees e
  JOIN job_history h
    ON h.department_id = e.department_id
 WHERE e.department_id IN (50, 80)
 GROUP BY e.department_id
 ORDER BY e.department_id;
```

```result
| department_id | total_sal | hist_cnt |
| --- | --- | --- |
| 50 | 312800.00 | 90 |
| 80 | 609000.00 | 68 |
```
:::

오류는 없지만 **두 값 모두 틀렸습니다.** 80번 부서의 직원 34행이 그 부서의 직무 이력 2행과 각각 짝지어져 **68행**이 되었고, 급여가 2번씩 더해졌습니다(304,500 × 2 = 609,000). 50번도 45 × 2 = 90행입니다.

### 5-3. 집계 먼저, 조인 나중 ⭐ {keep}

각 테이블을 **인라인 뷰에서 먼저 부서당 1행씩으로 집계**한 뒤 JOIN하면 맞는 값이 나옵니다.

:::cols
```sql
SELECT es.department_id
     , es.total_sal
     , jh.hist_cnt
  FROM (SELECT department_id
             , SUM(salary) AS total_sal
          FROM employees
         GROUP BY department_id) es
  JOIN (SELECT department_id
             , COUNT(*) AS hist_cnt
          FROM job_history
         GROUP BY department_id) jh
    ON jh.department_id = es.department_id
 WHERE es.department_id IN (50, 80)
 ORDER BY es.department_id;
```

```result
| department_id | total_sal | hist_cnt |
| --- | --- | --- |
| 50 | 156400.00 | 2 |
| 80 | 304500.00 | 2 |
```
:::

==1 : N 관계의 두 테이블을 각각 합계 낼 때는, 집계를 먼저 하고 JOIN은 나중에== 합니다. 5단원 4-3 오류 상자에서 말로 본 「늘어난 행에 SUM」 문제를 숫자로 확인한 것입니다. 오늘 이어지는 소요량·재료비 계산에서 숫자가 「몇 배로 부풀어」 나오면 이 문제부터 의심하세요.

### 5-4. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** 소싱 품목이 5개 이상인 업체의 업체 코드, **이름**, 국내 여부(`is_domestic`), 품목 수(`item_cnt`), 최장 리드타임(`max_lt`)을 품목 수가 많은 순(같으면 업체 코드 순)으로 출력하세요. (업체별 집계 인라인 뷰 + `vendor` JOIN)

**[응용]** 모델별 12월 생산계획 총수량(`total_plan`)과 BOM 행 수(`bom_lines`)를 한 표로 출력하세요. 5단원 복습 7처럼 `production_plan`과 `bom_structure`를 먼저 JOIN한 뒤 `SUM`·`COUNT`하면 냉장고(`TRF38316001`)가 3,460대·39행이 아니라 **134,940대·390행**으로 부풀어 나옵니다. 인라인 뷰로 「집계 먼저, 조인 나중」을 적용해 맞는 값을 구하세요.
:::

### 5-4. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
6행

```sql
SELECT v.vendor_code
     , v.vendor_name
     , v.is_domestic
     , s.item_cnt
     , s.max_lt
  FROM vendor v
  JOIN (SELECT vendor_code
             , COUNT(*)            AS item_cnt
             , MAX(lead_time_days) AS max_lt
          FROM part_sourcing
         GROUP BY vendor_code) s
    ON s.vendor_code = v.vendor_code
 WHERE s.item_cnt >= 5
 ORDER BY s.item_cnt DESC, v.vendor_code;
```

```result
| vendor_code | vendor_name | is_domestic | item_cnt | max_lt |
| --- | --- | --- | --- | --- |
| V1001 | 한빛정밀(주) | Y | 9 | 21 |
| V1011 | 태양전장(주) | Y | 8 | 14 |
| V1003 | 세진전자(주) | Y | 6 | 21 |
| V1006 | 우성사출(주) | Y | 6 | 14 |
| V1008 | 동아포장(주) | Y | 6 | 7 |
| V1010 | 한성고무(주) | Y | 5 | 14 |
```

4단원 3-6 확인 문제에서 `HAVING COUNT(*) >= 5`로 걸렀던 조건을, 인라인 뷰 밖에서는 `WHERE s.item_cnt >= 5`로 씁니다.
:::

### 5-4. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
```sql
SELECT pl.model_part_no
     , pl.total_plan
     , bm.bom_lines
  FROM (SELECT model_part_no
             , SUM(plan_qty) AS total_plan
          FROM production_plan
         GROUP BY model_part_no) pl
  JOIN (SELECT model_part_no
             , COUNT(*) AS bom_lines
          FROM bom_structure
         GROUP BY model_part_no) bm
    ON bm.model_part_no = pl.model_part_no
 ORDER BY pl.model_part_no;
```

```result
| model_part_no | total_plan | bom_lines |
| --- | --- | --- |
| TRF38316001 | 3460 | 39 |
| TWM61868701 | 4520 | 43 |
```

먼저 JOIN하면 냉장고의 계획 10행이 BOM 39행과 각각 짝지어져 **390행**이 되고, 계획 수량이 39번씩 더해집니다(3,460 × 39 = 134,940). 계획과 BOM을 각각 모델당 1행으로 집계한 뒤 JOIN해야 합니다.
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 6. WITH — 서브쿼리에 이름 붙여 단계 나누기

### 6-1. 인라인 뷰를 위로 꺼내기 {keep}

5-3처럼 인라인 뷰가 두세 개 들어가면 괄호가 겹쳐 읽기 어려워집니다. **`WITH`** 절을 쓰면 서브쿼리에 **이름을 붙여 쿼리 맨 위로 꺼낼** 수 있습니다. 이렇게 이름 붙인 서브쿼리를 **CTE(Common Table Expression)** 라고 합니다.

```text WITH의 모양
WITH 이름1 AS ( SELECT … ),      ← 1단계
     이름2 AS ( SELECT … )       ← 2단계
SELECT …                         ← 최종 단계: 이름1, 이름2를 테이블처럼 사용
  FROM 이름1
  JOIN 이름2 ON …;
```

### 6-1. 5-3의 쿼리를 WITH로 {keep}

:::cols
```sql
WITH es AS (                          -- 1단계: 부서별 급여 합계
     SELECT department_id
          , SUM(salary) AS total_sal
       FROM employees
      GROUP BY department_id
), jh AS (                            -- 2단계: 부서별 직무 이력 건수
     SELECT department_id
          , COUNT(*) AS hist_cnt
       FROM job_history
      GROUP BY department_id
)
SELECT es.department_id               -- 3단계: 두 결과 JOIN
     , es.total_sal
     , jh.hist_cnt
  FROM es
  JOIN jh
    ON jh.department_id = es.department_id
 WHERE es.department_id IN (50, 80)
 ORDER BY es.department_id;
```

```result
| department_id | total_sal | hist_cnt |
| --- | --- | --- |
| 50 | 156400.00 | 2 |
| 80 | 304500.00 | 2 |
```
:::

- 결과는 5-3과 **똑같습니다.** 바뀐 것은 **읽는 순서**뿐입니다. 위에서 아래로 「1단계 → 2단계 → 최종」으로 읽힙니다.
- 각 단계(`es`, `jh`)는 따로 떼어 실행해 볼 수 있어, ==중간 결과를 확인하며 쿼리를 쌓아 올리기== 좋습니다.

### 6-1. 인라인 뷰와 WITH 비교 {keep}

| | 인라인 뷰 | WITH (CTE) |
| --- | --- | --- |
| 위치 | `FROM` 절 괄호 안 | 쿼리 맨 위 |
| 읽는 순서 | 안쪽 → 바깥쪽 | 위 → 아래 |
| 같은 결과를 두 번 쓰기 | 서브쿼리를 두 번 적어야 함 | 이름으로 여러 번 참조 |

> 다음 교시(재귀 CTE)에서는 `WITH RECURSIVE`로 **자기 자신을 다시 부르는** CTE를 만들어 BOM 트리를 레벨 끝까지 펼칩니다. 오늘 익힌 「`WITH 이름 AS (…)` 후 테이블처럼 쓰기」가 그 출발점입니다.

### 6-2. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[응용]** 5-4 [응용]의 인라인 뷰 두 개(모델별 계획 합계, 모델별 BOM 행 수)를 `WITH pl AS (…), bm AS (…)`로 꺼내 다시 작성하세요. 결과가 5-4와 같은지 확인합니다.
:::

### 6-2. 확인 문제 답 {keep}

:::answer [응용] 예시 답안
결과는 5-4 [응용]과 같은 2행입니다.

```sql
WITH pl AS (                          -- 1단계: 모델별 계획 합계
     SELECT model_part_no
          , SUM(plan_qty) AS total_plan
       FROM production_plan
      GROUP BY model_part_no
), bm AS (                            -- 2단계: 모델별 BOM 행 수
     SELECT model_part_no
          , COUNT(*) AS bom_lines
       FROM bom_structure
      GROUP BY model_part_no
)
SELECT pl.model_part_no               -- 3단계: 두 결과 JOIN
     , pl.total_plan
     , bm.bom_lines
  FROM pl
  JOIN bm
    ON bm.model_part_no = pl.model_part_no
 ORDER BY pl.model_part_no;
```

```result
| model_part_no | total_plan | bom_lines |
| --- | --- | --- |
| TRF38316001 | 3460 | 39 |
| TWM61868701 | 4520 | 43 |
```
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 7. 복습 문제

### 7-0. 복습 문제 안내 {keep}

> 범위: 서브쿼리 전체(단일행 · 다중행 · 다중열 · 스칼라 · 인라인 뷰 · WITH). `bom` 스키마의 테이블로 풀어 주세요. 실행 전: `SET search_path TO bom;` 출력 순서는 `ORDER BY` 기준입니다.

```icons 여섯 문항
equal | 1 · 단일행 | 도어 가스켓과 리드타임이 같은 품목 | rose
list-checks | 2 · IN | 입고 예정이 있는 부품 | plum
file-x | 3 · NOT EXISTS | 소싱 정보 없는 구매품 | lime
table | 4 · 스칼라 | 입고 예정 + 업체명·현재고 | ivory
chart-bar | 5 · (심화) 인라인 뷰 | 평균 이상 품목 수 업체 | plum
refrigerator | 6 · (심화) WITH | 컴프레서 수급 균형 | hot
```

### 7-1. 복습 1 · 2 {keep}

**1.** 도어 가스켓(`MGK25528301`)과 리드타임이 같은 소싱 품목의 품번, 업체 코드, 리드타임을 업체 코드 → 품번 순으로 출력하세요. 리드타임 값(10)을 직접 적지 말고 서브쿼리로 구합니다. [힌트: 단일행 서브쿼리, `=`]

```result 출력 결과 (총 7행)
| part_no | vendor_code | lead_time_days |
| --- | --- | --- |
| RPP53183301 | V1002 | 10 |
| RPU53256801 | V1002 | 10 |
| RRS44997401 | V1002 | 10 |
| MFT20558801 | V1010 | 10 |
| MGK25528301 | V1010 | 10 |
| MGK31172901 | V1010 | 10 |
| MHS18920401 | V1010 | 10 |
```

**2.** 입고 예정(`scheduled_receipt`)이 있는 부품의 품번, 한글 품명, UIT를 품번 순으로 출력하세요. 2-5의 `EXISTS`로도 풀 수 있지만, 이번에는 `IN`으로 풀어 보세요.

```result 출력 결과 (총 5행)
| part_no | description_kr | uit |
| --- | --- | --- |
| EBA56264701 | 메인 PCB 조립체 | G |
| ECP39799101 | 컴프레서 | D |
| EIC93178801 | 마이컴 | D |
| MGL96663301 | 도어 글라스 | D |
| RSS86949501 | 스테인리스 강판 | D |
```

### 7-2. 복습 3 · 4 {keep}

**3.** 구매품·관리용 품목(UIT가 G, D, X)인데 소싱 정보(`part_sourcing`)가 하나도 없는 부품을 찾으세요. [힌트: `NOT EXISTS` + 상관 서브쿼리]

```result 출력 결과 (총 1행)
| part_no | description_kr | uit |
| --- | --- | --- |
| SAA76541601 | 메인 펌웨어 | X |
```

**4.** 입고 예정 6건에 업체 이름(`vendor_name`)과 같은 사이트의 현재고(`on_hand`)를 붙여 입고 예정일 → 입고 번호 순으로 출력하세요. [힌트: 스칼라 서브쿼리 2개. 재고는 `part_no`와 `site_code`가 모두 같아야 합니다.]

```result 출력 결과 (총 6행)
| receipt_id | part_no | eta_date | qty | vendor_name | on_hand |
| --- | --- | --- | --- | --- | --- |
| 6 | EBA56264701 | 2026-12-04 | 2000.00 | 세진전자(주) | 5970.00 |
| 3 | MGL96663301 | 2026-12-05 | 1500.00 | Global Steel Trading | 2600.00 |
| 1 | ECP39799101 | 2026-12-08 | 800.00 | AsiaComp Co., Ltd. | 1150.00 |
| 4 | EIC93178801 | 2026-12-10 | 6000.00 | NanoChip Semiconductor | 8428.00 |
| 5 | RSS86949501 | 2026-12-12 | 800.00 | Global Steel Trading | 1922.00 |
| 2 | ECP39799101 | 2026-12-15 | 1600.00 | AsiaComp Co., Ltd. | 1150.00 |
```

### 7-3. 복습 5 · 6 (심화) {keep}

**5.** (심화) 업체별 소싱 품목 수를 구하되, 「업체당 평균 품목 수」 이상인 업체만 품목 수가 많은 순(같으면 업체 코드 순)으로 출력하세요.

[힌트] (1) 업체당 평균 품목 수 = 업체별 품목 수(인라인 뷰)의 `AVG` → 4.33… (2) (1)을 `HAVING`의 단일행 서브쿼리로 넣습니다. `HAVING COUNT(*) >= (SELECT AVG(…) FROM (…) t)`

```result 출력 결과 (총 6행)
| vendor_code | item_cnt |
| --- | --- |
| V1001 | 9 |
| V1011 | 8 |
| V1003 | 6 |
| V1006 | 6 |
| V1008 | 6 |
| V1010 | 5 |
```

**6.** (심화) 냉장고(`TRF38316001`) 1대에는 컴프레서(`ECP39799101`)가 1개 들어갑니다(BOM: 냉장고 세트 → 냉동 사이클 조립체 1 → 컴프레서 1). 12월 냉장고 계획 총수량(`plan_qty`), 컴프레서 현재고(`on_hand`), 컴프레서 입고 예정 합계(`receipt_qty`)를 스칼라 서브쿼리 3개로 한 행에 구하고, `WITH`를 이용해 남는 수량(`balance = on_hand + receipt_qty - plan_qty`)까지 출력하세요.

```result 출력 결과 (총 1행)
| plan_qty | on_hand | receipt_qty | balance |
| --- | --- | --- | --- |
| 3460 | 1150.00 | 2400.00 | 90.00 |
```

### 7-4. 복습 1 · 2 답 {keep}

:::answer 복습 1 · 2 예시 답안
```sql 1
SELECT part_no, vendor_code, lead_time_days
  FROM part_sourcing
 WHERE lead_time_days = (SELECT lead_time_days
                           FROM part_sourcing
                          WHERE part_no = 'MGK25528301')
 ORDER BY vendor_code, part_no;
```

```sql 2
SELECT part_no, description_kr, uit
  FROM part_master
 WHERE part_no IN (SELECT part_no
                     FROM scheduled_receipt)
 ORDER BY part_no;
```
:::

### 7-5. 복습 3 · 4 답 {keep}

:::answer 복습 3 · 4 예시 답안
```sql 3
SELECT p.part_no, p.description_kr, p.uit
  FROM part_master p
 WHERE p.uit IN ('G', 'D', 'X')
   AND NOT EXISTS (SELECT 1
                     FROM part_sourcing s
                    WHERE s.part_no = p.part_no)
 ORDER BY p.part_no;
```

```sql 4
SELECT r.receipt_id
     , r.part_no
     , r.eta_date
     , r.qty
     , (SELECT v.vendor_name
          FROM vendor v
         WHERE v.vendor_code = r.vendor_code) AS vendor_name
     , (SELECT i.on_hand_qty
          FROM inventory i
         WHERE i.part_no   = r.part_no
           AND i.site_code = r.site_code)     AS on_hand
  FROM scheduled_receipt r
 ORDER BY r.eta_date, r.receipt_id;
```

- 3번 결과의 의미: 메인 펌웨어(`SAA76541601`)는 UIT X(관리용: 문서·정보)라 구매 단가가 없을 수 있는 품목입니다. 같은 X인 사용설명서(`MFL37467701`)는 소싱 정보(V1008)가 있으므로, 두 품목을 비교해 「없어도 되는 빈칸인지」 판단해 보세요.
- 4번의 재고 서브쿼리는 `SUM` 없이 썼습니다. 같은 부품의 재고 행이 여러 개가 될 수 있다면, 안전하게는 6번처럼 `SUM(i.on_hand_qty)`로 감쌉니다.
:::

### 7-6. 복습 5 · 6 답 {keep}

:::answer 복습 5 · 6 예시 답안
```sql 5
SELECT vendor_code
     , COUNT(*) AS item_cnt
  FROM part_sourcing
 GROUP BY vendor_code
HAVING COUNT(*) >= (SELECT AVG(item_cnt)
                      FROM (SELECT vendor_code
                                 , COUNT(*) AS item_cnt
                              FROM part_sourcing
                             GROUP BY vendor_code) t)
 ORDER BY item_cnt DESC, vendor_code;
```

```sql 6
WITH t AS (
     SELECT (SELECT SUM(plan_qty)
               FROM production_plan
              WHERE model_part_no = 'TRF38316001') AS plan_qty
          , (SELECT SUM(on_hand_qty)
               FROM inventory
              WHERE part_no = 'ECP39799101')       AS on_hand
          , (SELECT SUM(qty)
               FROM scheduled_receipt
              WHERE part_no = 'ECP39799101')       AS receipt_qty
)
SELECT plan_qty
     , on_hand
     , receipt_qty
     , on_hand + receipt_qty - plan_qty AS balance
  FROM t;
```

- 5번의 `t`처럼, 서브쿼리 안에 인라인 뷰가 또 들어갈 수 있습니다. 가장 안쪽 `(SELECT vendor_code, COUNT(*) … GROUP BY vendor_code)`만 먼저 실행해 12행이 나오는지 확인하면서 쌓아 올리세요.
- 6번은 **12월 총량**만 보면 90개가 남지만, 12/15 입고(1,600)는 계획 마지막 날(12/14) 이후이고 `receipt_type`도 Planned(계획 입고)입니다. 날짜별로 따져 보면 부족한 날이 생깁니다 — Day 3 7교시 MRP 결품 예측(Q11)에서 **결품 발생일**을 구합니다. 6번처럼 `SUM`으로 감싸 두면 재고 행이 여러 개여도 스칼라 서브쿼리가 1행을 보장합니다.
:::

:::teacher 강사 확인
- 6번의 결품 시점은 README 4장 이상 데이터 **A7**(컴프레서 on-hand 1,150, 12/4 결품, 12/8 800 입고로도 미복구)입니다. 훈련생이 「90개 남으니 괜찮다」고 답하면, 총량 비교의 한계를 짚고 7교시로 넘기세요.
:::

## 8. 정리

### 8-1. 오늘 배운 것 {keep}

:::summary
- **서브쿼리**: SQL 안의 SELECT. 괄호 안이 먼저 값(또는 표)이 된다고 읽습니다. 값을 적어 넣지 않고 「값을 구하는 방법」을 넣습니다.
- **위치별 이름**: `WHERE`·`HAVING` → (일반) 서브쿼리 / `SELECT` → 스칼라 서브쿼리 / `FROM` → 인라인 뷰 / 맨 위 `WITH` → CTE.
- **단일행 서브쿼리**: 결과 1행 → `=`, `>`, `<` 등. 여러 행이면 오류, 0행이면 NULL이 되어 결과 0행(오류 없음).
- **다중행 서브쿼리**: `IN`(하나라도 같으면), `ANY`(하나라도), `ALL`(전부), `EXISTS`(1행이라도 있으면).
- **NOT IN 함정**: 서브쿼리 결과에 NULL이 하나라도 있으면 결과 0행. `IS NOT NULL`로 거르거나 `NOT EXISTS`를 씁니다.
- **다중열 서브쿼리**: `(컬럼1, 컬럼2) IN (SELECT …)`. 「그룹별 최댓값 행」은 기준 컬럼과 짝으로 비교해야 합니다.
- **스칼라 서브쿼리**: 행마다 **1행 1열**. 짝이 없으면 NULL(LEFT JOIN과 같음), 2행 이상이면 오류.
- **인라인 뷰**: 집계 결과를 테이블처럼 JOIN. 1 : N 테이블은 **집계 먼저, 조인 나중**.
- **WITH**: 서브쿼리에 이름을 붙여 위에서 아래로 읽히게 단계를 나눕니다. 다음 교시 재귀 CTE의 출발점.
:::

### 8-2. 확인 문제

:::quiz
Q. `WHERE salary > (SELECT salary FROM employees WHERE first_name = 'David')`가 오류 나는 이유와 고치는 방법은?
A. David가 3명이라 서브쿼리가 3행을 돌려주는데 `>`는 값 하나와만 비교할 수 있기 때문입니다. 한 사람과 비교하려면 `employee_id`(PK)로 찾고, 여러 값과 비교하려면 의도에 따라 `> ANY`(최솟값보다 큼) 또는 `> ALL`(최댓값보다 큼)이나 `MIN`/`MAX` 서브쿼리로 바꿉니다.

Q. 서브쿼리의 조건 값을 잘못 적어(예: `'shelli'`) 0행이 되면 메인쿼리는 어떻게 되나요?
A. 서브쿼리 값이 NULL이 되어 비교가 참이 되지 않으므로, 오류 없이 결과가 0행으로 나옵니다.

Q. `department_id NOT IN (SELECT department_id FROM employees)`가 0행인 이유는?
A. 서브쿼리 결과에 NULL(부서 없는 직원)이 있어 `<> NULL`이 참이 될 수 없기 때문입니다. 서브쿼리에 `WHERE department_id IS NOT NULL`을 넣거나 `NOT EXISTS`로 씁니다.

Q. 부서별 최저 급여 직원을 `salary IN (SELECT MIN(salary) … GROUP BY department_id)`로 구하면 무엇이 틀리나요?
A. 다른 부서의 최솟값과 우연히 같은 급여도 걸려 행이 늘어납니다(12행 → 26행). `(department_id, salary) IN (…)`처럼 기준 컬럼과 짝으로 비교합니다.

Q. 직원과 직무 이력을 부서 번호로 먼저 JOIN한 뒤 `SUM(salary)`를 구하면 80번 부서 급여 합계가 609,000이 나옵니다. 원인과 해결 방법은?
A. 직원 34행이 그 부서의 직무 이력 2행과 각각 짝지어져 급여가 2번씩 더해졌기 때문입니다. 각 테이블을 인라인 뷰(또는 WITH)에서 먼저 부서별 1행으로 집계한 뒤 JOIN합니다.
:::
