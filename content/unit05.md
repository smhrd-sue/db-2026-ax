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

냉장고 세트(`TRF38316001`) BOM의 앞부분 5행을 봅니다.

:::cols
```sql
SELECT bom_id, parent_part_no, child_part_no, qty_per, supply_type
  FROM bom_structure
 WHERE model_part_no  = 'TRF38316001'
   AND parent_part_no = 'TRF38316001'
 ORDER BY bom_id
 LIMIT 5;
```

```result
| bom_id | parent_part_no | child_part_no | qty_per | supply_type |
| --- | --- | --- | --- | --- |
| 1 | TRF38316001 | ACB22943901 | 1.000 | Assembly Pull |
| 2 | TRF38316001 | ADR24872401 | 2.000 | Phantom |
| 3 | TRF38316001 | ACC12625601 | 1.000 | Assembly Pull |
| 4 | TRF38316001 | EBA56264701 | 1.000 | Assembly Pull |
| 5 | TRF38316001 | EFN66589301 | 1.000 | Assembly Pull |
```
:::

`ACB22943901`이 **무슨 부품인지**, UIT가 무엇인지는 이 표에 없습니다. 품명과 UIT는 `part_master`에, UIT의 뜻은 `code_uit`에 있습니다.

### 1-1. JOIN하면 한 표로 볼 수 있습니다 {keep}

같은 5행에 `part_master`의 품명·UIT와 `code_uit`의 UIT 뜻을 이어 붙이면 다음과 같습니다. (쓰는 법은 2절에서 배웁니다.)

```sql
SELECT b.bom_id, b.child_part_no, p.description_kr, p.uit, u.meaning_kr, b.qty_per
  FROM bom_structure b
 INNER JOIN part_master p ON p.part_no = b.child_part_no
 INNER JOIN code_uit u    ON u.uit = p.uit
 WHERE b.model_part_no = 'TRF38316001' AND b.parent_part_no = 'TRF38316001'
 ORDER BY b.bom_id LIMIT 5;
```

```result
| bom_id | child_part_no | description_kr | uit | meaning_kr | qty_per |
| --- | --- | --- | --- | --- | --- |
| 1 | ACB22943901 | 캐비닛 조립체 | T | 사내 조립품, 계획·표준시간·재고 관리 | 1.000 |
| 2 | ADR24872401 | 냉장실 도어 조립체 | P | 사내 중간 조립품, 재고 관리 없음(팬텀) | 2.000 |
| 3 | ACC12625601 | 냉동 사이클 조립체 | T | 사내 조립품, 계획·표준시간·재고 관리 | 1.000 |
| 4 | EBA56264701 | 메인 PCB 조립체 | G | 국내 구매품 | 1.000 |
| 5 | EFN66589301 | 팬 모터 | D | 수입 구매품 | 1.000 |
```

이제 「1번 행은 **캐비닛 조립체**이고, 사내에서 조립하는 부품(T)」이라고 바로 읽을 수 있습니다. 세 테이블에 나뉘어 있던 정보가 한 행에 모였습니다.

### 1-1. 나뉜 테이블을 다시 잇는 작업 {keep}

> 1단원(데이터 모델링)에서 본 것처럼, 같은 정보를 여러 곳에 중복 저장하지 않으려고 테이블을 나눕니다. 그 대가로, 조회할 때는 **나뉜 테이블을 다시 이어 붙여야** 합니다. 이 작업이 **JOIN**입니다.
한 문장으로 정리하면: ==서로 다른 테이블에 나뉘어 저장된 관련 데이터를 연결하여 한 번에 결과로 확인하는 작업==.

### 1-2. 조인 키 찾기 — 같은 값을 가진 컬럼 {keep}

조인하려면 두 테이블에서 **같은 값을 담고 있는 컬럼**을 찾아야 합니다. 대부분 한쪽의 **PK**와 다른 쪽의 **FK**(`REFERENCES`)입니다. 이 수업에서 가장 많이 잇는 테이블은 `part_master`입니다.

```erd part_master를 가운데 두고 뻗어 나가는 조인 키 — 선 위 글자가 FK 컬럼 (bom_structure는 parent_part_no·child_part_no 둘 다)
part_master (품목) @package [*part_no (품번), description_kr (한글 품명), uit (UIT) (FK), status_code (상태 코드) (FK)] ; ||--o< parent·child ; bom_structure (BOM) @list-tree [*bom_id (BOM 행 번호), parent_part_no (부모 품번) (FK), child_part_no (자식 품번) (FK), qty_per (소요량)]
part_master (품목) @package ; ||--o< part_no ; part_sourcing (소싱) @wallet [part_no (품번) (FK), vendor_code (업체 코드) (FK), po_price (단가)]
part_master (품목) @package ; ||--o< part_no ; inventory (재고) @warehouse [part_no (품번) (FK)]
part_master (품목) @package ; ||--o< model_part_no ; production_plan (생산계획) @calendar [*plan_id (계획 번호), model_part_no (모델 품번) (FK), plan_qty (계획 수량)]
part_master (품목) @package ; >o--|| uit ; code_uit (UIT 코드표) @tag [*uit (UIT), meaning_kr (한글 의미)]
part_master (품목) @package ; >o--|| status_code ; code_status (상태 코드표) @circle-check [*status_code (상태 코드), status_name (상태 이름)]
```

### 1-2. 코드표·업체로 한 번 더 이어지는 키 {keep}

```erd part_master를 거치지 않고 바로 잇는 키
vendor (업체) @building-2 [*vendor_code (업체 코드), vendor_name (업체명), country (국가)] ; ||--o< vendor_code ; part_sourcing (소싱) @wallet [part_no (품번) (FK), vendor_code (업체 코드) (FK)] ; >o--|| part_no ; part_master (품목) @package [*part_no (품번)]
code_supply_type (공급 방식 코드표) @truck [*supply_type (공급 방식), meaning_kr (한글 의미)] ; ||--o< supply_type ; bom_structure (BOM) @list-tree [*bom_id (BOM 행 번호), supply_type (공급 방식) (FK)]
```

### 1-2. 조인 키 한눈에 보기 {keep}

`schema_postgres.sql`의 DDL에서 이 수업에서 주로 쓰는 키를 표로 정리하면 다음과 같습니다.

| 이 테이블의 컬럼 (FK) | → 참조하는 테이블의 컬럼 (PK) | 이어 붙이면 알 수 있는 것 |
| --- | --- | --- |
| `bom_structure.child_part_no` | `part_master.part_no` | 자식 부품의 품명·UIT |
| `bom_structure.parent_part_no` | `part_master.part_no` | 부모(상위 조립품)의 품명 |
| `bom_structure.supply_type` | `code_supply_type.supply_type` | 공급 방식의 한글 의미 |
| `part_master.uit` | `code_uit.uit` | UIT의 한글 의미 |
| `part_master.status_code` | `code_status.status_code` | 상태 이름 |
| `part_sourcing.part_no` | `part_master.part_no` | 사 오는 부품의 품명 |
| `part_sourcing.vendor_code` | `vendor.vendor_code` | 업체 이름·국가 |
| `inventory.part_no` | `part_master.part_no` | 재고 부품의 품명 |
| `production_plan.model_part_no` | `part_master.part_no` | 계획 모델의 품명 |

> 표에는 없지만 `bom_structure.model_part_no`도 품번을 담고 있어 `part_master.part_no`와 이을 수 있습니다. 4-2에서 모델의 품명을 가져올 때 씁니다.

### 1-2. 이름이 달라도 값이 같으면 조인 키 {keep}

