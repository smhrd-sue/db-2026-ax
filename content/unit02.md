---
label: 2. PostgreSQL 설치
title: PostgreSQL 설치와 실습 데이터 적재
---

# PostgreSQL 설치하기

:::goal
- PostgreSQL을 설치하고 SQL Shell (psql)로 접속할 수 있습니다.
- `schema_postgres.sql`로 실습 DB를 만들고 행 수로 적재를 확인할 수 있습니다.
- pgAdmin 4에서 첫 쿼리를 실행할 수 있습니다.
- 복습으로 `hr` 샘플 데이터를 혼자 적재하고 확인할 수 있습니다.
- 코드표로 품번·UIT·Status·UOM·Supply Type 값의 뜻을 읽을 수 있습니다.
:::



## 1. 이번 시간에 할 일

### 1-1. ERD를 실제 DB로 만드는 시간 {keep}

1장에서 그린 ERD·관계 모델을 **실제 DB로 만드는 시간**입니다. 1장 6. 물리적 모델링의 결과물인 `schema_postgres.sql`을 직접 실행합니다.

```flow 이번 시간의 흐름
download | 설치 | PostgreSQL 18 | ivory
log-in | 접속 | SQL Shell (psql) | ivory
database | 실습 DB 만들기 | bom_lab | lime
file-spreadsheet | 데이터 적재 | 테이블 17개 | lime
list-checks | 적재 확인 | 행 수 맞춰 보기 | plum
search | 첫 쿼리 | pgAdmin 4 | hot
```

### 1-1. 순서와 결과

| 순서 | 할 일 | 쓰는 도구 | 결과 |
| --- | --- | --- | --- |
| 1 | PostgreSQL 설치 | 설치 프로그램 | 내 PC에 DB 서버가 생김 |
| 2 | 접속 | SQL Shell (psql) | `postgres` 계정으로 로그인 |
| 3 | 실습 DB 만들기 | SQL Shell (psql) | `bom_lab` 데이터베이스 |
| 4 | 데이터 적재 | SQL Shell (psql) | `bom` 스키마 + 테이블 17개 + 데이터 |
| 5 | 적재 확인 | SQL Shell (psql) | 테이블별 행 수가 맞는지 확인 |
| 6 | 첫 쿼리 | pgAdmin 4 | `part_master` 조회 |
| 7 | 복습 | SQL Shell (psql) | `hr` 스키마 + 테이블 7개 직접 적재 |
| 8 | 데이터 탐색 | pgAdmin 4 | 품번·UIT·Status·UOM·Supply Type 코드 읽기 |

## 2. 설치 전에 알아 둘 것 — 서버와 클라이언트

### 2-1. 서버 하나, 도구 둘 {keep}

DB는 **데이터를 보관하는 프로그램(서버)** 과 **서버에 접속해 SQL을 보내는 프로그램(클라이언트)** 으로 나뉩니다. 이번에 설치하는 것은 세 가지입니다.

```icons 이번에 설치하는 세 가지
si:postgresql | PostgreSQL Server | 데이터를 저장하고 SQL을 실제로 실행하는 본체. Windows 서비스로 계속 켜져 있음 | #4169E1 | [비유] 창고
square-terminal | SQL Shell (psql) | 글자로 명령을 입력하는 클라이언트. `\copy` 같은 **psql 전용 명령**을 쓸 수 있음 | lime | [비유] 창고 관리 단말기
monitor | pgAdmin 4 | 마우스로 테이블을 보고 쿼리를 실행하는 그래픽 클라이언트 | plum | [비유] 창고 관리 화면
```

> 두 도구가 같은 서버에 접속합니다. 데이터 **적재는 psql**, 이후 **조회 실습은 pgAdmin**으로 나눠 씁니다. 적재 스크립트가 psql에서만 동작하는 `\copy` 명령을 쓰기 때문입니다(6-3, 8-4에서 다룹니다).

## 3. PostgreSQL 설치 (Windows)

### 3-1. 설치 파일 받기 {keep}

