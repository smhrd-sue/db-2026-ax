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
- 기존 교안 `8. 서브쿼리.pptx` · `8. 서브쿼리 복습문제.txt`의 **순서(서브쿼리 → 단일행 → 다중행 → 다중열 → 인라인 뷰 → 스칼라)와 예제 유형**을 따르되, 스칼라 서브쿼리를 인라인 뷰 앞에 두어 「WHERE → SELECT → FROM → WITH」 순으로 위치가 넓어지도록 바꿨습니다. 예제는 모두 BOM 실습 데이터(`bom` 스키마)입니다.
- 교안의 모든 SQL과 실행 결과는 `schema_postgres.sql`로 적재한 DB에서 **직접 실행한 결과**입니다. 오류 메시지도 실제 출력입니다. (검증 환경: PostgreSQL 16, `DateStyle = ISO, MDY`. 수업 PC는 PostgreSQL 18이므로 수업 전 한 번 더 실행해 보세요.)
- 각 장 끝 「확인 문제」(복습 1 + 응용 1)는 HR 실습 데이터(`hr_postgres.sql`, `hr` 스키마)로 만들었고, 답안 결과도 직접 실행한 값입니다. 실행 전 `SET search_path TO hr;`가 필요합니다.
- 이 단원은 1교시(60분) 분량입니다. 확인 문제와 7장 복습 문제는 시간에 따라 일부만 풀고, 나머지는 과제로 활용하세요.

| 교시 | 시간 | 내용 | 해당 장 | 기존 교안 대응 |
| --- | --- | --- | --- | --- |
| **1교시** | 0~12분 | 서브쿼리 개념 · 단일행 서브쿼리 · 여러 행 오류 · 0행이면 NULL | 1 | `8. 서브쿼리.pptx` 3~7 |
| | 12~27분 | 다중행: IN · NOT IN과 NULL · ANY/ALL · EXISTS(상관 서브쿼리) | 2 | `8. 서브쿼리.pptx` 8~13 |
| | 27~33분 | 다중열 서브쿼리 · 단일열 IN과의 차이 | 3 | `8. 서브쿼리.pptx` 14~16 |
| | 33~43분 | 스칼라 서브쿼리(SELECT절) · NULL과 오류 | 4 | `8. 서브쿼리 복습문제.txt` 1번 |
| | 43~53분 | 인라인 뷰(FROM절) · 「집계 먼저, 조인 나중」 | 5 | `8. 서브쿼리.pptx` 17~18, 복습문제 2번 |
| | 53~60분 | WITH로 단계 나누기 · 복습 문제 안내 | 6~7 | — |
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

### 1-2. 쿼리 두 번 — ① 컴프레서의 리드타임 {keep}

**질문:** 컴프레서(`ECP39799101`)보다 리드타임이 **긴** 소싱 품목은?

이 질문은 두 단계로 풀 수 있습니다.

:::cols
```sql ① 컴프레서의 리드타임을 먼저 조회
SELECT lead_time_days
  FROM part_sourcing
 WHERE part_no = 'ECP39799101';
```

```result
| lead_time_days |
| --- |
| 50 |
```
:::

:::cols
```sql ② 그 값(50)을 조건에 넣어 다시 조회
SELECT part_no, vendor_code, line_type, lead_time_days
  FROM part_sourcing
 WHERE lead_time_days > 50;
```

```result
| part_no | vendor_code | line_type | lead_time_days |
| --- | --- | --- | --- |
| EIC93178801 | V1005 | I | 60 |
```
:::

### 1-2. 쿼리 두 번 → 한 번으로 {keep}

①의 결과를 손으로 옮겨 적는 대신, **① 쿼리를 ②의 자리에 그대로 넣은 것**이 서브쿼리입니다.

:::cols
```sql
SELECT part_no, vendor_code, line_type, lead_time_days
  FROM part_sourcing
 WHERE lead_time_days > (SELECT lead_time_days
                           FROM part_sourcing
                          WHERE part_no = 'ECP39799101');
```

```result
| part_no | vendor_code | line_type | lead_time_days |
| --- | --- | --- | --- |
| EIC93178801 | V1005 | I | 60 |
```
:::

- 괄호 안이 **먼저 실행되어 값(50)이 되고**, 그 값으로 메인쿼리가 실행된다고 읽으면 됩니다.
- 컴프레서의 리드타임이 바뀌어도 쿼리를 고칠 필요가 없습니다. ==값을 적어 넣지 않고 「값을 구하는 방법」을 적어 넣는 것==이 서브쿼리의 장점입니다.

### 1-3. 단일행 서브쿼리와 단일행 연산자 {keep}

1-2의 서브쿼리는 결과가 **1행 1열(값 하나)** 입니다. 이런 서브쿼리를 **단일행 서브쿼리**라고 하고, 비교에는 **단일행 연산자**를 씁니다.

| 단일행 연산자 | 의미 |
| --- | --- |
| `=` | 같다 |
| `<>`, `!=` | 같지 않다 |
| `>`, `>=` | 크다, 크거나 같다 |
| `<`, `<=` | 작다, 작거나 같다 |

**집계 함수와 함께** — 4단원의 집계 함수는 결과가 항상 1행이므로 단일행 서브쿼리에 잘 어울립니다.

### 1-3. 평균보다 오래 걸리는 소싱 품목 {keep}

**질문:** 전체 평균 리드타임보다 오래 걸리는 소싱 품목은?

:::answer 예시 답안 — 눌러서 보기
```sql 평균 리드타임
SELECT ROUND(AVG(lead_time_days), 1) AS avg_lt
  FROM part_sourcing;
```

```result
| avg_lt |
| --- |
| 16.8 |
```

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

> 4단원 3-2에서 `WHERE`에는 집계 함수를 쓸 수 없다고 했습니다. `WHERE lead_time_days > AVG(lead_time_days)`는 오류지만, ==집계 함수를 서브쿼리 안에 넣으면== 서브쿼리가 먼저 값(16.8…)으로 바뀌므로 `WHERE`에서 비교할 수 있습니다.
:::

### 1-3. 가장 최근에 등록된 부품 {keep}

**질문:** 가장 최근에 등록된 부품은?

:::answer 예시 답안 — 눌러서 보기
```sql
SELECT part_no, description_kr, created_at
  FROM part_master
 WHERE created_at = (SELECT MAX(created_at)
                       FROM part_master);
```

```result
| part_no | description_kr | created_at |
| --- | --- | --- |
| EBA60141001 | 디스플레이 PCB | 2025-12-26 |
```
:::

### 1-4. 주의 ① 서브쿼리 결과가 여러 행이면 ⭐ {keep}

:::error 서브쿼리 결과가 여러 행이면 — 단일행 연산자 오류
`V1009`(Pacific Motor Parts)는 소싱 품목이 4개라 리드타임도 4개입니다. 값 4개와 `>` 하나로 비교할 수는 없습니다.

```sql
SELECT part_no, lead_time_days
  FROM part_sourcing
 WHERE lead_time_days > (SELECT lead_time_days
                           FROM part_sourcing
                          WHERE vendor_code = 'V1009');
```

