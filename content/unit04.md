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
| 단일행 함수 | **1개** 행 | 행마다 결과 1개 | `ROUND(po_price, 0)` (반올림 — 1-2에서 씁니다) |
| **집계 함수** (다중행 함수) | **여러 개** 행 | 그룹마다 결과 **1개** | `COUNT`, `SUM`, `AVG`, `MAX`, `MIN` |

> 3단원에서 `WHERE`로 **행을 골랐다면**, 이번 단원은 고른 행을 **묶어서 세고, 더하고, 평균 내는** 방법입니다.
“UIT별로 부품이 몇 개인가?”, “업체별로 몇 품목을 사 오는가?”, “부서별 직원 수는 몇 명인가?” 같은 질문이 모두 집계입니다.

### 1-1. 집계 함수 다섯 가지 {keep}

```icons 집계 함수 다섯 가지
hash | COUNT() | 개수 | rose
plus | SUM() | 합계 | plum
equal | AVG() | 평균 | lime
trending-up | MAX() | 최댓값 | ivory
minus | MIN() | 최솟값 | hot
```

### 1-2. 테이블 전체를 하나의 그룹으로 {keep}

집계 함수를 쓰면서 `GROUP BY`를 쓰지 않으면 **테이블 전체(또는 WHERE로 남은 행 전체)가 하나의 그룹**이 됩니다. <br>그래서 결과는 항상 **1행**입니다.

```sql
SELECT COUNT(*)      AS 행수
     , SUM(po_price) AS 단가합계
     , MAX(po_price) AS 최고단가
     , MIN(po_price) AS 최저단가
     , AVG(po_price) AS 평균단가
  FROM part_sourcing
 WHERE currency = 'KRW';
```

```result
| 행수 | 단가합계 | 최고단가 | 최저단가 | 평균단가 |
| --- | --- | --- | --- | --- |
| 45 | 389215.00 | 61000.00 | 0.00 | 8845.7954545454545455 |
```

> 단가합계 ÷ 행수(45)를 직접 계산하면 평균단가와 다릅니다. 이유는 1-4에서 봅니다.

### 1-2. ROUND로 반올림 {keep}

`AVG`는 소수점 아래가 길게 나옵니다. **`ROUND(값, 자리수)`** 로 반올림합니다.

```sql
SELECT ROUND(AVG(po_price), 1) AS 평균단가
  FROM part_sourcing
 WHERE currency = 'KRW';
```

```result
| 평균단가 |
| --- |
| 8845.8 |
```

### 1-2. 생각해 보기 — 통화가 섞이면? {keep}

:::try 생각해 보기 — 통화가 섞이면?
`WHERE currency = 'KRW'`를 빼고 `SELECT SUM(po_price) FROM part_sourcing;`을 실행하면 `389342.90`이 나옵니다. 오류는 없지만, 이 숫자는 **원화 45행 + 달러 7행을 그냥 더한 값**이라 의미가 없습니다.
SQL은 단위를 검사해 주지 않습니다. ==합계·평균을 내기 전에 단위(통화, UOM)가 같은지 먼저 확인==하세요.
:::


### 1-3. COUNT의 세 가지 모양 ⭐ {keep}

| 쓰는 법 | 세는 것 |
| --- | --- |
| `COUNT(*)` | **행** 개수 (NULL이 있어도 셈) |
| `COUNT(컬럼)` | 그 컬럼 값이 **NULL이 아닌** 행 개수 |
| `COUNT(DISTINCT 컬럼)` | NULL이 아닌 값의 **종류** 개수 |

### 1-3. COUNT 세 가지를 한 번에 {keep}

```sql
SELECT COUNT(*)                 AS 전체행
     , COUNT(svc_code)          AS svc있음
     , COUNT(DISTINCT svc_code) AS svc종류
     , COUNT(DISTINCT uit)      AS uit종류
  FROM part_master;
```

```result
| 전체행 | svc있음 | svc종류 | uit종류 |
| --- | --- | --- | --- |
| 68 | 15 | 2 | 7 |
```

- 부품 68개 중 서비스 코드가 있는 부품은 15개, 서비스 코드 종류는 R·Z **2종**입니다.
- `uit종류 = 7`은 3단원 2-4에서 `SELECT DISTINCT uit`로 본 **7행**과 같은 값입니다.

### 1-4. 집계 함수는 NULL을 빼고 계산합니다 ⭐ {keep}

`V1010`(한성고무)의 소싱 5행 중 1행은 단가가 NULL입니다(3단원 3-3).

```sql
SELECT part_no, po_price
  FROM part_sourcing
 WHERE vendor_code = 'V1010'
 ORDER BY part_no;
```

```result
| part_no | po_price |
| --- | --- |
| MFT20558801 | 1100.00 |
| MFT43979901 | NULL |
| MGK25528301 | 4300.00 |
| MGK31172901 | 6900.00 |
| MHS18920401 | 1900.00 |
```

### 1-4. AVG는 무엇으로 나눌까? {keep}

```sql
SELECT COUNT(*)                 AS 전체행
     , COUNT(po_price)          AS 단가있음
     , SUM(po_price)            AS 합계
     , AVG(po_price)            AS 평균
     , SUM(po_price) / COUNT(*) AS 합계나누기전체
  FROM part_sourcing
 WHERE vendor_code = 'V1010';
```

