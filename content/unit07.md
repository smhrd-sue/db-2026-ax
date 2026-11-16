---
label: 7. DDL
title: 데이터 구조 만들기
---

# CREATE · 제약조건 · ALTER · DROP

:::goal
- `CREATE TABLE`로 알맞은 PostgreSQL 자료형(CHAR·VARCHAR·TEXT·NUMERIC·DATE·TIMESTAMP)을 골라 테이블을 만들고, NOT NULL과 DEFAULT의 동작을 설명할 수 있습니다.
- 제약조건 다섯 가지(PK·UNIQUE·NOT NULL·CHECK·FK)를 걸고, 오류 메시지로 무엇이 막혔는지 읽을 수 있습니다.
- `ALTER TABLE`로 컬럼·이름·기본값·제약조건을 고치고, DELETE·TRUNCATE·DROP과 CASCADE의 차이를 설명할 수 있습니다.
- 판단 결과(결품 경고)를 기록하는 테이블을 PK·FK·CHECK와 함께 설계할 수 있습니다.
:::

:::teacher 단원 구성 (60분)
- 운영안 Day 4 **3H(기록 테이블 설계: 판단 기록에 필요한 컬럼, PostgreSQL 자료형, PK·FK·CHECK 제약 포함 CREATE TABLE, 기존 이력 테이블 2종과 비교)** 에 해당합니다. Day 4 1H에서 쓰는 `CREATE TABLE ... AS SELECT`(연습용 사본 만들기)도 2-6에서 함께 다룹니다.
- 기존 교안 `9. DDL.pptx` · `09.DDL복습문제.txt`의 **순서(CREATE → 제약조건 → ALTER → DROP/TRUNCATE)와 실습 유형(회원·블로그 테이블, TB_CUST)** 을 따르되, 예제는 BOM 실습 데이터(`bom` 스키마)로 바꾸고 마지막에 **판단 기록 테이블 설계(6장)** 를 붙였습니다.
- 기존 교안의 문법 중 PostgreSQL에서 그대로 쓰지 않는 것은 다음과 같이 바꿨습니다: `VARCHAR2` → `VARCHAR`, `NUMBER` → `INT`/`NUMERIC`, `MODIFY` → `ALTER COLUMN ... TYPE / SET NOT NULL`, `CASCADE CONSTRAINT` → `CASCADE`, 「가변형문자 n**BYTE**」 → PostgreSQL의 `VARCHAR(n)`은 **글자 수** 기준(2-4). 또 `9. DDL.pptx` 31번 「TRUNCATE: 복구 불가능」은 PostgreSQL에서는 맞지 않습니다(5-2).
- INSERT는 **제약조건이 실제로 막는지 확인하는 용도로만** 씁니다. 문법은 DML 단원에서 다룹니다.
- 원본(`bom`) 보호를 위해 모든 실습 테이블은 **`lab` 스키마**에 만듭니다(1-4). 수업이 끝나면 `DROP SCHEMA lab CASCADE;` 한 줄로 정리됩니다(7장 5번).
- 교안의 모든 SQL과 실행 결과는 `schema_postgres.sql`로 적재한 DB에서 **위에서부터 순서대로 직접 실행한 결과**입니다. 오류 메시지도 실제 출력입니다. (검증 환경: PostgreSQL 16, `DateStyle = ISO, MDY`. 수업 PC는 PostgreSQL 18이므로 수업 전 한 번 더 실행해 보세요.) 순서를 바꿔 실행하면 일부 결과(행 수, 오류 여부)가 달라집니다. PostgreSQL 18은 NOT NULL도 `pg_constraint`에 기록하므로(3-5), 제약조건 조회 쿼리에는 모두 `contype IN ('p', 'u', 'c', 'f')` 조건을 넣어 두 버전에서 결과가 같도록 했습니다.
- 각 장 끝 「확인 문제」(복습 1 + 응용 1)는 기존 교안 실습(회원·블로그)과 HR 실습 데이터(`hr_postgres.sql`, `hr` 스키마)로 만들었고, 답안 결과도 직접 실행한 값입니다. 실행 전 `SET search_path TO lab, hr;`가 필요합니다.
- 이 단원은 1교시(60분) 분량입니다. 확인 문제와 7장 복습 문제는 시간에 따라 일부만 풀고, 나머지는 과제로 활용하세요.

| 교시 | 시간 | 내용 | 해당 장 | 기존 교안 대응 |
| --- | --- | --- | --- | --- |
| **Day 4 3교시** | 0~8분 | SQL 종류 · 이미 본 DDL(schema_postgres.sql) · 구조 확인 · lab 스키마 | 1 | `9. DDL.pptx` 3~4 |
| | 8~20분 | CREATE TABLE · 자료형 · NOT NULL · DEFAULT · 이름 규칙 · CTAS 사본 | 2 | `9. DDL.pptx` 5~9, 20~21 |
| | 20~35분 | 제약조건 5종 · PK/UK/CHECK/FK 동작 · 제약조건으로 이상 데이터 찾기 | 3 | `9. DDL.pptx` 10~19, 22 |
| | 35~42분 | ALTER TABLE: 추가 · 변경 · 이름 변경 · 삭제 | 4 | `9. DDL.pptx` 23~25 |
| | 42~48분 | DROP · CASCADE · TRUNCATE · DELETE/TRUNCATE/DROP 비교 | 5 | `9. DDL.pptx` 26~31 |
| | 48~60분 | 결품 경고 기록 테이블 설계 · 복습 문제 안내 | 6~7 | `09.DDL복습문제.txt` |
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

### 1-2. 이미 만나 본 DDL — schema_postgres.sql {keep}

Day 1에 실행한 `schema_postgres.sql`은 대부분이 DDL입니다. 품목 마스터를 만드는 부분을 다시 읽어 봅니다.

```sql schema_postgres.sql — part_master
CREATE TABLE part_master (
  part_no          CHAR(11) PRIMARY KEY,          -- 3자리 분류코드 + 8자리 (끝 2자리 = 시리즈)
  description      TEXT NOT NULL,                 -- 영문 명칭 (Main Function + Sub)
  description_kr   TEXT,
  class_lv1        CHAR(1) NOT NULL,              -- E/F/R/S/T/M/A/C
  class_lv2        CHAR(3) NOT NULL,
  tech_spec        TEXT,
  uom              CHAR(2) REFERENCES code_uom,
  uit              CHAR(1) REFERENCES code_uit,
  status_code      SMALLINT REFERENCES code_status,
  svc_code         CHAR(1) REFERENCES code_svc,   -- NULL이면 서비스 부품 아님
  svc_location_no  TEXT,
  created_at       DATE
);
```

### 1-2. 한 줄씩 읽기 {keep}

| 줄 | 읽는 법 | 이번 단원 |
| --- | --- | --- |
| `part_no CHAR(11) PRIMARY KEY` | 품번은 **11글자 고정**이고, **비어 있을 수 없고 중복될 수 없다** | 2-2, 3-1 |
| `description TEXT NOT NULL` | 영문 명칭은 길이 제한 없는 문자, **반드시 있어야** 한다 | 2-3 |
| `uit CHAR(1) REFERENCES code_uit` | UIT는 **`code_uit`에 있는 코드만** 넣을 수 있다 | 3-4 |
| `status_code SMALLINT ...` | 상태 코드는 **작은 정수** | 2-2 |
| `created_at DATE` | 등록일은 **날짜** | 2-2 |

> Day 1 3교시에 그린 ERD의 선(관계)은 DDL의 `REFERENCES`(외래키)에서 나온 것입니다. ==ERD는 그림, DDL은 그 그림을 DB가 이해하는 문장으로 쓴 것==입니다(1단원 「물리적 모델링」).

### 1-3. 테이블 구조 확인하기 {keep}

만들어진 테이블의 구조는 **`information_schema.columns`** 를 조회하면 볼 수 있습니다. DBeaver·pgAdmin·psql 어디서나 똑같이 동작합니다.

:::cols
```sql
SELECT column_name
     , data_type
     , character_maximum_length AS max_len
     , is_nullable
     , column_default
  FROM information_schema.columns
 WHERE table_schema = 'bom'
   AND table_name   = 'part_master'
 ORDER BY ordinal_position;
```

```result
| column_name | data_type | max_len | is_nullable | column_default |
| --- | --- | --- | --- | --- |
| part_no | character | 11 | NO | NULL |
| description | text | NULL | NO | NULL |
| description_kr | text | NULL | YES | NULL |
| class_lv1 | character | 1 | NO | NULL |
| class_lv2 | character | 3 | NO | NULL |
| tech_spec | text | NULL | YES | NULL |
| uom | character | 2 | YES | NULL |
| uit | character | 1 | YES | NULL |
| status_code | smallint | NULL | YES | NULL |
| svc_code | character | 1 | YES | NULL |
| svc_location_no | text | NULL | YES | NULL |
| created_at | date | NULL | YES | NULL |
```
:::

### 1-3. 결과 읽기 {keep}

- `is_nullable = NO`인 컬럼은 `NOT NULL`(또는 PK)이 걸려 있다는 뜻입니다.
- `CHAR`는 `character`로, `INT`는 `integer`로 표시됩니다. 같은 자료형의 **정식 이름**입니다.

> **psql을 쓴다면** `\d bom.part_master` 한 줄로 컬럼·PK·FK·「이 테이블을 참조하는 테이블」까지 한 번에 볼 수 있습니다. `\d`는 psql 전용 명령이라 DBeaver에서는 동작하지 않습니다.

### 1-4. 연습 공간 만들기 — lab 스키마 ⭐ {keep}

DDL은 **테이블 자체를** 바꾸거나 지웁니다. 실수로 `bom`의 원본 테이블을 건드리면 Day 1~3에 배운 쿼리 결과가 모두 달라집니다. 그래서 연습용 스키마 `lab`을 따로 만들고, 그 안에서만 실습합니다.

```sql
CREATE SCHEMA lab;
SET search_path TO lab, bom;
```

```sql
SELECT current_schemas(false);
```

```result
| current_schemas |
| --- |
| {lab,bom} |
```

### 1-4. search_path — 스키마를 찾아보는 순서 {keep}

- `search_path`는 「스키마 이름을 생략했을 때 찾아볼 순서」입니다. 이제 **새로 만드는 테이블은 맨 앞의 `lab`** 에 생기고, `part_master`처럼 이름만 쓰면 `lab`에 없으니 `bom`에서 찾습니다.
- 원본을 가리킬 때는 이 교안처럼 ==`bom.part_master`, `bom.vendor`로 스키마를 붙여 쓰는 습관==을 들이세요. 어느 테이블을 읽는지 헷갈리지 않습니다.

:::teacher 강사 확인
- `search_path`는 접속(세션)마다 초기화됩니다. 쉬는 시간 뒤 DBeaver를 다시 연결했다면 `SET search_path TO lab, bom;`부터 다시 실행하게 하세요. 테이블이 `public`에 만들어졌다는 질문이 나오면 대부분 이 원인입니다.
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

### 2-2. PostgreSQL 자료형 — BOM 데이터에 쓰인 것부터 {keep}

