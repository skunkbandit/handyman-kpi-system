import os
import sqlite3
import datetime
import csv
import shutil
from flask import current_app

def optimize_database():
    """Optimize the SQLite database by running VACUUM and ANALYZE commands"""
    try:
        # Get database path
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Create connection (auto-commit is off by default)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get database size before optimization
        db_size_before = os.path.getsize(db_path)
        
        # Run ANALYZE to update statistics
        cursor.execute("ANALYZE;")
        
        # Run VACUUM to defragment and optimize
        cursor.execute("VACUUM;")
        
        # Commit and close
        conn.commit()
        conn.close()
        
        # Get database size after optimization
        db_size_after = os.path.getsize(db_path)
        
        # Calculate size difference
        size_diff = db_size_before - db_size_after
        
        if size_diff > 0:
            size_saved = format_size(size_diff)
            return {
                'success': True,
                'message': f"Database optimized successfully. Reduced by {size_saved}.",
                'size_before': db_size_before,
                'size_after': db_size_after,
                'size_saved': size_diff
            }
        else:
            return {
                'success': True,
                'message': "Database optimized successfully. No size reduction achieved.",
                'size_before': db_size_before,
                'size_after': db_size_after,
                'size_saved': 0
            }
    except Exception as e:
        current_app.logger.error(f"Error optimizing database: {str(e)}")
        return {
            'success': False,
            'message': f"Error optimizing database: {str(e)}"
        }

def get_database_stats():
    """Get statistics about the database"""
    stats = {
        'size': 0,
        'size_formatted': '0 B',
        'tables': {},
        'indexes': {},
        'last_optimized': None,
        'total_records': 0
    }
    
    try:
        # Get database path
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            return stats
        
        # Get database size
        db_size = os.path.getsize(db_path)
        stats['size'] = db_size
        stats['size_formatted'] = format_size(db_size)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Get table statistics
        total_records = 0
        for table in tables:
            table_name = table[0]
            
            # Skip SQLite internal tables
            if table_name.startswith('sqlite_'):
                continue
                
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            total_records += row_count
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Store table stats
            stats['tables'][table_name] = {
                'records': row_count,
                'columns': len(columns),
                'column_names': [col[1] for col in columns]
            }
        
        # Store total records
        stats['total_records'] = total_records
        
        # Get index information
        cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index';")
        indexes = cursor.fetchall()
        
        for index in indexes:
            index_name = index[0]
            table_name = index[1]
            
            # Skip SQLite internal indexes
            if index_name.startswith('sqlite_'):
                continue
                
            # Get index info
            cursor.execute(f"PRAGMA index_info({index_name});")
            index_info = cursor.fetchall()
            
            if table_name not in stats['indexes']:
                stats['indexes'][table_name] = []
                
            stats['indexes'][table_name].append({
                'name': index_name,
                'columns': [info[2] for info in index_info]
            })
        
        # Close connection
        conn.close()
        
        return stats
    except Exception as e:
        current_app.logger.error(f"Error getting database stats: {str(e)}")
        return stats

