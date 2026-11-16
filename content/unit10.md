---
label: 10. DCL
title: 권한 관리
---

# 사용자 · GRANT · REVOKE · ROLE

:::goal
- `CREATE USER`와 `CREATE ROLE`의 차이(LOGIN)를 설명하고, 데이터베이스 접속 권한(`CONNECT`)을 주고 회수할 수 있습니다.
- 스키마 권한(`USAGE`) → 테이블 권한(`SELECT`·`INSERT`·`UPDATE`·`DELETE`) → 컬럼 권한 순서로 권한을 주고, 오류 메시지로 어디서 막혔는지 읽을 수 있습니다.
- `REVOKE`로 권한을 회수하고, `has_…_privilege` 함수와 `\dp`로 실제로 남은 권한을 확인할 수 있습니다.
- 권한을 ROLE로 묶어 부여하고, 직접 받은 권한과 롤로 물려받은 권한의 차이를 설명할 수 있습니다.
- 에이전트 계정(조회만)과 승인자 계정(필요한 컬럼 수정 + 이력 INSERT)을 최소 권한 원칙에 따라 나눌 수 있습니다.
:::

:::teacher 단원 구성 (60분)
- 기존 교안 `12. DCL.pptx` · `12. DCL.txt`의 **흐름(사용자 생성 → 접속 권한 → GRANT/REVOKE → ROLE → 스키마 → 객체 권한)** 을 따르되, 예제는 모두 BOM 실습 데이터(`bom` 스키마)로 바꿨습니다.
- `AI 융합·생산 SQL 수업 운영안 (32H)` 표에는 DCL 교시가 따로 없습니다. 6장(에이전트 계정 / 승인자 계정)이 Day 4 2교시 **Q13**(UIT 정정 + 이력 INSERT)과 5교시 **Python 연동**(접속 계정) 사이를 잇는 내용이므로, **Day 4 2교시 뒤 ~ 5교시 앞**에 두는 것을 제안합니다. 배치는 강사님이 정해 주세요.
- 교안의 모든 SQL과 실행 결과·오류 메시지는 `schema_postgres.sql`로 적재한 `bom_lab` DB에서 **새 계정으로 직접 접속해 실행한 결과**입니다. (검증 환경: PostgreSQL 16.15, 접속은 `localhost` 비밀번호 인증. 수업 PC는 PostgreSQL 18이므로 수업 전 한 번 더 실행해 보세요.)
- 각 장 끝 「확인 문제」는 HR 실습 데이터(`hr` 스키마)로 만들었습니다. 답안 결과는 `hr.departments`·`hr.employees` 두 테이블의 데이터로 직접 실행한 값입니다.
- ==관리자 명령은 `postgres` 창, 확인은 새 계정 창==에서 실행합니다. `postgres`는 슈퍼유저라 권한 검사를 받지 않으므로, `postgres` 창에서 테스트하면 오류가 나지 않아 실습이 되지 않습니다(1-3). 코드 위 캡션에 어느 창에서 실행하는지 적어 두었습니다.
- 이 단원은 1교시(60분) 분량입니다. 확인 문제와 8장 복습 문제는 시간에 따라 일부만 풀고, 나머지는 과제로 활용하세요.

| 시간 | 내용 | 해당 장 | 기존 교안 대응 |
| --- | --- | --- | --- |
| 0~7분 | SQL 분류 · DCL이 필요한 이유 · 슈퍼유저 | 1 | `12. DCL.pptx` 3~4 |
| 7~17분 | 사용자 만들기(LOGIN) · DB 접속 권한(CONNECT) | 2 | `12. DCL.pptx` 5~9 |
| 17~32분 | 스키마 권한(USAGE) · 객체 권한 · 권한 확인 · 컬럼 권한 | 3 | `12. DCL.pptx` 11~16 |
| 32~37분 | REVOKE | 4 | `12. DCL.pptx` 9 |
| 37~47분 | ROLE(권한 묶음) · 새 테이블 함정 | 5 | `12. DCL.pptx` 10 |
| 47~57분 | 실무: 에이전트 계정 / 승인자 계정 / 이력 보호 | 6 | — |
| 57~60분 | 계정 정리 · 복습 문제 안내 | 7~8 | — |
:::

## 1. DCL — 누가 무엇을 할 수 있는가

### 1-1. SQL 문장의 종류 {keep}

| 분류 | 이름 | 대표 명령 | 이 과정에서 |
| --- | --- | --- | --- |
| 조회 | Query | `SELECT` | Day 1~3 |
| DDL | 데이터 정의어 | `CREATE`, `ALTER`, `DROP` | Day 4 3교시 |
| DML | 데이터 조작어 | `INSERT`, `UPDATE`, `DELETE` | Day 4 1교시 |
| TCL | 트랜잭션 제어어 | `BEGIN`, `COMMIT`, `ROLLBACK` | Day 4 2교시 |
| **DCL** | **데이터 제어어** | **`GRANT`, `REVOKE`** | **이번 단원** |

**DCL(Data Control Language)** 은 **누가 어떤 데이터에 무엇을 할 수 있는지**를 정하는 명령입니다.

### 1-1. 이번 단원에서 배우는 DCL {keep}

```icons DCL 명령어
key-round | GRANT | 권한 **부여** (2~3장) | rose
ban | REVOKE | 권한 **회수** (4장) | hot
users | ROLE | 권한 **묶음** — 여러 권한을 한 이름으로 묶어 한꺼번에 부여 (5장) | plum
```

### 1-2. 왜 필요할까요? {keep}

Day 4에서 만드는 구조는 「**에이전트가 조회·판단 → 사람이 승인 → 기록**」입니다(운영안 Day 4 목표). 이때 에이전트가 `postgres`(관리자) 계정으로 접속한다면 어떻게 될까요?

- 판단만 해야 하는 에이전트가 `part_master`의 UIT를 **직접 바꿀 수 있습니다.**
- 실수 한 번으로 `uit_change_history`(변경 이력)를 **지우거나 덮어쓸 수 있습니다.**

==계정마다 「하는 일에 꼭 필요한 권한만」 주는 것==을 **최소 권한 원칙**이라고 합니다. DCL은 이 원칙을 DB에서 지키는 방법입니다. 6장에서 에이전트 계정과 승인자 계정을 직접 나눠 봅니다.

### 1-3. 지금 나는 누구로 접속해 있나요? {keep}

```sql postgres 창
SELECT current_user;
```

```result
| current_user |
| --- |
| postgres |
```

PostgreSQL에서는 사용자와 권한 묶음을 모두 **롤(role)** 이라고 부릅니다. 지금 있는 롤을 조회해 봅니다.

```sql postgres 창
SELECT rolname, rolsuper, rolcanlogin
  FROM pg_roles
 WHERE rolname NOT LIKE 'pg\_%'
 ORDER BY rolname;
```

```result
| rolname | rolsuper | rolcanlogin |
| --- | --- | --- |
| postgres | t | t |
```

### 1-3. 결과 읽기 — 슈퍼유저 {keep}

- `pg_roles`는 롤 목록을 보여 주는 시스템 뷰입니다. `pg_`로 시작하는 롤은 PostgreSQL이 미리 만들어 둔 롤이라 뺐습니다(5-4).
- `rolsuper = t`: `postgres`는 **슈퍼유저**입니다. `rolcanlogin = t`: 접속할 수 있는 롤입니다.
- psql에서는 `t`/`f`, pgAdmin에서는 `true`/`false`로 보입니다.

:::error 슈퍼유저로는 권한 실습이 안 됩니다
슈퍼유저는 접속 권한을 제외한 **모든 권한 검사를 건너뜁니다.** `postgres` 창에서 아무리 테스트해도 권한 오류가 나지 않습니다. 이 단원에서는 ==권한을 주는 명령은 `postgres` 창==에서, ==결과 확인은 새로 만든 계정 창==에서 실행합니다.
:::

## 2. 사용자 만들기와 접속 권한

### 2-1. CREATE ROLE — 롤 만들기 {keep}

```sql postgres 창
CREATE ROLE dcl_test PASSWORD '1234';
```

```result
CREATE ROLE
```

```sql postgres 창
SELECT rolname, rolsuper, rolcanlogin
  FROM pg_roles
 WHERE rolname = 'dcl_test';
```

```result
| rolname | rolsuper | rolcanlogin |
| --- | --- | --- |
| dcl_test | f | f |
```

### 2-1. 새 계정으로 접속해 보기 {keep}

