---
label: 4. GROUP BY · HAVING
title: 그룹화·조건·집계
---

# 집계 함수 · GROUP BY · HAVING

:::goal
- 집계 함수(COUNT, SUM, AVG, MAX, MIN)로 여러 행을 하나의 값으로 만들 수 있습니다.
- COUNT의 세 가지 모양과, 집계 함수가 NULL을 빼고 계산한다는 점을 설명할 수 있습니다.
- GROUP BY로 「~별」 집계를 하고, 여러 컬럼·CASE 라벨로도 묶을 수 있습니다.
- WHERE(행 조건)와 HAVING(그룹 조건)을 구분해 쓸 수 있습니다.
:::

## 1. 집계 함수 — 여러 행을 하나의 값으로

### 1-1. 단일행 함수와 집계 함수 {keep}

| 구분 | 입력 행 | 결과 | 예 |
| --- | --- | --- | --- |
| 단일행 함수 | **1개** 행 | 행마다 결과 1개 | `ROUND(salary / 30, 0)` (반올림 — 1-2에서 씁니다) |
| **집계 함수** (다중행 함수) | **여러 개** 행 | 그룹마다 결과 **1개** | `COUNT`, `SUM`, `AVG`, `MAX`, `MIN` |

> 3단원에서 `WHERE`로 **행을 골랐다면**, 이번 단원은 고른 행을 **묶어서 세고, 더하고, 평균 내는** 방법입니다.
“부서별 직원 수는 몇 명인가?”, “직책별 평균 급여는 얼마인가?”, “급여 총액은 얼마인가?” 같은 질문이 모두 집계입니다.

### 1-1. 집계 함수 다섯 가지 {keep}

```icons 집계 함수 다섯 가지
hash | COUNT() | 개수 | rose
plus | SUM() | 합계 | plum
equal | AVG() | 평균 | lime
trending-up | MAX() | 최댓값 | ivory
minus | MIN() | 최솟값 | hot
```

### 1-2. 테이블 전체를 하나의 그룹으로 {keep}

> 실행 전: `SET search_path TO hr;` — 이 단원의 예제는 HR 실습 데이터(`hr_postgres.sql`의 `hr` 스키마)로 실행합니다.

집계 함수를 쓰면서 `GROUP BY`를 쓰지 않으면 **테이블 전체(또는 WHERE로 남은 행 전체)가 하나의 그룹**이 됩니다. <br>그래서 결과는 항상 **1행**입니다.

```sql
SELECT COUNT(*)    AS 직원수
     , SUM(salary) AS 급여합계
     , MAX(salary) AS 최고급여
     , MIN(salary) AS 최저급여
     , AVG(salary) AS 평균급여
  FROM employees
 WHERE department_id = 50;
```

```result
| 직원수 | 급여합계 | 최고급여 | 최저급여 | 평균급여 |
| --- | --- | --- | --- | --- |
| 45 | 156400.00 | 8200.00 | 2100.00 | 3475.5555555555555556 |
```

> 급여합계 ÷ 직원수(45)를 직접 계산하면 평균급여와 같습니다. 급여가 비어 있는(NULL) 직원이 없기 때문입니다. NULL이 섞이면 어떻게 되는지는 1-4에서 봅니다.

### 1-2. ROUND로 반올림 {keep}

`AVG`는 소수점 아래가 길게 나옵니다. **`ROUND(값, 자리수)`** 로 반올림합니다.

```sql
SELECT ROUND(AVG(salary), 1) AS 평균급여
  FROM employees
 WHERE department_id = 50;
```

```result
| 평균급여 |
| --- |
| 3475.6 |
```

### 1-2. 생각해 보기 — 숫자면 다 더해도 될까? {keep}

:::try 생각해 보기 — 숫자면 다 더해도 될까?
`SELECT SUM(department_id), AVG(department_id) FROM employees;`를 실행하면 `6700`, `63.2075…`가 나옵니다. 오류는 없지만, 부서 번호는 **이름표(코드)** 라서 더하거나 평균 낸 값에는 의미가 없습니다. 63.2번 부서는 없습니다.
SQL은 숫자의 뜻이나 단위를 검사해 주지 않습니다. ==합계·평균을 내기 전에 그 숫자가 더해서 의미가 있는 값인지(코드 번호는 아닌지, 단위·통화가 같은지) 먼저 확인==하세요. 생산 데이터에서 원화·달러 단가가 섞인 경우는 3-6 확인 문제에서 직접 봅니다.
:::


### 1-3. COUNT의 세 가지 모양 ⭐ {keep}

| 쓰는 법 | 세는 것 |
| --- | --- |
| `COUNT(*)` | **행** 개수 (NULL이 있어도 셈) |
| `COUNT(컬럼)` | 그 컬럼 값이 **NULL이 아닌** 행 개수 |
| `COUNT(DISTINCT 컬럼)` | NULL이 아닌 값의 **종류** 개수 |

### 1-3. COUNT 세 가지를 한 번에 {keep}

```sql
SELECT COUNT(*)                       AS 전체행
     , COUNT(commission_pct)          AS 커미션있음
     , COUNT(DISTINCT commission_pct) AS 커미션종류
     , COUNT(DISTINCT department_id)  AS 부서종류
  FROM employees;
```

```result
| 전체행 | 커미션있음 | 커미션종류 | 부서종류 |
| --- | --- | --- | --- |
| 107 | 35 | 7 | 11 |
```

- 직원 107명 중 커미션 비율이 있는 직원은 35명(3단원 5-1의 `IS NOT NULL` 35행), 커미션 비율의 종류는 0.10~0.40 **7종**입니다.
- `부서종류 = 11`은 3단원 2-4에서 `SELECT DISTINCT department_id`로 본 **12행**에서 `NULL`을 뺀 값입니다. `COUNT(DISTINCT …)`도 NULL은 세지 않습니다.

### 1-4. 집계 함수는 NULL을 빼고 계산합니다 ⭐ {keep}

3단원 3-3에서 본 급여 13000 이상 직원 6명 중 4명은 커미션 비율이 NULL입니다.

```sql
SELECT employee_id, first_name, commission_pct
  FROM employees
 WHERE salary >= 13000
 ORDER BY employee_id;
```

```result
| employee_id | first_name | commission_pct |
| --- | --- | --- |
| 100 | Steven | NULL |
| 101 | Neena | NULL |
| 102 | Lex | NULL |
| 145 | John | 0.40 |
| 146 | Karen | 0.30 |
| 201 | Michael | NULL |
```

### 1-4. AVG는 무엇으로 나눌까? {keep}

```sql
SELECT COUNT(*)                       AS 전체행
     , COUNT(commission_pct)          AS 커미션있음
     , SUM(commission_pct)            AS 합계
     , AVG(commission_pct)            AS 평균
     , SUM(commission_pct) / COUNT(*) AS 합계나누기전체
  FROM employees
 WHERE salary >= 13000;
```

```result
| 전체행 | 커미션있음 | 합계 | 평균 | 합계나누기전체 |
| --- | --- | --- | --- | --- |
| 6 | 2 | 0.70 | 0.35000000000000000000 | 0.11666666666666666667 |
```

