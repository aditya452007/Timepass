# TECH_STACK.md — Exact Versions & Technology Decisions

> Every version is pinned. No vagueness. Verified as of March 2026.

---

## RUNTIME & PACKAGE MANAGER

| Tool | Version | Why |
|------|---------|-----|
| Node.js | 24.x LTS ("Krypton") | Latest LTS (entered LTS Oct 2025, supported to April 2028) |
| npm | 10.x (bundled with Node 24) | Default, no need for yarn/pnpm |

---

## FRONTEND

| Package | Version | Purpose |
|---------|---------|---------|
| react | 19.2.4 | UI framework (latest stable as of Jan 2026) |
| react-dom | 19.2.4 | DOM rendering |
| react-router-dom | 7.1.x | Client-side routing |
| video.js | 8.x | HLS video player |
| videojs-http-streaming (VHS) | 4.x | HLS support for Video.js |
| axios | 1.7.x | HTTP client for API calls |
| vite | 6.x | Build tool (fast, no CRA) |

**No** Tailwind. **No** CSS-in-JS. Plain CSS with CSS custom properties (variables).  
See `FRONTEND_GUIDELINES.md` for the full color system and design tokens.

---

## BACKEND

| Package | Version | Purpose |
|---------|---------|---------|
| express | 4.21.x | HTTP server framework |
| mongoose | 8.x | MongoDB ODM |
| bcryptjs | 2.4.x | Password hashing |
| jsonwebtoken | 9.x | JWT generation and verification |
| cookie-parser | 1.4.x | Parse httpOnly cookies |
| cors | 2.8.x | Cross-origin request handling |
| multer | 1.4.x | Handle multipart/form-data file metadata |
| dotenv | 16.x | Load `.env` into `process.env` |
| imagekitio-node | 4.x | ImageKit server SDK (auth signature generation) |

---

## DATABASE

| Service | Details |
|---------|---------|
| MongoDB Atlas | Free M0 cluster, cloud-hosted |
| Mongoose ODM | Version 8.x, schema-based models |
| Connection | Via `MONGODB_URI` in `.env` (Atlas connection string with username/password) |

---

## VIDEO STORAGE & STREAMING

| Service | Details |
|---------|---------|
| ImageKit.io | Free tier — 20GB storage, 20GB bandwidth/month |
| Upload method | Client uploads directly to ImageKit using server-signed auth token |
| Streaming format | ImageKit auto-serves HLS (`.m3u8`) for uploaded MP4 files |
| Video.js | Plays the `.m3u8` HLS URL from ImageKit in browser |

---

## PROJECT STRUCTURE

```
streamvibe/
├── .env                    ← ALL secrets go here (never commit)
├── .gitignore
├── README.md
│
├── backend/                ← Express API server
│   ├── package.json
│   ├── server.js           ← Entry point, starts Express
│   ├── config/
│   │   └── db.js           ← MongoDB Atlas connection
│   ├── models/
│   │   ├── User.js
│   │   └── Video.js
│   ├── routes/
│   │   ├── auth.js         ← /api/auth/*
│   │   ├── videos.js       ← /api/videos/*
│   │   ├── users.js        ← /api/users/*
│   │   └── upload.js       ← /api/upload/*
│   ├── middleware/
│   │   └── auth.js         ← JWT verify middleware
│   └── utils/
│       └── imagekit.js     ← ImageKit SDK instance
│
└── frontend/               ← React + Vite app
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx        ← React entry point
        ├── App.jsx         ← Router setup
        ├── api/
        │   └── index.js    ← All axios API calls
        ├── context/
        │   └── AuthContext.jsx   ← Global auth state
        ├── components/
        │   ├── Navbar.jsx
        │   ├── VideoCard.jsx
        │   └── VideoPlayer.jsx
        ├── pages/
        │   ├── Home.jsx
        │   ├── Login.jsx
        │   ├── Register.jsx
        │   ├── Upload.jsx
        │   ├── Watch.jsx
        │   ├── Profile.jsx
        │   └── Search.jsx
        └── styles/
            ├── global.css       ← CSS variables + resets
            └── components.css   ← Component-level styles
```

---

## ENVIRONMENT VARIABLES (`.env` in project root)

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/streamvibe?retryWrites=true&w=majority

# JWT
JWT_SECRET=your_super_secret_jwt_key_here_min_32_chars
JWT_EXPIRES_IN=7d

# ImageKit.io
IMAGEKIT_PUBLIC_KEY=public_xxxxxxxxxxxx
IMAGEKIT_PRIVATE_KEY=private_xxxxxxxxxxxx
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_imagekit_id

# Server
PORT=5000
NODE_ENV=development

# Frontend (Vite reads VITE_ prefixed vars)
VITE_API_BASE_URL=http://localhost:5000
VITE_IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_imagekit_id
```

> **Rule:** `.env` is in `.gitignore`. Never commit it. Copy `.env.example` (with blank values) to source control.

---

## DEV COMMANDS

```bash
# Backend
cd backend && npm install && npm run dev

# Frontend
cd frontend && npm install && npm run dev

# Backend runs on: http://localhost:5000
# Frontend runs on: http://localhost:5173
```