| 자료형 | 저장하는 값 | BOM 데이터 예 |
| --- | --- | --- |
| `CHAR(n)` | **정확히 n글자**인 문자 (짧으면 뒤를 공백으로 채움) | `part_no CHAR(11)`, `uit CHAR(1)`, `site_code CHAR(2)` |
| `VARCHAR(n)` | **최대 n글자**인 문자 | (6장 `reviewed_by VARCHAR(30)`) |
| `TEXT` | 길이 제한 없는 문자 | `description`, `change_reason` |
| `SMALLINT` / `INT` / `BIGINT` | 정수 (작은 / 보통 / 큰) | `status_code SMALLINT`, `plan_qty INT` |
| `NUMERIC(p, s)` | 전체 p자리, 소수 s자리인 **정확한** 숫자 | `qty_per NUMERIC(10,3)`, `po_price NUMERIC(12,2)` |
| `DATE` | 날짜 | `plan_date`, `eta_date` |
| `TIMESTAMP` | 날짜 + 시각 | (6장 `created_at TIMESTAMP`) |
| `BOOLEAN` | 참/거짓 | — |

- 품번·UIT·사이트 코드처럼 **길이가 정해진 코드**는 `CHAR(n)`, 이름·사유처럼 **길이가 제각각인 글**은 `VARCHAR(n)` 또는 `TEXT`를 씁니다.
- 수량·단가는 `NUMERIC`을 씁니다. 소요량 `0.002`(테이프) 같은 값을 오차 없이 저장해야 하기 때문입니다.

### 2-3. NOT NULL과 DEFAULT — 테이블 만들기 {keep}

부품별 메모를 남기는 테이블을 만들어 봅니다.

```sql
CREATE TABLE part_memo (
      memo_id     INT          NOT NULL
    , part_no     CHAR(11)     NOT NULL
    , memo        TEXT
    , writer      VARCHAR(20)  DEFAULT '미지정'
    , memo_date   DATE
);
```

```sql
SELECT table_schema, table_name
  FROM information_schema.tables
 WHERE table_name = 'part_memo';
```

```result
| table_schema | table_name |
| --- | --- |
| lab | part_memo |
```

`search_path` 덕분에 `lab` 스키마에 만들어졌습니다.

### 2-3. 값을 안 주면 vs NULL을 주면 {keep}

이제 행을 두 개 넣어 봅니다. (INSERT 문법은 DML 단원에서 자세히 다룹니다. 지금은 「괄호 안 컬럼에 VALUES의 값을 순서대로 넣는다」로만 읽으세요.)

```sql
INSERT INTO part_memo (memo_id, part_no, memo, memo_date)
VALUES (1, 'ECP39799101', '12/4 결품 예상', '2026-11-30');

INSERT INTO part_memo (memo_id, part_no, writer)
VALUES (2, 'EIC93178801', NULL);
```

```sql
SELECT * FROM part_memo ORDER BY memo_id;
```

```result
| memo_id | part_no | memo | writer | memo_date |
| --- | --- | --- | --- | --- |
| 1 | ECP39799101 | 12/4 결품 예상 | 미지정 | 2026-11-30 |
| 2 | EIC93178801 | NULL | NULL | NULL |
```

- 1번 행은 `writer`를 **아예 적지 않았으므로** 기본값 `'미지정'`이 들어갔습니다.
- 2번 행은 `writer`에 **NULL을 직접 적었으므로** NULL이 들어갔습니다. ==DEFAULT는 「값을 안 줬을 때」만 동작하고, NULL을 명시하면 NULL이 들어갑니다.==

### 2-3. NOT NULL 컬럼을 비우면 {keep}

:::error NOT NULL 컬럼을 비우면
```sql
INSERT INTO part_memo (memo_id, memo)
VALUES (3, '품번을 빠뜨림');
```

```error
ERROR:  null value in column "part_no" of relation "part_memo" violates not-null constraint
DETAIL:  Failing row contains (3, null, 품번을 빠뜨림, 미지정, null).
```

`DETAIL`의 괄호는 **들어가려던 행 전체**입니다. 어느 컬럼이 비었는지(`part_no` 자리가 `null`)를 바로 확인할 수 있습니다.
:::

### 2-4. 자료형의 크기를 넘으면 {keep}

:::error CHAR(n)·VARCHAR(n)보다 긴 값
```sql
INSERT INTO part_memo (memo_id, part_no)
VALUES (3, 'EIC93178801X');
```

```error
ERROR:  value too long for type character(11)
```

```sql
INSERT INTO part_memo (memo_id, part_no, writer)
VALUES (3, 'EIC93178801', 'Manufacturing Engineering');
```

```error
ERROR:  value too long for type character varying(20)
```

`'Manufacturing Engineering'`은 `uit_change_history.changed_by_dept`에 실제로 있는 값입니다(25글자). 부서명을 담을 컬럼을 `VARCHAR(20)`으로 만들었다면 이 이력을 옮겨 담을 수 없습니다. ==컬럼 크기는 「지금 떠오르는 값」이 아니라 「들어올 수 있는 가장 긴 값」 기준==으로 정합니다.
:::

### 2-4. CHAR(n)은 짧은 값을 공백으로 채웁니다 {keep}

```sql
INSERT INTO part_memo (memo_id, part_no)
VALUES (3, 'ECP');
```

```sql
SELECT memo_id, part_no, length(part_no) AS len, octet_length(part_no) AS bytes
  FROM part_memo
 WHERE memo_id = 3;
```

```result
| memo_id | part_no | len | bytes |
| --- | --- | --- | --- |
| 3 | ECP         | 3 | 11 |
```

3글자 `'ECP'`가 **오류 없이** 들어가 뒤에 공백 8칸이 채워졌습니다(저장 11바이트). `CHAR(11)`은 「11글자 이하면 받는다」이지 「11글자여야 한다」가 아닙니다.

### 2-4. 정확히 11자리인지까지 막으려면 — CHECK {keep}

품번이 정확히 11자리인지까지 막으려면 3장의 **CHECK** 제약이 필요합니다.

```sql
CREATE TABLE m ( part_no CHAR(11) CONSTRAINT m_len_ck CHECK (length(part_no) = 11) );
INSERT INTO m VALUES ('ECP');
```

```error
ERROR:  new row for relation "m" violates check constraint "m_len_ck"
DETAIL:  Failing row contains (ECP        ).
```

(확인용 테이블 `m`은 바로 `DROP TABLE m;`으로 지웁니다.)

### 2-4. VARCHAR(n)의 n은 바이트가 아니라 글자 수 {keep}

```sql
INSERT INTO part_memo (memo_id, part_no, writer)
VALUES (4, 'MGL96663301', '자재팀 수입자재 담당 김부장님');
```

```sql
SELECT memo_id, writer, length(writer) AS len, octet_length(writer) AS bytes
  FROM part_memo
 WHERE memo_id = 4;
```

```result
| memo_id | writer | len | bytes |
| --- | --- | --- | --- |
| 4 | 자재팀 수입자재 담당 김부장님 | 16 | 42 |
```

42바이트지만 16글자이므로 `VARCHAR(20)`에 들어갑니다. 한글 이름·사유를 담을 컬럼도 **글자 수로** 크기를 정하면 됩니다.

### 2-4. NUMERIC(p, s)의 자릿수를 넘으면 {keep}

:::error NUMERIC(p, s)의 자릿수를 넘으면
```sql
CREATE TABLE price_test ( price NUMERIC(5,2) );

INSERT INTO price_test VALUES (123.456);
INSERT INTO price_test VALUES (1234.5);
```

```error
ERROR:  numeric field overflow
DETAIL:  A field with precision 5, scale 2 must round to an absolute value less than 10^3.
```

```sql
SELECT * FROM price_test;
```

```result
| price |
| --- |
| 123.46 |
```

- `NUMERIC(5,2)`는 전체 5자리 중 소수 2자리 → **정수부는 3자리(999.99)까지**입니다. `1234.5`는 오류입니다.
- 소수 자릿수가 넘치는 `123.456`은 오류 없이 **`123.46`으로 반올림**되어 들어갔습니다. 오류가 안 나는 쪽이 더 조심해야 할 쪽입니다.
:::

### 2-5. 이름 규칙 {keep}

| 규칙 | 예 |
| --- | --- |
| 한 스키마 안에서 **테이블 이름은 중복 불가** | `relation "part_memo" already exists` |
| 한 테이블 안에서 **컬럼 이름은 중복 불가** | `column "part_no" specified more than once` |
| 문자(또는 `_`)로 시작, **예약어는 그대로 못 씀** | `order`, `select`, `table` … |
| 따옴표 없이 쓴 이름은 **소문자로 바뀜** | `Line_Info` → `line_info` |

### 2-5. 중복 이름 · 예약어 {keep}

```sql
CREATE TABLE part_memo ( memo_id INT );
```

```error
ERROR:  relation "part_memo" already exists
```

```sql
CREATE TABLE dup_col ( part_no CHAR(11), part_no TEXT );
```

```error
ERROR:  column "part_no" specified more than once
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
CREATE TABLE Line_Info ( Line_Code TEXT );
```

```sql
SELECT table_name, column_name
  FROM information_schema.columns
 WHERE table_schema = 'lab'
   AND table_name   = 'line_info';
```

```result
| table_name | column_name |
| --- | --- |
| line_info | line_code |
```

```sql
SELECT * FROM LINE_INFO;        -- 성공 (line_info로 바뀌어 찾음)
SELECT * FROM "Line_Info";      -- 실패
```

```error
ERROR:  relation "Line_Info" does not exist
LINE 1: SELECT * FROM "Line_Info";
                      ^
```

### 2-5. 큰따옴표 이름은 피합니다 {keep}

큰따옴표로 감싸면 **쓴 그대로**(대소문자, 예약어 포함) 이름이 됩니다. 그 대신 그 테이블을 쓸 때마다 매번 큰따옴표를 붙여야 합니다. ==테이블·컬럼 이름은 영문 소문자와 `_`만으로== 짓는 것이 가장 덜 헷갈립니다. BOM 데이터셋(`part_master`, `child_part_no`)도 이 규칙을 따릅니다.

연습용으로 만든 두 테이블은 지웁니다(DROP은 5장).

```sql
DROP TABLE price_test;
DROP TABLE line_info;
```

### 2-6. CREATE TABLE ... AS SELECT — 연습용 사본 만들기 ⭐ {keep}

`SELECT` 결과를 그대로 새 테이블로 만들 수 있습니다. 줄여서 **CTAS**라고 부릅니다. Day 4에서 원본 대신 **사본으로 DML을 연습**할 때 이 방법을 씁니다.

```text CTAS의 모양
CREATE TABLE 새테이블 AS
SELECT ... FROM 원본 [WHERE 조건];
```

```sql
CREATE TABLE sourcing_copy AS
SELECT * FROM bom.part_sourcing;
```

```result
SELECT 52
```

### 2-6. 조건으로 고르기 · 컬럼만 고르기 {keep}

```sql
CREATE TABLE bom_wm AS
SELECT *
  FROM bom.bom_structure
 WHERE model_part_no = 'TWM61868701';
```

```sql
SELECT COUNT(*) AS cnt FROM bom_wm;
```

```result
| cnt |
| --- |
| 43 |
```

- 소싱 52행 전체, 세탁기 BOM 43행만 골라 사본을 만들었습니다(서브쿼리 단원 5-3의 세탁기 BOM 행 수와 같습니다).
- 필요한 컬럼만 골라 만들 수도 있습니다.

```sql
CREATE TABLE vendor_copy AS
SELECT vendor_code, vendor_name, country, is_domestic
  FROM bom.vendor;
```