```result
| 전체행 | 단가있음 | 합계 | 평균 | 합계나누기전체 |
| --- | --- | --- | --- | --- |
| 5 | 4 | 14200.00 | 3550.0000000000000000 | 2840.0000000000000000 |
```

- `AVG`는 **NULL이 아닌 4행**으로 나눕니다: 14200 ÷ 4 = **3550**
- `SUM / COUNT(*)`는 **5행**으로 나눕니다: 14200 ÷ 5 = **2840**
- 어느 쪽이 맞는지는 질문에 달려 있습니다. ==“단가를 모르는 부품을 빼고 평균”==이면 `AVG`, “모르는 것을 0원으로 보고 평균”이면 NULL을 0으로 바꿔 계산해야 합니다.

### 1-5. 집계 결과와 일반 컬럼은 함께 쓸 수 없습니다 {keep}

```sql
SELECT vendor_code, COUNT(*)
  FROM part_sourcing;
```

```result
ERROR:  column "part_sourcing.vendor_code" must appear in the GROUP BY clause or be used in an aggregate function
```

`COUNT(*)`는 테이블 전체에서 **1행**을 만들고, `vendor_code`는 **52행**이 있습니다.
행 개수가 맞지 않아 한 결과표에 담을 수 없습니다.
오류 메시지가 해결 방법도 알려 줍니다. → `vendor_code`를 **GROUP BY에 넣으라**는 뜻입니다.

### 1-6. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마)

:::try
**[복습]** `employees` 전체 직원의 직원 수, 급여 합계, 최고 급여, 최저 급여, 평균 급여를 구하세요. 별칭은 `emp_cnt`, `sal_sum`, `max_sal`, `min_sal`, `avg_sal`이고, 평균은 소수 둘째 자리까지 반올림합니다.

**[응용]** 아래 쿼리를 실행하고, 다섯 개의 숫자가 각각 무엇을 센 것인지 설명하세요. (같은 숫자가 나와도 빠진 행은 다를 수 있습니다.)

```sql
SELECT COUNT(*)                      AS 전체
     , COUNT(commission_pct)         AS 커미션
     , COUNT(department_id)          AS 부서있음
     , COUNT(DISTINCT department_id) AS 부서종류
     , COUNT(manager_id)             AS 상사있음
  FROM employees;
```
:::

### 1-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
```sql
SELECT COUNT(*)              AS emp_cnt
     , SUM(salary)           AS sal_sum
     , MAX(salary)           AS max_sal
     , MIN(salary)           AS min_sal
     , ROUND(AVG(salary), 2) AS avg_sal
  FROM employees;
```

```result
| emp_cnt | sal_sum | max_sal | min_sal | avg_sal |
| --- | --- | --- | --- | --- |
| 107 | 691416.00 | 24000.00 | 2100.00 | 6461.83 |
```
:::

### 1-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
```result
| 전체 | 커미션 | 부서있음 | 부서종류 | 상사있음 |
| --- | --- | --- | --- | --- |
| 107 | 35 | 106 | 11 | 106 |
```

- `COUNT(*)` = 107: 행 전체
- `COUNT(commission_pct)` = 35: 커미션이 있는(NULL이 아닌) 직원만
- `COUNT(department_id)` = 106: 부서가 없는 직원 1명(178 Kimberely Grant) 제외
- `COUNT(DISTINCT department_id)` = 11: 직원이 실제로 있는 부서의 종류
- `COUNT(manager_id)` = 106: 상사가 없는 직원 1명(100 Steven King, 사장) 제외
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

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

1. 질문에서 **“~별”** 을 찾습니다. → 그 컬럼이 `GROUP BY` 기준입니다. (“UIT**별** 부품 수” → `GROUP BY uit`)
2. 그룹마다 구할 값을 **집계 함수**로 씁니다. (“부품 **수**” → `COUNT(*)`)
3. `SELECT`에는 **GROUP BY 기준 컬럼**과 **집계 함수**만 씁니다.

:::teacher 강사 확인
- 위 세 단계는 기존 교안 「GROUP BY 프로세스」에 해당합니다.
:::

### 2-1. 실행 순서 따라가기 {keep}

