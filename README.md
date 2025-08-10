# PostgreSQL Database Dumper

A Streamlit-based web application that provides a user-friendly interface for connecting to and exploring PostgreSQL databases. The application allows users to view database tables, analyze data statistics, and export data in various formats.

## Features

- **Dual Database Support**: Connect to both external databases and local Replit databases
- **Interactive Data Exploration**: Browse tables with pagination, search, and filtering
- **Data Export**: Export data in CSV, JSON, and Excel formats
- **Data Visualization**: Interactive charts and statistics for numeric data
- **Schema Analysis**: View database relationships and table structures
- **Real-time Statistics**: Column statistics and data type information

## Deployment on Vercel

### Prerequisites

1. A Vercel account
2. Access to your PostgreSQL database

### Deployment Steps

1. **Fork or Clone this repository**

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your repository
   - Vercel will automatically detect the configuration

3. **Set Environment Variables** (if using Replit database)
   In your Vercel dashboard, add these environment variables:
   ```
   DATABASE_URL=your_postgresql_connection_string
   PGHOST=your_host
   PGPORT=5432
   PGDATABASE=your_database_name
   PGUSER=your_username
   PGPASSWORD=your_password
   ```

4. **Deploy**
   - Click "Deploy" in Vercel
   - Your app will be available at `https://your-app-name.vercel.app`

### Files for Vercel Deployment

- `vercel.json` - Vercel configuration
- `requirements_vercel.txt` - Python dependencies
- `streamlit_app.py` - Main application entry point
- `runtime.txt` - Python version specification
- `Procfile` - Process configuration
- `setup.sh` - Streamlit setup script

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements_vercel.txt
   ```

2. Run the application:
   ```bash
   streamlit run streamlit_app.py
   ```

3. Open your browser to `http://localhost:8501`

## Database Configuration

The application supports two database connection modes:

1. **External Database** (default): Uses the ReviewPilot database URL configured in the code
2. **Replit Database**: Uses environment variables for local development

You can switch between these options using the radio buttons in the application interface.

## Technical Stack

- **Frontend**: Streamlit
- **Database**: PostgreSQL with SQLAlchemy
- **Data Processing**: Pandas
- **Visualization**: Plotly
- **Export**: openpyxl for Excel files

## Security Notes

- Database credentials are handled securely through environment variables
- The application includes read-only database operations for safety
- No destructive SQL operations are exposed in the interface

## Support

For deployment issues:
- Check Vercel deployment logs
- Ensure all environment variables are set correctly
- Verify database connectivity from your deployment environment