**새 SQL Shell (psql) 창**을 열고 `Database`에 `bom_lab`, `Username`에 `dcl_test`, 비밀번호 `1234`를 입력해 접속해 봅니다. (2단원 5장 접속 화면과 같고, 이름만 바꿔 넣습니다.)

```error
psql: error: connection to server at "localhost" (127.0.0.1), port 5432 failed: FATAL:  role "dcl_test" is not permitted to log in
```

비밀번호까지 정했는데 접속이 안 됩니다. `rolcanlogin`이 `f`이기 때문입니다. ==`CREATE ROLE`로 만든 롤은 기본이 「접속 불가(NOLOGIN)」== 입니다.

### 2-2. LOGIN 속성 주기 {keep}

```sql postgres 창
ALTER ROLE dcl_test LOGIN;
```

```result
ALTER ROLE
```

```sql postgres 창
SELECT rolname, rolsuper, rolcanlogin
  FROM pg_roles
 WHERE rolname = 'dcl_test';
```

```result
| rolname | rolsuper | rolcanlogin |
| --- | --- | --- |
| dcl_test | f | t |
```

다시 `dcl_test`로 접속하면 성공합니다.

```sql dcl_test 창
SELECT current_user;
```

```result
| current_user |
| --- |
| dcl_test |
```

### 2-2. CREATE USER = CREATE ROLE + LOGIN {keep}

| 명령 | 기본 속성 | 쓰임 |
| --- | --- | --- |
| `CREATE USER 이름 PASSWORD '…';` | **LOGIN** (접속 가능) | 사람·프로그램이 접속할 **계정** |
| `CREATE ROLE 이름;` | **NOLOGIN** (접속 불가) | 권한을 묶어 두는 **권한 묶음**(5장) |
| `CREATE ROLE 이름 LOGIN PASSWORD '…';` | LOGIN | `CREATE USER`와 같음 |

> 같은 이름으로 다시 만들면 오류가 납니다. 롤은 DB가 아니라 **서버 전체**에 하나씩 있습니다.

```error
ERROR:  role "dcl_test" already exists
```

### 2-3. CONNECT — 데이터베이스 접속 권한 {keep}

`dcl_test`는 아무 권한도 받지 않았는데 `bom_lab`에 접속했습니다. PostgreSQL은 데이터베이스를 만들 때 **모든 롤(PUBLIC)에게 접속(CONNECT) 권한을 기본으로** 주기 때문입니다.

```sql postgres 창 — 데이터베이스 권한 확인
SELECT datname, datacl
  FROM pg_database
 WHERE datname = 'bom_lab';
```

```result
| datname | datacl |
| --- | --- |
| bom_lab | NULL |
```

`datacl`이 NULL이면 **기본 권한 그대로**라는 뜻입니다.

### 2-3. PUBLIC의 접속 권한 회수 {keep}

PUBLIC의 기본 접속 권한을 회수해, 허락받은 계정만 접속하게 바꿉니다.

```sql postgres 창
REVOKE CONNECT ON DATABASE bom_lab FROM PUBLIC;
```

```result
REVOKE
```

```sql postgres 창
SELECT datname, datacl
  FROM pg_database
 WHERE datname = 'bom_lab';
```

```result
| datname | datacl |
| --- | --- |
| bom_lab | {=T/postgres,postgres=CTc/postgres} |
```

이제 `dcl_test`로 새로 접속하면 거절됩니다.

```error
psql: error: connection to server at "localhost" (127.0.0.1), port 5432 failed: FATAL:  permission denied for database "bom_lab"
DETAIL:  User does not have CONNECT privilege.
```

### 2-3. 한 계정에만 접속 권한 주기 {keep}

```sql postgres 창
GRANT CONNECT ON DATABASE bom_lab TO dcl_test;
```

```result
GRANT
```

```sql postgres 창
SELECT datname, datacl
  FROM pg_database
 WHERE datname = 'bom_lab';
```

```result
| datname | datacl |
| --- | --- |
| bom_lab | {=T/postgres,postgres=CTc/postgres,dcl_test=c/postgres} |
```

- `dcl_test=c/postgres`는 「`dcl_test`가 `c`(CONNECT) 권한을 `postgres`에게서 받았다」는 뜻입니다. 이제 다시 접속됩니다.
- 맨 앞의 `=T/postgres`처럼 **이름이 비어 있으면 PUBLIC**입니다(`T` = TEMPORARY, 임시 테이블 생성).

### 2-3. 두 접속 오류를 구분하세요 {keep}

:::error 두 접속 오류를 구분하세요
| 오류 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `role "…" is not permitted to log in` | 롤에 **LOGIN 속성**이 없음 | `ALTER ROLE 이름 LOGIN;` |
| `permission denied for database "…"` | 그 DB의 **CONNECT 권한**이 없음 | `GRANT CONNECT ON DATABASE DB이름 TO 이름;` |
:::

- 오류 메시지 앞부분의 주소(`"localhost" (127.0.0.1)`)는 PC 설정에 따라 다르게 보일 수 있습니다. `FATAL:` 뒤의 내용을 보세요.
- 열려 있는 psql 창에서 `\c bom_lab dcl_test`로 계정을 바꿔 접속할 수도 있습니다(필요하면 비밀번호를 묻습니다).

### 2-4. 확인 문제 — HR 데이터 {keep}

> 이 단원의 확인 문제는 `postgres` 창(관리자)과 새 계정 창(확인)을 오가며 풉니다. 2-3까지 실행해 `bom_lab`의 PUBLIC 접속 권한이 회수된 상태라고 가정합니다.

:::try
**[복습]** 인사 데이터 조회용 계정 `hr_viewer`(비밀번호 `1234`)를 **한 문장으로** 만들고, `bom_lab`에 접속할 수 있게 하세요. `hr_viewer` 창에서 `SELECT current_user;`로 확인합니다.

**[응용]** 동료가 `hr_viewer`로 접속하다가 아래 두 오류를 차례로 만났습니다. 각각의 원인과 관리자가 실행할 해결 명령을 쓰세요.

```error
FATAL:  role "hr_viewer" is not permitted to log in
```

```error
FATAL:  permission denied for database "bom_lab"
DETAIL:  User does not have CONNECT privilege.
```
:::

### 2-4. 확인 문제 답 {keep}

:::answer [복습] 예시 답안
```sql postgres 창
CREATE USER hr_viewer PASSWORD '1234';
GRANT CONNECT ON DATABASE bom_lab TO hr_viewer;
```

```sql hr_viewer 창
SELECT current_user;
```

```result
| current_user |
| --- |
| hr_viewer |
```

`CREATE ROLE`로 만들었다면 `LOGIN`을 함께 적어야 합니다(`CREATE ROLE hr_viewer LOGIN PASSWORD '1234';`).
:::

:::answer [응용] 예시 답안
- 첫 번째: `CREATE ROLE`로 만들어 **LOGIN 속성이 없음** → `ALTER ROLE hr_viewer LOGIN;`
- 두 번째: LOGIN은 되지만 `bom_lab`의 **CONNECT 권한이 없음**(PUBLIC 권한을 회수했기 때문) → `GRANT CONNECT ON DATABASE bom_lab TO hr_viewer;`

접속은 「① 롤이 로그인할 수 있는가 → ② 그 DB에 들어갈 수 있는가」 두 단계로 검사됩니다.
:::

## 3. 스키마 권한과 객체 권한

### 3-1. USAGE — 스키마에 들어갈 권한 {keep}

`dcl_test`로 접속은 되었습니다. 이제 부품 마스터를 조회해 봅니다.

```sql dcl_test 창
SELECT part_no, description_kr, uit
  FROM bom.part_master
 WHERE part_no = 'EMT73633001';
```

```error
ERROR:  permission denied for schema bom
LINE 1: SELECT part_no, description_kr, uit FROM bom.part_master WHE...
                                                 ^
```

테이블보다 먼저 **스키마(`bom`)** 에서 막혔습니다. 2단원 6-4에서 스키마는 **DB 안의 폴더**라고 했습니다. 폴더에 들어갈 권한이 없으면 안의 파일(테이블)을 볼 수 없습니다.

### 3-1. search_path를 걸어도 「테이블이 없다」고 나옵니다 {keep}

:::error search_path를 걸어도 「테이블이 없다」고 나옵니다
스키마 권한이 없는 상태에서 `SET search_path TO bom;` 후 테이블 이름만 쓰면, 오류 메시지가 달라집니다.

```sql dcl_test 창
SET search_path TO bom;

SELECT part_no, description_kr, uit
  FROM part_master
 WHERE part_no = 'EMT73633001';
```

```error
ERROR:  relation "part_master" does not exist
LINE 1: SELECT part_no, description_kr, uit FROM part_master WHERE p...
                                                 ^
```

