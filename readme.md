# takachanman app
```txt
# ディレクトリ構成
/takachanman_app/
  ├── docs/
  ├── server/
  │   ├── app.py                    # FastAPI起動点（単一アプリ）
  │   ├── core/
  │   │   ├── config.py              # 設定・環境変数
  │   │   ├── deps.py                # 共通依存（DB, 認証など）
  │   │   └── middleware.py          # CORS, Logging, RootPath対応
  │   ├── common/
  │   │   ├── models/                # 共有Pydanticモデル
  │   │   ├── utils/                 # 共通ユーティリティ
  │   │   └── errors.py              # 例外ハンドラ
  │   └── services/                  # ← 各サービスをBPとして管理
  │       ├── __init__.py
  │       ├── accounts/
  │       │   ├── __init__.py
  │       │   ├── router.py          # prefix="/accounts"
  │       │   └── endpoints/
  │       │       ├── profile.py     # /accounts/profile
  │       │       └── sessions.py    # /accounts/sessions
  │       ├── payments/
  │       │   ├── __init__.py
  │       │   ├── router.py          # prefix="/payments"
  │       │   └── endpoints/
  │       │       ├── refund.py      # /payments/refund
  │       │       └── invoice.py     # /payments/invoice
  │       └── analytics/
  │           ├── __init__.py
  │           ├── router.py          # prefix="/analytics"
  │           └── endpoints/
  │               └── events.py      # /analytics/events
  │
  ├── pyproject.toml or requirements.txt
  └── README.md
```

# 確認方法
```bash
docker compose build
docker compose up
```