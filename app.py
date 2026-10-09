from flask import Flask, render_template_string, jsonify, request
import pandas as pd
import random

app = Flask(__name__)

# Sample server fleet
NODES = [
    {"name": "Web-Server-01", "ip": "192.168.1.10", "role": "Nginx/Frontend"},
    {"name": "Db-Node-Primary", "ip": "192.168.1.12", "role": "PostgreSQL"},
    {"name": "App-Worker-01", "ip": "192.168.1.15", "role": "Python/Celery"},
    {"name": "Cache-Redis-01", "ip": "192.168.1.18", "role": "Redis Cache"}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NodePulse Infrastructure Monitor</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; }
        .card { background-color: #1e293b; border: 1px solid #334155; color: #f8fafc; }
        .table-dark { --bs-table-bg: #1e293b; }
        .badge-healthy { background-color: #22c55e; }
        .badge-warning { background-color: #eab308; color: #000; }
        .badge-critical { background-color: #ef4444; }
    </style>
</head>
<body class="p-4">
    <div class="container">
        <h1 class="fw-bold text-primary">⚡ NodePulse Infrastructure Telemetry</h1>
        <p class="text-muted">Agentless Real-Time Linux Health & SSH Audit Pipeline</p>
        
        <div class="row g-3 mb-4">
            <div class="col-md-3"><div class="card p-3"><h5>Monitored Nodes</h5><h2>4</h2></div></div>
            <div class="col-md-3"><div class="card p-3"><h5>System Health</h5><h2 class="text-success">87%</h2></div></div>
            <div class="col-md-3"><div class="card p-3"><h5>Avg SSH Latency</h5><h2>12ms</h2></div></div>
            <div class="col-md-3"><div class="card p-3"><h5>Agent Footprint</h5><h2 class="text-info">0 KB</h2></div></div>
        </div>

        <div class="card p-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4 class="m-0">Fleet Scan Status</h4>
                <a href="/api/scan" class="btn btn-primary fw-bold">🚀 Run Parallel Inspection Pass</a>
            </div>
            
            <table class="table table-dark table-hover align-middle">
                <thead>
                    <tr>
                        <th>Node Name</th>
                        <th>IP Address</th>
                        <th>Status</th>
                        <th>CPU Load (1m)</th>
                        <th>RAM Usage</th>
                        <th>Disk Usage</th>
                    </tr>
                </thead>
                <tbody>
                    {% for node in results %}
                    <tr>
                        <td><strong>{{ node.name }}</strong></td>
                        <td><code>{{ node.ip }}</code></td>
                        <td>
                            {% if node.status == 'CRITICAL' %}
                                <span class="badge badge-critical">CRITICAL</span>
                            {% elif node.status == 'WARNING' %}
                                <span class="badge badge-warning">WARNING</span>
                            {% else %}
                                <span class="badge badge-healthy">HEALTHY</span>
                            {% endif %}
                        </td>
                        <td>{{ node.cpu }}</td>
                        <td>{{ node.ram }}%</td>
                        <td>{{ node.disk }}%</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

def fetch_telemetry():
    results = []
    for node in NODES:
        if "Db" in node["name"]:
            cpu, ram, disk = round(random.uniform(1.2, 2.5), 2), random.randint(82, 92), random.randint(70, 75)
            status = "CRITICAL" if cpu >= 2.0 else "WARNING"
        elif "App" in node["name"]:
            cpu, ram, disk = round(random.uniform(0.5, 1.1), 2), random.randint(60, 75), random.randint(86, 91)
            status = "WARNING" if disk >= 85 else "HEALTHY"
        else:
            cpu, ram, disk = round(random.uniform(0.1, 0.45), 2), random.randint(30, 55), random.randint(40, 60)
            status = "HEALTHY"
            
        results.append({
            "name": node["name"],
            "ip": node["ip"],
            "status": status,
            "cpu": cpu,
            "ram": ram,
            "disk": disk
        })
    return results

@app.route("/")
def home():
    data = fetch_telemetry()
    return render_template_string(HTML_TEMPLATE, results=data)

@app.route("/api/scan")
def api_scan():
    data = fetch_telemetry()
    return render_template_string(HTML_TEMPLATE, results=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
