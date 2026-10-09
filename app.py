cat << 'EOF' > app.py
from flask import Flask, render_template_string, jsonify, Response
import pandas as pd
import random

app = Flask(__name__)

NODES = [
    {"name": "Web-Server-01", "ip": "192.168.1.10", "os": "Ubuntu 22.04 LTS"},
    {"name": "Db-Node-Primary", "ip": "192.168.1.12", "os": "Debian 12"},
    {"name": "App-Worker-01", "ip": "192.168.1.15", "os": "RHEL 9"},
    {"name": "Cache-Redis-01", "ip": "192.168.1.18", "os": "Alpine Linux"}
]

def get_node_telemetry():
    data = []
    for node in NODES:
        cpu = round(random.uniform(0.1, 2.8), 2)
        ram = random.randint(25, 96)
        disk = random.randint(40, 94)
        status = "CRITICAL" if disk > 88 or ram > 90 else ("WARNING" if ram > 75 or disk > 80 else "HEALTHY")
        data.append({
            "Node Name": node["name"],
            "IP Address": node["ip"],
            "OS": node["os"],
            "Status": status,
            "CPU Load (1m)": cpu,
            "RAM Usage": f"{ram}%",
            "Disk Usage": f"{disk}%",
            "raw_ram": ram,
            "raw_disk": disk
        })
    return data

@app.route('/api/telemetry')
def api_telemetry():
    return jsonify(get_node_telemetry())

@app.route('/export/csv')
def export_csv():
    data = get_node_telemetry()
    df = pd.DataFrame(data).drop(columns=['raw_ram', 'raw_disk'])
    csv_data = df.to_csv(index=False)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=nodepulse_telemetry_report.csv"}
    )