> 컬럼 **이름이 달라도** 같은 값을 담고 있으면 조인 키입니다. `bom_structure.child_part_no`와 `part_master.part_no`가 그 예입니다. 반대로 이름이 같아도 의미가 다르면 조인 키가 아닙니다. 정리하면 ==PK–FK 관계로 주로 조인이 이루어지지만, 다 그런 것은 아닙니다.==

### 1-3. 조인 조건이 없으면 — CROSS JOIN {keep}

조인 조건 없이 두 테이블을 이으면, 한쪽의 모든 행이 다른 쪽의 모든 행과 하나씩 짝지어집니다. 이것을 **CROSS JOIN**(카티션 곱)이라고 합니다.

```shot 조인 조건이 없으면 모든 행끼리 짝지어집니다
unit05/cross-join.svg
```

### 1-3. 소싱 × 업체 = 624행 {keep}

:::cols
```sql
SELECT COUNT(*)
  FROM part_sourcing CROSS JOIN vendor;
```

```result
| count |
| --- |
| 624 |
```
:::

소싱 52행 × 업체 12행 = **624행**. 각 소싱 행이 **자기 업체가 아닌 업체 11곳과도** 짝지어진 결과라 의미가 없습니다.

### 1-3. 조인 조건을 빠뜨리면 {keep}

:::error 조인 조건을 빠뜨리면 — 오류 없이 행이 불어납니다
`FROM 테이블1, 테이블2`처럼 쉼표로 잇고 조인 조건을 빠뜨려도 **CROSS JOIN과 같은 결과**가 나옵니다. 오류가 나지 않으므로 더 위험합니다.

```sql
SELECT COUNT(*)
  FROM bom_structure b, part_master p
 WHERE b.model_part_no  = 'TRF38316001'
   AND b.parent_part_no = 'TRF38316001';
```

```result
| count |
| --- |
| 816 |
```

냉장고 1레벨 구성품은 12행인데, 부품 68개와 모두 짝지어져 12 × 68 = **816행**이 되었습니다. ==결과 행 수가 예상보다 크게 늘었다면 조인 조건부터 확인==하세요.
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

### 2-2. 소싱 정보에 업체 이름 붙이기 {keep}

4단원 1-4에서 본 `V1010`의 소싱 5행에 업체 이름을 붙여 봅니다. 업체 이름은 `part_sourcing`에 없고 `vendor`에 있습니다.

```erd 소싱 여러 행이 업체 하나를 가리킵니다 — ON s.vendor_code = v.vendor_code
part_sourcing s (소싱) @wallet [part_no (품번) (FK), vendor_code (업체 코드) (FK), po_price (단가), currency (통화)] ; >o--|| vendor_code ; vendor v (업체) @building-2 [*vendor_code (업체 코드), vendor_name (업체명), country (국가)]
```

- `s`의 `vendor_code`(FK)와 `v`의 `vendor_code`(PK)에 **같은 값**이 들어 있어서 조인 키가 됩니다.
- 이번에는 두 컬럼의 **이름도 같습니다**. 그래서 어느 쪽 `vendor_code`인지 `s.`·`v.`로 밝혀야 합니다(2-3).

### 2-2. 쿼리와 결과 {keep}

:::cols
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
:::

- `s`, `v`는 **테이블 별칭**입니다(2-3).
- 조인 조건(`ON`)과 행 조건(`WHERE`)은 따로 씁니다. 조인 조건은 「어떤 행끼리 짝지을지」, 행 조건은 「짝지은 결과 중 무엇을 남길지」입니다.

### 2-3. 테이블 별칭 ① 같은 이름의 컬럼은 어느 테이블 것인지 밝히기 {keep}

```sql
SELECT vendor_code, vendor_name
  FROM part_sourcing s
 INNER JOIN vendor v
    ON s.vendor_code = v.vendor_code
 LIMIT 1;
```

```error
ERROR:  column reference "vendor_code" is ambiguous
```

`vendor_code`는 `part_sourcing`에도 `vendor`에도 있어서 어느 쪽인지 알 수 없다는 뜻입니다. `s.vendor_code`처럼 **별칭을 붙이면** 해결됩니다.
`vendor_name`처럼 한 테이블에만 있는 컬럼은 별칭 없이도 실행되지만, ==코드의 가독성을 위해 모든 컬럼 앞에 테이블 별칭(`s.`, `v.`)을 붙이는 것이 좋습니다.==

### 2-3. 테이블 별칭 ② 별칭을 지으면 원래 이름은 못 씁니다 {keep}

```sql
SELECT part_sourcing.part_no
  FROM part_sourcing s
 LIMIT 1;
```

```error
ERROR:  invalid reference to FROM-clause entry for table "part_sourcing"
HINT:  Perhaps you meant to reference the table alias "s".
```

PostgreSQL이 「별칭 `s`를 쓰려던 것 아니냐」고 힌트까지 알려 줍니다. ==테이블에 별칭을 지었으면 이후 모든 절에서 별칭으로만== 부릅니다.

> 테이블 별칭은 `FROM part_sourcing AS s`처럼 `AS`를 붙여도 되고, 공백만 두어도 됩니다. 이 교안은 공백 방식으로 씁니다.

### 2-4. 쉼표 조인 — 다른 사람의 쿼리에서 보게 되는 모양 {keep}

`FROM`에 테이블을 쉼표로 나열하고, 조인 조건을 `WHERE`에 쓰는 방식도 있습니다. 2-2와 **결과가 같습니다**.

```sql
SELECT s.part_no, s.vendor_code, v.vendor_name, s.po_price, s.currency
  FROM part_sourcing s, vendor v
 WHERE s.vendor_code = v.vendor_code      -- 조인 조건
   AND s.vendor_code = 'V1010'            -- 행 조건
 ORDER BY s.part_no;
```

이 방식은 조인 조건과 행 조건이 `WHERE`에 섞여서, 조인 조건 하나를 빠뜨려도 알아채기 어렵습니다(1-3). 이 수업에서는 **`JOIN … ON`** 으로 작성합니다.

### 2-5. 세 개 테이블 잇기 — 냉장고 1레벨 구성품 (Q1) {keep}

**질문:** 냉장고 세트의 1레벨 구성품을 품명, UIT, **UIT 한글 의미**와 함께 보여 주세요.

필요한 컬럼이 어디에 있는지 먼저 찾습니다.

| 필요한 것 | 테이블 | 조인 키 |
| --- | --- | --- |
| 1레벨 구성품, 소요량, 공급 방식 | `bom_structure` | — |
| 품명, UIT | `part_master` | `b.child_part_no = p.part_no` |
| UIT 한글 의미 | `code_uit` | `p.uit = u.uit` |

### 2-5. 세 테이블이 이어지는 모양 {keep}

```erd ① BOM과 품목을 잇고 → ② 그 결과에 UIT 코드표를 잇습니다
bom_structure b (BOM) @list-tree [*bom_id (BOM 행 번호), child_part_no (자식 품번) (FK), qty_per (소요량), supply_type (공급 방식)] ; >o--|| ① 품번 ; part_master p (품목) @package [*part_no (품번), description_kr (한글 품명), uit (UIT) (FK)] ; >o--|| ② UIT ; code_uit u (UIT 코드표) @tag [*uit (UIT), meaning_kr (한글 의미)]
```

- ① `ON p.part_no = b.child_part_no` — 두 컬럼은 **이름이 달라도 같은 값**(품번)이라 조인 키가 됩니다(1-2).
- ② `ON u.uit = p.uit` — 두 번째 조인은 `bom_structure`가 아니라 **`part_master`의 `uit`** 를 거쳐 `code_uit`로 이어집니다. BOM에는 UIT 컬럼이 없기 때문입니다.

### 2-5. 1단계 — BOM에 품목 정보 붙이기 {keep}

