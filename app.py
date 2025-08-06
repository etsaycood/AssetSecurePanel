from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# --- Configuration ---
DASHBOARD_DB = "dashboard.db"

def get_db_connection():
    conn = sqlite3.connect(DASHBOARD_DB)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def is_host_updated(host, days_threshold):
    """
    Checks if a host's antivirus and log updates are within the specified days_threshold.
    Returns True if both are updated, False otherwise (including missing data).
    """
    now = datetime.now()
    threshold_date = now - timedelta(days=days_threshold)

    av_updated = False
    if host['antivirus_last_updated']:
        try:
            av_date = datetime.strptime(host['antivirus_last_updated'], "%Y-%m-%d %H:%M:%S")
            if av_date >= threshold_date:
                av_updated = True
        except ValueError:
            pass # Handle malformed date strings

    log_updated = False
    if host['logserver_last_received']:
        try:
            log_date = datetime.strptime(host['logserver_last_received'], "%Y-%m-%d %H:%M:%S")
            if log_date >= threshold_date:
                log_updated = True
        except ValueError:
            pass # Handle malformed date strings

    return av_updated and log_updated

def get_group_status(hosts_in_group, days_threshold):
    """
    Determines the color status (green, yellow, red) for a group of hosts.
    """
    if not hosts_in_group:
        return "red" # Or some other indicator for empty group

    total_hosts = len(hosts_in_group)
    updated_hosts_count = sum(1 for host in hosts_in_group if is_host_updated(host, days_threshold))

    if updated_hosts_count == total_hosts:
        return "green"
    elif updated_hosts_count >= 0.8 * total_hosts:
        return "yellow"
    else:
        return "red"

@app.route('/', methods=['GET', 'POST'])
def index():
    days_threshold = 7
    if request.method == 'POST':
        try:
            days_threshold = int(request.form.get('days', 7))
            if days_threshold <= 0:
                days_threshold = 7 # Ensure positive
        except ValueError:
            days_threshold = 7 # Fallback to default

    conn = get_db_connection()
    hosts = conn.execute('SELECT * FROM dashboard_hosts').fetchall()
    conn.close()

    # Group hosts by classification
    classifications_data = {}
    for host in hosts:
        classification = host['classification']
        if classification not in classifications_data:
            classifications_data[classification] = []
        classifications_data[classification].append(host)

    # Calculate status for each classification
    classification_statuses = {}
    for classification, hosts_in_group in classifications_data.items():
        status = get_group_status(hosts_in_group, days_threshold)
        classification_statuses[classification] = {
            'status': status,
            'count': len(hosts_in_group)
        }

    return render_template('index.html', 
                           classification_statuses=classification_statuses, 
                           days_threshold=days_threshold)

@app.route('/classification/<classification_name>', methods=['GET', 'POST'])
def purpose_detail(classification_name):
    days_threshold = 7 # Default
    if request.method == 'POST':
        try:
            days_threshold = int(request.form.get('days', 7))
            if days_threshold <= 0:
                days_threshold = 7
        except ValueError:
            days_threshold = 7
    else: # GET request
        try:
            days_threshold = int(request.args.get('days', 7)) # Get from query parameters
            if days_threshold <= 0:
                days_threshold = 7
        except ValueError:
            days_threshold = 7

    conn = get_db_connection()
    hosts = conn.execute('SELECT * FROM dashboard_hosts WHERE classification = ?', (classification_name,)).fetchall()
    conn.close()

    # Group hosts by purpose within this classification
    purposes_data = {}
    for host in hosts:
        purpose = host['purpose']
        if purpose not in purposes_data:
            purposes_data[purpose] = []
        purposes_data[purpose].append(host)

    # Calculate status for each purpose
    purpose_statuses = {}
    for purpose, hosts_in_group in purposes_data.items():
        status = get_group_status(hosts_in_group, days_threshold)
        purpose_statuses[purpose] = {
            'status': status,
            'count': len(hosts_in_group)
        }

    return render_template('purpose_detail.html', 
                           classification_name=classification_name,
                           purpose_statuses=purpose_statuses,
                           days_threshold=days_threshold)

@app.route('/host_list/<classification_name>/<purpose_name>', methods=['GET'])
def host_list(classification_name, purpose_name):
    days_threshold = int(request.args.get('days', 7)) # Get days from query param

    conn = get_db_connection()
    hosts = conn.execute('SELECT * FROM dashboard_hosts WHERE classification = ? AND purpose = ?', 
                         (classification_name, purpose_name)).fetchall()
    conn.close()

    # Determine individual host AV/Log status
    hosts_with_status = []
    for host_row in hosts:
        host_dict = dict(host_row) # Convert Row object to dict for easier manipulation
        
        host_dict['av_status'] = "red"
        if host_dict['antivirus_last_updated']:
            try:
                av_date = datetime.strptime(host_dict['antivirus_last_updated'], "%Y-%m-%d %H:%M:%S")
                if av_date >= (datetime.now() - timedelta(days=days_threshold)):
                    host_dict['av_status'] = "green"
            except ValueError:
                pass

        host_dict['log_status'] = "red"
        if host_dict['logserver_last_received']:
            try:
                log_date = datetime.strptime(host_dict['logserver_last_received'], "%Y-%m-%d %H:%M:%S")
                if log_date >= (datetime.now() - timedelta(days=days_threshold)):
                    host_dict['log_status'] = "green"
            except ValueError:
                pass
        hosts_with_status.append(host_dict)
    
    hosts = hosts_with_status # Update hosts to the new list of dictionaries
    
    return render_template('host_list.html', 
                           classification_name=classification_name,
                           purpose_name=purpose_name,
                           hosts=hosts,
                           days_threshold=days_threshold)

if __name__ == '__main__':
    app.run(debug=True)
