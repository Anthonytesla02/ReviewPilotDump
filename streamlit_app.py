#!/usr/bin/env python3

"""
Alternative web interface for Vercel deployment using Flask
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import json
from database import DatabaseManager
from utils import export_to_excel

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PostgreSQL Database Dumper</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        .container-fluid { padding: 20px; }
        .table-container { max-height: 600px; overflow-y: auto; }
        .stats-card { margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <h1 class="mb-4">🗄️ PostgreSQL Database Dumper</h1>
        
        <div class="row">
            <div class="col-md-3">
                <div class="card">
                    <div class="card-header">
                        <h5>Database Selection</h5>
                    </div>
                    <div class="card-body">
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="dbType" id="reviewpilot" value="custom" checked>
                            <label class="form-check-label" for="reviewpilot">
                                ReviewPilot Database
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="dbType" id="replit" value="replit">
                            <label class="form-check-label" for="replit">
                                Replit Database
                            </label>
                        </div>
                        <button class="btn btn-primary mt-3" onclick="connectDatabase()">Connect</button>
                    </div>
                </div>
                
                <div class="card mt-3" id="tablesCard" style="display: none;">
                    <div class="card-header">
                        <h5>Tables</h5>
                    </div>
                    <div class="card-body">
                        <select class="form-select" id="tableSelect" onchange="loadTable()">
                            <option value="">Select a table...</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="col-md-9">
                <div id="connectionStatus"></div>
                <div id="tableContent"></div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentDbType = 'custom';
        
        function connectDatabase() {
            const dbType = document.querySelector('input[name="dbType"]:checked').value;
            currentDbType = dbType;
            
            fetch('/connect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({db_type: dbType})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('connectionStatus').innerHTML = 
                        '<div class="alert alert-success">✅ Connected to ' + data.db_info.source + '</div>';
                    loadTables(data.tables);
                    document.getElementById('tablesCard').style.display = 'block';
                } else {
                    document.getElementById('connectionStatus').innerHTML = 
                        '<div class="alert alert-danger">❌ Connection failed: ' + data.error + '</div>';
                }
            })
            .catch(error => {
                document.getElementById('connectionStatus').innerHTML = 
                    '<div class="alert alert-danger">❌ Error: ' + error + '</div>';
            });
        }
        
        function loadTables(tables) {
            const select = document.getElementById('tableSelect');
            select.innerHTML = '<option value="">Select a table...</option>';
            tables.forEach(table => {
                const option = document.createElement('option');
                option.value = table;
                option.textContent = table;
                select.appendChild(option);
            });
        }
        
        function loadTable() {
            const tableName = document.getElementById('tableSelect').value;
            if (!tableName) return;
            
            fetch('/table_data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({table_name: tableName, db_type: currentDbType, limit: 50})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayTableData(data.data, data.info, tableName);
                } else {
                    document.getElementById('tableContent').innerHTML = 
                        '<div class="alert alert-danger">Error loading table: ' + data.error + '</div>';
                }
            });
        }
        
        function displayTableData(data, info, tableName) {
            let html = '<div class="card"><div class="card-header"><h5>Table: ' + tableName + '</h5>';
            html += '<p>Rows: ' + info.row_count + ' | Columns: ' + info.column_count + '</p></div>';
            html += '<div class="card-body"><div class="table-container">';
            
            if (data.length > 0) {
                html += '<table class="table table-striped table-hover"><thead class="table-dark"><tr>';
                Object.keys(data[0]).forEach(col => {
                    html += '<th>' + col + '</th>';
                });
                html += '</tr></thead><tbody>';
                
                data.forEach(row => {
                    html += '<tr>';
                    Object.values(row).forEach(val => {
                        html += '<td>' + (val || '') + '</td>';
                    });
                    html += '</tr>';
                });
                html += '</tbody></table>';
            } else {
                html += '<p>No data found in this table.</p>';
            }
            
            html += '</div><div class="mt-3">';
            html += '<button class="btn btn-success me-2" onclick="exportData(\'' + tableName + '\', \'csv\')">Export CSV</button>';
            html += '<button class="btn btn-info me-2" onclick="exportData(\'' + tableName + '\', \'json\')">Export JSON</button>';
            html += '<button class="btn btn-warning" onclick="exportData(\'' + tableName + '\', \'excel\')">Export Excel</button>';
            html += '</div></div></div>';
            
            document.getElementById('tableContent').innerHTML = html;
        }
        
        function exportData(tableName, format) {
            const url = '/export/' + format + '/' + tableName + '?db_type=' + currentDbType;
            window.open(url, '_blank');
        }
        
        // Auto-connect on page load
        connectDatabase();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/connect', methods=['POST'])
def connect_database():
    try:
        data = request.get_json()
        db_type = data.get('db_type', 'custom')
        use_custom = db_type == 'custom'
        
        db_manager = DatabaseManager(use_custom=use_custom)
        
        if not db_manager.test_connection():
            return jsonify({'success': False, 'error': 'Database connection failed'})
        
        tables = db_manager.get_all_tables()
        
        return jsonify({
            'success': True,
            'tables': tables,
            'db_info': db_manager.connection_params
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/table_data', methods=['POST'])
def get_table_data():
    try:
        data = request.get_json()
        table_name = data.get('table_name')
        db_type = data.get('db_type', 'custom')
        limit = data.get('limit', 50)
        
        use_custom = db_type == 'custom'
        db_manager = DatabaseManager(use_custom=use_custom)
        
        table_data = db_manager.get_table_data(table_name, limit=limit)
        table_info = db_manager.get_table_info(table_name)
        row_count = db_manager.get_table_row_count(table_name)
        
        if table_data is not None:
            data_dict = table_data.to_dict('records')
            return jsonify({
                'success': True,
                'data': data_dict,
                'info': {
                    'row_count': row_count,
                    'column_count': len(table_info)
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to load table data'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export/<format>/<table_name>')
def export_data(format, table_name):
    try:
        db_type = request.args.get('db_type', 'custom')
        use_custom = db_type == 'custom'
        db_manager = DatabaseManager(use_custom=use_custom)
        
        table_data = db_manager.get_table_data(table_name)
        
        if table_data is None:
            return "Error: Could not retrieve table data", 500
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'csv':
            output = io.StringIO()
            table_data.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{table_name}_{timestamp}.csv'
            )
            
        elif format == 'json':
            json_data = table_data.to_json(orient='records', indent=2)
            
            return send_file(
                io.BytesIO(json_data.encode()),
                mimetype='application/json',
                as_attachment=True,
                download_name=f'{table_name}_{timestamp}.json'
            )
            
        elif format == 'excel':
            excel_data = export_to_excel(table_data, table_name)
            
            return send_file(
                io.BytesIO(excel_data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'{table_name}_{timestamp}.xlsx'
            )
        
        return "Unsupported format", 400
        
    except Exception as e:
        return f"Export error: {str(e)}", 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)