:::cols
```sql
SELECT b.bom_id
     , b.child_part_no
     , p.description_kr
     , p.uit
     , b.qty_per
  FROM bom_structure b
 INNER JOIN part_master p
    ON p.part_no = b.child_part_no
 WHERE b.model_part_no  = 'TRF38316001'
   AND b.parent_part_no = 'TRF38316001'
 ORDER BY b.bom_id;
```

```result
| bom_id | child_part_no | description_kr | uit | qty_per |
| --- | --- | --- | --- | --- |
| 1 | ACB22943901 | 캐비닛 조립체 | T | 1.000 |
| 2 | ADR24872401 | 냉장실 도어 조립체 | P | 2.000 |
| 3 | ACC12625601 | 냉동 사이클 조립체 | T | 1.000 |
| 4 | EBA56264701 | 메인 PCB 조립체 | G | 1.000 |
| 5 | EFN66589301 | 팬 모터 | D | 1.000 |
| 6 | MSH53664101 | 선반 | G | 4.000 |
| 7 | MFT43979901 | 정수 필터 | G | 1.000 |
| 8 | EHN19575601 | 와이어 하네스 | G | 1.000 |
| 9 | APK15762301 | 포장 조립체 | P | 1.000 |
| 10 | FSC67181101 | 나사 M4x12 | G | 24.000 |
| 11 | MFL37467701 | 사용설명서 | X | 1.000 |
| 12 | SAA76541601 | 메인 펌웨어 | X | 1.000 |
```
:::

### 2-5. 2단계 — UIT 코드표를 하나 더 잇기 {keep}

`JOIN … ON`을 한 번 더 이어 쓰면 됩니다. 두 번째 조인은 **첫 번째 조인 결과**(`b` + `p`)에 `code_uit`를 잇는 것입니다.

```sql
SELECT b.bom_id
     , p.part_no
     , p.description_kr
     , p.uit
     , u.meaning_kr
     , b.qty_per
     , b.supply_type
  FROM bom_structure b
 INNER JOIN part_master p
    ON p.part_no = b.child_part_no
 INNER JOIN code_uit u
    ON u.uit = p.uit
 WHERE b.model_part_no  = 'TRF38316001'
   AND b.parent_part_no = 'TRF38316001'
 ORDER BY b.bom_id;
```

### 2-5. 2단계 실행 결과 {keep}

```result
| bom_id | part_no | description_kr | uit | meaning_kr | qty_per | supply_type |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ACB22943901 | 캐비닛 조립체 | T | 사내 조립품, 계획·표준시간·재고 관리 | 1.000 | Assembly Pull |
| 2 | ADR24872401 | 냉장실 도어 조립체 | P | 사내 중간 조립품, 재고 관리 없음(팬텀) | 2.000 | Phantom |
| 3 | ACC12625601 | 냉동 사이클 조립체 | T | 사내 조립품, 계획·표준시간·재고 관리 | 1.000 | Assembly Pull |
| 4 | EBA56264701 | 메인 PCB 조립체 | G | 국내 구매품 | 1.000 | Assembly Pull |
| 5 | EFN66589301 | 팬 모터 | D | 수입 구매품 | 1.000 | Assembly Pull |
| 6 | MSH53664101 | 선반 | G | 국내 구매품 | 4.000 | Assembly Pull |
| 7 | MFT43979901 | 정수 필터 | G | 국내 구매품 | 1.000 | Assembly Pull |
| 8 | EHN19575601 | 와이어 하네스 | G | 국내 구매품 | 1.000 | Assembly Pull |
| 9 | APK15762301 | 포장 조립체 | P | 사내 중간 조립품, 재고 관리 없음(팬텀) | 1.000 | Phantom |
| 10 | FSC67181101 | 나사 M4x12 | G | 국내 구매품 | 24.000 | Assembly Pull |
| 11 | MFL37467701 | 사용설명서 | X | 관리용(문서·정보) | 1.000 | Supplier |
| 12 | SAA76541601 | 메인 펌웨어 | X | 관리용(문서·정보) | 1.000 | Supplier |
```

- 조인을 하나 더 해도 **행 수는 12행 그대로**입니다. 부품 하나에 UIT는 하나뿐이므로(`code_uit`의 PK) 행마다 짝이 정확히 하나씩(N:1) 붙기 때문입니다.
- 이제 「냉장고 1대에 나사 M4x12를 24개 쓰고, 이 나사는 국내에서 사 오는 부품」이라고 한 줄로 읽을 수 있습니다.

:::teacher 강사 확인
- `bom_level = 1` 조건으로 찾으면 냉장고는 **13행**이 나옵니다(4단원 2-6). 13행 중 1행(`bom_id` 26)은 부모가 모델이 아니라 `AHD26818801`(핸들 조립체)입니다. 이 행은 README 4장 이상 데이터 **A6** 위치이기도 합니다. Q1 정답(`exercises_mysql.sql`)은 `parent_part_no = model_part_no` 조건을 쓰므로 교안도 그 기준을 따랐습니다. `bom_level` 값 자체가 맞는지는 README에 설명이 없으므로, 질문이 나오면 「1레벨은 부모가 모델인 행」으로만 안내하세요.
:::

### 2-6. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마)

:::try
**[복습]** `employees`와 `departments`를 조인해 직원의 `employee_id`, `first_name`, `department_id`와 부서의 `department_name`, `location_id`를 출력하세요. 단, 급여(`salary`)가 4500~6000인 직원만, 직원 ID 순으로 출력합니다.

**[응용]** `departments` → `locations` → `countries` 세 테이블을 조인해 부서 ID, 부서명, 위치 ID, 도시(`city`), 국가 ID, 국가명(`country_name`)을 출력하세요. 부서 ID가 10, 50, 60인 부서만 부서 ID 순으로 출력합니다.
(힌트: `departments`와 `locations`는 `location_id`, `locations`와 `countries`는 `country_id`로 연결됩니다.)
:::

### 2-6. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
5행

```sql
SELECT e.employee_id
     , e.first_name
     , e.department_id
     , d.department_name
     , d.location_id
  FROM employees e
 INNER JOIN departments d
    ON e.department_id = d.department_id
 WHERE e.salary BETWEEN 4500 AND 6000
 ORDER BY e.employee_id;
```

```result
| employee_id | first_name | department_id | department_name | location_id |
| --- | --- | --- | --- | --- |
| 104 | Bruce | 60 | IT | 1400 |
| 105 | David | 60 | IT | 1400 |
| 106 | Valli | 60 | IT | 1400 |
| 124 | Kevin | 50 | Shipping | 1500 |
| 202 | Pat | 20 | Marketing | 1800 |
```
:::

### 2-6. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
3행

```sql
SELECT d.department_id
     , d.department_name
     , d.location_id
     , l.city
     , l.country_id
     , c.country_name
  FROM departments d
 INNER JOIN locations l
    ON d.location_id = l.location_id
 INNER JOIN countries c
    ON l.country_id = c.country_id
 WHERE d.department_id IN (10, 50, 60)
 ORDER BY d.department_id;
```

```result
| department_id | department_name | location_id | city | country_id | country_name |
| --- | --- | --- | --- | --- | --- |
| 10 | Administration | 1700 | Seattle | US | United States of America |
| 50 | Shipping | 1500 | South San Francisco | US | United States of America |
| 60 | IT | 1400 | Southlake | US | United States of America |
```
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

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
  FROM part_master p
  JOIN part_sourcing s
    ON s.part_no = p.part_no;
