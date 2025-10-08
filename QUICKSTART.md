# Serverless Quick Start

## 5-Minute Setup

### Step 1: Create GitHub Repository (2 min)

1. Go to https://github.com/new
2. Name: `breakfast-wrap-feed`
3. ✅ Make it **PUBLIC**
4. ✅ Check "Add a README file"
5. Click "Create repository"

### Step 2: Upload Files (1 min)

In your new repository:

1. Click "Add file" → "Create new file"
2. Type `.github/workflows/update-feed.yml` in filename box
3. Paste contents from `serverless/.github/workflows/update-feed.yml`
4. Click "Commit new file"

Repeat for:
- `filter_feed.py` (from `serverless/filter_feed.py`)
- `breakfast-wrap.xml` (from `serverless/breakfast-wrap.xml`)

**OR** use git:
```bash
cd /home/alan/Source/Breakfast/serverless
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/breakfast-wrap-feed.git
git push -u origin main
```

### Step 3: Enable GitHub Pages (1 min)

1. Go to repo **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** / **/ (root)**
4. Click **Save**

### Step 4: Trigger First Run (30 sec)

1. Go to **Actions** tab
2. Click "Update Breakfast Wrap Feed"
3. Click "Run workflow" → "Run workflow"

Watch it run (takes ~30 seconds)

### Step 5: Get Your Feed URL (30 sec)

Your feed is now at:
```
https://YOUR_USERNAME.github.io/breakfast-wrap-feed/breakfast-wrap.xml
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 6: Add to PocketCast

1. Open PocketCast
2. Discover → Enter URL
3. Paste your feed URL
4. Subscribe

**Done!** 🎉

---

## What Happens Now?

- Workflow runs **weekdays at 00:05 UTC** (5 min after ABC publishes at 10am AEST/AEDT)
- Fetches ABC feed
- Filters for "Breakfast Wrap" episodes
- Updates your feed within minutes of publication
- PocketCast downloads episodes directly from ABC

**Note:** During Australian DST (Oct-Apr), there's a ~1 hour delay. See `SCHEDULE_NOTE.md` for details.

## Check It's Working

1. Visit your feed URL in a browser
2. Go to repo **Actions** tab to see workflow runs
3. Click latest run to see logs showing episodes found

## Troubleshooting

**Feed shows placeholder content?**
- Wait for first workflow run to complete
- Check Actions tab for any errors

**Can't access feed URL?**
- Wait 2-3 minutes after enabling Pages
- Ensure repository is PUBLIC
- Check Settings → Pages shows site is published

**No episodes in feed?**
- Check Actions → Latest run → View logs
- Verify "Found: ..." lines showing episodes
- Filter keyword might need adjustment

---

That's it! Enjoy your filtered podcast feed with zero infrastructure! 🚀