1. [postgresql.org/download/windows](https://www.postgresql.org/download/windows/) 접속
2. **Download the installer** (EDB에서 제공하는 설치 프로그램) 클릭
3. 버전 **18**, 운영체제 **Windows x86-64** 파일을 내려받기

```shot ① postgresql.org — Windows installers 페이지. 맨 위 「Download the installer」를 누릅니다.
unit02/01-download-windows.png
```

### 3-1. EDB 다운로드 표에서 고르기 {keep}

```shot ② EDB 다운로드 표 — 18.x 행의 「Windows x86-64」 열 아이콘을 누릅니다. 맨 위 행이 다른 버전이어도 18.x 행을 고릅니다. (캡처 시점 18.6)
unit02/02-edb-installer.png
```

> 공식 다운로드 페이지는 Windows용 설치 프로그램으로 PostgreSQL 여러 버전을 제공하며, 설치 프로그램에 **PostgreSQL 서버·pgAdmin·StackBuilder**가 함께 들어 있다고 안내합니다.
> 내려받을 때 회원가입이나 로그인은 필요하지 않습니다.

### 3-2. 설치 마법사 따라가기

내려받은 `postgresql-18.x-x-windows-x64.exe`를 **마우스 오른쪽 클릭 → 관리자 권한으로 실행**합니다.

| 단계 | 화면 | 이렇게 합니다 |
| --- | --- | --- |
| 1 | Setup (시작) | Next |
| 2 | Installation Directory | 기본값 그대로 Next |
| 3 | Select Components | **4개 모두 체크 유지** — PostgreSQL Server, pgAdmin 4, Stack Builder, Command Line Tools |
| 4 | Data Directory | 기본값 그대로 Next |
| 5 | Password | `postgres` 계정 비밀번호 입력 → ==수업용은 모두 `12345`로 통일== |
| 6 | Port | **5432** 그대로 |
| 7 | Advanced Options (Locale) | 기본값(Default locale) 그대로 |
| 8 | Pre Installation Summary | 내용 확인 후 Next |
| 9 | Installing | 끝날 때까지 기다리기 |
| 10 | Completing | **Stack Builder 체크 해제** 후 Finish (이번 수업에는 추가 설치가 필요 없음) |

### 3-2. 꼭 확인할 화면 ① 구성 요소 · 비밀번호 {keep}

:::cols
```shot 3단계 Select Components — 4개 모두 체크된 상태 그대로
unit02/03-select-components.png
```

```shot 5단계 Password — 같은 비밀번호를 두 번 입력 (수업용 `12345`)
unit02/04-password.png
```
:::

### 3-2. 꼭 확인할 화면 ② 포트 · 마침 {keep}

:::cols
```shot 6단계 Port — 5432 그대로
unit02/05-port.png
```

```shot 10단계 Completing — Stack Builder 체크 해제 후 Finish
unit02/06-completing.png
```
:::

> **비밀번호는 꼭 기억하세요.** psql·pgAdmin으로 접속할 때마다 입력합니다. 잊어버리면 다시 설정하는 과정이 번거롭습니다.

### 3-3. 설치 확인 {keep}

Windows 시작 메뉴에서 **PostgreSQL 18** 폴더를 열면 아래 두 개가 보여야 합니다.

- **SQL Shell (psql)**
- **pgAdmin 4**

```shot 설치 후 생긴 PostgreSQL 18 폴더 — SQL Shell (psql) · pgAdmin 4가 보이면 성공 (맥 화면 · Windows는 시작 메뉴의 같은 이름 폴더)
unit02/07-start-menu.png
```

:::teacher 강사 확인
- Mac 사용 훈련생이 있으면 [postgresql.org/download/macosx](https://www.postgresql.org/download/macosx/)에서 설치 방법을 고르게 합니다. 이 교안의 화면·경로는 Windows 기준입니다.
- 설치가 오래 걸리는 PC가 있으므로 설치 파일을 미리 내려받아 공유 폴더·USB로 나눠 주면 시간을 줄일 수 있습니다.
:::

## 4. 실습 폴더 준비

### 4-1. 스크립트와 CSV를 한 폴더에 {keep}

`\copy` 명령은 **psql이 지금 있는 폴더**를 기준으로 CSV 파일을 찾습니다. 그래서 적재 스크립트와 CSV 17개를 **한 폴더**에 모아 둡니다.

1. `C:\bom_lab` 폴더를 만듭니다.
2. [{{ic:download}} 실습 자료 내려받기 (Google Drive)](https://drive.google.com/drive/folders/17UrEDgKNiYYt4ewRip8qfxExgHazR8t9?usp=sharing)에서 SQL 1개와 CSV 17개를 받아 모두 이 폴더에 넣습니다.

```text 실습 폴더
C:\bom_lab
├─ schema_postgres.sql          ← 적재 스크립트 (물리적 모델링 결과물)
├─ part_master.csv  vendor.csv  bom_structure.csv  part_sourcing.csv
├─ site_part_attr.csv  uit_change_history.csv  part_status_history.csv
├─ production_plan.csv  inventory.csv  scheduled_receipt.csv
└─ code_uit.csv  code_uom.csv  code_status.csv  code_supply_type.csv
   code_line_type.csv  code_svc.csv  code_cosp.csv          (CSV 총 17개)
```

> ==폴더 경로에 한글과 띄어쓰기를 넣지 마세요.== `바탕 화면\DB 수업`처럼 한글·공백이 있으면 경로를 따옴표로 정확히 감싸야 해서 실수가 잦습니다. `C:\bom_lab`처럼 짧은 영문 경로를 권장합니다.

# 실습 데이터 적재하기

## 5. SQL Shell (psql)로 접속하기

### 5-1. 기본값은 Enter, 비밀번호만 입력 {keep}

시작 메뉴 → **SQL Shell (psql)** 실행. 검은 창에 아래 질문이 차례로 나옵니다. 대괄호 `[ ]` 안이 기본값이며, **Enter만 누르면 기본값**이 들어갑니다.

```text psql 접속 화면
Server [localhost]:          ← Enter
Database [postgres]:         ← Enter
Port [5432]:                 ← Enter
Username [postgres]:         ← Enter
Password for user postgres:  ← 설치할 때 정한 비밀번호 입력 (화면에 안 보이는 게 정상) 후 Enter
```

(한국어 Windows에서는 비밀번호 질문이 한국어로 나올 수 있습니다.)

접속에 성공하면 맨 아래에 `postgres=#` 가 보입니다. `postgres`는 **지금 접속한 데이터베이스 이름**입니다.

### 5-1. 접속 성공 화면 {keep}

```screen SQL Shell (psql) 접속 성공 예시 — 맨 아래 postgres=# 가 보이면 성공
Server [localhost]:
Database [postgres]:
Port [5432]:
Username [postgres]:
Password for user postgres:

psql (18.x)
WARNING: Console code page (949) differs from Windows code page (…)
         8-bit characters might not work correctly. See psql reference
         page "Notes for Windows users" for details.
Type "help" for help.

postgres=#
```

> 비밀번호를 입력해도 글자가 나타나지 않는 것은 보안 때문입니다. 그대로 입력하고 Enter를 누르세요.
>
> `psql (18.x)` 아래에 `Console code page (949) differs from Windows code page …` 같은 경고가 보일 수도 있습니다. 한국어 Windows의 psql은 파일과 입력을 **UHC(CP949)** 로 읽는다는 뜻입니다. 적재 스크립트는 UTF-8로 저장되어 있으므로, 6-2에서 스크립트를 실행하기 전에 ==`\encoding UTF8`== 을 먼저 입력합니다.

:::teacher 강사 확인
- `\encoding UTF8` 없이 `\i schema_postgres.sql`을 실행하면 한글 주석이 든 `CREATE TABLE`(part_master, bom_structure)에서 `0xec 0x9e 바이트로 조합된 문자(인코딩: "UHC")와 대응되는 문자 코드가 "UTF8" 인코딩에는 없습니다` 오류가 나고, 그 뒤 테이블이 연쇄로 만들어지지 않습니다. 코드표 7개와 vendor만 적재되므로 학생이 "일부만 됐다"고 하면 이 경우입니다.
- 적재 후 `\encoding UHC`를 빠뜨리면 `\dn`·`\dt`의 한글 머리글이 `\xB8\xA7`, `테\u000C\xBA`처럼 깨집니다. 데이터는 정상이니 `\encoding UHC`만 입력하게 하세요.
:::

### 5-2. psql 명령은 두 종류입니다 {keep}

```icons
braces | SQL 문 | 일반 영어 문장. 끝에 **세미콜론 `;` 필수** | plum | `CREATE DATABASE bom_lab;`
square-terminal | psql 메타 명령 | 역슬래시 `\` 로 시작. `;` 없이 Enter로 끝 | lime | `\c bom_lab` · `\dt` · `\q`
```

> `;` 없이 Enter를 누르면 프롬프트가 `postgres-#` 로 바뀌며 **명령이 끝나지 않았다**고 기다립니다. 이때 `;`만 입력하고 Enter를 누르면 실행됩니다.

### 5-2. 자주 쓰는 메타 명령

| 명령 | 뜻 |
| --- | --- |
| `\l` | 데이터베이스 목록 |
| `\c DB이름` | 다른 데이터베이스로 접속 |
| `\conninfo` | 지금 어디에 누구로 접속했는지 |
| `\dn` | 스키마 목록 |
| `\dt` | 테이블 목록 |
| `\cd '폴더'` | psql의 현재 폴더 바꾸기 |
| `\i 파일` | SQL 파일을 읽어 그대로 실행 |
| `\q` | psql 종료 |

## 6. 실습 DB 만들고 데이터 적재하기

### 6-1. 실습용 데이터베이스 만들기 {keep}

기본 DB인 `postgres`는 그대로 두고, 실습 전용 DB `bom_lab`을 새로 만듭니다.

```sql
CREATE DATABASE bom_lab;
```

```result
CREATE DATABASE
```

방금 만든 DB로 옮겨 접속합니다.

```psql
\c bom_lab
```

```result
You are now connected to database "bom_lab" as user "postgres".
```

(한국어 Windows에서는 같은 뜻의 한국어 문장으로 보일 수 있습니다.) 프롬프트가 `bom_lab=#` 으로 바뀌면 성공입니다.

### 6-2. 폴더로 이동한 뒤 스크립트 실행 {keep}

```psql
\cd 'C:/bom_lab'
\encoding UTF8
\i schema_postgres.sql
\encoding UHC
```

- Windows 경로지만 **역슬래시 `\` 대신 슬래시 `/`** 를 쓰고, 작은따옴표로 감쌉니다.
- `\encoding UTF8`은 psql이 파일을 **UTF-8로 읽게** 합니다. 빠뜨리면 한글 주석에서 `"UHC" … "UTF8" 인코딩에는 없습니다` 오류가 납니다(11-1).
- `\i`는 파일 안의 문장을 **위에서부터 한 줄씩 그대로 입력한 것처럼** 실행합니다.
- 적재가 끝나면 `\encoding UHC`로 **화면용 인코딩을 되돌립니다**. psql 창은 949(UHC)로 글자를 그리므로, UTF8인 채로 두면 `\dt` 결과의 `이름`·`소유주` 같은 한글 머리글이 `\xB8\xA7`처럼 깨집니다. ==파일을 읽을 때는 UTF8, 화면에 볼 때는 UHC==로 기억하세요.

### 6-2. 화면에 나오는 내용 읽기 {keep}

```result 화면에 나오는 내용 (일부)
psql:schema_postgres.sql:6: NOTICE:  schema "bom" does not exist, skipping
DROP SCHEMA
CREATE SCHEMA
SET
CREATE TABLE
CREATE TABLE
…
COPY 11
COPY 7
COPY 6
…
COPY 68
…
```

- 처음 실행할 때 나오는 `NOTICE … does not exist, skipping`은 오류가 아닙니다. “지울 `bom` 스키마가 아직 없어서 건너뛴다”는 뜻입니다.
- `COPY 숫자`는 **그 테이블에 들어간 행 수**입니다. 7-2에서 기대값과 맞춰 봅니다.

### 6-3. 스크립트는 무슨 일을 했나요? {keep}

`schema_postgres.sql`은 1장에서 배운 **물리적 모델링 결과물**입니다. 위에서부터 이 순서로 실행됩니다.

```flow
trash-2 | DROP SCHEMA | 예전 bom 지우기 | ivory
folder-tree | CREATE SCHEMA | bom 폴더 만들기 | ivory
map | SET search_path | bom. 생략 | ivory
table | CREATE TABLE × 17 | PK·FK 생성 | hot
file-spreadsheet | \copy × 17 | CSV → 테이블 | lime
```

### 6-3. 문장별로 보기

| 순서 | 문장 | 하는 일 |
| --- | --- | --- |
| 1 | `DROP SCHEMA IF EXISTS bom CASCADE;` | 예전 `bom` 스키마가 있으면 통째로 지움 → **다시 실행해도 처음 상태로** 돌아감 |
| 2 | `CREATE SCHEMA bom;` | 테이블을 담을 `bom` 스키마(폴더)를 만듦 |
| 3 | `SET search_path TO bom;` | 이후 테이블 이름 앞에 `bom.`을 안 붙여도 되게 함 |
| 4 | `CREATE TABLE …` × 17 | 코드표 7개 → 마스터 → BOM → 소싱·이력 → 계획·재고 순서로 테이블 생성. ==PK·FK(`REFERENCES`)가 여기서 실제로 만들어짐== |
| 5 | `\copy … FROM '….csv' CSV HEADER ENCODING 'UTF8'` × 17 | CSV 파일을 읽어 테이블에 데이터를 넣음 |

### 6-3. 왜 코드표부터 넣을까요? {keep}

`part_master.uit`는 `code_uit`를 참조하는 FK입니다. 부모(코드표)가 먼저 있어야 자식(part_master)에 값을 넣을 수 있습니다(1장 5-2 참조 무결성). 순서를 바꾸면 FK 위반 오류가 납니다.

```flow
list | 코드표 | code_uit 등 (부모) | lime
package | part_master | uit → code_uit (자식) | plum
```

:::note \copy 옵션 읽기
- `CSV` — 쉼표로 구분된 파일
- `HEADER` — 첫 줄은 컬럼 이름이므로 건너뜀
- `ENCODING 'UTF8'` — 파일 글자 코드가 UTF-8 (한글 품명이 깨지지 않게)
- `NULL ''` — 빈 칸을 NULL로 넣음. CSV 형식의 기본 동작을 명시한 것으로, `svc_code`, `po_price`에 빈 값이 있는 `part_master`, `part_sourcing`에만 적혀 있음
:::

### 6-4. DB · 스키마 · 테이블의 관계 {keep}

```text 서버 > DB > 스키마 > 테이블
PostgreSQL 서버 (localhost:5432)
 ├─ postgres        ← 기본 DB
 └─ bom_lab         ← 우리가 만든 DB
     ├─ public      ← 기본 스키마 (비어 있음)
     └─ bom         ← 스크립트가 만든 스키마
         ├─ part_master
         ├─ bom_structure
         └─ … (테이블 17개)
```

> 스키마는 **DB 안의 폴더**입니다. 같은 DB 안에서 테이블을 묶어 관리합니다. 테이블의 정식 이름은 `bom.part_master`처럼 `스키마.테이블`입니다.

## 7. 적재 확인

### 7-1. 스키마와 테이블 목록 {keep}

:::cols
```psql 결과에 테이블 17개가 보이면 성공
\dn
\dt bom.*
```

```shot `\dt bom.*` 실행 결과 — 맨 아래 (17 rows)
unit02/08-dt-tables.png
```
:::

### 7-2. 테이블별 행 수 맞춰 보기

```sql 테이블별 행 수 (17개)
SELECT 'part_master' AS 테이블, COUNT(*) AS 행수 FROM bom.part_master
UNION ALL SELECT 'bom_structure',       COUNT(*) FROM bom.bom_structure
UNION ALL SELECT 'vendor',              COUNT(*) FROM bom.vendor
UNION ALL SELECT 'part_sourcing',       COUNT(*) FROM bom.part_sourcing
UNION ALL SELECT 'site_part_attr',      COUNT(*) FROM bom.site_part_attr
UNION ALL SELECT 'uit_change_history',  COUNT(*) FROM bom.uit_change_history
UNION ALL SELECT 'part_status_history', COUNT(*) FROM bom.part_status_history
UNION ALL SELECT 'production_plan',     COUNT(*) FROM bom.production_plan
UNION ALL SELECT 'inventory',           COUNT(*) FROM bom.inventory
UNION ALL SELECT 'scheduled_receipt',   COUNT(*) FROM bom.scheduled_receipt
UNION ALL SELECT 'code_uit',            COUNT(*) FROM bom.code_uit
UNION ALL SELECT 'code_uom',            COUNT(*) FROM bom.code_uom
UNION ALL SELECT 'code_status',         COUNT(*) FROM bom.code_status
UNION ALL SELECT 'code_supply_type',    COUNT(*) FROM bom.code_supply_type
UNION ALL SELECT 'code_line_type',      COUNT(*) FROM bom.code_line_type
UNION ALL SELECT 'code_svc',            COUNT(*) FROM bom.code_svc
UNION ALL SELECT 'code_cosp',           COUNT(*) FROM bom.code_cosp;
```

### 7-2. 기대값 {keep}

```stats 제공 CSV 행 수 기준
table | 17 | 테이블
rows-3 | 360 | 전체 행
package | 68 | 품번
list-tree | 82 | BOM 라인
```

| 그룹 | 테이블 | 행 수 |
| --- | --- | --- |
| 마스터 | `part_master` · `vendor` | 68 · 12 |
| BOM·소싱 | `bom_structure` · `part_sourcing` · `site_part_attr` | 82 · 52 · 16 |
| 계획·재고 | `production_plan` · `inventory` · `scheduled_receipt` | 20 · 53 · 6 |
| 이력 | `uit_change_history` · `part_status_history` | 5 · 5 |
| 코드표 | `code_uit` · `code_uom` · `code_status` · `code_supply_type` · `code_line_type` · `code_svc` · `code_cosp` | 11 · 7 · 6 · 3 · 9 · 2 · 3 |

### 7-3. search_path — 매번 bom.을 붙여야 하나요? {keep}

**`search_path`** 는 테이블 이름만 썼을 때 PostgreSQL이 **어느 스키마에서 그 테이블을 찾을지** 정한 순서입니다. 실습 테이블은 모두 `bom` 스키마 안에 있으므로 정식 이름은 `bom.part_master`처럼 `스키마.테이블`입니다.

```sql
SELECT * FROM bom.part_master;    -- 스키마를 직접 적음 → 항상 찾음
SELECT * FROM part_master;        -- 스키마 생략 → search_path에 있는 스키마에서 찾음
```

| 상태 | `search_path` | `part_master`만 썼을 때 |
| --- | --- | --- |
| 기본값 | `"$user", public` (접속 계정 이름의 스키마 → `public`) | `bom`을 찾지 않아 ==테이블을 못 찾음== |
| `SET search_path TO bom;` 실행 후 | `bom` | `bom.part_master`를 찾음 |

### 7-3. bom 폴더 안에 들어가 있는 상태 {keep}

폴더에 빗대면 **`bom` 폴더 안으로 들어가 있는 상태**입니다. 그 안에서는 파일 이름만 불러도 찾을 수 있습니다.

지금 설정은 아래 명령으로 확인합니다.

```sql
SHOW search_path;
```

스크립트 안의 `SET search_path TO bom;`은 **그 접속에서만** 유효합니다. psql을 껐다 켜거나 pgAdmin에서 새로 접속하면 다시 기본값으로 돌아가, `part_master`만 쓰면 테이블을 못 찾습니다.

```error
ERROR:  relation "part_master" does not exist
```

### 7-3. 해결 방법 두 가지 {keep}

```sql ① 접속할 때마다 한 번 실행 (수업 기본 방식)
SET search_path TO bom;
```

```sql ② bom_lab DB의 기본값으로 저장 (한 번만 실행하면 다음 접속부터 적용)
ALTER DATABASE bom_lab SET search_path TO bom, public;
```

> ②를 실행한 뒤에는 **새로 접속한 창부터** 적용됩니다. 지금 창에는 ①을 한 번 더 실행하세요.

:::teacher 강사 확인
- 운영안은 ①(`SET search_path TO bom;`)을 기준으로 합니다. ②를 수업 표준으로 쓸지는 강사가 정해 주세요. ②를 쓰면 pgAdmin 실습 중 `relation … does not exist` 질문이 크게 줄어듭니다.
- README 3장 안내대로, `exercises_mysql.sql`을 PostgreSQL에서 쓸 때는 `bom.` 접두사를 붙이거나 search_path를 설정해야 합니다.
:::

### 7-4. 테이블 사전 — 17개 테이블은 각각 무엇인가 {keep}

방금 적재한 데이터는 **창원(CW) 가전 공장**의 생산 데이터입니다. 공장에서 일어나는 일을 따라가면 테이블 17개가 순서대로 나옵니다.

```rows
- | 공장에서 일어나는 일 | 테이블 | 담긴 내용
package | 어떤 물건을 다루나 | `part_master` | 완제품부터 나사 하나까지, 회사가 다루는 모든 품목의 명부
building-2 | 누구에게서 사 오나 | `vendor` · `part_sourcing` | 협력사 명단 · 어떤 부품을 어느 업체에서 얼마에 사는지
list-tree | 무엇으로 만드나 | `bom_structure` | 제품 하나에 어떤 부품이 몇 개 들어가는지(제품의 레시피)
calendar | 언제 얼마나 만드나 | `production_plan` | 12월 1~14일 라인별 생산 대수
warehouse | 지금 무엇이 있고 무엇이 오나 | `inventory` · `scheduled_receipt` | 창고 재고 · 앞으로 들어올 자재
history | 무엇이 바뀌었나 | `uit_change_history` · `part_status_history` · `site_part_attr` | 품목 유형·상태가 바뀐 기록 · 공장마다 다르게 관리하는 품목
book-open | 코드는 무슨 뜻인가 | `code_` 로 시작하는 7개 | `G`, `3`, `EA` 같은 코드를 사람이 읽는 말로 풀어 둔 표
```

### 7-4. part_master — 품목 명부 (68행) {keep}

회사가 다루는 **모든 물건의 신분증**입니다. 냉장고 완제품, 그 안의 도어 조립체, 컴프레서, 나사, 수지 원료까지 한 행에 하나씩 들어 있습니다.

| 컬럼 | 의미 | 데이터 예와 뜻 |
| --- | --- | --- |
| `part_no` | 품번. 물건마다 붙는 11자리 번호 | `ECP39799101` — 앞 3자리 `ECP`는 분류, 끝 2자리 `01`은 시리즈 |
| `description` · `description_kr` | 영문 · 한글 품명 | `Compressor,Reciprocating` · 컴프레서 |
| `class_lv1` | 대분류 (품번 첫 글자) | `T` 완제품 세트 · `A` 조립체 · `E` 전기·전자 · `M` 기구 · `R` 원자재 · `F` 나사·테이프 · `S` 소프트웨어 |
| `class_lv2` | 중분류 (품번 앞 3자리) | `ECP` 컴프레서 · `FSC` 나사 · `MHG` 힌지 |
| `tech_spec` | 규격 — 크기·재질·사양 | `M4x12 Zinc` — 굵기 4mm·길이 12mm 아연 도금 나사 |
| `uom` | 수량을 세는 단위 | `EA` 개 · `KG` 킬로그램 · `SH` 장 |
| `uit` | 품목 유형 — 누가 만들고 재고를 어떻게 관리하나 | `T` 사내 조립품 · `G` 국내 구매품 · `D` 수입 구매품 |
| `status_code` | 지금 이 품번의 상태 | `3` 승인(양산 중) · `5` 폐기 예정 · `1` 폐기 |
| `svc_code` · `svc_location_no` | A/S용으로도 파는 부품인가 · 서비스 부품 위치 | `R` 서비스 전용 · `Z` 소모품 겸 서비스(필터 등) · 비어 있으면 생산용만 |
| `created_at` | 품번을 등록한 날 | 2025-02-06 |

### 7-4. vendor — 협력사 명단 (12행) {keep}

부품과 원자재를 **공급하는 회사**의 목록입니다.

| 컬럼 | 의미 | 데이터 예와 뜻 |
| --- | --- | --- |
| `vendor_code` | 업체 번호 | `V1001` |
| `vendor_name` | 업체 이름 | 한빛정밀(주) |
| `country` | 업체가 있는 나라 | `KR` 한국 · `CN` 중국 · `JP` 일본 · `TW` 대만 · `VN` 베트남 |
| `is_domestic` | 국내 업체인가 | `Y` 국내 · `N` 해외 |
| `main_item` | 주로 공급하는 것 | 판금·프레스 · 수지 원료 · 가스켓·호스 |

> `V1012` **LG 사내 부품라인(C1)** 은 회사 밖 업체가 아니라 공장 안의 부품 생산 라인입니다. 사내에서 만든 부품도 업체처럼 번호를 붙여 거래를 기록합니다.

### 7-4. bom_structure — 제품의 레시피 (82행) {keep}

**제품 하나를 만드는 데 무엇이 몇 개 들어가는지** 적은 표입니다. 한 행은 "이것(부모) 1개에 저것(자식)이 몇 개 들어간다"는 한 줄입니다. 냉장고·세탁기 두 모델의 구성이 1~3단계로 내려갑니다.

| 컬럼 | 의미 | 데이터 예와 뜻 |
| --- | --- | --- |
| `bom_id` | 줄 번호 | `1` |
| `model_part_no` | 이 줄이 속한 완제품 모델 | `TRF38316001` 냉장고 세트 |
| `parent_part_no` | 조립되는 쪽 (부모) | `TRF38316001` 냉장고 세트 |
| `child_part_no` | 들어가는 쪽 (자식) | `ACB22943901` 캐비닛 조립체 |
| `bom_level` | 완제품에서 몇 단계 아래인가 | `1` 완제품에 바로 들어감 · `3` 조립체의 조립체에 들어감 |
| `qty_per` · `uom` | 부모 1개에 들어가는 양과 단위 | `2` `EA` → 2개 · `0.35` `KG` → 수지 0.35kg |
| `supply_type` | 이 자재가 라인에 오는 방식 | `Assembly Pull` LG가 발주·입고 · `Supplier` 협력사가 알아서 조달 · `Phantom` 공정 관리용, 재고 없음 |
| `c_osp_flag` | 유상사급인가 — LG가 산 자재를 협력사에 **돈 받고 넘겨** 가공시키나 | `Y` 유상사급 · `N` 직거래·협력사 자체 제작 · `H` 둘 다 |
| `effective_from` | 이 구성을 적용하기 시작한 날 | 2026-01-01 |

### 7-4. part_sourcing — 구매 조건표 (52행) {keep}

**어떤 부품을 어느 업체에서, 얼마에, 어떤 조건으로 사는지** 적은 표입니다. 같은 부품을 두 업체에서 사면 두 행이 됩니다.

| 컬럼 | 의미 | 데이터 예와 뜻 |
| --- | --- | --- |
| `part_no` | 사는 부품 | `FSC67181101` 나사 M4x12 |
| `vendor_code` | 사 오는 업체 | `V1001` 한빛정밀(주) |
| `site_code` | 사는 공장 | `CW` 창원 |
| `line_type` | 구매 방식 | `D` 국내 구매 · `I` 수입 · `N` 사내 거래 · `S` 유상사급 |
| `po_price` · `currency` | 1개(1단위) 구매 단가와 통화 | `12` `KRW` → 나사 1개 12원 · `14.0` `USD` |
| `lead_time_days` | 주문하고 받을 때까지 걸리는 날 수 | `7` → 1주일 |
| `moq` | 한 번에 주문해야 하는 최소 수량 | `10000` → 나사는 1만 개 단위로 주문 |

### 7-4. production_plan — 생산계획 (20행) {keep}

**언제, 어느 라인에서, 어떤 모델을 몇 대 만들지** 정한 표입니다. 12월 1일부터 14일까지의 계획이 들어 있습니다.

| 컬럼 | 의미 | 데이터 예와 뜻 |
| --- | --- | --- |
| `plan_id` | 계획 번호 | `1` |
| `plan_date` | 생산하는 날 | 2026-12-01 |
| `site_code` | 공장 | `CW` 창원 |
| `line_code` | 생산 라인 | `LINE-A` 세탁기 라인 · `LINE-B` 냉장고 라인 |
| `model_part_no` | 만들 완제품 모델 | `TRF38316001` 냉장고 세트 |
| `plan_qty` | 만들 대수 | `380` → 그날 냉장고 380대 |
| `shift` | 근무조 | `D` (이 데이터에는 `D`만 있음) |

> 생산계획 × BOM의 `qty_per`를 하면 **그날 필요한 부품 수량**이 나옵니다. 뒤 단원에서 재고·입고 예정과 비교해 부족한 부품을 찾습니다.

### 7-4. inventory — 창고 재고 (53행) {keep}

**2026년 11월 30일 기준으로 창고에 있는 수량**입니다.

| 컬럼 | 의미 | 데이터 예와 뜻 |
| --- | --- | --- |
| `site_code` | 공장 | `CW` 창원 |
| `part_no` | 보관 중인 품목 | `FSC67181101` 나사 M4x12 |
| `location` | 보관 창고 | `WH-A` 자재 창고 · `WH-C1` 사내 부품라인(C1) 창고 |
| `on_hand_qty` | 지금 있는 수량 (단위는 품목의 `uom`) | `372486` → 나사 37만여 개 |
| `as_of_date` | 언제 기준 수량인가 | 2026-11-30 (모든 행 같음) |

### 7-4. scheduled_receipt — 입고 예정 (6행) {keep}

**아직 도착하지 않았지만 앞으로 들어올 자재**입니다. 재고와 합쳐서 "계획한 날까지 부품이 충분한가"를 판단할 때 씁니다.

| 컬럼 | 의미 | 데이터 예와 뜻 |
| --- | --- | --- |
| `receipt_id` | 입고 예정 번호 | `1` |
| `site_code` | 들어올 공장 | `CW` 창원 |
| `part_no` | 들어올 품목 | `ECP39799101` 컴프레서 |
| `vendor_code` | 보내는 업체 | `V1004` |
| `eta_date` | 도착 예정일 | 2026-12-08 |
| `qty` | 들어올 수량 | `800` → 컴프레서 800대 |
| `po_no` | 구매 주문서 번호 | `PO26-1101` |
| `receipt_type` | 입고가 얼마나 확실한가 | `Scheduled` 주문이 확정된 입고 · `Planned` 아직 계획 단계 |

### 7-4. 변경 이력 두 가지 (각 5행) {keep}

품목은 한 번 정해지면 끝이 아니라 **외주화·내재화·설계 변경으로 바뀝니다.** 그 기록입니다.

`uit_change_history` — **품목 유형(UIT)이 바뀐 기록**

| 컬럼 | 의미 | 데이터 예와 뜻 |
| --- | --- | --- |
| `change_id` · `part_no` | 변경 번호 · 바뀐 품목 | `1` · `EBA56264701` PCB |
| `old_uit` → `new_uit` | 바뀌기 전 → 뒤 유형 | `T` → `G` 사내 조립하던 것을 국내에서 사 오게 됨 |
| `changed_by_dept` · `change_reason` | 바꾼 부서 · 이유 | Manufacturing Engineering · PCB 조립 외주화 |
| `changed_at` · `line_type_updated` | 바꾼 날 · 구매 방식도 함께 바꿨나 | 2026-03-12 · `Y` |

`part_status_history` — **상태가 바뀐 기록**

| 컬럼 | 의미 | 데이터 예와 뜻 |
| --- | --- | --- |
| `part_no` | 상태가 바뀐 품목 | `MHG51215701` 도어 힌지(구형) |
| `old_status` → `new_status` | 바뀌기 전 → 뒤 상태 | `3` → `5` 양산 중이던 것을 폐기 예정으로 |
| `changed_at` · `reason` | 바꾼 날 · 이유 | 2026-04-01 · 신규 힌지로 설계 변경 |

### 7-4. site_part_attr — 공장마다 다른 품목 속성 (16행) {keep}

같은 부품이라도 **공장에 따라 직접 만들기도 하고 사 오기도 합니다.** 그래서 공장별 유형·상태를 따로 적어 둡니다.

| 컬럼 | 의미 | 데이터 예와 뜻 |
| --- | --- | --- |
| `site_code` · `site_name` | 공장 | `CW` 창원 · `HN` 해외법인 |
| `part_no` | 품목 | `EBA56264701` PCB |
| `uit` | 이 공장에서의 품목 유형 | 창원 `G`(국내 구매) · 해외법인 `T`(사내 조립) |
| `status_code` | 이 공장에서의 상태 | `3` 승인(양산 중) |

> 같은 PCB를 창원은 사 오고 해외법인은 직접 조립합니다. `part_master`의 `uit`는 대표값 하나뿐이라, 공장별 차이는 이 표에서 봅니다.

### 7-4. 코드표 7개 — 코드를 말로 풀어 둔 표 {keep}

다른 테이블에는 `G`, `3`, `EA`처럼 **짧은 코드**만 들어 있습니다. 코드표는 그 코드가 무슨 뜻인지 적어 둔 사전입니다. 모두 **코드 + 영문 뜻(`meaning_en`) + 한글 뜻(`meaning_kr`)** 이 기본입니다.

| 코드표 | 무엇을 나타내나 | 코드와 뜻 |
| --- | --- | --- |
| `code_uit` (11) | 품목 유형 | 완제품 `F`·`C`·`Q` · 사내 제작 `T`·`P` · 협력사 제작 `S`·`M`·`R` · 구매 `G` 국내·`D` 수입 · 관리용 `X` |
| `code_status` (6) | 품번 상태 | `1` 폐기 · `2` 등록 처리중 · `3` 승인(양산) · `4` 서비스 전용 · `5` 폐기 예정 · `6` 생산 중단 |
| `code_uom` (7) | 수량 단위 | `EA` 개 · `SH` 장 · `MZ` 미터 · `KG` · `GR` 그램 · `ST` 세트 · `LI` 리터 |
| `code_supply_type` (3) | 자재 공급 방식 | `Assembly Pull` · `Supplier` · `Phantom` |
| `code_line_type` (9) | 구매 방식 | 상품 `Q`·`V`·`P` · 부품 `D` 국내 · `I` 수입 · `N` 사내 거래 · `S` 유상사급 · `R`·`M` 무상사급 |
| `code_svc` (2) | 서비스 부품 구분 | `R` 서비스 전용 · `Z` 소모품 겸 서비스 |
| `code_cosp` (3) | 유상사급 구분 | `Y` 유상사급 · `N` 직거래·자체 제작 · `H` 둘 다 |

> 몇몇 코드표에는 뜻 말고도 정보가 더 있습니다. `code_uit`의 `classification`·`maker`(누가 만드나), `code_status`의 `active_flag`·`system_effect`(그 상태에서 발주·BOM 변경이 되는지), `code_uom`의 `uom_class`(개수·길이·무게·부피), `code_line_type`의 `category`(상품·부품). 코드 하나하나는 13절에서 직접 조회하며 읽습니다.

# 실습 데이터 조회하기

## 8. pgAdmin 4로 접속하기

### 8-1. 서버 접속 {keep}

1. 시작 메뉴 → **pgAdmin 4** 실행 (첫 실행은 조금 오래 걸립니다)
2. 왼쪽 **Servers** 앞의 `>` 클릭 → **PostgreSQL 18** 클릭
3. 비밀번호 입력 창에 설치 때 정한 비밀번호 입력 → (선택) **Save Password** 체크 → OK

```shot Connect to Server — 비밀번호 입력 · Save Password 체크 후 OK
unit02/09-pgadmin-password.png
```

> 설치 프로그램이 내 PC 서버(`localhost:5432`)를 미리 등록해 두기 때문에, 접속 정보를 새로 만들 필요가 없습니다.

### 8-1. pgAdmin이 열리지 않을 때 {keep}

**원인** — Windows 11의 **스마트 앱 컨트롤**이 pgAdmin 안의 파이썬 파일을 "서명이 없다"며 막아서 pgAdmin 서버가 뜨지 못합니다.

:::cols
```shot 실행하자마자 뜨는 `Fatal Error` 창
unit02/14-pgadmin-fatal-error.png
```

1. 열린 pgAdmin 창을 모두 닫습니다. (작업 관리자에 `pgAdmin4.exe`가 남아 있으면 종료)
2. **Windows 보안 → 앱 및 브라우저 컨트롤 → 스마트 앱 컨트롤 설정 → 끄기**
3. pgAdmin 4를 다시 실행합니다.
:::

> 끌 때 "다시 켜려면 Windows를 재설치해야 한다"는 경고가 나올 수 있습니다. 끄기 어렵다면 조회 실습도 SQL Shell (psql)에서 그대로 할 수 있습니다.

:::teacher 강사 확인
- 스마트 앱 컨트롤이 켜진 Windows 11에서는 pgAdmin 내장 파이썬의 서명 없는 확장 파일(`.pyd`)이 차단되어 pgAdmin 서버가 뜨지 않습니다. 로그(`%APPDATA%\pgadmin4\pgadmin4.*.log`) 끝에 `ImportError: DLL load failed while importing _processors_cy`가 남고, 뒤의 한글 메시지는 깨져 보입니다.
- 학생 PC는 **Windows 보안 → 앱 및 브라우저 컨트롤 → 스마트 앱 컨트롤 설정**에서 상태를 미리 확인하세요. 끌 때 Windows 버전에 따라 "다시 켜려면 재설치가 필요하다"는 경고가 나올 수 있으므로, 끄기 어려운 학생은 조회 실습을 psql에서 진행하게 하면 됩니다.
:::

### 8-2. 테이블 확인 — 왼쪽 트리 펼치기 {keep}

```text pgAdmin 왼쪽 트리
Servers > PostgreSQL 18 > Databases > bom_lab > Schemas > bom > Tables
```

`Tables (17)` 이 보이면 적재가 끝난 상태입니다.

> 테이블이 안 보이면 **bom_lab** 또는 **Tables**에서 마우스 오른쪽 클릭 → **Refresh**.

### 8-2. 트리를 펼친 화면 {keep}

:::cols
```shot ① Servers → PostgreSQL 18 → bom_lab → Schemas → bom → Tables (17)
unit02/10-tree-open.png
```

```shot ② Tables (17)을 펼치면 테이블 17개
unit02/11-tree-tables.png
```
:::

### 8-3. 쿼리 창 열기 {keep}

:::cols
1. 트리에서 **bom_lab** 클릭 (어느 DB에 쿼리를 보낼지 고르는 것)
2. 위쪽 메뉴 **Tools → Query Tool**
3. 쿼리를 쓰고 **F5** 또는 ▶ (Execute) 버튼으로 실행

```shot Tools 메뉴 → Query Tool
unit02/12-tools-menu.png
```
:::

### 8-3. Query Tool 화면 {keep}

:::cols
```shot Query Tool — 위: 쿼리 입력(Query), 아래: 실행 결과(Data Output)
unit02/13-query-tool.png
```

> 쿼리 창 제목에 `bom_lab/postgres@PostgreSQL 18`처럼 **DB 이름/계정**이 보입니다. 여기가 `postgres`로 되어 있으면 엉뚱한 DB에 접속한 것입니다.
:::

### 8-4. 적재는 psql, 조회는 pgAdmin {keep}

:::error
`schema_postgres.sql`을 pgAdmin Query Tool에 붙여 넣고 실행하면 `\copy` 줄에서 오류가 납니다. `\copy`는 **psql 전용 메타 명령**이라 pgAdmin은 이해하지 못합니다(스크립트에도 「psql 전용 메타커맨드」라고 적혀 있습니다). ==적재는 psql, 조회는 pgAdmin==으로 나눠 쓰세요.
:::

## 9. 첫 쿼리

### 9-1. part_master 10행 보기 {keep}

pgAdmin Query Tool에서 실행합니다.

```sql
SET search_path TO bom;    -- 7-3에서 ②를 했다면 생략 가능

SELECT * FROM part_master LIMIT 10;
```

- `SELECT *` — 모든 컬럼을
- `FROM part_master` — 품목 마스터 테이블에서
- `LIMIT 10` — 10행만 보여 줘

### 9-1. 실행 결과 {keep}

```result 앞 5행, 일부 컬럼만 표시
| part_no | description | description_kr | uom | uit | status_code |
| --- | --- | --- | --- | --- | --- |
| FSC67181101 | Screw,Customized | 나사 M4x12 | EA | G | 3 |
| FSC33042701 | Screw,Customized | 나사 M5x16 | EA | G | 3 |
| FTP68745401 | Tape,Filament | 필라멘트 테이프 | MZ | G | 3 |
| RRS44997401 | Resin,ABS | ABS 수지 | KG | G | 3 |
| RPP53183301 | Resin,PP | PP 수지 | KG | G | 3 |
```

> `ORDER BY`(정렬)를 쓰지 않았으므로 **행 순서는 보장되지 않습니다.** 방금 적재한 DB에서는 보통 CSV 순서대로 나오지만, 다른 행이 보여도 오류가 아닙니다.

### 9-2. 1장과 연결해서 읽어 보기 {keep}

- `part_no` = 1장 4-2 예시 ③의 **품번**, `part_master`의 **PK**
- `uom`, `uit`, `status_code` = 각각 `code_uom`, `code_uit`, `code_status`를 참조하는 **FK** (1장 7-4 FK 정리표)
- `uit`가 `G`인 행 → `code_uit`에서 `G`의 뜻을 찾으면 됩니다. 이렇게 **두 테이블을 잇는 방법(JOIN)** 을 뒤에서 배웁니다.

### 9-3. 직접 해 보기 {keep}

:::try 직접 해 보기
1. `vendor` 테이블 전체를 조회해 보세요. 행이 몇 개 나오나요?
2. `code_uit` 테이블을 조회해 `G`와 `D`가 각각 무슨 뜻인지 찾아보세요.
3. pgAdmin 왼쪽 트리에서 `part_sourcing` → **Constraints**를 펼쳐 PK와 FK가 몇 개 있는지 확인해 보세요. 1장 7-4 관계 모델 그림과 비교합니다.
:::

:::answer
1. 12행 (`SELECT * FROM vendor;`)
2. `SELECT * FROM code_uit;` — `meaning_kr` 컬럼에서 확인합니다. G = 국내 구매품, D = 수입 구매품
3. PK 1개(`part_no + vendor_code + site_code` 복합키), FK 3개(`part_no` → `part_master`, `vendor_code` → `vendor`, `line_type` → `code_line_type`). `schema_postgres.sql`의 `part_sourcing` 정의와 같습니다.
:::

## 10. 복습 — hr 데이터도 적재하기

### 10-1. 같은 순서로 한 번 더 — 파일 준비 {keep}

지금까지 한 순서(**파일 준비 → psql 접속 → `\i` 실행 → 적재 확인**)를 직원·부서 인사(HR) 샘플 데이터로 **한 번 더 혼자** 해 봅니다. 같은 `bom_lab` DB 안에 `hr` 스키마를 하나 더 만듭니다.

:::cols
```text 같은 DB에 스키마 하나 더
PostgreSQL 서버 (localhost:5432)
 └─ bom_lab
     ├─ public
     ├─ bom      ← 앞에서 적재 (테이블 17개)
     └─ hr       ← 이번에 적재 (테이블 7개 + 뷰 1개)
```

> **파일 준비** — `hr_postgres.sql`을 `C:\bom_lab` 폴더에 복사합니다. 이 스크립트는 CSV 없이 **`INSERT` 문으로 데이터를 넣기 때문에** 파일 하나만 있으면 됩니다.
:::

### 10-2. psql에서 실행 {keep}

```psql
\c bom_lab
\cd 'C:/bom_lab'
\encoding UTF8
\i hr_postgres.sql
\encoding UHC
```

- 6-2와 같이 **읽을 때 UTF8 → 다 읽고 나서 UHC**로 되돌립니다.

- `INSERT 0 1`은 **한 행을 넣었다**는 뜻입니다. 행마다 한 줄씩 나오므로 화면이 길게 올라갑니다.
- 스크립트가 끝나면 `SET search_path TO hr;`이 실행된 상태입니다. 이제 이 창에서 `part_master`만 쓰면 못 찾으니, `bom` 테이블도 쓰려면 `SET search_path TO bom, hr;`을 실행하세요(10-5).

### 10-2. 화면에 나오는 내용 {keep}

```result 화면에 나오는 내용 (일부)
psql:hr_postgres.sql:…: NOTICE:  schema "hr" does not exist, skipping
DROP SCHEMA
CREATE SCHEMA
SET
CREATE TABLE
…
INSERT 0 1
INSERT 0 1
…
ALTER TABLE
CREATE INDEX
…
CREATE VIEW
…
COMMENT
```

### 10-3. 스크립트는 무슨 일을 했나요? {keep}

| 순서 | 문장 | 하는 일 | 앞에서 배운 것 |
| --- | --- | --- | --- |
| 1 | `DROP SCHEMA IF EXISTS hr CASCADE;` · `CREATE SCHEMA hr;` | `hr` 스키마를 새로 만듦 | 6-3과 같음 |
| 2 | `CREATE TABLE …` × 7 | `regions` → `countries` → `locations` → `departments` → `jobs` → `employees` → `job_history` 순서로 생성 | ==부모 먼저, 자식 나중== |
| 3 | `INSERT INTO … VALUES (…);` | 데이터를 한 행씩 넣음 | `\copy` 대신 SQL 문으로 넣는 방법 |
| 4 | `ALTER TABLE departments ADD CONSTRAINT dept_mgr_fk …` | 부서장(`manager_id`) → 직원 FK를 **데이터를 다 넣은 뒤** 추가 | 부서와 직원이 서로를 참조하기 때문 |
| 5 | `CREATE INDEX` · `CREATE VIEW` · `COMMENT ON` | 검색용 인덱스, 조인 뷰 `emp_details_view`, 테이블·컬럼 설명 | 1장 6. 물리적 모델링(인덱스) |

### 10-3. 4번은 왜 나중에 할까요? {keep}

부서는 부서장(직원)을, 직원은 소속 부서를 참조합니다. 둘 다 처음부터 FK를 걸면 **어느 쪽도 먼저 넣을 수 없습니다.** 그래서 데이터를 다 넣은 뒤 FK 하나를 추가합니다.

```icons 서로를 참조하는 두 테이블
building-2 | departments | 부서장(`manager_id`)이 **직원**을 참조 | plum | [FK] `dept_mgr_fk` — 나중에 추가
users | employees | 소속 부서가 **부서**를 참조 | lime | [FK] `emp_dept_fk` — 테이블 만들 때
```

### 10-4. 직접 확인해 보기 {keep}

:::try 직접 해 보기
1. `\dn`으로 스키마 목록을 보고, `bom`과 `hr`이 둘 다 있는지 확인하세요.
2. `\dt hr.*`로 `hr` 스키마의 테이블이 몇 개인지 세어 보세요. 뷰는 `\dv hr.*`로 봅니다.
3. 아래 「10-4. hr 테이블별 행 수」의 쿼리를 실행해 행 수가 기대값과 같은지 확인하세요.
4. pgAdmin 왼쪽 트리에서 `bom_lab > Schemas > hr > Tables > employees > Constraints`를 펼쳐 FK가 몇 개이고, 각각 어느 테이블을 가리키는지 적어 보세요. (`hr`이 안 보이면 **Schemas**에서 마우스 오른쪽 클릭 → **Refresh**)
5. `job_history`의 PK는 컬럼 몇 개로 이루어져 있나요? 1장에서 배운 용어로 무엇이라고 부르나요?
:::

:::answer
1. `bom`, `hr`, `public` 세 개가 보입니다.
2. 테이블 7개, 뷰 1개(`emp_details_view`)
3. 아래 「10-4. hr 테이블별 행 수」의 기대값과 같으면 성공입니다.
4. FK 3개 — `emp_dept_fk`(→ `departments`), `emp_job_fk`(→ `jobs`), `emp_manager_fk`(→ `employees` **자기 자신**). 직원의 매니저도 직원이라 같은 테이블을 참조합니다. `bom_structure`가 `part_master`를 부모·자식으로 참조하는 것과 비슷한 구조입니다.
5. 2개(`employee_id + start_date`) → **복합키**. `employee_id`는 `employees`를 참조하는 FK이면서 PK의 일부이므로 `employees`와 `job_history`는 **식별 관계**입니다.
:::

### 10-4. hr 테이블별 행 수 {keep}

```sql hr 테이블별 행 수 (7개)
SELECT 'regions' AS 테이블, COUNT(*) AS 행수 FROM hr.regions
UNION ALL SELECT 'countries',   COUNT(*) FROM hr.countries
UNION ALL SELECT 'locations',   COUNT(*) FROM hr.locations
UNION ALL SELECT 'departments', COUNT(*) FROM hr.departments
UNION ALL SELECT 'jobs',        COUNT(*) FROM hr.jobs
UNION ALL SELECT 'employees',   COUNT(*) FROM hr.employees
UNION ALL SELECT 'job_history', COUNT(*) FROM hr.job_history;
```

**기대값** (`hr_postgres.sql` 머리말 기준, 합계 215행)

| 테이블 | `regions` | `countries` | `locations` | `departments` | `jobs` | `employees` | `job_history` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 행 수 | 4 | 25 | 23 | 27 | 19 | 107 | 10 |

### 10-5. 두 스키마를 함께 쓰려면 {keep}

`search_path`에는 스키마를 **여러 개** 적을 수 있습니다. 적은 순서대로 찾습니다.

```sql ① 지금 창에서만
SET search_path TO bom, hr;
```

```sql ② bom_lab DB의 기본값으로 저장 (7-3 ②를 대신함)
ALTER DATABASE bom_lab SET search_path TO bom, hr, public;
```

> `bom`의 테이블 17개와 `hr`의 테이블 7개는 이름이 겹치지 않으므로, 두 스키마를 함께 적어도 `part_master`와 `employees`를 각각 찾습니다.

:::teacher 강사 확인
- `hr_postgres.sql` 머리말 기준: PostgreSQL 13 이상 대상, 16에서 실행 검증. 수업 PC(18)에서 미리 한 번 실행해 확인하세요.
- 스크립트 머리말에 원본(`github.com/oracle-samples/db-sample-schemas`, MIT License) 표기가 있으므로 배포 시 머리말을 지우지 마세요.
- 이 스크립트는 `\copy`가 없어 pgAdmin Query Tool에서도 실행할 수 있습니다. 복습 목적상 psql로 진행하고, 시간이 남으면 pgAdmin으로 다시 실행해 보게 해도 됩니다(첫 줄 `DROP SCHEMA … CASCADE`로 처음 상태가 됩니다).
:::

## 11. 자주 하는 실수와 해결

### 11-1. 증상별 해결표

| 증상 (메시지) | 원인 | 해결 |
| --- | --- | --- |
| `password authentication failed for user "postgres"` | 비밀번호 틀림 | 설치할 때 정한 비밀번호 확인 (수업용 `12345`) |
| `part_master.csv: No such file or directory` | psql의 현재 폴더에 CSV가 없음 | `\cd 'C:/bom_lab'` 후 다시 `\i schema_postgres.sql` |
| `\i` 실행 시 `schema_postgres.sql: No such file or directory` | 폴더 이동을 안 했거나 경로 오타 | 경로를 `/`로, 작은따옴표로 감쌌는지 확인 |
| `0xec 0x9e 바이트로 조합된 문자(인코딩: "UHC")와 대응되는 문자 코드가 "UTF8" 인코딩에는 없습니다` (영문: `character with byte sequence … in encoding "UHC" has no equivalent in encoding "UTF8"`) 뒤로 `relation "part_master" does not exist`가 줄줄이 | psql이 UTF-8 스크립트를 UHC로 읽어 한글 주석이 든 `CREATE TABLE`이 실패 | `\encoding UTF8` 입력 후 `\i schema_postgres.sql` 다시 실행 |
| `\dn`·`\dt` 결과의 한글 머리글이 `\xB8\xA7`, `테\u000C\xBA`처럼 깨짐 (영문 값은 정상) | `\encoding UTF8` 상태로 결과를 보는 중. 콘솔은 949(UHC)로 글자를 그림 | `\encoding UHC` 입력. 데이터는 정상이므로 다시 적재할 필요 없음 |
| `relation "part_master" does not exist` | search_path가 `bom`이 아님 / 다른 DB에 접속 | `SET search_path TO bom;` 실행, 접속 DB가 `bom_lab`인지 확인 (`\conninfo`) |
| pgAdmin 실행 시 `The pgAdmin 4 server could not be contacted` 창 (Fatal Error) | Windows 11 **스마트 앱 컨트롤**이 pgAdmin 내장 파이썬 파일을 차단 | pgAdmin 창을 모두 닫고 **Windows 보안 → 앱 및 브라우저 컨트롤 → 스마트 앱 컨트롤 설정 → 끄기** 후 다시 실행. 끄기 어렵다면 조회도 psql에서 진행 |
| pgAdmin에서 `\copy` 줄 syntax error | psql 전용 명령을 pgAdmin에서 실행 | 적재는 SQL Shell (psql)에서 |
| 프롬프트가 `bom_lab-#`에서 멈춤 | SQL 끝에 `;`이 없음 | `;` 입력 후 Enter |
| `database "bom_lab" already exists` | 이미 만든 DB를 다시 만듦 | 그대로 `\c bom_lab` 하면 됨 |
| hr 적재 후 `relation "part_master" does not exist` | `hr_postgres.sql`이 search_path를 `hr`로 바꿈 | `SET search_path TO bom, hr;` |
| 적재 중간에 오류가 나서 다시 하고 싶음 | — | `\i schema_postgres.sql`을 **다시 실행**. 첫 줄 `DROP SCHEMA … CASCADE`가 기존 것을 지우고 새로 만듦 |

## 12. 정리

### 12-1. 오늘 만든 것 {keep}

:::summary
- PostgreSQL = **서버**(데이터 보관·실행) + **psql**(명령줄) + **pgAdmin 4**(그래픽). 기본 계정 `postgres`, 포트 `5432`.
- 실습 DB `bom_lab` 안의 **`bom` 스키마**에 테이블 17개, 총 360행을 적재했습니다.
- 복습으로 같은 DB의 **`hr` 스키마**에 테이블 7개, 총 215행을 적재했습니다. 두 스키마를 함께 쓰려면 `SET search_path TO bom, hr;`.
- 적재 스크립트는 `\copy`(psql 전용)를 쓰므로 **적재는 psql**, **조회는 pgAdmin**.
- 테이블 이름만 쓰려면 `SET search_path TO bom;`.
- `schema_postgres.sql` = 1장 6. **물리적 모델링의 결과물**. 1장 ERD의 PK·FK가 여기서 실제 제약조건이 됩니다.
:::

### 12-2. 확인 문제

:::quiz
Q. psql에서 SQL 문과 메타 명령은 어떻게 구분하나요?
A. 메타 명령은 `\`로 시작하고 `;`이 필요 없습니다. SQL 문은 끝에 `;`을 붙여야 실행됩니다.

Q. `schema_postgres.sql`을 pgAdmin Query Tool에서 실행하면 안 되는 이유는?
A. CSV를 넣는 `\copy`가 psql 전용 메타 명령이라 pgAdmin에서는 실행되지 않기 때문입니다.

Q. 스크립트에서 코드표(`code_uit` 등)를 `part_master`보다 먼저 적재하는 이유는?
A. `part_master`의 `uit` 등이 코드표를 참조하는 FK이므로, 부모(코드표)에 값이 먼저 있어야 참조 무결성을 지킬 수 있기 때문입니다.

Q. pgAdmin에서 `SELECT * FROM part_master;`를 실행했더니 `relation "part_master" does not exist`가 나왔습니다. 확인할 두 가지는?
A. ① 쿼리 창이 `bom_lab` DB에 접속했는지 ② `SET search_path TO bom;`을 실행했는지(또는 `bom.part_master`로 썼는지)
:::

# 데이터 탐색 — 생산 도메인: 품목 관리

## 13. 코드표로 품목 읽기

:::teacher 강사 확인
- 운영안 Day 1 2H(생산 도메인: 품목 관리)에 해당합니다. 아래 쿼리 결과는 제공 CSV를 PostgreSQL 16에 `schema_postgres.sql`로 적재해 실행한 값과 같습니다.
- JOIN·GROUP BY가 들어 있지만 이 시간의 목표는 **문법이 아니라 코드 값의 뜻을 읽는 것**입니다. 쿼리는 복사해 실행하고 결과표를 함께 읽습니다.
- 본문의 「4단원 1-2·2-3」, 「데이터 사전(3장)」, 「Day 2 5교시(5장)」는 다른 단원 원고를 가리킵니다. 최종 단원 번호에 맞춰 확인해 주세요.
:::

### 13-1. 이번 시간에 읽을 다섯 가지 {keep}

SQL을 쓰기 전에 어떤 값이 무슨 뜻인지부터 읽습니다. 의미는 모두 DB 안의 코드표(`code_*`)에 들어 있습니다.

```icons
hash | P/No | 품번 11자리 = 분류코드 3 + 8 | rose | `ECP39799101`
tag | UIT | 누가 만들고, 어떻게 관리하나 | plum | `code_uit` 11종
history | Status | 품번의 라이프사이클 상태 (번호는 순서가 아님) | lime | `code_status` 6종
ruler | UOM | 수량을 세는 단위 | ivory | `code_uom` 7종
truck | Supply Type | BOM에서 자재가 어떻게 공급되나 | hot | `code_supply_type` 3종
```

```sql pgAdmin Query Tool에서 먼저 실행합니다 (7-3)
SET search_path TO bom;
```

### 13-2. P/No — 11자리 품번 읽기 {keep}

실습 데이터 설명서(README) 1장: 품번은 **3자리 분류코드 + 8자리**이고, 끝 2자리는 **시리즈**입니다.

```sql
SELECT part_no
     , LEFT(part_no, 3)         AS 분류코드
     , SUBSTRING(part_no, 4, 6) AS 일련번호
     , RIGHT(part_no, 2)        AS 시리즈
     , description
     , description_kr
  FROM part_master
 WHERE part_no IN ('TRF38316001', 'ECP39799101', 'MCK79020001', 'MHG51215701', 'MHG91254002')
 ORDER BY part_no;
```

### 13-2. P/No — 실행 결과 {keep}

```result
| part_no | 분류코드 | 일련번호 | 시리즈 | description | description_kr |
| --- | --- | --- | --- | --- | --- |
| ECP39799101 | ECP | 397991 | 01 | Compressor,Reciprocating | 컴프레서 |
| MCK79020001 | MCK | 790200 | 01 | Door,Outer | 도어 외판 |
| MHG51215701 | MHG | 512157 | 01 | Hinge,Door | 도어 힌지(구형) |
| MHG91254002 | MHG | 912540 | 02 | Hinge,Door | 도어 힌지 |
| TRF38316001 | TRF | 383160 | 01 | Refrigerator,Set | 냉장고 세트 |
```

- 분류코드 3자리는 `class_lv2`, 그 첫 글자는 `class_lv1`과 **68개 품번 모두 일치**합니다(`LEFT(part_no, 3) <> class_lv2`인 행 0개).
- 시리즈가 `02`인 품번은 `MHG91254002`(도어 힌지) 하나뿐입니다.

### 13-2. Description 규칙 — Main Function + Sub {keep}

실습 데이터 설명서(README) 1장: 영문 품명은 `Main Function,Sub` 형식입니다. 쉼표 앞뒤를 `SPLIT_PART`로 나눠 봅니다.

```sql
SELECT description
     , SPLIT_PART(description, ',', 1) AS main_function
     , SPLIT_PART(description, ',', 2) AS sub
  FROM part_master
 WHERE part_no IN ('ECP39799101', 'MCK79020001', 'FSC67181101',
                   'ACB22943901', 'RSS86949501')
 ORDER BY part_no;
```

### 13-2. Description — 실행 결과 {keep}

```result
| description | main_function | sub |
| --- | --- | --- |
| Cabinet Assembly | Cabinet Assembly |  |
| Compressor,Reciprocating | Compressor | Reciprocating |
| Screw,Customized | Screw | Customized |
| Door,Outer | Door | Outer |
| Sheet Steel,Stainless | Sheet Steel | Stainless |
```

`SPLIT_PART(문자열, 구분자, n)`은 구분자로 잘라 **n번째 조각**을 돌려줍니다. 쉼표가 없는 `Cabinet Assembly`는 2번째 조각이 **빈 문자열(NULL 아님)** 입니다.

### 13-3. UIT — 누가 만들고, 어떻게 관리하나 {keep}

```sql
SELECT p.uit, u.classification, u.maker, u.meaning_kr, COUNT(*) AS part_cnt
  FROM part_master p
  JOIN code_uit u ON u.uit = p.uit
 GROUP BY p.uit, u.classification, u.maker, u.meaning_kr
 ORDER BY u.classification, p.uit;
```

### 13-3. UIT — 실행 결과 {keep}

```result
| uit | classification | maker | meaning_kr | part_cnt |
| --- | --- | --- | --- | --- |
| D | Buy item | Vendor | 수입 구매품 | 7 |
| G | Buy item | Vendor | 국내 구매품 | 41 |
| X | Buy item | Management | 관리용(문서·정보) | 2 |
| F | Finished product | LG | 완제품(모델) | 2 |
| P | Make item | LG | 사내 중간 조립품, 재고 관리 없음(팬텀) | 8 |
| S | Make item | Vendor | 협력사 제작, 유상사급 품목 포함 | 2 |
| T | Make item | LG | 사내 조립품, 계획·표준시간·재고 관리 | 6 |
```

> `code_uit`에는 11종이 있지만 품목 마스터에는 **7종만** 쓰입니다(C·Q·M·R은 0개).

### 13-3. T와 P의 차이 — 재고를 관리하나? {keep}

두 UIT 모두 LG 사내 조립품입니다. 차이는 `meaning_kr`의 「재고 관리」 여부입니다. 재고 테이블과 붙여 **실제로 그런지** 확인합니다.

```sql
SELECT p.part_no, p.description_kr, p.uit
     , i.on_hand_qty, i.location
  FROM part_master p
  LEFT JOIN inventory i ON i.part_no = p.part_no
 WHERE p.uit IN ('T', 'P')
 ORDER BY p.uit DESC, p.part_no;
```

> pgAdmin에서는 NULL이 `[null]`로 보일 수 있습니다. 아래 결과표는 NULL로 적었습니다.

### 13-3. T — 실행 결과 {keep}

```result T — 6개
| part_no | description_kr | uit | on_hand_qty | location |
| --- | --- | --- | --- | --- |
| ACB22943901 | 캐비닛 조립체 | T | NULL | NULL |
| ACB29328801 | 캐비닛 조립체 | T | NULL | NULL |
| ACC12625601 | 냉동 사이클 조립체 | T | NULL | NULL |
| ADU49470801 | 구동부 조립체 | T | NULL | NULL |
| ATB35230801 | 터브 조립체 | T | NULL | NULL |
| EMT68237401 | DD 모터 | T | 900.00 | WH-C1 |
```

- T 중에서는 `EMT68237401`(DD 모터)만 재고가 있습니다. 실습 데이터 설명서(README) 1장: DD 모터는 사내 부품라인(C1)에서 만들어 메인라인으로 공급하는 T 품목이고, 위치도 `WH-C1`입니다.
- 나머지 T 5개는 재고 행이 없습니다. 코드표의 뜻과 실제 데이터가 다를 수 있다는 예입니다. 이것이 정상인지는 데이터만으로 판단할 수 없으므로 데이터 사전(3장)의 「확인 필요」 목록에 적습니다.

### 13-3. P — 실행 결과 {keep}

```result P — 8개
| part_no | description_kr | uit | on_hand_qty | location |
| --- | --- | --- | --- | --- |
| ACP85953101 | 컨트롤 패널 조립체 | P | NULL | NULL |
| ADR24872401 | 냉장실 도어 조립체 | P | NULL | NULL |
| ADR69737101 | 도어 조립체 | P | NULL | NULL |
| APK15762301 | 포장 조립체 | P | NULL | NULL |
| APK23572301 | 포장 조립체 | P | NULL | NULL |
| MCB45577701 | 외함 캐비닛 | P | NULL | NULL |
| MCB74311201 | 외함 캐비닛 | P | NULL | NULL |
| MLN40306101 | 내상 라이너 | P | NULL | NULL |
```

- P(팬텀) 8개는 모두 재고 행이 없습니다 — 코드표 뜻 그대로 「재고 관리 없음」.

### 13-3. G와 D의 차이 — 어디서 사 오나? {keep}

G·D 모두 구매품입니다. G는 국내, D는 수입입니다. 구매 속성 `line_type`과 업체의 `is_domestic`을 함께 봅니다. `line_type`의 D·I는 UIT의 D와 글자만 같은 **다른 코드**이며, 뜻은 `code_line_type`에서 확인합니다.

```sql
SELECT p.uit, s.line_type, v.is_domestic
     , COUNT(*) AS cnt
  FROM part_master p
  JOIN part_sourcing s ON s.part_no = p.part_no
  JOIN vendor v        ON v.vendor_code = s.vendor_code
 WHERE p.uit IN ('G', 'D')
 GROUP BY p.uit, s.line_type, v.is_domestic
 ORDER BY p.uit, s.line_type, v.is_domestic;
```

### 13-3. G와 D — 실행 결과 {keep}

```result
| uit | line_type | is_domestic | cnt |
| --- | --- | --- | --- |
| D | D | Y | 1 |
| D | I | N | 6 |
| G | D | N | 1 |
| G | D | Y | 39 |
| G | I | N | 1 |
```

- 대부분은 **G = 국내 업체 + `line_type` D**, **D = 해외 업체 + `line_type` I**로 짝이 맞습니다.
- 짝이 안 맞는 3행(D–D–Y, G–D–N, G–I–N)이 있습니다. 어떤 품번인지는 Day 2 5교시(5장)에서 찾습니다.

### 13-3. 한 문장으로 설명해 보기 {keep}

:::try 한 문장으로 설명해 보기
1. T와 P는 무엇이 같고 무엇이 다른가요?
2. G와 D는 무엇이 같고 무엇이 다른가요?
:::

:::answer 예시 답안
1. 둘 다 LG가 사내에서 조립하는 Make item입니다. T는 계획·표준시간·재고를 관리하고, P(팬텀)는 재고를 관리하지 않고 공정을 지나가기만 합니다.
2. 둘 다 협력사에서 사 오는 Buy item입니다. G는 국내 구매품, D는 수입 구매품입니다.
:::

### 13-4. Status — 품번의 라이프사이클 {keep}

```sql
SELECT * FROM code_status ORDER BY status_code;
```

```result
| status_code | status_name | active_flag | system_effect | meaning_kr |
| --- | --- | --- | --- | --- |
| 1 | Obsolete | Inactive | Order/Receiving/SVC disabled | 폐기 |
| 2 | Processing | Active | Add/Change available in BOM | 등록 처리중 |
| 3 | Approved | Active | Add/Change available in BOM | 승인(양산) |
| 4 | Service only | Active | Order/Service available | 서비스 전용 |
| 5 | To be obsolete | Inactive | Add/Change disabled in BOM | 폐기 예정 |
| 6 | MFG Discontinued | Inactive | Add/Change disabled in BOM | 생산 중단 |
```

- `active_flag`가 **Inactive(1·5·6)** 인 품번은 더 쓰지 않는 품번입니다(5·6은 BOM 추가·변경 불가, 1은 발주·입고·서비스 불가). 이런 부품이 BOM에 남아 있으면 품질 이슈입니다(Day 2 6교시).
- 품목 마스터에는 **1(폐기) 1개, 3(승인) 67개**만 있습니다(4단원 2-3).

### 13-5. UOM — 수량의 단위 {keep}

:::cols
```sql
SELECT p.uom, u.name, u.remark_kr
     , COUNT(*) AS part_cnt
  FROM part_master p
  JOIN code_uom u ON u.uom = p.uom
 GROUP BY p.uom, u.name, u.remark_kr
 ORDER BY part_cnt DESC, p.uom;
```

```result
| uom | name | remark_kr | part_cnt |
| --- | --- | --- | --- |
| EA | EACH | 개수 단위 표준 부품 | 60 |
| KG | KILOGRAM | 강판·수지 등 중량 단위 | 3 |
| SH | SHEET | 판재(Sheet Steel 등) | 2 |
| ST | SET | 제품 세트 | 2 |
| MZ | METER | 테이프·밴드 등 부자재 | 1 |
```
:::

BOM의 `qty_per`는 **자식 품번의 UOM 기준**입니다. 우레탄 발포액 `6.5`는 6.5개가 아니라 ==6.5kg==입니다. 단위가 다른 수량을 그냥 더하면 4단원 1-2의 통화 문제와 같은 일이 생깁니다.

### 13-6. Supply Type — BOM에서 자재가 공급되는 방식 {keep}

```sql
SELECT * FROM code_supply_type;
```

```result
| supply_type | meaning_en | meaning_kr |
| --- | --- | --- |
| Assembly Pull | Items with financial relationship with LG (LG orders, warehoused, or C-OSP) | LG가 발주·입고하거나 유상사급하는 품목 |
| Supplier | Items purchased or made directly by the vendor | 협력사가 직접 제작·구매하는 품목(LG 발주 없음) |
| Phantom | Items for separate process management, not stocked | 공정 관리용 가상 품목, 재고 없음 |
```

### 13-6. UIT와 Supply Type의 조합 {keep}

:::cols
```sql
SELECT p.uit, b.supply_type
     , COUNT(*) AS bom_rows
  FROM bom_structure b
  JOIN part_master p
    ON p.part_no = b.child_part_no
 GROUP BY p.uit, b.supply_type
 ORDER BY p.uit, b.supply_type;
```

```result
| uit | supply_type | bom_rows |
| --- | --- | --- |
| D | Assembly Pull | 6 |
| D | Supplier | 2 |
| G | Assembly Pull | 46 |
| G | Supplier | 8 |
| P | Assembly Pull | 1 |
| P | Phantom | 7 |
| S | Assembly Pull | 2 |
| T | Assembly Pull | 6 |
| X | Supplier | 4 |
```
:::

이 실습 데이터에서 점검하는 규칙은 세 가지입니다: **P → Phantom, T → Assembly Pull, X → Supplier**. 위 표에서 ==P | Assembly Pull | 1==이 규칙에 맞지 않는 1행입니다(Day 2 6교시에서 찾습니다).