```stepper
{
  "title": "국가별 업체 수 — 실제 실행 순서",
  "code": "SELECT country, COUNT(*) AS vendor_cnt\n  FROM vendor\n GROUP BY country\n ORDER BY vendor_cnt DESC, country;",
  "steps": [
    {"line": 1, "note": "① FROM — vendor 테이블 12행을 모두 가져옵니다. (이 쿼리에는 WHERE·HAVING이 없어 ②·④는 건너뜁니다.)",
     "cols": ["vendor_code", "vendor_name", "country"],
     "rows": [["V1001","한빛정밀(주)","KR"],["V1002","대양화학(주)","KR"],["V1003","세진전자(주)","KR"],["V1004","AsiaComp Co., Ltd.","CN"],["V1005","NanoChip Semiconductor","TW"],["V1006","우성사출(주)","KR"],["V1007","Global Steel Trading","JP"],["V1008","동아포장(주)","KR"],["V1009","Pacific Motor Parts","VN"],["V1010","한성고무(주)","KR"],["V1011","태양전장(주)","KR"],["V1012","LG 사내 부품라인(C1)","KR"]]},
    {"line": 2, "note": "③ GROUP BY — country가 같은 행끼리 모읍니다. 12행이 CN·JP·KR·TW·VN 5개 그룹이 됩니다.",
     "cols": ["country", "vendor_code", "vendor_name"],
     "rows": [["CN","V1004","AsiaComp Co., Ltd."],["JP","V1007","Global Steel Trading"],["KR","V1001","한빛정밀(주)"],["KR","V1002","대양화학(주)"],["KR","V1003","세진전자(주)"],["KR","V1006","우성사출(주)"],["KR","V1008","동아포장(주)"],["KR","V1010","한성고무(주)"],["KR","V1011","태양전장(주)"],["KR","V1012","LG 사내 부품라인(C1)"],["TW","V1005","NanoChip Semiconductor"],["VN","V1009","Pacific Motor Parts"]], "hot": ["country"]},
    {"line": 0, "note": "⑤ SELECT — 그룹마다 1행. 기준 컬럼 country와 COUNT(*)만 남습니다. vendor_name은 그룹 안에 여러 개라 쓸 수 없습니다.",
     "cols": ["country", "vendor_cnt"],
     "rows": [["CN",1],["JP",1],["KR",8],["TW",1],["VN",1]], "hot": ["vendor_cnt"]},
    {"line": 3, "note": "⑥ ORDER BY — SELECT 다음이므로 별칭 vendor_cnt로 정렬할 수 있습니다.",
     "cols": ["country", "vendor_cnt"],
     "rows": [["KR",8],["CN",1],["JP",1],["TW",1],["VN",1]], "hot": ["vendor_cnt"]}
  ]
}
```

### 2-2. UIT별 부품 수 {keep}

:::cols
```sql
SELECT uit
     , COUNT(*) AS part_cnt
  FROM part_master
 GROUP BY uit
 ORDER BY part_cnt DESC, uit;
```

```result
| uit | part_cnt |
| --- | --- |
| G | 41 |
| P | 8 |
| D | 7 |
| T | 6 |
| F | 2 |
| S | 2 |
| X | 2 |
```
:::

- 68행 → 7개 그룹. 각 그룹이 **1행**이 됩니다.
- `ORDER BY`는 `SELECT` 다음에 실행되므로 **별칭 `part_cnt`로 정렬**할 수 있습니다(3단원 3-1).
- 부품의 60%가 G(국내 구매품)입니다. `code_uit`를 함께 보면서 “우리 BOM은 대부분 사 오는 부품”이라고 읽어 보세요.

### 2-2. DISTINCT와 GROUP BY {keep}

> `GROUP BY uit`에 집계 함수를 쓰지 않으면 `SELECT DISTINCT uit`와 같은 결과(7행)가 나옵니다.
**종류만** 볼 때는 `DISTINCT`, **종류별 개수·합계**까지 볼 때는 `GROUP BY`를 씁니다.

```compare DISTINCT와 GROUP BY
list | SELECT DISTINCT uit || layers | SELECT uit, COUNT(*) … GROUP BY uit
shapes | 종류만 (7행) || hash | 종류별 개수 (7행 + part_cnt)
```

### 2-3. Status별 부품 수 {keep}

:::cols
```sql
SELECT status_code
     , COUNT(*) AS part_cnt
  FROM part_master
 GROUP BY status_code
 ORDER BY status_code;
```

```result
| status_code | part_cnt |
| --- | --- |
| 1 | 1 |
| 3 | 67 |
```
:::

- `code_status`에는 1~6까지 6개 코드가 있지만, 부품 마스터에는 **1(폐기)과 3(승인·양산) 두 가지만** 쓰입니다.
- 폐기(1) 상태인 부품 1개는 `MHG51215701`(도어 힌지(구형))입니다.

:::teacher 강사 확인
- `MHG51215701`은 README 4장의 이상 데이터 **A2**(폐기 상태인데 냉장고 캐비닛 BOM에 잔존)입니다. BOM에 남아 있는지는 `bom_structure`와 JOIN해야 확인할 수 있으므로 Day 2(Q6)로 넘기고, 여기서는 “폐기 부품이 1개 있다”까지만 보여 주세요.
:::

### 2-4. 업체별 소싱 품목 수 {keep}

:::cols
```sql
SELECT vendor_code
     , COUNT(*) AS item_cnt
  FROM part_sourcing
 GROUP BY vendor_code
 ORDER BY item_cnt DESC, vendor_code;
```

```result 12행
| vendor_code | item_cnt |
| --- | --- |
| V1001 | 9 |
| V1011 | 8 |
| V1003 | 6 |
| V1006 | 6 |
| V1008 | 6 |
| V1010 | 5 |
| V1009 | 4 |
| V1002 | 3 |
| V1007 | 2 |
| V1004 | 1 |
| V1005 | 1 |
| V1012 | 1 |
```
:::

- 1-5에서 오류가 났던 쿼리에 `GROUP BY vendor_code` 한 줄을 붙인 것입니다.
- 업체 이름은 `vendor` 테이블에 있습니다. 코드와 이름을 함께 보려면 **JOIN**이 필요합니다.

### 2-5. 그룹마다 여러 집계 — 라인별 생산 계획 {keep}

```sql
SELECT line_code
     , COUNT(*)                AS 계획일수
     , SUM(plan_qty)           AS 총계획수량
     , ROUND(AVG(plan_qty), 1) AS 일평균
     , MAX(plan_qty)           AS 최대
     , MIN(plan_qty)           AS 최소
  FROM production_plan
 GROUP BY line_code
 ORDER BY line_code;
```