```

```result
| count |
| --- |
| 52 |
```
:::

부품은 68개인데 결과는 **52행**입니다. 소싱 정보가 **없는** 부품 16개는 짝이 없어 결과에서 빠졌습니다. 「어떤 부품이 소싱 정보가 없는가?」를 알려면 빠진 쪽을 남기는 조인이 필요합니다.

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

### 3-2. 68행이 모두 남습니다 {keep}

:::cols
```sql
SELECT COUNT(*)
  FROM part_master p
  LEFT JOIN part_sourcing s
    ON s.part_no = p.part_no;
```

```result
| count |
| --- |
| 68 |
```
:::

68행이 모두 남았습니다. 짝이 없는 16행은 `part_sourcing` 쪽 컬럼이 모두 **NULL**로 채워집니다.

| 조인 | 남는 행 |
| --- | --- |
| `INNER JOIN` | 양쪽에 짝이 **있는** 행만 |
| `LEFT [OUTER] JOIN` | **왼쪽** 테이블의 모든 행 + 오른쪽은 짝이 있으면 값, 없으면 NULL |
| `RIGHT [OUTER] JOIN` | **오른쪽** 테이블의 모든 행 (3-7) |
| `FULL [OUTER] JOIN` | **양쪽** 테이블의 모든 행 (3-7) |

> `OUTER`는 생략할 수 있습니다. `LEFT OUTER JOIN`과 `LEFT JOIN`은 같습니다.

### 3-3. 안티 조인 — 짝이 없는 행만 골라내기 ⭐ {keep}

LEFT JOIN 결과에서 **오른쪽 컬럼이 NULL인 행**만 남기면 「짝이 없는 행」이 됩니다. 이 패턴을 **안티 조인**이라고 부릅니다.

**① 소싱 정보가 없는 부품**

```sql
SELECT p.part_no
     , p.description_kr
     , p.uit
     , s.vendor_code
  FROM part_master p
  LEFT JOIN part_sourcing s
    ON s.part_no = p.part_no
 WHERE s.part_no IS NULL
 ORDER BY p.uit, p.part_no;
```

### 3-3. ① 실행 결과와 해석 {keep}

:::cols
```result 16행
| part_no | description_kr | uit | vendor_code |
| --- | --- | --- | --- |
| TRF38316001 | 냉장고 세트 | F | NULL |
| TWM61868701 | 세탁기 세트 | F | NULL |
| ACP85953101 | 컨트롤 패널 조립체 | P | NULL |
| ADR24872401 | 냉장실 도어 조립체 | P | NULL |
| ADR69737101 | 도어 조립체 | P | NULL |
| APK15762301 | 포장 조립체 | P | NULL |
| APK23572301 | 포장 조립체 | P | NULL |
| MCB45577701 | 외함 캐비닛 | P | NULL |
| MCB74311201 | 외함 캐비닛 | P | NULL |
| MLN40306101 | 내상 라이너 | P | NULL |
| ACB22943901 | 캐비닛 조립체 | T | NULL |
| ACB29328801 | 캐비닛 조립체 | T | NULL |
| ACC12625601 | 냉동 사이클 조립체 | T | NULL |
| ADU49470801 | 구동부 조립체 | T | NULL |
| ATB35230801 | 터브 조립체 | T | NULL |
| SAA76541601 | 메인 펌웨어 | X | NULL |
```

- **결과를 해석하는 것까지가 진단**입니다. 16개는 모두 완제품(F), 사내 조립품(T·P), 관리용(X)입니다. 사 오는 부품이 아니므로 소싱 정보가 없는 것이 자연스럽습니다.
- 반대로 **구매품(G·D)인데 이 목록에 나왔다면** 「사 와야 하는데 어디서 사는지 모르는 부품」이므로 이상 데이터입니다. 이 데이터에서는 한 건도 없습니다.
:::

### 3-3. IS NULL은 어느 컬럼으로? {keep}

:::error IS NULL은 오른쪽 테이블의 「NULL이 될 수 없는 컬럼」으로
`WHERE s.part_no IS NULL`의 `s.part_no`는 조인 조건(`ON`)에 쓴 조인 키 컬럼이라, 짝이 지어진 행에서는 NULL일 수 없습니다. 그래서 NULL이면 「짝이 없어서 채운 NULL」이라고 확신할 수 있습니다.
`WHERE s.po_price IS NULL`로 쓰면 **짝은 있지만 단가가 비어 있는 행**(`MFT43979901`, 4단원 1-4)까지 섞여 나옵니다. ==「짝이 없다」와 「값이 비었다」를 구분==하세요.
:::

### 3-3. ② 재고가 없는 부품 — 구매품만 점검 {keep}

:::cols
```sql
SELECT p.part_no
     , p.description_kr
     , p.uit
  FROM part_master p
  LEFT JOIN inventory i
    ON i.part_no = p.part_no
 WHERE i.part_no IS NULL
   AND p.uit IN ('G', 'D', 'S')
 ORDER BY p.part_no;
```

```result 0행
| part_no | description_kr | uit |
| --- | --- | --- |
```
:::

- **0행**입니다. 구매품(G·D)과 협력사 제작품(S)은 모두 재고 행이 있습니다. `AND p.uit IN (…)` 조건을 빼면 15행(F 2, P 8, T 5)이 나옵니다(6절 복습 문제 5번).

> 결과가 0행이라는 것도 **진단 결과**입니다. 「점검했고, 문제없음」을 쿼리로 증명한 것입니다.

### 3-3. ③ 생산계획에 없는 모델 {keep}

:::cols
```sql
SELECT p.part_no
     , p.description_kr
  FROM part_master p
  LEFT JOIN production_plan pl
    ON pl.model_part_no = p.part_no
 WHERE p.uit = 'F'
   AND pl.plan_id IS NULL;
```

```result 0행
| part_no | description_kr |
| --- | --- |
```
:::

완제품(UIT F) 2개 모델(냉장고·세탁기)은 모두 12월 생산계획에 있습니다.

:::teacher 강사 확인
- ②에서 UIT 조건 없이 나오는 15행에는 T(사내 조립품) 5개가 포함됩니다. `code_uit`의 T 설명은 「계획·표준시간·재고 관리」인데 재고 행이 없습니다. README 4장 이상 데이터 목록(A1~A9)에는 이 항목이 없으므로 이상으로 단정하지 말고, 「재고 0」과 「재고 행 없음」은 다르다는 점만 짚어 주세요.
:::

### 3-4. NOT EXISTS — 같은 질문을 다른 모양으로 {keep}

안티 조인은 `NOT EXISTS`로도 씁니다. 「재고 테이블에 이 품번의 행이 **존재하지 않는** 부품」이라는 뜻입니다.

:::cols
```sql
SELECT p.part_no
     , p.description_kr
     , p.uit
  FROM part_master p
 WHERE p.uit IN ('G', 'D', 'S')
   AND NOT EXISTS (SELECT 1
                     FROM inventory i
                    WHERE i.part_no = p.part_no);
```

```result 0행
| part_no | description_kr | uit |
| --- | --- | --- |
```
:::

3-3 ②와 같은 0행입니다. 괄호 안의 쿼리(서브쿼리)는 Day 3 1교시에서 자세히 다룹니다. 여기서는 ==「LEFT JOIN + IS NULL」과 「NOT EXISTS」가 같은 질문==이라는 것만 기억하세요.

### 3-5. 코드표 기준 LEFT JOIN + COUNT — 0도 보여 주기 {keep}

4단원 2-2의 「UIT별 부품 수」는 부품이 있는 UIT 7개만 나왔습니다. 코드표(`code_uit`)를 **왼쪽**에 두고 LEFT JOIN하면 **쓰이지 않는 코드까지** 0으로 볼 수 있습니다.

```sql
SELECT u.uit
     , u.meaning_kr
     , COUNT(p.part_no) AS part_cnt
     , COUNT(*)         AS star_cnt
  FROM code_uit u
  LEFT JOIN part_master p
    ON p.uit = u.uit
 GROUP BY u.uit, u.meaning_kr
 ORDER BY part_cnt DESC, u.uit;
