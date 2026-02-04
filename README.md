# Voice Sales Visit Tracker

A hands-free, voice-controlled web application for sales teams to capture customer visit information quickly and efficiently.

## Features

- 🎤 **Voice-Controlled Interface**: Speak your answers instead of typing
- 🗣️ **Text-to-Speech**: App asks questions out loud
- 📝 **Automatic Transcription**: Your voice responses are converted to text
- 📍 **GPS Location Capture**: Automatically records visit location
- 💾 **Centralized Database**: All visits stored in SQLite database
- 🔐 **Secure Authentication**: Login system for sales reps
- 👥 **Manager Tracking**: Each rep's manager email is saved for reporting

## How It Works

1. **Register/Login**: Sales reps create an account with their email and manager's email
2. **Voice Interview**: The app asks 6 questions about the customer visit:
   - Visit date
   - Customer company name
   - Contact person name
   - Meeting location
   - Discussion summary
   - Next steps
3. **Speak Answers**: Tap the microphone, speak your answer, then click "Done with Answer"
4. **Review & Submit**: Review the summary and submit to the database

## Technology Stack

- **Frontend**: React (single-page application)
- **Backend**: Python Flask REST API
- **Database**: SQLite (no external database needed)
- **Voice**: Web Speech API (Chrome/Edge supported)
- **Authentication**: Token-based sessions

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- Modern web browser (Chrome or Edge recommended for voice features)

### Step 1: Install Dependencies

```bash
cd sales-visit-app
pip install -r requirements.txt
```

### Step 2: Start the Server

```bash
python server.py
```

The server will start on `http://localhost:5000`

### Step 3: Access the App

Open your web browser and go to:
```
http://localhost:5000
```

## Deployment Options

### Option 1: Deploy to Cloud (Heroku)

1. Create a `Procfile`:
```
web: python server.py
```

2. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key-here
```

3. Deploy:
```bash
git init
heroku create your-app-name
git add .
git commit -m "Initial deployment"
git push heroku main
```

### Option 2: Deploy to AWS/Azure

1. Set up a virtual machine (EC2/Azure VM)
2. Install Python and dependencies
3. Run the server with:
```bash
python server.py
```

4. Configure reverse proxy (nginx) for production

### Option 3: Local Network Deployment

For internal company use:

1. Run the server on a local server/computer
2. Find your IP address: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
3. Share the URL with your team: `http://YOUR-IP:5000`

## Configuration

### Environment Variables

- `SECRET_KEY`: Secret key for session tokens (auto-generated if not set)
- `PORT`: Server port (default: 5000)

### Customizing Questions

Edit the `QUESTIONS` array in `index.html` (around line 375) to add/modify questions:

```javascript
const QUESTIONS = [
    {
        id: 'custom_field',
        text: 'Your question here?',
        hint: 'Guidance for the user',
        field: 'database_field_name'
    },
    // ... more questions
];
```

## Database

The app creates a `sales_visits.db` SQLite database with three tables:

- **users**: Sales rep information and credentials
- **sessions**: Authentication tokens
- **visits**: Customer visit records

### Accessing the Data

You can query the database directly using SQLite:

```bash
sqlite3 sales_visits.db

# View all visits
SELECT * FROM visits;

# View visits by rep
SELECT * FROM visits WHERE user_id = 1;

# Export to CSV
.mode csv
.output visits.csv
SELECT * FROM visits;
```

### Export to Excel/Google Sheets

Use the `/api/visits/all` endpoint to get all visits as JSON, then import into Excel or Google Sheets.

## Browser Compatibility

| Feature | Chrome | Edge | Safari | Firefox |
|---------|--------|------|--------|---------|
| Voice Recognition | ✅ | ✅ | ❌ | ❌ |
| Text-to-Speech | ✅ | ✅ | ✅ | ✅ |
| GPS Location | ✅ | ✅ | ✅ | ✅ |

**Recommendation**: Use Chrome or Edge for full voice functionality.

## Troubleshooting

### Voice Recognition Not Working

1. **Check browser**: Use Chrome or Edge
2. **Check permissions**: Allow microphone access when prompted
3. **Check HTTPS**: Voice API requires HTTPS in production (not localhost)

### Can't Hear Questions

1. Check device volume
2. Check browser audio permissions
3. Try clicking the mic button to trigger audio

### Location Not Captured

1. Allow location permissions when prompted
2. Location may take a few seconds to load
3. Check that location services are enabled on your device

## Security Considerations

For production deployment:

1. **Use HTTPS**: Required for microphone access
2. **Change SECRET_KEY**: Set a strong random secret key
3. **Add Rate Limiting**: Prevent brute force login attempts
4. **Database Backups**: Regularly backup `sales_visits.db`
5. **Password Strength**: Implement password requirements

## API Endpoints

### Authentication
- `POST /api/register` - Register new sales rep
- `POST /api/login` - Login existing user
- `GET /api/profile` - Get current user profile

### Visits
- `POST /api/visits` - Submit new visit
- `GET /api/visits` - Get current user's visits
- `GET /api/visits/all` - Get all visits (manager view)

## Future Enhancements

Potential features to add:

- Email notifications to managers when visits are submitted
- Dashboard for managers to view team activity
- Export visits to PDF reports
- Voice commands for navigation ("next question", "go back")
- Offline mode with sync when online
- Integration with CRM systems (Salesforce, HubSpot)
- Analytics and reporting dashboard

## Support

For issues or questions, contact your IT department or system administrator.

## License

Internal company use only.