들어갈 수 없는 스키마는 테이블을 찾을 때 **건너뛰기** 때문입니다. 2단원 7-3의 「search_path를 안 걸었을 때」와 같은 메시지라서 헷갈리기 쉽습니다. ==새 계정에서 `does not exist`가 나오면 스키마 권한부터 의심==하세요.
:::

### 3-1. 스키마 권한 주기 {keep}

```sql postgres 창
GRANT USAGE ON SCHEMA bom TO dcl_test;
```

```result
GRANT
```

```sql dcl_test 창
SET search_path TO bom;

SELECT part_no, description_kr, uit
  FROM part_master
 WHERE part_no = 'EMT73633001';
```

```error
ERROR:  permission denied for table part_master
```

이번에는 **테이블**에서 막혔습니다. 폴더에는 들어갔지만 파일을 열 권한은 따로 받아야 합니다.

### 3-2. 객체 권한 — GRANT 권한 ON 객체 TO 사용자 {keep}

```text GRANT의 모양
GRANT 권한  ON 스키마.객체  TO 사용자;
```

```sql postgres 창
GRANT SELECT ON bom.part_master TO dcl_test;
```

```result
GRANT
```

```sql dcl_test 창
SET search_path TO bom;

SELECT part_no, description_kr, uit
  FROM part_master
 WHERE part_no = 'EMT73633001';
```

```result
| part_no | description_kr | uit |
| --- | --- | --- |
| EMT73633001 | 스테이터 | G |
```

조회가 됩니다. 하지만 **받은 권한은 딱 `part_master`의 `SELECT` 하나**입니다.

### 3-2. 받지 않은 권한은 모두 막힙니다 {keep}

```sql dcl_test 창
UPDATE part_master
   SET uit = 'D'
 WHERE part_no = 'EMT73633001';
```

```error
ERROR:  permission denied for table part_master
```

```sql dcl_test 창
SELECT vendor_code, vendor_name
  FROM vendor;
```

```error
ERROR:  permission denied for table vendor
```

```sql dcl_test 창
CREATE TABLE my_note (memo TEXT);
```

```error
ERROR:  permission denied for schema bom
LINE 1: CREATE TABLE my_note (memo TEXT);
                     ^
```

### 3-2. 무엇이 되고 무엇이 막혔나 {keep}

| 해 본 것 | 결과 | 이유 |
| --- | --- | --- |
| `part_master` 조회 | 성공 | `SELECT` 권한을 받음 |
| `part_master` 수정 | 실패 | `UPDATE` 권한은 안 받음 |
| `vendor` 조회 | 실패 | 권한은 **테이블마다 따로** 받음 |
| `bom`에 테이블 만들기 | 실패 | 스키마의 `USAGE`는 「들어가기」뿐, 만들려면 `CREATE` 권한이 필요 |

> `public` 스키마에 테이블을 만드는 것도 막혀 있습니다(`permission denied for schema public`). PostgreSQL 15부터 모든 사용자(PUBLIC)의 `public` 스키마 `CREATE` 권한이 기본에서 빠졌기 때문입니다.

### 3-3. 객체 권한의 종류 {keep}

테이블에 줄 수 있는 권한과, 권한 목록에 보이는 **약어**입니다.

| 권한 | 약어 | 할 수 있는 일 |
| --- | --- | --- |
| `SELECT` | `r` (read) | 조회 |
| `INSERT` | `a` (append) | 행 추가 |
| `UPDATE` | `w` (write) | 수정 |
| `DELETE` | `d` | 행 삭제 |
| `TRUNCATE` | `D` | 전체 행 비우기 |
| `REFERENCES` | `x` | 이 테이블을 참조하는 FK 만들기 |
| `TRIGGER` | `t` | 트리거 만들기 |
| `ALL` (또는 `ALL PRIVILEGES`) | — | 위 권한 전부 |

### 3-3. 데이터베이스·스키마에 주는 권한 {keep}

| 대상 | 권한 | 약어 | 뜻 |
| --- | --- | --- | --- |
| 데이터베이스 | `CONNECT` | `c` | 접속 |
| 데이터베이스 | `TEMPORARY` | `T` | 임시 테이블 만들기 |
| 데이터베이스·스키마 | `CREATE` | `C` | DB: 스키마 만들기 / 스키마: 테이블 등 만들기 |
| 스키마 | `USAGE` | `U` | 스키마 안의 객체에 접근하기 |

### 3-4. 권한 확인하기 ① psql `\dp` {keep}

```psql postgres 창
\dp bom.part_master
```

```screen
                                    Access privileges
 Schema |    Name     | Type  |     Access privileges     | Column privileges | Policies
--------+-------------+-------+---------------------------+-------------------+----------
 bom    | part_master | table | postgres=arwdDxt/postgres+|                   |
        |             |       | dcl_test=r/postgres       |                   |
(1 row)
```

- `postgres=arwdDxt/postgres`: 테이블 주인(owner)인 `postgres`는 **모든 권한**(`arwdDxt`)을 가집니다. 테이블을 만든 사람이 주인이 됩니다.
- `dcl_test=r/postgres`: `dcl_test`는 `r`(SELECT)만 받았습니다.

### 3-4. 권한 확인하기 ② 함수 · ③ information_schema {keep}

**② 권한 확인 함수** — 결과가 `t`/`f`라 쿼리 안에서 쓰기 좋습니다.

```sql postgres 창
SELECT has_table_privilege('dcl_test', 'bom.part_master', 'SELECT') AS can_select
     , has_table_privilege('dcl_test', 'bom.part_master', 'UPDATE') AS can_update;
```

```result
| can_select | can_update |
| --- | --- |
| t | f |
```

**③ information_schema** — 받은 권한을 표로 봅니다.

```sql postgres 창
SELECT grantee, table_schema, table_name, privilege_type
  FROM information_schema.role_table_grants
 WHERE grantee = 'dcl_test';
```

```result
| grantee | table_schema | table_name | privilege_type |
| --- | --- | --- | --- |
| dcl_test | bom | part_master | SELECT |
```

### 3-5. 컬럼 권한 — 꼭 필요한 컬럼만 ⭐ {keep}

**질문:** `dcl_test`가 UIT 정정 업무를 맡았습니다. `part_master`에서 **UIT만** 바꿀 수 있게 하려면?

테이블 전체에 `UPDATE`를 주면 품명·상태 코드까지 바꿀 수 있습니다. 권한 뒤에 **(컬럼)** 을 적으면 그 컬럼만 허용합니다.

```sql postgres 창
GRANT UPDATE (uit) ON bom.part_master TO dcl_test;
```

```result
GRANT
```

```psql postgres 창
\dp bom.part_master
```

```screen
                                      Access privileges
 Schema |    Name     | Type  |     Access privileges     |   Column privileges   | Policies
--------+-------------+-------+---------------------------+-----------------------+----------
 bom    | part_master | table | postgres=arwdDxt/postgres+| uit:                 +|
        |             |       | dcl_test=r/postgres       |   dcl_test=w/postgres |
(1 row)
```

`Column privileges` 칸에 `uit: dcl_test=w`(UIT 컬럼 UPDATE)가 생겼습니다.

### 3-5. UIT는 바꿀 수 있습니다 {keep}

실습 데이터가 바뀌지 않도록 트랜잭션 안에서 해 보고 되돌립니다(Day 4 2교시).

```sql dcl_test 창
SET search_path TO bom;
BEGIN;

UPDATE part_master
   SET uit = 'D'
 WHERE part_no = 'EMT73633001';
```

```result
UPDATE 1
```

```sql dcl_test 창
SELECT part_no, uit
  FROM part_master
 WHERE part_no = 'EMT73633001';
```

```result
| part_no | uit |
| --- | --- |
| EMT73633001 | D |
```

```sql dcl_test 창
ROLLBACK;
```

```result
ROLLBACK
```

### 3-5. UIT가 아닌 컬럼은 바꿀 수 없습니다 {keep}

```sql dcl_test 창
UPDATE part_master
   SET description_kr = '스테이터(수입)'
 WHERE part_no = 'EMT73633001';
```

```error
ERROR:  permission denied for table part_master
```

```sql dcl_test 창
SELECT part_no, uit
  FROM part_master
 WHERE part_no = 'EMT73633001';
```

```result
| part_no | uit |
| --- | --- |
| EMT73633001 | G |
```

`ROLLBACK`으로 UIT는 원래 값(G)으로 돌아왔습니다.

### 3-5. 컬럼 권한 확인 {keep}

