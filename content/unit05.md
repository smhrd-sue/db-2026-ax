---
label: 5. JOIN
title: 나뉘어 있는 데이터 잇기
---

# JOIN 기본 · INNER JOIN

:::goal
- 데이터가 여러 테이블에 나뉘어 있는 이유를 설명하고, 두 테이블의 조인 키(PK–FK)를 찾을 수 있습니다.
- 조인 조건을 빠뜨리면 CROSS JOIN(카티션 곱)이 된다는 것을 행 수로 확인할 수 있습니다.
- INNER JOIN … ON으로 두 개·세 개 테이블을 잇고, 테이블 별칭으로 컬럼을 구분할 수 있습니다.
:::


## 1. JOIN이란 — 나뉘어 저장된 데이터를 잇기

### 1-1. 데이터는 왜 나뉘어 있을까? {keep}

> 실행 전: `SET search_path TO hr;` — 이 단원의 예제는 HR 실습 데이터(`hr_postgres.sql`의 `hr` 스키마)로 실행합니다.

부서 20, 60, 90에 속한 직원 앞 5명을 봅니다.

:::cols
```sql
SELECT employee_id, first_name, last_name, job_id, department_id
  FROM employees
 WHERE department_id IN (20, 60, 90)
 ORDER BY employee_id
 LIMIT 5;
```

```result
| employee_id | first_name | last_name | job_id | department_id |
| --- | --- | --- | --- | --- |
| 100 | Steven | King | AD_PRES | 90 |
| 101 | Neena | Kochhar | AD_VP | 90 |
| 102 | Lex | De Haan | AD_VP | 90 |
| 103 | Alexander | Hunold | IT_PROG | 60 |
| 104 | Bruce | Ernst | IT_PROG | 60 |
```
:::

부서 번호 `90`이 **무슨 부서인지**, 그 부서가 어느 도시에 있는지는 이 표에 없습니다. 부서 이름은 `departments`에, 도시는 `locations`에 있습니다.

### 1-1. JOIN하면 한 표로 볼 수 있습니다 {keep}

같은 5행에 `departments`의 부서 이름과 `locations`의 도시를 이어 붙이면 다음과 같습니다. (쓰는 법은 2절에서 배웁니다.)

```sql
SELECT e.employee_id, e.first_name, e.department_id, d.department_name, l.city
  FROM employees e
 INNER JOIN departments d ON d.department_id = e.department_id
 INNER JOIN locations l   ON l.location_id = d.location_id
 WHERE e.department_id IN (20, 60, 90)
 ORDER BY e.employee_id LIMIT 5;
```

```result
| employee_id | first_name | department_id | department_name | city |
| --- | --- | --- | --- | --- |
| 100 | Steven | 90 | Executive | Seattle |
| 101 | Neena | 90 | Executive | Seattle |
| 102 | Lex | 90 | Executive | Seattle |
| 103 | Alexander | 60 | IT | Southlake |
| 104 | Bruce | 60 | IT | Southlake |
```

이제 「100번 Steven은 **Executive** 부서이고, **Seattle**에서 일한다」고 바로 읽을 수 있습니다. 세 테이블에 나뉘어 있던 정보가 한 행에 모였습니다.

### 1-1. 나뉜 테이블을 다시 잇는 작업 {keep}

> 1단원(데이터 모델링)에서 본 것처럼, 같은 정보를 여러 곳에 중복 저장하지 않으려고 테이블을 나눕니다. 그 대가로, 조회할 때는 **나뉜 테이블을 다시 이어 붙여야** 합니다. 이 작업이 **JOIN**입니다.
한 문장으로 정리하면: ==서로 다른 테이블에 나뉘어 저장된 관련 데이터를 연결하여 한 번에 결과로 확인하는 작업==.

JOIN을 모르면 「100번 직원의 부서 이름」 하나를 알기 위해서도 `employees`에서 부서 번호(90)를 찾고, `departments`에서 90번을 다시 찾는 식으로 **두 번 나눠** 조회해야 합니다.

### 1-2. 조인 키 찾기 — 같은 값을 가진 컬럼 {keep}

조인하려면 두 테이블에서 **같은 값을 담고 있는 컬럼**을 찾아야 합니다. 대부분 한쪽의 **PK**와 다른 쪽의 **FK**(`REFERENCES`)입니다. HR 데이터에서 가장 많이 잇는 테이블은 `employees`입니다.

```erd employees를 가운데 두고 뻗어 나가는 조인 키 — 선 위 글자가 FK 컬럼
departments (부서) @building-2 [*department_id (부서 번호), department_name (부서 이름), manager_id (부서장) (FK), location_id (근무지) (FK)] ; ||..o< department_id ; employees (직원) @users [*employee_id (직원 번호), first_name (이름), job_id (직무) (FK), manager_id (상사) (FK), department_id (부서) (FK)]
jobs (직무) @id-card [*job_id (직무 코드), job_title (직무 이름), min_salary · max_salary (급여 범위)] ; ||..o< job_id ; employees (직원) @users
employees (직원) @users ; ||--o< employee_id ; job_history (직무 이력) @history [*employee_id (직원 번호) (FK), *start_date (시작일), job_id (그때 직무) (FK), department_id (그때 부서) (FK)]
```

### 1-2. 부서에서 한 번 더 이어지는 키 {keep}

```erd employees를 거치지 않고 부서에서 바로 잇는 키 — 근무지 → 국가 → 대륙
departments (부서) @building-2 [*department_id (부서 번호), location_id (근무지) (FK)] ; >o..|| location_id ; locations (근무지) @building [*location_id (근무지 번호), city (도시), country_id (국가) (FK)] ; >o..|| country_id ; countries (국가) @map [*country_id (국가 코드), country_name (국가 이름), region_id (대륙) (FK)] ; >o..|| region_id ; regions (대륙) @globe [*region_id (대륙 번호), region_name (대륙 이름)]
```

### 1-2. 조인 키 한눈에 보기 {keep}

`hr_postgres.sql`의 DDL에서 이 단원에서 주로 쓰는 키를 표로 정리하면 다음과 같습니다.

| 이 테이블의 컬럼 (FK) | → 참조하는 테이블의 컬럼 (PK) | 이어 붙이면 알 수 있는 것 |
| --- | --- | --- |
| `employees.department_id` | `departments.department_id` | 직원이 속한 부서 이름 |
| `employees.job_id` | `jobs.job_id` | 직무 이름·급여 범위 |
| `employees.manager_id` | `employees.employee_id` | 상사의 이름 (같은 테이블, 5절) |
| `departments.manager_id` | `employees.employee_id` | 부서장의 이름 |
| `departments.location_id` | `locations.location_id` | 부서가 있는 도시 |
| `locations.country_id` | `countries.country_id` | 국가 이름 |
| `countries.region_id` | `regions.region_id` | 대륙 이름 |
| `job_history.employee_id` | `employees.employee_id` | 이력 주인의 이름 |
| `job_history.job_id` | `jobs.job_id` | 그때 맡았던 직무 이름 |

> `employees`에는 `location_id`가 없습니다. 직원이 일하는 도시를 알려면 `departments`를 거쳐 `locations`로 가야 합니다(2-5).

### 1-2. 이름이 달라도 값이 같으면 조인 키 {keep}

> 컬럼 **이름이 달라도** 같은 값을 담고 있으면 조인 키입니다. `departments.manager_id`와 `employees.employee_id`가 그 예입니다(둘 다 직원 번호). 반대로 이름이 같아도 의미가 다르면 조인 키가 아닙니다. `employees.manager_id`(직원의 상사)와 `departments.manager_id`(부서장)는 이름은 같지만 서로 잇는 키가 아닙니다. 정리하면 ==PK–FK 관계로 주로 조인이 이루어지지만, 다 그런 것은 아닙니다.==

### 1-3. 조인 조건이 없으면 — CROSS JOIN {keep}

조인 조건 없이 두 테이블을 이으면, 한쪽의 모든 행이 다른 쪽의 모든 행과 하나씩 짝지어집니다. 이것을 **CROSS JOIN**(카티션 곱)이라고 합니다.

```shot 조인 조건이 없으면 모든 행끼리 짝지어집니다
unit05/cross-join.svg
```

### 1-3. 직원 × 부서 = 2889행 {keep}

:::cols
```sql
SELECT COUNT(*)
  FROM employees CROSS JOIN departments;
```

```result
| count |
| --- |
| 2889 |
```
:::

직원 107행 × 부서 27행 = **2889행**. 각 직원이 **자기 부서가 아닌 부서들과도** 모두 짝지어진 결과라 의미가 없습니다.

### 1-3. 조인 조건을 빠뜨리면 {keep}

:::error 조인 조건을 빠뜨리면 — 오류 없이 행이 불어납니다
`FROM 테이블1, 테이블2`처럼 쉼표로 잇고 조인 조건을 빠뜨려도 **CROSS JOIN과 같은 결과**가 나옵니다. 오류가 나지 않으므로 더 위험합니다.

```sql
SELECT COUNT(*)
  FROM employees e, departments d
 WHERE e.department_id = 60;
```

```result
| count |
| --- |
| 135 |
```

60번 부서(IT) 직원은 5명인데, 부서 27개와 모두 짝지어져 5 × 27 = **135행**이 되었습니다. ==결과 행 수가 예상보다 크게 늘었다면 조인 조건부터 확인==하세요.
:::

## 2. INNER JOIN — 양쪽에 짝이 있는 행만

### 2-1. INNER JOIN의 모양 {keep}

:::cols
```shot INNER JOIN — 교집합
unit05/inner-join.svg
```

```sql 기본 모양
SELECT   별칭1.컬럼, 별칭2.컬럼
  FROM   테이블1 별칭1
 INNER JOIN 테이블2 별칭2
    ON   별칭1.조인키 = 별칭2.조인키  -- 조인 조건 (어떤 행끼리 짝지을지)
 WHERE   일반 조건                    -- 행 조건 (3단원과 같음)
 ORDER BY 정렬
```
:::

### 2-1. 조인 프로세스 {keep}

**조인 프로세스** (`JOIN … ON` 문법 기준)

1. 가져올 컬럼이 **어느 테이블에 있는지** 확인합니다. (1-2 표)
2. `FROM`에 기준 테이블을 쓰고, `JOIN` 뒤에 이을 테이블을 씁니다.
3. `ON`에 **두 테이블에서 같은 값을 가진 컬럼**으로 조인 조건을 씁니다.
4. `SELECT`에 출력할 컬럼을 **`별칭.컬럼`** 형태로 씁니다.