- `AVG`는 **NULL이 아닌 2행**으로 나눕니다: 0.70 ÷ 2 = **0.35**
- `SUM / COUNT(*)`는 **6행**으로 나눕니다: 0.70 ÷ 6 = **0.1167**
- 어느 쪽이 맞는지는 질문에 달려 있습니다. ==“커미션을 받는 직원만의 평균”==이면 `AVG`, “커미션이 없는 직원을 0으로 보고 평균”이면 NULL을 0으로 바꿔 계산해야 합니다.

### 1-5. 집계 결과와 일반 컬럼은 함께 쓸 수 없습니다 {keep}

```sql
SELECT job_id, COUNT(*)
  FROM employees;
```

```result
ERROR:  column "employees.job_id" must appear in the GROUP BY clause or be used in an aggregate function
```

`COUNT(*)`는 테이블 전체에서 **1행**을 만들고, `job_id`는 **107행**이 있습니다.
행 개수가 맞지 않아 한 결과표에 담을 수 없습니다.
오류 메시지가 해결 방법도 알려 줍니다. → `job_id`를 **GROUP BY에 넣으라**는 뜻입니다.

### 1-6. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `part_sourcing`에서 원화(`currency = 'KRW'`) 소싱의 행 수, 단가 합계, 최고 단가, 최저 단가, 평균 단가를 구하세요. 별칭은 `src_cnt`, `price_sum`, `max_price`, `min_price`, `avg_price`이고, 평균은 소수 첫째 자리까지 반올림합니다.

**[응용]** 아래 쿼리는 협력사 `V1010`(한성고무)의 소싱 행을 집계합니다. 실행하고, 다섯 개의 숫자가 각각 무엇인지, 그리고 `평균`과 `합계나누기전체`가 왜 다른지 설명하세요.

```sql
SELECT COUNT(*)                 AS 전체행
     , COUNT(po_price)          AS 단가있음
     , SUM(po_price)            AS 합계
     , AVG(po_price)            AS 평균
     , SUM(po_price) / COUNT(*) AS 합계나누기전체
  FROM part_sourcing
 WHERE vendor_code = 'V1010';
```
:::

### 1-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
```sql
SELECT COUNT(*)                AS src_cnt
     , SUM(po_price)           AS price_sum
     , MAX(po_price)           AS max_price
     , MIN(po_price)           AS min_price
     , ROUND(AVG(po_price), 1) AS avg_price
  FROM part_sourcing
 WHERE currency = 'KRW';
```

```result
| src_cnt | price_sum | max_price | min_price | avg_price |
| --- | --- | --- | --- | --- |
| 45 | 389215.00 | 61000.00 | 0.00 | 8845.8 |
```

`WHERE`를 빼면 원화 45행과 달러 7행이 그냥 더해져 단가 합계가 `389342.90`이 됩니다. 오류는 없지만 원과 달러를 더한 숫자라 의미가 없습니다(1-2 생각해 보기).
:::

### 1-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
```result
| 전체행 | 단가있음 | 합계 | 평균 | 합계나누기전체 |
| --- | --- | --- | --- | --- |
| 5 | 4 | 14200.00 | 3550.0000000000000000 | 2840.0000000000000000 |
```

- `COUNT(*)` = 5: `V1010`의 소싱 행 전체
- `COUNT(po_price)` = 4: 단가가 비어 있는 `MFT43979901` 1행 제외(3단원 3-5 확인 문제에서 본 단가 NULL)
- `SUM` = 14200: NULL을 뺀 4행의 합
- `AVG` = 14200 ÷ **4** = 3550 (NULL이 아닌 행으로 나눔)
- `SUM / COUNT(*)` = 14200 ÷ **5** = 2840 (단가를 모르는 부품까지 넣어 나눔)
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 2. GROUP BY — 기준 컬럼으로 묶기

### 2-1. GROUP BY의 모양과 실행 순서 {keep}

```sql 쓰는 순서와 실행 순서(①~⑥)
SELECT   기준 컬럼, 집계 함수      -- ⑤
  FROM   테이블                    -- ①
 WHERE   행 조건                   -- ②
 GROUP BY 기준 컬럼                -- ③ 같은 값끼리 묶어 그룹마다 1행
 HAVING  그룹 조건                 -- ④ (3-1에서)
 ORDER BY 정렬                     -- ⑥
```

**GROUP BY를 쓰는 세 단계**

1. 질문에서 **“~별”** 을 찾습니다. → 그 컬럼이 `GROUP BY` 기준입니다. (“부서**별** 직원 수” → `GROUP BY department_id`)
2. 그룹마다 구할 값을 **집계 함수**로 씁니다. (“직원 **수**” → `COUNT(*)`)
3. `SELECT`에는 **GROUP BY 기준 컬럼**과 **집계 함수**만 씁니다.

:::teacher 강사 확인
- 위 세 단계는 기존 교안 「GROUP BY 프로세스」에 해당합니다.
:::

### 2-1. 실행 순서 따라가기 {keep}

```stepper
{
  "title": "직원별 직무 이력 건수 — 실제 실행 순서",
  "code": "SELECT employee_id, COUNT(*) AS hist_cnt\n  FROM job_history\n GROUP BY employee_id\n ORDER BY hist_cnt DESC, employee_id;",
  "steps": [
    {"line": 1, "note": "① FROM — job_history(직무 이력) 테이블 10행을 모두 가져옵니다. (이 쿼리에는 WHERE·HAVING이 없어 ②·④는 건너뜁니다.)",
     "cols": ["employee_id", "job_id", "start_date"],
     "rows": [["102","IT_PROG","2001-01-13"],["101","AC_ACCOUNT","1997-09-21"],["101","AC_MGR","2001-10-28"],["201","MK_REP","2004-02-17"],["114","ST_CLERK","2006-03-24"],["122","ST_CLERK","2007-01-01"],["200","AD_ASST","1995-09-17"],["176","SA_REP","2006-03-24"],["176","SA_MAN","2007-01-01"],["200","AC_ACCOUNT","2002-07-01"]]},
    {"line": 2, "note": "③ GROUP BY — employee_id가 같은 행끼리 모읍니다. 10행이 101·102·114·122·176·200·201 7개 그룹이 됩니다.",
     "cols": ["employee_id", "job_id", "start_date"],
     "rows": [["101","AC_ACCOUNT","1997-09-21"],["101","AC_MGR","2001-10-28"],["102","IT_PROG","2001-01-13"],["114","ST_CLERK","2006-03-24"],["122","ST_CLERK","2007-01-01"],["176","SA_REP","2006-03-24"],["176","SA_MAN","2007-01-01"],["200","AD_ASST","1995-09-17"],["200","AC_ACCOUNT","2002-07-01"],["201","MK_REP","2004-02-17"]], "hot": ["employee_id"]},
    {"line": 0, "note": "⑤ SELECT — 그룹마다 1행. 기준 컬럼 employee_id와 COUNT(*)만 남습니다. job_id는 그룹 안에 여러 개라 쓸 수 없습니다.",
     "cols": ["employee_id", "hist_cnt"],
     "rows": [["101",2],["102",1],["114",1],["122",1],["176",2],["200",2],["201",1]], "hot": ["hist_cnt"]},
    {"line": 3, "note": "⑥ ORDER BY — SELECT 다음이므로 별칭 hist_cnt로 정렬할 수 있습니다.",
     "cols": ["employee_id", "hist_cnt"],
     "rows": [["101",2],["176",2],["200",2],["102",1],["114",1],["122",1],["201",1]], "hot": ["hist_cnt"]}
  ]
}
```