```sql postgres 창
SELECT has_column_privilege('dcl_test', 'bom.part_master', 'uit', 'UPDATE')            AS uit_upd
     , has_column_privilege('dcl_test', 'bom.part_master', 'description_kr', 'UPDATE') AS desc_upd;
```

```result
| uit_upd | desc_upd |
| --- | --- |
| t | f |
```

> `UPDATE … WHERE part_no = …`가 실행되려면 `uit` **UPDATE 권한**과 함께, `WHERE`에서 읽는 `part_no`의 **SELECT 권한**도 필요합니다. 위 실습에서는 3-2에서 테이블 전체 SELECT를 받아 두었기 때문에 실행되었습니다.

### 3-6. ALL TABLES IN SCHEMA — 스키마의 모든 테이블에 한 번에 {keep}

테이블이 17개인데 하나씩 `GRANT`하기는 번거롭습니다.

```sql postgres 창
GRANT SELECT ON ALL TABLES IN SCHEMA bom TO dcl_test;
```

```result
GRANT
```

```sql postgres 창
SELECT COUNT(*) AS select_ok
  FROM information_schema.role_table_grants
 WHERE grantee      = 'dcl_test'
   AND table_schema = 'bom'
   AND privilege_type = 'SELECT';
```

```result
| select_ok |
| --- |
| 17 |
```

### 3-6. 이제 vendor도 조회됩니다 {keep}

```sql dcl_test 창
SELECT vendor_code, vendor_name
  FROM bom.vendor
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

> `ALL TABLES IN SCHEMA`는 **명령을 실행한 순간 있는 테이블**에만 적용됩니다. 나중에 만든 테이블은 따로 다뤄야 합니다(5-3).

### 3-7. 확인 문제 — HR 데이터 {keep}

> `hr_viewer`는 2-4에서 만든 계정입니다.

:::try
**[복습]** `hr_viewer`가 `hr.departments`를 조회할 수 있게 권한을 주고, `hr_viewer` 창에서 부서 수를 세어 보세요. 권한 명령은 몇 개가 필요한가요?

**[응용]** 인사 담당이 아닌 `hr_viewer`에게 `hr.employees`의 급여(`salary`)와 커미션(`commission_pct`)은 **보여 주지 않고**, 나머지 9개 컬럼만 조회하게 하려고 합니다.
① 권한 명령을 쓰세요.
② `hr_viewer` 창에서 아래 세 쿼리를 실행하면 각각 어떻게 되나요?

```sql hr_viewer 창
SELECT * FROM hr.employees;

SELECT employee_id, first_name, last_name, job_id
  FROM hr.employees
 WHERE department_id = 60
 ORDER BY employee_id;

SELECT first_name
  FROM hr.employees
 WHERE salary > 10000;
```
:::

### 3-7. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안
명령 2개 — 스키마 `USAGE` + 테이블 `SELECT`

```sql postgres 창
GRANT USAGE ON SCHEMA hr TO hr_viewer;
GRANT SELECT ON hr.departments TO hr_viewer;
```

```sql hr_viewer 창
SELECT COUNT(*) AS dept_cnt
  FROM hr.departments;
```

```result
| dept_cnt |
| --- |
| 27 |
```

`USAGE` 없이 `SELECT`만 주면 `permission denied for schema hr`가 납니다.
:::

### 3-7. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
① 컬럼 목록을 적어 `SELECT` 권한을 줍니다.

```sql postgres 창
GRANT SELECT (employee_id, first_name, last_name, email, phone_number,
              hire_date, job_id, manager_id, department_id)
   ON hr.employees TO hr_viewer;
```

② 첫 번째 — `*`에는 권한이 없는 `salary`·`commission_pct`가 포함되므로 오류입니다.

```error
ERROR:  permission denied for table employees
```

두 번째 — 허용된 컬럼만 썼으므로 5행이 나옵니다.

```result
| employee_id | first_name | last_name | job_id |
| --- | --- | --- | --- |
| 103 | Alexander | Hunold | IT_PROG |
| 104 | Bruce | Ernst | IT_PROG |
| 105 | David | Austin | IT_PROG |
| 106 | Valli | Pataballa | IT_PROG |
| 107 | Diana | Lorentz | IT_PROG |
```

세 번째 — `SELECT` 절에는 `first_name`만 있지만 `WHERE`에서 `salary`를 **읽기** 때문에 오류입니다.

```error
ERROR:  permission denied for table employees
```

==보지 못하게 한 컬럼은 조건(WHERE)으로도 쓸 수 없습니다.== 조건에 쓸 수 있으면 「급여가 10000보다 큰 사람」을 알아낼 수 있기 때문입니다.
:::

## 4. REVOKE — 권한 회수

### 4-1. REVOKE 권한 ON 객체 FROM 사용자 {keep}

```text REVOKE의 모양
REVOKE 권한  ON 스키마.객체  FROM 사용자;
```

`GRANT … TO`와 모양이 같고, `TO` 대신 **`FROM`** 을 씁니다. 3장에서 준 테이블 권한을 회수합니다.

```sql postgres 창
REVOKE UPDATE (uit) ON bom.part_master FROM dcl_test;
```

```result
REVOKE
```

```sql postgres 창
REVOKE SELECT ON ALL TABLES IN SCHEMA bom FROM dcl_test;
```

```result
REVOKE
```

### 4-1. 회수 결과 확인 {keep}

```sql postgres 창
SELECT COUNT(*) AS select_ok
  FROM information_schema.role_table_grants
 WHERE grantee      = 'dcl_test'
   AND table_schema = 'bom';
```

```result
| select_ok |
| --- |
| 0 |
```

```psql postgres 창
\dp bom.part_master
```

```screen
                                    Access privileges
 Schema |    Name     | Type  |     Access privileges     | Column privileges | Policies
--------+-------------+-------+---------------------------+-------------------+----------
 bom    | part_master | table | postgres=arwdDxt/postgres |                   |
(1 row)
```

### 4-1. 두 번 준 권한도 회수는 한 번 {keep}

```sql dcl_test 창
SELECT COUNT(*)
  FROM bom.part_master;
```

```error
ERROR:  permission denied for table part_master
```

`part_master`의 SELECT는 3-2에서 따로 한 번, 3-6에서 `ALL TABLES`로 한 번 더 주었지만, 회수는 한 번으로 끝났습니다. 같은 권한을 여러 번 주어도 **권한은 하나**로 기록됩니다.

### 4-2. 없는 권한을 회수해도 오류가 나지 않습니다 {keep}

```sql postgres 창
REVOKE DELETE ON bom.part_master FROM dcl_test;
```

```result
REVOKE
```

`dcl_test`는 처음부터 `DELETE` 권한이 없었지만 `REVOKE`가 그대로 끝났습니다. ==`REVOKE`가 성공했다고 권한이 없어졌다고 단정하지 말고, 3-4의 방법으로 확인==하세요. 5-2에서 「회수했는데도 남아 있는」 경우를 봅니다.

## 5. ROLE — 권한 묶음

### 5-1. 롤로 권한을 묶는 이유 {keep}

생산관리팀 10명에게 「`bom` 전체 조회」 권한을 줘야 한다면, 사람마다 `USAGE` + `SELECT ON ALL TABLES`를 반복해야 합니다. 권한을 **롤 하나에 묶어 두고 그 롤을 부여**하면 한 번에 끝납니다.

```flow 사용자 ← 롤(권한 묶음) ← 권한들
key-round | 권한들 | USAGE · SELECT | ivory
users | 롤 | bom_reader | plum
user | 사용자 | dcl_test | hot
```

### 5-1. 롤 만들고 권한 묶기 {keep}

① 롤 만들기 (`CREATE ROLE`이므로 접속 불가 롤)

```sql postgres 창
CREATE ROLE bom_reader;
```

② 롤에 권한 주기

```sql postgres 창
GRANT USAGE ON SCHEMA bom TO bom_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA bom TO bom_reader;
```

③ 사용자에게 롤 주기 — `ON 객체`가 없습니다.

```sql postgres 창
GRANT bom_reader TO dcl_test;
```

```result
GRANT ROLE
```

### 5-1. 롤과 구성원 확인 {keep}

```sql postgres 창
SELECT rolname, rolcanlogin
  FROM pg_roles
 WHERE rolname IN ('bom_reader', 'dcl_test')
 ORDER BY rolname;
```

```result
| rolname | rolcanlogin |
| --- | --- |
| bom_reader | f |
| dcl_test | t |
```

누가 어느 롤의 구성원인지는 `pg_auth_members`에서 봅니다.

```sql postgres 창
SELECT r.rolname AS role_name
     , m.rolname AS member_name
  FROM pg_auth_members a
  JOIN pg_roles r ON r.oid = a.roleid
  JOIN pg_roles m ON m.oid = a.member
 WHERE r.rolname = 'bom_reader';