> `INNER`는 생략할 수 있습니다. `JOIN`만 쓰면 `INNER JOIN`입니다. 이 교안에서는 2절까지 `INNER JOIN`, 3절부터 `JOIN`으로 씁니다.

### 2-2. 직원 정보에 부서 이름 붙이기 {keep}

부서 번호가 30인 직원들에게 부서 이름을 붙여 봅니다. 부서 이름은 `employees`에 없고 `departments`에 있습니다.

```erd 직원 여러 명이 부서 하나를 가리킵니다 — ON e.department_id = d.department_id
employees e (직원) @users [*employee_id (직원 번호), first_name (이름), last_name (성), department_id (부서 번호) (FK)] ; >o..|| department_id ; departments d (부서) @building-2 [*department_id (부서 번호), department_name (부서 이름), location_id (근무지)]
```

- `e`의 `department_id`(FK)와 `d`의 `department_id`(PK)에 **같은 값**이 들어 있어서 조인 키가 됩니다.
- 이번에는 두 컬럼의 **이름도 같습니다**. 그래서 어느 쪽 `department_id`인지 `e.`·`d.`로 밝혀야 합니다(2-3).

### 2-2. 쿼리와 결과 {keep}

:::cols
```sql
SELECT e.employee_id
     , e.first_name
     , e.last_name
     , e.department_id
     , d.department_name
  FROM employees e
 INNER JOIN departments d
    ON e.department_id = d.department_id
 WHERE e.department_id = 30
 ORDER BY e.employee_id;
```

```result
| employee_id | first_name | last_name | department_id | department_name |
| --- | --- | --- | --- | --- |
| 114 | Den | Raphaely | 30 | Purchasing |
| 115 | Alexander | Khoo | 30 | Purchasing |
| 116 | Shelli | Baida | 30 | Purchasing |
| 117 | Sigal | Tobias | 30 | Purchasing |
| 118 | Guy | Himuro | 30 | Purchasing |
| 119 | Karen | Colmenares | 30 | Purchasing |
```
:::

- `e`, `d`는 **테이블 별칭**입니다(2-3).
- 조인 조건(`ON`)과 행 조건(`WHERE`)은 따로 씁니다. 조인 조건은 「어떤 행끼리 짝지을지」, 행 조건은 「짝지은 결과 중 무엇을 남길지」입니다.

### 2-3. 테이블 별칭 ① 같은 이름의 컬럼은 어느 테이블 것인지 밝히기 {keep}

```sql
SELECT department_id, department_name
  FROM employees e
 INNER JOIN departments d
    ON e.department_id = d.department_id
 LIMIT 1;
```

```error
ERROR:  column reference "department_id" is ambiguous
```

`department_id`는 `employees`에도 `departments`에도 있어서 어느 쪽인지 알 수 없다는 뜻입니다. `e.department_id`처럼 **별칭을 붙이면** 해결됩니다.
`department_name`처럼 한 테이블에만 있는 컬럼은 별칭 없이도 실행되지만, ==코드의 가독성을 위해 모든 컬럼 앞에 테이블 별칭(`e.`, `d.`)을 붙이는 것이 좋습니다.==

### 2-3. 테이블 별칭 ② 별칭을 지으면 원래 이름은 못 씁니다 {keep}

```sql
SELECT employees.employee_id
  FROM employees e
 LIMIT 1;
```

```error
ERROR:  invalid reference to FROM-clause entry for table "employees"
HINT:  Perhaps you meant to reference the table alias "e".
```

PostgreSQL이 「별칭 `e`를 쓰려던 것 아니냐」고 힌트까지 알려 줍니다. ==테이블에 별칭을 지었으면 이후 모든 절에서 별칭으로만== 부릅니다.

> 테이블 별칭은 `FROM employees AS e`처럼 `AS`를 붙여도 되고, 공백만 두어도 됩니다. 이 교안은 공백 방식으로 씁니다.

### 2-4. 쉼표 조인 — 다른 사람의 쿼리에서 보게 되는 모양 {keep}

`FROM`에 테이블을 쉼표로 나열하고, 조인 조건을 `WHERE`에 쓰는 방식도 있습니다. 2-2와 **결과가 같습니다**.

```sql
SELECT e.employee_id, e.first_name, e.last_name, e.department_id, d.department_name
  FROM employees e, departments d
 WHERE e.department_id = d.department_id   -- 조인 조건
   AND e.department_id = 30                -- 행 조건
 ORDER BY e.employee_id;
```

이 방식은 조인 조건과 행 조건이 `WHERE`에 섞여서, 조인 조건 하나를 빠뜨려도 알아채기 어렵습니다(1-3). 예전 Oracle 교재·코드에서 많이 보이는 모양이지만, 이 수업에서는 **`JOIN … ON`** 으로 작성합니다.

### 2-5. 세 개 테이블 잇기 — 직원의 부서와 근무 도시 {keep}

**질문:** 부서 20, 60, 90 직원의 이름을 부서 이름, **근무 도시**와 함께 보여 주세요.

필요한 컬럼이 어디에 있는지 먼저 찾습니다.

| 필요한 것 | 테이블 | 조인 키 |
| --- | --- | --- |
| 직원 번호, 이름, 부서 번호 | `employees` | — |
| 부서 이름, 근무지 번호 | `departments` | `e.department_id = d.department_id` |
| 근무 도시, 국가 코드 | `locations` | `d.location_id = l.location_id` |

### 2-5. 세 테이블이 이어지는 모양 {keep}

```erd ① 직원과 부서를 잇고 → ② 그 결과에 근무지를 잇습니다
employees e (직원) @users [*employee_id (직원 번호), first_name (이름), department_id (부서 번호) (FK)] ; >o..|| ① 부서 번호 ; departments d (부서) @building-2 [*department_id (부서 번호), department_name (부서 이름), location_id (근무지) (FK)] ; >o..|| ② 근무지 번호 ; locations l (근무지) @building [*location_id (근무지 번호), city (도시), country_id (국가)]
```

- ① `ON d.department_id = e.department_id` — 직원의 부서 번호로 부서를 찾습니다.
- ② `ON l.location_id = d.location_id` — 두 번째 조인은 `employees`가 아니라 **`departments`의 `location_id`** 를 거쳐 `locations`로 이어집니다. 직원 테이블에는 근무지 컬럼이 없기 때문입니다.

### 2-5. 1단계 — 직원에 부서 정보 붙이기 {keep}

:::cols
```sql
SELECT e.employee_id
     , e.first_name
     , e.department_id
     , d.department_name
     , d.location_id
  FROM employees e
 INNER JOIN departments d
    ON d.department_id = e.department_id
 WHERE e.department_id IN (20, 60, 90)
 ORDER BY e.employee_id;
```

```result
| employee_id | first_name | department_id | department_name | location_id |
| --- | --- | --- | --- | --- |
| 100 | Steven | 90 | Executive | 1700 |
| 101 | Neena | 90 | Executive | 1700 |
| 102 | Lex | 90 | Executive | 1700 |
| 103 | Alexander | 60 | IT | 1400 |
| 104 | Bruce | 60 | IT | 1400 |
| 105 | David | 60 | IT | 1400 |
| 106 | Valli | 60 | IT | 1400 |
| 107 | Diana | 60 | IT | 1400 |
| 201 | Michael | 20 | Marketing | 1800 |
| 202 | Pat | 20 | Marketing | 1800 |
```
:::

### 2-5. 2단계 — 근무지를 하나 더 잇기 {keep}

`JOIN … ON`을 한 번 더 이어 쓰면 됩니다. 두 번째 조인은 **첫 번째 조인 결과**(`e` + `d`)에 `locations`를 잇는 것입니다.

```sql
SELECT e.employee_id
     , e.first_name
     , e.department_id
     , d.department_name
     , d.location_id
     , l.city
     , l.country_id
  FROM employees e
 INNER JOIN departments d
    ON d.department_id = e.department_id
 INNER JOIN locations l
    ON l.location_id = d.location_id
 WHERE e.department_id IN (20, 60, 90)
 ORDER BY e.employee_id;
```

### 2-5. 2단계 실행 결과 {keep}

```result
| employee_id | first_name | department_id | department_name | location_id | city | country_id |
| --- | --- | --- | --- | --- | --- | --- |
| 100 | Steven | 90 | Executive | 1700 | Seattle | US |
| 101 | Neena | 90 | Executive | 1700 | Seattle | US |
| 102 | Lex | 90 | Executive | 1700 | Seattle | US |
| 103 | Alexander | 60 | IT | 1400 | Southlake | US |
| 104 | Bruce | 60 | IT | 1400 | Southlake | US |
| 105 | David | 60 | IT | 1400 | Southlake | US |
| 106 | Valli | 60 | IT | 1400 | Southlake | US |
| 107 | Diana | 60 | IT | 1400 | Southlake | US |
| 201 | Michael | 20 | Marketing | 1800 | Toronto | CA |
| 202 | Pat | 20 | Marketing | 1800 | Toronto | CA |
```

- 조인을 하나 더 해도 **행 수는 10행 그대로**입니다. 부서 하나에 근무지는 하나뿐이므로(`locations`의 PK) 행마다 짝이 정확히 하나씩(N:1) 붙기 때문입니다.
- 이제 「201번 Michael은 Marketing 부서이고, 캐나다(CA) Toronto에서 일한다」고 한 줄로 읽을 수 있습니다.

### 2-6. 확인 문제 준비 — 생산 데이터의 조인 키 {keep}

확인 문제는 생산 데이터(`bom` 스키마)로 풉니다. `schema_postgres.sql`의 DDL에서 자주 쓰는 키를 정리하면 다음과 같습니다.

| 이 테이블의 컬럼 (FK) | → 참조하는 테이블의 컬럼 (PK) | 이어 붙이면 알 수 있는 것 |
| --- | --- | --- |
| `bom_structure.child_part_no` | `part_master.part_no` | 자식 부품의 품명·UIT |
| `bom_structure.parent_part_no` | `part_master.part_no` | 부모(상위 조립품)의 품명 |
| `bom_structure.supply_type` | `code_supply_type.supply_type` | 공급 방식의 한글 의미 |
| `part_master.uit` | `code_uit.uit` | UIT의 한글 의미·Make/Buy 분류 |
| `part_master.status_code` | `code_status.status_code` | 상태 이름 |
| `part_sourcing.part_no` | `part_master.part_no` | 사 오는 부품의 품명 |
| `part_sourcing.vendor_code` | `vendor.vendor_code` | 업체 이름·국가 |
| `inventory.part_no` | `part_master.part_no` | 재고 부품의 품명 |
| `production_plan.model_part_no` | `part_master.part_no` | 계획 모델의 품명 |