```result
| line_code | 계획일수 | 총계획수량 | 일평균 | 최대 | 최소 |
| --- | --- | --- | --- | --- | --- |
| LINE-A | 10 | 4520 | 452.0 | 480 | 420 |
| LINE-B | 10 | 3460 | 346.0 | 380 | 320 |
```

> LINE-A(세탁기)는 12월 평일 10일 동안 4,520대, LINE-B(냉장고)는 3,460대를 만들 계획입니다.

### 2-6. 여러 컬럼으로 묶기 {keep}

`GROUP BY` 뒤에 컬럼이 여러 개면, 그 **조합**마다 그룹이 만들어집니다. (`DISTINCT` 여러 컬럼과 같은 원리)

:::cols
```sql
SELECT model_part_no
     , bom_level
     , COUNT(*) AS line_cnt
  FROM bom_structure
 GROUP BY model_part_no, bom_level
 ORDER BY model_part_no, bom_level;
```

```result
| model_part_no | bom_level | line_cnt |
| --- | --- | --- |
| TRF38316001 | 1 | 13 |
| TRF38316001 | 2 | 22 |
| TRF38316001 | 3 | 4 |
| TWM61868701 | 1 | 17 |
| TWM61868701 | 2 | 20 |
| TWM61868701 | 3 | 6 |
```
:::

- 냉장고(`TRF38316001`) BOM 39행, 세탁기(`TWM61868701`) BOM 43행이 레벨별로 나뉘었습니다.
- 두 모델 모두 **3레벨**까지 있습니다. 이 레벨을 따라 내려가며 전개하는 방법(재귀 CTE)은 Day 3에서 배웁니다.

### 2-7. NULL도 하나의 그룹이 됩니다 {keep}

:::cols
```sql
SELECT svc_code
     , COUNT(*)        AS part_cnt
     , COUNT(svc_code) AS svc_cnt
  FROM part_master
 GROUP BY svc_code
 ORDER BY svc_code;
```

```result
| svc_code | part_cnt | svc_cnt |
| --- | --- | --- |
| R | 9 | 9 |
| Z | 6 | 6 |
| NULL | 53 | 0 |
```
:::

- `WHERE`에서는 `= NULL`로 비교가 안 됐지만(3단원 5-1), `GROUP BY`에서는 NULL끼리 **한 그룹**으로 묶입니다.
- 같은 NULL 그룹인데 `COUNT(*)`는 53, `COUNT(svc_code)`는 0입니다(1-3).
- NULL 그룹을 빼고 싶으면 그룹을 만들기 **전에** `WHERE svc_code IS NOT NULL`로 행을 거릅니다.

### 2-8. CASE로 만든 라벨로 묶기 — 국내/해외 업체 {keep}

3단원 6-3에서 만든 국내/해외 라벨로 묶습니다.

:::cols
```sql
SELECT CASE WHEN is_domestic = 'Y' THEN '국내' ELSE '해외' END AS 구분
     , COUNT(*) AS 업체수
  FROM vendor
 GROUP BY 구분
 ORDER BY 업체수 DESC;
```

```result
| 구분 | 업체수 |
| --- | --- |
| 국내 | 8 |
| 해외 | 4 |
```
:::

> PostgreSQL은 `GROUP BY`에 **SELECT의 별칭**(`구분`)을 쓸 수 있습니다.
별칭 대신 `GROUP BY CASE WHEN is_domestic = 'Y' THEN '국내' ELSE '해외' END`처럼 식을 그대로 써도 결과는 같습니다.

### 2-8. 비율을 한 줄로 {keep}

`CASE`로 1/0을 만들고 `SUM`으로 더하면 조건에 맞는 행 수가 됩니다.

```sql
SELECT COUNT(*) AS 전체
     , SUM(CASE WHEN is_domestic = 'Y' THEN 1 ELSE 0 END) AS 국내
     , ROUND(SUM(CASE WHEN is_domestic = 'Y' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS 국내비율
     , ROUND(SUM(CASE WHEN is_domestic = 'N' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS 해외비율
  FROM vendor;
```

```result
| 전체 | 국내 | 국내비율 | 해외비율 |
| --- | --- | --- | --- |
| 12 | 8 | 66.7 | 33.3 |
```

### 2-8. 비율이 66으로 나온다면 {keep}

:::error 비율이 66으로 나온다면 — 정수 ÷ 정수
`… * 100 / COUNT(*)`처럼 `100`(정수)을 쓰면 결과가 `66`(몫)만 나옵니다. 3단원 2-5에서 본 것처럼 ==`100.0`으로 소수를 섞어야== `66.7`이 나옵니다.

```sql
SELECT SUM(CASE WHEN is_domestic = 'Y' THEN 1 ELSE 0 END) * 100 / COUNT(*) AS ratio
  FROM vendor;
```

```result
| ratio |
| --- |
| 66 |
```
:::

### 2-8. Make / Buy 비중 {keep}

3단원 6-1의 라벨로도 묶을 수 있습니다.

:::cols
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

### 2-9. GROUP BY를 쓸 때 주의할 점 {keep}

