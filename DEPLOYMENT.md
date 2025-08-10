# Deployment Guide for Vercel

## Important: Flask-Based Solution

Due to Streamlit's incompatibility with Vercel's serverless functions, I've created a Flask-based web interface that provides the same functionality. The Flask app is fully compatible with Vercel deployment.

## Quick Deploy

1. **Connect Repository to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import this repository

2. **Configure Environment Variables**
   If you want to use a different database than the default ReviewPilot one, add these in Vercel:
   ```
   DATABASE_URL=your_postgresql_connection_string
   ```

3. **Deploy**
   - Vercel will automatically detect the Flask app and deploy using the configuration in `vercel.json`
   - Your app will be live at `https://your-project-name.vercel.app`

## Files Created for Deployment

- `vercel.json` - Vercel build configuration for Flask
- `requirements.txt` - Python dependencies with Flask
- `api/index.py` - Vercel serverless function entry point
- `streamlit_app.py` - Flask web application (renamed for clarity)
- `runtime.txt` - Python version specification
- `Procfile` - Process configuration for other platforms

## Flask App Features

The Flask version includes:
- ✅ Same database connectivity (ReviewPilot + Replit databases)
- ✅ Interactive table browser with pagination
- ✅ Data export (CSV, JSON, Excel)
- ✅ Bootstrap-styled responsive interface
- ✅ Real-time database connection status
- ✅ Table statistics and row counts

## Testing Deployment Locally

Run this command to test the Flask app locally:
```bash
python streamlit_app.py
```
Then visit `http://localhost:5000`

## Alternative Deployment Platforms

The app is ready for:
- **Vercel**: Primary recommendation (uses Flask)
- **Heroku**: Uses `Procfile` and works with Flask
- **Railway**: Compatible with Flask configuration
- **Render**: Works with Flask setup
- **Streamlit Cloud**: Use the original `app.py` for Streamlit-specific deployment

## Why Flask Instead of Streamlit for Vercel?

- Streamlit requires a persistent web server, incompatible with Vercel's serverless functions
- Flask provides the same functionality in a serverless-compatible format
- Better performance on Vercel's infrastructure
- More reliable deployment process

## Database Configuration

The app defaults to the ReviewPilot database but can be switched to use environment variables for other databases. Users can toggle between database sources in the web interface.