### 2-2. 부서별 직원 수 {keep}

:::cols
```sql
SELECT department_id
     , COUNT(*) AS emp_cnt
  FROM employees
 GROUP BY department_id
 ORDER BY emp_cnt DESC, department_id;
```

```result 12행
| department_id | emp_cnt |
| --- | --- |
| 50 | 45 |
| 80 | 34 |
| 30 | 6 |
| 100 | 6 |
| 60 | 5 |
| 90 | 3 |
| 20 | 2 |
| 110 | 2 |
| 10 | 1 |
| 40 | 1 |
| 70 | 1 |
| NULL | 1 |
```
:::

- 107행 → 12개 그룹. 각 그룹이 **1행**이 됩니다.
- `ORDER BY`는 `SELECT` 다음에 실행되므로 **별칭 `emp_cnt`로 정렬**할 수 있습니다(3단원 3-1).
- 직원의 70% 이상이 50번(Shipping)과 80번(Sales) 두 부서에 있습니다. 맨 아래 `NULL` 그룹은 2-7에서 봅니다.

### 2-2. DISTINCT와 GROUP BY {keep}

> `GROUP BY department_id`에 집계 함수를 쓰지 않으면 `SELECT DISTINCT department_id`(3단원 2-4)와 같은 결과(12행)가 나옵니다.
**종류만** 볼 때는 `DISTINCT`, **종류별 개수·합계**까지 볼 때는 `GROUP BY`를 씁니다.

```compare DISTINCT와 GROUP BY
list | SELECT DISTINCT department_id || layers | SELECT department_id, COUNT(*) … GROUP BY department_id
shapes | 종류만 (12행) || hash | 종류별 개수 (12행 + emp_cnt)
```

### 2-3. 지역별 국가 수 {keep}

:::cols
```sql
SELECT region_id
     , COUNT(*) AS country_cnt
  FROM countries
 GROUP BY region_id
 ORDER BY region_id;
```

```result
| region_id | country_cnt |
| --- | --- |
| 1 | 8 |
| 2 | 5 |
| 3 | 6 |
| 4 | 6 |
```
:::

- 3단원 6-2에서 `CASE`로 지역 이름을 붙이고 「유럽 8 · 미주 5 · 아시아 6 · 중동·아프리카 6」이라고 셌던 숫자를 `GROUP BY` 한 번으로 얻었습니다.
- 25개 나라가 4개 지역에 나뉘어 있습니다.

:::teacher 강사 확인
- 지역 이름(1 Europe, 2 Americas, 3 Asia, 4 Middle East and Africa)은 `regions` 테이블에 있습니다. 이름과 함께 보려면 `regions`와 JOIN해야 하므로 Day 2로 넘기고, 여기서는 번호로만 보여 주세요.
:::

### 2-4. 직책별 직원 수 {keep}

:::cols
```sql
SELECT job_id
     , COUNT(*) AS emp_cnt
  FROM employees
 GROUP BY job_id
 ORDER BY emp_cnt DESC, job_id;
```

```result 앞 10행 (총 19행)
| job_id | emp_cnt |
| --- | --- |
| SA_REP | 30 |
| SH_CLERK | 20 |
| ST_CLERK | 20 |
| FI_ACCOUNT | 5 |
| IT_PROG | 5 |
| PU_CLERK | 5 |
| SA_MAN | 5 |
| ST_MAN | 5 |
| AD_VP | 2 |
| AC_ACCOUNT | 1 |
```
:::

- 1-5에서 오류가 났던 쿼리에 `GROUP BY job_id` 한 줄을 붙인 것입니다.
- 직책 이름(`job_title`)은 `jobs` 테이블에 있습니다. 코드와 이름을 함께 보려면 **JOIN**이 필요합니다.

### 2-5. 그룹마다 여러 집계 — 부서별 급여 {keep}

```sql
SELECT department_id
     , COUNT(*)              AS 직원수
     , SUM(salary)           AS 급여합계
     , ROUND(AVG(salary), 1) AS 평균급여
     , MAX(salary)           AS 최고
     , MIN(salary)           AS 최저
  FROM employees
 WHERE department_id IN (50, 80)
 GROUP BY department_id
 ORDER BY department_id;
```

```result
| department_id | 직원수 | 급여합계 | 평균급여 | 최고 | 최저 |
| --- | --- | --- | --- | --- | --- |
| 50 | 45 | 156400.00 | 3475.6 | 8200.00 | 2100.00 |
| 80 | 34 | 304500.00 | 8955.9 | 14000.00 | 6100.00 |
```

> 50번(Shipping)은 45명의 월 급여 합계가 156,400, 80번(Sales)은 34명이 304,500입니다. 직원은 50번이 더 많지만 급여 합계는 80번이 약 2배입니다.

### 2-6. 여러 컬럼으로 묶기 {keep}

`GROUP BY` 뒤에 컬럼이 여러 개면, 그 **조합**마다 그룹이 만들어집니다. (`DISTINCT` 여러 컬럼과 같은 원리)

:::cols
```sql
SELECT department_id
     , job_id
     , COUNT(*) AS emp_cnt
  FROM employees
 WHERE department_id IN (50, 80)
 GROUP BY department_id, job_id
 ORDER BY department_id, job_id;
```

```result
| department_id | job_id | emp_cnt |
| --- | --- | --- |
| 50 | SH_CLERK | 20 |
| 50 | ST_CLERK | 20 |
| 50 | ST_MAN | 5 |
| 80 | SA_MAN | 5 |
| 80 | SA_REP | 29 |
```
:::

- 2-5의 두 부서가 직책별로 나뉘었습니다. 50번 45명은 직책 3개, 80번 34명은 직책 2개입니다.
- `SA_REP`는 2-4에서 **30명**이었는데 여기서는 **29명**입니다. 부서가 NULL인 `SA_REP` 1명(178 Kimberely Grant)이 `WHERE department_id IN (50, 80)`에서 빠졌기 때문입니다.

### 2-7. NULL도 하나의 그룹이 됩니다 {keep}

:::cols
```sql
SELECT commission_pct
     , COUNT(*)              AS emp_cnt
     , COUNT(commission_pct) AS comm_cnt
  FROM employees
 GROUP BY commission_pct
 ORDER BY commission_pct;
```

```result
| commission_pct | emp_cnt | comm_cnt |
| --- | --- | --- |
| 0.10 | 6 | 6 |
| 0.15 | 5 | 5 |
| 0.20 | 7 | 7 |
| 0.25 | 6 | 6 |
| 0.30 | 7 | 7 |
| 0.35 | 3 | 3 |
| 0.40 | 1 | 1 |
| NULL | 72 | 0 |
```
:::

- `WHERE`에서는 `= NULL`로 비교가 안 됐지만(3단원 5-1), `GROUP BY`에서는 NULL끼리 **한 그룹**으로 묶입니다. 2-2의 부서 `NULL` 그룹(1명)도 같은 원리입니다.
- 같은 NULL 그룹인데 `COUNT(*)`는 72, `COUNT(commission_pct)`는 0입니다(1-3).
- NULL 그룹을 빼고 싶으면 그룹을 만들기 **전에** `WHERE commission_pct IS NOT NULL`로 행을 거릅니다.

### 2-8. CASE로 만든 라벨로 묶기 — 커미션 대상/미대상 {keep}

