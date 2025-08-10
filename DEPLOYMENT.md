# Deployment Guide for Vercel

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
   - Vercel will automatically build and deploy using the configuration in `vercel.json`
   - Your app will be live at `https://your-project-name.vercel.app`

## Files Created for Deployment

- `vercel.json` - Vercel build configuration
- `requirements_vercel.txt` - Python dependencies list
- `streamlit_app.py` - Entry point for Vercel
- `runtime.txt` - Python version specification
- `Procfile` - Process configuration (backup for other platforms)
- `setup.sh` - Streamlit configuration script

## Testing Deployment Locally

Run this command to test the Vercel deployment setup:
```bash
streamlit run streamlit_app.py --server.port 8501
```

## Alternative Deployment Platforms

The app is also ready for:
- **Heroku**: Uses `Procfile` and `requirements_vercel.txt`
- **Railway**: Compatible with the current configuration
- **Render**: Works with the Streamlit setup
- **Streamlit Cloud**: Can deploy directly from GitHub

## Database Configuration

The app defaults to the ReviewPilot database but can be switched to use environment variables for other databases. Users can toggle between database sources in the application interface.