```

```result
| role_name | member_name |
| --- | --- |
| bom_reader | dcl_test |
```

### 5-1. psql `\du` · 롤로 다시 조회 {keep}

```psql postgres 창
\du
```

```screen
                              List of roles
 Role name  |                         Attributes
------------+------------------------------------------------------------
 bom_reader | Cannot login
 dcl_test   |
 postgres   | Superuser, Create role, Create DB, Replication, Bypass RLS
```

4장에서 테이블 권한을 모두 회수했지만, 롤을 통해 다시 조회됩니다.

```sql dcl_test 창
SELECT model_part_no, SUM(plan_qty) AS total_plan
  FROM bom.production_plan
 GROUP BY model_part_no
 ORDER BY model_part_no;
```

```result
| model_part_no | total_plan |
| --- | --- |
| TRF38316001 | 3460 |
| TWM61868701 | 4520 |
```

### 5-1. 권한을 주는 세 가지 모양 {keep}

| 권한을 주는 방법 | 문장 모양 |
| --- | --- |
| 사용자에게 직접 | `GRANT SELECT ON 테이블 TO 사용자;` |
| 롤에 주기 | `GRANT SELECT ON 테이블 TO 롤;` |
| 사용자에게 롤 주기 | `GRANT 롤 TO 사용자;` (ON 없음) |

### 5-2. 직접 회수해도 롤로 받은 권한은 남습니다 {keep}

`dcl_test`는 3-1에서 `bom` 스키마 `USAGE`를 **직접** 받았고, 5-1에서 `bom_reader` 롤로 **한 번 더** 받았습니다. 직접 받은 것만 회수해 봅니다.

```sql postgres 창
REVOKE USAGE ON SCHEMA bom FROM dcl_test;
```

```result
REVOKE
```

```sql postgres 창
SELECT has_schema_privilege('dcl_test', 'bom', 'USAGE') AS usage_ok;
```

```result
| usage_ok |
| --- |
| t |
```

여전히 `t`입니다. `bom_reader`의 구성원이라 **롤의 권한을 물려받기** 때문입니다. 권한을 완전히 막으려면 ==직접 준 권한과 롤 멤버십을 모두 확인==해야 합니다(`REVOKE bom_reader FROM dcl_test;`).

### 5-3. 나중에 만든 테이블에는 권한이 없습니다 ⭐ {keep}

Day 4 1교시처럼 관리자가 연습용 사본 테이블을 새로 만들었습니다.

```sql postgres 창
CREATE TABLE bom.part_master_copy AS
SELECT * FROM bom.part_master;
```

```result
SELECT 68
```

```sql dcl_test 창
SELECT COUNT(*) AS cnt
  FROM bom.part_master_copy;
```

```error
ERROR:  permission denied for table part_master_copy
```

`bom_reader`에 준 `SELECT ON ALL TABLES IN SCHEMA bom`은 **5-1을 실행한 순간의 17개 테이블**에만 적용되었기 때문입니다.

### 5-3. ALTER DEFAULT PRIVILEGES — 앞으로 만들 테이블에도 {keep}

앞으로 만들 테이블에도 권한이 자동으로 붙게 하려면 **기본 권한**을 정해 둡니다.

```sql postgres 창
ALTER DEFAULT PRIVILEGES IN SCHEMA bom
GRANT SELECT ON TABLES TO bom_reader;
```

```result
ALTER DEFAULT PRIVILEGES
```

```sql postgres 창
CREATE TABLE bom.inventory_copy AS
SELECT * FROM bom.inventory;
```

```result
SELECT 53
```

```sql postgres 창
SELECT has_table_privilege('bom_reader', 'bom.part_master_copy', 'SELECT') AS part_copy
     , has_table_privilege('bom_reader', 'bom.inventory_copy',   'SELECT') AS inv_copy;
```

```result
| part_copy | inv_copy |
| --- | --- |
| f | t |
```

### 5-3. 기존 테이블에는 소급되지 않습니다 {keep}

| 테이블 | 만든 시점 | `bom_reader` 조회 |
| --- | --- | --- |
| `part_master_copy` | 기본 권한 설정 **전** | 불가 (기존 테이블에는 소급되지 않음) |
| `inventory_copy` | 기본 권한 설정 **후** | 가능 |

```psql postgres 창
\ddp
```

```screen
             Default access privileges
  Owner   | Schema | Type  |   Access privileges
----------+--------+-------+-----------------------
 postgres | bom    | table | bom_reader=r/postgres
(1 row)
```

- `ALTER DEFAULT PRIVILEGES`는 ==명령을 실행한 롤(여기서는 `postgres`)이 앞으로 만드는 객체==에 적용됩니다. 다른 롤이 만드는 테이블에도 적용하려면 `FOR ROLE 그롤`을 붙입니다.
- 이미 있는 `part_master_copy`는 `GRANT SELECT ON bom.part_master_copy TO bom_reader;`로 따로 줍니다.

실습용 사본은 지웁니다.

```sql postgres 창
DROP TABLE bom.part_master_copy, bom.inventory_copy;
```

### 5-4. 참고 — 미리 정의된 롤 {keep}

PostgreSQL에는 `pg_`로 시작하는 롤이 미리 만들어져 있습니다(1-3에서 뺀 롤들). 그중 두 가지입니다.

```sql postgres 창
SELECT rolname
  FROM pg_roles
 WHERE rolname IN ('pg_read_all_data', 'pg_write_all_data')
 ORDER BY rolname;
```

```result
| rolname |
| --- |
| pg_read_all_data |
| pg_write_all_data |
```

| 롤 | 뜻 |
| --- | --- |
| `pg_read_all_data` | 모든 테이블·뷰·시퀀스에 `SELECT`, 모든 스키마에 `USAGE`가 있는 것처럼 동작 |
| `pg_write_all_data` | 모든 테이블·뷰·시퀀스에 `INSERT`·`UPDATE`·`DELETE`, 모든 스키마에 `USAGE`가 있는 것처럼 동작 |

편리하지만 **DB 전체**에 적용됩니다. 이 수업처럼 `bom`과 `hr`을 나눠 관리하려면 5-1처럼 직접 만든 롤이 더 알맞습니다.

### 5-5. 확인 문제 — HR 데이터 {keep}

:::try
**[복습]** `hr` 스키마 전체 조회용 롤 `hr_read`를 만들어 `hr_viewer`에게 부여하세요. 그다음 `hr_viewer` 창에서 60번 부서 직원의 이름과 급여를 급여가 높은 순(같으면 이름 순)으로 출력합니다. (3-7에서는 급여를 볼 수 없었습니다.)

**[응용]** 관리자가 `hr_viewer`의 부서 조회를 막으려고 아래 명령을 실행했습니다.

```sql postgres 창
REVOKE SELECT ON hr.departments FROM hr_viewer;
```

그런데 `hr_viewer`는 여전히 `hr.departments`를 조회할 수 있습니다. 이유를 설명하고, 부서 조회를 실제로 막는 명령을 쓰세요. 그 명령 뒤에도 `hr_viewer`가 `employees`의 `first_name`은 볼 수 있는 이유도 설명하세요.
:::

### 5-5. 확인 문제 답 — 복습 {keep}

:::answer [복습] 예시 답안 (5행)
```sql postgres 창
CREATE ROLE hr_read;
GRANT USAGE ON SCHEMA hr TO hr_read;
GRANT SELECT ON ALL TABLES IN SCHEMA hr TO hr_read;
GRANT hr_read TO hr_viewer;
```

```sql hr_viewer 창
SELECT first_name, salary
  FROM hr.employees
 WHERE department_id = 60
 ORDER BY salary DESC, first_name;
```

```result
| first_name | salary |
| --- | --- |
| Alexander | 9000.00 |
| Bruce | 6000.00 |
| David | 4800.00 |
| Valli | 4800.00 |
| Diana | 4200.00 |
```
:::

### 5-5. 확인 문제 답 — 응용 {keep}

:::answer [응용] 예시 답안
`hr_viewer`는 `hr_read` 롤의 구성원이라, 직접 받은 권한을 회수해도 **롤로 받은 `SELECT`** 가 남아 있습니다(5-2).

```sql postgres 창
REVOKE SELECT ON hr.departments FROM hr_viewer;

