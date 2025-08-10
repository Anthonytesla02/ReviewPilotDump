# PostgreSQL Database Dumper

## Overview

This is a Streamlit-based web application that provides a user-friendly interface for connecting to and exploring PostgreSQL databases. The application allows users to view database tables, analyze data statistics, and export data in various formats. It's designed as a database administration and data exploration tool with visualization capabilities using Plotly for charts and graphs.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Framework**: Uses Streamlit as the primary web framework for creating the user interface
- **Component Structure**: Modular design with separate files for database operations, utilities, and main application logic
- **Caching Strategy**: Implements Streamlit's `@st.cache_resource` decorator for database connection management to optimize performance
- **Layout Design**: Wide layout configuration with expandable sidebar for navigation and database overview

### Backend Architecture
- **Database Abstraction Layer**: `DatabaseManager` class handles all database operations and connection management
- **Connection Management**: Supports both `DATABASE_URL` environment variable and individual PostgreSQL connection parameters
- **Data Processing**: Pandas integration for data manipulation and analysis
- **Error Handling**: Comprehensive connection testing and error reporting

### Data Visualization
- **Plotly Integration**: Uses Plotly Express and Graph Objects for creating interactive charts and visualizations
- **Statistical Analysis**: Built-in column statistics calculation including type-specific metrics for numeric and string data
- **Export Capabilities**: Excel export functionality using openpyxl engine

### Configuration Management
- **Environment Variables**: Flexible configuration system supporting both `DATABASE_URL` and individual PostgreSQL parameters
- **Fallback Mechanism**: Graceful fallback to default values when environment variables are not set
- **Page Configuration**: Streamlit page settings with custom title, icon, and layout preferences

## External Dependencies

### Database
- **PostgreSQL**: Primary database system with psycopg2 driver for direct connections
- **SQLAlchemy**: ORM and database toolkit for connection management and query execution

### Data Processing & Analysis
- **Pandas**: Data manipulation and analysis library for handling database query results
- **NumPy**: Underlying numerical computing support (via pandas dependency)

### Web Framework & UI
- **Streamlit**: Primary web application framework for the user interface
- **Plotly**: Interactive visualization library for charts and graphs (plotly.express and plotly.graph_objects)

### File Processing
- **openpyxl**: Excel file format support for data export functionality
- **io**: Built-in Python library for handling byte streams and file operations

### Utilities
- **urllib.parse**: URL parsing for `DATABASE_URL` connection string handling
- **logging**: Application logging and debugging support
- **datetime**: Date and time handling utilities
- **json**: JSON data format support