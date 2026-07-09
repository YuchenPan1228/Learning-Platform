# Quant Prep Web

Next.js frontend shell for the local MVP.

## Setup

From the repository root:

```bash
cp .env.example .env
```

Install dependencies:

```bash
cd apps/web
npm install
```

## Run

```bash
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Open [http://127.0.0.1:3000](http://127.0.0.1:3000).

## MVP routes

- `/`
- `/topics`
- `/topics/[slug]`
- `/concepts/[slug]`
- `/practice`
- `/mental-math`
- `/flashcards`
- `/admin/import`
- `/admin/review`

Page content is placeholder-only in QP-004. Feature pages arrive in Phase 2.
