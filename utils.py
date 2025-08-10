import pandas as pd
import io
from typing import Dict, Any, List
import streamlit as st

def format_bytes(bytes_value):
    """Convert bytes to human readable format"""
    if bytes_value == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_index = 0
    
    while bytes_value >= 1024 and size_index < len(size_names) - 1:
        bytes_value /= 1024.0
        size_index += 1
    
    return f"{bytes_value:.2f} {size_names[size_index]}"

def get_column_stats(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Get statistics for a specific column"""
    col_data = df[column]
    stats = {}
    
    # Basic stats
    stats['count'] = len(col_data)
    stats['null_count'] = col_data.isnull().sum()
    stats['unique_count'] = col_data.nunique()
    
    # Type-specific stats
    if pd.api.types.is_numeric_dtype(col_data):
        stats['min'] = col_data.min()
        stats['max'] = col_data.max()
        stats['mean'] = col_data.mean()
        stats['median'] = col_data.median()
        stats['std'] = col_data.std()
    elif pd.api.types.is_string_dtype(col_data):
        stats['min_length'] = col_data.str.len().min()
        stats['max_length'] = col_data.str.len().max()
        stats['avg_length'] = col_data.str.len().mean()
    
    return stats

def export_to_excel(df: pd.DataFrame, sheet_name: str = "Data") -> bytes:
    """Export DataFrame to Excel format and return as bytes"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Auto-adjust columns width
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output.getvalue()

def validate_sql_query(query: str) -> bool:
    """Basic SQL query validation (prevent dangerous operations)"""
    dangerous_keywords = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 
        'INSERT', 'UPDATE', 'GRANT', 'REVOKE'
    ]
    
    query_upper = query.upper().strip()
    
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False
    
    return True

def format_data_type(data_type: str, max_length: int = None, precision: int = None, scale: int = None) -> str:
    """Format data type with additional information"""
    formatted_type = data_type.upper()
    
    if max_length and data_type.lower() in ['varchar', 'char', 'character']:
        formatted_type += f"({max_length})"
    elif precision and data_type.lower() in ['numeric', 'decimal']:
        if scale:
            formatted_type += f"({precision},{scale})"
        else:
            formatted_type += f"({precision})"
    
    return formatted_type

def create_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Create a comprehensive summary of the DataFrame"""
    summary = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'null_counts': df.isnull().sum().to_dict(),
        'data_types': df.dtypes.astype(str).to_dict(),
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
        'datetime_columns': df.select_dtypes(include=['datetime']).columns.tolist()
    }
    
    return summary

def paginate_dataframe(df: pd.DataFrame, page_size: int, page_number: int) -> pd.DataFrame:
    """Paginate a DataFrame"""
    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size
    
    return df.iloc[start_idx:end_idx]

def search_dataframe(df: pd.DataFrame, search_term: str, columns: List[str] = None) -> pd.DataFrame:
    """Search for a term across specified columns or all columns"""
    if not search_term:
        return df
    
    if columns is None:
        columns = df.columns.tolist()
    
    # Create a mask for rows that contain the search term
    mask = pd.Series([False] * len(df), index=df.index)
    
    for col in columns:
        if col in df.columns:
            # Convert to string and search (case-insensitive)
            col_mask = df[col].astype(str).str.contains(search_term, case=False, na=False)
            mask = mask | col_mask
    
    return df[mask]

def get_table_preview(df: pd.DataFrame, max_rows: int = 5) -> pd.DataFrame:
    """Get a preview of the table with limited rows"""
    return df.head(max_rows)

def calculate_table_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate comprehensive statistics for a table"""
    stats = {
        'shape': df.shape,
        'memory_usage': format_bytes(df.memory_usage(deep=True).sum()),
        'null_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
        'unique_counts': df.nunique().to_dict(),
        'duplicate_rows': df.duplicated().sum()
    }
    
    # Add numeric statistics if numeric columns exist
    numeric_df = df.select_dtypes(include=['number'])
    if not numeric_df.empty:
        stats['numeric_summary'] = numeric_df.describe().to_dict()
    
    return stats