3단원 6-3에서 만든 커미션 대상/미대상 라벨로 묶습니다.

:::cols
```sql
SELECT CASE WHEN commission_pct IS NULL THEN '미대상' ELSE '대상' END AS 커미션
     , COUNT(*) AS 인원수
  FROM employees
 GROUP BY 커미션
 ORDER BY 인원수 DESC;
```

```result
| 커미션 | 인원수 |
| --- | --- |
| 미대상 | 72 |
| 대상 | 35 |
```
:::

> PostgreSQL은 `GROUP BY`에 **SELECT의 별칭**(`커미션`)을 쓸 수 있습니다.
별칭 대신 `GROUP BY CASE WHEN commission_pct IS NULL THEN '미대상' ELSE '대상' END`처럼 식을 그대로 써도 결과는 같습니다.

### 2-8. 비율을 한 줄로 {keep}

`CASE`로 1/0을 만들고 `SUM`으로 더하면 조건에 맞는 행 수가 됩니다.

```sql
SELECT COUNT(*) AS 전체
     , SUM(CASE WHEN commission_pct IS NOT NULL THEN 1 ELSE 0 END) AS 대상
     , ROUND(SUM(CASE WHEN commission_pct IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS 대상비율
     , ROUND(SUM(CASE WHEN commission_pct IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS 미대상비율
  FROM employees;
```

```result
| 전체 | 대상 | 대상비율 | 미대상비율 |
| --- | --- | --- | --- |
| 107 | 35 | 32.7 | 67.3 |
```

### 2-8. 비율이 32로 나온다면 {keep}

:::error 비율이 32로 나온다면 — 정수 ÷ 정수
`… * 100 / COUNT(*)`처럼 `100`(정수)을 쓰면 결과가 `32`(몫)만 나옵니다. 3단원 2-5에서 본 것처럼 ==`100.0`으로 소수를 섞어야== `32.7`이 나옵니다.

```sql
SELECT SUM(CASE WHEN commission_pct IS NOT NULL THEN 1 ELSE 0 END) * 100 / COUNT(*) AS ratio
  FROM employees;
```

```result
| ratio |
| --- |
| 32 |
```
:::

### 2-8. 직군별 인원 {keep}

3단원 6-1의 직군 라벨로도 묶을 수 있습니다.

:::cols
```sql
SELECT CASE WHEN job_id IN ('SA_MAN', 'SA_REP')               THEN '영업'
            WHEN job_id IN ('ST_MAN', 'ST_CLERK', 'SH_CLERK') THEN '물류'
            ELSE '사무'
       END AS job_group
     , COUNT(*) AS emp_cnt
  FROM employees
 GROUP BY job_group
 ORDER BY emp_cnt DESC;
```

```result
| job_group | emp_cnt |
| --- | --- |
| 물류 | 45 |
| 영업 | 35 |
| 사무 | 27 |
```
:::

### 2-9. GROUP BY를 쓸 때 주의할 점 {keep}

:::error SELECT에는 GROUP BY 기준 컬럼과 집계 함수만
`GROUP BY department_id`로 묶으면 그룹(부서)마다 **1행**만 남습니다. 그런데 `first_name`은 그룹 안에 값이 여러 개라 어느 것을 보여 줄지 정할 수 없습니다.

```sql
SELECT department_id, first_name, COUNT(*)
  FROM employees
 GROUP BY department_id;
```

```result
ERROR:  column "employees.first_name" must appear in the GROUP BY clause or be used in an aggregate function
```

==GROUP BY를 쓰는 순간 출력되는 행의 개수가 줄어들기 때문에== GROUP BY보다 늦게 실행되는 절(HAVING, SELECT, ORDER BY)에서는 쓸 수 있는 컬럼이 제한됩니다. 대신 **집계 함수로 처리한 컬럼은** 쓸 수 있습니다(`MAX(first_name)` 등).
:::

### 2-10. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `production_plan`(생산 계획)에서 라인(`line_code`)별 계획일수, 총계획수량, 일평균 계획수량, 최대·최소 계획수량을 구하세요. 별칭은 `plan_days`, `total_qty`, `avg_qty`, `max_qty`, `min_qty`이고, 일평균은 소수 첫째 자리까지 반올림하며, 라인 순으로 정렬합니다.

**[응용]** `part_master`의 UIT를 세 묶음으로 나눠 묶음별 부품 수(`part_cnt`)를 구하세요. UIT가 `T`·`P`·`S`·`M`·`R`이면 `Make`(사내에서 만드는 것), `G`·`D`·`X`면 `Buy`(사 오는 것), 그 밖은 `완제품`이고, 라벨 별칭은 `make_buy`입니다. 부품 수가 많은 순으로 정렬합니다.
:::

### 2-10. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
2행. LINE-A(세탁기)는 12월 평일 10일 동안 4,520대, LINE-B(냉장고)는 3,460대를 만들 계획입니다.

```sql
SELECT line_code
     , COUNT(*)                AS plan_days
     , SUM(plan_qty)           AS total_qty
     , ROUND(AVG(plan_qty), 1) AS avg_qty
     , MAX(plan_qty)           AS max_qty
     , MIN(plan_qty)           AS min_qty
  FROM production_plan
 GROUP BY line_code
 ORDER BY line_code;
```

```result
| line_code | plan_days | total_qty | avg_qty | max_qty | min_qty |
| --- | --- | --- | --- | --- | --- |
| LINE-A | 10 | 4520 | 452.0 | 480 | 420 |
| LINE-B | 10 | 3460 | 346.0 | 380 | 320 |
```
:::

### 2-10. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
3행. UIT별로 보면 7개 그룹(G 41 · P 8 · D 7 · T 6 · F 2 · S 2 · X 2)인 것을 세 가지 큰 구분으로 다시 묶었습니다.

```sql
SELECT CASE WHEN uit IN ('T', 'P', 'S', 'M', 'R') THEN 'Make'
            WHEN uit IN ('G', 'D', 'X')           THEN 'Buy'
            ELSE '완제품'
       END AS make_buy
     , COUNT(*) AS part_cnt
  FROM part_master
 GROUP BY make_buy
 ORDER BY part_cnt DESC;
```

```result
| make_buy | part_cnt |
| --- | --- |
| Buy | 50 |
| Make | 16 |
| 완제품 | 2 |
```
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 3. HAVING — 그룹을 고르는 조건

### 3-1. HAVING의 모양 {keep}

```sql 쓰는 순서와 실행 순서(①~⑥)
SELECT   기준 컬럼, 집계 함수      -- ⑤
  FROM   테이블                    -- ①
 WHERE   행 조건                   -- ② 묶기 전에 「행」을 거름
 GROUP BY 기준 컬럼                -- ③
 HAVING  집계 함수 조건            -- ④ 묶은 뒤에 「그룹」을 거름
 ORDER BY 정렬                     -- ⑥
```

### 3-1. 실행 순서 따라가기 {keep}