SELECT has_table_privilege('hr_viewer', 'hr.departments', 'SELECT') AS dept_select;
```

```result
| dept_select |
| --- |
| t |
```

롤 멤버십을 회수합니다.

```sql postgres 창
REVOKE hr_read FROM hr_viewer;

SELECT has_table_privilege('hr_viewer', 'hr.departments', 'SELECT')              AS dept_select
     , has_column_privilege('hr_viewer', 'hr.employees', 'salary', 'SELECT')     AS salary_select
     , has_column_privilege('hr_viewer', 'hr.employees', 'first_name', 'SELECT') AS name_select;
```

```result
| dept_select | salary_select | name_select |
| --- | --- | --- |
| f | f | t |
```

```sql hr_viewer 창
SELECT COUNT(*) AS dept_cnt
  FROM hr.departments;
```

```error
ERROR:  permission denied for table departments
```

`first_name`은 3-7 [응용]에서 `hr_viewer`에게 **직접** 준 컬럼 권한이라 롤을 회수해도 남습니다. 반대로 `salary`는 롤로만 받았던 권한이라 다시 볼 수 없게 되었습니다.
:::

## 6. 실무 — 에이전트 계정과 승인자 계정 나누기

### 6-1. 누가 무엇을 해야 하나 {keep}

Day 4의 「**조회 → 판단 → 승인 → 기록**」 흐름을 계정으로 나눠 봅니다. A1 이상 데이터인 스테이터(`EMT73633001`, 해외 벤더인데 UIT G)를 Q13처럼 정정하는 상황입니다.

| 계정 | 맡은 일 | 줄 권한 | 주지 않을 권한 |
| --- | --- | --- | --- |
| `agent_bot` | 데이터를 **조회**해 이상을 판단 (Day 4 6교시 `check_shortage` 같은 도구가 이 계정으로 접속) | `bom_reader` | 마스터 수정, 이력 기록 |
| `mat_staff` | 판단을 보고 **승인**한 뒤 UIT를 정정하고 **이력을 기록** (Q13) | `bom_reader` + `part_master.uit` UPDATE + `uit_change_history` INSERT | 다른 컬럼 수정, 이력 수정·삭제 |
| (누구도) | — | — | `uit_change_history`의 **UPDATE·DELETE** (이력 덮어쓰기 금지, Day 4 4교시) |

### 6-2. 계정 만들고 권한 주기 {keep}

```sql postgres 창
CREATE USER agent_bot PASSWORD 'agent1234';
CREATE USER mat_staff PASSWORD 'staff1234';
```

```result
CREATE ROLE
CREATE ROLE
```

`CREATE USER`도 결과 메시지는 `CREATE ROLE`입니다(2-2).

```sql postgres 창
GRANT CONNECT ON DATABASE bom_lab TO agent_bot, mat_staff;
GRANT bom_reader TO agent_bot, mat_staff;
GRANT UPDATE (uit) ON bom.part_master TO mat_staff;
GRANT INSERT ON bom.uit_change_history TO mat_staff;
```

```result
GRANT
GRANT ROLE
GRANT
GRANT
```

`TO` 뒤에 사용자를 쉼표로 여러 명 적을 수 있습니다.

### 6-3. agent_bot — 조회는 됩니다 {keep}

```sql agent_bot 창
SET search_path TO bom;

SELECT p.part_no, p.description_kr, p.uit
     , s.vendor_code, v.is_domestic, s.line_type
  FROM part_master p
  JOIN part_sourcing s ON s.part_no = p.part_no
  JOIN vendor v        ON v.vendor_code = s.vendor_code
 WHERE p.part_no = 'EMT73633001';
```

```result
| part_no | description_kr | uit | vendor_code | is_domestic | line_type |
| --- | --- | --- | --- | --- | --- |
| EMT73633001 | 스테이터 | G | V1009 | N | D |
```

해외 업체(`is_domestic = 'N'`)인데 UIT가 G(국내 구매품)입니다. 에이전트는 여기까지 **판단**할 수 있습니다.

### 6-3. agent_bot — 바꾸지는 못합니다 {keep}

```sql agent_bot 창
UPDATE part_master
   SET uit = 'D'
 WHERE part_no = 'EMT73633001';
```

```error
ERROR:  permission denied for table part_master
```

```sql agent_bot 창
INSERT INTO uit_change_history
VALUES (6, 'EMT73633001', 'G', 'D', 'AI Agent', '해외 벤더 조달 확인', CURRENT_DATE, 'N');
```

```error
ERROR:  permission denied for table uit_change_history
```

==에이전트 코드에 실수가 있거나 엉뚱한 SQL을 만들어 내도, DB가 권한으로 막아 줍니다.==

### 6-4. mat_staff — 승인 후 정정과 기록 {keep}

Q13과 같은 「UIT 정정 + 이력 INSERT」를 한 트랜잭션으로 실행합니다. 실습 데이터를 그대로 두기 위해 마지막에 `ROLLBACK`합니다.

```sql mat_staff 창
SET search_path TO bom;
BEGIN;

UPDATE part_master
   SET uit = 'D'
 WHERE part_no = 'EMT73633001';
```

```result
UPDATE 1
```

```sql mat_staff 창
INSERT INTO uit_change_history
SELECT MAX(change_id) + 1, 'EMT73633001', 'G', 'D', 'Procurement',
       '해외 벤더 조달 확인, UIT 정정', CURRENT_DATE, 'N'
  FROM uit_change_history;
```

```result
INSERT 0 1
```

> `change_id`를 `MAX(change_id) + 1`로 구한 이유: Q13을 이미 `COMMIT`한 PC에는 6번이 있어 `6`을 직접 적으면 PK 중복 오류가 납니다. 이 방식은 Q13 실행 여부와 상관없이 동작합니다.

### 6-4. 기록 확인 후 되돌리기 {keep}

```sql mat_staff 창
SELECT change_id, part_no, old_uit, new_uit, changed_by_dept
  FROM uit_change_history
 ORDER BY change_id;
```

```result
| change_id | part_no | old_uit | new_uit | changed_by_dept |
| --- | --- | --- | --- | --- |
| 1 | EBA56264701 | T | G | Manufacturing Engineering |
| 2 | EMT68237401 | G | T | Manufacturing Engineering |
| 3 | AHD26818801 | G | S | Procurement |
| 4 | EPM57964301 | G | D | Procurement |
| 5 | APK23572301 | T | P | R&D |
| 6 | EMT73633001 | G | D | Procurement |
```

```sql mat_staff 창
ROLLBACK;
```

```result
ROLLBACK
```

### 6-4. 승인자라도 막히는 것 {keep}

승인자라도 **허락된 컬럼 밖**과 **이력 수정·삭제**는 막힙니다.

```sql mat_staff 창
UPDATE part_master
   SET status_code = 1
 WHERE part_no = 'EMT73633001';
```

```error
ERROR:  permission denied for table part_master
```

```sql mat_staff 창
UPDATE uit_change_history
   SET change_reason = '사유 수정'
 WHERE change_id = 4;
```

```error
ERROR:  permission denied for table uit_change_history
```

```sql mat_staff 창
DELETE FROM uit_change_history
 WHERE change_id = 4;
```

```error
ERROR:  permission denied for table uit_change_history
```

### 6-4. 이력은 그대로 남았습니다 {keep}

```sql mat_staff 창
SELECT COUNT(*) AS cnt
  FROM uit_change_history;
```

```result
| cnt |
| --- |
| 5 |
```

Day 4 4교시의 「DELETE 대신 상태 변경, 이력 덮어쓰기 금지」는 사람이 지켜야 할 규칙입니다. ==권한으로 막아 두면 규칙을 잊어도 DB가 지켜 줍니다.==

### 6-5. 한눈에 보는 권한표 {keep}

```sql postgres 창
SELECT u.usr AS 계정
     , has_table_privilege(u.usr, 'bom.part_master', 'SELECT')        AS 마스터_조회
     , has_column_privilege(u.usr, 'bom.part_master', 'uit', 'UPDATE') AS uit_수정
     , has_table_privilege(u.usr, 'bom.uit_change_history', 'INSERT') AS 이력_기록
     , has_table_privilege(u.usr, 'bom.uit_change_history', 'UPDATE') AS 이력_수정
     , has_table_privilege(u.usr, 'bom.uit_change_history', 'DELETE') AS 이력_삭제
  FROM (VALUES ('agent_bot'), ('mat_staff'), ('dcl_test')) AS u(usr)
 ORDER BY u.usr;
