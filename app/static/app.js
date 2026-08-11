const $ = s => document.querySelector(s);
const chatBox = $('#chat-box');
const chatInput = $('#chat-input');
const sendBtn = $('#send-btn');
const modeBadge = $('#mode-badge');
const footerMode = $('#footer-mode');

let history = [
  {role:'assistant', content: 'سلام وحشی! من VAHSHI هستم — مشاور کنکورت.'}
];

// Health
fetch('/health').then(r=>r.json()).then(d=>{
  const online = d.mode === 'online';
  modeBadge.textContent = online ? `● آنلاین — ${d.model}` : '● آفلاین (بدون API Key)';
  modeBadge.className = 'badge ' + (online ? 'online' : 'offline');
  footerMode.textContent = online ? 'حالت آنلاین' : 'حالت آفلاین — برای چت هوشمند OPENAI_API_KEY بذار';
}).catch(()=>{
  modeBadge.textContent = '● آفلاین';
  modeBadge.className = 'badge offline';
});

// Tabs
document.querySelectorAll('.tab').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
    btn.classList.add('active');
    $('#tab-'+btn.dataset.tab).classList.add('active');
    if(btn.dataset.tab==='knowledge') loadKnowledge();
  });
});

function appendMsg(role, text){
  const div = document.createElement('div');
  div.className = 'msg ' + (role==='user' ? 'user' : 'vahshi');
  const avatar = role==='user' ? '🧑' : '🔥';
  div.innerHTML = `<div class="avatar">${avatar}</div><div class="bubble">${escapeHtml(text)}</div>`;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}
function escapeHtml(t){
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
          .replace(/\n/g,'<br>')
          .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>');
}
function addTyping(){
  const d=document.createElement('div');
  d.id='typing'; d.className='msg vahshi';
  d.innerHTML=`<div class="avatar">🔥</div><div class="bubble">وحشی دارم فکر می‌کنم... ⏳</div>`;
  chatBox.appendChild(d); chatBox.scrollTop=chatBox.scrollHeight;
}
function removeTyping(){ const e=$('#typing'); if(e) e.remove(); }

async function send(){
  const text = chatInput.value.trim();
  if(!text) return;
  chatInput.value='';
  appendMsg('user', text);
  history.push({role:'user', content:text});
  addTyping();
  sendBtn.disabled=true;
  try{
    const res = await fetch('/api/chat',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({messages: history})
    });
    const data = await res.json();
    removeTyping();
    const reply = data.reply || 'وحشی خطا خورد — دوباره بفرست';
    appendMsg('assistant', reply);
    history.push({role:'assistant', content: reply});
  }catch(e){
    removeTyping();
    appendMsg('assistant','وحشی اینترنت یا سرور مشکل داره — دوباره امتحان کن');
  }finally{ sendBtn.disabled=false; chatInput.focus(); }
}
sendBtn.addEventListener('click', send);
chatInput.addEventListener('keydown', e=>{
  if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); send(); }
});
document.querySelectorAll('.chip').forEach(c=>{
  c.addEventListener('click', ()=>{ chatInput.value=c.dataset.text; chatInput.focus(); });
});

// Plan
$('#plan-btn').addEventListener('click', async ()=>{
  const body={
    field: $('#plan-field').value,
    grade: $('#plan-grade').value,
    daily_hours: parseFloat($('#plan-hours').value)||6,
    weak_subjects: $('#plan-weak').value.split(',').map(s=>s.trim()).filter(Boolean),
    strong_subjects: $('#plan-strong').value.split(',').map(s=>s.trim()).filter(Boolean),
  };
  const btn=$('#plan-btn'); btn.disabled=true; btn.textContent='دارم می‌سازم...';
  try{
    const r=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const d=await r.json();
    const tip=$('#plan-tip'); tip.textContent='💡 ' + d.tip; tip.classList.remove('hidden');
    const res=$('#plan-result'); res.textContent=d.plan; res.classList.remove('hidden');
    // render markdown table lightly
    res.innerHTML = renderMarkdown(d.plan);
  }catch(e){ alert('خطا: '+e.message)}
  finally{ btn.disabled=false; btn.textContent='برنامه‌ام رو بساز 🔥';}
});