> 표에는 없지만 `bom_structure.model_part_no`도 품번을 담고 있어 `part_master.part_no`와 이을 수 있습니다(모델의 품명).

### 2-6. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** `part_sourcing`과 `vendor`를 조인해, 업체 코드가 `V1010`인 소싱 행의 품번(`part_no`), 업체 코드, 업체명(`vendor_name`), 단가(`po_price`), 통화(`currency`)를 품번 순으로 출력하세요.

**[응용]** (Q1) 냉장고 세트(`TRF38316001`)의 1레벨 구성품을 품명, UIT, **UIT 한글 의미**(`meaning_kr`), 소요량과 함께 `bom_id` 순으로 출력하세요. 1레벨은 「모델 품번과 부모 품번이 모두 `TRF38316001`인 BOM 행」입니다.
(힌트: `bom_structure` → `part_master` → `code_uit`. UIT는 BOM이 아니라 `part_master`에 있습니다.)
:::

### 2-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
5행

```sql
SELECT s.part_no
     , s.vendor_code
     , v.vendor_name
     , s.po_price
     , s.currency
  FROM part_sourcing s
 INNER JOIN vendor v
    ON s.vendor_code = v.vendor_code
 WHERE s.vendor_code = 'V1010'
 ORDER BY s.part_no;
```

```result
| part_no | vendor_code | vendor_name | po_price | currency |
| --- | --- | --- | --- | --- |
| MFT20558801 | V1010 | 한성고무(주) | 1100.00 | KRW |
| MFT43979901 | V1010 | 한성고무(주) | NULL | KRW |
| MGK25528301 | V1010 | 한성고무(주) | 4300.00 | KRW |
| MGK31172901 | V1010 | 한성고무(주) | 6900.00 | KRW |
| MHS18920401 | V1010 | 한성고무(주) | 1900.00 | KRW |
```

`vendor_code`는 두 테이블에 모두 있으므로 `s.`·`v.`를 꼭 붙입니다(2-3).
:::

### 2-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
12행. `code_uit`는 BOM이 아니라 **`part_master`의 `uit`** 를 거쳐 이어집니다(2-5의 `locations`와 같은 모양).

```sql
SELECT b.bom_id
     , p.part_no
     , p.description_kr
     , p.uit
     , u.meaning_kr
     , b.qty_per
  FROM bom_structure b
 INNER JOIN part_master p
    ON p.part_no = b.child_part_no
 INNER JOIN code_uit u
    ON u.uit = p.uit
 WHERE b.model_part_no  = 'TRF38316001'
   AND b.parent_part_no = 'TRF38316001'
 ORDER BY b.bom_id;
```

```result 총 12행 — 앞 6행
| bom_id | part_no | description_kr | uit | meaning_kr | qty_per |
| --- | --- | --- | --- | --- | --- |
| 1 | ACB22943901 | 캐비닛 조립체 | T | 사내 조립품, 계획·표준시간·재고 관리 | 1.000 |
| 2 | ADR24872401 | 냉장실 도어 조립체 | P | 사내 중간 조립품, 재고 관리 없음(팬텀) | 2.000 |
| 3 | ACC12625601 | 냉동 사이클 조립체 | T | 사내 조립품, 계획·표준시간·재고 관리 | 1.000 |
| 4 | EBA56264701 | 메인 PCB 조립체 | G | 국내 구매품 | 1.000 |
| 5 | EFN66589301 | 팬 모터 | D | 수입 구매품 | 1.000 |
| 6 | MSH53664101 | 선반 | G | 국내 구매품 | 4.000 |
```
:::

:::teacher 강사 확인
- `bom_level = 1` 조건으로 찾으면 냉장고는 **13행**이 나옵니다. 13행 중 1행(`bom_id` 26)은 부모가 모델이 아니라 `AHD26818801`(핸들 조립체)입니다. 이 행은 README 4장 이상 데이터 **A6** 위치이기도 합니다. Q1 정답(`exercises_mysql.sql`)은 `parent_part_no = model_part_no` 조건을 쓰므로 교안도 그 기준을 따랐습니다. `bom_level` 값 자체가 맞는지는 README에 설명이 없으므로, 질문이 나오면 「1레벨은 부모가 모델인 행」으로만 안내하세요.
- 나머지 6행: 선반 다음으로 정수 필터(G), 와이어 하네스(G), 포장 조립체(P), 나사 M4x12(G, 소요량 24), 사용설명서(X), 메인 펌웨어(X)입니다.
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

# OUTER JOIN · 안티 조인

:::goal
- LEFT JOIN으로 짝이 없는 행까지 남기고, 짝이 없는 쪽 컬럼이 NULL로 채워지는 것을 설명할 수 있습니다.
- 안티 조인(LEFT JOIN + IS NULL)과 NOT EXISTS로 「짝이 없는 행」을 찾을 수 있습니다.
- LEFT JOIN에서 조건을 ON에 쓸 때와 WHERE에 쓸 때의 차이를 설명할 수 있습니다.
:::

## 3. OUTER JOIN — 짝이 없는 행까지

### 3-1. INNER JOIN은 짝이 없는 행을 버립니다 {keep}

:::cols
```sql
SELECT COUNT(*)
  FROM employees e
  JOIN departments d
    ON d.department_id = e.department_id;
```

```result
| count |
| --- |
| 106 |
```
:::

직원은 107명인데 결과는 **106행**입니다. 부서 번호가 **NULL**인 직원 1명(4단원 2-2의 NULL 그룹)은 `NULL = 부서 번호`가 참이 될 수 없어(3단원) 짝이 없고, 결과에서 빠졌습니다. 「어떤 직원이 부서가 없는가?」를 알려면 빠진 쪽을 남기는 조인이 필요합니다.

### 3-2. LEFT JOIN — 왼쪽 테이블의 행은 모두 남기기 {keep}

:::cols
```shot LEFT JOIN — 교집합 + 왼쪽
unit05/left-join.svg
```

```sql 기본 모양
SELECT ...
  FROM 기준테이블 a          -- 왼쪽: 모든 행을 남김
  LEFT JOIN 이을테이블 b     -- 오른쪽: 짝이 없으면 NULL로 채움
    ON a.키 = b.키
```
:::

### 3-2. 107행이 모두 남습니다 {keep}

:::cols
```sql
SELECT COUNT(*)
  FROM employees e
  LEFT JOIN departments d
    ON d.department_id = e.department_id;
```

```result
| count |
| --- |
| 107 |
```
:::

107행이 모두 남았습니다. 짝이 없는 1행은 `departments` 쪽 컬럼이 모두 **NULL**로 채워집니다.

| 조인 | 남는 행 |
| --- | --- |
| `INNER JOIN` | 양쪽에 짝이 **있는** 행만 |
| `LEFT [OUTER] JOIN` | **왼쪽** 테이블의 모든 행 + 오른쪽은 짝이 있으면 값, 없으면 NULL |
| `RIGHT [OUTER] JOIN` | **오른쪽** 테이블의 모든 행 (3-7) |
| `FULL [OUTER] JOIN` | **양쪽** 테이블의 모든 행 (3-7) |

> `OUTER`는 생략할 수 있습니다. `LEFT OUTER JOIN`과 `LEFT JOIN`은 같습니다.

### 3-3. 안티 조인 — 짝이 없는 행만 골라내기 ⭐ {keep}

LEFT JOIN 결과에서 **오른쪽 컬럼이 NULL인 행**만 남기면 「짝이 없는 행」이 됩니다. 이 패턴을 **안티 조인**이라고 부릅니다.

**① 직원이 한 명도 없는 부서**

```sql
SELECT d.department_id
     , d.department_name
     , d.manager_id
     , d.location_id
     , e.employee_id
  FROM departments d
  LEFT JOIN employees e
    ON e.department_id = d.department_id
 WHERE e.employee_id IS NULL
 ORDER BY d.department_id;
```

### 3-3. ① 실행 결과와 해석 {keep}

:::cols
```result 16행
| department_id | department_name | manager_id | location_id | employee_id |
| --- | --- | --- | --- | --- |
| 120 | Treasury | NULL | 1700 | NULL |
| 130 | Corporate Tax | NULL | 1700 | NULL |
| 140 | Control And Credit | NULL | 1700 | NULL |
| 150 | Shareholder Services | NULL | 1700 | NULL |
| 160 | Benefits | NULL | 1700 | NULL |
| 170 | Manufacturing | NULL | 1700 | NULL |
| 180 | Construction | NULL | 1700 | NULL |
| 190 | Contracting | NULL | 1700 | NULL |
| 200 | Operations | NULL | 1700 | NULL |
| 210 | IT Support | NULL | 1700 | NULL |
| 220 | NOC | NULL | 1700 | NULL |
| 230 | IT Helpdesk | NULL | 1700 | NULL |
| 240 | Government Sales | NULL | 1700 | NULL |
| 250 | Retail Sales | NULL | 1700 | NULL |
| 260 | Recruiting | NULL | 1700 | NULL |
| 270 | Payroll | NULL | 1700 | NULL |
```

- **결과를 해석하는 것까지가 진단**입니다. 16개 부서는 모두 부서장(`manager_id`)이 없고 근무지가 1700(Seattle)입니다. 부서만 만들어 두고 아직 사람을 배치하지 않은 부서로 읽을 수 있습니다.
- 반대로 **부서장이 있는데 이 목록에 나왔다면** 「부서장은 정해졌는데 소속 직원이 0명」이므로 확인해 볼 데이터입니다. 이 데이터에서는 한 건도 없습니다.
:::

### 3-3. IS NULL은 어느 컬럼으로? {keep}

:::error IS NULL은 오른쪽 테이블의 「NULL이 될 수 없는 컬럼」으로
`WHERE e.employee_id IS NULL`의 `e.employee_id`는 `employees`의 PK라, 짝이 지어진 행에서는 NULL일 수 없습니다. 그래서 NULL이면 「짝이 없어서 채운 NULL」이라고 확신할 수 있습니다.
`WHERE e.manager_id IS NULL`로 쓰면 **짝은 있지만 상사 번호가 비어 있는 직원**(100번 Steven King)이 있는 90번 Executive 부서까지 섞여 17행이 나옵니다. ==「짝이 없다」와 「값이 비었다」를 구분==하세요.
:::

