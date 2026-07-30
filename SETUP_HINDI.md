# Setup — Telegram + GitHub Version

## Step 1 — Bot banao
1. Telegram par `@BotFather` ko message karo
2. `/newbot` bhejo, naam do
3. Jo token mile (jaisa: `123456:ABC-xyz...`) — usko copy kar lo, kisi ko mat dikhao

## Step 2 — Repo banao
1. Yeh saari files ek naye **public** GitHub repo mein daal do
2. Repo → Settings → Secrets and variables → Actions → **New repository secret**
3. Name: `TELEGRAM_BOT_TOKEN`
4. Value: apna bot token paste karo
5. Save

## Step 3 — Chalao
1. Repo → **Actions** tab → left side "Telegram Scraper" workflow par click karo
2. "Run workflow" button se ek baar manually chala kar test karo (yeh confirm karega sab set hai)
3. Fir Telegram par apne bot ko message bhejo:
   ```
   /scrape
   Kabir Das dohas
   Tulsidas Ramcharitmanas
   ```
4. Agla scheduled run (10 minute ke andar) topic utha lega, scrape karega, aur result files (JSON/CSV/PDF) wapas Telegram par bhej dega

## Zaroori baatein
- Ek run mein 6 ghante ki hard limit hai — agar bahut saare topics ek saath bheje to results der se ya adhoore aa sakte hain. 15-20 topics se zyada ek saath mat bhejo.
- Repo public rehne se Actions minutes bilkul free/unlimited hain
- `data/` folder repo mein commit nahi hota (`.gitignore` mein hai) — result sirf Telegram par milega
