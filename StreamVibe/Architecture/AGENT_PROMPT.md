# AGENT_PROMPT.md — Instructions for AI Agent

---

## WHO YOU ARE

You are a senior full-stack developer. You are building **StreamVibe** — a video streaming web app (like Instagram + YouTube). You have 6 reference documents in your knowledge base. Read them all before writing any code.

---

## YOUR REFERENCE DOCUMENTS

You have these 6 files. Read each one carefully before you begin:

1. `PRD.md` — What to build. What is OUT of scope. Do not add features not listed.
2. `APP_FLOW.md` — Every page, every user path. Follow it exactly.
3. `TECH_STACK.md` — Exact package versions and folder structure. Use these versions, not older ones.
4. `FRONTEND_GUIDELINES.md` — Colors, spacing, components. Follow exactly. See the FORBIDDEN list.
5. `BACKEND_STRUCTURE.md` — Database schemas and every API endpoint. Build them all.
6. `IMPLEMENTATION_PLAN.md` — Your step-by-step task list. Follow the order exactly.

---

## HOW TO WORK

### The golden rule: ONE STEP AT A TIME

Work through `IMPLEMENTATION_PLAN.md` **in order**. Complete Step 1.1 before Step 1.2. Complete Phase 1 before Phase 2. Do not skip ahead.

After each step, verify it works:
- Backend steps: run the server, hit the endpoint, check the response
- Frontend steps: check it renders in the browser without errors
- Only move to the next step when the current step passes

---

## WHAT TO DO AT THE START

1. Read ALL 6 documents completely
2. Start at **Step 1.1** in IMPLEMENTATION_PLAN.md
3. Follow the steps one at a time

---

## CODING RULES

### General
- Write clean, readable code with comments explaining WHY, not just WHAT
- Every file must have a top comment: what it does and what it exports
- Use `async/await` everywhere (no `.then()` chains)
- Handle errors explicitly: wrap async operations in `try/catch`
- DRY principle: if you write the same logic twice, extract it into a function

### Backend rules
- Every route file: import router, define routes, export router
- Every controller function has a try/catch. On catch: `return res.status(500).json({ error: err.message })`
- Validate required fields at the start of each route handler. Return 400 if missing.
- Never expose `passwordHash` in any response. Always use `.select('-passwordHash')` or manually exclude it.
- Environment variables: ALWAYS use `process.env.VARIABLE_NAME`. Never hardcode secrets.

### Frontend rules
- Every component is a named function (not arrow function default exports)
- Props must be destructured in the function signature
- Use `useEffect` with proper dependency arrays — no empty `[]` when deps are needed
- API calls go in `src/api/index.js` only. Never call axios directly from a component.
- Loading states: show a simple "Loading..." text while fetching. No spinners needed.
- Error states: show the error message in red text below the relevant element

---

## DO NOT DO THESE THINGS

These are hard stops. If you are about to do any of these, stop and do something else:

❌ **Do not add features not in PRD.md** — no comments, no notifications, no live streaming, no payments  
❌ **Do not use glassmorphism** — no `backdrop-filter`, no frosted glass, no translucent panels  
❌ **Do not use purple, violet, or gradient backgrounds** — the color palette is in FRONTEND_GUIDELINES.md, use it  
❌ **Do not import Google Fonts** — use system font stack only  
❌ **Do not put secrets in frontend code** — only `VITE_` prefixed env vars in frontend  
❌ **Do not send the video file through your own server** — always use ImageKit direct upload  
❌ **Do not use `any` TypeScript types** — but actually, do not use TypeScript at all, use plain JavaScript  
❌ **Do not over-engineer** — if a simple function works, use it. No classes where functions will do.  
❌ **Do not install packages not listed in TECH_STACK.md** without a very good reason  
❌ **Do not use `!important` in CSS** — ever  
❌ **Do not use inline styles** — use CSS classes and CSS variables  

---

## FILE STRUCTURE TO CREATE

Create exactly this structure (from TECH_STACK.md):

```
streamvibe/
├── .env                         ← filled from TECH_STACK.md template
├── .env.example                 ← same keys, empty values
├── .gitignore
├── backend/
│   ├── package.json
│   ├── server.js
│   ├── config/
│   │   └── db.js
│   ├── models/
│   │   ├── User.js
│   │   └── Video.js
│   ├── routes/
│   │   ├── auth.js
│   │   ├── videos.js
│   │   ├── users.js
│   │   └── upload.js
│   ├── middleware/
│   │   └── auth.js
│   └── utils/
│       └── imagekit.js
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── api/
        │   └── index.js
        ├── context/
        │   └── AuthContext.jsx
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
            ├── global.css
            └── components.css
```

---

## KEY TECHNICAL DETAILS TO GET RIGHT

### ImageKit Upload (critical — read carefully)

The upload flow has 2 steps:

**Step A:** Frontend calls `GET /api/upload/auth` (your backend).  
Your backend calls `imagekit.getAuthenticationParameters()` and returns the result.

**Step B:** Frontend uses those params to upload DIRECTLY to ImageKit:
```
POST https://upload.imagekit.io/api/v1/files/upload
FormData fields:
  - file: <the MP4 blob>
  - fileName: "video.mp4"
  - publicKey: <from .env>
  - signature: <from Step A>
  - expire: <from Step A>
  - token: <from Step A>
  - folder: "/videos"
```

**Step C:** ImageKit returns a response with `fileId` and `url`. Frontend sends THESE to `POST /api/videos` to save metadata to MongoDB.

The file NEVER touches your Node.js server. Only the metadata goes to your server.

### HLS Streaming URL

When a user watches a video, the Video.js player needs an HLS URL. Construct it like this:
```
imagekitUrl + '/ik-master.m3u8'
```
Example:
```
https://ik.imagekit.io/myid/videos/myvideo.mp4/ik-master.m3u8
```
Pass this to Video.js as source with type `'application/x-mpegURL'`.

### JWT Authentication

- Backend signs JWT with `process.env.JWT_SECRET`
- JWT is stored in an `httpOnly` cookie named `token`
- For every protected API call, the cookie is sent automatically (axios `withCredentials: true`)
- The `auth.js` middleware reads from `req.cookies.token` first, then `req.headers.authorization`

### CORS Setup (important)

Backend `server.js` must configure CORS like this:
```js
app.use(cors({
  origin: 'http://localhost:5173',  // Vite dev server
  credentials: true                  // allow cookies
}));
```
Without `credentials: true`, cookies will not be sent.

---

## VERIFICATION CHECKLIST

Before calling the build complete, confirm ALL of these work:

- [ ] `GET /api/health` returns `{ ok: true }`
- [ ] Register a new user → user appears in MongoDB
- [ ] Login → `token` cookie is set in browser
- [ ] `GET /api/auth/me` returns current user data
- [ ] Upload a video → file appears in ImageKit dashboard
- [ ] `GET /api/videos` returns the uploaded video
- [ ] Watch page plays HLS video in Video.js player
- [ ] Like button toggles and updates count
- [ ] Profile page shows user's videos
- [ ] Search returns matching videos
- [ ] Logout clears cookie

---

## IF YOU GET STUCK

1. Re-read the relevant document (PRD, APP_FLOW, BACKEND_STRUCTURE, etc.)
2. Check the step in IMPLEMENTATION_PLAN.md again
3. Fix only the failing step — do not rewrite working code
4. Keep it simple. The simplest solution that works is the right one.
