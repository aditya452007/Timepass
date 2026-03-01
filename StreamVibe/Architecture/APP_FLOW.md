# APP_FLOW.md — All Pages & User Paths

---

## PAGES

```
/                     → Home Feed (public)
/login                → Login Page
/register             → Register Page
/upload               → Upload Page (auth required)
/watch/:videoId       → Video Player Page (public)
/profile/:username    → User Profile Page (public)
/search?q=...         → Search Results Page (public)
```

---

## PAGE-BY-PAGE BREAKDOWN

---

### `/` — Home Feed

**What's on screen:**
- Top navbar: Logo | Search bar | [Upload] button | [Login/Register] or [Avatar/Logout]
- Grid of video cards (3 columns desktop, 1 column mobile)
- Each card: thumbnail image, video title, username, view count
- "Load More" button at the bottom (or auto-infinite scroll)

**User paths:**
- Click any video card → go to `/watch/:videoId`
- Click username on card → go to `/profile/:username`
- Click Upload button (logged in) → go to `/upload`
- Click Upload button (not logged in) → redirect to `/login`
- Type in search bar + press Enter → go to `/search?q=...`

---

### `/login` — Login Page

**What's on screen:**
- Email input
- Password input
- "Login" button
- Link: "Don't have an account? Register"

**User paths:**
- Submit valid credentials → JWT cookie set → redirect to `/`
- Submit invalid credentials → show error message inline
- Click Register link → go to `/register`

---

### `/register` — Register Page

**What's on screen:**
- Username input
- Email input
- Password input
- "Register" button
- Link: "Already have an account? Login"

**User paths:**
- Submit valid form → account created → auto-login → redirect to `/`
- Submit with existing email → show error: "Email already in use"
- Click Login link → go to `/login`

---

### `/upload` — Upload Video Page (REQUIRES LOGIN)

**What's on screen:**
- File picker (accepts `.mp4` only)
- Title input (required)
- Description textarea (optional)
- Tags input (comma separated, optional)
- "Upload" button
- Upload progress bar (appears after submit)
- Success message with link to the new video

**User flow:**
1. User picks MP4 file
2. User fills title
3. User clicks Upload
4. Frontend calls `GET /api/upload/auth` to get ImageKit auth params
5. Frontend uploads file directly to ImageKit.io
6. On ImageKit success, frontend calls `POST /api/videos` with metadata + ImageKit fileId + URL
7. Progress bar fills → show "Upload complete!" + "Watch your video" link
8. Error: show error message, keep form data intact

---

### `/watch/:videoId` — Video Player Page

**What's on screen:**
- Video.js player at the top (16:9 aspect ratio)
- Video title (large)
- Username (clickable → profile)
- View count + Like button (heart icon + count)
- Description text
- Tags shown as chips

**User flow:**
- On page load: fetch video metadata, increment view count by 1
- Video player loads the ImageKit `.m3u8` HLS URL
- Click Like (logged in): toggle like, update count optimistically
- Click Like (not logged in): redirect to `/login`
- Click username: go to `/profile/:username`

---

### `/profile/:username` — User Profile Page

**What's on screen:**
- Username + avatar (initials fallback)
- Follower count | Following count
- Follow / Unfollow button (hidden if viewing own profile)
- Grid of that user's uploaded videos

**User flow:**
- Click a video card → `/watch/:videoId`
- Click Follow (logged in): follow user, count increments
- Click Follow (not logged in): redirect to `/login`
- Viewing own profile: no Follow button, "Edit Profile" placeholder (disabled/TODO)

---

### `/search?q=...` — Search Results Page

**What's on screen:**
- Search bar (pre-filled with query)
- Results: same video card grid as home feed
- "No results found" empty state if nothing matches

**User flow:**
- Same as home feed card interactions
- Submit new search → updates URL and re-fetches

---

## NAVIGATION RULES

- Navbar is present on ALL pages
- If user is logged in: show avatar (initials) + Logout button
- If user is not logged in: show Login + Register buttons
- Clicking logo always goes to `/`
- Auth pages (`/login`, `/register`) redirect to `/` if already logged in

---

## AUTH GUARD

Pages that require login:
- `/upload` — redirect to `/login?next=/upload` if not authenticated

All other pages are public (read-only access without login).