```

### 3-5. 실행 결과 — COUNT(*)가 1인 코드 {keep}

```result
| uit | meaning_kr | part_cnt | star_cnt |
| --- | --- | --- | --- |
| G | 국내 구매품 | 41 | 41 |
| P | 사내 중간 조립품, 재고 관리 없음(팬텀) | 8 | 8 |
| D | 수입 구매품 | 7 | 7 |
| T | 사내 조립품, 계획·표준시간·재고 관리 | 6 | 6 |
| F | 완제품(모델) | 2 | 2 |
| S | 협력사 제작, 유상사급 품목 포함 | 2 | 2 |
| X | 관리용(문서·정보) | 2 | 2 |
| C | 세트 모델(여러 모델 조합) | 0 | 1 |
| M | 협력사 제작, 무상사급만 | 0 | 1 |
| Q | 상품(외부 구매 완제품) | 0 | 1 |
| R | 협력사 제작, 무상사급+협력사 구매 | 0 | 1 |
```

:::error LEFT JOIN 뒤에는 COUNT(*) 대신 COUNT(오른쪽 컬럼)
C·M·Q·R은 부품이 하나도 없는데 `COUNT(*)`는 **1**입니다. LEFT JOIN이 짝 없는 코드에도 NULL로 채운 **1행**을 만들었고, `COUNT(*)`는 그 행까지 세기 때문입니다(4단원 1-3).
==LEFT JOIN 결과를 셀 때는 `COUNT(오른쪽 테이블의 PK)`== 로 셉니다.
:::

### 3-6. ON에 쓸까, WHERE에 쓸까 ⭐ {keep}

**질문:** 업체별로 **달러(USD) 소싱 건수**를 구하되, 달러 소싱이 없는 업체도 0으로 보여 주세요.

:::cols
```sql A. 통화 조건을 ON에
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

```sql B. 통화 조건을 WHERE에
SELECT v.vendor_code
     , v.vendor_name
     , COUNT(s.part_no) AS usd_cnt
  FROM vendor v
  LEFT JOIN part_sourcing s
    ON s.vendor_code = v.vendor_code
 WHERE s.currency = 'USD'
 GROUP BY v.vendor_code, v.vendor_name
 ORDER BY v.vendor_code;
```
:::

### 3-6. 결과 비교 — 12행 vs 4행 {keep}

:::cols
```result A. ON에 (12행)
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

```result B. WHERE에 (4행)
| vendor_code | vendor_name | usd_cnt |
| --- | --- | --- |
| V1004 | AsiaComp Co., Ltd. | 1 |
| V1005 | NanoChip Semiconductor | 1 |
| V1007 | Global Steel Trading | 2 |
| V1009 | Pacific Motor Parts | 3 |
```
:::

### 3-6. ON과 WHERE의 차이 {keep}

| | 조건을 `ON`에 | 조건을 `WHERE`에 |
| --- | --- | --- |
| 실행 시점 | 짝을 **지을 때** 적용 | 짝을 다 지은 **뒤에** 적용 |
| 달러 소싱이 없는 업체 | 조건에 맞는 짝이 없어 NULL로 채워 **남음** → 0 | 짝지어진 KRW 행이 모두 걸러져 업체가 **사라짐** (소싱이 아예 없는 업체였다면 `s.currency`가 NULL이라 역시 탈락) |
| 결과 | 12행 | 4행 (INNER JOIN과 같아짐) |

> ==LEFT JOIN에서 오른쪽 테이블 조건을 WHERE에 쓰면, LEFT JOIN이 INNER JOIN처럼 동작합니다.== 「짝이 없는 행도 남기고 싶다」면 오른쪽 테이블의 조건은 `ON`에 씁니다. 왼쪽 테이블의 조건(예: `v.is_domestic = 'N'`)은 `WHERE`에 써도 됩니다.

### 3-7. RIGHT JOIN {keep}

:::cols
```shot RIGHT JOIN — 교집합 + 오른쪽
unit05/right-join.svg
```

```sql
SELECT COUNT(*)
  FROM part_sourcing s
 RIGHT JOIN part_master p
    ON s.part_no = p.part_no;
```
:::

**RIGHT JOIN**은 LEFT JOIN과 방향만 반대입니다. 위 쿼리는 3-2(`part_master LEFT JOIN part_sourcing`)와 같은 **68행**입니다.

> 테이블 순서만 바꾸면 RIGHT JOIN은 언제나 LEFT JOIN으로 바꿔 쓸 수 있습니다. 읽기 쉽도록 ==기준 테이블을 왼쪽(FROM)에 두고 LEFT JOIN으로 통일==하는 것을 권합니다.

### 3-7. FULL JOIN {keep}

**FULL JOIN**은 짝이 있는 행에 더해, 왼쪽·오른쪽 어느 쪽이든 짝이 없는 행까지 모두 남깁니다. 「소싱 정보는 있는데 재고 행이 없는 부품」과 「재고 행은 있는데 소싱 정보가 없는 부품」을 한 번에 봅니다.

:::cols
```shot FULL JOIN — 양쪽 모두
unit05/full-join.svg
```

```sql
SELECT s.part_no AS src_part
     , i.part_no AS inv_part
  FROM part_sourcing s
  FULL JOIN inventory i
    ON i.part_no = s.part_no
 WHERE s.part_no IS NULL
    OR i.part_no IS NULL;
```
:::

```result
| src_part | inv_part |
| --- | --- |
| NULL | SAA76541601 |
```

- 소싱이 있는 52개 부품은 모두 재고 행이 있습니다.
- `SAA76541601`(메인 펌웨어, UIT X)은 재고 행은 있지만 소싱 정보가 없습니다. 3-3 ① 목록에도 있던 부품입니다.

### 3-8. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;`

:::try
**[복습]** `location_id`가 1700인 부서의 `department_id`, `department_name`, `manager_id`와 그 관리자의 `first_name`, `last_name`을 출력하세요. 관리자(`manager_id`)가 NULL인 부서도 출력되어야 하며, 부서 ID 순으로 정렬합니다.
(힌트: `departments.manager_id`와 `employees.employee_id`가 연결됩니다.)

**[응용]** 직원이 **한 명도 없는** 부서의 부서 ID와 부서명을 부서 ID 순으로 출력하세요. LEFT JOIN + IS NULL과 NOT EXISTS 두 가지 방법으로 작성하고 결과 행 수가 같은지 확인합니다.
(힌트: NOT EXISTS는 3-4 쿼리에서 테이블과 컬럼만 바꿔 쓰면 됩니다.)
:::

### 3-8. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
21행. 관리자가 있는 부서 5개 + 관리자가 NULL인 부서 16개입니다.

```sql
SELECT d.department_id
     , d.department_name
     , d.manager_id
     , e.first_name
     , e.last_name
  FROM departments d
  LEFT JOIN employees e
    ON d.manager_id = e.employee_id
 WHERE d.location_id = 1700
 ORDER BY d.department_id;
```