:::error SELECT에는 GROUP BY 기준 컬럼과 집계 함수만
`GROUP BY uit`로 묶으면 그룹(UIT)마다 **1행**만 남습니다. 그런데 `description_kr`은 그룹 안에 값이 여러 개라 어느 것을 보여 줄지 정할 수 없습니다.

```sql
SELECT uit, description_kr, COUNT(*)
  FROM part_master
 GROUP BY uit;
```

```result
ERROR:  column "part_master.description_kr" must appear in the GROUP BY clause or be used in an aggregate function
```

==GROUP BY를 쓰는 순간 출력되는 행의 개수가 줄어들기 때문에== GROUP BY보다 늦게 실행되는 절(HAVING, SELECT, ORDER BY)에서는 쓸 수 있는 컬럼이 제한됩니다. 대신 **집계 함수로 처리한 컬럼은** 쓸 수 있습니다(`MAX(description_kr)` 등).
:::

### 2-10. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마)

:::try
**[복습]** 부서별 최고 급여와 최저 급여를 구하세요. 별칭은 `max_sal`, `min_sal`이고, 부서가 NULL인 직원은 제외하며, 부서 순으로 정렬합니다.

**[응용]** 부서 50·80에 대해 **부서별·직책별** 직원 수와 급여 합계를 구하세요. 별칭은 `emp_cnt`, `sal_sum`이고, 부서 → 직책 순으로 정렬합니다.
결과에서 `SA_REP` 직원 수를 확인한 뒤, 1-6 확인 문제 [응용]의 `COUNT(department_id)` 결과와 연결해 설명해 보세요. (힌트: 전체 `SA_REP`는 30명입니다.)
:::

### 2-10. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
11행. `WHERE`를 빼면 부서 NULL 그룹(7000 / 7000)이 하나 더 생겨 12행이 됩니다(2-7).

```sql
SELECT department_id
     , MAX(salary) AS max_sal
     , MIN(salary) AS min_sal
  FROM employees
 WHERE department_id IS NOT NULL
 GROUP BY department_id
 ORDER BY department_id;
```

```result
| department_id | max_sal | min_sal |
| --- | --- | --- |
| 10 | 4400.00 | 4400.00 |
| 20 | 13000.00 | 6000.00 |
| 30 | 11000.00 | 2500.00 |
| 40 | 6500.00 | 6500.00 |
| 50 | 8200.00 | 2100.00 |
| 60 | 9000.00 | 4200.00 |
| 70 | 10000.00 | 10000.00 |
| 80 | 14000.00 | 6100.00 |
| 90 | 24000.00 | 17000.00 |
| 100 | 12008.00 | 6900.00 |
| 110 | 12008.00 | 8300.00 |
```
:::

### 2-10. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
5행

```sql
SELECT department_id
     , job_id
     , COUNT(*)    AS emp_cnt
     , SUM(salary) AS sal_sum
  FROM employees
 WHERE department_id IN (50, 80)
 GROUP BY department_id, job_id
 ORDER BY department_id, job_id;
```

```result
| department_id | job_id | emp_cnt | sal_sum |
| --- | --- | --- | --- |
| 50 | SH_CLERK | 20 | 64300.00 |
| 50 | ST_CLERK | 20 | 55700.00 |
| 50 | ST_MAN | 5 | 36400.00 |
| 80 | SA_MAN | 5 | 61000.00 |
| 80 | SA_REP | 29 | 243500.00 |
```

`SA_REP`는 전체 30명인데 부서 80에는 **29명**입니다. 부서가 NULL인 `SA_REP` 1명(178 Kimberely Grant)이 `WHERE department_id IN (50, 80)`에서 빠졌기 때문입니다.
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

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
  "title": "업체가 2곳 이상인 국가 — 실제 실행 순서",
  "code": "SELECT country, COUNT(*) AS vendor_cnt\n  FROM vendor\n GROUP BY country\nHAVING COUNT(*) >= 2\n ORDER BY vendor_cnt DESC;",
  "steps": [
    {"line": 1, "note": "① FROM — vendor 테이블 12행을 모두 가져옵니다. (이 쿼리에는 WHERE가 없어 ②는 건너뜁니다.)",
     "cols": ["vendor_code", "vendor_name", "country"],
     "rows": [["V1001","한빛정밀(주)","KR"],["V1002","대양화학(주)","KR"],["V1003","세진전자(주)","KR"],["V1004","AsiaComp Co., Ltd.","CN"],["V1005","NanoChip Semiconductor","TW"],["V1006","우성사출(주)","KR"],["V1007","Global Steel Trading","JP"],["V1008","동아포장(주)","KR"],["V1009","Pacific Motor Parts","VN"],["V1010","한성고무(주)","KR"],["V1011","태양전장(주)","KR"],["V1012","LG 사내 부품라인(C1)","KR"]]},
    {"line": 2, "note": "③ GROUP BY — country별로 묶어 5개 그룹을 만듭니다. 그룹마다 COUNT(*)를 셀 수 있게 됩니다.",
     "cols": ["country", "COUNT(*)"],
     "rows": [["CN",1],["JP",1],["KR",8],["TW",1],["VN",1]], "hot": ["country"]},
    {"line": 3, "note": "④ HAVING — 그룹 단위로 조건을 검사합니다. COUNT(*) >= 2가 아닌 4개 그룹이 탈락합니다.", "dim": [0,1,3,4], "hot": ["COUNT(*)"]},
    {"line": 0, "note": "⑤ SELECT — 남은 그룹에서 country와 COUNT(*)를 꺼내고 별칭 vendor_cnt를 붙입니다.",
     "cols": ["country", "vendor_cnt"],
     "rows": [["KR",8]], "hot": ["vendor_cnt"]},
    {"line": 4, "note": "⑥ ORDER BY — 마지막으로 정렬합니다. (남은 그룹이 1개라 순서는 그대로)",
     "cols": ["country", "vendor_cnt"],
     "rows": [["KR",8]]}
  ]
}
```

### 3-1. 소싱 품목이 5개 이상인 업체 {keep}

**질문:** 소싱 품목이 **5개 이상**인 업체는?

:::cols
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

- 2-4의 12개 그룹 중 조건에 맞는 **6개 그룹만** 남았습니다.

### 3-2. WHERE에는 집계 함수를 쓸 수 없습니다 ⭐ {keep}

```sql
SELECT vendor_code, COUNT(*)
  FROM part_sourcing
 WHERE COUNT(*) >= 5
 GROUP BY vendor_code;
