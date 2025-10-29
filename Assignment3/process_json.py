#!/usr/bin/python3

import json
import os
from urllib.parse import parse_qs

def escape_html(text):
    """Escape HTML special characters"""
    if text is None:
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def build_table_html(headers, rows):
    """Build HTML table from headers and rows"""
    # Build table header
    thead = '<thead><tr>'
    for header in headers:
        thead += f'<th>{escape_html(header)}</th>'
    thead += '</tr></thead>'
    
    # Build table body
    tbody = '<tbody>'
    for company in rows:
        name = escape_html(company.get('Company', ''))
        services = escape_html(company.get('Services', ''))
        
        # Handle Hubs - can be array or single value
        hubs_data = company.get('Hubs', {})
        if isinstance(hubs_data, dict) and 'Hub' in hubs_data:
            hub_list = hubs_data['Hub']
            if isinstance(hub_list, list):
                hubs_html = '<br>'.join([escape_html(hub) for hub in hub_list])
            else:
                hubs_html = escape_html(hub_list)
        else:
            hubs_html = ''
        
        revenue = escape_html(company.get('Revenue', ''))
        
        # Handle homepage link
        homepage = company.get('HomePage', '')
        if homepage:
            homepage_cell = f'<a href="{escape_html(homepage)}" target="_blank" rel="noopener">HomePage</a>'
        else:
            homepage_cell = ''
        
        # Handle logo image
        logo = company.get('Logo', '')
        if logo:
            logo_cell = f'<img src="{escape_html(logo)}" alt="{name} Logo" width="50" height="50" />'
        else:
            logo_cell = ''
        
        tbody += f'''<tr>
            <td>{name}</td>
            <td>{services}</td>
            <td>{hubs_html}</td>
            <td>{revenue}</td>
            <td>{homepage_cell}</td>
            <td>{logo_cell}</td>
        </tr>'''
    
    tbody += '</tbody>'
    
    return f'<table border="1" style="border-collapse: collapse; width: 100%;">{thead}{tbody}</table>'

def main():
    # Print CGI headers
    print("Content-Type: text/html")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: GET, POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()  # Empty line required after headers
    
    try:
        # Get query string parameters
        query_string = os.environ.get('QUERY_STRING', '')
        params = parse_qs(query_string)
        
        # Get filename from query parameter
        filename = params.get('file', [''])[0]
        
        if not filename:
            print('<html><body><h1>Error: No file parameter provided</h1></body></html>')
            return
        
        # Security check - only allow certain file extensions and no path traversal
        if not filename.endswith('.json') or '/' in filename or '\\' in filename or '..' in filename:
            print('<html><body><h1>Error: Invalid filename</h1></body></html>')
            return
        
        # Read and parse JSON file
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f'<html><body><h1>Error: File "{escape_html(filename)}" not found</h1></body></html>')
            return
        except json.JSONDecodeError:
            print('<html><body><h1>Error: Invalid JSON file</h1></body></html>')
            return
        
        # Extract data from JSON structure
        mainline = data.get('Mainline', {})
        table_data = mainline.get('Table', {})
        
        # Get headers
        header_data = table_data.get('Header', {})
        headers = header_data.get('Data', [
            'Parent Company',
            'Subsidiary Portfolio / Services', 
            'HQ / Info',
            'Annual Revenue ($ million)',
            'HomePage',
            'Logo'
        ])
        
        # Get rows
        rows = table_data.get('Row', [])
        
        if not rows:
            print('<html><body><h1>No trucking companies found in the JSON file</h1></body></html>')
            return
        
        # Build table HTML
        table_html = build_table_html(headers, rows)
        
        # Generate complete HTML response
        html_response = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Trucking Companies</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background-color: #f3f4f6;
            font-weight: bold;
        }}
        img {{
            object-fit: contain;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>Trucking Companies Information</h1>
    {table_html}
</body>
</html>'''
        
        print(html_response)
        
    except Exception as e:
        print(f'<html><body><h1>Error: {escape_html(str(e))}</h1></body></html>')

if __name__ == '__main__':
    main()
