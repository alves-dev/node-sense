from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NodeSense</title><style>
:root{color-scheme:dark;--bg:#071326;--card:#0d2139;--line:#174362;--text:#e9f4ff;--muted:#8fa9bd;--cyan:#26e0d0;--green:#61ef76}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 80% 0,#123558 0,#071326 45%);color:var(--text);font:15px system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1180px;margin:auto;padding:28px}.hero{display:flex;align-items:center;gap:22px;margin-bottom:24px}.hero img{width:150px;height:92px;object-fit:cover;object-position:center top;border-radius:14px;border:1px solid #1b5473}.hero h1{margin:0;font-size:30px}.hero p{color:var(--muted);margin:5px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}.card{background:linear-gradient(145deg,#102b47,#0a1b30);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 12px 35px #02091466}.label{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}.value{font-size:25px;font-weight:650;margin-top:8px}.wide{grid-column:1/-1}.bar{height:8px;background:#071321;border-radius:8px;overflow:hidden;margin-top:12px}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--cyan),var(--green));border-radius:8px}.status{color:var(--green)}table{width:100%;border-collapse:collapse;margin-top:8px}td{padding:9px 4px;border-bottom:1px solid #173650}td:last-child{text-align:right;color:var(--cyan)}small{color:var(--muted)}
@media(max-width:600px){main{padding:16px}.hero img{width:100px;height:70px}.hero h1{font-size:24px}}
</style></head><body><main><section class="hero"><img src="/logo.png" alt="NodeSense"><div><h1 id="title">NodeSense</h1><p id="subtitle">Host overview</p><small id="updated">Loading…</small></div></section><section class="grid"><div class="card"><div class="label">Operating system</div><div class="value" id="os">—</div><small id="kernel">—</small></div><div class="card"><div class="label">Model</div><div class="value" id="model">—</div></div><div class="card"><div class="label">Uptime</div><div class="value" id="uptime">—</div></div><div class="card"><div class="label">Machine time</div><div class="value" id="datetime">—</div></div><div class="card"><div class="label">CPU</div><div class="value" id="cpu">—</div><small id="cores">—</small><div class="bar"><i id="cpu-bar"></i></div></div><div class="card"><div class="label">Memory</div><div class="value" id="memory">—</div><small id="memory-total">—</small><div class="bar"><i id="memory-bar"></i></div></div><div class="card"><div class="label">Storage</div><div class="value" id="storage">—</div><small id="storage-detail">—</small><div class="bar"><i id="storage-bar"></i></div></div><div class="card"><div class="label">Containers</div><div class="value" id="container-count">—</div><small id="speed-status">Speed test: —</small></div><div class="card wide"><div class="label">Docker containers</div><table><thead><tr><th align="left">Name</th><th align="left">Status</th><th align="right">Memory</th></tr></thead><tbody id="containers"><tr><td>Loading…</td></tr></tbody></table></div></section></main><script>
const byId=id=>document.getElementById(id), fmtBytes=n=>{if(n==null)return '—';const u=['B','KB','MB','GB','TB'];let i=0;while(n>=1024&&i<u.length-1){n/=1024;i++}return `${n.toFixed(i?1:0)} ${u[i]}`}, fmtUptime=s=>{if(s==null)return '—';let d=Math.floor(s/86400);s%=86400;let h=Math.floor(s/3600);s%=3600;let m=Math.floor(s/60);return `${d}d ${h}h ${m}m`}, fmtMachineTime=v=>{if(!v)return '—';const m=v.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.\d+)?([+-]\d{2}:\d{2}|Z)?$/);return m?`${m[1]} ${m[2]} ${m[3]||''}`.trim():v.replace('T',' ').split('.')[0]}, setBar=(id,v)=>byId(id).style.width=v==null?'0%':`${Math.min(100,Math.max(0,v))}%`;
async function refresh(){try{const s=await (await fetch('/api/state',{cache:'no-store'})).json();const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));byId('title').textContent=`NodeSense — ${s.hostname||'Host'}`;byId('subtitle').textContent=s.os||'Linux';byId('updated').textContent=`Updated ${new Date().toLocaleTimeString()}`;byId('os').textContent=s.os||'—';byId('kernel').textContent=`Linux ${s.kernel||'—'}`;byId('model').textContent=s.model||'—';byId('uptime').textContent=fmtUptime(s.uptime_seconds);byId('datetime').textContent=fmtMachineTime(s.datetime);byId('cpu').textContent=s.cpu_usage_pct==null?'—':`${s.cpu_usage_pct.toFixed(1)}%`;byId('cores').textContent=`${s.cpu_cores||'—'} logical CPUs`;setBar('cpu-bar',s.cpu_usage_pct);byId('memory').textContent=s.memory_used_pct==null?'—':`${s.memory_used_pct.toFixed(1)}% used`;byId('memory-total').textContent=`${fmtBytes(s.memory_used_bytes)} / ${fmtBytes(s.memory_total_bytes)}`;setBar('memory-bar',s.memory_used_pct);const st=s.storage||{};byId('storage').textContent=st.used_pct==null?'—':`${st.used_pct.toFixed(1)}% used`;byId('storage-detail').textContent=`${fmtBytes(st.used_bytes)} / ${fmtBytes(st.total_bytes)} (${fmtBytes(st.free_bytes)} free)`;setBar('storage-bar',st.used_pct);byId('container-count').textContent=s.container_count==null?'Unavailable':s.container_count;byId('speed-status').textContent=`Speed test: ${s.speedtest?.status||'idle'}`;byId('containers').innerHTML=(s.containers||[]).map(c=>`<tr><td>${esc(c.name)}</td><td class="status">${esc(c.status)}</td><td align="right">${c.memory_mb==null?'—':`${Number(c.memory_mb).toFixed(1)} MB`}</td></tr>`).join('')||'<tr><td colspan="3">No Docker containers available</td></tr>'}catch(e){byId('updated').textContent='Unable to load status'}}refresh();setInterval(refresh,5000);
</script></body></html>"""


class WebServer:
    def __init__(self, settings, get_state):
        self.settings = settings
        self.get_state = get_state
        self.server = None
        self.thread = None

    def start(self):
        owner = self
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path = urlparse(self.path).path
                if path == "/":
                    body, content_type = HTML.encode(), "text/html; charset=utf-8"
                elif path == "/api/state":
                    body, content_type = json.dumps(owner.get_state(), ensure_ascii=False).encode(), "application/json; charset=utf-8"
                elif path == "/logo.png":
                    try: body, content_type = Path(__file__).parent.parent / "static/nodesense-logo.png", "image/png"; body = body.read_bytes()
                    except OSError: self.send_error(404); return
                else: self.send_error(404); return
                self.send_response(200); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body)
            def log_message(self, *_): return
        self.server = ThreadingHTTPServer((self.settings.web_host, self.settings.web_port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, name="nodesense-web", daemon=True); self.thread.start()

    def close(self):
        if self.server: self.server.shutdown(); self.server.server_close()
