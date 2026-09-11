import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. & 5. Add bottom metrics bar & script BEFORE </body>
metrics_html = '''<!-- ===== REAL-TIME METRICS BAR ===== -->
<div id="metrics-bar" style="position:fixed;bottom:0;left:0;right:0;background:rgba(5,8,17,0.97);border-top:1px solid rgba(0,240,255,0.25);padding:5px 20px;display:flex;gap:20px;align-items:center;z-index:9999;font-size:11.5px;font-family:monospace;backdrop-filter:blur(8px);">
  <span style="color:#00f0ff;font-weight:700;letter-spacing:1px;">&#x1F451; JARVIS</span>
  <span>&#x1F9E0; CPU: <b id="m-cpu" style="color:#10b981;">--</b>%</span>
  <span>&#x1F4BE; RAM: <b id="m-ram" style="color:#3b82f6;">--</b>%</span>
  <span>&#x1F4BE; DISK: <b id="m-disk" style="color:#a855f7;">--</b>%</span>
  <span>&#x23F1; UP: <b id="m-uptime" style="color:#f59e0b;">--</b></span>
  <span>&#x26A1; Engines: <b id="m-engines" style="color:#00f0ff;">8</b></span>
  <span style="margin-left:auto;color:#10b981;font-size:10px;">&#x25CF; ONLINE v2.0-GeminiSpark</span>
</div>
<script>
(function(){
  function fmtUp(s){var h=Math.floor(s/3600),m=Math.floor((s%3600)/60);return h+'h '+m+'m';}
  async function poll(){
    try{
      var r=await fetch('/api/metrics');
      var d=await r.json();
      if(d.success){
        document.getElementById('m-cpu').textContent=d.cpu_percent||'--';
        document.getElementById('m-ram').textContent=d.ram_percent||'--';
        document.getElementById('m-disk').textContent=d.disk_percent||'--';
        document.getElementById('m-uptime').textContent=fmtUp(d.uptime_sec||0);
        document.getElementById('m-engines').textContent=d.engines_online||8;
      }
    }catch(e){}
  }
  poll();
  setInterval(poll,10000);
})();
</script>
<script>
function addBatchTask(){
  var q=document.getElementById('batch-queue');
  var row=document.createElement('div');
  row.style.cssText='display:flex;gap:8px;align-items:center;';
  row.innerHTML='<select style="padding:6px 10px;background:#1e293b;border:1px solid rgba(0,240,255,0.3);border-radius:6px;color:#f8fafc;font-size:12px;"><option value="basit1">Basit1 Code</option><option value="basit2">Basit2 Research</option><option value="basit3">Basit3 Security</option><option value="basit4">Basit4 HedgeFund</option><option value="basitswarm">BasitSwarm</option><option value="basitloop">BasitLoop</option><option value="gemini-spark">Gemini Spark</option></select><input type="text" placeholder="Task description..." style="flex:1;padding:6px 10px;background:#1e293b;border:1px solid rgba(0,240,255,0.3);border-radius:6px;color:#f8fafc;font-size:12px;"><button onclick="this.parentElement.remove()" style="padding:4px 10px;background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);border-radius:6px;color:#ef4444;cursor:pointer;">&#x2715;</button>';
  q.appendChild(row);
}
async function runBatch(){
  var rows=document.querySelectorAll('#batch-queue > div');
  var tasks=[...rows].map(function(r){return{engine:r.querySelector('select').value,task:r.querySelector('input').value};}).filter(function(t){return t.task.trim();});
  if(!tasks.length){alert('Pehle tasks add karo!');return;}
  var out=document.getElementById('batch-output');
  out.style.color='#f59e0b';
  out.textContent='Running '+tasks.length+' tasks... please wait...';
  try{
    var r=await fetch('/api/batch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tasks:tasks})});
    var d=await r.json();
    var result='';
    if(d.results){
      d.results.forEach(function(res,i){
        var icon=res.success?'SUCCESS':'FAIL';
        result+='['+( i+1)+'] '+res.engine+' ('+icon+')\\n';
        result+=(res.summary||'No summary')+'\\n\\n';
      });
    }
    out.style.color='#94a3b8';
    out.textContent=result||JSON.stringify(d,null,2);
  }catch(e){
    out.style.color='#ef4444';
    out.textContent='Error: '+e.message;
  }
}
</script>
</body>'''
content = content.replace('</body>', metrics_html)

# 2. Add padding-bottom: 40px; to body {
content = content.replace('body {', 'body {\n      padding-bottom: 40px;')

# 3. Add Batch Runner tab
tab_html = '''<button class="engine-tab-btn" data-engine="geminispark" onclick="switchEngineTab('geminispark')">
          <span style="color:#38bdf8;">?</span> <strong>Gemini Spark</strong>
        </button>
        <button class="engine-tab-btn" data-engine="batch" onclick="switchEngineTab('batch')" style="border-color:rgba(245,158,11,0.5);color:#f59e0b;">
          &#x26A1; <strong>Batch Runner</strong>
          <small style="color:#94a3b8;">Multi-Engine Sequential</small>
        </button>'''
content = re.sub(r'<button class="engine-tab-btn" data-engine="geminispark" onclick="switchEngineTab\(\'geminispark\'\)">[\s\S]*?<\/button>', tab_html, content)

# 4. Insert Batch Runner Panel before end of engine-panels
panel_html = '''        <!-- ===== BATCH RUNNER PANEL ===== -->
        <div id="panel-batch" class="engine-panel" style="display:none;">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <span style="font-size:2rem;">&#x26A1;</span>
            <div>
              <h3 style="color:#f59e0b;margin:0;">Batch Runner</h3>
              <p style="color:#94a3b8;margin:4px 0 0;font-size:13px;">Queue multiple engines to run sequentially</p>
            </div>
          </div>
          <div id="batch-queue" style="display:flex;flex-direction:column;gap:8px;margin-bottom:12px;"></div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <button onclick="addBatchTask()" style="padding:8px 16px;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.4);border-radius:8px;color:#f59e0b;cursor:pointer;font-size:13px;">+ Add Task</button>
            <button onclick="runBatch()" style="padding:8px 20px;background:rgba(245,158,11,0.3);border:1px solid rgba(245,158,11,0.6);border-radius:8px;color:#f59e0b;font-weight:700;cursor:pointer;font-size:13px;">&#x25B6; Run Batch</button>
            <button onclick="document.getElementById('batch-queue').innerHTML='';document.getElementById('batch-output').textContent='Queue cleared.';" style="padding:8px 16px;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:8px;color:#ef4444;cursor:pointer;font-size:13px;">&#x1F5D1; Clear</button>
          </div>
          <div id="batch-output" style="margin-top:16px;padding:16px;background:rgba(0,0,0,0.35);border:1px solid rgba(245,158,11,0.2);border-radius:10px;min-height:100px;max-height:400px;overflow-y:auto;font-family:monospace;font-size:12px;white-space:pre-wrap;color:#94a3b8;">Queue up tasks above and click Run Batch...</div>
        </div>'''
# Locate the end of engine-panels which is right before the JS Interactivity script
content = content.replace('<!-- JS Interactivity (Bilingual Voice & Commands) -->', panel_html + '\n      </div>\n    </div> <!-- Close right column -->\n  </div> <!-- Close main grid -->\n\n  <!-- JS Interactivity (Bilingual Voice & Commands) -->')
# wait, wait! The original html already has the closing tags! I should just insert before them. Let's see the context.

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
