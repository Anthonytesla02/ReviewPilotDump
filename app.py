import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import json
from database import DatabaseManager
from utils import format_bytes, get_column_stats, export_to_excel

# Page configuration
st.set_page_config(
    page_title="PostgreSQL Database Dumper",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database manager
@st.cache_resource
def init_database():
    return DatabaseManager()

def main():
    st.title("🗄️ PostgreSQL Database Dumper")
    st.markdown("---")
    
    # Initialize database connection
    db_manager = init_database()
    
    # Check connection status
    if not db_manager.test_connection():
        st.error("❌ Failed to connect to database. Please check your connection settings.")
        st.stop()
    
    st.success("✅ Connected to database successfully!")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    
    # Get all tables
    tables = db_manager.get_all_tables()
    
    if not tables:
        st.warning("No tables found in the database.")
        return
    
    # Database overview section
    st.sidebar.subheader("Database Overview")
    st.sidebar.info(f"📊 Total Tables: {len(tables)}")
    
    # Table selection
    st.sidebar.subheader("Select Table")
    selected_table = st.sidebar.selectbox("Choose a table to explore:", tables)
    
    # Main content area
    if selected_table:
        display_table_content(db_manager, selected_table)
    
    # Database schema section
    st.sidebar.markdown("---")
    if st.sidebar.button("🔍 View Database Schema"):
        display_database_schema(db_manager, tables)

def display_table_content(db_manager, table_name):
    """Display content of selected table with interactive features"""
    
    # Table header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.header(f"📋 Table: {table_name}")
    
    # Get table info
    table_info = db_manager.get_table_info(table_name)
    row_count = db_manager.get_table_row_count(table_name)
    
    with col2:
        st.metric("Total Rows", f"{row_count:,}")
    with col3:
        st.metric("Columns", len(table_info))
    
    # Table schema information
    with st.expander("📋 Table Schema", expanded=False):
        schema_df = pd.DataFrame(table_info)
        st.dataframe(schema_df, use_container_width=True)
    
    # Data filtering and pagination controls
    st.subheader("🔧 Data Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        page_size = st.selectbox("Rows per page:", [10, 25, 50, 100, 500], index=2)
    
    with col2:
        page_number = st.number_input("Page:", min_value=1, value=1, max_value=max(1, (row_count + page_size - 1) // page_size))
    
    with col3:
        refresh_data = st.button("🔄 Refresh Data")
    
    with col4:
        show_stats = st.checkbox("📊 Show Statistics", value=False)
    
    # Search and filter
    search_term = st.text_input("🔍 Search in all columns:")
    
    # Column selection for filtering
    columns = [col['column_name'] for col in table_info]
    selected_columns = st.multiselect("Select columns to display:", columns, default=columns)
    
    if not selected_columns:
        selected_columns = columns
    
    # Get data with pagination
    offset = (page_number - 1) * page_size
    data = db_manager.get_table_data(table_name, limit=page_size, offset=offset, columns=selected_columns, search_term=search_term)
    
    if data is not None and not data.empty:
        # Display data statistics
        if show_stats:
            st.subheader("📈 Data Statistics")
            stats_cols = st.columns(min(4, len(selected_columns)))
            
            for i, col in enumerate(selected_columns[:4]):
                with stats_cols[i % 4]:
                    if data[col].dtype in ['int64', 'float64']:
                        st.metric(f"{col} (Avg)", f"{data[col].mean():.2f}")
                    else:
                        st.metric(f"{col} (Unique)", f"{data[col].nunique()}")
        
        # Data table display
        st.subheader("📊 Data Preview")
        st.dataframe(data, use_container_width=True, height=400)
        
        # Export functionality
        st.subheader("💾 Export Data")
        
        export_cols = st.columns(4)
        
        with export_cols[0]:
            if st.button("📄 Export as CSV"):
                csv_data = data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with export_cols[1]:
            if st.button("📋 Export as JSON"):
                json_data = data.to_json(orient='records', indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with export_cols[2]:
            if st.button("📊 Export as Excel"):
                excel_data = export_to_excel(data, table_name)
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name=f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with export_cols[3]:
            # Export all data (not just current page)
            if st.button("📁 Export Full Table"):
                full_data = db_manager.get_table_data(table_name, columns=selected_columns)
                if full_data is not None:
                    csv_data = full_data.to_csv(index=False)
                    st.download_button(
                        label="Download Full CSV",
                        data=csv_data,
                        file_name=f"{table_name}_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        # Data visualization for numeric columns
        numeric_columns = data.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        if numeric_columns and show_stats:
            st.subheader("📈 Data Visualization")
            
            viz_col = st.selectbox("Select column for visualization:", numeric_columns)
            
            if viz_col:
                fig = px.histogram(data, x=viz_col, title=f"Distribution of {viz_col}")
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("No data found for the selected criteria.")

def display_database_schema(db_manager, tables):
    """Display complete database schema information"""
    
    st.header("🏗️ Database Schema Overview")
    
    # Create tabs for different schema views
    tab1, tab2, tab3 = st.tabs(["📋 All Tables", "🔗 Relationships", "📊 Statistics"])
    
    with tab1:
        st.subheader("Table Overview")
        
        schema_data = []
        for table in tables:
            table_info = db_manager.get_table_info(table)
            row_count = db_manager.get_table_row_count(table)
            
            schema_data.append({
                'Table Name': table,
                'Column Count': len(table_info),
                'Row Count': row_count,
                'Primary Keys': ', '.join([col['column_name'] for col in table_info if col.get('is_primary_key', False)]),
                'Estimated Size': format_bytes(row_count * len(table_info) * 50)  # Rough estimate
            })
        
        schema_df = pd.DataFrame(schema_data)
        st.dataframe(schema_df, use_container_width=True)
    
    with tab2:
        st.subheader("Table Relationships")
        foreign_keys = db_manager.get_foreign_keys()
        
        if foreign_keys:
            fk_df = pd.DataFrame(foreign_keys)
            st.dataframe(fk_df, use_container_width=True)
        else:
            st.info("No foreign key relationships found.")
    
    with tab3:
        st.subheader("Database Statistics")
        
        total_rows = sum(db_manager.get_table_row_count(table) for table in tables)
        total_columns = sum(len(db_manager.get_table_info(table)) for table in tables)
        
        stat_cols = st.columns(4)
        
        with stat_cols[0]:
            st.metric("Total Tables", len(tables))
        with stat_cols[1]:
            st.metric("Total Rows", f"{total_rows:,}")
        with stat_cols[2]:
            st.metric("Total Columns", f"{total_columns:,}")
        with stat_cols[3]:
            st.metric("Avg Rows/Table", f"{total_rows // len(tables) if tables else 0:,}")
        
        # Table size visualization
        if tables:
            table_sizes = []
            for table in tables:
                row_count = db_manager.get_table_row_count(table)
                table_sizes.append({'Table': table, 'Row Count': row_count})
            
            size_df = pd.DataFrame(table_sizes)
            fig = px.bar(size_df, x='Table', y='Row Count', title='Table Sizes by Row Count')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