### 3-3. ② 부서가 배정되지 않은 직원 {keep}

:::cols
```sql
SELECT e.employee_id
     , e.first_name
     , e.last_name
     , e.job_id
     , e.department_id
  FROM employees e
  LEFT JOIN departments d
    ON d.department_id = e.department_id
 WHERE d.department_id IS NULL;
```

```result 1행
| employee_id | first_name | last_name | job_id | department_id |
| --- | --- | --- | --- | --- |
| 178 | Kimberely | Grant | SA_REP | NULL |
```
:::

- 3-1에서 빠졌던 **1명**입니다. 영업 사원(`SA_REP`)인데 부서 번호가 비어 있습니다.
- 이번에는 왼쪽 테이블이 `employees`이므로, `IS NULL`은 오른쪽 `departments`의 PK에 겁니다. 안티 조인은 부서 번호가 비어 있는 직원뿐 아니라 `departments`에 **없는 번호**를 가진 직원까지 찾아 줍니다(이 데이터에는 FK가 있어 그런 직원은 없습니다).

### 3-3. ③ 맡은 직원이 없는 직무 {keep}

:::cols
```sql
SELECT j.job_id
     , j.job_title
  FROM jobs j
  LEFT JOIN employees e
    ON e.job_id = j.job_id
 WHERE e.employee_id IS NULL;
```

```result 0행
| job_id | job_title |
| --- | --- |
```
:::

직무 19개는 모두 맡은 직원이 있습니다.

> 결과가 0행이라는 것도 **진단 결과**입니다. 「점검했고, 문제없음」을 쿼리로 증명한 것입니다.

:::teacher 강사 확인
- 예전 Oracle 교안(`reference/7. JOIN.sql`)에는 「직원 108명, 부서 NULL 직원 2명(207, 178)」으로 적혀 있지만, 이 수업의 HR 데이터는 **107명**이고 부서가 NULL인 직원은 **178번 1명**뿐입니다. 숫자는 실행 결과를 기준으로 안내하세요.
:::

### 3-4. NOT EXISTS — 같은 질문을 다른 모양으로 {keep}

안티 조인은 `NOT EXISTS`로도 씁니다. 「부서 테이블에 이 직원의 부서 번호를 가진 행이 **존재하지 않는** 직원」이라는 뜻입니다.

:::cols
```sql
SELECT e.employee_id
     , e.first_name
     , e.last_name
     , e.department_id
  FROM employees e
 WHERE NOT EXISTS (SELECT 1
                     FROM departments d
                    WHERE d.department_id = e.department_id);
```

```result 1행
| employee_id | first_name | last_name | department_id |
| --- | --- | --- | --- |
| 178 | Kimberely | Grant | NULL |
```
:::

3-3 ②와 같은 1행입니다. 괄호 안의 쿼리(서브쿼리)는 Day 3 1교시에서 자세히 다룹니다. 여기서는 ==「LEFT JOIN + IS NULL」과 「NOT EXISTS」가 같은 질문==이라는 것만 기억하세요.

### 3-5. 부서 기준 LEFT JOIN + COUNT — 0도 보여 주기 {keep}

4단원 2-2처럼 `employees`만 `department_id`로 묶어 세면 직원이 있는 부서 11개(와 NULL 그룹)만 나옵니다. 부서 테이블(`departments`)을 **왼쪽**에 두고 LEFT JOIN하면 **직원이 없는 부서까지** 0으로 볼 수 있습니다.

```sql
SELECT d.department_id
     , d.department_name
     , COUNT(e.employee_id) AS emp_cnt
     , COUNT(*)             AS star_cnt
  FROM departments d
  LEFT JOIN employees e
    ON e.department_id = d.department_id
 GROUP BY d.department_id, d.department_name
 ORDER BY emp_cnt DESC, d.department_id;
```

### 3-5. 실행 결과 — COUNT(*)가 1인 부서 {keep}

```result 총 27행 (일부)
| department_id | department_name | emp_cnt | star_cnt |
| --- | --- | --- | --- |
| 50 | Shipping | 45 | 45 |
| 80 | Sales | 34 | 34 |
| … | … | … | … |
| 40 | Human Resources | 1 | 1 |
| 70 | Public Relations | 1 | 1 |
| 120 | Treasury | 0 | 1 |
| 130 | Corporate Tax | 0 | 1 |
| … | … | … | … |
| 270 | Payroll | 0 | 1 |
```

:::error LEFT JOIN 뒤에는 COUNT(*) 대신 COUNT(오른쪽 컬럼)
직원이 없는 16개 부서(120 Treasury ~ 270 Payroll)는 직원이 하나도 없는데 `COUNT(*)`는 **1**입니다. LEFT JOIN이 짝 없는 부서에도 NULL로 채운 **1행**을 만들었고, `COUNT(*)`는 그 행까지 세기 때문입니다(4단원 1-3).
==LEFT JOIN 결과를 셀 때는 `COUNT(오른쪽 테이블의 PK)`== 로 셉니다.
:::

### 3-6. ON에 쓸까, WHERE에 쓸까 ⭐ {keep}

**질문:** 부서별로 **급여가 10000 이상인 직원 수**를 구하되, 그런 직원이 없는 부서도 0으로 보여 주세요.

:::cols
```sql A. 급여 조건을 ON에
SELECT d.department_id
     , d.department_name
     , COUNT(e.employee_id) AS high_cnt
  FROM departments d
  LEFT JOIN employees e
    ON e.department_id = d.department_id
   AND e.salary       >= 10000
 GROUP BY d.department_id, d.department_name
 ORDER BY d.department_id;
```

```sql B. 급여 조건을 WHERE에
SELECT d.department_id
     , d.department_name
     , COUNT(e.employee_id) AS high_cnt
  FROM departments d
  LEFT JOIN employees e
    ON e.department_id = d.department_id
 WHERE e.salary >= 10000
 GROUP BY d.department_id, d.department_name
 ORDER BY d.department_id;
```
:::

### 3-6. 결과 비교 — 27행 vs 7행 {keep}

:::cols
```result A. ON에 (총 27행) — 앞 10행
| department_id | department_name | high_cnt |
| --- | --- | --- |
| 10 | Administration | 0 |
| 20 | Marketing | 1 |
| 30 | Purchasing | 1 |
| 40 | Human Resources | 0 |
| 50 | Shipping | 0 |
| 60 | IT | 0 |
| 70 | Public Relations | 1 |
| 80 | Sales | 11 |
| 90 | Executive | 3 |
| 100 | Finance | 1 |
```

```result B. WHERE에 (총 7행)
| department_id | department_name | high_cnt |
| --- | --- | --- |
| 20 | Marketing | 1 |
| 30 | Purchasing | 1 |
| 70 | Public Relations | 1 |
| 80 | Sales | 11 |
| 90 | Executive | 3 |
| 100 | Finance | 1 |
| 110 | Accounting | 1 |
```
:::

### 3-6. ON과 WHERE의 차이 {keep}

| | 조건을 `ON`에 | 조건을 `WHERE`에 |
| --- | --- | --- |
| 실행 시점 | 짝을 **지을 때** 적용 | 짝을 다 지은 **뒤에** 적용 |
| 고액 연봉자가 없는 부서 | 조건에 맞는 짝이 없어 NULL로 채워 **남음** → 0 | 짝지어진 1만 미만 직원 행이 모두 걸러져 부서가 **사라짐** (직원이 아예 없는 부서였다면 `e.salary`가 NULL이라 역시 탈락) |
| 결과 | 27행 | 7행 (INNER JOIN과 같아짐) |

> ==LEFT JOIN에서 오른쪽 테이블 조건을 WHERE에 쓰면, LEFT JOIN이 INNER JOIN처럼 동작합니다.== 「짝이 없는 행도 남기고 싶다」면 오른쪽 테이블의 조건은 `ON`에 씁니다. 왼쪽 테이블의 조건(예: `d.location_id = 1700`)은 `WHERE`에 써도 됩니다.

### 3-7. RIGHT JOIN {keep}

:::cols
```shot RIGHT JOIN — 교집합 + 오른쪽
unit05/right-join.svg
```

```sql
SELECT COUNT(*)
  FROM departments d
 RIGHT JOIN employees e
    ON d.department_id = e.department_id;
```
:::

**RIGHT JOIN**은 LEFT JOIN과 방향만 반대입니다. 위 쿼리는 3-2(`employees LEFT JOIN departments`)와 같은 **107행**입니다.

> 테이블 순서만 바꾸면 RIGHT JOIN은 언제나 LEFT JOIN으로 바꿔 쓸 수 있습니다. 읽기 쉽도록 ==기준 테이블을 왼쪽(FROM)에 두고 LEFT JOIN으로 통일==하는 것을 권합니다.

### 3-7. FULL JOIN {keep}

**FULL JOIN**은 짝이 있는 행에 더해, 왼쪽·오른쪽 어느 쪽이든 짝이 없는 행까지 모두 남깁니다. 「부서가 없는 직원」과 「직원이 없는 부서」를 한 번에 봅니다.

:::cols
```shot FULL JOIN — 양쪽 모두
unit05/full-join.svg
```

```sql
SELECT e.employee_id, e.first_name
     , d.department_id, d.department_name
  FROM employees e
  FULL JOIN departments d
    ON d.department_id = e.department_id
 WHERE e.employee_id IS NULL
    OR d.department_id IS NULL
 ORDER BY e.employee_id, d.department_id;
```
:::

### 3-7. FULL JOIN 실행 결과 {keep}

```result 총 17행
| employee_id | first_name | department_id | department_name |
| --- | --- | --- | --- |
| 178 | Kimberely | NULL | NULL |
| NULL | NULL | 120 | Treasury |
| NULL | NULL | 130 | Corporate Tax |
| … | … | … | … |
| NULL | NULL | 270 | Payroll |
```

- 부서가 없는 직원 1명(3-3 ②)과 직원이 없는 부서 16개(3-3 ①)가 한 결과에 모였습니다.
- `WHERE` 없이 세면 짝이 있는 106행 + 1 + 16 = **123행**입니다.

### 3-8. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** **소싱 정보가 없는** 부품(`part_sourcing`에 행이 없는 `part_master`의 부품)의 품번, 한글 품명, UIT를 UIT 순, 같으면 품번 순으로 출력하세요. 결과에 **사 오는 부품**(UIT G·D)이 있는지도 확인합니다.