```result
| department_id | department_name | manager_id | first_name | last_name |
| --- | --- | --- | --- | --- |
| 10 | Administration | 200 | Jennifer | Whalen |
| 30 | Purchasing | 114 | Den | Raphaely |
| 90 | Executive | 100 | Steven | King |
| 100 | Finance | 108 | Nancy | Greenberg |
| 110 | Accounting | 205 | Shelley | Higgins |
| 120 | Treasury | NULL | NULL | NULL |
| 130 | Corporate Tax | NULL | NULL | NULL |
| 140 | Control And Credit | NULL | NULL | NULL |
| 150 | Shareholder Services | NULL | NULL | NULL |
| 160 | Benefits | NULL | NULL | NULL |
| 170 | Manufacturing | NULL | NULL | NULL |
| 180 | Construction | NULL | NULL | NULL |
| 190 | Contracting | NULL | NULL | NULL |
| 200 | Operations | NULL | NULL | NULL |
| 210 | IT Support | NULL | NULL | NULL |
| 220 | NOC | NULL | NULL | NULL |
| 230 | IT Helpdesk | NULL | NULL | NULL |
| 240 | Government Sales | NULL | NULL | NULL |
| 250 | Retail Sales | NULL | NULL | NULL |
| 260 | Recruiting | NULL | NULL | NULL |
| 270 | Payroll | NULL | NULL | NULL |
```

`WHERE d.location_id = 1700`은 **왼쪽** 테이블(`departments`) 조건이라 `WHERE`에 써도 됩니다(3-6).
:::

### 3-8. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
두 방법 모두 16행

```sql LEFT JOIN + IS NULL
SELECT d.department_id
     , d.department_name
  FROM departments d
  LEFT JOIN employees e
    ON e.department_id = d.department_id
 WHERE e.employee_id IS NULL
 ORDER BY d.department_id;
```

```sql NOT EXISTS
SELECT d.department_id
     , d.department_name
  FROM departments d
 WHERE NOT EXISTS (SELECT 1
                     FROM employees e
                    WHERE e.department_id = d.department_id)
 ORDER BY d.department_id;
```

```result
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
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

# 다중 조인 + 집계 · 셀프 조인

:::goal
- 여러 테이블을 조인한 결과를 GROUP BY로 묶어 코드 이름·분류별로 집계할 수 있습니다.
- 1:N 조인으로 행이 늘어나는 경우를 COUNT(*)로 확인하고, 집계할 때 주의할 점을 설명할 수 있습니다.
- 같은 테이블에 다른 별칭을 붙여 셀프 조인(부모–자식, 직원–상사)을 할 수 있습니다.
:::

## 4. 여러 테이블 조인 + 집계

### 4-1. 조인한 뒤 묶기 — 업체 이름별 소싱 품목 수 {keep}

4단원 2-4에서는 업체 **코드**별로만 셀 수 있었습니다. `vendor`를 조인하면 이름까지 함께 볼 수 있습니다.

:::cols
```sql
SELECT v.vendor_code
     , v.vendor_name
     , COUNT(*) AS item_cnt
  FROM part_sourcing s
  JOIN vendor v
    ON s.vendor_code = v.vendor_code
 GROUP BY v.vendor_code, v.vendor_name
 ORDER BY item_cnt DESC, v.vendor_code;
```

```result
| vendor_code | vendor_name | item_cnt |
| --- | --- | --- |
| V1001 | 한빛정밀(주) | 9 |
| V1011 | 태양전장(주) | 8 |
| V1003 | 세진전자(주) | 6 |
| V1006 | 우성사출(주) | 6 |
| V1008 | 동아포장(주) | 6 |
| V1010 | 한성고무(주) | 5 |
| V1009 | Pacific Motor Parts | 4 |
| V1002 | 대양화학(주) | 3 |
| V1007 | Global Steel Trading | 2 |
| V1004 | AsiaComp Co., Ltd. | 1 |
| V1005 | NanoChip Semiconductor | 1 |
| V1012 | LG 사내 부품라인(C1) | 1 |
```
:::

- 실행 순서는 4단원과 같습니다. ==FROM·JOIN으로 먼저 큰 표를 만들고 → WHERE → GROUP BY== 순서로 진행됩니다.
- `SELECT`에 `v.vendor_name`을 쓰려면 `GROUP BY`에도 넣어야 합니다(4단원 2-9).

### 4-2. 모델별·UIT별 구성품 수 — Make/Buy 비중 (Q2) {keep}

**질문:** 모델별로 구성품을 UIT 분류(Make/Buy)와 UIT별로 세어 주세요.

:::cols
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

```result
| model_part_no | classification | uit | parts |
| --- | --- | --- | --- |
| TRF38316001 | Buy item | D | 3 |
| TRF38316001 | Buy item | G | 24 |
| TRF38316001 | Buy item | X | 2 |
| TRF38316001 | Make item | P | 4 |
| TRF38316001 | Make item | S | 1 |
| TRF38316001 | Make item | T | 2 |
| TWM61868701 | Buy item | D | 5 |
| TWM61868701 | Buy item | G | 25 |
| TWM61868701 | Buy item | X | 2 |
| TWM61868701 | Make item | P | 4 |
| TWM61868701 | Make item | S | 1 |
| TWM61868701 | Make item | T | 4 |
```
:::

- `classification`(Make item / Buy item)은 `code_uit`에만 있는 컬럼입니다. 4단원 2-8에서는 `CASE`로 Make/Buy 라벨을 직접 만들었지만, **코드표를 조인하면 정의된 분류를 그대로** 쓸 수 있습니다.
- 냉장고는 Buy item으로 분류된 구성품이 29종(D 3 + G 24 + X 2), 세탁기는 32종입니다. 관리용(X)도 코드표에서는 Buy item입니다.

### 4-2. 왜 COUNT(DISTINCT p.part_no)일까? {keep}

분류 단위로 묶어 `COUNT(*)`와 비교해 봅니다.

:::cols
```sql
SELECT m.description_kr AS model
     , u.classification
     , COUNT(*)                  AS line_cnt
     , COUNT(DISTINCT p.part_no) AS part_cnt
  FROM bom_structure b
  JOIN part_master p
    ON p.part_no = b.child_part_no
  JOIN code_uit u
    ON u.uit = p.uit
  JOIN part_master m
    ON m.part_no = b.model_part_no
 GROUP BY m.description_kr, u.classification
 ORDER BY model, u.classification;
```

```result
| model | classification | line_cnt | part_cnt |
| --- | --- | --- | --- |
| 냉장고 세트 | Buy item | 32 | 29 |
| 냉장고 세트 | Make item | 7 | 7 |
| 세탁기 세트 | Buy item | 34 | 32 |
| 세탁기 세트 | Make item | 9 | 9 |
```
:::

> 이 쿼리에서 `part_master`를 **두 번**(`p`, `m`) 조인했습니다. 한 번은 자식 부품의 UIT를, 한 번은 모델의 한글 이름을 가져오기 위해서입니다. 같은 테이블을 여러 번 쓰려면 **별칭을 다르게** 붙이면 됩니다(5절).

### 4-2. 같은 부품이 여러 번 쓰이는 BOM 행 {keep}

같은 부품이 한 모델 안에서 **여러 상위 조립품 아래 반복해서** 쓰이면 BOM 행은 여러 개입니다. 행 수(`line_cnt`)와 부품 종류 수(`part_cnt`)가 다른 이유입니다.

:::cols
```sql
SELECT model_part_no
     , child_part_no
     , COUNT(*) AS line_cnt
  FROM bom_structure
 GROUP BY model_part_no, child_part_no
HAVING COUNT(*) > 1
 ORDER BY model_part_no, child_part_no;
```

```result
| model_part_no | child_part_no | line_cnt |
| --- | --- | --- |
| TRF38316001 | FSC67181101 | 2 |
| TRF38316001 | FTP68745401 | 2 |
| TRF38316001 | RRS44997401 | 2 |
| TWM61868701 | FSC33042701 | 3 |
```
:::

### 4-3. 조인하면 행이 늘어날 수 있습니다 {keep}

짝이 1:1이 아니라 **1:N**이면, 조인 결과는 N쪽 행 수만큼 늘어납니다.

:::cols
```sql
SELECT COUNT(*)
  FROM production_plan pl
  JOIN bom_structure b
    ON b.model_part_no = pl.model_part_no;
