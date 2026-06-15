# linc backend (FastAPI)

Python API for linc. Its headline feature is the **creator social-connection
flow** — OAuth with a platform, then pulling followers / engagement / audience
insights. It's **multi-platform by design**: Instagram and YouTube ship today,
and adding another platform (e.g. TikTok) is one new `SocialProvider` class.

Each provider runs in **mock mode** until its credentials are supplied, so the
whole flow works locally and on a demo deploy with no apps set up.

## Run it

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # optional — defaults work in mock mode
uvicorn app.main:app --reload --port 8000
```

Open <http://localhost:8000> — the static UI is served by the API, so the
"Connect Instagram" button on the creator dashboard talks to this backend.

API docs (auto-generated): <http://localhost:8000/docs>

## Mock vs live (per platform)

| | Mock (default) | Live |
|---|---|---|
| Instagram trigger | `META_APP_ID` / `META_APP_SECRET` unset | both set in `.env` |
| YouTube trigger | `YOUTUBE_CLIENT_ID` / `…_SECRET` unset | both set in `.env` |
| OAuth | skips the dialog, bounces to the callback | real platform login |
| Insights | realistic sample numbers | platform API |

`GET /health` reports each provider's mode. Redirect URIs are derived as
`{API_BASE_URL}/api/auth/{platform}/callback` — register those in each app.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Status + per-provider mode |
| GET | `/api/stats` `…/deals` `…/campaigns` `…/activity` | Dashboard catalog |
| GET | `/api/creators` | Creators (with `connectedPlatforms`) |
| GET | `/api/creators/{id}` | One creator |
| GET | `/api/auth/{platform}/login?creator_id=` | Start OAuth (redirects) |
| GET | `/api/auth/{platform}/callback` | Finish OAuth (redirects to UI) |
| GET | `/api/creators/{id}/connections` | All linked accounts (no tokens) |
| GET | `/api/creators/{id}/connections/{platform}` | One linked account |
| GET | `/api/creators/{id}/insights/{platform}` | Followers / engagement / audience |
| DELETE | `/api/creators/{id}/connections/{platform}` | Disconnect a platform |

`{platform}` is `instagram` or `youtube` today.

## Layout

```
app/
  config.py          # env-driven settings; per-provider creds
  models/            # Pydantic schemas (snake_case in, camelCase out)
    connection.py    #   Platform, SocialConnection (generic, + metadata)
    insights.py      #   SocialInsights, Metric (per-platform metric list)
  providers/         # one integration per platform
    base.py          #   SocialProvider interface + shared helpers
    instagram.py     #   Meta / Instagram Graph API
    youtube.py       #   Google / YouTube Data API
    registry.py      #   Platform -> provider lookup
  repositories/
    base.py          # abstract interfaces (connections keyed by creator+platform)
    memory.py        # in-memory implementations (current)
  services/creator_service.py   # orchestration, provider-agnostic
  routers/           # auth, creators, platform
  deps.py            # DI wiring — swap in Postgres / add providers here
  data/seed.py       # demo seed data
  main.py            # app, CORS, serves the static UI
```

## Adding a platform

1. Add the value to `Platform` in `models/connection.py`.
2. Write `providers/tiktok.py` implementing `SocialProvider`.
3. Register it in `deps.py` `get_registry()`.

No model, route, repository, or service changes — and the frontend just needs
one more entry in its `PLATFORMS` list.

## Moving to Postgres later

The data layer is behind interfaces in `repositories/base.py`. To switch:

1. Add `repositories/postgres.py` implementing the same interfaces (e.g. with
   SQLAlchemy + asyncpg). The domain models map directly onto tables.
2. Set `DATABASE_URL` and return the Postgres repos from `deps.py`.

No service or router code changes.