**[응용]** 업체(`vendor`)별로 **달러(USD) 소싱 건수**(`usd_cnt`)를 구하되, 달러 소싱이 없는 업체도 0으로 업체 코드 순으로 출력하세요. 통화 조건을 `WHERE`에 쓰면 몇 행이 나오는지도 확인합니다.
(힌트: 3-6. 오른쪽 테이블의 조건은 어디에 써야 할까요?)
:::

### 3-8. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
16행. 모두 완제품(F), 사내 조립품(P·T), 관리용(X)이고 **사 오는 부품(G·D)은 없습니다.** 사 오지 않으니 소싱 정보가 없는 것이 자연스럽습니다.

```sql
SELECT p.part_no
     , p.description_kr
     , p.uit
  FROM part_master p
  LEFT JOIN part_sourcing s
    ON s.part_no = p.part_no
 WHERE s.part_no IS NULL
 ORDER BY p.uit, p.part_no;
```

```result 총 16행 — 앞 5행과 마지막 2행
| part_no | description_kr | uit |
| --- | --- | --- |
| TRF38316001 | 냉장고 세트 | F |
| TWM61868701 | 세탁기 세트 | F |
| ACP85953101 | 컨트롤 패널 조립체 | P |
| ADR24872401 | 냉장실 도어 조립체 | P |
| ADR69737101 | 도어 조립체 | P |
| … | … | … |
| ATB35230801 | 터브 조립체 | T |
| SAA76541601 | 메인 펌웨어 | X |
```

`WHERE s.po_price IS NULL`로 쓰면 소싱 행은 있지만 단가가 비어 있는 `MFT43979901`(2-6 복습)까지 섞입니다. `IS NULL`은 조인 키 `s.part_no`에 겁니다(3-3).
:::

### 3-8. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
12행. 통화 조건은 오른쪽 테이블(`part_sourcing`) 조건이므로 `ON`에 씁니다.

```sql
SELECT v.vendor_code
     , v.vendor_name
     , COUNT(s.part_no) AS usd_cnt
  FROM vendor v
  LEFT JOIN part_sourcing s
    ON s.vendor_code = v.vendor_code
   AND s.currency    = 'USD'
 GROUP BY v.vendor_code, v.vendor_name
 ORDER BY v.vendor_code;
```

```result
| vendor_code | vendor_name | usd_cnt |
| --- | --- | --- |
| V1001 | 한빛정밀(주) | 0 |
| V1002 | 대양화학(주) | 0 |
| V1003 | 세진전자(주) | 0 |
| V1004 | AsiaComp Co., Ltd. | 1 |
| V1005 | NanoChip Semiconductor | 1 |
| V1006 | 우성사출(주) | 0 |
| V1007 | Global Steel Trading | 2 |
| V1008 | 동아포장(주) | 0 |
| V1009 | Pacific Motor Parts | 3 |
| V1010 | 한성고무(주) | 0 |
| V1011 | 태양전장(주) | 0 |
| V1012 | LG 사내 부품라인(C1) | 0 |
```

`AND s.currency = 'USD'`를 `WHERE s.currency = 'USD'`로 옮기면 달러 소싱이 있는 **4행**(V1004·V1005·V1007·V1009)만 남습니다.
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

# 다중 조인 + 집계 · 셀프 조인

:::goal
- 여러 테이블을 조인한 결과를 GROUP BY로 묶어 이름·분류별로 집계할 수 있습니다.
- 1:N 조인으로 행이 늘어나는 경우를 COUNT(*)로 확인하고, 집계할 때 주의할 점을 설명할 수 있습니다.
- 같은 테이블에 다른 별칭을 붙여 역할별로 두 번 조인하고, 셀프 조인(직원–상사)을 할 수 있습니다.
:::

## 4. 여러 테이블 조인 + 집계

### 4-1. 조인한 뒤 묶기 — 부서 이름별 직원 수 {keep}

`employees`만으로는 부서 **번호**별로만 셀 수 있었습니다(4단원 2-2). `departments`를 조인하면 부서 이름까지 함께 볼 수 있습니다.

:::cols
```sql
SELECT d.department_id
     , d.department_name
     , COUNT(*) AS emp_cnt
  FROM employees e
  JOIN departments d
    ON e.department_id = d.department_id
 GROUP BY d.department_id, d.department_name
 ORDER BY emp_cnt DESC, d.department_id;
```

```result
| department_id | department_name | emp_cnt |
| --- | --- | --- |
| 50 | Shipping | 45 |
| 80 | Sales | 34 |
| 30 | Purchasing | 6 |
| 100 | Finance | 6 |
| 60 | IT | 5 |
| 90 | Executive | 3 |
| 20 | Marketing | 2 |
| 110 | Accounting | 2 |
| 10 | Administration | 1 |
| 40 | Human Resources | 1 |
| 70 | Public Relations | 1 |
```
:::

- 실행 순서는 4단원과 같습니다. ==FROM·JOIN으로 먼저 큰 표를 만들고 → WHERE → GROUP BY== 순서로 진행됩니다.
- `SELECT`에 `d.department_name`을 쓰려면 `GROUP BY`에도 넣어야 합니다(4단원 2-9).

### 4-2. 대륙별·국가별 직원 수 — 다섯 테이블 조인 {keep}

**질문:** 직원이 일하는 곳을 대륙·국가별로 묶어 직원 수를 세어 주세요.

:::cols
```sql
SELECT r.region_name
     , c.country_name
     , COUNT(*) AS emp_cnt
  FROM employees e
  JOIN departments d
    ON d.department_id = e.department_id
  JOIN locations l
    ON l.location_id = d.location_id
  JOIN countries c
    ON c.country_id = l.country_id
  JOIN regions r
    ON r.region_id = c.region_id
 GROUP BY r.region_name, c.country_name
 ORDER BY r.region_name, c.country_name;
```

```result
| region_name | country_name | emp_cnt |
| --- | --- | --- |
| Americas | Canada | 2 |
| Americas | United States of America | 68 |
| Europe | Germany | 1 |
| Europe | United Kingdom | 35 |
```
:::

- 대륙 이름(`region_name`)은 `regions`에만 있습니다. 직원에서 대륙까지 가려면 부서 → 근무지 → 국가 → 대륙으로 **네 번** 건너갑니다(1-2).
- 합계는 2 + 68 + 1 + 35 = **106명**입니다. 부서가 없는 178번이 첫 번째 INNER JOIN에서 빠졌기 때문입니다(3-1).

### 4-2. 부서 수를 세려면 COUNT(DISTINCT) {keep}

대륙 단위로 묶어 `COUNT(*)`와 `COUNT(DISTINCT d.department_id)`를 비교해 봅니다.

:::cols
```sql
SELECT r.region_name
     , COUNT(*)                        AS emp_cnt
     , COUNT(DISTINCT d.department_id) AS dept_cnt
  FROM employees e
  JOIN departments d
    ON d.department_id = e.department_id
  JOIN locations l
    ON l.location_id = d.location_id
  JOIN countries c
    ON c.country_id = l.country_id
  JOIN regions r
    ON r.region_id = c.region_id
 GROUP BY r.region_name
 ORDER BY r.region_name;
```

```result
| region_name | emp_cnt | dept_cnt |
| --- | --- | --- |
| Americas | 70 | 8 |
| Europe | 36 | 3 |
```
:::

> 조인 결과는 **직원 한 명당 한 행**입니다. 그래서 `COUNT(*)`는 직원 수가 되고, 부서 수를 세려면 `COUNT(DISTINCT d.department_id)`로 중복을 빼야 합니다. 참고로 이 다섯 테이블 조인(+ `jobs`)은 HR 데이터에 뷰 `emp_details_view`로 저장되어 있어, 이 뷰를 `region_name`으로 묶어 세도 70·36이 나옵니다.

### 4-2. 같은 부서가 여러 행에 나옵니다 {keep}

같은 부서에 직원이 여러 명이면 조인 결과에도 그 부서가 **직원 수만큼** 반복해서 나옵니다. 행 수(`emp_cnt`)와 부서 수(`dept_cnt`)가 다른 이유입니다.

:::cols
```sql
SELECT r.region_name
     , d.department_name
     , COUNT(*) AS emp_cnt
  FROM employees e
  JOIN departments d
    ON d.department_id = e.department_id
  JOIN locations l
    ON l.location_id = d.location_id
  JOIN countries c
    ON c.country_id = l.country_id
  JOIN regions r
    ON r.region_id = c.region_id
 GROUP BY r.region_name, d.department_name
 ORDER BY r.region_name, emp_cnt DESC;
```

```result
| region_name | department_name | emp_cnt |
| --- | --- | --- |
| Americas | Shipping | 45 |
| Americas | Finance | 6 |
| Americas | Purchasing | 6 |
| Americas | IT | 5 |
| Americas | Executive | 3 |
| Americas | Accounting | 2 |
| Americas | Marketing | 2 |
| Americas | Administration | 1 |
| Europe | Sales | 34 |
| Europe | Human Resources | 1 |
| Europe | Public Relations | 1 |
```
:::

### 4-3. 조인하면 행이 늘어날 수 있습니다 {keep}

짝이 1:1이 아니라 **1:N**이면, 조인 결과는 N쪽 행 수만큼 늘어납니다.

:::cols
```sql
SELECT COUNT(*)
  FROM jobs j
  JOIN employees e
    ON e.job_id = j.job_id;
```

```result
| count |
| --- |
| 107 |
```
:::

- 직무(`jobs`)는 19행입니다. 직무 1행마다 그 직무를 맡은 직원(`SA_REP` 30명, `SH_CLERK` 20명, `ST_CLERK` 20명 …)이 모두 붙어 **107행**이 되었습니다.
- 이것은 오류가 아니라 의도한 결과입니다. 「직원마다 직무 이름을 붙인 목록」이 필요할 때 바로 이 결과를 씁니다. (생산 데이터의 같은 상황은 복습 문제 7번)

### 4-3. 늘어난 행에 SUM을 하면 {keep}

:::error 늘어난 행에 SUM을 하면
1:N 조인 뒤 **1쪽 테이블의 숫자**를 `SUM`하면 같은 값이 N번 더해집니다. 예를 들어 위 결과에서 `SUM(j.max_salary)`를 구하면 직무별 최고 급여가 그 직무의 직원 수만큼(`SA_REP`는 30번) 반복해서 더해집니다.
==집계하기 전에 「이 조인으로 행이 몇 배가 되었나」를 COUNT(*)로 먼저 확인==하세요.
:::

