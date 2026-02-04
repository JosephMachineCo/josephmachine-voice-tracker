# Joseph Machine Voice Visit Tracker - Deployment Guide

## 🚀 Quick Start (Local Testing)

1. Install Python dependencies:
```bash
pip install Flask Flask-CORS
```

2. Start the server:
```bash
python server.py
```

3. Open in Chrome or Edge:
```
http://localhost:5000
```

## 🌐 Deploy to the Web (Free Options)

### Option 1: Render.com (Recommended - Easiest)

**Steps:**
1. Go to https://render.com and sign up (free)
2. Click "New +" → "Web Service"
3. Connect your GitHub account (or upload files)
4. Fill in:
   - **Name**: josephmachine-visits
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
5. Click "Create Web Service"
6. Your app will be live at: `https://josephmachine-visits.onrender.com`

**Pros:**
- Completely free
- Auto-deploys on code changes
- Provides HTTPS (required for voice features)

---

### Option 2: Railway.app (Very Easy)

**Steps:**
1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub" or "Empty Project"
4. Upload your files
5. Railway auto-detects Python and deploys
6. Your app will be live immediately

**Pros:**
- Extremely simple
- Free tier is generous
- Fast deployment

---

### Option 3: PythonAnywhere (Traditional)

**Steps:**
1. Sign up at https://www.pythonanywhere.com (free account)
2. Go to "Web" tab → "Add a new web app"
3. Choose "Flask" framework
4. Upload your files using "Files" tab
5. Configure WSGI file to point to your `server.py`
6. Reload web app

**Your URL**: `http://yourusername.pythonanywhere.com`

---

### Option 4: Fly.io (Advanced but Free)

**Steps:**
1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Create `fly.toml`:
```toml
app = "josephmachine-visits"

[build]
  builder = "paketobuildpacks/builder:base"

[[services]]
  internal_port = 5000
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

3. Deploy:
```bash
fly launch
fly deploy
```

---

## 🔐 Important: HTTPS Required

Voice recognition (Web Speech API) **requires HTTPS** in production. All the deployment options above provide free HTTPS certificates automatically.

If deploying to your own server, you MUST use HTTPS. Use Let's Encrypt for free SSL certificates.

---

## 📱 Share with Your Team

Once deployed, share the URL with your sales team:

**Example URLs:**
- Render: `https://josephmachine-visits.onrender.com`
- Railway: `https://josephmachine-visits.up.railway.app`
- Fly.io: `https://josephmachine-visits.fly.dev`

They can:
1. Open the URL on their phone or computer (Chrome/Edge)
2. Register with their email and manager's email
3. Start recording visits with voice!

---

## 🎯 Browser Requirements

| Browser | Voice Input | Works On |
|---------|-------------|----------|
| **Chrome** | ✅ Full Support | Desktop, Android |
| **Edge** | ✅ Full Support | Desktop, Android |
| **Safari** | ❌ No Voice | iOS, Mac |
| **Firefox** | ❌ No Voice | All Platforms |

**Recommendation:** Tell your team to use Chrome or Edge for best experience.

---

## 🗄️ Database Management

The app uses SQLite (`sales_visits.db` file). To access data:

### View All Visits
```bash
sqlite3 sales_visits.db
SELECT * FROM visits;
```

### Export to CSV
```bash
sqlite3 sales_visits.db <<EOF
.headers on
.mode csv
.output visits_export.csv
SELECT
    u.full_name as sales_rep,
    u.email as rep_email,
    u.manager_email,
    v.visit_date,
    v.customer_name,
    v.contact_name,
    v.location,
    v.discussion_summary,
    v.next_steps,
    v.created_at
FROM visits v
JOIN users u ON v.user_id = u.id
ORDER BY v.visit_date DESC;
.quit
EOF
```

### Download Database (Render.com)
1. Go to your service dashboard
2. Click "Shell" tab
3. Run: `cat sales_visits.db | base64` (copy output)
4. Decode locally: `echo "BASE64_STRING" | base64 -d > sales_visits.db`

---

## 🔧 Environment Variables

For production, set these in your hosting platform:

- `SECRET_KEY` - Random string for session security (auto-generated if not set)
- `PORT` - Port number (usually auto-set by platform)

**Example (Render.com):**
1. Go to Environment tab
2. Add: `SECRET_KEY = your-random-secret-key-here`

---

## 📊 Accessing Visit Data via API

Your managers can view all visits:

```bash
# Get authentication token first (after login)
curl -X POST https://your-app-url.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"manager@josephmachine.com","password":"password"}'

# Use token to get all visits
curl https://your-app-url.com/api/visits/all \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

This returns JSON data you can import into Excel, Google Sheets, or a dashboard.

---

## 🎨 Customization

### Change Questions
Edit `index.html` around line 512:

```javascript
const QUESTIONS = [
    {
        id: 'custom_field',
        text: 'Your question here?',
        hint: 'Help text for the user',
        field: 'database_field_name'
    },
    // Add more questions...
];
```

### Change Colors
Edit CSS variables in `index.html` around line 20:

```css
:root {
    --joseph-blue: #2563EB;  /* Primary color */
    --joseph-red: #DC2626;   /* Accent color */
    --joseph-dark: #1E3A8A;  /* Dark variant */
}
```

---

## 🐛 Troubleshooting

### "Speech recognition not supported"
- Use Chrome or Edge browser
- Ensure you're on HTTPS (not HTTP)
- Check browser permissions for microphone

### "Network error"
- Check if server is running
- Verify API_URL is correct
- Check browser console for errors

### Can't hear questions
- Check device volume
- Allow browser audio permissions
- Try different browser

### Database locked
- Only one process should write at a time
- Consider upgrading to PostgreSQL for multi-user

---

## 📈 Next Steps

After deployment:

1. **Test the app** yourself first
2. **Register a test account** with your email
3. **Record a sample visit** to verify everything works
4. **Check the database** to see data was saved
5. **Share URL with one sales rep** for beta testing
6. **Get feedback** and iterate
7. **Roll out to entire team**

---

## 💡 Tips for Success

- **Training**: Do a 15-minute team demo showing voice features
- **Quiet environment**: Voice works best without background noise
- **Clear speech**: Speak clearly and at normal pace
- **Mobile-friendly**: Works great on phones (Chrome Android)
- **Backup plan**: If voice fails, they can type (future feature)

---

## 📞 Support

For technical issues:
- Check browser console (F12)
- Test on different device/browser
- Verify HTTPS is enabled
- Check microphone permissions

---

## 🔒 Security Notes

- Passwords are hashed (SHA-256)
- Sessions expire after 30 days
- Use HTTPS in production (included in all deployment options)
- Set strong SECRET_KEY environment variable
- Regularly backup `sales_visits.db`

---

## 🎉 You're Ready!

Choose your deployment option above and get started. Render.com is recommended for the easiest setup.

Good luck! 🚀
