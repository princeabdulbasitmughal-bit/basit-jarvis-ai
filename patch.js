const fs = require('fs');
let html = fs.readFileSync('public/index.html', 'utf8');

const tabReplacement = <button class="engine-tab-btn" data-engine="geminispark" onclick="switchEngineTab('geminispark')">
          <span style="color:#38bdf8;">?</span> <strong>Gemini Spark</strong>
        </button>
        <button class="engine-tab-btn" data-engine="batch" onclick="switchEngineTab('batch')" style="border-color:rgba(245,158,11,0.5);color:#f59e0b;">
          &#x26A1; <strong>Batch Runner</strong>
          <small style="color:#94a3b8;">Multi-Engine Sequential</small>
        </button>;

html = html.replace(/<button class="engine-tab-btn" data-engine="geminispark" onclick="switchEngineTab\('geminispark'\)">[\s\S]*?<\/button>/, match => {
  return match + \n        <button class="engine-tab-btn" data-engine="batch" onclick="switchEngineTab('batch')" style="border-color:rgba(245,158,11,0.5);color:#f59e0b;">\n          &#x26A1; <strong>Batch Runner</strong>\n          <small style="color:#94a3b8;">Multi-Engine Sequential</small>\n        </button>;
});

const panelInsertion = 
        <!-- ===== BATCH RUNNER PANEL ===== -->
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
        </div>
      </div>
    </div> <!-- Close right column -->;

// Find where engine-panels closes. 
// A reliable way is just to search for       </div>\n    </div> <!-- Close right column -->
// Oh I see the file structure in my view. Let's look for <div class="engine-panels"> and trace.

// I can just replace <!-- JS Interactivity (Bilingual Voice & Commands) --> to put it right before script tags
// Wait, the panel should be inside .engine-panels.