### 4-4. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** 업체 **이름**별 소싱 품목 수(`item_cnt`)와 평균 리드타임(`avg_lt`, 소수 첫째 자리까지 반올림)을 구하되, 소싱 품목이 5개 이상인 업체만 품목 수가 많은 순, 같으면 업체 이름 순으로 출력하세요.

**[응용]** (Q2) 모델별로 구성품을 UIT 분류(`code_uit.classification`, Make item / Buy item)와 UIT별로 묶어 **부품 종류 수**(`parts`)를 세어 주세요. 모델 품번, 분류, UIT 순으로 정렬합니다.
`COUNT(*)`로 세면 어느 행의 숫자가 달라지나요? 왜일까요?
:::

### 4-4. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
6행

```sql
SELECT v.vendor_name
     , COUNT(*)                        AS item_cnt
     , ROUND(AVG(s.lead_time_days), 1) AS avg_lt
  FROM part_sourcing s
  JOIN vendor v
    ON v.vendor_code = s.vendor_code
 GROUP BY v.vendor_name
HAVING COUNT(*) >= 5
 ORDER BY item_cnt DESC, v.vendor_name;
```

```result
| vendor_name | item_cnt | avg_lt |
| --- | --- | --- |
| 한빛정밀(주) | 9 | 14.0 |
| 태양전장(주) | 8 | 14.0 |
| 동아포장(주) | 6 | 7.0 |
| 세진전자(주) | 6 | 15.2 |
| 우성사출(주) | 6 | 14.0 |
| 한성고무(주) | 5 | 10.8 |
```
:::

### 4-4. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
12행

```sql
SELECT b.model_part_no
     , u.classification
     , p.uit
     , COUNT(DISTINCT p.part_no) AS parts
  FROM bom_structure b
  JOIN part_master p
    ON p.part_no = b.child_part_no
  JOIN code_uit u
    ON u.uit = p.uit
 GROUP BY b.model_part_no, u.classification, p.uit
 ORDER BY b.model_part_no, u.classification, p.uit;
```

```result 총 12행 — 앞 6행
| model_part_no | classification | uit | parts |
| --- | --- | --- | --- |
| TRF38316001 | Buy item | D | 3 |
| TRF38316001 | Buy item | G | 24 |
| TRF38316001 | Buy item | X | 2 |
| TRF38316001 | Make item | P | 4 |
| TRF38316001 | Make item | S | 1 |
| TRF38316001 | Make item | T | 2 |
```

- 세탁기(`TWM61868701`)는 D 5 · G 25 · X 2 · P 4 · S 1 · T 4입니다. 관리용(X)도 코드표에서는 Buy item입니다.
- `COUNT(*)`로 세면 두 모델의 **G 행만 27**로 달라집니다. 같은 부품(냉장고는 나사 M4x12 등 3종이 2번씩, 세탁기는 나사 M5x16이 3번)이 한 모델 안에서 여러 상위 조립품 아래 반복해서 쓰여 BOM 행이 여러 개이기 때문입니다(4-2와 같은 원리).
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 5. 셀프 조인 — 같은 테이블을 두 번

### 5-1. 같은 테이블을 두 번 쓰기 — 이전 직무와 현재 직무 {keep}

`job_history`의 한 행에는 직원이 **예전에 맡았던 직무**(`h.job_id`)가 있고, `employees`에는 **지금 맡은 직무**(`e.job_id`)가 있습니다. 둘 다 `jobs.job_id`를 가리킵니다. 그래서 `jobs`를 **역할이 다른 두 개의 테이블처럼** 조인합니다. 테이블을 자기 자신과 잇는 셀프 조인은 5-2부터이고, 여기서는 그 준비로 같은 테이블을 역할별 별칭으로 두 번 조인합니다.

```sql
SELECT h.employee_id
     , e.first_name
     , oj.job_title AS old_title
     , cj.job_title AS cur_title
  FROM job_history h
  JOIN employees e
    ON e.employee_id = h.employee_id
  JOIN jobs oj                              -- 예전 직무용 jobs
    ON oj.job_id = h.job_id
  JOIN jobs cj                              -- 현재 직무용 jobs
    ON cj.job_id = e.job_id
 ORDER BY h.employee_id, h.start_date;
```

### 5-1. 실행 결과 {keep}

```result
| employee_id | first_name | old_title | cur_title |
| --- | --- | --- | --- |
| 101 | Neena | Public Accountant | Administration Vice President |
| 101 | Neena | Accounting Manager | Administration Vice President |
| 102 | Lex | Programmer | Administration Vice President |
| 114 | Den | Stock Clerk | Purchasing Manager |
| 122 | Payam | Stock Clerk | Stock Manager |
| 176 | Jonathon | Sales Representative | Sales Representative |
| 176 | Jonathon | Sales Manager | Sales Representative |
| 200 | Jennifer | Administration Assistant | Administration Assistant |
| 200 | Jennifer | Public Accountant | Administration Assistant |
| 201 | Michael | Marketing Representative | Marketing Manager |
```

> ==같은 테이블을 두 번 쓰는 것이기 때문에 반드시 테이블에 별칭을 사용해야 합니다.== 별칭이 없으면 `jobs.job_title`이 예전 직무인지 현재 직무인지 구분할 수 없습니다.

### 5-2. employees 셀프 조인 — 직원과 상사 {keep}

`employees.manager_id`는 **같은 테이블**의 `employee_id`를 가리킵니다(`hr_postgres.sql`의 `emp_manager_fk`). 상사도 직원이기 때문입니다. 그래서 `employees` **자기 자신**을 조인하면 직원과 상사를 한 행에 놓을 수 있습니다. 첫 번째 행의 `manager_id`가 두 번째 행의 `employee_id`와 같으면 이어집니다.

```screen 두 직원 행이 이어지는 모양
a (직원) :  101 Neena   manager_id = 100 ─┐
b (상사) :  100 Steven  employee_id = 100 ◀┘
            조인 조건: a.manager_id = b.employee_id
```

### 5-2. 직원과 상사를 한 행에 {keep}

**질문:** 부서 90 직원의 이름과 **상사 이름**은?

:::cols
```sql
SELECT a.employee_id
     , a.first_name
     , a.salary
     , a.manager_id
     , b.first_name AS manager_name
  FROM employees a
  JOIN employees b
    ON a.manager_id = b.employee_id
 WHERE a.department_id = 90
 ORDER BY a.employee_id;
```

```result
| employee_id | first_name | salary | manager_id | manager_name |
| --- | --- | --- | --- | --- |
| 101 | Neena | 17000.00 | 100 | Steven |
| 102 | Lex | 17000.00 | 100 | Steven |
```
:::

### 5-2. 결과 읽기 {keep}

- `a`는 **직원** 역할, `b`는 **상사** 역할입니다.
- 부서 90에는 직원이 3명(100·101·102)인데 2명만 나왔습니다. 100번 Steven King은 상사가 없어(`manager_id` NULL) 짝이 없기 때문입니다. 셀프 조인이어도 짝이 없는 행을 남기려면 3절과 똑같이 `LEFT JOIN`을 씁니다.

:::cols
```sql
SELECT a.employee_id
     , a.first_name
     , a.manager_id
     , b.first_name AS manager_name
  FROM employees a
  LEFT JOIN employees b
    ON a.manager_id = b.employee_id
 WHERE a.department_id = 90
 ORDER BY a.employee_id;
```

```result
| employee_id | first_name | manager_id | manager_name |
| --- | --- | --- | --- |
| 100 | Steven | NULL | NULL |
| 101 | Neena | 100 | Steven |
| 102 | Lex | 100 | Steven |
```
:::

### 5-3. 셀프 조인 + 집계 — 부하 직원을 둔 직원 {keep}

**질문:** 101번 Neena의 직속 부하 중 **자기 아래에 부하 직원을 둔** 사람과 그 부하 수는?

:::cols
```sql
SELECT a.employee_id
     , a.first_name
     , a.last_name
     , COUNT(*) AS sub_cnt
  FROM employees a                -- Neena의 직속 부하
  JOIN employees b                -- 그 사람의 부하
    ON b.manager_id = a.employee_id
 WHERE a.manager_id = 101
 GROUP BY a.employee_id, a.first_name, a.last_name
 ORDER BY a.employee_id;
```

```result
| employee_id | first_name | last_name | sub_cnt |
| --- | --- | --- | --- |
| 108 | Nancy | Greenberg | 5 |
| 205 | Shelley | Higgins | 1 |
```
:::

### 5-3. 결과 읽기 {keep}

- Neena의 직속 부하는 5명(108·200·203·204·205)인데 2명만 나왔습니다. 나머지 3명은 아래에 부하가 없어 `b`에 짝이 없으므로 INNER JOIN에서 빠졌습니다.
- `a`는 「Neena의 직속 부하」, `b`는 「그 사람의 부하」 역할입니다. 같은 테이블이지만 조인 조건(`b.manager_id = a.employee_id`)이 두 행을 한 단계 위아래로 잇습니다.

> 셀프 조인 한 번으로 조직도를 **한 단계** 내려갔습니다. 사장(100)부터 맨 아래 직원까지 내려가려면 셀프 조인을 계속 반복해야 하고, 단계 수를 모르면 몇 번 해야 할지 정할 수 없습니다. 이 문제를 푸는 방법이 Day 3의 **재귀 CTE**입니다.

### 5-4. 확인 문제 — 생산 데이터 {keep}

> 실행 전: `SET search_path TO bom;` (생산 실습 데이터 `bom` 스키마)

:::try
**[복습]** 냉장고 세트(`TRF38316001`) BOM에서 부모 품번이 `ACB22943901`(캐비닛 조립체)인 행의 `bom_id`, 부모 품번, **부모 품명**(`parent_name`), 자식 품번, **자식 품명**(`child_name`), 소요량을 `bom_id` 순으로 출력하세요.
(힌트: `bom_structure`의 `parent_part_no`와 `child_part_no`는 둘 다 `part_master.part_no`를 가리킵니다. 5-1처럼 `part_master`를 두 번.)

**[응용]** 냉장고 세트의 1레벨 구성품 중 **자기 아래에 구성품을 가진** 것의 품번, 한글 품명, UIT와 그 아래 구성품 수(`child_cnt`)를 품번 순으로 출력하세요.
(힌트: `bom_structure`를 `b1`(1레벨 행), `b2`(그 아래 행)로 셀프 조인. 첫 행의 자식 품번이 둘째 행의 부모 품번과 같으면 이어집니다.)
:::

