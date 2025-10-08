# Serverless Breakfast Wrap Feed Filter

**100% serverless, 100% free, zero infrastructure!**

This solution uses GitHub Actions to automatically filter the ABC News Daily podcast feed every hour and publish only "Breakfast Wrap" episodes.

## How It Works

```
GitHub Actions (runs hourly)
  ↓
Fetches ABC feed
  ↓
Filters for "Breakfast Wrap"
  ↓
Commits breakfast-wrap.xml to repo
  ↓
GitHub Pages serves the file
  ↓
PocketCast reads the feed
  ↓
Downloads audio directly from ABC
```

**No servers, no NAS, no docker containers needed!**

## Setup (5 minutes)

### 1. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `breakfast-wrap-feed` (or any name)
3. **Make it PUBLIC** (required for free GitHub Pages)
4. ✅ Check "Add a README file"
5. Click "Create repository"

### 2. Upload Files

Upload these files to your new repository:
- `.github/workflows/update-feed.yml`
- `filter_feed.py`

You can do this via:

**Option A: Web UI**
- Click "Add file" → "Upload files"
- Drag and drop the files
- Commit

**Option B: Command line**
```bash
cd serverless
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/breakfast-wrap-feed.git
git push -u origin main
```

### 3. Enable GitHub Pages

1. Go to your repo Settings → Pages
2. Source: "Deploy from a branch"
3. Branch: `main` / `/ (root)`
4. Click Save

### 4. Trigger First Run

**Option A: Wait for next hour**
- The workflow runs automatically every hour

**Option B: Manual trigger**
1. Go to "Actions" tab in your repo
2. Click "Update Breakfast Wrap Feed"
3. Click "Run workflow" → "Run workflow"

### 5. Get Your Feed URL

After the first run completes, your feed will be at:

```
https://YOUR_USERNAME.github.io/breakfast-wrap-feed/breakfast-wrap.xml
```

### 6. Add to PocketCast

1. Open PocketCast
2. Discover → Search → Enter URL
3. Paste: `https://YOUR_USERNAME.github.io/breakfast-wrap-feed/breakfast-wrap.xml`
4. Subscribe

Done! 🎉

## Features

- ✅ Runs automatically weekdays at 00:05 UTC (5 min after ABC's 10am AEST/AEDT publication)
- ✅ Completely free (GitHub Actions: 2000 min/month free)
- ✅ No infrastructure to maintain
- ✅ No NAS, docker, or servers needed
- ✅ Audio files stream directly from ABC
- ✅ Works from anywhere (not dependent on home network)
- ✅ Automatic updates forever

## Monitoring

### View Workflow Runs

Go to your repo → "Actions" tab to see:
- When it last ran
- Whether it succeeded
- How many episodes were found
- Any errors

### Check Your Feed

Visit your feed URL in a browser to see the XML:
```
https://YOUR_USERNAME.github.io/breakfast-wrap-feed/breakfast-wrap.xml
```

## Configuration

### Change Update Frequency

The default schedule runs weekdays at 00:05 UTC, optimized for ABC's publication time (10am Australian Eastern Time = ~00:00 UTC with 5-minute buffer).

Edit `.github/workflows/update-feed.yml`:

```yaml
schedule:
  - cron: '5 0 * * 1-5'  # Weekdays 00:05 UTC (default - optimized!)
  # - cron: '5 0 * * *'  # Daily 00:05 UTC (if you want weekends too)
  # - cron: '0 1 * * *'  # Once daily at 01:00 UTC (safer buffer)
  # - cron: '0 */6 * * *'  # Every 6 hours (fallback option)
```

**Note:** Breakfast Wrap is published weekdays at 10am AEST/AEDT (00:00 UTC), so running weekdays with a 5-minute buffer is optimal!

### Change Filter Keyword

Edit `filter_feed.py`:

```python
FILTER_KEYWORD = "Breakfast Wrap"  # Change this
```

### Change Maximum Episodes

Edit `filter_feed.py`:

```python
MAX_EPISODES = 50  # Change this
```

## Troubleshooting

### Workflow not running

- Check Actions tab for errors
- Ensure repository is public
- Verify workflow file is in `.github/workflows/`

### Feed is empty

- Check Actions tab → Latest run → View logs
- Look for "Found: ..." in the output
- Verify the filter keyword matches episode titles

### Can't access feed URL

- Wait 2-3 minutes after enabling GitHub Pages
- Ensure repository is public
- Check Settings → Pages shows "Your site is published at..."

### Feed not updating

- Check Actions tab → verify runs are succeeding
- GitHub Actions may be delayed during high usage
- Manually trigger a run to test

## Manual Trigger

To update the feed immediately:

1. Go to Actions tab
2. Select "Update Breakfast Wrap Feed"
3. Click "Run workflow"
4. Click green "Run workflow" button

## Privacy

- This uses a **public** GitHub repository
- Anyone can see your feed file
- Episode metadata is public (from ABC)
- Audio files are hosted by ABC (not re-uploaded)
- PocketCast downloads directly from ABC servers

## Costs

**FREE tier includes:**
- 2000 GitHub Actions minutes/month
- This workflow uses ~1 minute per run
- Running weekdays only = ~20-22 runs/month
- **Well within free tier!** (uses only 1% of quota)

## Stopping the Feed

To stop updates:

1. Go to `.github/workflows/update-feed.yml`
2. Delete the `schedule:` section
3. Commit

The feed file will remain accessible but won't update.

## Credits

- Original feed: [ABC Radio National Breakfast](https://www.abc.net.au/listen/programs/radionational-breakfast/) ([RSS Feed](https://www.abc.net.au/feeds/2890360/podcast.xml))
- Filtering: Python + [feedparser](https://github.com/kurtmckee/feedparser)
- Hosting: GitHub Pages
- Automation: GitHub Actions