### 2-6. 구조만 복사 — WITH NO DATA {keep}

**구조만** 필요하면 `WITH NO DATA`를 붙입니다.

```sql
CREATE TABLE plan_empty AS
SELECT * FROM bom.production_plan
WITH NO DATA;
```

```sql
SELECT COUNT(*) AS cnt FROM plan_empty;
```

```result
| cnt |
| --- |
| 0 |
```

### 2-6. CTAS는 제약조건을 복사하지 않습니다 ① {keep}

:::error CTAS는 제약조건을 복사하지 않습니다
원본 `part_sourcing`과 사본 `sourcing_copy`의 제약조건을 비교합니다. (`pg_constraint`는 3-5에서 자세히 봅니다. `contype`이 p = PK, f = FK입니다.)

```sql
SELECT conrelid::regclass AS table_name, contype, COUNT(*) AS cnt
  FROM pg_constraint
 WHERE conrelid IN ('bom.part_sourcing'::regclass, 'lab.sourcing_copy'::regclass)
   AND contype IN ('p', 'u', 'c', 'f')
 GROUP BY conrelid, contype
 ORDER BY 1, 2;
```

```result
| table_name | contype | cnt |
| --- | --- | --- |
| part_sourcing | f | 3 |
| part_sourcing | p | 1 |
```

사본(`sourcing_copy`)의 행이 **하나도 없습니다.** PK도 FK도 없다는 뜻입니다.
:::

### 2-6. CTAS는 제약조건을 복사하지 않습니다 ② NOT NULL {keep}

NOT NULL도 따라오지 않습니다.

```sql
SELECT table_schema, table_name, column_name, is_nullable
  FROM information_schema.columns
 WHERE (table_schema, table_name) IN (('bom','part_sourcing'), ('lab','sourcing_copy'))
   AND column_name = 'part_no'
 ORDER BY 1;
```

```result
| table_schema | table_name | column_name | is_nullable |
| --- | --- | --- | --- |
| bom | part_sourcing | part_no | NO |
| lab | sourcing_copy | part_no | YES |
```

### 2-6. CTAS는 제약조건을 복사하지 않습니다 ③ 중복이 들어감 {keep}

그래서 원본이라면 막혔을 **중복 행**이 사본에는 그냥 들어갑니다.

```sql
INSERT INTO sourcing_copy
SELECT * FROM bom.part_sourcing WHERE part_no = 'ECP39799101';
```

```sql
SELECT part_no, vendor_code, site_code, COUNT(*) AS cnt
  FROM sourcing_copy
 GROUP BY part_no, vendor_code, site_code
HAVING COUNT(*) > 1;
```

```result
| part_no | vendor_code | site_code | cnt |
| --- | --- | --- | --- |
| ECP39799101 | V1004 | CW | 2 |
```

CTAS는 ==데이터와 컬럼(이름·자료형)만 복사==합니다. 사본에도 규칙이 필요하면 3장의 방법으로 제약조건을 다시 걸어야 합니다(3-6에서 이 중복 때문에 PK가 실패하는 것을 봅니다).

### 2-7. 확인 문제 — 회원 테이블 · HR 데이터 {keep}

> 실행 전: `SET search_path TO lab, hr;` (HR 실습 데이터 `hr_postgres.sql`의 `hr` 스키마. 테이블은 `lab`에 만들어집니다.)

:::try
**[복습]** (기존 교안 `9. DDL.pptx` 20번) 아래 조건으로 회원 테이블 `member`를 만들고, 이름 없이 회원 한 명(`'kim01'`, 비밀번호 `'pw1234'`)을 넣었을 때 어떤 오류가 나는지 확인하세요. 그다음 이름 `'김생산'`, 성별 `'남'`으로 다시 넣으세요.

| 컬럼 | 자료형 | 조건 |
| --- | --- | --- |
| `member_id` | 가변 문자 15글자 | |
| `member_name` | 가변 문자 12글자 | NULL 불가 |
| `passwd` | 가변 문자 16글자 | |
| `birth_date` | 날짜 | |
| `gender` | 가변 문자 3글자 | |

**[응용]** `employees`에서 **부서 50(Shipping)** 직원의 사번, 이름(first/last), 급여, 입사일만 골라 `emp_ship` 사본을 만드세요. 몇 행인지 확인하고, 원본 `employees`와 사본 `emp_ship` 중 **PK가 있는 테이블**을 `pg_constraint`로 확인하세요.
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

기존 교안은 「12 BYTE」였지만, PostgreSQL의 `VARCHAR(12)`는 **12글자**까지 받습니다(2-4).
:::

### 2-7. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
45행. PK는 원본에만 있습니다.

```sql
CREATE TABLE emp_ship AS
SELECT employee_id, first_name, last_name, salary, hire_date
  FROM employees
 WHERE department_id = 50;

SELECT COUNT(*) AS cnt FROM emp_ship;
```

```result
| cnt |
| --- |
| 45 |
```

```sql
SELECT conrelid::regclass AS table_name, conname, contype
  FROM pg_constraint
 WHERE conrelid IN ('hr.employees'::regclass, 'lab.emp_ship'::regclass)
   AND contype = 'p';
```

```result
| table_name | conname | contype |
| --- | --- | --- |
| employees | emp_emp_id_pk | p |
```
:::

## 3. 제약조건 — 잘못된 데이터가 들어오지 못하게

### 3-1. 제약조건 다섯 가지 {keep}

**제약조건(constraint)** 은 테이블에 들어올 수 있는 값을 제한하는 **규칙**입니다. 규칙을 어기는 INSERT·UPDATE·DELETE는 DB가 오류로 거부합니다.

| 제약조건 | 규칙 | BOM 데이터 예 |
| --- | --- | --- |
| `PRIMARY KEY` (PK) | **NULL 불가 + 중복 불가.** 행을 구별하는 식별자 | `part_master.part_no`, `part_sourcing (part_no, vendor_code, site_code)` |
| `UNIQUE` (UK) | **중복 불가.** NULL은 허용 | `bom_structure (model_part_no, parent_part_no, child_part_no)` |
| `NOT NULL` | NULL 불가 | `part_master.description` |
| `CHECK` | **조건식이 참인 값만** 허용 | (BOM 원본에는 없음 → 3-6) |
| `FOREIGN KEY` (FK) | **다른 테이블(부모)에 있는 값만** 허용 | `part_master.uit → code_uit.uit` |

### 3-1. 무결성 {keep}

제약조건이 지켜 주는 것을 **무결성(integrity)**, 즉 「데이터에 결함이 없는 상태」라고 합니다.

| 무결성 | 뜻 | 지켜 주는 제약조건 |
| --- | --- | --- |
| 개체 무결성 | 기본키는 NULL일 수 없다 (모든 행은 구별될 수 있어야 한다) | PK |
| 참조 무결성 | 외래키는 부모에 없는 값을 가질 수 없다 | FK |

### 3-2. 제약조건을 거는 세 가지 위치 {keep}

```sql
-- ① 컬럼 옆에 (컬럼 레벨)
insp_id  INT  CONSTRAINT inspection_pk PRIMARY KEY

-- ② 컬럼 목록 끝에 (테이블 레벨) — 여러 컬럼을 묶을 때는 이 방법만 가능
, CONSTRAINT inspection_qty_ck CHECK (sample_qty > 0 AND defect_qty BETWEEN 0 AND sample_qty)

-- ③ 테이블을 만든 뒤에 (ALTER TABLE)
ALTER TABLE 테이블명 ADD CONSTRAINT 제약조건명 제약조건 (컬럼);
```

- `CONSTRAINT 이름`을 생략하면 PostgreSQL이 이름을 자동으로 붙입니다(`part_master_pkey`, `part_master_uit_fkey` …). 오류 메시지에는 **제약조건 이름**이 나오므로, 직접 만드는 테이블은 ==「테이블_컬럼_종류」(예: `inspection_result_ck`)처럼 읽으면 뜻이 보이는 이름==을 붙입니다.
- 이 교안의 접미사: `_pk`(기본키), `_uk`(유니크), `_ck`(체크), `_fk`(외래키)

### 3-3. 수입검사 테이블 만들기 {keep}

입고 부품의 **수입검사 결과**를 기록하는 테이블을 만들어 봅니다. 업체 코드는 2-6에서 만든 `vendor_copy`를 참조하도록 했습니다.

```sql
CREATE TABLE inspection (
      insp_id      INT          CONSTRAINT inspection_pk PRIMARY KEY
    , lot_no       VARCHAR(20)  CONSTRAINT inspection_lot_uk UNIQUE
    , part_no      CHAR(11)     NOT NULL
    , vendor_code  CHAR(5)      NOT NULL
    , insp_date    DATE         NOT NULL
    , sample_qty   INT          NOT NULL
    , defect_qty   INT          NOT NULL DEFAULT 0
    , result       VARCHAR(4)   NOT NULL
    , CONSTRAINT inspection_part_fk   FOREIGN KEY (part_no)     REFERENCES bom.part_master (part_no)
    , CONSTRAINT inspection_vendor_fk FOREIGN KEY (vendor_code) REFERENCES vendor_copy (vendor_code)
    , CONSTRAINT inspection_result_ck CHECK (result IN ('PASS', 'FAIL', 'HOLD'))
    , CONSTRAINT inspection_qty_ck    CHECK (sample_qty > 0 AND defect_qty BETWEEN 0 AND sample_qty)
);
```

```error
ERROR:  there is no unique constraint matching given keys for referenced table "vendor_copy"
```

### 3-3. FK는 PK(또는 UNIQUE)를 가리켜야 한다 {keep}

`vendor_copy`는 CTAS 사본이라 **PK가 없습니다**(2-6). FK가 가리키는 부모 컬럼은 ==PK 또는 UNIQUE여야== 합니다. 부모 값이 중복될 수 있으면 「어느 부모 행을 가리키는지」가 정해지지 않기 때문입니다. 사본에 PK를 먼저 겁니다(위치 ③).

```sql
ALTER TABLE vendor_copy ADD CONSTRAINT vendor_copy_pk PRIMARY KEY (vendor_code);
```

같은 `CREATE TABLE inspection (...)` 문장을 다시 실행하면 이번에는 성공합니다.

### 3-4. 정상 행 넣기 {keep}

```sql
INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty, defect_qty, result)
VALUES (1, 'L2612-0401', 'EBA56264701', 'V1003', '2026-12-04', 80, 0, 'PASS');

INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty, defect_qty, result)
VALUES (2, 'L2612-0501', 'MGL96663301', 'V1007', '2026-12-05', 50, 3, 'FAIL');
```

```sql
SELECT * FROM inspection ORDER BY insp_id;
```

```result
| insp_id | lot_no | part_no | vendor_code | insp_date | sample_qty | defect_qty | result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | L2612-0401 | EBA56264701 | V1003 | 2026-12-04 | 80 | 0 | PASS |
| 2 | L2612-0501 | MGL96663301 | V1007 | 2026-12-05 | 50 | 3 | FAIL |
```

> 품번·업체·날짜는 `scheduled_receipt`의 입고 예정 건을 본떴고, 로트 번호·시료 수·불량 수는 **연습용으로 만든 값**입니다.

### 3-4. PRIMARY KEY — 중복도, NULL도 안 됨 {keep}

```sql
INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty, result)
VALUES (1, 'L2612-0801', 'ECP39799101', 'V1004', '2026-12-08', 32, 'PASS');
```