### 5-4. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
5행. 부모용(`pp`)과 자식용(`cp`) 별칭을 따로 붙입니다.

```sql
SELECT b.bom_id
     , b.parent_part_no
     , pp.description_kr AS parent_name
     , b.child_part_no
     , cp.description_kr AS child_name
     , b.qty_per
  FROM bom_structure b
  JOIN part_master pp                       -- 부모용 part_master
    ON pp.part_no = b.parent_part_no
  JOIN part_master cp                       -- 자식용 part_master
    ON cp.part_no = b.child_part_no
 WHERE b.model_part_no  = 'TRF38316001'
   AND b.parent_part_no = 'ACB22943901'
 ORDER BY b.bom_id;
```

```result
| bom_id | parent_part_no | parent_name | child_part_no | child_name | qty_per |
| --- | --- | --- | --- | --- | --- |
| 13 | ACB22943901 | 캐비닛 조립체 | MCB45577701 | 외함 캐비닛 | 1.000 |
| 14 | ACB22943901 | 캐비닛 조립체 | MLN40306101 | 내상 라이너 | 1.000 |
| 15 | ACB22943901 | 캐비닛 조립체 | RPU53256801 | 우레탄 발포액 | 6.500 |
| 16 | ACB22943901 | 캐비닛 조립체 | MHG51215701 | 도어 힌지(구형) | 2.000 |
| 17 | ACB22943901 | 캐비닛 조립체 | MHG91254002 | 도어 힌지 | 2.000 |
```
:::

:::teacher 강사 확인
- `bom_id` 16의 `MHG51215701`(도어 힌지(구형))은 **폐기(`status_code` 1) 상태** 부품입니다. README 4장 **A2**(폐기 부품 BOM 잔존)이며, 이 단원 다음의 품질 진단 시간(Q6)에서 `code_status`를 조인해 찾습니다. 훈련생이 먼저 알아채면 칭찬하고, 「상태 코드를 같이 조인하면 확인할 수 있다」까지만 안내하세요.
:::

### 5-4. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
5행. 1레벨 12개 중 5개만 아래에 구성품을 가집니다. 나머지 7개(선반, 나사 등)는 `b2`에 짝이 없어 INNER JOIN에서 빠졌습니다.

```sql
SELECT b1.child_part_no
     , p.description_kr
     , p.uit
     , COUNT(*) AS child_cnt
  FROM bom_structure b1
  JOIN bom_structure b2
    ON b2.parent_part_no = b1.child_part_no
   AND b2.model_part_no  = b1.model_part_no
  JOIN part_master p
    ON p.part_no = b1.child_part_no
 WHERE b1.model_part_no  = 'TRF38316001'
   AND b1.parent_part_no = 'TRF38316001'
 GROUP BY b1.child_part_no, p.description_kr, p.uit
 ORDER BY b1.child_part_no;
```

```result
| child_part_no | description_kr | uit | child_cnt |
| --- | --- | --- | --- |
| ACB22943901 | 캐비닛 조립체 | T | 5 |
| ACC12625601 | 냉동 사이클 조립체 | T | 6 |
| ADR24872401 | 냉장실 도어 조립체 | P | 4 |
| APK15762301 | 포장 조립체 | P | 3 |
| EBA56264701 | 메인 PCB 조립체 | G | 4 |
```

`b2.model_part_no = b1.model_part_no`는 같은 모델의 BOM끼리만 잇는 조건입니다(이 데이터에서는 빼도 결과가 같지만, 같은 조립품이 다른 모델 BOM에도 있을 수 있으므로 함께 씁니다). BOM도 레벨 수를 모르면 몇 번 셀프 조인할지 정할 수 없어 Day 3의 재귀 CTE로 풉니다.
:::

> 확인 문제를 마치면 `SET search_path TO hr;`으로 돌아옵니다.

## 6. 복습 문제

### 6-0. 복습 문제 안내 {keep}

> 범위: INNER JOIN · OUTER JOIN · 안티 조인 · 다중 조인 + 집계. `bom` 스키마의 테이블로 풀어 주세요. 실행 전: `SET search_path TO bom;` 출력 순서는 `ORDER BY` 기준입니다. 조인 키는 2-6 표를 참고하세요.

```icons 일곱 문항
globe | 1 · INNER JOIN | 해외 업체에서 사 오는 부품 | rose
truck | 2 · 3개 테이블 | 세탁기 1레벨 + 공급 방식 의미 | plum
map | 3 · 조인 + 집계 | 국가별 소싱 건수 | lime
list-checks | 4 · LEFT JOIN + COUNT | 상태별 부품 수(0 포함) | ivory
package | 5 · (심화) 안티 조인 | 재고 행 없는 부품 UIT별 | plum
layers | 6 · (심화) 다중 조인 | 1레벨 수입 구매품의 업체 | hot
calendar | 7 · (심화) 1:N 조인 | 생산계획 × BOM 행 수 | lime
```

### 6-1. 복습 1 {keep}

**1.** 해외 업체(`vendor.is_domestic = 'N'`)에서 사 오는 부품의 품번, 한글 품명, 업체명, 국가, 단가, 통화를 출력하세요. 국가 순, 같으면 품번 순으로 정렬합니다. [힌트: `part_sourcing` + `part_master` + `vendor` 세 테이블]

```result 출력 결과 (총 8행)
| part_no | description_kr | vendor_name | country | po_price | currency |
| --- | --- | --- | --- | --- | --- |
| ECP39799101 | 컴프레서 | AsiaComp Co., Ltd. | CN | 48.50 | USD |
| MGL96663301 | 도어 글라스 | Global Steel Trading | JP | 11.50 | USD |
| RSS86949501 | 스테인리스 강판 | Global Steel Trading | JP | 42.00 | USD |
| EIC93178801 | 마이컴 | NanoChip Semiconductor | TW | 3.80 | USD |
| EFN66589301 | 팬 모터 | Pacific Motor Parts | VN | 6.20 | USD |
| EMT73633001 | 스테이터 | Pacific Motor Parts | VN | 28000.00 | KRW |
| EMT78269001 | 로터 | Pacific Motor Parts | VN | 14.00 | USD |
| MBR26166001 | 볼 베어링 | Pacific Motor Parts | VN | 1.90 | USD |
```

### 6-2. 복습 2 {keep}

**2.** 세탁기 세트(`TWM61868701`)의 1레벨 구성품을 BOM 순서(`bom_id`)대로 출력하되, 공급 방식(`supply_type`)의 한글 의미를 함께 보여 주세요. [힌트: `code_supply_type`]

```result 출력 결과 (총 15행) — 앞 5행과 마지막 2행
| bom_id | child_part_no | description_kr | supply_type | meaning_kr |
| --- | --- | --- | --- | --- |
| 40 | ACB29328801 | 캐비닛 조립체 | Assembly Pull | LG가 발주·입고하거나 유상사급하는 품목 |
| 41 | ATB35230801 | 터브 조립체 | Assembly Pull | LG가 발주·입고하거나 유상사급하는 품목 |
| 42 | ADU49470801 | 구동부 조립체 | Assembly Pull | LG가 발주·입고하거나 유상사급하는 품목 |
| 43 | EPM57964301 | 배수 펌프 | Assembly Pull | LG가 발주·입고하거나 유상사급하는 품목 |
| 44 | EVL17769301 | 급수 밸브 | Assembly Pull | LG가 발주·입고하거나 유상사급하는 품목 |
| … | … | … | … | … |
| 53 | MFL37467701 | 사용설명서 | Supplier | 협력사가 직접 제작·구매하는 품목(LG 발주 없음) |
| 54 | SAA76541601 | 메인 펌웨어 | Supplier | 협력사가 직접 제작·구매하는 품목(LG 발주 없음) |
```

### 6-3. 복습 3 · 4 {keep}

**3.** 업체 국가(`vendor.country`)별 소싱 건수(`src_cnt`)를 많은 순으로 출력하세요. 같으면 국가 순입니다.

```result 출력 결과 (총 5행)
| country | src_cnt |
| --- | --- |
| KR | 44 |
| VN | 4 |
| JP | 2 |
| CN | 1 |
| TW | 1 |
```

**4.** 상태 코드표(`code_status`)의 모든 상태에 대해 해당 상태의 부품 수(`part_cnt`)를 출력하세요. 부품이 없는 상태도 0으로 출력하고, 상태 코드 순으로 정렬합니다. [힌트: 코드표를 왼쪽에 두고 LEFT JOIN. `COUNT(*)`를 쓰면 안 되는 이유는 3-5]

```result 출력 결과 (총 6행)
| status_code | status_name | part_cnt |
| --- | --- | --- |
| 1 | Obsolete | 1 |
| 2 | Processing | 0 |
| 3 | Approved | 67 |
| 4 | Service only | 0 |
| 5 | To be obsolete | 0 |
| 6 | MFG Discontinued | 0 |
```

### 6-4. 복습 5 · 6 (심화) {keep}

**5.** (심화) 재고(`inventory`) 행이 없는 부품을 UIT별로 세어, UIT 한글 의미와 함께 출력하세요. 부품 수가 많은 순, 같으면 UIT 순으로 정렬합니다. [힌트: 안티 조인(LEFT JOIN + IS NULL)으로 고른 뒤 `code_uit`를 조인하고 GROUP BY]

```result 출력 결과 (총 3행)
| uit | meaning_kr | part_cnt |
| --- | --- | --- |
| P | 사내 중간 조립품, 재고 관리 없음(팬텀) | 8 |
| T | 사내 조립품, 계획·표준시간·재고 관리 | 5 |
| F | 완제품(모델) | 2 |
```

**6.** (심화) 두 모델의 1레벨 구성품 중 수입 구매품(UIT D)의 모델 한글명, 품번, 한글 품명, 업체명, 리드타임을 출력하세요. 리드타임이 긴 순으로 정렬합니다.

[힌트] (1) 1레벨 구성품 = 부모가 모델인 BOM 행 (`b.parent_part_no = b.model_part_no`) (2) `part_master`를 두 번 조인합니다. 한 번은 모델 이름용, 한 번은 자식 부품용 (5-1, 5-4 복습) (3) 업체명은 `part_sourcing` → `vendor` 순서로 이어서 가져옵니다.

```result 출력 결과 (총 2행)
| model | child_part_no | description_kr | vendor_name | lead_time_days |
| --- | --- | --- | --- | --- |
| 냉장고 세트 | EFN66589301 | 팬 모터 | Pacific Motor Parts | 40 |
| 세탁기 세트 | EPM57964301 | 배수 펌프 | 태양전장(주) | 14 |
```