```

```result
| count |
| --- |
| 820 |
```
:::

- 생산계획은 냉장고 10일 + 세탁기 10일 = 20행입니다. 계획 1행마다 그 모델의 BOM 행(냉장고 39 / 세탁기 43)이 모두 붙어 10 × 39 + 10 × 43 = **820행**이 되었습니다.
- 이것은 오류가 아니라 의도한 결과입니다. Day 3에서 「계획 수량 × 소요량」으로 **날짜별 부품 소요량**을 계산할 때 바로 이 결과를 씁니다.

### 4-3. 늘어난 행에 SUM을 하면 {keep}

:::error 늘어난 행에 SUM을 하면
1:N 조인 뒤 **1쪽 테이블의 숫자**를 `SUM`하면 같은 값이 N번 더해집니다. 예를 들어 위 결과에서 `SUM(pl.plan_qty)`를 구하면 계획 수량이 BOM 행 수만큼 반복해서 더해집니다.
==집계하기 전에 「이 조인으로 행이 몇 배가 되었나」를 COUNT(*)로 먼저 확인==하세요.
:::

### 4-4. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;`

:::try
**[복습]** 부서 **이름**별 직원 수(`emp_cnt`)와 평균 급여(`avg_sal`, 소수 첫째 자리까지 반올림)를 구하되, 직원이 5명 이상인 부서만 직원 수가 많은 순, 같으면 부서 이름 순으로 출력하세요.

**[응용]** `employees` → `departments` → `locations` → `countries` 네 테이블을 조인해 **국가명별 직원 수**(`emp_cnt`)를 많은 순으로 출력하세요.
결과의 직원 수를 모두 더하면 107명이 되나요? 아니라면 왜일까요?
:::

### 4-4. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
5행

```sql
SELECT d.department_name
     , COUNT(*)                AS emp_cnt
     , ROUND(AVG(e.salary), 1) AS avg_sal
  FROM employees e
  JOIN departments d
    ON e.department_id = d.department_id
 GROUP BY d.department_name
HAVING COUNT(*) >= 5
 ORDER BY emp_cnt DESC, d.department_name;
```

```result
| department_name | emp_cnt | avg_sal |
| --- | --- | --- |
| Shipping | 45 | 3475.6 |
| Sales | 34 | 8955.9 |
| Finance | 6 | 8601.3 |
| Purchasing | 6 | 4150.0 |
| IT | 5 | 5760.0 |
```
:::

### 4-4. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
4행

```sql
SELECT c.country_name
     , COUNT(*) AS emp_cnt
  FROM employees e
  JOIN departments d
    ON e.department_id = d.department_id
  JOIN locations l
    ON d.location_id = l.location_id
  JOIN countries c
    ON l.country_id = c.country_id
 GROUP BY c.country_name
 ORDER BY emp_cnt DESC;
```

```result
| country_name | emp_cnt |
| --- | --- |
| United States of America | 68 |
| United Kingdom | 35 |
| Canada | 2 |
| Germany | 1 |
```

합계는 68 + 35 + 2 + 1 = **106명**입니다. 부서가 NULL인 직원 1명(178 Kimberely Grant)이 첫 번째 INNER JOIN에서 짝이 없어 빠졌기 때문입니다. (4단원 1-6 확인 문제의 `COUNT(department_id)` = 106과 같은 원인)
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

## 5. 셀프 조인 — 같은 테이블을 두 번

### 5-1. 같은 테이블을 두 번 쓰기 — 부모와 자식의 이름 {keep}

`bom_structure`의 한 행에는 **부모 품번**과 **자식 품번**이 둘 다 있고, 둘 다 `part_master.part_no`를 가리킵니다. 그래서 `part_master`를 **역할이 다른 두 개의 테이블처럼** 조인합니다. 테이블을 자기 자신과 잇는 셀프 조인은 5-2부터이고, 여기서는 그 준비로 같은 테이블을 역할별 별칭으로 두 번 조인합니다.

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

### 5-1. 실행 결과 {keep}

```result
| bom_id | parent_part_no | parent_name | child_part_no | child_name | qty_per |
| --- | --- | --- | --- | --- | --- |
| 13 | ACB22943901 | 캐비닛 조립체 | MCB45577701 | 외함 캐비닛 | 1.000 |
| 14 | ACB22943901 | 캐비닛 조립체 | MLN40306101 | 내상 라이너 | 1.000 |
| 15 | ACB22943901 | 캐비닛 조립체 | RPU53256801 | 우레탄 발포액 | 6.500 |
| 16 | ACB22943901 | 캐비닛 조립체 | MHG51215701 | 도어 힌지(구형) | 2.000 |
| 17 | ACB22943901 | 캐비닛 조립체 | MHG91254002 | 도어 힌지 | 2.000 |
```

> ==같은 테이블을 두 번 쓰는 것이기 때문에 반드시 테이블에 별칭을 사용해야 합니다.== 별칭이 없으면 `part_master.description_kr`이 부모 것인지 자식 것인지 구분할 수 없습니다.

:::teacher 강사 확인
- `bom_id` 16의 `MHG51215701`(도어 힌지(구형))은 4단원 2-3에서 본 **폐기(1) 상태** 부품입니다. README 4장 **A2**(폐기 부품 BOM 잔존)이며, 이 단원 다음의 품질 진단 시간(Q6)에서 `code_status`를 조인해 찾습니다. 훈련생이 먼저 알아채면 칭찬하고, 「상태 코드를 같이 조인하면 확인할 수 있다」까지만 안내하세요.
:::

### 5-2. bom_structure 셀프 조인 — 한 단계 아래 구성품 {keep}

`bom_structure` **자기 자신**을 조인하면, 「1레벨 구성품의 **자식**」을 한 번에 볼 수 있습니다. 첫 번째 행의 `child_part_no`가 두 번째 행의 `parent_part_no`와 같으면 이어집니다.

```screen 두 BOM 행이 이어지는 모양
b1 :  TRF38316001(냉장고)  →  ACB22943901(캐비닛 조립체)
b2 :                          ACB22943901(캐비닛 조립체)  →  MCB45577701(외함 캐비닛) …
        조인 조건: b2.parent_part_no = b1.child_part_no
```

### 5-2. 아래에 구성품을 가진 1레벨 구성품 {keep}

**질문:** 냉장고 1레벨 구성품 중 **자기 아래에 구성품을 가진** 것과 그 구성품 수는?

:::cols
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
:::

### 5-2. 결과 읽기 {keep}

- 1레벨 12개 중 5개가 아래에 구성품을 가집니다. 나머지 7개(선반, 나사 등)는 INNER JOIN에서 짝이 없어 빠졌습니다.
- `b2.model_part_no = b1.model_part_no`는 같은 모델의 BOM끼리만 잇기 위한 조건입니다. (이 데이터에서는 이 조건을 빼도 결과가 같지만, 같은 조립품 품번이 다른 모델 BOM에도 있을 수 있으므로 습관적으로 함께 씁니다.)

> 셀프 조인 한 번으로 **한 단계**를 내려갔습니다. 3레벨까지 내려가려면 셀프 조인을 한 번 더 해야 하고, 레벨 수를 모르면 몇 번 해야 할지 정할 수 없습니다. 이 문제를 푸는 방법이 Day 3의 **재귀 CTE**입니다.

### 5-3. HR 데이터로 보는 셀프 조인 — 직원과 상사 {keep}