```stepper
{
  "title": "직무 이력이 2건 이상인 직원 — 실제 실행 순서",
  "code": "SELECT employee_id, COUNT(*) AS hist_cnt\n  FROM job_history\n GROUP BY employee_id\nHAVING COUNT(*) >= 2\n ORDER BY employee_id;",
  "steps": [
    {"line": 1, "note": "① FROM — job_history 테이블 10행을 모두 가져옵니다. (이 쿼리에는 WHERE가 없어 ②는 건너뜁니다.)",
     "cols": ["employee_id", "job_id", "start_date"],
     "rows": [["102","IT_PROG","2001-01-13"],["101","AC_ACCOUNT","1997-09-21"],["101","AC_MGR","2001-10-28"],["201","MK_REP","2004-02-17"],["114","ST_CLERK","2006-03-24"],["122","ST_CLERK","2007-01-01"],["200","AD_ASST","1995-09-17"],["176","SA_REP","2006-03-24"],["176","SA_MAN","2007-01-01"],["200","AC_ACCOUNT","2002-07-01"]]},
    {"line": 2, "note": "③ GROUP BY — employee_id별로 묶어 7개 그룹을 만듭니다. 그룹마다 COUNT(*)를 셀 수 있게 됩니다.",
     "cols": ["employee_id", "COUNT(*)"],
     "rows": [["101",2],["102",1],["114",1],["122",1],["176",2],["200",2],["201",1]], "hot": ["employee_id"]},
    {"line": 3, "note": "④ HAVING — 그룹 단위로 조건을 검사합니다. COUNT(*) >= 2가 아닌 4개 그룹이 탈락합니다.", "dim": [1,2,3,6], "hot": ["COUNT(*)"]},
    {"line": 0, "note": "⑤ SELECT — 남은 그룹에서 employee_id와 COUNT(*)를 꺼내고 별칭 hist_cnt를 붙입니다.",
     "cols": ["employee_id", "hist_cnt"],
     "rows": [["101",2],["176",2],["200",2]], "hot": ["hist_cnt"]},
    {"line": 4, "note": "⑥ ORDER BY — 마지막으로 employee_id 순으로 정렬합니다.",
     "cols": ["employee_id", "hist_cnt"],
     "rows": [["101",2],["176",2],["200",2]]}
  ]
}
```

### 3-1. 직원이 5명 이상인 직책 {keep}

**질문:** 직원이 **5명 이상**인 직책은?

:::cols
```sql
SELECT job_id
     , COUNT(*) AS emp_cnt
  FROM employees
 GROUP BY job_id
HAVING COUNT(*) >= 5
 ORDER BY emp_cnt DESC, job_id;
```

```result
| job_id | emp_cnt |
| --- | --- |
| SA_REP | 30 |
| SH_CLERK | 20 |
| ST_CLERK | 20 |
| FI_ACCOUNT | 5 |
| IT_PROG | 5 |
| PU_CLERK | 5 |
| SA_MAN | 5 |
| ST_MAN | 5 |
```
:::

- 2-4의 19개 그룹 중 조건에 맞는 **8개 그룹만** 남았습니다.

### 3-2. WHERE에는 집계 함수를 쓸 수 없습니다 ⭐ {keep}

```sql
SELECT job_id, COUNT(*)
  FROM employees
 WHERE COUNT(*) >= 5
 GROUP BY job_id;
```

```result
ERROR:  aggregate functions are not allowed in WHERE
```

`WHERE`(②)는 `GROUP BY`(③)보다 **먼저 실행**됩니다. `WHERE`를 실행하는 시점에는 아직 그룹이 없어서 `COUNT(*)`를 계산할 수 없습니다. ==그룹에 대한 조건은 HAVING==에 씁니다.

### 3-2. 왜 안 되는지 따라가기 {keep}

```stepper
{
  "title": "WHERE COUNT(*) — 어디서 막힐까?",
  "code": "SELECT employee_id, COUNT(*)\n  FROM job_history\n WHERE COUNT(*) >= 2\n GROUP BY employee_id;",
  "steps": [
    {"line": 1, "note": "① FROM — job_history 테이블 10행을 가져옵니다.",
     "cols": ["employee_id", "job_id", "start_date"],
     "rows": [["102","IT_PROG","2001-01-13"],["101","AC_ACCOUNT","1997-09-21"],["101","AC_MGR","2001-10-28"],["201","MK_REP","2004-02-17"],["114","ST_CLERK","2006-03-24"],["122","ST_CLERK","2007-01-01"],["200","AD_ASST","1995-09-17"],["176","SA_REP","2006-03-24"],["176","SA_MAN","2007-01-01"],["200","AC_ACCOUNT","2002-07-01"]]},
    {"line": 2, "note": "② WHERE — 행을 한 줄씩 검사하는 단계입니다. 아직 묶이지 않았으니 「몇 개인지」 셀 그룹이 없습니다. → ERROR: aggregate functions are not allowed in WHERE (실제로는 실행 전에 걸러집니다. 순서로 이해하기 위한 그림입니다.)", "hot": ["employee_id"]},
    {"line": 3, "note": "③ GROUP BY — 그룹은 여기서야 만들어집니다. 그래서 그룹 조건은 GROUP BY 다음의 HAVING에 써야 합니다.",
     "cols": ["employee_id", "COUNT(*)"],
     "rows": [["101",2],["102",1],["114",1],["122",1],["176",2],["200",2],["201",1]], "hot": ["COUNT(*)"]}
  ]
}
```

### 3-3. HAVING에서는 별칭을 못 씁니다 {keep}

```sql
SELECT job_id, COUNT(*) AS emp_cnt
  FROM employees
 GROUP BY job_id
HAVING emp_cnt >= 5;
```

```result
ERROR:  column "emp_cnt" does not exist
```

`HAVING`(④)은 `SELECT`(⑤)보다 먼저 실행되므로, 별칭 `emp_cnt`가 아직 없습니다. `HAVING COUNT(*) >= 5`처럼 집계 함수를 다시 씁니다. 반대로 `ORDER BY`(⑥)에서는 별칭을 쓸 수 있습니다.


### 3-3. 절마다 별칭을 쓸 수 있을까? {keep}

| 절 | 별칭 사용 | 이유 |
| --- | --- | --- |
| `WHERE` | ✕ | SELECT보다 먼저 실행 (3단원 2-6) |
| `GROUP BY` | ○ (PostgreSQL) | 출력 컬럼 이름을 허용 (2-8) |
| `HAVING` | ✕ | SELECT보다 먼저 실행 |
| `ORDER BY` | ○ | SELECT 다음에 실행 |

:::error GROUP BY에 별칭을 쓸 때 주의할 점
GROUP BY에 별칭을 쓰는 것은 PostgreSQL이 표준을 넓혀 준 기능입니다. SQL-92 표준에서 GROUP BY는 원래 테이블의 컬럼(입력 컬럼) 이름만 쓸 수 있습니다. GROUP BY도 SELECT보다 먼저 실행되지만, PostgreSQL이 SELECT 목록에서 별칭을 찾아 그 식으로 바꿔 줍니다. HAVING에는 이 기능이 없어서 별칭을 쓸 수 없습니다.
:::


### 3-4. WHERE와 HAVING을 함께 — 무엇이 달라질까? {keep}

**질문:** 부서별 평균 급여가 10,000 이상인 부서는?

:::cols
```sql HAVING만
SELECT department_id
     , COUNT(*)              AS emp_cnt
     , ROUND(AVG(salary), 0) AS avg_sal
  FROM employees
 GROUP BY department_id
HAVING AVG(salary) >= 10000
 ORDER BY avg_sal DESC;
```

