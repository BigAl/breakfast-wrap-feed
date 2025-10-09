# Email Notifications Setup

The workflow is configured to send you an email if it fails.

## Setup Instructions

### 1. Create GitHub Secrets

Go to your repository **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these three secrets:

#### `EMAIL_USERNAME`
Your Gmail address (or other SMTP email)
```
example@gmail.com
```

#### `EMAIL_PASSWORD`
For Gmail, use an **App Password** (not your regular password):
1. Go to https://myaccount.google.com/apppasswords
2. Create a new app password for "GitHub Actions"
3. Copy the 16-character password
4. Paste it as the secret value

#### `NOTIFICATION_EMAIL`
The email address where you want to receive notifications
```
your-email@gmail.com
```

### 2. That's It!

The workflow will now send you an email if:
- The feed fetch fails
- The Python script crashes
- The git push fails
- Any step in the workflow fails

### Example Email

```
Subject: ❌ Breakfast Wrap Feed Update Failed

The Breakfast Wrap feed update workflow failed.

Repository: BigAl/breakfast-wrap-feed
Workflow: Update Breakfast Wrap Feed
Run: https://github.com/BigAl/breakfast-wrap-feed/actions/runs/12345

Please check the logs for details.
```

## Using a Different Email Provider

If you don't use Gmail, update the workflow file:

### Outlook/Hotmail
```yaml
server_address: smtp-mail.outlook.com
server_port: 587
```

### Yahoo
```yaml
server_address: smtp.mail.yahoo.com
server_port: 587
```

### Custom SMTP
```yaml
server_address: smtp.your-provider.com
server_port: 587  # or 465 for SSL
```

## Testing

To test the notification:
1. Temporarily break something in `filter_feed.py` (e.g., change the feed URL to invalid)
2. Push the change
3. Wait for the workflow to fail
4. Check your email

Then revert the change!

## Disabling Notifications

To disable email notifications, comment out or remove the "Send failure notification" step in `.github/workflows/update-feed.yml`.