```error
ERROR:  more than one row returned by a subquery used as an expression
```

서브쿼리 결과가 여러 행이면 ==다중행 연산자(IN, ANY, ALL)== 를 써야 합니다(2장).
:::

### 1-4. 주의 ② 서브쿼리 결과가 0행이면 {keep}

:::error 서브쿼리 결과가 0행이면 — 오류 없이 0행
품번을 한 글자 빠뜨려(`ECP3979910`) 서브쿼리가 아무 행도 찾지 못하면, 서브쿼리 값은 **NULL**이 됩니다.

```sql
SELECT (SELECT lead_time_days
          FROM part_sourcing
         WHERE part_no = 'ECP3979910') AS sub_result;
```

```result
| sub_result |
| --- |
| NULL |
```

`lead_time_days > NULL`은 참이 아니므로(3단원 5-1) 메인쿼리 결과는 **0행**입니다. 오류 메시지가 없어서 「조건에 맞는 품목이 없다」로 오해하기 쉽습니다. ==결과가 0행이면 서브쿼리만 따로 실행해 값이 나오는지 먼저 확인==하세요.
:::

### 1-5. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마)

:::try
**[복습]** 이름(`first_name`)이 Nancy인 직원보다 **먼저 입사한** 직원의 이름과 입사일을 입사일 순(같으면 이름 순)으로 출력하세요.

**[응용]** 아래 쿼리는 오류가 납니다. 오류의 원인을 설명하고, **John Chen**(`last_name` = 'Chen')보다 급여가 많은 직원 **수**를 구하는 쿼리로 고치세요.

```sql
SELECT first_name, salary
  FROM employees
 WHERE salary > (SELECT salary
                   FROM employees
                  WHERE first_name = 'John');
```
:::

### 1-5. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
6행

```sql
SELECT first_name, hire_date
  FROM employees
 WHERE hire_date < (SELECT hire_date
                      FROM employees
                     WHERE first_name = 'Nancy')
 ORDER BY hire_date, first_name;
```

```result
| first_name | hire_date |
| --- | --- |
| Lex | 2001-01-13 |
| Hermann | 2002-06-07 |
| Shelley | 2002-06-07 |
| Susan | 2002-06-07 |
| William | 2002-06-07 |
| Daniel | 2002-08-16 |
```

기존 교안 예제는 `<=`라서 Nancy 본인(2002-08-17)도 함께 나옵니다. 「먼저」라면 `<`입니다.
:::

### 1-5. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
```error
ERROR:  more than one row returned by a subquery used as an expression
```

`first_name = 'John'`인 직원이 Chen(8200), Seo(2700), Russell(14000) **3명**이라 서브쿼리가 3행을 돌려주기 때문입니다. 성까지 조건에 넣어 1행으로 만듭니다.

```sql
SELECT COUNT(*) AS cnt
  FROM employees
 WHERE salary > (SELECT salary
                   FROM employees
                  WHERE first_name = 'John'
                    AND last_name  = 'Chen');
```

```result
| cnt |
| --- |
| 31 |
```

이름은 겹칠 수 있습니다. 실무에서는 `employee_id = 110`처럼 ==PK로 조회==하는 것이 가장 안전합니다(4단원 3-5 「조회와 기록은 항상 품번으로」와 같은 원리).
:::

## 2. 다중행 서브쿼리 — 결과가 여러 행일 때

### 2-1. 다중행 연산자 {keep}

서브쿼리 결과가 **여러 행**이면 단일행 연산자 대신 **다중행 연산자**를 씁니다.

| 다중행 연산자 | 참이 되는 경우 |
| --- | --- |
| `IN` | 서브쿼리 결과 중 **하나라도 같으면** |
| `비교연산자 ANY` (= `SOME`) | 서브쿼리 결과 중 **하나라도** 비교 결과가 참이면 |
| `비교연산자 ALL` | 서브쿼리 결과 **모두**와 비교 결과가 참이면 |
| `EXISTS` | 서브쿼리 결과가 **1행이라도 있으면** |

### 2-2. IN — 해외 업체 코드 {keep}

**질문:** 해외 업체에서 사 오는 소싱 품목은?

해외 업체 코드는 `vendor`에, 소싱 품목은 `part_sourcing`에 있습니다.

:::cols
```sql
SELECT vendor_code, vendor_name
  FROM vendor
 WHERE is_domestic = 'N'
 ORDER BY vendor_code;
```

```result
| vendor_code | vendor_name |
| --- | --- |
| V1004 | AsiaComp Co., Ltd. |
| V1005 | NanoChip Semiconductor |
| V1007 | Global Steel Trading |
| V1009 | Pacific Motor Parts |
```
:::

이 4개 코드를 `IN ('V1004', 'V1005', 'V1007', 'V1009')`로 적어 넣는 대신 **서브쿼리로** 넣습니다.

### 2-2. IN — 목록 중 하나와 같으면 {keep}

:::cols
```sql
SELECT part_no, vendor_code, line_type, currency
  FROM part_sourcing
 WHERE vendor_code IN (SELECT vendor_code
                         FROM vendor
                        WHERE is_domestic = 'N')
 ORDER BY vendor_code, part_no;
```

```result
| part_no | vendor_code | line_type | currency |
| --- | --- | --- | --- |
| ECP39799101 | V1004 | I | USD |
| EIC93178801 | V1005 | I | USD |
| MGL96663301 | V1007 | I | USD |
| RSS86949501 | V1007 | I | USD |
| EFN66589301 | V1009 | I | USD |
| EMT73633001 | V1009 | D | KRW |
| EMT78269001 | V1009 | I | USD |
| MBR26166001 | V1009 | I | USD |
```
:::

### 2-2. 서브쿼리 안에 서브쿼리 {keep}

이번에는 부품 마스터에서 품명과 UIT를 함께 봅니다. 서브쿼리는 여러 겹으로 넣을 수 있고, **가장 안쪽부터** 읽습니다.

:::cols
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
:::

### 2-2. 생각해 보기 — 해외 업체에서 사는데 UIT가 G? {keep}

:::try 생각해 보기 — 해외 업체에서 사는데 UIT가 G?
`code_uit`에서 G는 **국내 구매품**, D는 **수입 구매품**입니다. 해외 업체에서 사 오는 8개 중 스테이터·로터 2개는 UIT가 G입니다. 이 데이터는 맞는 걸까요? 어느 테이블을 더 보면 판단할 수 있을까요?
:::

:::teacher 강사 확인
- `EMT73633001`(스테이터)·`EMT78269001`(로터)는 README 4장 이상 데이터 **A1**(수입 벤더인데 UIT G)에 포함된 품번입니다. Day 2 품질 진단 시간(Q5)에서 다룬 내용이므로 「Day 2에서 JOIN으로 찾은 것을 서브쿼리로도 찾을 수 있다」 정도로 연결하세요.
- 원인 추적(A9, `uit_change_history.line_type_updated = 'N'`)은 Day 2에서 이미 다뤘으므로 여기서는 반복하지 않습니다.
:::