```sql WHERE + HAVING
SELECT department_id
     , COUNT(*)              AS emp_cnt
     , ROUND(AVG(salary), 0) AS avg_sal
  FROM employees
 WHERE job_id NOT LIKE '%CLERK'
 GROUP BY department_id
HAVING AVG(salary) >= 10000
 ORDER BY avg_sal DESC;
```
:::

:::cols
```result HAVING만 (3행)
| department_id | emp_cnt | avg_sal |
| --- | --- | --- |
| 90 | 3 | 19333 |
| 110 | 2 | 10154 |
| 70 | 1 | 10000 |
```

```result WHERE + HAVING (4행)
| department_id | emp_cnt | avg_sal |
| --- | --- | --- |
| 90 | 3 | 19333 |
| 30 | 1 | 11000 |
| 110 | 2 | 10154 |
| 70 | 1 | 10000 |
```
:::

### 3-4. 30번 부서가 새로 나타난 이유 {keep}

- 오른쪽 쿼리는 사무보조(`…CLERK`) 직원을 뺀 뒤(`WHERE`, 3단원 5-4의 `NOT LIKE`) 묶었습니다.
- 30번(Purchasing) 부서 6명은 **부서장(`PU_MAN`) 1명 + 사무보조(`PU_CLERK`) 5명**입니다.
- `WHERE` 없이 묶으면 사무보조 급여가 섞여 평균이 4,150으로 낮아졌고, `WHERE`로 사무보조를 빼니 부서장 1명만 남아 평균이 11,000이 되었습니다.

| | WHERE | HAVING |
| --- | --- | --- |
| 거르는 대상 | **행** | **그룹** |
| 실행 시점 | GROUP BY **전** | GROUP BY **후** |
| 집계 함수 | 쓸 수 없음 | 씀 |
| 이 예제에서 | 사무보조 행을 뺌 | 평균 10,000 이상 부서만 남김 |

> ==WHERE는 일반 조건으로 행을 고르고, HAVING은 묶은 뒤 집계 함수 조건으로 그룹을 고릅니다.==

### 3-5. HAVING으로 데이터 점검하기 {keep}

`HAVING COUNT(*) >= 2`는 “**같은 값이 두 번 이상 나오는 것**”을 찾는 패턴입니다. 중복 의심, 여러 곳에 걸친 값 찾기에 자주 씁니다.

**① 이름이 같은 직원**

:::cols
```sql
SELECT first_name
     , COUNT(*) AS cnt
  FROM employees
 GROUP BY first_name
HAVING COUNT(*) >= 2
 ORDER BY first_name;
```

```result 앞 8행 (총 13행)
| first_name | cnt |
| --- | --- |
| Alexander | 2 |
| David | 3 |
| James | 2 |
| Jennifer | 2 |
| John | 3 |
| Julia | 2 |
| Karen | 2 |
| Kevin | 2 |
```
:::

> 이름이 같아도 **직원ID(PK)가 다르면 다른 사람**입니다. 예를 들어 「Peter」는 `144`(Vargas), `150`(Tucker), `152`(Hall) 세 명입니다. 이름만으로 직원을 찾으면 엉뚱한 사람의 기록을 가져올 수 있으므로, ==조회와 기록은 항상 직원ID로== 합니다.

### 3-5. ② 직책이 두 가지 이상인 부서 {keep}

부서마다 직원 수와 **직책 종류 수**를 함께 세고, 직책이 두 가지 이상인 부서만 남깁니다.

:::cols
```sql
SELECT department_id
     , COUNT(*)               AS emp_cnt
     , COUNT(DISTINCT job_id) AS job_cnt
  FROM employees
 GROUP BY department_id
HAVING COUNT(DISTINCT job_id) >= 2
 ORDER BY department_id;
```

```result 7행
| department_id | emp_cnt | job_cnt |
| --- | --- | --- |
| 20 | 2 | 2 |
| 30 | 6 | 2 |
| 50 | 45 | 3 |
| 80 | 34 | 2 |
| 90 | 3 | 2 |
| 100 | 6 | 2 |
| 110 | 2 | 2 |
```
:::

### 3-5. emp_cnt와 job_cnt 읽기 {keep}

- `emp_cnt`(`COUNT(*)`)는 **직원 수**, `job_cnt`(`COUNT(DISTINCT job_id)`)는 **직책 종류 수**입니다. HAVING은 직책 종류 수(`COUNT(DISTINCT job_id)`)로 걸렀기 때문에 직원이 2명뿐인 부서도 나오고, 직원이 5명인 60번(IT)은 빠집니다(모두 `IT_PROG`).
- `emp_cnt`와 `job_cnt`가 같으면 직원마다 직책이 다른 것입니다. 예를 들어 아래 두 부서가 그렇습니다.
  - 20번(Marketing): `MK_MAN` 1명 + `MK_REP` 1명
  - 110번(Accounting): `AC_MGR` 1명 + `AC_ACCOUNT` 1명
- `HAVING`에 쓰는 집계 함수는 `SELECT`에 꼭 출력하지 않아도 됩니다. 여기서는 읽기 쉽게 `job_cnt`로 함께 출력했습니다.
- 부서 이름(`department_name`)과 직책 이름(`job_title`)은 Day 2에서 `departments`·`jobs`와 ==JOIN해 함께 봅니다.==

### 3-6. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `part_sourcing`에서 업체(`vendor_code`)별 소싱 품목 수를 구하되, 품목 수가 **5개 이상**인 업체만 출력하세요. 별칭은 `item_cnt`이고, 품목 수가 많은 순(같으면 업체 순)으로 정렬합니다.

**[응용]** 업체별 소싱 품목 수(`item_cnt`)와 평균 단가(`avg_price`, 정수로 반올림)를 구해, 평균 단가가 **10,000 이상**인 업체만 평균 단가가 높은 순으로 출력하세요. ① 전체 소싱으로 한 번, ② **원화(KRW) 소싱만** 대상으로 한 번 실행하고, 조건을 더한 ②의 결과가 왜 **더 많은지** 설명하세요.
:::

### 3-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
6행

```sql
SELECT vendor_code
     , COUNT(*) AS item_cnt
  FROM part_sourcing
 GROUP BY vendor_code
HAVING COUNT(*) >= 5
 ORDER BY item_cnt DESC, vendor_code;
```

```result
| vendor_code | item_cnt |
| --- | --- |
| V1001 | 9 |
| V1011 | 8 |
| V1003 | 6 |
| V1006 | 6 |
| V1008 | 6 |
| V1010 | 5 |
```
:::

### 3-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
①(전체 소싱)은 **2행**(`V1003` 15151, `V1001` 12159), ②(원화만)는 **3행**입니다. ②는 ①에 `WHERE currency = 'KRW'` 한 줄을 더한 것입니다.

```sql
SELECT vendor_code
     , COUNT(*)                AS item_cnt
     , ROUND(AVG(po_price), 0) AS avg_price
  FROM part_sourcing
 WHERE currency = 'KRW'
 GROUP BY vendor_code
HAVING AVG(po_price) >= 10000
 ORDER BY avg_price DESC;
```

```result
| vendor_code | item_cnt | avg_price |
| --- | --- | --- |
| V1009 | 1 | 28000 |
| V1003 | 6 | 15151 |
| V1001 | 9 | 12159 |
```
:::

### 3-6. 확인 문제 답 — 응용 해설 {keep}