```

```result
| 계정 | 마스터_조회 | uit_수정 | 이력_기록 | 이력_수정 | 이력_삭제 |
| --- | --- | --- | --- | --- | --- |
| agent_bot | t | f | f | f | f |
| dcl_test | t | f | f | f | f |
| mat_staff | t | t | t | f | f |
```

- `FROM (VALUES …) AS u(usr)`는 계정 이름 3개를 **임시 표**로 만든 것입니다. 계정마다 한 행씩 권한 확인 함수를 실행합니다.
- 이 표를 6-1의 설계표와 비교해, ==설계한 대로 권한이 들어갔는지 확인하는 것까지가 권한 작업==입니다.

:::teacher 강사 확인
- Day 4 5교시(Python 연동)에서 psycopg 접속 정보를 `postgres`가 아니라 `agent_bot`으로 바꾸면, 6교시 `check_shortage`가 조회만 할 수 있음을 직접 확인할 수 있습니다. 6교시에서 결품 기록 테이블에 INSERT해야 하면 그 테이블에만 `GRANT INSERT … TO agent_bot;`을 추가하는 식으로 연결하세요(기록 테이블 설계는 7단원 6장 `shortage_alert` 참고).
- 6-1의 역할 분담은 이 교안의 실습용 설계입니다. 실제 현장의 권한 체계를 설명하는 것은 아니라는 점을 말로 짚어 주세요.
:::

## 7. 계정 정리 — DROP ROLE

### 7-1. 권한이 남아 있으면 지울 수 없습니다 {keep}

```sql postgres 창
DROP ROLE dcl_test;
```

```error
ERROR:  role "dcl_test" cannot be dropped because some objects depend on it
DETAIL:  privileges for database bom_lab
```

`DETAIL`에 **아직 남아 있는 권한**이 나옵니다. `dcl_test`에게는 2-3의 CONNECT 권한이 남아 있습니다.

### 7-2. DROP OWNED BY → DROP ROLE {keep}

```sql postgres 창
DROP OWNED BY dcl_test;
DROP ROLE dcl_test;
```

```result
DROP OWNED
DROP ROLE
```

```sql postgres 창
SELECT rolname
  FROM pg_roles
 WHERE rolname NOT LIKE 'pg\_%'
 ORDER BY rolname;
```

```result
| rolname |
| --- |
| agent_bot |
| bom_reader |
| mat_staff |
| postgres |
```

### 7-2. DROP OWNED BY는 그 롤이 「주인인 객체」도 지웁니다 {keep}

:::error DROP OWNED BY는 그 롤이 「주인인 객체」도 지웁니다
`DROP OWNED BY`는 ① 그 롤이 받은 권한을 회수하고 ② **그 롤이 만든(주인인) 테이블 등을 삭제**합니다. 지우려는 계정이 만든 테이블을 남겨야 한다면, 먼저 주인을 바꿉니다.

```text 계정을 지우는 순서
REASSIGN OWNED BY 지울롤 TO 넘겨받을롤;   -- ① 주인 바꾸기
DROP OWNED BY 지울롤;                    -- ② 남은 권한 회수
DROP ROLE 지울롤;                        -- ③ 롤 삭제
```

두 명령은 **지금 접속한 데이터베이스 안에서만** 동작하므로, 그 롤이 쓰인 DB마다 실행해야 합니다.
:::

:::teacher 강사 확인
- **롤은 서버 전체, 권한은 객체마다** 저장됩니다. `schema_postgres.sql`을 다시 실행하면(`DROP SCHEMA bom CASCADE`) `bom` 스키마·테이블에 준 권한과 5-3의 기본 권한은 함께 사라지지만, `bom_reader`·`agent_bot`·`mat_staff` 롤은 남습니다(재적재 후 `has_table_privilege('bom_reader', 'bom.part_master', 'SELECT')` = `f`, `pg_default_acl` 0행 확인). 이때 `CREATE ROLE`부터 다시 실행하면 `role "…" already exists` 오류가 나므로, `GRANT` 문만 다시 실행하게 하세요.
- 2-3에서 회수한 PUBLIC 접속 권한은 `GRANT CONNECT ON DATABASE bom_lab TO PUBLIC;`로 되돌릴 수 있습니다. 회수한 상태로 두면 이후 새 계정마다 `GRANT CONNECT`가 필요합니다.
- 실습 계정을 모두 지우려면 `12. DCL.sql` 맨 아래 「정리」 블록을 실행합니다.
:::

## 8. 복습 문제

### 8-0. 복습 문제 안내 {keep}

> 범위: DCL 전체(사용자 · CONNECT · USAGE · 객체 권한 · 컬럼 권한 · ROLE · REVOKE · DROP ROLE). 관리자 명령은 `postgres` 창, 확인은 `plan_viewer` 창에서 실행합니다. 2-3에서 `bom_lab`의 PUBLIC 접속 권한을 회수한 상태라고 가정합니다.

```icons 여섯 문항
user-plus | 1 · 계정 · 권한 3개 | 생산계획 조회 계정 plan_viewer | rose
ban | 2 · 오류 읽기 | 받지 않은 테이블 조회 | plum
columns-3 | 3 · 컬럼 권한 | vendor 세 컬럼만 | lime
users | 4 · ROLE · 컬럼 UPDATE | 구매 담당 롤 mat_role | ivory
search | 5 · (심화) 권한 조회 | role_table_grants에 안 보이는 것 | plum
trash-2 | 6 · DROP ROLE | 계정 정리 | hot
```

### 8-1. 복습 1 {keep}

**1.** 생산계획 조회용 계정 `plan_viewer`(비밀번호 `1234`)를 만들고, `bom_lab` 접속과 `production_plan` 조회만 가능하게 하세요. `plan_viewer` 창에서 라인별 계획 합계를 라인 순으로 출력합니다.
[힌트: 권한 명령 3개 — `CONNECT`, `USAGE`, `SELECT`]

```result 출력 결과 (총 2행)
| line_code | total_plan |
| --- | --- |
| LINE-A | 4520 |
| LINE-B | 3460 |
```

### 8-2. 복습 2 {keep}

**2.** `plan_viewer` 창에서 컴프레서(`ECP39799101`)의 현재고를 조회하면 어떤 오류가 나나요? 그 오류가 나는 이유는?

```error 출력 결과
ERROR:  permission denied for table inventory
```

### 8-3. 복습 3 {keep}

**3.** `plan_viewer`가 업체 테이블(`vendor`)에서 `vendor_code`, `vendor_name`, `country` 세 컬럼만 볼 수 있게 하세요. 그다음 `plan_viewer` 창에서
(가) 해외 업체(`country`가 `KR`이 아닌 업체)의 세 컬럼을 업체 코드 순으로 출력하고,
(나) 같은 결과를 `WHERE is_domestic = 'N'`으로 구하면 어떻게 되는지 확인하세요.

```result 출력 결과 (가) (총 4행)
| vendor_code | vendor_name | country |
| --- | --- | --- |
| V1004 | AsiaComp Co., Ltd. | CN |
| V1005 | NanoChip Semiconductor | TW |
| V1007 | Global Steel Trading | JP |
| V1009 | Pacific Motor Parts | VN |
```

```error 출력 결과 (나)
ERROR:  permission denied for table vendor
```

### 8-4. 복습 4 {keep}

**4.** 구매 담당 롤 `mat_role`을 만들어, `bom` 스키마 `USAGE`와 `part_sourcing` 조회, 그리고 `part_sourcing`의 단가(`po_price`)와 리드타임(`lead_time_days`)만 수정할 수 있게 하세요. 이 롤을 `plan_viewer`에게 주고, `postgres` 창에서 `plan_viewer`의 컬럼 수정 권한을 확인합니다.

```result 출력 결과 (총 1행)
| po_price | lead_time | vendor_code |
| --- | --- | --- |
| t | t | f |
```

### 8-5. 복습 5 · 6 {keep}

**5.** (심화) `postgres` 창에서 `information_schema.role_table_grants`로 `plan_viewer`와 `mat_role`이 받은 테이블 권한을 조회하세요. 1~4번에서 준 권한 중 이 결과에 보이지 않는 것은 무엇이고, 왜 안 보일까요?

```result 출력 결과 (총 2행)
| grantee | table_name | privilege_type |
| --- | --- | --- |
| mat_role | part_sourcing | SELECT |
| plan_viewer | production_plan | SELECT |
```

**6.** `plan_viewer`와 `mat_role`을 삭제하세요. `DROP ROLE plan_viewer;`를 바로 실행했을 때의 오류를 확인하고, 삭제까지 마칩니다.

```error 출력 결과 — DROP ROLE plan_viewer; 첫 실행
ERROR:  role "plan_viewer" cannot be dropped because some objects depend on it
DETAIL:  privileges for database bom_lab
privileges for schema bom
privileges for column vendor_code of table bom.vendor
privileges for column vendor_name of table bom.vendor
privileges for column country of table bom.vendor
privileges for table bom.production_plan
```

### 8-6. 복습 1 · 2 답 {keep}

:::answer 복습 1 · 2 예시 답안
```sql 1 — postgres 창
CREATE USER plan_viewer PASSWORD '1234';
GRANT CONNECT ON DATABASE bom_lab TO plan_viewer;
GRANT USAGE ON SCHEMA bom TO plan_viewer;
GRANT SELECT ON bom.production_plan TO plan_viewer;
```

```sql 1 — plan_viewer 창
SELECT line_code, SUM(plan_qty) AS total_plan
  FROM bom.production_plan
 GROUP BY line_code
 ORDER BY line_code;
