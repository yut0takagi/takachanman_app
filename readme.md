<!-- このファイルはプロジェクトの概要・構成・使い方を説明するREADMEです。 -->
# takachanman unified FastAPI server

本プロジェクトは以下を単一サーバで提供します：

- /common/auth/* に一元化したJWT認証（access/refresh, bcrypt, RBAC）
- /common/payments/* など、共通機能は common 配下に集約
- /yutotkg/<service>/... 形式の複数サービス（analytics）
- SQLAlchemy + SQLite, Pydantic Settings, CORS, 簡易RateLimit, pytest最小テスト
- Dockerfile・docker-compose・README 付属

## ディレクトリ構成

```txt
/takachanman_app/
  ├── server/
  │   ├── main.py                    # FastAPIエントリ
  │   ├── core/
  │   │   ├── config.py              # Pydantic Settings
  │   │   ├── database.py            # SQLAlchemy (SQLite)
  │   │   ├── security.py            # bcrypt + JWT
  │   │   └── rate_limit.py          # 簡易RateLimitミドルウェア
  │   ├── api/
  │   │   ├── __init__.py
  │   │   └── routers/
  │   │       ├── analytics.py       # /yutotkg/analytics/*
  │   │       └── payments.py        # /common/payments/*
  │   ├── common/
  │   │   ├── __init__.py
  │   │   ├── auth.py                # /common/auth/*
  │   │   ├── deps.py                # 認証・RBAC依存
  │   │   ├── router.py              # /common/* 共通多数: health, metrics, audit, version, config, ping, time, uuid, ip, headers, echo, uptime, crypto(hash/verify), base64(encode/decode), env, readiness, liveness, whoami
  │   │   ├── metrics.py             # メトリクスミドルウェア/取得
  │   │   └── audit.py               # 監査ログ（簡易インメモリ）
  │   ├── models/
  │   │   ├── __init__.py
  │   │   └── user.py                # User, Role, UserRole
  │   └── schemas/
  │       ├── __init__.py
  │       ├── auth.py                # 認証系スキーマ
  │       └── common.py              # 共通スキーマ
  ├── tests/
  │   └── test_auth_flow.py          # pytest最小テスト
  ├── requirements.txt
  ├── Dockerfile
  ├── docker-compose.yml
  └── README.md (本ファイル)
```

## 主要機能

- 認証: /common/auth/register, /common/auth/login, /common/auth/refresh, /common/auth/me
- RBAC: `require_roles(["analyst", "billing", "admin"])` などで保護
- サービス: `/yutotkg/analytics/events`
- 共通例:
  - `/common/health`, `/common/health/deep`, `/common/readiness`, `/common/liveness`
  - `/common/metrics`, `/common/uptime`
  - `/common/metrics/prometheus` (text/plain; Prometheus exposition 0.0.4)
  - `/common/audit/events` (GET/POST, admin)
  - `/common/version`, `/common/config` (admin)
  - `/common/ping`, `/common/time`, `/common/uuid`, `/common/ip`, `/common/headers`, `/common/echo`
  - `/common/crypto/hash` (admin), `/common/crypto/verify` (admin)
  - `/common/base64/encode`, `/common/base64/decode`
  - `/common/env` (admin)
  - `/common/logs` (admin): 直近ログの取得（limit, level で絞り込み）
  - `/common/logs/level` (admin): ログレベル変更（payload: `{ "name": "", "level": "INFO" }`）
- 決済: `/common/payments/invoices`, `/common/payments/refund`
- CORS: `APP_CORS_ORIGINS` で設定（デフォルト `*`）
- RateLimit: デフォルト 60リクエスト/60秒（シングルプロセス用）

## 設計ポリシー（今日の変更点）

- 共通機能は server/common/ に統合（auth, deps, router, metrics, audit）。エンドポイントは `/common/*` 配下。
- サービス固有の API は server/api/routers/ に配置し、パスはサービス名で切る（例: `/yutotkg/analytics/*`）。
- 認証は共通化（/common/auth/*）。アクセストークン/リフレッシュトークン、bcrypt、RBAC（ロール）対応。
- 監視・運用向けの共通エンドポイントを多数追加（health/readiness/liveness、metrics、audit、version/config、whoami、base64 など）。
  - Prometheus 形式の `/common/metrics/prometheus` と、ログ閲覧 `/common/logs`・レベル変更 `/common/logs/level` を追加。
- OpenAPI の OAuth2 tokenUrl は `/common/auth/login`（フォームログイン）。Swagger の Authorize は手動 Bearer 設定が確実です。

## クイックスタート（API）

1) ユーザ登録（既定ロール: `user`）

```bash
curl -sS -X POST http://localhost:8000/common/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"secret123"}'
```

2) ログイン（OAuth2 Password）

```bash
curl -sS -X POST http://localhost:8000/common/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=user@example.com&password=secret123'
```

レスポンス例:

```json
{"access_token":"...","refresh_token":"...","token_type":"bearer"}
```

3) 自分情報

```bash
ACCESS=...(上の access_token)
curl -sS http://localhost:8000/common/auth/me -H "Authorization: Bearer $ACCESS"
```

4) 共通ユーティリティ例

```bash
curl -sS http://localhost:8000/common/health
curl -sS http://localhost:8000/common/whoami -H "Authorization: Bearer $ACCESS"
curl -sS http://localhost:8000/common/metrics
curl -sS http://localhost:8000/common/metrics/prometheus
curl -sS -X POST http://localhost:8000/common/base64/encode -H 'Content-Type: application/json' -d '{"text":"hello"}'
```

5) RBAC 保護エンドポイント

```bash
# ロール未付与の user では 403
curl -i http://localhost:8000/common/payments/invoices -H "Authorization: Bearer $ACCESS"
```

ロール付与（例: admin）を行うには、データベースにレコードを追加してください（SQLite 例）:

```bash
sqlite3 app.db "INSERT OR IGNORE INTO roles(name) VALUES('admin');
INSERT OR IGNORE INTO user_roles(user_id, role_id)
  SELECT u.id, r.id FROM users u, roles r
  WHERE u.email='user@example.com' AND r.name='admin';"
```

付与後は `Authorization: Bearer` で `/common/audit/events` POST/GET などの admin 限定 API が利用できます。

## 環境変数（主要）

- `APP_SECRET_KEY`: JWT署名キー（必ず変更してください）
- `APP_ACCESS_TOKEN_EXPIRES_MINUTES`: アクセストークン有効期限（分）
- `APP_REFRESH_TOKEN_EXPIRES_MINUTES`: リフレッシュトークン有効期限（分）
- `APP_SQLITE_PATH` or `APP_DATABASE_URL`: SQLiteファイル or 接続URL
- `APP_CORS_ORIGINS`: 例 `http://localhost:3000,https://example.com`
- `APP_RATE_LIMIT_MAX`, `APP_RATE_LIMIT_WINDOW`
 - `APP_DEFAULT_ROLES`: 新規登録時に付与するロール（カンマ区切り）

### .env サンプル

```env
APP_ENV=local
APP_DEBUG=true
APP_SECRET_KEY=dev-secret-change-me
APP_ACCESS_TOKEN_EXPIRES_MINUTES=30
APP_REFRESH_TOKEN_EXPIRES_MINUTES=10080
APP_SQLITE_PATH=./app.db
APP_CORS_ORIGINS=http://localhost:3000, http://127.0.0.1:3000, *
APP_RATE_LIMIT_MAX=60
APP_RATE_LIMIT_WINDOW=60
APP_DEFAULT_ROLES=user
```

## ローカル実行

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn server.main:app --reload
# http://localhost:8000/docs
```

## Docker 実行

```bash
docker compose build
docker compose up
# http://localhost:8000/docs
```

### DockerでDB管理（PostgreSQL）

- 本リポジトリの `docker-compose.yml` には `db` サービス（PostgreSQL 15）が同梱されています。
- API は `APP_DATABASE_URL` で Postgres に接続します。

デフォルト設定:
- DBホスト: `db`
- ポート: `5432`
- DB名: `takachan_db`
- ユーザ/パスワード: `takachan` / `takachan`

Compose で起動すると、自動的にテーブルを作成します（`server/main.py` の `create_all()` により）。

接続先を SQLite に戻したい場合は、`APP_DATABASE_URL` を未設定にし、`APP_SQLITE_PATH` を利用してください。

## pytest

```bash
pytest -q
```

## 備考

- RateLimitは簡易なメモリ実装のため、単一プロセス/コンテナでの利用を前提としています。
- RBAC用ロールはユーザ登録時に `APP_DEFAULT_ROLES`（デフォルト`user`）が付与されます。`admin`/`analyst`/`billing` 等は適宜DBに作成して付与してください。
 - 依存: `email-validator`（EmailStr 用）, `python-multipart`（フォームログイン用）は `requirements.txt` に含めています。
- Swagger の Authorize ボタンは `tokenUrl=/common/auth/login` を使います。ログイン API のレスポンスから手動で Bearer を設定するのが確実です。
 - ログ収集はアプリ起動時にリングバッファハンドラを登録（最大1000件）。`/common/logs` で取得、`/common/logs/level` でレベル変更できます。