### 2-3. NOT IN — 목록의 어느 것과도 같지 않으면 {keep}

**질문:** BOM에 **자식(child)으로 한 번도 쓰이지 않은** 품목은?

:::cols
```sql
SELECT part_no, description_kr, uit
  FROM part_master
 WHERE part_no NOT IN (SELECT child_part_no
                         FROM bom_structure)
 ORDER BY part_no;
```

```result
| part_no | description_kr | uit |
| --- | --- | --- |
| TRF38316001 | 냉장고 세트 | F |
| TWM61868701 | 세탁기 세트 | F |
```
:::

자식으로 쓰이지 않는 품목은 **최상위 세트(모델) 2개**뿐입니다. 나머지 66개 부품은 모두 어딘가의 자식입니다.

### 2-3. NOT IN과 NULL 함정 ⭐ {keep}

:::error NOT IN 목록에 NULL이 하나라도 있으면 → 결과 0행
`NOT IN (A, B)`는 `<> A AND <> B`와 같습니다. 목록에 NULL이 끼면 `<> NULL`이 **참도 거짓도 아닌 값(NULL)** 이 되어, `AND`로 묶인 전체가 참이 될 수 없습니다.

```sql
SELECT COUNT(*) AS cnt FROM part_master WHERE part_no NOT IN ('EIC93178801');        -- 67
SELECT COUNT(*) AS cnt FROM part_master WHERE part_no NOT IN ('EIC93178801', NULL);  -- 0
SELECT COUNT(*) AS cnt FROM part_master WHERE part_no IN     ('EIC93178801', NULL);  -- 1
```

- 첫 줄은 **67**, NULL을 넣은 둘째 줄은 **0**입니다.
- 반면 `IN`은 `= A OR = B`라서 NULL이 섞여도 같은 값이 하나 있으면 참입니다(셋째 줄 **1**).

서브쿼리도 똑같습니다. ==NOT IN 서브쿼리의 컬럼에 NULL이 있을 수 있으면==, 서브쿼리 안에 `WHERE 컬럼 IS NOT NULL`을 붙이거나 2-5의 `NOT EXISTS`를 씁니다. (2-6 확인 문제에서 HR 데이터로 직접 확인합니다.)
:::

> 위 예제의 `bom_structure.child_part_no`에는 NULL이 없어서 결과가 정상으로 나왔습니다. 하지만 **지금 NULL이 없다고 앞으로도 없는 것은 아닙니다.** `CREATE TABLE`에 `NOT NULL` 제약이 있는지 확인해 보세요(Day 4).

### 2-4. ANY와 ALL — 수입 소싱의 리드타임 {keep}

`ANY`와 `ALL`은 `>`, `<`, `=` 같은 **비교 연산자 뒤에** 붙여 씁니다. 수입(`line_type = 'I'`) 소싱의 리드타임은 다음 7개입니다.

:::cols
```sql
SELECT lead_time_days
  FROM part_sourcing
 WHERE line_type = 'I'
 ORDER BY lead_time_days;
```

```result
| lead_time_days |
| --- |
| 30 |
| 30 |
| 40 |
| 45 |
| 45 |
| 50 |
| 60 |
```
:::

### 2-4. >= ANY — 하나라도 크거나 같으면 {keep}

**`>= ANY`** — 하나라도 「크거나 같으면」 참 → 사실상 **최솟값(30) 이상**

**질문:** 국내 구매 조건(`D`)인데 리드타임이 **수입품 수준**(수입 리드타임 중 어느 하나 이상)인 소싱은?

:::cols
```sql
SELECT part_no, vendor_code, line_type, lead_time_days
  FROM part_sourcing
 WHERE line_type = 'D'
   AND lead_time_days >= ANY (SELECT lead_time_days
                                FROM part_sourcing
                               WHERE line_type = 'I');
```

```result
| part_no | vendor_code | line_type | lead_time_days |
| --- | --- | --- | --- |
| EMT73633001 | V1009 | D | 30 |
```
:::

2-2에서 본 스테이터가 또 나왔습니다. 국내 구매 조건인데 해외 업체(V1009)에서, 수입품만큼 오래 걸려 들어오는 품목입니다.

### 2-4. > ALL — 전부보다 크면 {keep}

**`> ALL`** — 전부보다 「커야」 참 → 사실상 **최댓값보다 큼**. 국내(`D`) 소싱의 최장 리드타임은 30일입니다(`SELECT MAX(lead_time_days) FROM part_sourcing WHERE line_type = 'D'` → 30).

**질문:** **모든** 국내 소싱보다 리드타임이 긴 소싱은?

:::cols
```sql
SELECT part_no, vendor_code, line_type, lead_time_days
  FROM part_sourcing
 WHERE lead_time_days > ALL (SELECT lead_time_days
                               FROM part_sourcing
                              WHERE line_type = 'D')
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
```
:::

### 2-4. ANY · ALL 정리 {keep}

| 쓰는 법 | 같은 뜻 | 기존 교안 그림 |
| --- | --- | --- |
| `> ANY (서브쿼리)` | `> (서브쿼리의 MIN)` | 하나라도 T면 T |
| `> ALL (서브쿼리)` | `> (서브쿼리의 MAX)` | 전부 T여야 T |
| `= ANY (서브쿼리)` | `IN (서브쿼리)` | — |

> `ANY`·`ALL`은 `MIN`·`MAX` 서브쿼리로 바꿔 쓸 수 있는 경우가 많습니다. 읽는 사람이 바로 이해할 수 있는 쪽을 고르세요. 이 교안에서는 `IN`·`EXISTS`를 주로 씁니다.

### 2-5. EXISTS — 짝이 있는가 (상관 서브쿼리) {keep}

`EXISTS`는 서브쿼리 결과가 **1행이라도 있으면 참**입니다. 값을 비교하지 않고 **있는지 없는지만** 봅니다.

**질문:** 입고 예정(`scheduled_receipt`)이 잡혀 있는 부품은?

:::cols
```sql
SELECT p.part_no, p.description_kr
  FROM part_master p
 WHERE EXISTS (SELECT 1
                 FROM scheduled_receipt r
                WHERE r.part_no = p.part_no)
 ORDER BY p.part_no;
```

```result
| part_no | description_kr |
| --- | --- |
| EBA56264701 | 메인 PCB 조립체 |
| ECP39799101 | 컴프레서 |
| EIC93178801 | 마이컴 |
| MGL96663301 | 도어 글라스 |
| RSS86949501 | 스테인리스 강판 |
```
:::

### 2-5. 상관 서브쿼리 읽는 법 {keep}

- 서브쿼리 안의 `r.part_no = p.part_no`에서 `p`는 **메인쿼리의 테이블**입니다. 이렇게 메인쿼리의 컬럼을 참조하는 서브쿼리를 **상관(correlated) 서브쿼리**라고 합니다.
- 읽는 법: 「`part_master`의 **한 행(p)마다**, 그 품번으로 입고 예정이 있는지 찾아보고, 있으면 남긴다.」
- `SELECT 1`의 `1`에는 의미가 없습니다. `EXISTS`는 **행이 있는지**만 보므로 무엇을 SELECT해도 결과가 같습니다.