:::answer [응용] 해설
- 조건을 하나 더했는데 `V1009`(Pacific Motor Parts)가 새로 나타났습니다. `V1009`의 소싱 4행은 **달러 3행 + 원화 1행**입니다.
- ①은 달러 단가(작은 숫자)와 원화 단가를 섞어 평균을 내서 평균이 낮아졌고, 10,000을 넘지 못해 탈락했습니다.
- ②는 `WHERE`로 원화 행만 남긴 뒤 묶었으므로 `V1009`에는 원화 1행만 남아 평균이 28,000이 되었습니다.
- 「원화만」은 묶기 전에 판단할 수 있는 **행 조건**이라 `WHERE`, 「평균 10,000 이상」은 묶어야 알 수 있는 **그룹 조건**이라 `HAVING`에 씁니다. 통화가 섞인 채 평균을 내면 오류 없이 틀린 숫자가 나옵니다(1-2 생각해 보기).
:::

> 이어지는 4절 복습 문제도 `bom` 스키마로 풉니다.

## 4. 복습 문제

### 4-0. 복습 문제 안내 {keep}

> 범위: 집계 함수 · GROUP BY · HAVING · ORDER BY 전체. `bom` 스키마의 테이블로 풀어 주세요(실행 전: `SET search_path TO bom;`). (출력 순서는 `ORDER BY` 기준)

```icons 여덟 문항
layers | 1 · GROUP BY | 대분류별 부품 수 | rose
list-checks | 2 · HAVING | 2개 이상인 단위(UOM) | plum
truck | 3 · GROUP BY | 공급 방식별 BOM 행 수 | lime
clock | 4 · 여러 집계 | 구매 속성별 리드타임 | ivory
wallet | 5 · (심화) WHERE + HAVING | 원화 최소 발주 금액 | plum
calendar | 6 · (심화) 식으로 묶기 | 등록월별 부품 수 | hot
share-2 | 7 · HAVING + DISTINCT | 두 모델 공용 부품 | lime
copy | 8 · HAVING | 품명이 같은 부품 | rose
```

### 4-1. 복습 1 · 2 {keep}

**1.** `part_master`에서 대분류(`class_lv1`)별 부품 수(`part_cnt`)를 구하세요. 부품 수가 많은 순으로 정렬하고, 같으면 대분류 순으로 정렬합니다. [힌트: COUNT, GROUP BY]

```result 출력 결과 (총 7행)
| class_lv1 | part_cnt |
| --- | --- |
| M | 29 |
| E | 17 |
| A | 11 |
| R | 5 |
| F | 3 |
| T | 2 |
| S | 1 |
```

**2.** `part_master`에서 단위(`uom`)별 부품 수(`part_cnt`)를 구하되, 2개 이상인 단위만 출력하세요. 부품 수가 많은 순, 같으면 단위 순으로 정렬합니다. [힌트: HAVING]

```result 출력 결과 (총 4행)
| uom | part_cnt |
| --- | --- |
| EA | 60 |
| KG | 3 |
| SH | 2 |
| ST | 2 |
```

### 4-2. 복습 3 · 4 {keep}

**3.** `bom_structure`에서 공급 방식(`supply_type`)별 BOM 행 수(`line_cnt`)를 많은 순으로 출력하세요.

```result 출력 결과 (총 3행)
| supply_type | line_cnt |
| --- | --- |
| Assembly Pull | 61 |
| Supplier | 14 |
| Phantom | 7 |
```

**4.** `part_sourcing`에서 구매 속성(`line_type`)별 소싱 품목 수(`src_cnt`), 평균 리드타임(`avg_lt`, 소수 첫째 자리 반올림), 최대 리드타임(`max_lt`)을 구하고 평균 리드타임이 긴 순으로 정렬하세요. [힌트: ROUND(AVG(…), 1)]

```result 출력 결과 (총 4행)
| line_type | src_cnt | avg_lt | max_lt |
| --- | --- | --- | --- |
| I | 7 | 42.9 | 60 |
| S | 2 | 17.5 | 21 |
| D | 42 | 12.7 | 30 |
| N | 1 | 3.0 | 3 |
```

### 4-3. 복습 5 · 6 (심화) {keep}

**5.** (심화) `part_sourcing`에서 원화(KRW) 소싱만 대상으로, 업체별 품목 수(`item_cnt`)와 최소 발주 금액(단가 × MOQ)의 합계(`min_order_sum`)를 구하세요. 합계가 1,000,000 이상인 업체만, 합계가 큰 순으로 출력합니다. [힌트: WHERE + GROUP BY + HAVING, SUM(po_price * moq)]

```result 출력 결과 (총 3행)
| vendor_code | item_cnt | min_order_sum |
| --- | --- | --- |
| V1002 | 3 | 3335000.00 |
| V1001 | 9 | 1285900.00 |
| V1003 | 6 | 1178800.00 |
```

**6.** (심화) `part_master`에서 등록월(`created_at`의 연-월, 별칭 `reg_month`)별로 부품이 몇 개 등록되었는지 구하되, 7개 이상 등록된 달만 등록월 순으로 출력하세요. 단, 정확한 계산을 위해 `created_at`이 NULL인 행은 묶기 전에 제외하세요.

[힌트: (1) GROUP BY에는 컬럼뿐 아니라 가공한 식도 쓸 수 있습니다. 예: `GROUP BY TO_CHAR(created_at, 'YYYY-MM')` — `TO_CHAR(날짜, 'YYYY-MM')`은 날짜를 `2025-01` 같은 연-월 글자로 바꾸는 함수입니다. (2) SELECT에는 GROUP BY에 쓴 식(또는 그 별칭)과 집계 함수만 쓸 수 있습니다. (3) 현재 `created_at`이 NULL인 데이터는 없지만, WHERE로 먼저 제외하는 습관을 들입니다.]

```result 출력 결과 (총 3행)
| reg_month | part_cnt |
| --- | --- |
| 2025-01 | 8 |
| 2025-03 | 11 |
| 2025-12 | 7 |
```

### 4-4. 복습 7 · 8 (데이터 점검) {keep}

**7.** `bom_structure`에서 냉장고·세탁기 **두 모델에 모두** 쓰이는 하위 부품(`child_part_no`)을 찾으세요. BOM 행 수(`used_cnt`)와 쓰이는 모델 수(`model_cnt`)를 함께 출력하고, BOM 행 수가 많은 순(같으면 품번 순)으로 정렬합니다. [힌트: HAVING COUNT(DISTINCT model_part_no) = 2]

```result 출력 결과 (총 11행 중 앞 5행)
| child_part_no | used_cnt | model_cnt |
| --- | --- | --- |
| FSC67181101 | 3 | 2 |
| FTP68745401 | 3 | 2 |
| RRS44997401 | 3 | 2 |
| EAE71986301 | 2 | 2 |
| EIC93178801 | 2 | 2 |
```

**8.** `part_master`에서 한글 품명(`description_kr`)이 같은 부품이 2개 이상인 품명과 부품 수(`cnt`)를 품명 순으로 출력하세요.

```result 출력 결과 (총 8행 중 앞 4행)
| description_kr | cnt |
| --- | --- |
| 도어 가스켓 | 2 |
| 메인 PCB 조립체 | 2 |
| 와이어 하네스 | 2 |
| 완충재 | 2 |
```