`employees.manager_id`는 같은 테이블의 `employee_id`를 가리킵니다(`hr_postgres.sql`의 `emp_manager_fk`). HR 데이터로 셀프 조인을 연습할 때 가장 많이 쓰는 예제입니다.

:::cols
```sql
SET search_path TO hr;

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

- `a`는 **직원** 역할, `b`는 **상사** 역할입니다.
- 부서 90에는 직원이 3명(100·101·102)인데 2명만 나왔습니다. 100번 Steven King은 상사가 없어(`manager_id` NULL) 짝이 없기 때문입니다. → 확인 문제 [복습]

> 바로 이어지는 5-4 확인 문제도 HR 데이터로 풉니다. `hr` 스키마 그대로 진행합니다.

### 5-4. 확인 문제 — HR 데이터 {keep}

> 실행 전: `SET search_path TO hr;`

:::try
**[복습]** 5-3 쿼리를 고쳐, 상사가 없는 직원(Steven King)도 함께 출력하세요. 출력 컬럼은 `employee_id`, `first_name`, `manager_id`, `manager_name`입니다.

**[응용]** **자기 상사보다 급여가 많은** 직원을 찾아 직원 ID, 이름, 급여, 상사 ID, 상사 이름, 상사 급여를 직원 ID 순으로 출력하세요. 별칭은 `mgr_id`, `mgr_name`, `mgr_salary`입니다.
:::

### 5-4. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
3행. 짝이 없는 직원도 남겨야 하므로 `LEFT JOIN`입니다.

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

### 5-4. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
2행. 셀프 조인으로 직원(`a`)과 상사(`b`)를 한 행에 놓으면, 두 사람의 급여를 `WHERE`에서 바로 비교할 수 있습니다.

```sql
SELECT a.employee_id
     , a.first_name
     , a.salary
     , b.employee_id AS mgr_id
     , b.first_name  AS mgr_name
     , b.salary      AS mgr_salary
  FROM employees a
  JOIN employees b
    ON a.manager_id = b.employee_id
 WHERE a.salary > b.salary
 ORDER BY a.employee_id;
```

```result
| employee_id | first_name | salary | mgr_id | mgr_name | mgr_salary |
| --- | --- | --- | --- | --- | --- |
| 168 | Lisa | 11500.00 | 148 | Gerald | 11000.00 |
| 174 | Ellen | 11000.00 | 149 | Eleni | 10500.00 |
```
:::

> 확인 문제를 마치면 `SET search_path TO bom;`으로 돌아옵니다.

## 6. 복습 문제

### 6-0. 복습 문제 안내 {keep}

> 범위: INNER JOIN · OUTER JOIN · 안티 조인 · 다중 조인 + 집계. `bom` 스키마의 테이블로 풀어 주세요. 실행 전: `SET search_path TO bom;` 출력 순서는 `ORDER BY` 기준입니다.

```icons 여섯 문항
globe | 1 · INNER JOIN | 해외 업체에서 사 오는 부품 | rose
truck | 2 · 3개 테이블 | 세탁기 1레벨 + 공급 방식 의미 | plum
map | 3 · 조인 + 집계 | 국가별 소싱 건수 | lime
list-checks | 4 · LEFT JOIN + COUNT | 상태별 부품 수(0 포함) | ivory
package | 5 · (심화) 안티 조인 | 재고 행 없는 부품 UIT별 | plum
layers | 6 · (심화) 다중 조인 | 1레벨 수입 구매품의 업체 | hot
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

[힌트] (1) 1레벨 구성품 = 부모가 모델인 BOM 행 (`b.parent_part_no = b.model_part_no`) (2) `part_master`를 두 번 조인합니다. 한 번은 모델 이름용, 한 번은 자식 부품용 (4-2, 5-1) (3) 업체명은 `part_sourcing` → `vendor` 순서로 이어서 가져옵니다.

```result 출력 결과 (총 2행)
| model | child_part_no | description_kr | vendor_name | lead_time_days |
| --- | --- | --- | --- | --- |
| 냉장고 세트 | EFN66589301 | 팬 모터 | Pacific Motor Parts | 40 |
| 세탁기 세트 | EPM57964301 | 배수 펌프 | 태양전장(주) | 14 |
```

### 6-5. 복습 1 · 2 답 {keep}

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

### 6-6. 복습 3 · 4 답 {keep}

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
- 4번 결과의 `Obsolete` 1개는 4단원 2-3의 `MHG51215701`입니다. 이 부품이 어디에 쓰이는지는 품질 진단 시간에 확인합니다.
:::

### 6-7. 복습 5 · 6 답 {keep}

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
:::

:::teacher 강사 확인 — 복습 문제에 보이는 이상 데이터
- 1번 `EMT73633001`(스테이터): 해외 업체(VN)인데 통화가 KRW입니다. 이 부품은 README **A1**(UIT G인데 해외 벤더)입니다.
- 2번 `APK23572301`(포장 조립체): UIT P(팬텀)인데 공급 방식이 `Assembly Pull`입니다. README **A3**입니다.
- 6번 `EPM57964301`(배수 펌프): 수입 구매품(D)인데 국내 업체(태양전장)에서 사 옵니다. README **A1**입니다.
- 세 건 모두 다음 품질 진단 시간(Q5·Q7)에서 다룹니다. 훈련생이 질문하면 「이상해 보이는 점을 메모해 두라」고 안내하고, 답은 진단 시간에 확인하게 하세요.
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
- **셀프 조인**: 한 테이블을 자기 자신과 조인(BOM 부모–자식 행, 직원–상사). 같은 테이블을 두 번 붙일 때도 역할별 별칭 필수.
:::

### 7-2. 확인 문제

:::quiz
Q. 냉장고 1레벨 구성품(12행)과 `part_master`(68행)를 조인 조건 없이 이었더니 816행이 나왔습니다. 원인과 해결 방법은?
A. 조인 조건이 없어 모든 행끼리 짝지어진 CROSS JOIN 결과(12 × 68)입니다. `ON p.part_no = b.child_part_no` 조인 조건을 씁니다.

Q. `SELECT vendor_code, vendor_name FROM part_sourcing s INNER JOIN vendor v ON …`이 `ambiguous` 오류가 나는 이유는?
A. `vendor_code`가 두 테이블에 모두 있어 어느 것인지 알 수 없기 때문입니다. `s.vendor_code`처럼 별칭을 붙입니다.

Q. 「소싱 정보가 없는 부품」을 찾을 때 INNER JOIN을 쓰면 안 되는 이유와, 대신 쓰는 패턴은?
A. INNER JOIN은 짝이 없는 행을 결과에서 버립니다. `part_master LEFT JOIN part_sourcing` 후 `WHERE s.part_no IS NULL`로 짝이 없는 행만 남깁니다.

Q. 업체별 달러 소싱 건수를 0건 업체까지 보려고 LEFT JOIN을 썼는데, `WHERE s.currency = 'USD'`를 붙이니 4개 업체만 나왔습니다. 왜일까요?
A. `WHERE`는 짝을 다 지은 뒤 적용되어, 달러가 아닌 행(그리고 짝이 없어 NULL인 행)이 모두 걸러지고 달러 소싱이 없는 업체는 남는 행이 없습니다. 조건을 `ON … AND s.currency = 'USD'`로 옮깁니다.

Q. `code_uit LEFT JOIN part_master` 후 `COUNT(*)`를 했더니, 부품이 없는 UIT C가 1로 나왔습니다. 0으로 나오게 하려면?
A. LEFT JOIN이 짝 없는 C에도 NULL로 채운 1행을 만들었기 때문입니다. `COUNT(p.part_no)`처럼 오른쪽 테이블의 PK를 셉니다.
:::
