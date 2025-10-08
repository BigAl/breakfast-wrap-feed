# Schedule Explanation

## Current Schedule

**Weekdays at 00:05 UTC** (`5 0 * * 1-5`)

## Why This Schedule?

ABC publishes Breakfast Wrap episodes at **10:00 AM Australian Eastern Time**, which converts to:

- **AEST (Apr-Oct):** 00:00 UTC same day
- **AEDT (Oct-Apr):** 23:00 UTC previous day

### The 5-Minute Buffer

The workflow runs at 00:05 UTC to allow a 5-minute buffer after the expected publication time (00:00 UTC during Australian Standard Time).

### Weekdays Only

Breakfast Wrap is published **Monday-Friday only**, so the schedule uses `1-5` (Mon-Fri) to avoid unnecessary weekend runs.

## Important: Daylight Saving Time

⚠️ **During Australian DST (Oct-April)**, episodes are published at **23:00 UTC the previous day**.

This means:
- **Monday's episode** (10am AEDT): Published Sunday 23:00 UTC
- **Tuesday's episode** (10am AEDT): Published Monday 23:00 UTC
- etc.

### Handling DST

**Option 1: Current Schedule (00:05 UTC weekdays)**
- ✅ Works perfectly Apr-Oct (AEST)
- ⚠️ During Oct-Apr (AEDT): Runs ~1 hour after publication (still fine!)
- Episodes published Sun 23:00 UTC are caught Mon 00:05 UTC

**Option 2: More Conservative (01:00 UTC daily)**
- ✅ Works year-round regardless of DST
- ✅ Always runs well after publication
- ⚠️ Slightly longer delay (~1 hour)
- Change cron to: `0 1 * * *`

**Option 3: Two Daily Runs (handles both scenarios)**
- Run at 23:05 UTC (catches AEDT publications)
- Run at 00:05 UTC (catches AEST publications)
- Change cron to: `5 23,0 * * 1-5`

## Recommendation

The current schedule (`5 0 * * 1-5`) is optimal for:
- **Speed:** Minimal delay after publication
- **Efficiency:** Only runs weekdays
- **Simplicity:** Single daily run

The ~1 hour delay during DST is negligible for podcast consumption.

If you want guaranteed consistency year-round, switch to `0 1 * * *` (daily at 01:00 UTC).

## How to Change

Edit `.github/workflows/update-feed.yml`:

```yaml
schedule:
  # Current (optimized for AEST, slight delay during AEDT)
  - cron: '5 0 * * 1-5'

  # Conservative (always works, slightly longer delay)
  # - cron: '0 1 * * *'

  # Covers both AEST and AEDT (twice daily)
  # - cron: '5 23,0 * * 1-5'
```

Then commit and push the change.