```error
ERROR:  duplicate key value violates unique constraint "inspection_pk"
DETAIL:  Key (insp_id)=(1) already exists.
```

```sql
INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty, result)
VALUES (NULL, 'L2612-0801', 'ECP39799101', 'V1004', '2026-12-08', 32, 'PASS');
```

```error
ERROR:  null value in column "insp_id" of relation "inspection" violates not-null constraint
DETAIL:  Failing row contains (null, L2612-0801, ECP39799101, V1004, 2026-12-08, 32, 0, PASS).
```

`insp_id`에 `NOT NULL`을 따로 쓰지 않았는데도 NULL이 거부됐습니다. ==PK = NOT NULL + UNIQUE==이기 때문입니다.

### 3-4. UNIQUE — 중복은 안 되지만 NULL은 여러 개 가능 {keep}

```sql
INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty, result)
VALUES (3, 'L2612-0501', 'ECP39799101', 'V1004', '2026-12-08', 32, 'PASS');
```

```error
ERROR:  duplicate key value violates unique constraint "inspection_lot_uk"
DETAIL:  Key (lot_no)=(L2612-0501) already exists.
```

```sql
INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty, result)
VALUES (3, NULL, 'ECP39799101', 'V1004', '2026-12-08', 32, 'PASS');

INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty, result)
VALUES (4, NULL, 'EIC93178801', 'V1005', '2026-12-10', 125, 'HOLD');
```

### 3-4. NULL 로트 번호 두 개가 들어갔습니다 {keep}

```sql
SELECT insp_id, lot_no, part_no, defect_qty, result FROM inspection ORDER BY insp_id;
```

```result
| insp_id | lot_no | part_no | defect_qty | result |
| --- | --- | --- | --- | --- |
| 1 | L2612-0401 | EBA56264701 | 0 | PASS |
| 2 | L2612-0501 | MGL96663301 | 3 | FAIL |
| 3 | NULL | ECP39799101 | 0 | PASS |
| 4 | NULL | EIC93178801 | 0 | HOLD |
```

- 로트 번호가 없는(NULL) 행이 두 개 들어갔습니다. NULL은 「값이 없음」이라 서로 **같다고 보지 않기** 때문입니다(3단원 5-1).
- `defect_qty`를 적지 않은 3·4번 행에는 `DEFAULT 0`이 들어갔습니다.

### 3-4. CHECK — 조건식이 참이어야 함 {keep}

```sql
INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty, result)
VALUES (5, 'L2612-1201', 'RSS86949501', 'V1007', '2026-12-12', 20, 'OK');
```

```error
ERROR:  new row for relation "inspection" violates check constraint "inspection_result_ck"
DETAIL:  Failing row contains (5, L2612-1201, RSS86949501, V1007, 2026-12-12, 20, 0, OK).
```

```sql
INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty, defect_qty, result)
VALUES (5, 'L2612-1201', 'RSS86949501', 'V1007', '2026-12-12', 20, 25, 'FAIL');
```

```error
ERROR:  new row for relation "inspection" violates check constraint "inspection_qty_ck"
DETAIL:  Failing row contains (5, L2612-1201, RSS86949501, V1007, 2026-12-12, 20, 25, FAIL).
```

시료 20개에서 불량 25개는 나올 수 없습니다. `inspection_qty_ck`처럼 ==컬럼 두 개를 비교하는 규칙==은 테이블 레벨(위치 ②)로 씁니다.

### 3-4. FOREIGN KEY — 부모에 있는 값만 {keep}

```sql
INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty, result)
VALUES (5, 'L2612-1201', 'RSS8694950X', 'V1007', '2026-12-12', 20, 'PASS');
```

```error
ERROR:  insert or update on table "inspection" violates foreign key constraint "inspection_part_fk"
DETAIL:  Key (part_no)=(RSS8694950X) is not present in table "part_master".
```

```sql
INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty, result)
VALUES (5, 'L2612-1201', 'RSS86949501', 'V9999', '2026-12-12', 20, 'PASS');
```

```error
ERROR:  insert or update on table "inspection" violates foreign key constraint "inspection_vendor_fk"
DETAIL:  Key (vendor_code)=(V9999) is not present in table "vendor_copy".
```

품번 오타, 등록되지 않은 업체 코드가 **기록되는 순간** 막힙니다. Day 2에 LEFT JOIN으로 찾던 「짝 없는 행」이 처음부터 생기지 않게 하는 것이 FK입니다.

### 3-4. FK는 부모 쪽 삭제도 막습니다 {keep}

```sql
DELETE FROM vendor_copy WHERE vendor_code = 'V1007';
```

```error
ERROR:  update or delete on table "vendor_copy" violates foreign key constraint "inspection_vendor_fk" on table "inspection"
DETAIL:  Key (vendor_code)=(V1007) is still referenced from table "inspection".
```

검사 기록(자식)이 남아 있는 업체(부모)를 지우면, 그 기록은 「존재하지 않는 업체의 검사 결과」가 됩니다. 이것이 **참조 무결성**입니다.

### 3-5. 걸려 있는 제약조건 조회하기 {keep}

```sql
SELECT conname, contype, pg_get_constraintdef(oid) AS definition
  FROM pg_constraint
 WHERE conrelid = 'lab.inspection'::regclass
   AND contype IN ('p', 'u', 'c', 'f')
 ORDER BY contype, conname;
```

```result
| conname | contype | definition |
| --- | --- | --- |
| inspection_qty_ck | c | CHECK (((sample_qty > 0) AND ((defect_qty >= 0) AND (defect_qty <= sample_qty)))) |
| inspection_result_ck | c | CHECK (((result)::text = ANY ((ARRAY['PASS'::character varying, 'FAIL'::character varying, 'HOLD'::character varying])::text[]))) |
| inspection_part_fk | f | FOREIGN KEY (part_no) REFERENCES part_master(part_no) |
| inspection_vendor_fk | f | FOREIGN KEY (vendor_code) REFERENCES vendor_copy(vendor_code) |
| inspection_pk | p | PRIMARY KEY (insp_id) |
| inspection_lot_uk | u | UNIQUE (lot_no) |
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

Day 1~2에 쿼리로 찾아낸 「이상해 보이는 데이터」를, 이번에는 **규칙(제약조건)을 걸어서** 찾아봅니다. 원본을 건드리지 않도록 2-6에서 만든 **사본**에 겁니다.

```icons 세 가지 규칙
ruler | ① CHECK | 소요량은 0보다 커야 한다 | rose
dollar-sign | ② NOT NULL | 구매 단가는 비어 있으면 안 된다 | plum
key-round | ③ PRIMARY KEY | (품번, 업체, 사이트)는 하나여야 한다 | lime
```

### 3-6. ① 소요량은 0보다 커야 한다 {keep}

```sql
ALTER TABLE bom_wm ADD CONSTRAINT bom_wm_qty_ck CHECK (qty_per > 0);
```

```error
ERROR:  check constraint "bom_wm_qty_ck" of relation "bom_wm" is violated by some row
```

제약조건을 **나중에** 걸면, PostgreSQL은 이미 들어 있는 행을 모두 검사합니다. 한 행이라도 어기면 제약조건 자체가 만들어지지 않습니다. 어긴 행은 조건을 뒤집어 찾습니다.

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

### 3-6. ② 구매 단가는 비어 있으면 안 된다 {keep}

```sql
ALTER TABLE sourcing_copy ALTER COLUMN po_price SET NOT NULL;
```

```error
ERROR:  column "po_price" of relation "sourcing_copy" contains null values
```

```sql
SELECT part_no, vendor_code, po_price
  FROM sourcing_copy
 WHERE po_price IS NULL;
```

```result
| part_no | vendor_code | po_price |
| --- | --- | --- |
| MFT43979901 | V1010 | NULL |
```

정수 필터(`MFT43979901`)의 단가가 NULL입니다. Day 3 재료비 계산에서 냉장고 합계를 왜곡한 그 행입니다.

### 3-6. ③ (품번, 업체, 사이트)는 하나여야 한다 {keep}

```sql
ALTER TABLE sourcing_copy ADD CONSTRAINT sourcing_copy_pk PRIMARY KEY (part_no, vendor_code, site_code);
```

```error
ERROR:  could not create unique index "sourcing_copy_pk"
DETAIL:  Key (part_no, vendor_code, site_code)=(ECP39799101, V1004, CW) is duplicated.
```

2-6에서 사본에 일부러 넣은 중복 행 때문입니다. 원본 `part_sourcing`에는 PK가 있어 이런 중복이 들어갈 수 없습니다.

### 3-6. 쿼리 점검은 사후에, 제약조건은 들어오는 순간 {keep}

| 원본 `bom`에 이 규칙이 있었다면 | 막혔을 이상 데이터 | 처음 찾은 곳 |
| --- | --- | --- |
| `CHECK (qty_per > 0)` | 소요량 0인 BOM 행 | Day 1 7교시 |
| `po_price NOT NULL` | 단가가 빈 소싱 행 | Day 1 7교시, Day 3 4교시 |
| PK `(part_no, vendor_code, site_code)` | 같은 소싱 조건 중복 (원본에는 PK가 있어 없음) | — |

==쿼리로 하는 품질 점검은 「이미 들어온 데이터」를 사후에 찾고, 제약조건은 「들어오는 순간」 막습니다.== 그래서 판단 결과를 기록하는 테이블(6장)을 만들 때는 처음부터 제약조건을 함께 설계합니다.

### 3-6. 사본 정리 — 다시 만들고 PK 걸기 {keep}

중복이 들어간 사본은 지우고 다시 만든 뒤 PK를 겁니다.

```sql
DROP TABLE sourcing_copy;

CREATE TABLE sourcing_copy AS
SELECT * FROM bom.part_sourcing;

ALTER TABLE sourcing_copy
  ADD CONSTRAINT sourcing_copy_pk PRIMARY KEY (part_no, vendor_code, site_code);
