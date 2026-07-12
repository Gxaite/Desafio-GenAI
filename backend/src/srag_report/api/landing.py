"""Página-hub (GET /) — ponto de entrada para apresentar e operar o sistema.

Não é um dashboard (isso é o Grafana): é um hub que apresenta o sistema, mostra o retrato
atual das métricas e permite gerar o relatório do agente. HTML/CSS/JS próprios, sem framework
nem CDN (offline/CSP-safe); consome os endpoints JSON via fetch.
"""

from __future__ import annotations

PAGINA = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SRAG · Sistema de Relatórios</title>
<style>
  :root{
    --bg:#f6f7f9; --surface:#fff; --ink:#0f172a; --muted:#5b6b7f; --faint:#94a3b8;
    --line:#e6e8ec; --accent:#4f46e5; --accent-weak:#eef2ff; --ring:rgba(79,70,229,.18);
    --ok:#16a34a; --warn:#d97706; --bad:#dc2626;
    --shadow:0 1px 2px rgba(16,24,40,.04),0 4px 16px rgba(16,24,40,.05);
    --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
  }
  *{box-sizing:border-box} html{scroll-behavior:smooth}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,"Segoe UI",Roboto,Inter,system-ui,sans-serif;line-height:1.5;}
  .wrap{max-width:1060px;margin:0 auto;padding:0 24px}
  a{color:inherit}

  /* topo */
  header{position:sticky;top:0;z-index:10;background:rgba(255,255,255,.85);
    backdrop-filter:saturate(1.4) blur(8px);border-bottom:1px solid var(--line)}
  .bar{display:flex;align-items:center;gap:12px;height:60px}
  .brand{display:flex;align-items:center;gap:10px;font-weight:700}
  .mark{width:30px;height:30px;border-radius:8px;background:linear-gradient(135deg,#4f46e5,#7c3aed);
    display:grid;place-items:center;color:#fff;font-size:15px;font-weight:800}
  .bar .sp{flex:1}
  .nav a{color:var(--muted);text-decoration:none;font-size:14px;font-weight:500;margin-left:18px}
  .nav a:hover{color:var(--ink)}
  .live{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;color:var(--muted)}
  .dot{width:8px;height:8px;border-radius:50%;background:var(--faint)}
  .dot.on{background:var(--ok);box-shadow:0 0 0 3px rgba(22,163,74,.15)}

  /* hero */
  .hero{padding:52px 0 30px}
  .eyebrow{font-size:12.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
  .hero h1{font-size:34px;line-height:1.15;margin:12px 0 10px;letter-spacing:-.02em;max-width:20ch}
  .hero p{font-size:16px;color:var(--muted);max-width:60ch;margin:0 0 22px}
  .cta{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
  .btn{border:none;cursor:pointer;font:inherit;font-size:14px;font-weight:600;
    padding:11px 18px;border-radius:10px;text-decoration:none;display:inline-flex;align-items:center;gap:8px}
  .btn.primary{background:var(--accent);color:#fff;box-shadow:var(--shadow)}
  .btn.primary:hover{background:#4338ca}
  .btn.ghost{background:var(--surface);color:var(--ink);border:1px solid var(--line)}
  .btn.ghost:hover{border-color:#cbd5e1}
  .btn[disabled]{opacity:.6;cursor:progress}

  h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--faint);margin:40px 0 14px}
  .card{background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow)}

  /* kpis */
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
  .kpi{padding:16px 16px 15px;position:relative;overflow:hidden}
  .kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--c,var(--accent))}
  .kpi .l{font-size:12px;color:var(--muted);font-weight:600}
  .kpi .v{font-size:27px;font-weight:800;letter-spacing:-.02em;margin-top:4px;font-variant-numeric:tabular-nums}
  .kpi .c{font-size:11.5px;color:var(--faint);margin-top:4px}

  /* passos do agente */
  .steps{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
  .step{padding:16px}
  .step .n{width:26px;height:26px;border-radius:8px;background:var(--accent-weak);color:var(--accent);
    font-weight:800;font-size:13px;display:grid;place-items:center;margin-bottom:10px}
  .step h3{font-size:14px;margin:0 0 4px}
  .step p{font-size:12.5px;color:var(--muted);margin:0}

  /* relatório */
  .report{padding:22px;display:flex;gap:22px;align-items:center;flex-wrap:wrap;
    background:linear-gradient(180deg,#fff, #fbfbff);border-color:#e7e5ff}
  .report .txt{flex:1;min-width:240px}
  .report h3{margin:0 0 4px;font-size:17px}
  .report p{margin:0;color:var(--muted);font-size:14px}
  #status{font-size:13px;color:var(--muted);min-height:18px;margin-top:10px}
  #status b{font-family:var(--mono);color:var(--ink);font-weight:600}

  /* execução */
  .two{display:grid;grid-template-columns:1.3fr 1fr;gap:16px}
  .panel{padding:18px}
  .panel h3{margin:0 0 12px;font-size:13px;color:var(--faint);text-transform:uppercase;letter-spacing:.05em}
  .trail{display:flex;flex-direction:column;gap:9px}
  .trail .r{display:grid;grid-template-columns:96px 1fr auto;align-items:center;gap:10px;font-size:13px}
  .trail .no{font-weight:600}
  .trail .bar{height:7px;border-radius:99px;background:var(--accent-weak);overflow:hidden}
  .trail .bar i{display:block;height:100%;background:var(--accent);border-radius:99px}
  .trail .ms{color:var(--faint);font-variant-numeric:tabular-nums;font-size:12px}
  .src{display:flex;flex-direction:column;gap:8px}
  .src .i{font-size:13px}
  .src .f{display:inline-block;font-size:11px;font-weight:600;color:var(--accent);
    background:var(--accent-weak);padding:1px 8px;border-radius:99px;margin-bottom:2px}

  footer{color:var(--faint);font-size:12.5px;padding:34px 0;text-align:center;border-top:1px solid var(--line);margin-top:44px}
  .chips{margin-top:10px;display:flex;gap:7px;flex-wrap:wrap;justify-content:center}
  .chip{border:1px solid var(--line);color:var(--muted);padding:2px 10px;border-radius:99px;font-size:11.5px}

  @media(max-width:820px){ .kpis,.steps{grid-template-columns:repeat(2,1fr)} .two{grid-template-columns:1fr} .hero h1{font-size:27px} }
</style></head>
<body>
<header><div class="wrap bar">
  <span class="brand"><span class="mark">S</span> SRAG · Sistema de Relatórios</span>
  <span class="sp"></span>
  <span class="live"><span class="dot" id="dot"></span><span id="livet">verificando…</span></span>
  <nav class="nav">
    <a href="http://localhost:3000/d/srag-overview" target="_blank">Grafana</a>
    <a href="/docs" target="_blank">API</a>
    <a href="/agente/grafo" target="_blank">Grafo</a>
  </nav>
</div></header>

<main class="wrap">
  <section class="hero">
    <div class="eyebrow">PoC · Indicium HealthCare</div>
    <h1>Relatórios de SRAG gerados por um agente de IA.</h1>
    <p>Um agente orquestrador consulta os dados do Open DATASUS e notícias em tempo real,
       calcula as métricas de forma determinística e produz um relatório com narrativa
       fundamentada — com trilha de auditoria de cada passo.</p>
    <div class="cta">
      <button class="btn primary" id="gerar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
        Gerar relatório
      </button>
      <a class="btn ghost" href="http://localhost:3000/d/srag-overview" target="_blank">Explorar no Grafana</a>
    </div>
    <div id="status"></div>
  </section>

  <h2>Métricas — últimos 30 dias</h2>
  <div class="kpis" id="kpis">
    <div class="card kpi"><div class="l">carregando…</div></div>
  </div>

  <h2>Como o agente trabalha</h2>
  <div class="steps">
    <div class="card step"><div class="n">1</div><h3>Métricas</h3><p>Calcula as 4 taxas no banco (SQL determinístico).</p></div>
    <div class="card step"><div class="n">2</div><h3>Gráficos</h3><p>Séries de casos diários (30d) e mensais (12m).</p></div>
    <div class="card step"><div class="n">3</div><h3>Notícias</h3><p>Busca e filtra notícias de SRAG em tempo real.</p></div>
    <div class="card step"><div class="n">4</div><h3>Narrativa</h3><p>O LLM contextualiza — só sobre os números apurados.</p></div>
  </div>

  <h2>Gerar relatório do sistema</h2>
  <div class="card report">
    <div class="txt">
      <h3>Relatório em PDF</h3>
      <p>Executa o agente ponta a ponta e monta o PDF (4 métricas + 2 gráficos + narrativa + rodapé de transparência).</p>
    </div>
    <button class="btn primary" id="gerar2">Gerar agora</button>
  </div>

  <h2>Última execução do agente</h2>
  <div class="two">
    <div class="card panel"><h3>Trilha (etapa · duração)</h3><div class="trail" id="trail">—</div></div>
    <div class="card panel"><h3>Fontes consultadas</h3><div class="src" id="src">—</div></div>
  </div>
</main>

<footer>
  Dados: Open DATASUS (SIVEP-Gripe). Métricas de UTI e vacinação são <b>proxies</b> (status por caso).
  Números calculados deterministicamente; narrativa por LLM sobre esses números.
  <div class="chips">
    <span class="chip">LangGraph</span><span class="chip">Claude · OpenRouter</span>
    <span class="chip">dbt · medallion</span><span class="chip">Postgres</span>
    <span class="chip">FastAPI · hexagonal</span><span class="chip">Docker</span>
  </div>
</footer>

<script>
const $ = s => document.querySelector(s);
async function j(u,o){ const r=await fetch(u,o); if(!r.ok) throw new Error(r.status); return r; }
const cor = n => n.includes('mortal')?'#dc2626':n.includes('UTI')?'#2563eb':n.includes('acina')?'#7c3aed':'#4f46e5';

async function health(){
  try{ await j('/health'); $('#dot').className='dot on'; $('#livet').textContent='sistema no ar'; }
  catch{ $('#livet').textContent='sistema indisponível'; }
}
async function kpis(){
  try{
    const ms = await (await j('/metricas')).json();
    $('#kpis').innerHTML = ms.map(m=>`<div class="card kpi" style="--c:${cor(m.nome)}">
      <div class="l">${m.nome}</div>
      <div class="v">${m.valor===null?'N/A':m.valor+m.unidade}</div>
      <div class="c">N=${m.denominador}</div></div>`).join('');
  }catch{ $('#kpis').innerHTML='<div class="card kpi"><div class="l">indisponível — rode o ETL</div></div>'; }
}
async function execucao(){
  try{
    const lst = await (await j('/auditoria/execucoes')).json();
    if(!lst.length) return;
    const e = await (await j('/auditoria/execucoes/'+lst[0].run_id)).json();
    const max = Math.max(1, ...e.eventos.map(v=>v.duracao_ms||0));
    $('#trail').innerHTML = e.eventos.map(v=>`<div class="r">
      <span class="no">${v.no}</span>
      <span class="bar"><i style="width:${Math.round(100*(v.duracao_ms||0)/max)}%"></i></span>
      <span class="ms">${v.duracao_ms??''} ms</span></div>`).join('');
    $('#src').innerHTML = e.noticias.length
      ? e.noticias.map(n=>`<div class="i"><span class="f">${n.fonte}</span><br>${n.titulo}</div>`).join('')
      : '<div class="i" style="color:var(--faint)">sem notícias nesta execução</div>';
  }catch{}
}
async function gerar(){
  const btns=[$('#gerar'),$('#gerar2')]; btns.forEach(b=>b.disabled=true);
  $('#status').textContent='Executando o agente (métricas → gráficos → notícias → narrativa)…';
  try{
    const r = await j('/relatorio',{method:'POST'});
    window.open(URL.createObjectURL(await r.blob()),'_blank');
    $('#status').innerHTML='Relatório pronto · run <b>'+(r.headers.get('X-Run-Id')||'').slice(0,12)+'</b>';
    execucao();
  }catch(e){ $('#status').textContent='Falhou ('+e.message+'). Confirme as chaves no .env e o ETL.'; }
  finally{ btns.forEach(b=>b.disabled=false); }
}
$('#gerar').onclick=gerar; $('#gerar2').onclick=gerar;
health(); kpis(); execucao();
</script>
</body></html>"""
