# linc

**One platform for creators, brands and agencies.** Book real creators, run AI-powered campaigns, and let creators keep earning from their look — all in one place. Built for India.

This repo is a NestJS app with a polished, VC-ready sample UI. The static UI also runs on its own (with built-in sample data) so it can be hosted on GitHub Pages with no backend.

## What's included

- **Landing page** — value for all three audiences (brands, creators, agencies), four flagship features, Certified Digi Creator spotlight, results, and the data flywheel
- **Brand dashboard** — campaign performance, deals, suggested creators, AI ad generator, live activity
- **Creator dashboard** — deals, Certified Digi Creator earnings, activity
- **Agency dashboard** — client campaigns, portfolio, delivery stats
- **REST API** — `/api/stats`, `/api/creators`, `/api/deals`, `/api/campaigns`, `/api/activity`, `/health`
- **Static fallback** — the UI ships with sample data, so it works with or without the backend
- **CI + Pages** — GitHub Actions for build/lint/test and GitHub Pages deploy
- **Docker** — production-ready container image

## Quick start

```bash
npm install
npm run start:dev
```

Open [http://localhost:3000](http://localhost:3000).

## Scripts

| Command | Description |
|---------|-------------|
| `npm run start:dev` | Dev server with hot reload |
| `npm run build` | Compile to `dist/` |
| `npm run start:prod` | Run production build |
| `npm test` | Unit tests |
| `npm run test:e2e` | End-to-end tests |
| `npm run lint` | ESLint |

## Deploy the UI on GitHub Pages

The `public/` folder is a self-contained static site. The workflow at
`.github/workflows/pages.yml` publishes it on every push to `main`.

1. Push this repo to GitHub.
2. In the repo, go to **Settings → Pages → Build and deployment** and set the source to **GitHub Actions**.
3. The site goes live at `https://YOUR_USERNAME.github.io/REPO/`.

When served as a static site there's no Node backend, so the dashboards
automatically fall back to the built-in sample data.

## Deploy the full app with Docker

```bash
docker build -t linc .
docker run -p 3000:3000 linc
```

Works on Railway, Render, Fly.io, or any container host. Set `PORT` if your platform requires a non-default port.

## API

| Endpoint | Description |
|----------|-------------|
| `GET /` | Sample UI |
| `GET /health` | Health check |
| `GET /api/stats` | Platform stats |
| `GET /api/creators` | Suggested creators |
| `GET /api/deals` | Active deals |
| `GET /api/campaigns` | Campaign performance |
| `GET /api/activity` | Live activity feed |

## Project structure

```
linc/
├── public/          # Static UI (HTML, CSS, JS) — also runs standalone
├── src/             # NestJS app
├── test/            # E2E tests
├── .github/         # CI + Pages workflows
└── Dockerfile
```

## License

UNLICENSED — private project.