### 6-5. 복습 7 (심화) {keep}

**7.** (심화) 12월 생산계획(`production_plan`)과 BOM(`bom_structure`)을 모델 품번으로 조인하면 행이 몇 개가 될까요? 모델별로 생산계획 행 수(`plan_rows`)와 조인 결과 행 수(`joined_rows`)를 출력하세요. 모델 품번 순으로 정렬합니다. [힌트: 생산계획 행 수는 조인 결과에서 `COUNT(DISTINCT pl.plan_id)`로 셉니다(4-2)]

```result 출력 결과 (총 2행)
| model_part_no | plan_rows | joined_rows |
| --- | --- | --- |
| TRF38316001 | 10 | 390 |
| TWM61868701 | 10 | 430 |
```

### 6-6. 복습 1 · 2 답 {keep}

:::answer 복습 1 · 2 예시 답안
```sql 1
SELECT s.part_no, p.description_kr, v.vendor_name, v.country, s.po_price, s.currency
  FROM part_sourcing s
  JOIN part_master p
    ON p.part_no = s.part_no
  JOIN vendor v
    ON v.vendor_code = s.vendor_code
 WHERE v.is_domestic = 'N'
 ORDER BY v.country, s.part_no;
```

```sql 2
SELECT b.bom_id, b.child_part_no, p.description_kr, b.supply_type, st.meaning_kr
  FROM bom_structure b
  JOIN part_master p
    ON p.part_no = b.child_part_no
  JOIN code_supply_type st
    ON st.supply_type = b.supply_type
 WHERE b.model_part_no  = 'TWM61868701'
   AND b.parent_part_no = 'TWM61868701'
 ORDER BY b.bom_id;
```
:::

### 6-7. 복습 3 · 4 답 {keep}

:::answer 복습 3 · 4 예시 답안
```sql 3
SELECT v.country, COUNT(*) AS src_cnt
  FROM part_sourcing s
  JOIN vendor v
    ON v.vendor_code = s.vendor_code
 GROUP BY v.country
 ORDER BY src_cnt DESC, v.country;
```

```sql 4
SELECT c.status_code, c.status_name, COUNT(p.part_no) AS part_cnt
  FROM code_status c
  LEFT JOIN part_master p
    ON p.status_code = c.status_code
 GROUP BY c.status_code, c.status_name
 ORDER BY c.status_code;
```

- 4번에서 `COUNT(*)`를 쓰면 부품이 없는 상태 2·4·5·6이 0이 아니라 1로 나옵니다(3-5).
- 4번 결과의 `Obsolete` 1개는 `MHG51215701`(도어 힌지(구형), 5-4 복습 결과에도 나옴)입니다. 이 부품이 어디에 쓰이는지는 품질 진단 시간에 확인합니다.
:::

### 6-8. 복습 5 · 6 답 {keep}

:::answer 복습 5 · 6 예시 답안
```sql 5
SELECT p.uit, u.meaning_kr, COUNT(*) AS part_cnt
  FROM part_master p
  LEFT JOIN inventory i
    ON i.part_no = p.part_no
  JOIN code_uit u
    ON u.uit = p.uit
 WHERE i.part_no IS NULL
 GROUP BY p.uit, u.meaning_kr
 ORDER BY part_cnt DESC, p.uit;
```

```sql 6
SELECT m.description_kr AS model, b.child_part_no, p.description_kr, v.vendor_name, s.lead_time_days
  FROM bom_structure b
  JOIN part_master m
    ON m.part_no = b.model_part_no
  JOIN part_master p
    ON p.part_no = b.child_part_no
  JOIN part_sourcing s
    ON s.part_no = p.part_no
  JOIN vendor v
    ON v.vendor_code = s.vendor_code
 WHERE b.parent_part_no = b.model_part_no
   AND p.uit = 'D'
 ORDER BY s.lead_time_days DESC;
```

- 5번에서 `COUNT(*)`를 써도 되는 이유: `WHERE i.part_no IS NULL`로 남긴 행은 모두 `part_master`의 실제 부품 행이기 때문입니다(LEFT JOIN으로 채운 「빈 부품」 행이 아님).
- 5번의 15개(P 8 · T 5 · F 2)는 모두 사내 조립품·완제품입니다. 구매품(G·D)과 협력사 제작품(S)은 모두 재고 행이 있습니다. 「재고 0」과 「재고 행 없음」은 다릅니다.
:::

### 6-9. 복습 7 답 {keep}

:::answer 복습 7 예시 답안
```sql 7
SELECT pl.model_part_no
     , COUNT(DISTINCT pl.plan_id) AS plan_rows
     , COUNT(*)                   AS joined_rows
  FROM production_plan pl
  JOIN bom_structure b
    ON b.model_part_no = pl.model_part_no
 GROUP BY pl.model_part_no
 ORDER BY pl.model_part_no;
```

- 계획 1행마다 그 모델의 BOM 행(냉장고 39 / 세탁기 43)이 모두 붙어 10 × 39 = 390, 10 × 43 = 430, 합계 **820행**이 됩니다.
- 오류가 아니라 의도한 결과입니다. Day 3에서 「계획 수량 × 소요량」으로 **날짜별 부품 소요량**을 계산할 때 바로 이 결과를 씁니다.
- 이 상태에서 `SUM(pl.plan_qty)`를 구하면 냉장고의 계획 수량 3460이 39번 더해져 134940이 됩니다(4-3).
:::

:::teacher 강사 확인 — 복습 문제에 보이는 이상 데이터
- 1번 `EMT73633001`(스테이터): 해외 업체(VN)인데 통화가 KRW입니다. 이 부품은 README **A1**(UIT G인데 해외 벤더)입니다.
- 2번 `APK23572301`(포장 조립체): UIT P(팬텀)인데 공급 방식이 `Assembly Pull`입니다. README **A3**입니다.
- 6번 `EPM57964301`(배수 펌프): 수입 구매품(D)인데 국내 업체(태양전장)에서 사 옵니다. README **A1**입니다.
- 세 건 모두 다음 품질 진단 시간(Q5·Q7)에서 다룹니다. 훈련생이 질문하면 「이상해 보이는 점을 메모해 두라」고 안내하고, 답은 진단 시간에 확인하게 하세요.
- 5번의 T 5개는 `code_uit`의 T 설명이 「계획·표준시간·재고 관리」인데 재고 행이 없습니다. README 4장 이상 데이터 목록(A1~A9)에는 이 항목이 없으므로 이상으로 단정하지 말고, 「재고 0」과 「재고 행 없음」은 다르다는 점만 짚어 주세요.
:::

## 7. 정리

### 7-1. 오늘 배운 것 {keep}

:::summary
- **JOIN**: 나뉘어 저장된 테이블을 **같은 값을 가진 컬럼(주로 PK–FK)** 으로 이어 한 결과로 보는 방법. 컬럼 이름이 달라도 값이 같으면 조인 키.
- **CROSS JOIN**: 조인 조건이 없으면 행 수 × 행 수. 조인 조건을 빠뜨린 쉼표 조인도 같은 결과(오류 없음).
- **INNER JOIN**: 양쪽에 짝이 있는 행만. `ON`에는 조인 조건, `WHERE`에는 행 조건.
- **테이블 별칭**: 같은 이름의 컬럼은 `별칭.컬럼`으로 구분. 별칭을 지으면 원래 이름은 못 씀.
- **LEFT JOIN**: 왼쪽 테이블의 행은 모두 남기고, 짝이 없으면 오른쪽을 NULL로 채움. **안티 조인** = LEFT JOIN + `오른쪽 테이블의 NULL이 될 수 없는 컬럼(PK·조인 키) IS NULL` (= `NOT EXISTS`).
- **ON vs WHERE**: LEFT JOIN에서 오른쪽 테이블 조건을 `WHERE`에 쓰면 INNER JOIN처럼 됨.
- **COUNT**: LEFT JOIN 결과는 `COUNT(오른쪽 PK)`로 셈. `COUNT(*)`는 NULL로 채운 행까지 셈.
- **1:N 조인**: 행이 늘어남. 집계 전에 `COUNT(*)`로 몇 배가 되었는지 확인.
- **셀프 조인**: 한 테이블을 자기 자신과 조인(직원–상사, BOM 부모–자식 행). 같은 테이블을 두 번 붙일 때도(예전 직무–현재 직무) 역할별 별칭 필수.
:::

### 7-2. 확인 문제

:::quiz
Q. 60번 부서 직원(5행)과 `departments`(27행)를 조인 조건 없이 이었더니 135행이 나왔습니다. 원인과 해결 방법은?
A. 조인 조건이 없어 모든 행끼리 짝지어진 CROSS JOIN 결과(5 × 27)입니다. `ON e.department_id = d.department_id` 조인 조건을 씁니다.

Q. `SELECT department_id, department_name FROM employees e INNER JOIN departments d ON …`이 `ambiguous` 오류가 나는 이유는?
A. `department_id`가 두 테이블에 모두 있어 어느 것인지 알 수 없기 때문입니다. `e.department_id`처럼 별칭을 붙입니다.

Q. 「직원이 한 명도 없는 부서」를 찾을 때 INNER JOIN을 쓰면 안 되는 이유와, 대신 쓰는 패턴은?
A. INNER JOIN은 짝이 없는 행을 결과에서 버립니다. `departments LEFT JOIN employees` 후 `WHERE e.employee_id IS NULL`로 짝이 없는 행만 남깁니다.

Q. 부서별 급여 10000 이상 직원 수를 0명 부서까지 보려고 LEFT JOIN을 썼는데, `WHERE e.salary >= 10000`을 붙이니 7개 부서만 나왔습니다. 왜일까요?
A. `WHERE`는 짝을 다 지은 뒤 적용되어, 1만 미만 직원 행(그리고 짝이 없어 NULL인 행)이 모두 걸러지고 그런 직원이 없는 부서는 남는 행이 없습니다. 조건을 `ON … AND e.salary >= 10000`으로 옮깁니다.

Q. `departments LEFT JOIN employees` 후 `COUNT(*)`를 했더니, 직원이 없는 120번 Treasury가 1로 나왔습니다. 0으로 나오게 하려면?
A. LEFT JOIN이 짝 없는 Treasury에도 NULL로 채운 1행을 만들었기 때문입니다. `COUNT(e.employee_id)`처럼 오른쪽 테이블의 PK를 셉니다.
:::