// Evaluate
$('#ev-btn').addEventListener('click', async ()=>{
  const body={
    field: $('#ev-field').value,
    grade: $('#ev-grade').value,
    months_to_konkoor: parseInt($('#ev-months').value)||10,
    daily_hours: parseFloat($('#ev-hours').value)||4,
    azmoon_taraz: $('#ev-taraz').value ? parseInt($('#ev-taraz').value): null,
    target: $('#ev-target').value,
    weak_subjects: $('#ev-weak').value.split(',').map(s=>s.trim()).filter(Boolean),
    strong_subjects: $('#ev-strong').value.split(',').map(s=>s.trim()).filter(Boolean),
  };
  const btn=$('#ev-btn'); btn.disabled=true; btn.textContent='در حال تحلیل...';
  try{
    const r=await fetch('/api/evaluate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const d=await r.json();
    const res=$('#ev-result'); res.innerHTML=renderMarkdown(d.analysis); res.classList.remove('hidden');
  }catch(e){ alert('خطا: '+e.message)}
  finally{ btn.disabled=false; btn.textContent='تحلیل کن وحشی 🧠';}
});

let knowledgeLoaded=false;
async function loadKnowledge(){
  if(knowledgeLoaded) return;
  try{
    const r=await fetch('/api/knowledge'); const d=await r.json();
    const info=d.info;
    let html=`<div style="color:#9a9aa0;font-size:13px;margin-bottom:12px">${info.update_note}</div>`;
    html+=`<h3>ساختار کنکور</h3><ul>`;
    for(const [k,v] of Object.entries(info.structure)) html+=`<li><strong>${k}:</strong> ${v}</li>`;
    html+=`</ul>`;
    html+=`<h3>رشته‌ها</h3>`;
    for(const [field, data] of Object.entries(info.fields)){
      html+=`<div style="background:#232326;border:1px solid #2a2a2e;border-radius:12px;padding:12px;margin:10px 0"><strong>${field}</strong><br>دروس: ${data.اختصاصی.join('، ')}<br>منابع: ${data.منابع_محبوب.join('، ')}</div>`;
    }
    html+=`<h3>تقویم</h3><ul>`;
    for(const [k,v] of Object.entries(info.timeline)) html+=`<li><strong>${k}:</strong> ${v}</li>`;
    html+=`</ul><p style="color:#ffcc00">${d.disclaimer}</p>`;
    $('#knowledge-box').innerHTML=html;
    knowledgeLoaded=true;
  }catch(e){ $('#knowledge-box').textContent='خطا در بارگذاری';}
}

function renderMarkdown(md){
  // minimal markdown: tables, bold, headers
  let html = escapeHtml(md);
  // headers
  html = html.replace(/^### (.*)$/gm,'<h3>$1</h3>');
  html = html.replace(/^## (.*)$/gm,'<h2 style="color:#ffcc00">$1</h2>');
  html = html.replace(/^# (.*)$/gm,'<h1>$1</h1>');
  // tables: detect | lines
  // simple: wrap table rows already escaped, convert | to td
  // We'll do a quick transform: lines with | -> table
  const lines = html.split('<br>');
  let inTable=false; let out=[];
  for(let line of lines){
    if(line.includes('|')){
      if(!inTable){ out.push('<table>'); inTable=true; }
      // split by |
      const cells = line.split('|').filter(c=>c.trim()!=='').map(c=>c.trim());
      // skip separator line
      if(cells.every(c=>/^[-:]+$/.test(c))) continue;
      const tag = out.length && out[out.length-1]==='<table>' ? 'th' : 'td';
      out.push('<tr>' + cells.map(c=>`<${tag}>${c}</${tag}>`).join('') + '</tr>');
    } else {
      if(inTable){ out.push('</table>'); inTable=false; }
      out.push(line + '<br>');
    }
  }
  if(inTable) out.push('</table>');
  html = out.join('');
  // blockquote
  html = html.replace(/&gt; (.*?)<br>/g,'<blockquote style="border-right:3px solid #ff3b30;padding-right:10px;color:#9a9aa0;margin:10px 0">$1</blockquote>');
  return html;
}