### 4-5. 복습 1 · 2 답 {keep}

:::answer 복습 1 · 2 예시 답안
```sql 1
SELECT class_lv1, COUNT(*) AS part_cnt
  FROM part_master
 GROUP BY class_lv1
 ORDER BY part_cnt DESC, class_lv1;
```

```sql 2
SELECT uom, COUNT(*) AS part_cnt
  FROM part_master
 GROUP BY uom
HAVING COUNT(*) >= 2
 ORDER BY part_cnt DESC, uom;
```
:::

### 4-6. 복습 3 · 4 답 {keep}

:::answer 복습 3 · 4 예시 답안
```sql 3
SELECT supply_type, COUNT(*) AS line_cnt
  FROM bom_structure
 GROUP BY supply_type
 ORDER BY line_cnt DESC;
```

```sql 4
SELECT line_type
     , COUNT(*)                      AS src_cnt
     , ROUND(AVG(lead_time_days), 1) AS avg_lt
     , MAX(lead_time_days)           AS max_lt
  FROM part_sourcing
 GROUP BY line_type
 ORDER BY avg_lt DESC;
```

- 4번 결과의 의미: line_type `I`(Import, UIT D와 짝)의 평균 리드타임이 42.9일로 국내(`D`) 12.7일의 3배가 넘습니다. 3단원 4-6 확인 문제에서 본 「해외에서 오래 걸려 들어오는 부품」을 숫자로 확인한 것입니다.
:::

### 4-7. 복습 5 · 6 답 {keep}

:::answer 복습 5 · 6 예시 답안
```sql 5
SELECT vendor_code
     , COUNT(*)            AS item_cnt
     , SUM(po_price * moq) AS min_order_sum
  FROM part_sourcing
 WHERE currency = 'KRW'
 GROUP BY vendor_code
HAVING SUM(po_price * moq) >= 1000000
 ORDER BY min_order_sum DESC;
```

```sql 6
SELECT TO_CHAR(created_at, 'YYYY-MM') AS reg_month
     , COUNT(*)                       AS part_cnt
  FROM part_master
 WHERE created_at IS NOT NULL
 GROUP BY TO_CHAR(created_at, 'YYYY-MM')
HAVING COUNT(*) >= 7
 ORDER BY reg_month;
```

- 5번에서 `WHERE currency = 'KRW'`를 빼면 달러 금액이 원화와 섞여 합계가 틀어집니다(3-6 확인 문제 [응용]).
- 6번은 `GROUP BY reg_month`처럼 별칭으로 묶어도 PostgreSQL에서는 같은 결과가 나옵니다(2-8).
:::

:::teacher 강사 확인
- 6번은 기존 HR 복습 문제 「연도별 입사자 수」와 같은 유형입니다.
:::

### 4-8. 복습 7 · 8 답 {keep}

:::answer 복습 7 · 8 예시 답안
```sql 7
SELECT child_part_no
     , COUNT(*)                      AS used_cnt
     , COUNT(DISTINCT model_part_no) AS model_cnt
  FROM bom_structure
 GROUP BY child_part_no
HAVING COUNT(DISTINCT model_part_no) = 2
 ORDER BY used_cnt DESC, child_part_no;
```

```sql 8
SELECT description_kr, COUNT(*) AS cnt
  FROM part_master
 GROUP BY description_kr
HAVING COUNT(*) >= 2
 ORDER BY description_kr;
```

- 7번: `used_cnt`가 3이면 한 모델 안에서 **서로 다른 상위 조립품**에 두 번 쓰인 것입니다. 예: `FTP68745401`(필라멘트 테이프)은 냉장고의 냉동 사이클 조립체·포장 조립체 + 세탁기의 포장 조립체. 공용 부품은 재고가 부족하면 ==LINE-A·LINE-B 두 라인에 모두 영향==을 줍니다(Day 2 Where-Used에서 JOIN으로 확인).
- 8번: 이름이 같아도 **품번(PK)이 다르면 다른 부품**입니다. 「도어 가스켓」은 `MGK25528301`, `MGK31172901` 두 품번이므로 ==조회와 기록은 항상 품번으로== 합니다(3-5 ①과 같은 원리).
:::

## 5. 정리

### 5-1. 오늘 배운 것 {keep}

:::summary
- **집계 함수**: `COUNT`, `SUM`, `AVG`, `MAX`, `MIN` — 여러 행을 그룹마다 **1행**으로 만듭니다. `GROUP BY`가 없으면 전체가 한 그룹.
- **COUNT**: `COUNT(*)`는 행 수, `COUNT(컬럼)`은 NULL 제외, `COUNT(DISTINCT 컬럼)`은 종류 수.
- **NULL**: 집계 함수는 NULL을 빼고 계산합니다(`AVG` = NULL 아닌 행으로 나눔). `GROUP BY`에서는 NULL끼리 한 그룹.
- **GROUP BY**: 질문의 「~별」이 기준 컬럼. `SELECT`에는 **기준 컬럼 + 집계 함수만**. 여러 컬럼이면 조합마다 그룹. `CASE` 라벨로도 묶을 수 있습니다.
- **HAVING**: 묶은 뒤 **그룹**을 거르는 조건(집계 함수 사용). `WHERE`는 묶기 전에 **행**을 거르는 조건(집계 함수 불가).
- **별칭**: `WHERE`·`HAVING` ✕ / `GROUP BY`(PostgreSQL)·`ORDER BY` ○.
- **뜻·단위 주의**: 코드 번호를 더하거나, 통화·UOM이 섞인 상태로 `SUM`·`AVG`를 내면 오류 없이 틀린 숫자가 나옵니다.
:::

### 5-2. 확인 문제

:::quiz
Q. `SELECT job_id, COUNT(*) FROM employees;`가 오류가 나는 이유와 고치는 방법은?
A. `COUNT(*)`는 전체를 1행으로 만들고 `job_id`는 107행이라 함께 출력할 수 없습니다. `GROUP BY job_id`를 붙여 직책별로 묶습니다.

Q. 커미션 비율이 NULL인 행이 섞여 있을 때 `AVG(commission_pct)`와 `SUM(commission_pct) / COUNT(*)`가 다른 이유는?
A. `AVG`는 NULL이 아닌 행 수로 나누고, `COUNT(*)`는 NULL을 포함한 전체 행 수로 나누기 때문입니다. (급여 13000 이상 6명: 0.35 vs 0.1167)

Q. “직원이 5명 이상인 직책”을 구할 때 `WHERE COUNT(*) >= 5`가 안 되는 이유는?
A. `WHERE`는 `GROUP BY`보다 먼저 실행되어 그룹이 없는 상태라 집계 함수를 쓸 수 없습니다. `HAVING COUNT(*) >= 5`로 씁니다.

Q. `HAVING emp_cnt >= 5`(별칭)는 오류가 나는데 `ORDER BY emp_cnt`는 되는 이유는?
A. `HAVING`은 `SELECT`보다 먼저, `ORDER BY`는 `SELECT`보다 나중에 실행되기 때문입니다.

Q. 커미션 대상 비율을 `… * 100 / COUNT(*)`로 구했더니 32가 나왔습니다. 32.7을 얻으려면?
A. 정수 ÷ 정수라 몫만 남은 것입니다. `* 100.0`처럼 소수를 섞고 `ROUND(…, 1)`로 반올림합니다.
:::