```

```result
ERROR:  aggregate functions are not allowed in WHERE
```

`WHERE`(②)는 `GROUP BY`(③)보다 **먼저 실행**됩니다. `WHERE`를 실행하는 시점에는 아직 그룹이 없어서 `COUNT(*)`를 계산할 수 없습니다. ==그룹에 대한 조건은 HAVING==에 씁니다.

### 3-2. 왜 안 되는지 따라가기 {keep}

```stepper
{
  "title": "WHERE COUNT(*) — 어디서 막힐까?",
  "code": "SELECT country, COUNT(*)\n  FROM vendor\n WHERE COUNT(*) >= 2\n GROUP BY country;",
  "steps": [
    {"line": 1, "note": "① FROM — vendor 테이블 12행을 가져옵니다.",
     "cols": ["vendor_code", "vendor_name", "country"],
     "rows": [["V1001","한빛정밀(주)","KR"],["V1002","대양화학(주)","KR"],["V1003","세진전자(주)","KR"],["V1004","AsiaComp Co., Ltd.","CN"],["V1005","NanoChip Semiconductor","TW"],["V1006","우성사출(주)","KR"],["V1007","Global Steel Trading","JP"],["V1008","동아포장(주)","KR"],["V1009","Pacific Motor Parts","VN"],["V1010","한성고무(주)","KR"],["V1011","태양전장(주)","KR"],["V1012","LG 사내 부품라인(C1)","KR"]]},
    {"line": 2, "note": "② WHERE — 행을 한 줄씩 검사하는 단계입니다. 아직 묶이지 않았으니 「몇 개인지」 셀 그룹이 없습니다. → ERROR: aggregate functions are not allowed in WHERE (실제로는 실행 전에 걸러집니다. 순서로 이해하기 위한 그림입니다.)", "hot": ["country"]},
    {"line": 3, "note": "③ GROUP BY — 그룹은 여기서야 만들어집니다. 그래서 그룹 조건은 GROUP BY 다음의 HAVING에 써야 합니다.",
     "cols": ["country", "COUNT(*)"],
     "rows": [["CN",1],["JP",1],["KR",8],["TW",1],["VN",1]], "hot": ["COUNT(*)"]}
  ]
}
```

### 3-3. HAVING에서는 별칭을 못 씁니다 {keep}

```sql
SELECT vendor_code, COUNT(*) AS item_cnt
  FROM part_sourcing
 GROUP BY vendor_code
HAVING item_cnt >= 5;
```

```result
ERROR:  column "item_cnt" does not exist
```

`HAVING`(④)은 `SELECT`(⑤)보다 먼저 실행되므로, 별칭 `item_cnt`가 아직 없습니다. `HAVING COUNT(*) >= 5`처럼 집계 함수를 다시 씁니다. 반대로 `ORDER BY`(⑥)에서는 별칭을 쓸 수 있습니다.


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

**질문:** 업체별 평균 단가가 10,000 이상인 업체는?

:::cols
```sql HAVING만
SELECT vendor_code
     , COUNT(*)                AS item_cnt
     , ROUND(AVG(po_price), 0) AS avg_price
  FROM part_sourcing
 GROUP BY vendor_code
HAVING AVG(po_price) >= 10000
 ORDER BY avg_price DESC;
```

```sql WHERE + HAVING
SELECT vendor_code
     , COUNT(*)                AS item_cnt
     , ROUND(AVG(po_price), 0) AS avg_price
  FROM part_sourcing
 WHERE currency = 'KRW'
 GROUP BY vendor_code
HAVING AVG(po_price) >= 10000
 ORDER BY avg_price DESC;