@app.route('/')
def dashboard():
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>NodePulse Infrastructure Telemetry</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <style>
            body { background-color: #0b0f19; color: #e2e8f0; font-family: system-ui, -apple-system, sans-serif; }
            .card-metric { background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; }
            .table-custom { background-color: #111827; color: #e2e8f0; border-radius: 8px; overflow: hidden; }
            .table-custom th { background-color: #1f2937; color: #9ca3af; border-bottom: none; }
            .table-custom td { border-color: #1f2937; vertical-align: middle; cursor: pointer; }
            .table-custom tr:hover td { background-color: #1f2937; }
            .badge-healthy { background-color: #059669; color: #fff; }
            .badge-warning { background-color: #d97706; color: #fff; }
            .badge-critical { background-color: #dc2626; color: #fff; }
            .search-input { background-color: #1f2937; border: 1px solid #374151; color: #fff; }
            .search-input:focus { background-color: #1f2937; color: #fff; border-color: #3b82f6; box-shadow: none; }
            .terminal-window { background-color: #050811; color: #10b981; font-family: monospace; border-radius: 6px; padding: 15px; border: 1px solid #1f2937; }
        </style>
    </head>
    <body class="p-4">
        <div class="container">
            <!-- Global Critical Alert Banner -->
            <div id="alertBanner" class="alert alert-danger border-0 text-white mb-4 d-none" style="background-color: #991b1b;" role="alert">
                <strong>⚠️ Critical System Alert:</strong> One or more nodes have exceeded maximum disk/RAM safety thresholds!
            </div>

            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 class="fw-bold text-primary">⚡ NodePulse Infrastructure Telemetry</h2>
                    <p class="text-secondary m-0">Agentless Real-Time Linux Health & SSH Audit Pipeline</p>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <a href="/export/csv" class="btn btn-outline-secondary btn-sm text-light border-secondary">📥 Export CSV</a>
                    <span class="badge bg-outline-success border border-success text-success p-2">● Live Sync Active</span>
                </div>
            </div>

            <!-- Metric Cards -->
            <div class="row g-3 mb-4">
                <div class="col-md-3">
                    <div class="card-metric p-3">
                        <small class="text-secondary fw-semibold">Monitored Nodes</small>
                        <h3 class="fw-bold mt-1 mb-0">4</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card-metric p-3">
                        <small class="text-secondary fw-semibold">Fleet Health Rating</small>
                        <h3 id="healthRating" class="fw-bold text-success mt-1 mb-0">94%</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card-metric p-3">
                        <small class="text-secondary fw-semibold">Avg SSH Latency</small>
                        <h3 class="fw-bold mt-1 mb-0">11ms</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card-metric p-3">
                        <small class="text-secondary fw-semibold">Agent Footprint</small>
                        <h3 class="fw-bold text-info mt-1 mb-0">0 KB</h3>
                    </div>
                </div>
            </div>

            <!-- Control Bar & Table -->
            <div class="card-metric p-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h4 class="fw-bold m-0">Fleet Scan Status</h4>
                        <small class="text-secondary">Click any node row for SSH telemetry audit</small>
                    </div>
                    <div class="d-flex gap-2">
                        <input type="text" id="searchInput" class="form-control search-input" placeholder="Filter node or IP..." onkeyup="filterNodes()">
                        <button class="btn btn-primary text-nowrap" onclick="fetchTelemetry()">🚀 Scan Now</button>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table table-custom align-middle m-0">
                        <thead>
                            <tr>
                                <th>Node Name</th>
                                <th>IP Address</th>
                                <th>OS</th>
                                <th>Status</th>
                                <th>CPU Load (1m)</th>
                                <th>RAM Usage</th>
                                <th>Disk Usage</th>
                            </tr>
                        </thead>
                        <tbody id="telemetryBody">
                            <!-- Dynamic Content -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Terminal Audit Modal -->
        <div class="modal fade" id="terminalModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content" style="background-color: #111827; border: 1px solid #374151; color: #fff;">
                    <div class="modal-header border-secondary">
                        <h5 class="modal-title font-monospace" id="modalNodeTitle">SSH Terminal Inspection</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p class="text-secondary small mb-2">Executing remote SSH query pipeline over agentless port 22...</p>
                        <div class="terminal-window" id="terminalContent">
                            Connecting...
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function fetchTelemetry() {
                try {
                    const res = await fetch('/api/telemetry');
                    const data = await res.json();
                    const tbody = document.getElementById('telemetryBody');
                    tbody.innerHTML = '';
                    
                    let hasCritical = false;

                    data.forEach(node => {
                        let badgeClass = 'badge-healthy';
                        if (node.Status === 'WARNING') badgeClass = 'badge-warning';
                        if (node.Status === 'CRITICAL') {
                            badgeClass = 'badge-critical';
                            hasCritical = true;
                        }

                        tbody.innerHTML += `
                            <tr onclick="openTerminal('${node['Node Name']}', '${node['IP Address']}', '${node['OS']}', '${node['CPU Load (1m)']}', '${node['RAM Usage']}', '${node['Disk Usage']}')">
                                <td class="fw-semibold">${node['Node Name']}</td>
                                <td class="text-danger small font-monospace">${node['IP Address']}</td>
                                <td class="small text-secondary">${node['OS']}</td>
                                <td><span class="badge ${badgeClass}">${node.Status}</span></td>
                                <td>${node['CPU Load (1m)']}</td>
                                <td>${node['RAM Usage']}</td>
                                <td>${node['Disk Usage']}</td>
                            </tr>
                        `;
                    });

                    document.getElementById('alertBanner').classList.toggle('d-none', !hasCritical);
                    filterNodes();
                } catch (e) {
                    console.error("Telemetry fetch error", e);
                }
            }

            function openTerminal(name, ip, os, cpu, ram, disk) {
                document.getElementById('modalNodeTitle').innerText = `ssh root@${ip} (${name})`;
                document.getElementById('terminalContent').innerHTML = `
[root@${name} ~]# uname -a
Linux ${name} 5.15.0-88-generic #98-Ubuntu SMP x86_64 ${os}

[root@${name} ~]# uptime
14:20:00 up 14 days, 3:12, 1 user, load average: ${cpu}, 0.52, 0.41

[root@${name} ~]# free -h
              total        used        free      shared  buff/cache   available
Mem:           16Gi        ${ram}        2.1Gi       120Mi       3.4Gi       4.2Gi

[root@${name} ~]# df -h /
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        98G   ${disk}   12G   ${disk} /

[root@${name} ~]# systemctl status sshd --no-pager
● sshd.service - OpenSSH server daemon
     Active: active (running) since Thu 2026-09-25 08:12:01 UTC; 2 weeks ago
`;
                new bootstrap.Modal(document.getElementById('terminalModal')).show();
            }

            function filterNodes() {
                const query = document.getElementById('searchInput').value.toLowerCase();
                const rows = document.querySelectorAll('#telemetryBody tr');
                rows.forEach(row => {
                    const text = row.innerText.toLowerCase();
                    row.style.display = text.includes(query) ? '' : 'none';
                });
            }

            setInterval(fetchTelemetry, 5000);
            fetchTelemetry();
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