```

이번에는 오류 없이 만들어집니다.

### 3-6. 앞으로 들어올 행만 막기 — NOT VALID {keep}

현장 DB에서는 「기존 이상 데이터는 담당 부서가 정리 중이니, 일단 **새로 들어오는 것만** 막자」는 경우가 있습니다. `CHECK`와 `FOREIGN KEY`는 `NOT VALID`를 붙이면 기존 행 검사를 건너뜁니다.

```sql
ALTER TABLE bom_wm ADD CONSTRAINT bom_wm_qty_ck CHECK (qty_per > 0) NOT VALID;
```

```sql
INSERT INTO bom_wm (bom_id, model_part_no, parent_part_no, child_part_no, bom_level, qty_per)
VALUES (999, 'TWM61868701', 'EMT68237401', 'FSC33042701', 3, 0);
```

```error
ERROR:  new row for relation "bom_wm" violates check constraint "bom_wm_qty_ck"
DETAIL:  Failing row contains (999, TWM61868701, EMT68237401, FSC33042701, 3, 0.000, null, null, null, null).
```

### 3-6. convalidated와 VALIDATE CONSTRAINT {keep}

```sql
SELECT conname, convalidated FROM pg_constraint WHERE conname = 'bom_wm_qty_ck';
```

```result
| conname | convalidated |
| --- | --- |
| bom_wm_qty_ck | f |
```

- 새 행(소요량 0)은 막혔습니다. `convalidated = f`는 「기존 행은 아직 검증하지 않았다」는 표시입니다.
- 기존 행 정리가 끝나면 `VALIDATE CONSTRAINT`로 검증을 완료합니다. 아직 bom_id 70이 남아 있으므로 지금은 실패합니다.

```sql
ALTER TABLE bom_wm VALIDATE CONSTRAINT bom_wm_qty_ck;
```

```error
ERROR:  check constraint "bom_wm_qty_ck" of relation "bom_wm" is violated by some row
```

:::teacher 강사 확인
- ①은 README 4장 이상 데이터 **A5**(DD모터 → 나사 M4, `bom_id` 70), ②는 **A4**(`MFT43979901` 단가 NULL)입니다. 훈련생에게 A 번호는 말하지 말고 「Day 1·3에 찾은 그 행」으로 연결하세요.
- `NOT VALID`는 PostgreSQL 16 기준 **CHECK·FK에만** 쓸 수 있습니다. 공식 문서 최신판(18)은 NOT NULL에도 허용한다고 적고 있으므로, 수업 PC(18)에서 NOT NULL에 `NOT VALID`를 써 보는 질문이 나오면 직접 실행해 확인하세요. 이 교안은 16에서 검증한 CHECK만 다룹니다.
- 원본 `bom` 테이블에 제약조건을 추가하는 것은 이 수업 범위가 아닙니다. 「현장에서는 DBA·담당 부서 승인 후 진행」으로 정리하세요.
:::

### 3-7. 확인 문제 — 블로그 테이블 · HR 데이터 {keep}

> 실행 전: `SET search_path TO lab, hr;`

:::try
**[복습]** (기존 교안 `9. DDL.pptx` 21~22번) 블로그 테이블 `blog`를 아래 구조로 만들고, 제약조건 4개를 `ALTER TABLE ... ADD CONSTRAINT`로 추가하세요. 그다음 ① 성별이 `'M'`인 회원 `'lee02'`(이름 `'이품질'`), ② 없는 회원 `'park03'`의 글, ③ `'kim01'`의 글(1번, 제목 `'첫 글'`)을 차례로 넣어 결과를 확인하세요.

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

**[응용]** `employees`의 사번, 이름, 급여, 직책, 부서 번호로 `emp_copy` 사본을 만들고, 「급여는 2500 이상 20000 이하」 CHECK(`emp_copy_sal_ck`)를 추가하세요. 실패한다면 **규칙을 어기는 직원**을 찾고, 기존 직원은 그대로 둔 채 **새 직원부터** 규칙을 적용하세요. 마지막으로 `employee_id` PK와 `department_id` → `departments` FK도 추가하세요. 부서가 NULL인 직원이 있는데 FK가 성공하는 이유는?
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

### 3-7. 확인 문제 답 — 응용 ① 규칙을 어기는 직원 {keep}

:::answer [응용] 예시 답안 ①
규칙을 어기는 직원은 6명입니다.

```sql
CREATE TABLE emp_copy AS
SELECT employee_id, first_name, salary, job_id, department_id
  FROM employees;

ALTER TABLE emp_copy ADD CONSTRAINT emp_copy_sal_ck CHECK (salary BETWEEN 2500 AND 20000);
```

```error
ERROR:  check constraint "emp_copy_sal_ck" of relation "emp_copy" is violated by some row
```

```sql
SELECT employee_id, first_name, salary
  FROM emp_copy
 WHERE NOT (salary BETWEEN 2500 AND 20000)
 ORDER BY salary;
```

```result
| employee_id | first_name | salary |
| --- | --- | --- |
| 132 | TJ | 2100.00 |
| 128 | Steven | 2200.00 |
| 136 | Hazel | 2200.00 |
| 127 | James | 2400.00 |
| 135 | Ki | 2400.00 |
| 100 | Steven | 24000.00 |
```
:::

### 3-7. 확인 문제 답 — 응용 ② 새 직원부터 · PK · FK {keep}

:::answer [응용] 예시 답안 ②
```sql
ALTER TABLE emp_copy ADD CONSTRAINT emp_copy_sal_ck CHECK (salary BETWEEN 2500 AND 20000) NOT VALID;

INSERT INTO emp_copy (employee_id, first_name, salary, job_id) VALUES (300, 'Test', 2000, 'ST_CLERK');
```

```error
ERROR:  new row for relation "emp_copy" violates check constraint "emp_copy_sal_ck"
DETAIL:  Failing row contains (300, Test, 2000.00, ST_CLERK, null).
```

```sql
ALTER TABLE emp_copy ADD CONSTRAINT emp_copy_pk      PRIMARY KEY (employee_id);
ALTER TABLE emp_copy ADD CONSTRAINT emp_copy_dept_fk FOREIGN KEY (department_id) REFERENCES departments (department_id);
```

두 문장 모두 성공합니다. 178번 Kimberely는 부서가 NULL이지만, **FK는 NULL을 검사하지 않습니다**(「부모를 가리키지 않음」으로 봄). 부서가 반드시 있어야 한다면 `department_id`에 `NOT NULL`을 따로 걸어야 합니다.
:::

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

3장의 `inspection`에 검사자와 판단 주체 컬럼을 추가합니다.

```sql
ALTER TABLE inspection ADD COLUMN inspector VARCHAR(30);
ALTER TABLE inspection ADD COLUMN judged_by VARCHAR(5) NOT NULL DEFAULT 'HUMAN';
```

```sql
SELECT insp_id, result, inspector, judged_by FROM inspection ORDER BY insp_id;
```

```result
| insp_id | result | inspector | judged_by |
| --- | --- | --- | --- |
| 1 | PASS | NULL | HUMAN |
| 2 | FAIL | NULL | HUMAN |
| 3 | PASS | NULL | HUMAN |
| 4 | HOLD | NULL | HUMAN |
```

- 기본값 없이 추가한 `inspector`는 기존 행이 모두 **NULL**입니다.
- `DEFAULT 'HUMAN'`과 함께 추가한 `judged_by`는 ==기존 행에도 기본값이 채워졌습니다.== 지금까지의 검사 기록은 사람이 판단한 것이라는 뜻으로 남길 수 있습니다.

### 4-2. 기본값 없는 NOT NULL 컬럼 추가 {keep}

:::error 데이터가 있는 테이블에 「기본값 없는 NOT NULL」 컬럼 추가
```sql
ALTER TABLE inspection ADD COLUMN remark TEXT NOT NULL;
```

```error
ERROR:  column "remark" of relation "inspection" contains null values
```

새 컬럼은 기존 행에서 NULL로 시작하는데, 동시에 NOT NULL을 요구하니 모순입니다. **`DEFAULT`를 함께 주거나**, NULL 허용으로 추가한 뒤 값을 채우고(DML) 나서 `SET NOT NULL`을 겁니다.
:::

### 4-3. 자료형 변경 — 줄이기와 늘리기 {keep}

:::error 들어 있는 값보다 작게 줄이기
```sql
ALTER TABLE inspection ALTER COLUMN lot_no TYPE VARCHAR(8);
```

```error
ERROR:  value too long for type character varying(8)
```

로트 번호 `'L2612-0401'`(10글자)이 들어 있어 8글자로 줄일 수 없습니다. 늘리는 것은 문제없습니다.
:::

```sql
ALTER TABLE inspection ALTER COLUMN lot_no TYPE VARCHAR(30);
```

### 4-3. 기본값 설정 {keep}

판정을 적지 않으면 `'HOLD'`(보류)로 기록되게 합니다.

```sql
ALTER TABLE inspection ALTER COLUMN result SET DEFAULT 'HOLD';

INSERT INTO inspection (insp_id, lot_no, part_no, vendor_code, insp_date, sample_qty)
VALUES (5, 'L2612-1201', 'RSS86949501', 'V1007', '2026-12-12', 20);
```

```sql
SELECT insp_id, lot_no, result, judged_by FROM inspection WHERE insp_id = 5;
```

```result
| insp_id | lot_no | result | judged_by |
| --- | --- | --- | --- |
| 5 | L2612-1201 | HOLD | HUMAN |
```

> 「판정을 안 적으면 합격」보다 「판정을 안 적으면 보류」가 안전합니다. ==기본값은 「실수했을 때 덜 위험한 값」== 으로 정합니다.

### 4-3. NOT NULL 설정 / 해제 {keep}

```sql
ALTER TABLE inspection ALTER COLUMN lot_no SET NOT NULL;
```

```error
ERROR:  column "lot_no" of relation "inspection" contains null values
```

3-4에서 로트 번호 없이 넣은 3·4번 행 때문입니다. 3-6 ②(`po_price`)와 같은 오류입니다.

```sql
ALTER TABLE inspection ALTER COLUMN inspector DROP NOT NULL;
```

`inspector`는 처음부터 NULL 허용이라 바뀌는 것이 없지만, 문법은 이렇게 씁니다.

### 4-4. 컬럼 이름 변경 {keep}

```sql
ALTER TABLE inspection RENAME COLUMN result TO insp_result;
```

```sql
SELECT conname, pg_get_constraintdef(oid) AS definition
  FROM pg_constraint
 WHERE conname = 'inspection_result_ck';
```

```result
| conname | definition |
| --- | --- |
| inspection_result_ck | CHECK (((insp_result)::text = ANY ((ARRAY['PASS'::character varying, 'FAIL'::character varying, 'HOLD'::character varying])::text[]))) |
```

컬럼 이름을 바꾸면 그 컬럼에 걸린 **CHECK 조건식도 새 이름으로 따라 바뀝니다.** 다만 제약조건 **이름**(`inspection_result_ck`)은 그대로입니다. 그 컬럼을 쓰던 **SELECT 쿼리는 자동으로 바뀌지 않으므로** 직접 고쳐야 합니다.

### 4-4. 컬럼 삭제 · 테이블 이름 변경 {keep}

```sql
ALTER TABLE inspection DROP COLUMN inspector;
ALTER TABLE inspection RENAME TO incoming_insp;
```

```sql
SELECT column_name, data_type, character_maximum_length AS max_len, is_nullable, column_default
  FROM information_schema.columns
 WHERE table_schema = 'lab'
   AND table_name   = 'incoming_insp'
 ORDER BY ordinal_position;
```

```result
| column_name | data_type | max_len | is_nullable | column_default |
| --- | --- | --- | --- | --- |
| insp_id | integer | NULL | NO | NULL |
| lot_no | character varying | 30 | YES | NULL |
| part_no | character | 11 | NO | NULL |
| vendor_code | character | 5 | NO | NULL |
| insp_date | date | NULL | NO | NULL |
| sample_qty | integer | NULL | NO | NULL |
| defect_qty | integer | NULL | NO | 0 |
| insp_result | character varying | 4 | NO | 'HOLD'::character varying |
| judged_by | character varying | 5 | NO | 'HUMAN'::character varying |
```

4장에서 바꾼 것(추가 `judged_by`, 삭제 `inspector`, 길이 `lot_no` 30, 이름 `insp_result`, 기본값 `'HOLD'`)이 모두 반영됐습니다.

### 4-4. 제약조건 삭제 {keep}

로트 번호 중복 허용으로 바꿉니다.

```sql
ALTER TABLE incoming_insp DROP CONSTRAINT inspection_lot_uk;
```

```sql
SELECT conname, contype
  FROM pg_constraint
 WHERE conrelid = 'lab.incoming_insp'::regclass
   AND contype IN ('p', 'u', 'c', 'f')
 ORDER BY contype, conname;