def export_database(format='sql'):
    """Export database to SQL or CSV format"""
    try:
        # Get database path
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            return {
                'success': False,
                'message': "Database file not found",
                'path': None
            }
        
        # Create exports directory if it doesn't exist
        export_dir = os.path.join(current_app.instance_path, 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'sql':
            # Export as SQL dump
            export_path = os.path.join(export_dir, f"kpi_system_export_{timestamp}.sql")
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            
            # Open output file
            with open(export_path, 'w') as f:
                # Get schema
                for line in conn.iterdump():
                    f.write(f"{line}\n")
            
            # Close connection
            conn.close()
            
            return {
                'success': True,
                'message': "Database exported successfully as SQL",
                'path': export_path
            }
        elif format == 'csv':
            # Export as CSV files (one per table)
            export_subdir = os.path.join(export_dir, f"kpi_system_export_{timestamp}")
            os.makedirs(export_subdir, exist_ok=True)
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                
                # Skip SQLite internal tables
                if table_name.startswith('sqlite_'):
                    continue
                
                # Export table to CSV
                csv_path = os.path.join(export_subdir, f"{table_name}.csv")
                
                # Get all rows
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()
                
                if not rows:
                    # Create empty file with headers if no data
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    headers = [col[1] for col in columns]
                    
                    with open(csv_path, 'w', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow(headers)
                else:
                    # Write data to CSV
                    with open(csv_path, 'w', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow(rows[0].keys())
                        for row in rows:
                            csv_writer.writerow(row)
            
            # Close connection
            conn.close()
            
            # Create a zip file of all CSVs
            zip_path = f"{export_subdir}.zip"
            shutil.make_archive(export_subdir, 'zip', export_subdir)
            
            # Remove the directory now that we have a zip
            shutil.rmtree(export_subdir)
            
            return {
                'success': True,
                'message': "Database exported successfully as CSV files",
                'path': zip_path
            }
        else:
            return {
                'success': False,
                'message': f"Unsupported export format: {format}",
                'path': None
            }
    except Exception as e:
        current_app.logger.error(f"Error exporting database: {str(e)}")
        return {
            'success': False,
            'message': f"Error exporting database: {str(e)}",
            'path': None
        }

def import_csv_data(table_name, csv_file_path, truncate=False):
    """Import data from CSV file into specified table"""
    try:
        # Get database path
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if not cursor.fetchone():
            conn.close()
            return {
                'success': False,
                'message': f"Table '{table_name}' does not exist",
                'records_imported': 0
            }
        
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Truncate table if requested
        if truncate:
            cursor.execute(f"DELETE FROM {table_name};")
        
        # Read CSV file
        with open(csv_file_path, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            headers = next(csv_reader)  # First row as headers
            
            # Validate headers against table columns
            valid_headers = []
            for header in headers:
                if header in column_names:
                    valid_headers.append(header)
                else:
                    current_app.logger.warning(f"Column '{header}' not found in table '{table_name}', it will be ignored")
            
            if not valid_headers:
                conn.close()
                return {
                    'success': False,
                    'message': f"No valid columns found in CSV file for table '{table_name}'",
                    'records_imported': 0
                }
            
            # Prepare placeholders for INSERT
            placeholders = ', '.join(['?' for _ in valid_headers])
            columns_str = ', '.join(valid_headers)
            
            # Import data
            records_imported = 0
            for row in csv_reader:
                # Map values to valid headers
                values = []
                for i, header in enumerate(headers):
                    if header in valid_headers and i < len(row):
                        values.append(row[i])
                
                # Skip if not enough values
                if len(values) != len(valid_headers):
                    continue
                
                # Insert row
                cursor.execute(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders});", values)
                records_imported += 1
        
        # Commit changes
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': f"Successfully imported {records_imported} records into table '{table_name}'",
            'records_imported': records_imported
        }
    except Exception as e:
        current_app.logger.error(f"Error importing CSV data: {str(e)}")
        return {
            'success': False,
            'message': f"Error importing CSV data: {str(e)}",
            'records_imported': 0
        }

def check_database_integrity():
    """Check database integrity"""
    try:
        # Get database path
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Run integrity check
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()[0]
        
        # Run foreign key check
        cursor.execute("PRAGMA foreign_key_check;")
        foreign_key_issues = cursor.fetchall()
        
        # Close connection
        conn.close()
        
        if result == 'ok' and not foreign_key_issues:
            return {
                'success': True,
                'message': "Database integrity check passed",
                'integrity': 'ok',
                'foreign_key_issues': []
            }
        else:
            issues = []
            if result != 'ok':
                issues.append(f"Integrity check: {result}")
            
            if foreign_key_issues:
                for issue in foreign_key_issues:
                    issues.append(f"Foreign key violation in table '{issue[0]}', row id {issue[1]}, refers to table '{issue[2]}'")
            
            return {
                'success': False,
                'message': "Database integrity check failed",
                'integrity': result,
                'foreign_key_issues': foreign_key_issues,
                'issues': issues
            }
    except Exception as e:
        current_app.logger.error(f"Error checking database integrity: {str(e)}")
        return {
            'success': False,
            'message': f"Error checking database integrity: {str(e)}",
            'integrity': 'error',
            'foreign_key_issues': [],
            'issues': [str(e)]
        }

def format_size(size_bytes):
    """Format file size from bytes to human-readable format"""
    if size_bytes == 0:
        return "0 B"
        
    size_names = ('B', 'KB', 'MB', 'GB', 'TB')
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
        
    return f"{size_bytes:.2f} {size_names[i]}"