```
:::

:::cols
```result HAVING만 (2행)
| vendor_code | item_cnt | avg_price |
| --- | --- | --- |
| V1003 | 6 | 15151 |
| V1001 | 9 | 12159 |
```

```result WHERE + HAVING (3행)
| vendor_code | item_cnt | avg_price |
| --- | --- | --- |
| V1009 | 1 | 28000 |
| V1003 | 6 | 15151 |
| V1001 | 9 | 12159 |
```
:::

### 3-4. V1009가 새로 나타난 이유 {keep}

- 1-2에서 본 것처럼 단가에는 **원화와 달러가 섞여** 있습니다. 오른쪽 쿼리는 원화 소싱만 남긴 뒤(`WHERE`) 묶었습니다.
- `V1009`(Pacific Motor Parts)의 소싱 4행은 **달러 3행 + 원화 1행**입니다.
- `WHERE` 없이 묶으면 달러 단가(작은 숫자)와 원화 단가가 섞여 평균이 낮아졌고, `WHERE`로 원화만 남기니 평균이 28,000이 되었습니다.

| | WHERE | HAVING |
| --- | --- | --- |
| 거르는 대상 | **행** | **그룹** |
| 실행 시점 | GROUP BY **전** | GROUP BY **후** |
| 집계 함수 | 쓸 수 없음 | 씀 |
| 이 예제에서 | 원화 행만 남김 | 평균 10,000 이상 업체만 남김 |

> ==WHERE는 일반 조건으로 행을 고르고, HAVING은 묶은 뒤 집계 함수 조건으로 그룹을 고릅니다.==

### 3-5. HAVING으로 데이터 점검하기 {keep}

`HAVING COUNT(*) >= 2`는 “**같은 값이 두 번 이상 나오는 것**”을 찾는 패턴입니다. 중복 의심, 공용 부품 찾기에 자주 씁니다.

**① 한글 품명이 같은 부품**

:::cols
```sql
SELECT description_kr
     , COUNT(*) AS cnt
  FROM part_master
 GROUP BY description_kr
HAVING COUNT(*) >= 2
 ORDER BY description_kr;
```

```result 8행
| description_kr | cnt |
| --- | --- |
| 도어 가스켓 | 2 |
| 메인 PCB 조립체 | 2 |
| 와이어 하네스 | 2 |
| 완충재 | 2 |
| 외함 캐비닛 | 2 |
| 카톤 박스 | 2 |
| 캐비닛 조립체 | 2 |
| 포장 조립체 | 2 |
```
:::

> 이름이 같아도 **품번(PK)이 다르면 다른 부품**입니다. 예를 들어 「도어 가스켓」은 `MGK25528301`, `MGK31172901` 두 품번입니다. 이름만으로 부품을 찾으면 엉뚱한 부품을 가져올 수 있으므로, ==조회와 기록은 항상 품번으로== 합니다.

### 3-5. ② 두 모델에 모두 쓰이는 공용 부품 {keep}

냉장고·세탁기 **두 모델에 모두** 쓰이는 부품을 찾습니다.

:::cols
```sql
SELECT child_part_no
     , COUNT(*)                      AS used_cnt
     , COUNT(DISTINCT model_part_no) AS model_cnt
  FROM bom_structure
 GROUP BY child_part_no
HAVING COUNT(DISTINCT model_part_no) = 2
 ORDER BY used_cnt DESC, child_part_no;
```

```result 11행
| child_part_no | used_cnt | model_cnt |
| --- | --- | --- |
| FSC67181101 | 3 | 2 |
| FTP68745401 | 3 | 2 |
| RRS44997401 | 3 | 2 |
| EAE71986301 | 2 | 2 |
| EIC93178801 | 2 | 2 |
| EPB98715501 | 2 | 2 |
| ERS64202801 | 2 | 2 |
| MFL37467701 | 2 | 2 |
| RPP53183301 | 2 | 2 |
| RST13919601 | 2 | 2 |
| SAA76541601 | 2 | 2 |
```
:::

### 3-5. used_cnt와 model_cnt 읽기 {keep}

- `used_cnt`(`COUNT(*)`)는 **BOM 행 수**, `model_cnt`(`COUNT(DISTINCT model_part_no)`)는 **쓰이는 모델 종류 수**입니다. HAVING은 모델 종류 수(`COUNT(DISTINCT model_part_no)`)로 걸렀기 때문에 `used_cnt`가 3인 부품도 나옵니다.
- `used_cnt`가 3이면 한 모델 안에서 **서로 다른 상위 조립품**에 두 번 쓰인 것입니다. 예를 들어 아래 두 부품이 그렇습니다.
  - `FTP68745401`(필라멘트 테이프): 냉장고의 냉동 사이클 조립체·포장 조립체 + 세탁기의 포장 조립체
  - `RRS44997401`(ABS 수지): 냉장고의 핸들 조립체·내상 라이너 + 세탁기의 도어 조립체
- `HAVING`에 쓰는 집계 함수는 `SELECT`에 꼭 출력하지 않아도 됩니다. 여기서는 읽기 쉽게 `model_cnt`로 함께 출력했습니다.
- 공용 부품은 재고가 부족하면 ==LINE-A·LINE-B 두 라인에 모두 영향==을 줍니다. Day 2 Where-Used(역전개)에서 이 부품이 어느 상위 조립품에 쓰이는지 JOIN으로 확인합니다.

### 3-6. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마)

:::try
**[복습]** 직책(`job_id`)별 직원 수를 구하되, 직원 수가 **10명 이상**인 직책만 출력하세요. 별칭은 `emp_cnt`이고, 직원 수가 많은 순(같으면 직책 순)으로 정렬합니다.

**[응용]** 사장 직책(`AD_PRES`)을 **제외**한 직책별 평균 급여를 구하고, 평균 급여가 **10000 이상**인 직책만 평균 급여가 높은 순(같으면 직책 순)으로 출력하세요. 평균 급여는 소수 첫째 자리까지 반올림하고 별칭은 `avg_sal`입니다.
`AD_PRES` 제외 조건은 `WHERE`와 `HAVING` 중 어디에 쓰는 것이 맞을까요?
:::

### 3-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
3행

```sql
SELECT job_id
     , COUNT(*) AS emp_cnt
  FROM employees
 GROUP BY job_id