```

```result
| conname | contype |
| --- | --- |
| inspection_qty_ck | c |
| inspection_result_ck | c |
| inspection_part_fk | f |
| inspection_vendor_fk | f |
| inspection_pk | p |
```

> 테이블 이름을 `incoming_insp`로 바꿔도 제약조건 이름은 `inspection_…`으로 남아 있습니다. 이름 규칙(3-2)을 지키려면 `ALTER TABLE … RENAME CONSTRAINT 옛이름 TO 새이름;`으로 함께 바꿔 줍니다.

### 4-5. 확인 문제 — 블로그 테이블 · HR 데이터 {keep}

> 실행 전: `SET search_path TO lab, hr;`

:::try
**[복습]** 3-7의 `blog` 테이블을 다음과 같이 고친 뒤, `information_schema.columns`로 결과를 확인하세요.
① 조회수 `view_cnt`(정수, NULL 불가, 기본값 0) 추가 ② `content` → `body`로 이름 변경 ③ `title`을 200글자로 늘리기

**[응용]** 2-7의 `emp_ship`에 보너스 비율 `bonus_pct NUMERIC(3,2) NOT NULL`을 추가하려니 오류가 납니다. 이유를 설명하고, **한 문장으로** 추가하는 방법을 쓰세요. 추가 후 45명 모두의 값이 어떻게 되었는지 확인하세요.
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
ALTER TABLE emp_ship ADD COLUMN bonus_pct NUMERIC(3,2) NOT NULL;
```

```error
ERROR:  column "bonus_pct" of relation "emp_ship" contains null values
```

이미 45행이 있는데 새 컬럼은 NULL로 시작하므로 NOT NULL을 만족할 수 없습니다(4-2). 기본값을 함께 줍니다.

```sql
ALTER TABLE emp_ship ADD COLUMN bonus_pct NUMERIC(3,2) NOT NULL DEFAULT 0;

SELECT COUNT(*) AS cnt, MIN(bonus_pct) AS min_pct, MAX(bonus_pct) AS max_pct FROM emp_ship;
```

```result
| cnt | min_pct | max_pct |
| --- | --- | --- |
| 45 | 0.00 | 0.00 |
```
:::

## 5. DROP · TRUNCATE — 지우기

### 5-1. DROP TABLE — 테이블 통째로 삭제 {keep}

```text DROP TABLE의 모양
DROP TABLE [IF EXISTS] 테이블명 [CASCADE];
```

:::error 다른 테이블이 참조하는 테이블은 지울 수 없음
`incoming_insp`(옛 `inspection`)의 FK가 `vendor_copy`를 참조하고 있습니다.

```sql
DROP TABLE vendor_copy;
```

```error
ERROR:  cannot drop table vendor_copy because other objects depend on it
DETAIL:  constraint inspection_vendor_fk on table incoming_insp depends on table vendor_copy
HINT:  Use DROP ... CASCADE to drop the dependent objects too.
```

`DETAIL`이 **무엇이 이 테이블에 기대고 있는지**(제약조건 `inspection_vendor_fk`)를 알려 줍니다.
:::

### 5-1. CASCADE — 기대고 있는 객체까지 함께 삭제 {keep}

```sql
DROP TABLE vendor_copy CASCADE;
```

```result
NOTICE:  drop cascades to constraint inspection_vendor_fk on table incoming_insp
```

```sql
SELECT conname, contype
  FROM pg_constraint
 WHERE conrelid = 'lab.incoming_insp'::regclass
   AND contype IN ('p', 'u', 'c', 'f')
 ORDER BY contype, conname;
```

```result
| conname | contype |
| --- | --- |
| inspection_qty_ck | c |
| inspection_result_ck | c |
| inspection_part_fk | f |
| inspection_pk | p |
```

### 5-1. CASCADE는 규칙을 함께 지웁니다 {keep}

```sql
SELECT COUNT(*) AS cnt FROM incoming_insp;
```

```result
| cnt |
| --- |
| 5 |
```

- `CASCADE`가 지운 것은 **자식 테이블이 아니라 FK 제약조건**(`inspection_vendor_fk`)입니다. 검사 기록 5행은 그대로 남았습니다.
- 그 대신 이제 `incoming_insp.vendor_code`에는 **아무 업체 코드나** 들어갈 수 있습니다. ==CASCADE는 오류를 없애 주는 옵션이 아니라, 규칙을 함께 지우는 옵션==입니다. `NOTICE`에 무엇이 함께 지워졌는지 반드시 읽으세요.

### 5-1. IF EXISTS — 없으면 오류 대신 안내만 {keep}

```sql
DROP TABLE vendor_copy;
```

```error
ERROR:  table "vendor_copy" does not exist
```

```sql
DROP TABLE IF EXISTS vendor_copy;
```

```result
NOTICE:  table "vendor_copy" does not exist, skipping
```

`schema_postgres.sql` 맨 위의 `DROP SCHEMA IF EXISTS bom CASCADE;`도 같은 원리입니다. 스크립트를 몇 번 다시 실행해도 처음 실행에서 오류가 나지 않게 합니다.

### 5-2. TRUNCATE — 구조는 두고 데이터만 비우기 {keep}

```sql
TRUNCATE TABLE incoming_insp;
```

```sql
SELECT COUNT(*) AS cnt FROM incoming_insp;
```

```result
| cnt |
| --- |
| 0 |
```

```sql
SELECT column_name FROM information_schema.columns
 WHERE table_schema = 'lab' AND table_name = 'incoming_insp'
 ORDER BY ordinal_position;
```

```result
| column_name |
| --- |
| insp_id |
| lot_no |
| part_no |
| vendor_code |
| insp_date |
| sample_qty |
| defect_qty |
| insp_result |
| judged_by |
```

행은 0개가 됐지만 테이블과 컬럼·제약조건은 그대로입니다.

### 5-2. 참조되는 테이블은 TRUNCATE도 막힘 {keep}

:::error 참조되는 테이블은 TRUNCATE도 막힘
5-1의 `CASCADE` 전, `vendor_copy`가 아직 참조되고 있을 때 실행한 결과입니다.

```sql
TRUNCATE TABLE vendor_copy;
```

```error
ERROR:  cannot truncate a table referenced in a foreign key constraint
DETAIL:  Table "incoming_insp" references "vendor_copy".
HINT:  Truncate table "incoming_insp" at the same time, or use TRUNCATE ... CASCADE.
```

`TRUNCATE ... CASCADE`는 참조하는 **자식 테이블의 데이터까지 모두** 비웁니다. 원본 코드표·마스터에 실행하면 BOM·소싱·재고가 한꺼번에 사라질 수 있으므로 쓰지 않습니다.
:::

### 5-2. PostgreSQL의 TRUNCATE는 되돌릴 수 있습니다 {keep}

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
SELECT COUNT(*) AS cnt_after_rollback FROM bom_wm;
```

```result
| cnt_after_rollback |
| --- |
| 43 |
```

`BEGIN`으로 시작한 묶음 안에서 비운 데이터는 `ROLLBACK`으로 43행이 그대로 돌아왔습니다. 단, PostgreSQL 클라이언트는 기본이 **자동 커밋**이라 `BEGIN` 없이 실행한 TRUNCATE는 그 즉시 확정됩니다. `BEGIN`·`ROLLBACK`은 TCL 단원에서 자세히 다룹니다.

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
- 기존 교안 `9. DDL.pptx` 31번은 「TRUNCATE·DROP: 복구 불가능」입니다. PostgreSQL에서는 `BEGIN … ROLLBACK`으로 되돌아오므로 슬라이드를 수정해야 합니다. 5-3 표의 DELETE·DROP 칸도 검증 환경에서 직접 실행해 확인했습니다(`bom.vendor` 사본 `t`로 `BEGIN; DROP TABLE t; ROLLBACK;` 후 12행 그대로, `BEGIN; DELETE FROM t; ROLLBACK;` 후 12행 그대로).
- 「되돌릴 수 있다」를 강조하다 보면 훈련생이 BEGIN 없이 실험할 수 있습니다. 자동 커밋이 기본이라는 점을 반드시 같이 말해 주세요.
:::

### 5-4. 확인 문제 — 회원·블로그 · HR 데이터 {keep}

> 실행 전: `SET search_path TO lab, hr;`

:::try
**[복습]** 3-7·4-5에서 만든 `member`와 `blog`를 모두 지우려 합니다. `DROP TABLE member;`부터 실행하면 어떻게 되나요? `CASCADE` 없이 두 테이블을 지우는 순서를 쓰고, 이미 지워졌어도 오류가 나지 않도록 작성하세요.

**[응용]** `emp_ship`을 `BEGIN`으로 묶어 `TRUNCATE`한 뒤, 묶음 안에서 행 수를 확인하고 `ROLLBACK`하세요. 묶음 밖에서 다시 확인한 행 수는?
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
묶음 안에서는 0행, ROLLBACK 후에는 45행입니다.

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
SELECT COUNT(*) AS cnt_after FROM emp_ship;
```

```result
| cnt_after |
| --- |
| 45 |
```
:::

## 6. 판단 결과 기록 테이블 설계 — 결품 경고

### 6-1. 기존 이력 테이블 ① uit_change_history {keep}

BOM 데이터셋에는 이미 「변경 기록」 테이블이 두 개 있습니다. psql의 `\d`로 구조를 봅니다.

```screen psql — \d bom.uit_change_history
                   Table "bom.uit_change_history"
      Column       |     Type      | Collation | Nullable | Default 
-------------------+---------------+-----------+----------+---------
 change_id         | integer       |           | not null | 
 part_no           | character(11) |           |          | 
 old_uit           | character(1)  |           |          | 
 new_uit           | character(1)  |           |          | 
 changed_by_dept   | text          |           |          | 
 change_reason     | text          |           |          | 
 changed_at        | date          |           |          | 
 line_type_updated | character(1)  |           |          | 
Indexes:
    "uit_change_history_pkey" PRIMARY KEY, btree (change_id)
Foreign-key constraints:
    "uit_change_history_part_no_fkey" FOREIGN KEY (part_no) REFERENCES bom.part_master(part_no)
```

### 6-1. 기존 이력 테이블 ② part_status_history {keep}

```screen psql — \d bom.part_status_history
               Table "bom.part_status_history"
   Column   |     Type      | Collation | Nullable | Default 
------------+---------------+-----------+----------+---------
 part_no    | character(11) |           |          | 
 old_status | smallint      |           |          | 
 new_status | smallint      |           |          | 
 changed_at | date          |           |          | 
 reason     | text          |           |          | 
Foreign-key constraints:
    "part_status_history_part_no_fkey" FOREIGN KEY (part_no) REFERENCES bom.part_master(part_no)
```

### 6-1. 두 이력 테이블 점검 {keep}

| 점검 항목 | `uit_change_history` | `part_status_history` |
| --- | --- | --- |
| 기록을 구별하는 PK | `change_id` 있음 | **없음** |
| 대상 품번이 실제로 있는지 (FK) | 있음 | 있음 |
| 대상 품번이 비어 있지 않은지 (NOT NULL) | 없음 | 없음 |
| 값의 범위 (CHECK) | 없음 — `line_type_updated`에 `Y`/`N` 외 값도 들어감 | 없음 |
| 기록 시각 | `DATE`(날짜만) | `DATE`(날짜만) |
| 누가 판단·변경했나 | 부서(`changed_by_dept`) | 없음 |