### 2-5. NOT EXISTS — 짝이 없는 행 {keep}

**질문:** 재고(`inventory`) 행이 **없는** 부품은? (5단원 3-3·3-4 안티 조인)

```sql
SELECT p.part_no, p.description_kr, p.uit
  FROM part_master p
 WHERE NOT EXISTS (SELECT 1
                     FROM inventory i
                    WHERE i.part_no = p.part_no)
 ORDER BY p.uit, p.part_no;
```

- 68개 부품 중 **15개**입니다. 5단원 3-3 ②에서 「UIT 조건을 빼면 15행(F 2, P 8, T 5)이 나온다」고 한 바로 그 행들을, `LEFT JOIN … WHERE i.part_no IS NULL` 대신 `NOT EXISTS`로 찾은 것입니다.
- `NOT EXISTS`는 **행이 있는지만 보기 때문에** 2-3의 NOT IN NULL 함정이 없습니다.

### 2-5. NOT EXISTS 실행 결과 {keep}

```result 15행
| part_no | description_kr | uit |
| --- | --- | --- |
| TRF38316001 | 냉장고 세트 | F |
| TWM61868701 | 세탁기 세트 | F |
| ACP85953101 | 컨트롤 패널 조립체 | P |
| ADR24872401 | 냉장실 도어 조립체 | P |
| ADR69737101 | 도어 조립체 | P |
| APK15762301 | 포장 조립체 | P |
| APK23572301 | 포장 조립체 | P |
| MCB45577701 | 외함 캐비닛 | P |
| MCB74311201 | 외함 캐비닛 | P |
| MLN40306101 | 내상 라이너 | P |
| ACB22943901 | 캐비닛 조립체 | T |
| ACB29328801 | 캐비닛 조립체 | T |
| ACC12625601 | 냉동 사이클 조립체 | T |
| ADU49470801 | 구동부 조립체 | T |
| ATB35230801 | 터브 조립체 | T |
```

### 2-5. 생각해 보기 — P와 T는 같은 「재고 없음」일까? {keep}

:::try 생각해 보기 — P와 T는 같은 「재고 없음」일까?
`code_uit`에서 P는 「사내 중간 조립품, **재고 관리 없음**(팬텀)」, T는 「사내 조립품, 계획·표준시간·**재고 관리**」입니다. 결과의 P 8개와 T 5개를 이 정의에 비춰 보면, 어느 쪽이 「원래 없는 것이 맞는」 행이고 어느 쪽이 「확인이 필요한」 행일까요?
:::

:::teacher 강사 확인
- 5단원 3-3 ② 강사 확인과 같은 15행입니다. T 5개는 README 4장 목록(A1~A9)에 **없는 항목**이므로 이상 데이터로 단정하지 말고, 「코드 정의와 데이터가 어긋나 보이면 담당 부서에 확인한다」는 태도로 마무리하세요. 같은 T인 `EMT68237401`(DD 모터)은 사내 부품라인 창고(`WH-C1`)에 재고 900이 있습니다.
:::

### 2-6. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;`

:::try
**[복습]** `location_id`가 1700인 부서에 근무하는 직원 중 급여가 10000 이상인 직원의 이름, 급여, 부서 번호를 급여가 높은 순(같으면 이름 순)으로 출력하세요. (`IN` 서브쿼리 사용)

**[응용]** 직원이 한 명도 없는 부서 수를 아래처럼 구했더니 **0**이 나왔습니다. 실제로는 몇 개일까요? 0이 나온 이유를 설명하고, 바르게 고친 쿼리 두 가지를 쓰세요.

```sql
SELECT COUNT(*) AS cnt
  FROM departments
 WHERE department_id NOT IN (SELECT department_id
                               FROM employees);
```
:::

### 2-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
6행

```sql
SELECT first_name, salary, department_id
  FROM employees
 WHERE department_id IN (SELECT department_id
                           FROM departments
                          WHERE location_id = 1700)
   AND salary >= 10000
 ORDER BY salary DESC, first_name;
```

```result
| first_name | salary | department_id |
| --- | --- | --- |
| Steven | 24000.00 | 90 |
| Lex | 17000.00 | 90 |
| Neena | 17000.00 | 90 |
| Nancy | 12008.00 | 100 |
| Shelley | 12008.00 | 110 |
| Den | 11000.00 | 30 |
```
:::

### 2-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
실제로는 **16개**입니다. `employees.department_id`에는 부서가 없는 직원 1명(178 Kimberely Grant)의 **NULL**이 있습니다(4단원 1-6). 서브쿼리 목록에 NULL이 섞여 `NOT IN`이 어떤 부서에서도 참이 되지 못했습니다(2-3).

```sql 방법 1: 서브쿼리에서 NULL 제외
SELECT COUNT(*) AS cnt
  FROM departments
 WHERE department_id NOT IN (SELECT department_id
                               FROM employees
                              WHERE department_id IS NOT NULL);
```

```sql 방법 2: NOT EXISTS
SELECT COUNT(*) AS cnt
  FROM departments d
 WHERE NOT EXISTS (SELECT 1
                     FROM employees e
                    WHERE e.department_id = d.department_id);
```

```result 두 방법 모두
| cnt |
| --- |
| 16 |
```
:::

## 3. 다중열 서브쿼리 — 두 컬럼을 짝으로 비교

### 3-1. (컬럼1, 컬럼2) IN (서브쿼리) {keep}

서브쿼리가 **컬럼 여러 개**를 돌려주면, 메인쿼리도 **같은 개수·같은 순서**로 괄호에 묶어 비교합니다. 주로 `IN`과 함께 씁니다.

**질문:** 원화 소싱 기준, **업체별로 가장 비싼** 품목은?

:::cols
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
:::

- 서브쿼리는 「업체 코드 + 그 업체의 최고 단가」 **짝**을 9개 돌려줍니다. 메인쿼리의 `(vendor_code, po_price)`가 그 짝 중 하나와 **둘 다** 같아야 남습니다.
- 4단원에서 `GROUP BY`를 쓰면 `SELECT`에 일반 컬럼(`part_no`)을 쓸 수 없었습니다. ==「그룹의 최댓값을 가진 행 전체」== 를 보고 싶을 때 다중열 서브쿼리를 씁니다.

### 3-2. 업체별 최장 리드타임 {keep}

**질문:** 업체별로 리드타임이 **가장 긴** 소싱 품목은? (같은 업체 안에서 최장 리드타임이 같으면 모두 출력)

:::cols
```sql
SELECT vendor_code, MAX(lead_time_days) AS max_lt
  FROM part_sourcing
 GROUP BY vendor_code
 ORDER BY vendor_code;
```