HAVING COUNT(*) >= 10
 ORDER BY emp_cnt DESC, job_id;
```

```result
| job_id | emp_cnt |
| --- | --- |
| SA_REP | 30 |
| SH_CLERK | 20 |
| ST_CLERK | 20 |
```
:::

### 3-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
7행. `AD_PRES` 제외는 집계와 상관없는 **행 조건**이므로 `WHERE`에 씁니다. 묶기 전에 걸러 두면 불필요한 그룹을 만들지 않습니다. (`WHERE`를 빼면 `AD_PRES 24000.0`이 맨 위에 붙어 8행이 됩니다.)

```sql
SELECT job_id
     , ROUND(AVG(salary), 1) AS avg_sal
  FROM employees
 WHERE job_id <> 'AD_PRES'
 GROUP BY job_id
HAVING AVG(salary) >= 10000
 ORDER BY avg_sal DESC, job_id;
```

```result
| job_id | avg_sal |
| --- | --- |
| AD_VP | 17000.0 |
| MK_MAN | 13000.0 |
| SA_MAN | 12200.0 |
| AC_MGR | 12008.0 |
| FI_MGR | 12008.0 |
| PU_MAN | 11000.0 |
| PR_REP | 10000.0 |
```
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

## 4. 복습 문제

### 4-0. 복습 문제 안내 {keep}

> 범위: 집계 함수 · GROUP BY · HAVING · ORDER BY 전체. `bom` 스키마의 테이블로 풀어 주세요. (`SET search_path TO bom;` 출력 순서는 `ORDER BY` 기준)

```icons 여섯 문항
layers | 1 · GROUP BY | 대분류별 부품 수 | rose
list-checks | 2 · HAVING | 2개 이상인 단위(UOM) | plum
truck | 3 · GROUP BY | 공급 방식별 BOM 행 수 | lime
clock | 4 · 여러 집계 | 구매 속성별 리드타임 | ivory
wallet | 5 · (심화) WHERE + HAVING | 원화 최소 발주 금액 | plum
calendar | 6 · (심화) 식으로 묶기 | 등록월별 부품 수 | hot
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

### 4-4. 복습 1 · 2 답 {keep}

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

### 4-5. 복습 3 · 4 답 {keep}

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

- 4번 결과의 의미: line_type `I`(Import, UIT D와 짝)의 평균 리드타임이 42.9일로 국내(`D`) 12.7일의 3배가 넘습니다. 3단원 4-4에서 본 「해외에서 오래 걸려 들어오는 부품」을 숫자로 확인한 것입니다.
:::

### 4-6. 복습 5 · 6 답 {keep}

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

- 5번에서 `WHERE currency = 'KRW'`를 빼면 달러 금액이 원화와 섞여 합계가 틀어집니다(1-2 생각해 보기).
- 6번은 `GROUP BY reg_month`처럼 별칭으로 묶어도 PostgreSQL에서는 같은 결과가 나옵니다(2-8).
:::

:::teacher 강사 확인
- 6번은 기존 HR 복습 문제 「연도별 입사자 수」와 같은 유형입니다.
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
- **단위 주의**: 통화·UOM이 섞인 상태로 `SUM`·`AVG`를 내면 오류 없이 틀린 숫자가 나옵니다.
:::

### 5-2. 확인 문제

:::quiz
Q. `SELECT vendor_code, COUNT(*) FROM part_sourcing;`이 오류가 나는 이유와 고치는 방법은?
A. `COUNT(*)`는 전체를 1행으로 만들고 `vendor_code`는 52행이라 함께 출력할 수 없습니다. `GROUP BY vendor_code`를 붙여 업체별로 묶습니다.

Q. 단가가 NULL인 행이 섞여 있을 때 `AVG(po_price)`와 `SUM(po_price) / COUNT(*)`가 다른 이유는?
A. `AVG`는 NULL이 아닌 행 수로 나누고, `COUNT(*)`는 NULL을 포함한 전체 행 수로 나누기 때문입니다. (V1010: 3550 vs 2840)

Q. “소싱 품목이 5개 이상인 업체”를 구할 때 `WHERE COUNT(*) >= 5`가 안 되는 이유는?
A. `WHERE`는 `GROUP BY`보다 먼저 실행되어 그룹이 없는 상태라 집계 함수를 쓸 수 없습니다. `HAVING COUNT(*) >= 5`로 씁니다.

Q. `HAVING item_cnt >= 5`(별칭)는 오류가 나는데 `ORDER BY item_cnt`는 되는 이유는?
A. `HAVING`은 `SELECT`보다 먼저, `ORDER BY`는 `SELECT`보다 나중에 실행되기 때문입니다.

Q. 국내 업체 비율을 `… * 100 / COUNT(*)`로 구했더니 66이 나왔습니다. 66.7을 얻으려면?
A. 정수 ÷ 정수라 몫만 남은 것입니다. `* 100.0`처럼 소수를 섞고 `ROUND(…, 1)`로 반올림합니다.
:::

