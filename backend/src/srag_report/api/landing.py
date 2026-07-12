"""Página-hub (GET /) e página do grafo do agente (GET /agente/grafo).

Não é um dashboard (isso é o Grafana): apresenta o sistema, mostra o retrato atual das
métricas e gera o relatório do agente. HTML/CSS/JS próprios, sem framework nem CDN
(offline/CSP-safe); consome os endpoints JSON via fetch.
"""

from __future__ import annotations

PAGINA = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SRAG · Sistema de Relatórios</title>
<style>
  :root{
    --bg:#ffffff; --soft:#fafafb; --ink:#0b0d12; --muted:#6b7280; --faint:#9aa3af;
    --line:#eceded; --accent:#4f46e5; --accent-weak:#f2f2fd; --ok:#16a34a;
    --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
  }
  *{box-sizing:border-box} html{scroll-behavior:smooth}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,"Segoe UI",Roboto,Inter,system-ui,sans-serif;
    line-height:1.55;-webkit-font-smoothing:antialiased;letter-spacing:-.005em}
  .wrap{max-width:960px;margin:0 auto;padding:0 24px}
  a{color:inherit;text-decoration:none}

  header{position:sticky;top:0;z-index:10;background:rgba(255,255,255,.8);
    backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
  .bar{display:flex;align-items:center;height:64px;gap:14px}
  .brand{display:flex;align-items:center;gap:10px;font-weight:650;font-size:15px}
  .mark{width:26px;height:26px;border-radius:7px;background:var(--ink);color:#fff;
    display:grid;place-items:center;font-size:13px;font-weight:800}
  .sp{flex:1}
  .live{display:inline-flex;align-items:center;gap:7px;font-size:13px;color:var(--muted)}
  .dot{width:7px;height:7px;border-radius:50%;background:var(--faint)}
  .dot.on{background:var(--ok)}
  .nav a{color:var(--muted);font-size:14px;margin-left:20px}
  .nav a:hover{color:var(--ink)}

  .hero{padding:72px 0 20px}
  .eyebrow{font-size:13px;font-weight:600;color:var(--accent);letter-spacing:0}
  .hero h1{font-size:40px;line-height:1.1;letter-spacing:-.03em;margin:14px 0 16px;max-width:16ch;font-weight:700}
  .hero p{font-size:17px;color:var(--muted);max-width:58ch;margin:0 0 26px}
  .cta{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
  .btn{border:none;cursor:pointer;font:inherit;font-size:14px;font-weight:550;
    padding:11px 18px;border-radius:9px;display:inline-flex;align-items:center;gap:8px;transition:.15s}
  .btn.primary{background:var(--ink);color:#fff}
  .btn.primary:hover{background:#242833}
  .btn.ghost{background:var(--bg);color:var(--ink);border:1px solid var(--line)}
  .btn.ghost:hover{background:var(--soft)}
  .btn[disabled]{opacity:.55;cursor:progress}

  h2{font-size:13px;font-weight:600;color:var(--faint);letter-spacing:.02em;margin:56px 0 16px}
  .card{background:var(--bg);border:1px solid var(--line);border-radius:14px}

  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
  .kpi{padding:18px}
  .kpi .l{font-size:12.5px;color:var(--muted);display:flex;align-items:center;gap:7px}
  .kpi .l::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--c,var(--accent))}
  .kpi .v{font-size:30px;font-weight:700;letter-spacing:-.02em;margin-top:8px;font-variant-numeric:tabular-nums}
  .kpi .c{font-size:12px;color:var(--faint);margin-top:2px}

  .steps{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
  .step{padding:18px}
  .step .n{width:24px;height:24px;border-radius:50%;border:1px solid var(--line);
    color:var(--muted);font-weight:650;font-size:12px;display:grid;place-items:center;margin-bottom:12px}
  .step h3{font-size:14.5px;margin:0 0 5px;font-weight:600}
  .step p{font-size:13px;color:var(--muted);margin:0}

  .report{padding:24px;display:flex;gap:24px;align-items:center;flex-wrap:wrap}
  .report .txt{flex:1;min-width:240px}
  .report h3{margin:0 0 5px;font-size:18px;font-weight:650}
  .report p{margin:0;color:var(--muted);font-size:14.5px}
  #status{font-size:13.5px;color:var(--muted);min-height:18px;margin-top:14px}
  #status b{font-family:var(--mono);color:var(--ink);font-weight:600;font-size:12.5px}

  .two{display:grid;grid-template-columns:1.25fr 1fr;gap:12px}
  .panel{padding:20px}
  .panel h3{margin:0 0 16px;font-size:12.5px;color:var(--faint);font-weight:600;letter-spacing:.02em}
  .trail{display:flex;flex-direction:column;gap:12px}
  .trail .r{display:grid;grid-template-columns:90px 1fr 62px;align-items:center;gap:12px;font-size:13.5px}
  .trail .no{font-weight:550}
  .trail .bar{height:6px;border-radius:99px;background:var(--soft)}
  .trail .bar i{display:block;height:100%;background:var(--accent);border-radius:99px}
  .trail .ms{color:var(--faint);text-align:right;font-variant-numeric:tabular-nums;font-size:12.5px}
  .src{display:flex;flex-direction:column;gap:14px}
  .src .i{font-size:13.5px;line-height:1.4}
  .src .f{display:inline-block;font-size:11px;font-weight:600;color:var(--muted);
    background:var(--soft);border:1px solid var(--line);padding:1px 8px;border-radius:99px;margin-bottom:5px}

  footer{color:var(--faint);font-size:13px;padding:44px 0 40px;text-align:center;
    border-top:1px solid var(--line);margin-top:64px;line-height:1.7}
  .tech{margin-top:8px;color:var(--muted);font-size:12.5px}

  @media(max-width:820px){.kpis,.steps{grid-template-columns:repeat(2,1fr)}.two{grid-template-columns:1fr}.hero h1{font-size:30px}}
</style></head>
<body>
<header><div class="wrap bar">
  <span class="brand"><span class="mark">S</span> SRAG Relatórios</span>
  <span class="sp"></span>
  <span class="live"><span class="dot" id="dot"></span><span id="livet">verificando</span></span>
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
    <p>Um agente orquestrador consulta o Open DATASUS e notícias em tempo real, calcula as
       métricas de forma determinística e produz um relatório com narrativa fundamentada.
       Cada passo fica registrado na trilha de auditoria.</p>
    <div class="cta">
      <button class="btn primary" id="gerar">Gerar relatório</button>
      <a class="btn ghost" href="http://localhost:3000/d/srag-overview" target="_blank">Explorar no Grafana</a>
    </div>
    <div id="status"></div>
  </section>

  <h2>Métricas dos últimos 30 dias</h2>
  <div class="kpis" id="kpis"><div class="card kpi"><div class="l">carregando</div></div></div>

  <h2>Como o agente trabalha</h2>
  <div class="steps">
    <div class="card step"><div class="n">1</div><h3>Métricas</h3><p>Calcula as quatro taxas no banco, em SQL determinístico.</p></div>
    <div class="card step"><div class="n">2</div><h3>Gráficos</h3><p>Séries de casos diários (30 dias) e mensais (12 meses).</p></div>
    <div class="card step"><div class="n">3</div><h3>Notícias</h3><p>Busca e filtra notícias de SRAG em tempo real.</p></div>
    <div class="card step"><div class="n">4</div><h3>Narrativa</h3><p>O LLM contextualiza usando apenas os números apurados.</p></div>
  </div>

  <h2>Gerar relatório do sistema</h2>
  <div class="card report">
    <div class="txt">
      <h3>Relatório em PDF</h3>
      <p>Executa o agente de ponta a ponta e monta o PDF com as quatro métricas, os dois gráficos, a narrativa e o rodapé de transparência.</p>
    </div>
    <button class="btn primary" id="gerar2">Gerar agora</button>
  </div>

  <h2>Última execução do agente</h2>
  <div class="two">
    <div class="card panel"><h3>Trilha por etapa</h3><div class="trail" id="trail">carregando</div></div>
    <div class="card panel"><h3>Fontes consultadas</h3><div class="src" id="src">carregando</div></div>
  </div>
</main>

<footer>
  Dados do Open DATASUS (SIVEP-Gripe). Métricas de UTI e vacinação são proxies por caso.
  Os números são calculados deterministicamente e a narrativa é escrita pelo LLM sobre eles.
  <div class="tech">LangGraph · Claude via OpenRouter · dbt medallion · Postgres · FastAPI hexagonal · Docker</div>
</footer>

<script>
const $ = s => document.querySelector(s);
async function j(u,o){ const r=await fetch(u,o); if(!r.ok) throw new Error(r.status); return r; }
const cor = n => n.includes('mortal')?'#dc2626':n.includes('UTI')?'#2563eb':n.includes('acina')?'#7c3aed':'#4f46e5';

async function health(){
  try{ await j('/health'); $('#dot').className='dot on'; $('#livet').textContent='no ar'; }
  catch{ $('#livet').textContent='indisponível'; }
}
async function kpis(){
  try{
    const ms = await (await j('/metricas')).json();
    $('#kpis').innerHTML = ms.map(m=>`<div class="card kpi">
      <div class="l" style="--c:${cor(m.nome)}">${m.nome}</div>
      <div class="v">${m.valor===null?'N/A':m.valor+m.unidade}</div>
      <div class="c">base de ${m.denominador.toLocaleString('pt-BR')}</div></div>`).join('');
  }catch{ $('#kpis').innerHTML='<div class="card kpi"><div class="l">indisponível, rode o ETL</div></div>'; }
}
async function execucao(){
  try{
    const lst = await (await j('/auditoria/execucoes')).json();
    if(!lst.length){ $('#trail').textContent='nenhuma execução ainda'; $('#src').textContent=''; return; }
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
  const bs=[$('#gerar'),$('#gerar2')]; bs.forEach(b=>b.disabled=true);
  $('#status').textContent='Executando o agente. Isso leva alguns segundos.';
  try{
    const r = await j('/relatorio',{method:'POST'});
    window.open(URL.createObjectURL(await r.blob()),'_blank');
    $('#status').innerHTML='Relatório pronto. Execução <b>'+(r.headers.get('X-Run-Id')||'').slice(0,12)+'</b>';
    execucao();
  }catch(e){ $('#status').textContent='Não foi possível gerar ('+e.message+'). Verifique as chaves e o ETL.'; }
  finally{ bs.forEach(b=>b.disabled=false); }
}
$('#gerar').onclick=gerar; $('#gerar2').onclick=gerar;
health(); kpis(); execucao();
</script>
</body></html>"""


GRAFO = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Grafo do agente · SRAG</title>
<style>
  :root{--bg:#fff;--soft:#fafafb;--ink:#0b0d12;--muted:#6b7280;--faint:#9aa3af;
    --line:#eceded;--accent:#4f46e5;--accent-weak:#f2f2fd;--mono:ui-monospace,Menlo,monospace}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,"Segoe UI",Roboto,Inter,system-ui,sans-serif;letter-spacing:-.005em}
  .wrap{max-width:960px;margin:0 auto;padding:0 24px}
  a{color:inherit;text-decoration:none}
  header{border-bottom:1px solid var(--line)}
  .bar{display:flex;align-items:center;height:64px;gap:14px}
  .brand{display:flex;align-items:center;gap:10px;font-weight:650;font-size:15px}
  .mark{width:26px;height:26px;border-radius:7px;background:var(--ink);color:#fff;
    display:grid;place-items:center;font-size:13px;font-weight:800}
  .sp{flex:1}
  .back{color:var(--muted);font-size:14px}.back:hover{color:var(--ink)}
  .hero{padding:56px 0 8px}
  .eyebrow{font-size:13px;font-weight:600;color:var(--accent)}
  h1{font-size:32px;line-height:1.1;letter-spacing:-.03em;margin:12px 0 10px;font-weight:700}
  .hero p{color:var(--muted);font-size:16px;max-width:60ch;margin:0}

  .flow{display:flex;align-items:stretch;gap:0;flex-wrap:wrap;margin:44px 0 24px}
  .cap{align-self:center;font-size:12px;font-weight:600;color:var(--muted);
    background:var(--soft);border:1px solid var(--line);border-radius:99px;padding:6px 12px;white-space:nowrap}
  .node{flex:1;min-width:150px;background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:16px}
  .node .nn{width:24px;height:24px;border-radius:50%;background:var(--accent-weak);color:var(--accent);
    font-weight:700;font-size:12px;display:grid;place-items:center;margin-bottom:10px}
  .node .nt{font-size:15px;font-weight:650;margin-bottom:3px}
  .node .ns{font-size:12px;color:var(--muted)}
  .node .tag{display:inline-block;margin-top:10px;font-size:11px;color:var(--muted);
    font-family:var(--mono);background:var(--soft);border:1px solid var(--line);padding:1px 7px;border-radius:6px}
  .arrow{align-self:center;color:var(--faint);padding:0 10px;font-size:18px}
  @media(max-width:760px){ .flow{flex-direction:column} .arrow{transform:rotate(90deg);padding:8px 0} .node,.cap{width:100%} }

  .note{color:var(--muted);font-size:13.5px;margin-top:20px;line-height:1.6}
  .src{margin-top:28px;font-size:12.5px}
  .src a{color:var(--accent)}
  footer{color:var(--faint);font-size:13px;padding:40px 0;text-align:center;border-top:1px solid var(--line);margin-top:56px}
</style></head>
<body>
<header><div class="wrap bar">
  <span class="brand"><span class="mark">S</span> SRAG Relatórios</span>
  <span class="sp"></span>
  <a class="back" href="/">voltar ao hub</a>
</div></header>

<main class="wrap">
  <section class="hero">
    <div class="eyebrow">Orquestração</div>
    <h1>Fluxo do agente</h1>
    <p>Grafo linear em LangGraph. Cada nó é um passo auditável: as três tools alimentam o
       estado e o nó de narrativa contextualiza com o LLM.</p>
  </section>

  <div class="flow">
    <span class="cap">início</span>
    <span class="arrow">&rarr;</span>
    <div class="node"><div class="nn">1</div><div class="nt">Métricas</div>
      <div class="ns">calcula as quatro taxas</div><span class="tag">gold</span></div>
    <span class="arrow">&rarr;</span>
    <div class="node"><div class="nn">2</div><div class="nt">Gráficos</div>
      <div class="ns">séries 30 dias e 12 meses</div><span class="tag">gold</span></div>
    <span class="arrow">&rarr;</span>
    <div class="node"><div class="nn">3</div><div class="nt">Notícias</div>
      <div class="ns">busca e filtra em tempo real</div><span class="tag">NewsAPI</span></div>
    <span class="arrow">&rarr;</span>
    <div class="node"><div class="nn">4</div><div class="nt">Narrativa</div>
      <div class="ns">contextualiza os números</div><span class="tag">LLM</span></div>
    <span class="arrow">&rarr;</span>
    <span class="cap">relatório</span>
  </div>

  <p class="note">Notícias e LLM têm degradação graciosa: se falharem, o relatório sai mesmo
     assim (sem notícias, com narrativa determinística). Cada passo grava duração e resultado
     na trilha de auditoria.</p>
  <p class="src">Fonte do grafo em Mermaid: <a href="/agente/grafo?format=mermaid">/agente/grafo?format=mermaid</a></p>
</main>
<footer>SRAG Relatórios · agente orquestrador em LangGraph</footer>
</body></html>"""