```result
| vendor_code | max_lt |
| --- | --- |
| V1001 | 21 |
| V1002 | 10 |
| V1003 | 21 |
| V1004 | 50 |
| V1005 | 60 |
| V1006 | 14 |
| V1007 | 45 |
| V1008 | 7 |
| V1009 | 40 |
| V1010 | 14 |
| V1011 | 14 |
| V1012 | 3 |
```
:::

업체 코드는 빼고 **리드타임만** 비교하면 어떻게 될까요?

### 3-2. 단일열 IN으로 쓰면 안 되는 이유 {keep}

두 방식의 결과 행 수를 비교합니다.

:::cols
```sql 다중열 — 업체와 짝으로
SELECT COUNT(*) AS cnt
  FROM part_sourcing
 WHERE (vendor_code, lead_time_days) IN (SELECT vendor_code, MAX(lead_time_days)
                                           FROM part_sourcing
                                          GROUP BY vendor_code);
```

```result
| cnt |
| --- |
| 35 |
```
:::

:::cols
```sql 단일열 — 리드타임만
SELECT COUNT(*) AS cnt
  FROM part_sourcing
 WHERE lead_time_days IN (SELECT MAX(lead_time_days)
                            FROM part_sourcing
                           GROUP BY vendor_code);
```

```result
| cnt |
| --- |
| 49 |
```
:::

### 3-2. 14행이 더 나온 이유 {keep}

- 단일열 쪽이 **14행 더** 나왔습니다. 예를 들어 `V1001`의 나사 `FSC33042701`(7일)은 V1001의 최장(21일)이 아닌데도 나옵니다. 7일이 **`V1008`의 최장 리드타임**이라 목록 `(21, 10, 21, 50, 60, 14, 45, 7, 40, 14, 14, 3)` 안에 있기 때문입니다.
- ==「업체별」 최댓값은 업체와 짝을 지어야 의미가 있습니다.== 기준 컬럼(`vendor_code`)까지 함께 비교하세요.

> 같은 업체 안에서 최장 리드타임이 같은 품목이 여럿이면(예: V1006은 6품목 모두 14일) 모두 나옵니다. 그래서 35행입니다. 1행만 고르는 방법은 Day 3 6교시 `ROW_NUMBER`에서 다룹니다.

### 3-3. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;`

:::try
**[복습]** 직책(`job_id`)별로 **가장 적은** 급여를 받는 직원의 이름, 급여, 직책을 직책 순(같으면 이름 순)으로 출력하세요. (다중열 서브쿼리 사용)

**[응용]** [복습]의 `WHERE`를 `salary IN (SELECT MIN(salary) FROM employees GROUP BY job_id)`로 바꾸면 결과가 몇 행이 되나요? 왜 늘어나는지 예를 하나 들어 설명하세요.
:::

### 3-3. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
21행. 직책은 19개인데 `AD_VP`(17000, 2명)와 `SH_CLERK`(2500, 2명)는 최저 급여를 받는 직원이 2명씩이라 21행입니다.

```sql
SELECT first_name, salary, job_id
  FROM employees
 WHERE (job_id, salary) IN (SELECT job_id, MIN(salary)
                              FROM employees
                             GROUP BY job_id)
 ORDER BY job_id, first_name;
```

```result
| first_name | salary | job_id |
| --- | --- | --- |
| William | 8300.00 | AC_ACCOUNT |
| Shelley | 12008.00 | AC_MGR |
| Jennifer | 4400.00 | AD_ASST |
| Steven | 24000.00 | AD_PRES |
| Lex | 17000.00 | AD_VP |
| Neena | 17000.00 | AD_VP |
| Luis | 6900.00 | FI_ACCOUNT |
| Nancy | 12008.00 | FI_MGR |
| Susan | 6500.00 | HR_REP |
| Diana | 4200.00 | IT_PROG |
| Michael | 13000.00 | MK_MAN |
| Pat | 6000.00 | MK_REP |
| Hermann | 10000.00 | PR_REP |
| Karen | 2500.00 | PU_CLERK |
| Den | 11000.00 | PU_MAN |
| Eleni | 10500.00 | SA_MAN |
| Sundita | 6100.00 | SA_REP |
| Martha | 2500.00 | SH_CLERK |
| Randall | 2500.00 | SH_CLERK |
| TJ | 2100.00 | ST_CLERK |
| Kevin | 5800.00 | ST_MAN |
```
:::

### 3-3. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
**33행**(12행 증가)

```sql
SELECT COUNT(*) AS cnt
  FROM employees
 WHERE salary IN (SELECT MIN(salary)
                    FROM employees
                   GROUP BY job_id);
```

```result
| cnt |
| --- |
| 33 |
```

예: `ST_CLERK`인 James·Joshua·Peter(2500)는 ST_CLERK의 최저 급여(2100)가 아닌데도 나옵니다. 2500이 **PU_CLERK·SH_CLERK의 최저 급여**라 목록에 들어 있기 때문입니다.
:::

:::teacher 강사 확인
- 기존 교안 `8. 서브쿼리.pptx` 10번 슬라이드(`SALARY IN (SELECT MAX(SALARY) … GROUP BY DEPARTMENT_ID)`)도 같은 이유로 「부서별 최고 연봉 직원」보다 많은 행이 나올 수 있으므로, 14번 슬라이드의 다중열 방식과 비교해서 보여 주세요.
:::

## 4. 스칼라 서브쿼리 — SELECT절에서 컬럼 하나 만들기

### 4-1. 행마다 값 하나를 가져오기 {keep}

`SELECT` 절에 쓰는 서브쿼리를 **스칼라(scalar) 서브쿼리**라고 합니다. 「스칼라」는 **값 하나**라는 뜻이고, 메인쿼리의 **행마다 1행 1열**을 돌려줘 컬럼 하나가 됩니다. 대부분 2-5의 **상관 서브쿼리** 모양입니다.

**질문:** 수입(`I`) 소싱 품목을 업체 **이름**과 함께 보여 주세요.

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

### 4-1. 실행 결과 {keep}

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

읽는 법: 「소싱 한 행(s)마다, 그 업체 코드로 `vendor`에서 이름을 찾아 옆에 붙인다.」 5단원 2-2(소싱 정보에 업체 이름 붙이기)의 JOIN과 같은 결과를 **컬럼 단위로** 만드는 방법입니다.

### 4-2. 짝이 없으면 NULL {keep}

**질문:** 조립품(`class_lv1 = 'A'`)의 UIT 한글 의미와 현재 재고를 함께 보여 주세요.

```sql
SELECT p.part_no
     , p.description_kr
     , p.uit
     , (SELECT c.meaning_kr
          FROM code_uit c
         WHERE c.uit = p.uit)         AS uit_kr
     , (SELECT i.on_hand_qty
          FROM inventory i
         WHERE i.part_no = p.part_no) AS on_hand
  FROM part_master p
 WHERE p.class_lv1 = 'A'
 ORDER BY p.part_no;
```

### 4-2. 실행 결과 {keep}