```

```sql 2 — plan_viewer 창
SELECT part_no, on_hand_qty
  FROM bom.inventory
 WHERE part_no = 'ECP39799101';
```

- 2번: `plan_viewer`는 `production_plan`의 SELECT만 받았습니다. 스키마 `USAGE`가 있어 스키마 단계는 통과하고, **테이블** 단계에서 막힙니다.
:::

### 8-7. 복습 3 · 4 답 {keep}

:::answer 복습 3 · 4 예시 답안
```sql 3 — postgres 창
GRANT SELECT (vendor_code, vendor_name, country) ON bom.vendor TO plan_viewer;
```

```sql 3 — plan_viewer 창
-- (가)
SELECT vendor_code, vendor_name, country
  FROM bom.vendor
 WHERE country <> 'KR'
 ORDER BY vendor_code;

-- (나)
SELECT vendor_code, vendor_name
  FROM bom.vendor
 WHERE is_domestic = 'N';
```

```sql 4 — postgres 창
CREATE ROLE mat_role;
GRANT USAGE ON SCHEMA bom TO mat_role;
GRANT SELECT, UPDATE (po_price, lead_time_days) ON bom.part_sourcing TO mat_role;
GRANT mat_role TO plan_viewer;

SELECT has_column_privilege('plan_viewer', 'bom.part_sourcing', 'po_price', 'UPDATE')       AS po_price
     , has_column_privilege('plan_viewer', 'bom.part_sourcing', 'lead_time_days', 'UPDATE') AS lead_time
     , has_column_privilege('plan_viewer', 'bom.part_sourcing', 'vendor_code', 'UPDATE')    AS vendor_code;
```

- 3번 (나): `is_domestic`은 허용한 세 컬럼에 없으므로 `WHERE`에서도 쓸 수 없습니다(3-7 [응용]). 그래서 (가)는 `country`로 조건을 걸었습니다.
- 4번: 한 문장 `GRANT SELECT, UPDATE (po_price, lead_time_days)`에서 `SELECT`는 **테이블 전체**, `UPDATE`는 **두 컬럼**에만 적용됩니다. 괄호는 바로 앞의 권한에만 붙습니다.
:::

### 8-8. 복습 5 · 6 답 {keep}

:::answer 복습 5 · 6 예시 답안
```sql 5 — postgres 창
SELECT grantee, table_name, privilege_type
  FROM information_schema.role_table_grants
 WHERE grantee IN ('plan_viewer', 'mat_role')
 ORDER BY grantee, table_name, privilege_type;
```

```sql 6 — postgres 창
DROP ROLE plan_viewer;        -- 오류 확인
DROP OWNED BY plan_viewer;
DROP ROLE plan_viewer;

DROP OWNED BY mat_role;
DROP ROLE mat_role;
```

- 5번: 보이지 않는 것은 ① 3번의 `vendor` **컬럼** 권한과 4번의 `po_price`·`lead_time_days` **컬럼** UPDATE 권한(`role_table_grants`는 테이블 전체에 준 권한만 보여 줍니다. 컬럼 권한은 `information_schema.column_privileges`에서 봅니다), ② `plan_viewer`가 `mat_role`을 통해 물려받은 `part_sourcing` 권한(이 뷰는 **직접 받은** 롤 기준으로 보여 줍니다), ③ `CONNECT`·`USAGE`(테이블 권한이 아닙니다). 권한 확인은 `has_…_privilege` 함수가 물려받은 권한까지 반영합니다.
- 6번: `mat_role`을 먼저 지우지 않아도 `plan_viewer`는 삭제됩니다(멤버십은 롤과 함께 사라짐). `mat_role`도 받은 권한이 있으므로 같은 순서로 지웁니다.
:::

## 9. 정리

### 9-1. 오늘 배운 것 {keep}

:::summary
- **DCL** = `GRANT`(부여) · `REVOKE`(회수) · ROLE(권한 묶음). 「누가 무엇을 할 수 있는가」를 정합니다.
- **슈퍼유저(`postgres`)** 는 권한 검사를 건너뜁니다. 권한 확인은 반드시 새 계정으로 접속해서 합니다.
- **사용자** = LOGIN 속성이 있는 롤. `CREATE USER`(LOGIN 기본) / `CREATE ROLE`(NOLOGIN 기본).
- **접속 3단계**: ① LOGIN 속성 → ② DB의 `CONNECT` → ③ 스키마의 `USAGE` → 그다음에야 테이블 권한(`SELECT`·`INSERT`·`UPDATE`·`DELETE` …).
- **오류로 위치 찾기**: `not permitted to log in`(LOGIN) / `permission denied for database`(CONNECT) / `permission denied for schema`(USAGE) / `permission denied for table`(객체 권한). 새 계정에서 `does not exist`면 스키마 권한부터 의심합니다.
- **컬럼 권한**: `GRANT UPDATE (uit) ON …`. 보지 못하게 한 컬럼은 `WHERE`에도 쓸 수 없습니다.
- **ROLE**: 권한을 롤에 묶어 `GRANT 롤 TO 사용자;`로 부여. 직접 회수해도 롤로 받은 권한은 남습니다.
- **ALL TABLES IN SCHEMA**는 지금 있는 테이블만. 앞으로 만들 테이블은 `ALTER DEFAULT PRIVILEGES`.
- **최소 권한**: 에이전트는 조회만, 승인자는 필요한 컬럼 수정 + 이력 INSERT, 이력의 UPDATE·DELETE는 아무에게도 주지 않습니다.
- **DROP ROLE** 전에 `DROP OWNED BY`(필요하면 `REASSIGN OWNED BY` 먼저).
:::

### 9-2. 확인 문제

:::quiz
Q. `CREATE ROLE kim PASSWORD '1234';`로 만든 계정으로 접속이 안 되는 이유와 해결 방법은?
A. `CREATE ROLE`은 기본이 NOLOGIN이라 `role "kim" is not permitted to log in` 오류가 납니다. `ALTER ROLE kim LOGIN;`을 실행하거나 처음부터 `CREATE USER`로 만듭니다.

Q. `GRANT SELECT ON bom.part_master TO kim;`만 실행했더니 `permission denied for schema bom`이 납니다. 무엇이 빠졌나요?
A. 스키마에 들어갈 권한 `GRANT USAGE ON SCHEMA bom TO kim;`이 빠졌습니다. 스키마 권한 → 테이블 권한 순서로 검사됩니다.

Q. `GRANT SELECT ON ALL TABLES IN SCHEMA bom TO bom_reader;` 뒤에 만든 테이블을 `bom_reader` 구성원이 조회하지 못하는 이유는?
A. `ALL TABLES IN SCHEMA`는 실행한 순간 있던 테이블에만 적용되기 때문입니다. 새 테이블에 `GRANT`를 따로 하거나, 미리 `ALTER DEFAULT PRIVILEGES IN SCHEMA bom GRANT SELECT ON TABLES TO bom_reader;`를 설정해 둡니다.

Q. `REVOKE SELECT ON hr.departments FROM hr_viewer;`가 성공했는데도 `hr_viewer`가 부서를 조회할 수 있습니다. 왜일까요?
A. `hr_viewer`가 SELECT 권한이 있는 롤(`hr_read`)의 구성원이라 롤의 권한을 물려받기 때문입니다. `REVOKE hr_read FROM hr_viewer;`로 멤버십도 회수해야 합니다.

Q. 에이전트 계정 `agent_bot`에 `bom_reader`만 준 이유는 무엇인가요?
A. 에이전트는 조회·판단만 하고, 마스터 정정과 이력 기록은 사람이 승인한 뒤 승인자 계정이 하도록 나누기 위해서입니다(최소 권한 원칙). 잘못된 SQL이 실행되어도 DB가 권한으로 막습니다.
:::
