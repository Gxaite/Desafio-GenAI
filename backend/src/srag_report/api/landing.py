"""Página-hub (GET /) — ponto de entrada único para demonstrar o projeto.

HTML leve, sem framework nem CDN (offline/CSP-safe). Consome os endpoints JSON já
existentes via fetch no cliente — não acopla nova lógica de servidor.
"""

from __future__ import annotations

PAGINA = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SRAG · Relatório Automatizado por Agente de IA</title>
<style>
  :root { --bg:#0f172a; --card:#fff; --muted:#64748b; --line:#e2e8f0; --brand:#7c3aed; --accent:#2563eb; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: system-ui, sans-serif; color:#0f172a; background:#f1f5f9; }
  header { background: linear-gradient(120deg,#0f172a,#3730a3); color:#fff; padding:32px 24px; }
  .wrap { max-width: 1040px; margin: 0 auto; }
  header h1 { margin:0 0 6px; font-size:24px; }
  header p { margin:0; color:#c7d2fe; }
  .chips { margin-top:14px; display:flex; gap:8px; flex-wrap:wrap; }
  .chip { background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.2); padding:3px 10px; border-radius:999px; font-size:12px; }
  main { padding: 24px; }
  h2 { font-size:15px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); margin:28px 0 12px; }
  .grid { display:grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap:14px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px; }
  .card .v { font-size:26px; font-weight:800; }
  .card .t { font-size:12px; color:var(--muted); text-transform:uppercase; }
  .card .o { font-size:11px; color:#94a3b8; margin-top:6px; }
  .row { display:flex; gap:12px; flex-wrap:wrap; align-items:center; }
  button, a.btn { background:var(--brand); color:#fff; border:none; padding:11px 18px; border-radius:10px;
    font-size:14px; font-weight:600; cursor:pointer; text-decoration:none; display:inline-block; }
  a.btn.sec { background:#fff; color:var(--accent); border:1px solid var(--accent); }
  #status { color:var(--muted); font-size:13px; }
  table { width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; }
  th,td { text-align:left; padding:9px 12px; border-bottom:1px solid var(--line); font-size:13px; }
  th { background:#f8fafc; color:var(--muted); font-weight:600; }
  .two { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
  @media (max-width:720px){ .two{ grid-template-columns:1fr; } }
  footer { color:var(--muted); font-size:12px; padding:24px; text-align:center; }
</style></head>
<body>
<header><div class="wrap">
  <h1>SRAG · Relatório Automatizado por Agente de IA</h1>
  <p>Agente (LangGraph) consulta dados do Open DATASUS + notícias e gera um relatório com métricas e narrativa.</p>
  <div class="chips">
    <span class="chip">LangGraph</span><span class="chip">Claude · OpenRouter</span>
    <span class="chip">dbt · medallion</span><span class="chip">Postgres</span>
    <span class="chip">FastAPI · hexagonal</span><span class="chip">Docker</span>
  </div>
</div></header>

<main class="wrap">
  <h2>Métricas — últimos 30 dias</h2>
  <div class="grid" id="metricas"><div class="card"><div class="t">carregando…</div></div></div>

  <h2>Relatório do agente</h2>
  <div class="row">
    <button id="gerar">Gerar relatório PDF</button>
    <a class="btn sec" href="/docs" target="_blank">API (Swagger)</a>
    <a class="btn sec" href="/agente/grafo" target="_blank">Grafo do agente</a>
    <a class="btn sec" href="http://localhost:3000/d/srag-overview" target="_blank">Dashboard (Grafana)</a>
    <span id="status"></span>
  </div>

  <h2>Última execução do agente</h2>
  <div class="two">
    <div><h3 style="font-size:13px;color:var(--muted);margin:0 0 8px">Trilha (etapa · duração)</h3>
      <table id="trilha"><tbody><tr><td>carregando…</td></tr></tbody></table></div>
    <div><h3 style="font-size:13px;color:var(--muted);margin:0 0 8px">Fontes consultadas</h3>
      <table id="fontes"><tbody><tr><td>carregando…</td></tr></tbody></table></div>
  </div>
</main>
<footer>PoC · Indicium HealthCare — dados: Open DATASUS (SIVEP-Gripe). Métricas de UTI/vacinação são proxies.</footer>

<script>
async function j(u,o){ const r = await fetch(u,o); if(!r.ok) throw new Error(r.status); return r; }

async function carregarMetricas(){
  try {
    const ms = await (await j('/metricas')).json();
    document.getElementById('metricas').innerHTML = ms.map(m => `
      <div class="card"><div class="t">${m.nome}</div>
        <div class="v">${m.valor===null?'N/A':m.valor+m.unidade}</div>
        <div class="o">N=${m.denominador} · ${m.observacao||''}</div></div>`).join('');
  } catch(e){ document.getElementById('metricas').innerHTML =
      '<div class="card"><div class="t">indisponível — rode o ETL primeiro</div></div>'; }
}

async function carregarExecucao(){
  try {
    const lista = await (await j('/auditoria/execucoes')).json();
    if(!lista.length) return;
    const e = await (await j('/auditoria/execucoes/'+lista[0].run_id)).json();
    document.getElementById('trilha').innerHTML = '<thead><tr><th>Etapa</th><th>Tipo</th><th>ms</th></tr></thead><tbody>'
      + e.eventos.map(v=>`<tr><td>${v.no}</td><td>${v.tipo}</td><td>${v.duracao_ms??''}</td></tr>`).join('') + '</tbody>';
    document.getElementById('fontes').innerHTML = '<thead><tr><th>Fonte</th><th>Notícia</th></tr></thead><tbody>'
      + (e.noticias.length? e.noticias.map(n=>`<tr><td>${n.fonte}</td><td>${n.titulo}</td></tr>`).join('')
         : '<tr><td colspan=2>sem notícias nesta execução</td></tr>') + '</tbody>';
  } catch(err){ /* sem execuções ainda */ }
}

document.getElementById('gerar').onclick = async () => {
  const st = document.getElementById('status');
  st.textContent = 'gerando (agente + LLM)…';
  try {
    const r = await j('/relatorio', {method:'POST'});
    const blob = await r.blob();
    window.open(URL.createObjectURL(blob), '_blank');
    st.textContent = 'pronto · run ' + (r.headers.get('X-Run-Id')||'').slice(0,8);
    carregarExecucao();
  } catch(e){ st.textContent = 'falhou (' + e.message + ')'; }
};

carregarMetricas(); carregarExecucao();
</script>
</body></html>"""