```result
| part_no | description_kr | uit | uit_kr | on_hand |
| --- | --- | --- | --- | --- |
| ACB22943901 | 캐비닛 조립체 | T | 사내 조립품, 계획·표준시간·재고 관리 | NULL |
| ACB29328801 | 캐비닛 조립체 | T | 사내 조립품, 계획·표준시간·재고 관리 | NULL |
| ACC12625601 | 냉동 사이클 조립체 | T | 사내 조립품, 계획·표준시간·재고 관리 | NULL |
| ACP85953101 | 컨트롤 패널 조립체 | P | 사내 중간 조립품, 재고 관리 없음(팬텀) | NULL |
| ADR24872401 | 냉장실 도어 조립체 | P | 사내 중간 조립품, 재고 관리 없음(팬텀) | NULL |
| ADR69737101 | 도어 조립체 | P | 사내 중간 조립품, 재고 관리 없음(팬텀) | NULL |
| ADU49470801 | 구동부 조립체 | T | 사내 조립품, 계획·표준시간·재고 관리 | NULL |
| AHD26818801 | 핸들 조립체 | S | 협력사 제작, 유상사급 품목 포함 | 4233.00 |
| APK15762301 | 포장 조립체 | P | 사내 중간 조립품, 재고 관리 없음(팬텀) | NULL |
| APK23572301 | 포장 조립체 | P | 사내 중간 조립품, 재고 관리 없음(팬텀) | NULL |
| ATB35230801 | 터브 조립체 | T | 사내 조립품, 계획·표준시간·재고 관리 | NULL |
```

- 재고 행이 없는 부품은 `on_hand`가 **NULL**입니다. 행이 사라지지 않고 NULL로 남는다는 점이 **LEFT JOIN과 같습니다**. (2-5의 NOT EXISTS 결과와 비교해 보세요.)
- 재고가 「0」인 것과 「행이 없어 NULL」인 것은 다릅니다(Day 1 7교시).

### 4-2. 집계 함수와 함께 {keep}

스칼라 서브쿼리 안에서 집계하면 행마다 「개수」, 「합계」를 붙일 수 있습니다.

**질문:** 체결 부품(`class_lv1 = 'F'`)이 BOM에 몇 번, 몇 개 모델에 쓰이는지 보여 주세요.

:::cols
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
:::

4단원 3-5의 「공용 부품」(`HAVING COUNT(DISTINCT model_part_no) = 2`)을 부품 마스터 기준으로 다시 본 것입니다. 나사 M4x12와 필라멘트 테이프는 두 모델에 모두 쓰입니다.

### 4-3. 주의 ① 행마다 「1행」이 아니면 오류 {keep}

:::error 행마다 「1행」이 아니면 오류
나사는 BOM에 3번씩 쓰여 **부모가 3개**입니다. 부모 품번을 스칼라 서브쿼리로 가져오면 오류가 납니다.

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

부모가 하나뿐인 컴프레서(`WHERE p.part_no = 'ECP39799101'`)만 조회하면 오류 없이 `ACC12625601`(냉동 사이클 조립체)이 나옵니다. 하지만 ==지금 데이터에서 오류가 안 난다고 안전한 것이 아닙니다.== 컴프레서가 내일 다른 조립품에도 쓰이면 같은 쿼리가 오류로 바뀝니다. 여러 부모를 모두 봐야 하는 질문(Where-Used)은 **JOIN**으로 풉니다(Day 2).
:::

### 4-3. 주의 ② 컬럼이 2개여도 오류 {keep}

:::error 컬럼이 2개여도 오류
```sql
SELECT p.part_no
     , (SELECT v.vendor_name, v.country
          FROM vendor v
         WHERE v.vendor_code = 'V1001')
  FROM part_master p
 LIMIT 1;
```

```error
ERROR:  subquery must return only one column
```

스칼라 서브쿼리는 **1행 1열**입니다. 컬럼이 두 개 필요하면 스칼라 서브쿼리를 두 개 쓰거나 JOIN을 씁니다.
:::

:::teacher 강사 확인
- `inventory`의 PK는 `(site_code, part_no, location)`입니다. 지금은 모든 재고가 창원(CW) 한 위치에만 있어 4-2가 오류 없이 실행되지만, 같은 부품이 두 창고에 있으면 스칼라 서브쿼리가 오류를 냅니다. 질문이 나오면 「`SUM(on_hand_qty)`로 감싸면 1행이 보장된다」로 답하세요(7장 복습 6번).
:::

### 4-4. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;`

:::try
**[복습]** (기존 복습문제 1번) `employees`에는 부서 번호만 있고, 부서 이름은 `departments`에 있습니다. 스칼라 서브쿼리로 부서 이름을 붙여, 급여가 7000~7500인 직원의 사번, 이름, 부서 번호, 급여, 부서 이름을 이름 순으로 출력하세요.

**[응용]** `departments`의 부서 번호 130 이하 부서마다 **직원 수**(`emp_cnt`)와 **최고 급여**(`max_sal`)를 스칼라 서브쿼리로 붙여 부서 번호 순으로 출력하세요. 직원이 없는 부서에서 두 값이 어떻게 다르게 나오는지 설명하세요.
:::

### 4-4. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
8행

```sql
SELECT a.employee_id
     , a.first_name
     , a.department_id
     , a.salary
     , (SELECT d.department_name
          FROM departments d
         WHERE d.department_id = a.department_id) AS department_name
  FROM employees a
 WHERE a.salary BETWEEN 7000 AND 7500
 ORDER BY a.first_name;
```

```result
| employee_id | first_name | department_id | salary | department_name |
| --- | --- | --- | --- | --- |
| 172 | Elizabeth | 80 | 7300.00 | Sales |
| 178 | Kimberely | NULL | 7000.00 | NULL |
| 160 | Louise | 80 | 7500.00 | Sales |
| 164 | Mattea | 80 | 7200.00 | Sales |
| 154 | Nanette | 80 | 7500.00 | Sales |
| 155 | Oliver | 80 | 7000.00 | Sales |
| 161 | Sarath | 80 | 7000.00 | Sales |
| 171 | William | 80 | 7400.00 | Sales |
```

부서가 없는 Kimberely도 행이 사라지지 않고 부서 이름이 NULL로 나옵니다(4-2).
:::

### 4-4. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
13행

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
 WHERE d.department_id <= 130
 ORDER BY d.department_id;
