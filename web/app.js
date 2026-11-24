const $ = id => document.getElementById(id);
let token;
fetch('/api/session').then(r => r.json()).then(data => { token = data.token; });
const node = (tag, className, value) => { const el = document.createElement(tag); if (className) el.className = className; if (value !== undefined) el.textContent = value; return el; };
const levels = [['critical','Crítica'],['high','Alta'],['medium','Media'],['low','Baja'],['info','Informativa']];
$('mode').addEventListener('change', () => {
  const fileMode = $('mode').value === 'file';
  $('file-fields').hidden = !fileMode; $('repo-fields').hidden = fileMode;
  $('file').required = fileMode; $('repo').required = !fileMode; $('base').required = !fileMode;
});
$('form').addEventListener('submit', async event => {
  event.preventDefault(); $('submit').disabled = true; $('submit').textContent = 'Analizando…'; $('status').textContent = 'ANALIZANDO'; $('error').hidden = true;
  try {
    if (!token) throw new Error('No se pudo iniciar la sesión local. Recarga la página.');
    let request;
    if ($('mode').value === 'file') {
      const file = $('file').files[0];
      if (!file || file.size === 0 || file.size > 262144) throw new Error('Selecciona un archivo de texto no vacío de hasta 256 KB.');
      let content;
      try { content = new TextDecoder('utf-8', {fatal:true}).decode(await file.arrayBuffer()); }
      catch { throw new Error('El archivo debe ser texto con codificación UTF-8.'); }
      if (content.includes('\0')) throw new Error('Selecciona un archivo de texto, no un archivo binario.');
      request = {mode:'file',name:file.name,content,provider:$('provider').value};
    } else {
      request = {mode:'diff',repo:$('repo').value,base:$('base').value,provider:$('provider').value};
    }
    const response = await fetch('/api/review', {method:'POST', headers:{'Content-Type':'application/json','X-Review-Token':token}, body:JSON.stringify(request)});
    const data = await response.json(); if (!response.ok) throw new Error(data.error || 'No se pudo completar la revisión.');
    $('empty').hidden = true; $('results').hidden = false; $('status').textContent = data.warnings?.length ? 'REVISIÓN PARCIAL' : 'COMPLETADA';
    $('score').textContent = data.score.score; $('count').textContent = data.findings.length; $('count-label').textContent = `${data.findings.length} resultados`;
    $('scope').textContent = data.scope === 'file' ? 'Archivo' : 'Diff Git'; $('scope-detail').textContent = data.scope === 'file' ? data.base : 'Líneas añadidas';
    $('warnings').hidden = !data.warnings?.length; $('warnings').textContent = (data.warnings || []).join('\n');
    $('chart').replaceChildren(); const max = Math.max(1,...levels.map(([key]) => data.score.counts[key] || 0));
    for (const [key, label] of levels) { const row = node('div','bar-row'); row.append(node('span','bar-label',label)); const track = node('div','track'); const bar = node('div',`bar ${key}`); bar.style.width = `${100*(data.score.counts[key] || 0)/max}%`; track.append(bar); row.append(track,node('strong','',String(data.score.counts[key] || 0))); $('chart').append(row); }
    $('findings').replaceChildren();
    if (!data.findings.length) $('findings').append(node('div','panel finding muted','No se detectaron hallazgos. Esto no garantiza que el cambio esté libre de errores.'));
    for (const f of data.findings) { const card = node('article','panel finding'); const meta = node('div','finding-meta'); meta.append(node('span',`badge ${f.severity}`,f.severity.toUpperCase()),node('span','',f.rule_id),node('span','',f.source)); card.append(meta,node('h4','',f.title),node('p','location',`${f.path}:${f.line} · ${f.category}`),node('pre','',f.evidence),node('p','recommendation',f.recommendation)); $('findings').append(card); }
  } catch (error) { $('error').textContent = error.message; $('error').hidden = false; $('status').textContent = 'ERROR'; }
  finally { $('submit').disabled = false; $('submit').textContent = 'Analizar cambios'; }
});
