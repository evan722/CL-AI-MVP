# CL-AI-MVP Frontend UI

This directory contains a Next.js App Router frontend that provides a modern interface for the existing CL-AI-MVP backend. All original API routes and player/upload flows remain untouched.

## Getting Started

```bash
cd frontend
npm install
npm run dev
```

## Integration Notes

- `lib/routes.ts` defines `LEGACY_UPLOAD_PATH` and `LEGACY_PLAYER_PATH` constants. Adjust these to match the paths of the current upload page and player.
- The player wrapper at `/player/[id]` loads the existing player inside an `iframe`. No backend changes are required.
- The catalog includes a pre-generated **Python Basics** course and a **Design Your Own** flow that links to the legacy uploader.
- Components are styled with Tailwind CSS and shadcn/ui primitives. Animations use Framer Motion where applicable.
- All features are front-end only; replace mock data with real API calls as needed.

## Building for Production

```bash
npm run build
npm start
```