```

```result
| department_id | department_name | emp_cnt | max_sal |
| --- | --- | --- | --- |
| 10 | Administration | 1 | 4400.00 |
| 20 | Marketing | 2 | 13000.00 |
| 30 | Purchasing | 6 | 11000.00 |
| 40 | Human Resources | 1 | 6500.00 |
| 50 | Shipping | 45 | 8200.00 |
| 60 | IT | 5 | 9000.00 |
| 70 | Public Relations | 1 | 10000.00 |
| 80 | Sales | 34 | 14000.00 |
| 90 | Executive | 3 | 24000.00 |
| 100 | Finance | 6 | 12008.00 |
| 110 | Accounting | 2 | 12008.00 |
| 120 | Treasury | 0 | NULL |
| 130 | Corporate Tax | 0 | NULL |
```

직원이 없는 120·130 부서에서 `COUNT(*)`는 **0**, `MAX`는 **NULL**입니다. 대상 행이 하나도 없을 때 `COUNT`는 0을, 나머지 집계 함수는 NULL을 돌려줍니다.
:::

## 5. 인라인 뷰 — FROM절의 가상 테이블

### 5-1. 집계 결과를 테이블처럼 쓰기 {keep}

`FROM` 절에 쓰는 서브쿼리를 **인라인 뷰(inline view)** 라고 합니다. 서브쿼리의 결과표를 **임시 테이블처럼** 놓고, 다른 테이블과 JOIN하거나 그 컬럼으로 조건을 걸 수 있습니다.

**질문:** 소싱 품목이 5개 이상인 업체의 **이름**, 국내 여부, 품목 수, 최장 리드타임은?

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

### 5-1. 실행 결과 {keep}

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

- 괄호 안은 4단원 2-4의 「업체별 소싱 품목 수」 쿼리입니다. 그 결과표에 `s`라는 이름을 붙여 `vendor`와 JOIN했습니다.
- 4단원 3-1에서는 `HAVING COUNT(*) >= 5`로 걸렀던 조건을, 인라인 뷰 밖에서는 **일반 컬럼처럼** `WHERE s.item_cnt >= 5`로 씁니다. 인라인 뷰 안에서 만든 **별칭(`item_cnt`)은 바깥에서 컬럼 이름**이 됩니다.

> 인라인 뷰에는 `s`처럼 **별칭을 붙이는 습관**을 들이세요. PostgreSQL 16부터는 별칭을 생략해도 실행되지만, 별칭이 없으면 바깥에서 `s.item_cnt`처럼 어느 결과표의 컬럼인지 적을 수 없습니다.

### 5-2. 그룹의 최댓값 행 찾기 — 다중열 서브쿼리와 비교 {keep}

3-1의 「업체별 최고 단가 품목」을 인라인 뷰 + JOIN으로 풀 수도 있습니다. (기존 복습문제 2번과 같은 방식)

:::cols
```sql
SELECT s.vendor_code, s.part_no, s.po_price
  FROM part_sourcing s
  JOIN (SELECT vendor_code
             , MAX(po_price) AS max_price
          FROM part_sourcing
         WHERE currency = 'KRW'
         GROUP BY vendor_code) m
    ON m.vendor_code = s.vendor_code
   AND m.max_price   = s.po_price
 ORDER BY s.vendor_code;
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
:::

| | 다중열 서브쿼리 (3-1) | 인라인 뷰 + JOIN (5-2) |
| --- | --- | --- |
| 서브쿼리 위치 | `WHERE` | `FROM` |
| 결과 | 같음 (9행) | 같음 (9행) |
| 최고 단가 값을 SELECT에 | 쓸 수 없음 | `m.max_price`로 **쓸 수 있음** |

### 5-3. 먼저 JOIN하고 집계하면 ⭐ {keep}

**질문:** 모델별로 12월 생산계획 총수량과 BOM 행 수를 한 표로 보여 주세요.

4단원에서 냉장고 계획은 **3,460대**, BOM은 **39행**이었습니다(4단원 2-5, 2-6). 두 테이블을 먼저 JOIN하고 집계하면 어떻게 될까요?

:::cols
```sql
SELECT p.model_part_no
     , SUM(p.plan_qty) AS total_plan
     , COUNT(*)        AS bom_lines
  FROM production_plan p
  JOIN bom_structure b
    ON b.model_part_no = p.model_part_no
 GROUP BY p.model_part_no
 ORDER BY p.model_part_no;
```

```result
| model_part_no | total_plan | bom_lines |
| --- | --- | --- |
| TRF38316001 | 134940 | 390 |
| TWM61868701 | 194360 | 430 |
```
:::

오류는 없지만 **두 값 모두 틀렸습니다.** 냉장고의 계획 10행이 BOM 39행과 각각 짝지어져 **390행**이 되었고, 계획 수량이 39번씩 더해졌습니다(3,460 × 39 = 134,940).

### 5-3. 집계 먼저, 조인 나중 ⭐ {keep}

각 테이블을 **인라인 뷰에서 먼저 1행씩으로 집계**한 뒤 JOIN하면 맞는 값이 나옵니다.

:::cols
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
:::

==1 : N 관계의 두 테이블을 각각 합계 낼 때는, 집계를 먼저 하고 JOIN은 나중에== 합니다. 5단원 4-3 오류 상자에서 말로 본 「늘어난 행에 SUM」 문제를 숫자로 확인한 것입니다. Day 3 소요량·재료비 계산에서 숫자가 「몇 배로 부풀어」 나오면 이 문제부터 의심하세요.

### 5-4. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;`

:::try
**[복습]** (기존 복습문제 2번) 부서별 최고 급여를 구하는 인라인 뷰를 만들고, `employees`와 JOIN해 **부서별 최고 급여를 받는 직원**의 사번, 이름, 급여, 부서 번호를 부서 번호 순으로 출력하세요. 부서가 NULL인 직원은 제외합니다.

**[응용]** 부서마다 **자기 부서 평균 급여보다 많이 받는 직원 수**를 구하세요. 출력 컬럼은 부서 이름, 부서 평균 급여(`avg_sal`, 소수 첫째 자리 반올림), 직원 수(`above_cnt`)이고, 직원 수가 많은 순(같으면 부서 이름 순)으로 정렬합니다.
(힌트: 부서별 평균 급여 인라인 뷰 + `employees` + `departments` JOIN)
:::

### 5-4. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
11행

```sql
SELECT b.employee_id
     , b.first_name
     , b.salary
     , b.department_id
  FROM (SELECT department_id
             , MAX(salary) AS max_salary
          FROM employees
         WHERE department_id IS NOT NULL
         GROUP BY department_id) a
  JOIN employees b
    ON b.department_id = a.department_id
   AND b.salary        = a.max_salary
 ORDER BY b.department_id;
```

```result
| employee_id | first_name | salary | department_id |
| --- | --- | --- | --- |
| 200 | Jennifer | 4400.00 | 10 |
| 201 | Michael | 13000.00 | 20 |
| 114 | Den | 11000.00 | 30 |
| 203 | Susan | 6500.00 | 40 |
| 121 | Adam | 8200.00 | 50 |
| 103 | Alexander | 9000.00 | 60 |
| 204 | Hermann | 10000.00 | 70 |
| 145 | John | 14000.00 | 80 |
| 100 | Steven | 24000.00 | 90 |
| 108 | Nancy | 12008.00 | 100 |
| 205 | Shelley | 12008.00 | 110 |
```
:::

### 5-4. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
8행. 비교는 반올림하지 않은 평균(`a.avg_sal`)으로 하고, 반올림은 출력할 때만 합니다.