:::try 생각해 보기
`part_status_history`에는 PK가 없습니다. 같은 품번·같은 날짜·같은 상태 변경이 실수로 두 번 들어가면 어떻게 될까요? 「몇 건이 변경되었나」를 세는 쿼리 결과에는 어떤 영향이 있을까요?
:::

### 6-2. 요구사항 → 컬럼 {keep}

Day 3 7교시에 컴프레서(`ECP39799101`)가 **12/4에 결품**된다는 것을 계산했습니다. 이 판단을 「누가·언제·왜·무엇을」과 함께 남기는 테이블을 설계합니다. 이 테이블은 Day 4 4교시(승인 흐름)와 6교시(`check_shortage` 함수의 결과 INSERT)에서 그대로 씁니다.

| 기록할 것 | 컬럼 | 자료형 | 규칙 |
| --- | --- | --- | --- |
| 기록 번호 | `alert_id` | `BIGINT` 자동 번호 | PK |
| 어느 사이트, 어떤 품번 | `site_code`, `part_no` | `CHAR(2)`, `CHAR(11)` | NOT NULL, 품번은 `part_master` FK |
| 언제, 얼마나 부족 | `shortage_date`, `shortage_qty` | `DATE`, `NUMERIC(12,2)` | NOT NULL, 부족 수량 > 0 |
| 왜 (근거) | `basis` | `TEXT` | NOT NULL — 근거 없는 판단은 기록 불가 |
| 누가 판단 | `judged_by` | `VARCHAR(5)` | `'AI'` 또는 `'HUMAN'`만 |
| 처리 상태 | `status` | `VARCHAR(10)` | `'PENDING'`(대기) / `'APPROVED'`(승인) / `'REJECTED'`(반려), 기본값 대기 |
| 언제 기록 | `created_at` | `TIMESTAMP` | NOT NULL, 기본값 현재 시각 |
| 누가·언제 승인/반려 | `reviewed_by`, `reviewed_at` | `VARCHAR(30)`, `TIMESTAMP` | 대기가 아니면 둘 다 있어야 함 |

### 6-3. CREATE TABLE {keep}

```sql
SET search_path TO lab, bom;

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

### 6-3. 새로 나온 두 가지 — IDENTITY · now() {keep}

- **`GENERATED ALWAYS AS IDENTITY`** — 행을 넣을 때마다 1, 2, 3 … 번호를 **DB가 자동으로** 매깁니다. 사람이나 프로그램이 번호를 직접 정하다가 겹치는 일이 없습니다.
- **`now()`** — 현재 날짜·시각을 돌려주는 함수입니다. `DEFAULT now()`이므로 기록 시각을 따로 적지 않아도 INSERT한 시각이 남습니다.

### 6-4. 동작 확인 — AI 판단 기록하기 {keep}

Day 3에서 계산한 결과를 AI 판단으로 기록합니다. 근거에는 계산 과정을 적습니다. (11/30 재고 1,150 − 12/1~12/4 냉장고 계획 380 + 320 + 380 + 320 = 1,400 → 12/4에 250 부족)

```sql
INSERT INTO shortage_alert (site_code, part_no, shortage_date, shortage_qty, basis, judged_by)
VALUES ('CW', 'ECP39799101', '2026-12-04', 250,
        '11/30 재고 1150 - 12/1~12/4 냉장고 계획 누적 1400 = -250', 'AI');
```

```sql
SELECT alert_id, part_no, shortage_date, shortage_qty, judged_by, status,
       created_at IS NOT NULL AS has_created_at, reviewed_by
  FROM shortage_alert;
```

```result
| alert_id | part_no | shortage_date | shortage_qty | judged_by | status | has_created_at | reviewed_by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ECP39799101 | 2026-12-04 | 250.00 | AI | PENDING | t | NULL |
```

번호(1), 상태(`PENDING`), 기록 시각이 **적지 않아도** 채워졌습니다. (`created_at`은 실행할 때마다 값이 달라 `IS NOT NULL`로만 확인했습니다.)

### 6-4. 이 테이블이 막아 주는 것 ① · ② {keep}

:::error ① 번호를 직접 정하면
```sql
INSERT INTO shortage_alert (alert_id, site_code, part_no, shortage_date, shortage_qty, basis, judged_by)
VALUES (100, 'CW', 'ECP39799101', '2026-12-04', 250, '수동 입력', 'HUMAN');
```

```error
ERROR:  cannot insert a non-DEFAULT value into column "alert_id"
DETAIL:  Column "alert_id" is an identity column defined as GENERATED ALWAYS.
HINT:  Use OVERRIDING SYSTEM VALUE to override.
```
:::

:::error ② 판단 주체가 정해진 값이 아니면
(`DETAIL`의 시각은 실행 시각이라 매번 다릅니다)

```sql
INSERT INTO shortage_alert (site_code, part_no, shortage_date, shortage_qty, basis, judged_by)
VALUES ('CW', 'EIC93178801', '2026-12-10', 100, '테스트', 'GPT');
```

```error
ERROR:  new row for relation "shortage_alert" violates check constraint "shortage_alert_judged_ck"
DETAIL:  Failing row contains (2, CW, EIC93178801, 2026-12-10, 100.00, 테스트, GPT, PENDING, 2026-11-05 03:24:46.037191, null, null).
```
:::

### 6-4. 이 테이블이 막아 주는 것 ③ · ④ {keep}

:::error ③ 승인자 없이 「승인」으로 기록하면
```sql
INSERT INTO shortage_alert (site_code, part_no, shortage_date, shortage_qty, basis, judged_by, status)
VALUES ('CW', 'EIC93178801', '2026-12-10', 100, '테스트', 'AI', 'APPROVED');
```

```error
ERROR:  new row for relation "shortage_alert" violates check constraint "shortage_alert_review_ck"
DETAIL:  Failing row contains (3, CW, EIC93178801, 2026-12-10, 100.00, 테스트, AI, APPROVED, 2026-11-05 03:24:46.069955, null, null).
```
:::

:::error ④ 부족 수량이 0이면
```sql
INSERT INTO shortage_alert (site_code, part_no, shortage_date, shortage_qty, basis, judged_by)
VALUES ('CW', 'EIC93178801', '2026-12-10', 0, '테스트', 'AI');
```

```error
ERROR:  new row for relation "shortage_alert" violates check constraint "shortage_alert_qty_ck"
DETAIL:  Failing row contains (4, CW, EIC93178801, 2026-12-10, 0.00, 테스트, AI, PENDING, 2026-11-05 03:24:46.103374, null, null).
```
:::

특히 ③은 「AI가 혼자 승인까지 끝낸 기록」을 DB 차원에서 막습니다. ==사람 승인 없이는 승인 상태가 될 수 없다는 업무 규칙을 CHECK 하나로 강제==한 것입니다.

### 6-4. 실패한 INSERT도 번호를 하나씩 씁니다 {keep}

```sql
INSERT INTO shortage_alert (site_code, part_no, shortage_date, shortage_qty, basis, judged_by)
VALUES ('CW', 'MGL96663301', '2026-12-09', 10, '연습 입력', 'HUMAN');
```

```sql
SELECT alert_id, part_no, judged_by, status FROM shortage_alert ORDER BY alert_id;
```

```result
| alert_id | part_no | judged_by | status |
| --- | --- | --- | --- |
| 1 | ECP39799101 | AI | PENDING |
| 5 | MGL96663301 | HUMAN | PENDING |
```

②~④의 `DETAIL`에 보였던 2, 3, 4번이 실패와 함께 버려져 다음 번호는 5입니다. 자동 번호는 ==겹치지 않는 것만 보장하고, 빈칸 없이 이어지는 것은 보장하지 않습니다.== 「기록이 몇 건인가」는 번호가 아니라 `COUNT(*)`로 셉니다.

### 6-4. 기존 이력 테이블과 비교 {keep}

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

```result
| table_name | contype | cnt |
| --- | --- | --- |
| uit_change_history | f | 1 |
| uit_change_history | p | 1 |
| part_status_history | f | 1 |
| shortage_alert | c | 4 |
| shortage_alert | f | 1 |
| shortage_alert | p | 1 |
```

> 승인(`PENDING` → `APPROVED`)은 행을 새로 넣는 것이 아니라 **기존 행의 상태를 바꾸는** 작업(UPDATE)입니다. 반려된 판단도 지우지 않고 `REJECTED`로 남겨 「AI가 무엇을 틀렸는지」를 기록으로 쌓습니다. 이 흐름은 Day 4 4교시에서 이어집니다.

:::teacher 강사 확인
- 6-4의 12/4·250개는 README 4장 **A7**(컴프레서 on-hand 1,150, 12/4 결품)과 `production_plan`의 냉장고 12/1~12/4 계획(380·320·380·320)으로 계산한 값입니다. Day 3 Q11 결과표의 12/4 행과 같은지 수업 전 대조하세요.
- `shortage_alert_review_ck`의 `OR` 조건식이 어렵다면 「대기(PENDING)이거나, 아니면 승인자와 승인 시각이 둘 다 있어야 한다」로 읽어 주세요. 3단원 `AND`·`OR` 우선순위 때문에 괄호가 필요하다는 점도 짚어 주세요.
:::

### 6-5. 확인 문제 — 품질 판단 테이블 (도전) {keep}

> 실행 전: `SET search_path TO lab, bom;`

:::try
**[응용 · 도전]** (운영안 Day 4 도전 과제) 품질 점검 판단을 **AI 판단**과 **사람 최종 판단**으로 나눠 기록하는 `quality_judgment` 테이블을 만드세요.

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
DETAIL:  Failing row contains (4, ECP39799101, SHORTAGE, NG, REVIEW, 2026-11-05 03:25:52.842394).
```
:::

## 7. 복습 문제

### 7-0. 복습 문제 안내 {keep}

> 범위: DDL 전체(CREATE · 자료형 · 제약조건 · ALTER · DROP · TRUNCATE · CTAS). 1번은 기존 복습문제(`09.DDL복습문제.txt`), 2~5번은 BOM 데이터입니다. 실행 전 `SET search_path TO lab, bom;`

```icons 다섯 문항
users | 1 · CREATE · PK | 회원정보 테이블 TB_CUST | rose
refrigerator | 2 · CTAS · 제약조건 | 냉장고 BOM 사본 bom_rf | plum
pencil | 3 · ALTER TABLE | bom_rf 고치기 | lime
clipboard-list | 4 · (심화) 설계 | 품질 이상 기록 quality_issue | ivory
trash-2 | 5 · DROP SCHEMA | lab 스키마 정리 | hot
```

### 7-1. 복습 1 {keep}

**1.** (기존 복습문제 1~3) 회원정보 테이블 `TB_CUST`를 만드세요.

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

3-6에서 세탁기 사본(`bom_wm`)은 같은 CHECK가 실패했습니다. 냉장고 사본은 어떻게 되나요? 이유는?

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

**4.** (심화) Day 2 품질 진단 리포트의 이상 항목을 기록할 `quality_issue` 테이블을 설계하세요.