```sql
SELECT d.department_name
     , ROUND(a.avg_sal, 1) AS avg_sal
     , COUNT(*)            AS above_cnt
  FROM employees e
  JOIN (SELECT department_id
             , AVG(salary) AS avg_sal
          FROM employees
         GROUP BY department_id) a
    ON a.department_id = e.department_id
  JOIN departments d
    ON d.department_id = e.department_id
 WHERE e.salary > a.avg_sal
 GROUP BY d.department_name, a.avg_sal
 ORDER BY above_cnt DESC, d.department_name;
```

```result
| department_name | avg_sal | above_cnt |
| --- | --- | --- |
| Sales | 8955.9 | 17 |
| Shipping | 3475.6 | 13 |
| Finance | 8601.3 | 2 |
| IT | 5760.0 | 2 |
| Accounting | 10154.0 | 1 |
| Executive | 19333.3 | 1 |
| Marketing | 9500.0 | 1 |
| Purchasing | 4150.0 | 1 |
```

직원이 1명뿐인 부서(10, 40, 70)는 본인이 곧 평균이라 「평균보다 많은」 직원이 없어 결과에 나오지 않습니다.
:::

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

- 결과는 5-3과 **똑같습니다.** 바뀐 것은 **읽는 순서**뿐입니다. 위에서 아래로 「1단계 → 2단계 → 최종」으로 읽힙니다.
- 각 단계(`pl`, `bm`)는 따로 떼어 실행해 볼 수 있어, ==중간 결과를 확인하며 쿼리를 쌓아 올리기== 좋습니다.

### 6-1. 인라인 뷰와 WITH 비교 {keep}

| | 인라인 뷰 | WITH (CTE) |
| --- | --- | --- |
| 위치 | `FROM` 절 괄호 안 | 쿼리 맨 위 |
| 읽는 순서 | 안쪽 → 바깥쪽 | 위 → 아래 |
| 같은 결과를 두 번 쓰기 | 서브쿼리를 두 번 적어야 함 | 이름으로 여러 번 참조 |

> 다음 교시(재귀 CTE)에서는 `WITH RECURSIVE`로 **자기 자신을 다시 부르는** CTE를 만들어 BOM 트리를 레벨 끝까지 펼칩니다. 오늘 익힌 「`WITH 이름 AS (…)` 후 테이블처럼 쓰기」가 그 출발점입니다.

### 6-2. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;`

:::try
**[응용]** 5-4 [응용]의 부서별 평균 급여 인라인 뷰를 `WITH dept_avg AS (…)`로 꺼내 다시 작성하세요. 결과가 5-4와 같은지 확인합니다.
:::

### 6-2. 확인 문제 답 {keep}

:::answer [응용] 예시 답안
결과는 5-4 [응용]과 같은 8행입니다.

```sql
WITH dept_avg AS (
     SELECT department_id
          , AVG(salary) AS avg_sal
       FROM employees
      GROUP BY department_id
)
SELECT d.department_name
     , ROUND(a.avg_sal, 1) AS avg_sal
     , COUNT(*)            AS above_cnt
  FROM employees e
  JOIN dept_avg a
    ON a.department_id = e.department_id
  JOIN departments d
    ON d.department_id = e.department_id
 WHERE e.salary > a.avg_sal
 GROUP BY d.department_name, a.avg_sal
 ORDER BY above_cnt DESC, d.department_name;
```

```result
| department_name | avg_sal | above_cnt |
| --- | --- | --- |
| Sales | 8955.9 | 17 |
| Shipping | 3475.6 | 13 |
| Finance | 8601.3 | 2 |
| IT | 5760.0 | 2 |
| Accounting | 10154.0 | 1 |
| Executive | 19333.3 | 1 |
| Marketing | 9500.0 | 1 |
| Purchasing | 4150.0 | 1 |
```
:::

## 7. 복습 문제

### 7-0. 복습 문제 안내 {keep}

> 범위: 서브쿼리 전체(단일행 · 다중행 · 다중열 · 스칼라 · 인라인 뷰 · WITH). `bom` 스키마의 테이블로 풀어 주세요. (`SET search_path TO bom;` 출력 순서는 `ORDER BY` 기준)

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

**2.** 입고 예정(`scheduled_receipt`)이 있는 부품의 품번, 한글 품명, UIT를 품번 순으로 출력하세요. 본문 2-5에서는 `EXISTS`로 풀었습니다. 이번에는 `IN`으로 풀어 보세요.

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

**3.** 구매품(UIT가 G, D, X)인데 소싱 정보(`part_sourcing`)가 하나도 없는 부품을 찾으세요. [힌트: `NOT EXISTS` + 상관 서브쿼리]

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
- 6번은 **12월 총량**만 보면 90개가 남지만, 12/15 입고(1,600)는 계획 마지막 날(12/14) 이후이고 `receipt_type`도 Planned(계획 입고)입니다. 날짜별로 따져 보면 부족한 날이 생깁니다 — Day 3 7교시 MRP 결품 예측(Q11)에서 **결품 발생일**을 구합니다. 4-3 강사 확인처럼 `SUM`으로 감싸 두면 재고 행이 여러 개여도 스칼라 서브쿼리가 1행을 보장합니다.
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
Q. `WHERE lead_time_days > (SELECT lead_time_days FROM part_sourcing WHERE vendor_code = 'V1009')`가 오류 나는 이유와 고치는 방법은?
A. 서브쿼리가 4행을 돌려주는데 `>`는 값 하나와만 비교할 수 있기 때문입니다. 의도에 따라 `> ANY`(최솟값보다 큼) 또는 `> ALL`(최댓값보다 큼)이나 `MIN`/`MAX` 서브쿼리로 바꿉니다.

Q. 서브쿼리의 품번을 잘못 적어 0행이 되면 메인쿼리는 어떻게 되나요?
A. 서브쿼리 값이 NULL이 되어 비교가 참이 되지 않으므로, 오류 없이 결과가 0행으로 나옵니다.

Q. `department_id NOT IN (SELECT department_id FROM employees)`가 0행인 이유는?
A. 서브쿼리 결과에 NULL(부서 없는 직원)이 있어 `<> NULL`이 참이 될 수 없기 때문입니다. 서브쿼리에 `WHERE department_id IS NOT NULL`을 넣거나 `NOT EXISTS`로 씁니다.

Q. 업체별 최장 리드타임 품목을 `lead_time_days IN (SELECT MAX(…) … GROUP BY vendor_code)`로 구하면 무엇이 틀리나요?
A. 다른 업체의 최댓값과 우연히 같은 값도 걸려 행이 늘어납니다(35행 → 49행). `(vendor_code, lead_time_days) IN (…)`처럼 기준 컬럼과 짝으로 비교합니다.

Q. 생산계획과 BOM을 먼저 JOIN한 뒤 `SUM(plan_qty)`를 구하면 냉장고 계획이 134,940이 나옵니다. 원인과 해결 방법은?
A. 계획 10행이 BOM 39행과 각각 짝지어져 수량이 39번 더해졌기 때문입니다. 각 테이블을 인라인 뷰(또는 WITH)에서 먼저 모델별 1행으로 집계한 뒤 JOIN합니다.
:::