| 컬럼 | 조건 |
| --- | --- |
| `issue_id` | 자동 번호, PK |
| `part_no` | NOT NULL, `bom.part_master` FK |
| `issue_type` | NOT NULL, `'MISSING_VALUE'`(값 누락) / `'ATTR_MISMATCH'`(속성 불일치) / `'RULE_VIOLATION'`(규칙 위반)만 |
| `detail` | NOT NULL (근거) |
| `owner_dept` | NOT NULL, `'R&D'` / `'자재'` / `'구매'`만 |
| `status` | NOT NULL, `'OPEN'` / `'CLOSED'`만, 기본값 `'OPEN'` |
| `found_at` | NOT NULL, 기본값 오늘 날짜 (`CURRENT_DATE`) |

3-6에서 찾은 두 건을 기록하고, `issue_type`에 목록에 없는 `'ZERO_QTY'`를 넣으면 어떻게 되는지 확인하세요.
(1) `MFT43979901` / `MISSING_VALUE` / `'part_sourcing.po_price가 NULL'` / 구매
(2) `FSC67181101` / `RULE_VIOLATION` / `'bom_id 70 qty_per = 0'` / R&D

```result 출력 결과 (총 2행, today는 found_at = CURRENT_DATE 결과)
| issue_id | part_no | issue_type | owner_dept | status | today |
| --- | --- | --- | --- | --- | --- |
| 1 | MFT43979901 | MISSING_VALUE | 구매 | OPEN | t |
| 2 | FSC67181101 | RULE_VIOLATION | R&D | OPEN | t |
```

### 7-5. 복습 5 {keep}

**5.** 실습을 마치고 `lab` 스키마에 만든 테이블을 확인한 뒤, `lab` 스키마를 통째로 지우세요. 원본 `bom` 스키마의 테이블 수가 그대로인지 확인합니다. [힌트: `information_schema.tables`, `DROP SCHEMA ... CASCADE`]

```result 출력 결과 — lab 스키마 테이블 (이 교안을 처음부터 순서대로 실행했다면 총 12행)
bom_rf, bom_wm, emp_copy, emp_ship, incoming_insp, part_memo, plan_empty,
quality_issue, quality_judgment, shortage_alert, sourcing_copy, tb_cust
```

```result 출력 결과 — 삭제 후 bom 스키마 테이블 수
| bom_tables |
| --- |
| 17 |
```

### 7-6. 복습 1 · 2 답 {keep}

:::answer 복습 1 · 2 예시 답안
```sql 1
CREATE TABLE tb_cust (
      cust_id    VARCHAR(20)   NOT NULL
    , passwd     VARCHAR(300)  NOT NULL
    , cust_name  VARCHAR(50)   DEFAULT '????'
);

ALTER TABLE tb_cust ADD CONSTRAINT pk_test PRIMARY KEY (cust_id);

INSERT INTO tb_cust (cust_id, passwd) VALUES ('C0001', 'pass111');
INSERT INTO tb_cust (cust_id, passwd, cust_name) VALUES ('C0001', 'pass222', 'pk설정했나');   -- 오류가 나야 정상
INSERT INTO tb_cust (cust_id, passwd, cust_name) VALUES ('C0002', 'pass222', '고객2');

SELECT * FROM tb_cust ORDER BY cust_id;
```

```error
ERROR:  duplicate key value violates unique constraint "pk_test"
DETAIL:  Key (cust_id)=(C0001) already exists.
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

- 1번: 기존 답안의 `VARCHAR2`는 PostgreSQL에서 `VARCHAR`입니다. 중복 오류 메시지에는 ==직접 붙인 제약조건 이름 `pk_test`가 그대로 나옵니다.== 이름을 붙이는 이유입니다(3-2). (대문자로 적은 `PK_TEST`도 소문자 `pk_test`로 바뀝니다 — 2-5.)
- 2번: 소요량 0인 행(bom_id 70)은 **세탁기** BOM(DD모터 → 나사 M4)에만 있어서, 냉장고 사본에는 CHECK가 바로 걸립니다. 「규칙을 걸 수 있는가」로 데이터 범위별 품질을 비교할 수 있습니다.
:::

### 7-7. 복습 3 답 {keep}

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

### 7-8. 복습 4 답 {keep}

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

INSERT INTO quality_issue (part_no, issue_type, detail, owner_dept)
VALUES ('FSC67181101', 'ZERO_QTY', 'bom_id 70 qty_per = 0', 'R&D');   -- 오류

SELECT issue_id, part_no, issue_type, owner_dept, status, found_at = CURRENT_DATE AS today
  FROM quality_issue
 ORDER BY issue_id;
```

```error
ERROR:  new row for relation "quality_issue" violates check constraint "quality_issue_type_ck"
DETAIL:  Failing row contains (3, FSC67181101, ZERO_QTY, bom_id 70 qty_per = 0, R&D, OPEN, 2026-11-05).
```

- 4번: `issue_type`처럼 값의 종류가 정해진 컬럼에 CHECK를 걸면, 사람마다 `'ZERO_QTY'`, `'zero qty'`, `'소요량0'`처럼 제각각 적어 **집계가 안 되는** 문제를 막을 수 있습니다(4단원 GROUP BY).
:::

### 7-9. 복습 5 답 {keep}

:::answer 복습 5 예시 답안
```sql 5
SELECT table_name
  FROM information_schema.tables
 WHERE table_schema = 'lab'
 ORDER BY table_name;

DROP SCHEMA lab CASCADE;

SELECT COUNT(*) AS bom_tables FROM information_schema.tables WHERE table_schema = 'bom';
```

```result
NOTICE:  drop cascades to 12 other objects
DETAIL:  drop cascades to table part_memo
drop cascades to table bom_wm
drop cascades to table plan_empty
drop cascades to table incoming_insp
drop cascades to table sourcing_copy
drop cascades to table shortage_alert
drop cascades to table emp_ship
drop cascades to table emp_copy
drop cascades to table quality_judgment
drop cascades to table tb_cust
drop cascades to table bom_rf
drop cascades to table quality_issue
```

- 5번: `DROP SCHEMA … CASCADE`는 스키마 안의 **모든** 테이블을 지웁니다. 반드시 `lab`인지 확인하고 실행하세요. `bom`에 실행하면 원본이 모두 사라지고 `schema_postgres.sql`을 다시 적재해야 합니다.
:::

:::teacher 강사 확인
- 5번은 HR 확인 문제의 테이블(`emp_ship`, `emp_copy`)까지 `lab`에 만들어졌다는 전제입니다. 확인 문제 일부를 건너뛰었다면 행 수가 12보다 적습니다.
- 4번의 두 건은 README 4장 **A4**·**A5**입니다. 실제 Day 4 7교시 종합 미니 과제에서 이 테이블 구조를 그대로 써도 됩니다.
:::

## 8. 정리

### 8-1. 오늘 배운 것 {keep}

:::summary
- **DDL**: 데이터를 담을 그릇(테이블)을 만들고(`CREATE`), 고치고(`ALTER`), 지우는(`DROP`, `TRUNCATE`) SQL입니다. 원본을 보호하려고 실습은 `lab` 스키마에서 합니다.
- **자료형**: 고정 길이 코드 `CHAR(n)`, 가변 길이 글 `VARCHAR(n)`/`TEXT`, 수량·단가 `NUMERIC(p,s)`, 날짜 `DATE`, 날짜+시각 `TIMESTAMP`. `VARCHAR(n)`은 **글자 수** 기준입니다.
- **NOT NULL / DEFAULT**: DEFAULT는 「값을 안 줬을 때」만 동작합니다. NULL을 직접 적으면 NULL이 들어갑니다.
- **이름 규칙**: 따옴표 없는 이름은 소문자로 바뀝니다. 영문 소문자와 `_`만 쓰고, 예약어는 피합니다.
- **CTAS**: `CREATE TABLE … AS SELECT`는 데이터와 컬럼만 복사하고 **제약조건은 복사하지 않습니다.**
- **제약조건**: PK(NULL·중복 불가), UNIQUE(중복 불가, NULL 허용), NOT NULL, CHECK(조건식이 거짓이면 거부, NULL이면 통과), FK(부모에 있는 값만, 부모 삭제도 막음). FK가 가리키는 부모 컬럼은 PK 또는 UNIQUE여야 합니다.
- **제약조건 = 품질 규칙**: 나중에 거는 제약조건은 기존 행을 모두 검사하므로, 실패하면 그 자체가 이상 데이터 발견입니다. `NOT VALID`로 새 행부터 막을 수 있습니다.
- **ALTER TABLE**: `ADD COLUMN`, `DROP COLUMN`, `ALTER COLUMN … TYPE / SET DEFAULT / SET NOT NULL`, `RENAME COLUMN`, `RENAME TO`, `ADD/DROP CONSTRAINT`.
- **DROP · TRUNCATE**: 참조되는 테이블은 지울 수도 비울 수도 없습니다. `CASCADE`는 규칙(FK)까지 함께 지웁니다. PostgreSQL의 TRUNCATE는 `BEGIN … ROLLBACK`으로 되돌릴 수 있습니다.
- **판단 기록 테이블**: 대상·판단값·근거·판단 주체·시각·상태를 컬럼으로 두고, 자동 번호(`IDENTITY`), 기본값(`now()`, `'PENDING'`), CHECK(판단 주체·상태·승인 조건)로 업무 규칙을 DB에 새깁니다.
:::

### 8-2. 확인 문제

:::quiz
Q. `writer VARCHAR(20) DEFAULT '미지정'` 컬럼에 `INSERT … (writer) VALUES (NULL)`을 실행하면 무엇이 저장되나요?
A. NULL입니다. DEFAULT는 컬럼 값을 아예 주지 않았을 때만 동작합니다.

Q. `CREATE TABLE sourcing_copy AS SELECT * FROM bom.part_sourcing;`로 만든 사본에 같은 행을 한 번 더 넣으면 어떻게 되나요?
A. 오류 없이 들어갑니다. CTAS는 PK 같은 제약조건을 복사하지 않기 때문입니다. 필요하면 `ALTER TABLE … ADD CONSTRAINT … PRIMARY KEY`로 다시 겁니다.

Q. `UNIQUE`가 걸린 `lot_no`에 NULL을 두 번 넣으면? PK라면?
A. UNIQUE는 NULL을 서로 같다고 보지 않아 두 번 다 들어갑니다. PK는 NOT NULL이 포함되어 있어 NULL 자체가 거부됩니다.

Q. 사본 `bom_wm`에 `CHECK (qty_per > 0)`을 추가하려는데 「violated by some row」 오류가 납니다. 다음에 할 일은?
A. `WHERE NOT (qty_per > 0)`으로 규칙을 어기는 행을 찾아 원인을 확인합니다(bom_id 70, 소요량 0). 기존 행 정리 전에 새 행부터 막으려면 `NOT VALID`를 붙여 추가합니다.

Q. `DROP TABLE vendor_copy CASCADE;` 실행 후 `incoming_insp` 테이블은 어떻게 되나요?
A. 테이블과 데이터는 남고, `vendor_copy`를 가리키던 FK 제약조건만 삭제됩니다. 그 결과 업체 코드에 아무 값이나 들어갈 수 있게 됩니다.

Q. `shortage_alert`에 `status = 'APPROVED'`인데 `reviewed_by`가 없는 행을 넣으면 어떻게 되나요? 왜 이런 제약조건을 두나요?
A. `shortage_alert_review_ck` 위반으로 거부됩니다. 사람(승인자)·승인 시각 없이 승인 상태가 되는 것, 즉 AI 판단이 사람 승인 없이 확정되는 것을 DB 차원에서 막기 위해서입니다.
:::
