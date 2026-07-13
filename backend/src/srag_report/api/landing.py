"""Página-hub (GET /) e página do grafo do agente (GET /agente/grafo).

Não é um dashboard (isso é o Grafana): apresenta o sistema, mostra o retrato atual das
métricas, gera o relatório e traz um waterfall da última execução do agente. HTML/CSS/JS
próprios, sem framework nem CDN (offline/CSP-safe); consome os endpoints JSON via fetch.
"""

from __future__ import annotations

PAGINA = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SRAG · Sistema de Relatórios</title>
<style>
  :root{
    --bg:#fbfbfd; --panel:#ffffff; --soft:#f4f4f7; --ink:#0b0d12; --muted:#5f6673; --faint:#9aa3af;
    --line:#ebebef; --accent:#4f46e5; --accent2:#7c3aed; --accent-weak:#eef0ff; --ok:#16a34a;
    --header:rgba(251,251,253,.8);
    --shadow:0 1px 2px rgba(16,18,27,.05), 0 14px 30px -16px rgba(16,18,27,.16);
    --shadow-lg:0 2px 8px rgba(16,18,27,.07), 0 28px 54px -22px rgba(16,18,27,.26);
    --radius:16px;
    --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
  }
  /* Tema claro por padrão; escuro só quando o usuário aciona o toggle (data-theme). */
  :root[data-theme="dark"]{
    --bg:#0a0b0f; --panel:#14161f; --soft:#1b1e2a; --ink:#f1f3f8; --muted:#9aa2b1; --faint:#6a7285;
    --line:#242838; --accent:#8b93f8; --accent2:#a78bfa; --accent-weak:#1d2133; --ok:#34d399;
    --header:rgba(10,11,15,.72);
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 14px 32px -16px rgba(0,0,0,.6);
    --shadow-lg:0 2px 10px rgba(0,0,0,.5), 0 30px 60px -22px rgba(0,0,0,.72);
  }
  *{box-sizing:border-box} html{scroll-behavior:smooth}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,"Segoe UI",Roboto,Inter,system-ui,sans-serif;
    line-height:1.55;-webkit-font-smoothing:antialiased;letter-spacing:-.005em}
  .wrap{max-width:940px;margin:0 auto;padding:0 24px}
  a{color:inherit;text-decoration:none}

  header{position:sticky;top:0;z-index:10;background:var(--header);
    backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
  .bar{display:flex;align-items:center;height:64px;gap:14px}
  .brand{display:flex;align-items:center;gap:10px;font-weight:650;font-size:15px}
  .mark{width:28px;height:28px;border-radius:8px;
    background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;
    display:grid;place-items:center;font-size:13px;font-weight:800;
    box-shadow:0 4px 12px -4px color-mix(in srgb,var(--accent) 70%,transparent)}
  .sp{flex:1}
  .live{display:inline-flex;align-items:center;gap:7px;font-size:13px;color:var(--muted)}
  .dot{width:7px;height:7px;border-radius:50%;background:var(--faint)}
  .dot.on{background:var(--ok)}
  .nav a{color:var(--muted);font-size:14px;margin-left:20px}
  .nav a:hover{color:var(--ink)}
  .tbtn{margin-left:20px;width:34px;height:34px;border-radius:9px;border:1px solid var(--line);
    background:var(--panel);color:var(--muted);cursor:pointer;font-size:15px;line-height:1;
    display:grid;place-items:center;transition:.15s}
  .tbtn:hover{color:var(--ink);border-color:color-mix(in srgb,var(--accent) 30%,var(--line))}

  /* tudo centralizado e simétrico */
  .hero{text-align:center;padding:92px 0 24px;position:relative}
  .hero::before{content:"";position:absolute;top:-30px;left:50%;transform:translateX(-50%);
    width:720px;height:380px;max-width:110%;pointer-events:none;z-index:-1;
    background:radial-gradient(58% 60% at 50% 38%,var(--accent-weak),transparent 72%);opacity:.85}
  .eyebrow{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:600;
    color:var(--accent);background:var(--accent-weak);padding:6px 13px;border-radius:99px;
    border:1px solid color-mix(in srgb,var(--accent) 20%,transparent)}
  .hero h1{font-size:44px;line-height:1.06;letter-spacing:-.035em;margin:18px auto 16px;
    max-width:18ch;font-weight:700;color:var(--ink)}
  .hero p{font-size:17px;color:var(--muted);max-width:56ch;margin:0 auto 28px}
  .cta{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;align-items:center}
  .btn{border:none;cursor:pointer;font:inherit;font-size:14px;font-weight:550;
    padding:11px 20px;border-radius:9px;display:inline-flex;align-items:center;gap:8px;transition:.15s}
  .btn.primary{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;
    box-shadow:0 10px 22px -10px color-mix(in srgb,var(--accent) 75%,transparent)}
  .btn.primary:hover{filter:brightness(1.07);transform:translateY(-1px)}
  .btn.ghost{background:var(--panel);color:var(--ink);border:1px solid var(--line)}
  .btn.ghost:hover{background:var(--soft);border-color:color-mix(in srgb,var(--accent) 30%,var(--line))}
  .btn[disabled]{opacity:.55;cursor:progress}
  #status{font-size:13.5px;color:var(--muted);min-height:20px;margin-top:16px;text-align:center}
  #status b{font-family:var(--mono);color:var(--ink);font-weight:600;font-size:12.5px}

  .sec{text-align:center;font-size:12.5px;font-weight:600;color:var(--faint);
    letter-spacing:.04em;text-transform:uppercase;margin:64px 0 18px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
    box-shadow:var(--shadow)}

  .grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
  .kpi{padding:24px 20px;text-align:center;position:relative;overflow:hidden;
    transition:box-shadow .2s,transform .2s}
  .kpi::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,var(--c,var(--accent)),transparent)}
  .kpi:hover{transform:translateY(-3px);box-shadow:var(--shadow-lg)}
  .kpi .l{font-size:12.5px;color:var(--muted);display:flex;justify-content:center;align-items:center;gap:7px}
  .kpi .l::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--c,var(--accent))}
  .kpi .v{font-size:32px;font-weight:800;letter-spacing:-.025em;margin-top:10px;
    font-variant-numeric:tabular-nums;color:var(--ink)}
  .kpi .c{font-size:12px;color:var(--faint);margin-top:4px}
  .kpi .obs{font-size:10.5px;color:var(--faint);margin-top:10px;line-height:1.4;
    padding-top:10px;border-top:1px solid var(--line)}

  .step{padding:22px 18px;text-align:center;transition:box-shadow .2s,border-color .2s}
  .step .n{width:36px;height:36px;border-radius:11px;background:var(--accent-weak);color:var(--accent);
    border:1px solid color-mix(in srgb,var(--accent) 18%,transparent);
    font-weight:700;font-size:14px;display:grid;place-items:center;margin:0 auto 12px;transition:.2s}
  .step h3{font-size:14.5px;margin:0 0 5px;font-weight:600}
  .step p{font-size:13px;color:var(--muted);margin:0 auto;max-width:24ch}
  .step .sms{font-size:11px;color:var(--faint);margin-top:8px;min-height:14px;font-variant-numeric:tabular-nums}
  .step:hover{transform:translateY(-3px);box-shadow:var(--shadow-lg)}
  .step.run{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-weak)}
  .step.run .n{border-color:var(--accent);color:var(--accent)}
  .step.done .n{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border-color:transparent}

  .report{padding:32px 24px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:6px}
  .report h3{margin:0;font-size:19px;font-weight:650}
  .report p{margin:0 auto 6px;color:var(--muted);font-size:14.5px;max-width:52ch}

  /* waterfall */
  .trace{padding:22px 24px}
  .thead{display:flex;justify-content:center;align-items:center;gap:10px;font-size:13px;color:var(--muted);margin-bottom:20px}
  .thead b{font-family:var(--mono);color:var(--ink);font-weight:600;font-size:12px}
  .wf{display:grid;grid-template-columns:92px 1fr 64px;align-items:center;gap:14px;margin:11px 0}
  .wf .l{font-weight:550;text-align:right;font-size:13.5px}
  .wf .track{position:relative;height:10px;background:var(--soft);border-radius:99px}
  .wf .track i{position:absolute;top:0;height:100%;background:var(--ink);border-radius:99px;min-width:3px}
  .wf .track i.llm{background:var(--accent)}
  .wf .d{color:var(--faint);text-align:right;font-variant-numeric:tabular-nums;font-size:12.5px}
  .srcs{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:22px;padding-top:18px;border-top:1px solid var(--line)}
  .srcs .s{font-size:12.5px;color:var(--muted);border:1px solid var(--line);border-radius:99px;padding:4px 12px}
  .srcs .s b{color:var(--ink);font-weight:600}

  /* explorador de notícias */
  .nbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
  .nbar span{font-size:13px;color:var(--muted)}
  .news{display:flex;flex-direction:column}
  .ni{display:grid;grid-template-columns:130px 1fr 88px;gap:14px;align-items:center;
    padding:12px 4px;border-bottom:1px solid var(--line);font-size:13.5px;color:var(--ink)}
  .ni:last-child{border-bottom:none} .ni:hover{background:var(--soft)}
  .ni .f{font-size:11px;color:var(--muted);border:1px solid var(--line);border-radius:99px;
    padding:2px 9px;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .ni .t{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .ni .dt{color:var(--faint);text-align:right;font-size:12px;font-variant-numeric:tabular-nums}
  /* filtros do explorador */
  .nfilters{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}
  .nfilters select{font:inherit;font-size:13px;color:var(--ink);background:var(--bg);
    border:1px solid var(--line);border-radius:8px;padding:7px 12px;cursor:pointer}

  footer{color:var(--faint);font-size:13px;padding:56px 0 40px;text-align:center;
    border-top:1px solid var(--line);margin-top:72px;line-height:1.7}
  .tech{margin-top:8px;color:var(--muted);font-size:12.5px}

  @media(max-width:820px){.grid4{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:30px}}
</style>
<script>try{document.documentElement.setAttribute('data-theme',localStorage.getItem('tema')||'light')}catch(e){document.documentElement.setAttribute('data-theme','light')}</script>
</head>
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
  <button class="tbtn" id="theme" aria-label="Alternar tema claro/escuro" title="Alternar tema">☾</button>
</div></header>

<main class="wrap">
  <section class="hero">
    <div class="eyebrow">PoC · Indicium HealthCare</div>
    <h1>Relatórios de SRAG gerados por um agente de IA.</h1>
    <p>Um agente orquestrador consulta o Open DATASUS e notícias em tempo real, calcula as
       métricas de forma determinística e produz um relatório com narrativa fundamentada.</p>
    <div class="cta">
      <button class="btn primary" id="gerar">Gerar relatório</button>
      <a class="btn ghost" href="http://localhost:3000/d/srag-overview" target="_blank">Explorar no Grafana</a>
    </div>
    <div id="status"></div>
  </section>

  <div class="sec">Métricas dos últimos 30 dias</div>
  <div class="grid4" id="kpis"><div class="card kpi"><div class="l">carregando</div></div></div>

  <div class="sec">Como o agente trabalha</div>
  <div class="grid4">
    <div class="card step" data-no="metricas"><div class="n">1</div><h3>Métricas</h3><p>Calcula as quatro taxas no banco, em SQL determinístico.</p><div class="sms"></div></div>
    <div class="card step" data-no="graficos"><div class="n">2</div><h3>Gráficos</h3><p>Séries de casos diários e mensais.</p><div class="sms"></div></div>
    <div class="card step" data-no="noticias"><div class="n">3</div><h3>Notícias</h3><p>Busca e filtra notícias em tempo real.</p><div class="sms"></div></div>
    <div class="card step" data-no="narrativa"><div class="n">4</div><h3>Narrativa</h3><p>O LLM contextualiza apenas os números apurados.</p><div class="sms"></div></div>
  </div>

  <div class="sec">Gerar relatório do sistema</div>
  <div class="card report">
    <h3>Relatório em PDF</h3>
    <p>Executa o agente de ponta a ponta e monta o PDF com as quatro métricas, os dois gráficos, a narrativa e o rodapé de transparência.</p>
    <button class="btn primary" id="gerar2">Gerar agora</button>
  </div>

  <div class="sec">Última execução do agente</div>
  <div class="card trace">
    <div class="thead" id="thead">carregando</div>
    <div id="wf"></div>
    <div class="srcs" id="srcs"></div>
  </div>

  <div class="sec">Explorador de notícias</div>
  <div class="card panel">
    <div class="nfilters">
      <select id="fperiodo">
        <option value="30">Últimos 30 dias</option>
        <option value="90">Últimos 90 dias</option>
        <option value="180">Últimos 6 meses</option>
        <option value="365">Últimos 12 meses</option>
        <option value="">Todo o histórico</option>
      </select>
      <select id="ffonte"><option value="">Todas as fontes</option></select>
    </div>
    <div class="nbar">
      <span id="ncount">carregando</span>
      <button class="btn ghost" id="buscar" style="padding:8px 14px">Buscar mais</button>
    </div>
    <div class="news" id="news"></div>
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

// tema: claro por padrão, escuro via toggle (persistido em localStorage)
const _root = document.documentElement;
function _setTema(t){ _root.setAttribute('data-theme', t);
  try{ localStorage.setItem('tema', t); }catch(e){}
  const b=$('#theme'); if(b) b.textContent = t==='dark' ? '☀' : '☾'; }
$('#theme').onclick = () => _setTema(_root.getAttribute('data-theme')==='dark' ? 'light' : 'dark');
_setTema(_root.getAttribute('data-theme') || 'light');

async function health(){
  try{ await j('/health'); $('#dot').className='dot on'; $('#livet').textContent='no ar'; }
  catch{ $('#livet').textContent='indisponível'; }
}
async function kpis(){
  try{
    const ms = await (await j('/metricas')).json();
    $('#kpis').innerHTML = ms.map(m=>`<div class="card kpi" style="--c:${cor(m.nome)}">
      <div class="l">${m.nome}</div>
      <div class="v">${m.valor===null?'N/A':m.valor+m.unidade}</div>
      <div class="c">base de ${m.denominador.toLocaleString('pt-BR')}</div>
      <div class="obs">${m.observacao}</div></div>`).join('');
  }catch{ $('#kpis').innerHTML='<div class="card kpi"><div class="l">indisponível, rode o ETL</div></div>'; }
}
async function execucao(){
  try{
    const lst = await (await j('/auditoria/execucoes')).json();
    if(!lst.length){ $('#thead').textContent='nenhuma execução ainda'; return; }
    const e = await (await j('/auditoria/execucoes/'+lst[0].run_id)).json();
    const evs = e.eventos.map(v=>({no:v.no,tipo:v.tipo,dur:v.duracao_ms||0,end:new Date(v.ts).getTime()}));
    evs.forEach(x=>x.start=x.end-x.dur);
    const t0=Math.min(...evs.map(x=>x.start)), t1=Math.max(...evs.map(x=>x.end)), span=Math.max(1,t1-t0);
    $('#thead').innerHTML='execução <b>'+e.run_id.slice(0,12)+'</b> · '+(span/1000).toFixed(2)+' s no total';
    $('#wf').innerHTML = evs.map(x=>{
      const left=100*(x.start-t0)/span, w=Math.max(1.5,100*x.dur/span);
      return `<div class="wf"><span class="l">${x.no}</span>
        <span class="track"><i class="${x.tipo==='llm'?'llm':''}" style="left:${left}%;width:${w}%"></i></span>
        <span class="d">${x.dur} ms</span></div>`;
    }).join('');
    $('#srcs').innerHTML = e.noticias.length
      ? e.noticias.map(n=>`<span class="s"><b>${n.fonte}</b> · ${n.titulo}</span>`).join('')
      : '<span class="s">sem notícias nesta execução</span>';
  }catch{ $('#thead').textContent='trilha indisponível'; }
}
const ORDEM=['metricas','graficos','noticias','narrativa'];
function resetSteps(){ document.querySelectorAll('.step').forEach(s=>{s.classList.remove('run','done');s.querySelector('.sms').textContent='';}); }
function passoRun(no){ const s=document.querySelector('.step[data-no="'+no+'"]'); if(s) s.classList.add('run'); }
function passoDone(no,ms){ const s=document.querySelector('.step[data-no="'+no+'"]'); if(s){ s.classList.remove('run'); s.classList.add('done'); s.querySelector('.sms').textContent=ms+' ms'; } }
function abrirPdf(b64){ const bin=atob(b64); const a=new Uint8Array(bin.length); for(let i=0;i<bin.length;i++)a[i]=bin.charCodeAt(i);
  window.open(URL.createObjectURL(new Blob([a],{type:'application/pdf'})),'_blank'); }

function gerar(){
  const bs=[$('#gerar'),$('#gerar2')]; bs.forEach(b=>b.disabled=true);
  resetSteps(); passoRun('metricas');
  $('#status').textContent='Executando o agente ao vivo…';
  const es=new EventSource('/relatorio/stream');
  es.onmessage=e=>{
    const d=JSON.parse(e.data);
    if(d.tipo==='evento'){ passoDone(d.no,d.duracao_ms); const i=ORDEM.indexOf(d.no); if(i>=0&&i+1<ORDEM.length) passoRun(ORDEM[i+1]); }
    else if(d.tipo==='fim'){ abrirPdf(d.pdf_b64); $('#status').innerHTML='Relatório pronto. Execução <b>'+(d.run_id||'').slice(0,12)+'</b>'; es.close(); bs.forEach(b=>b.disabled=false); execucao(); }
    else if(d.tipo==='erro'){ $('#status').textContent='Não foi possível gerar ('+d.msg+').'; es.close(); bs.forEach(b=>b.disabled=false); }
  };
  es.onerror=()=>{ $('#status').textContent='Conexão de streaming perdida.'; es.close(); bs.forEach(b=>b.disabled=false); };
}
$('#gerar').onclick=gerar; $('#gerar2').onclick=gerar;

function qs(){ const d=$('#fperiodo').value, f=$('#ffonte').value;
  const p=new URLSearchParams(); if(d)p.set('dias',d); if(f)p.set('fonte',f); return p; }
async function fontesFiltro(){
  try{
    const fs = await (await j('/noticias/fontes')).json();
    const atual=$('#ffonte').value;
    $('#ffonte').innerHTML='<option value="">Todas as fontes</option>'+
      fs.map(f=>`<option value="${f}">${f}</option>`).join('');
    $('#ffonte').value=atual;
  }catch{}
}
async function noticias(){
  try{
    const p=qs(); p.set('limite','60');
    const ns = await (await j('/noticias?'+p)).json();
    $('#ncount').textContent = ns.length + ' notícias no período';
    $('#news').innerHTML = ns.length ? ns.map(n=>`<a class="ni" href="${n.url}" target="_blank">
      <span class="f">${n.fonte||''}</span><span class="t">${n.titulo}</span>
      <span class="dt">${n.publicado_em||''}</span></a>`).join('')
      : '<div style="color:var(--faint);padding:8px 4px">nada neste período. amplie o filtro ou clique em Buscar mais.</div>';
  }catch{ $('#ncount').textContent='indisponível'; }
}
async function explorador(){ await noticias(); }
$('#fperiodo').onchange=noticias; $('#ffonte').onchange=noticias;
$('#buscar').onclick=async e=>{
  const b=e.target; b.disabled=true; b.textContent='buscando…';
  try{ const r=await (await j('/noticias/buscar',{method:'POST'})).json(); b.textContent=(r.novas||0)+' novas';
    await fontesFiltro(); await explorador(); }
  catch{ b.textContent='falhou'; }
  finally{ setTimeout(()=>{b.disabled=false; b.textContent='Buscar mais';}, 1800); }
};

health(); kpis(); execucao(); fontesFiltro(); explorador();
</script>
</body></html>"""


GRAFO = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Grafo do agente · SRAG</title>
<style>
  :root{--bg:#fbfbfd;--panel:#fff;--soft:#f4f4f7;--ink:#0b0d12;--muted:#5f6673;--faint:#9aa3af;
    --line:#ebebef;--accent:#4f46e5;--accent2:#7c3aed;--accent-weak:#eef0ff;--radius:16px;
    --shadow:0 1px 2px rgba(16,18,27,.05),0 14px 30px -16px rgba(16,18,27,.16);--mono:ui-monospace,Menlo,monospace}
  :root[data-theme="dark"]{--bg:#0a0b0f;--panel:#14161f;--soft:#1b1e2a;--ink:#f1f3f8;
    --muted:#9aa2b1;--faint:#6a7285;--line:#242838;--accent:#8b93f8;--accent2:#a78bfa;--accent-weak:#1d2133;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 14px 32px -16px rgba(0,0,0,.6)}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,"Segoe UI",Roboto,Inter,system-ui,sans-serif;letter-spacing:-.005em}
  .wrap{max-width:940px;margin:0 auto;padding:0 24px}
  a{color:inherit;text-decoration:none}
  header{border-bottom:1px solid var(--line)}
  .bar{display:flex;align-items:center;height:64px;gap:14px}
  .brand{display:flex;align-items:center;gap:10px;font-weight:650;font-size:15px}
  .mark{width:28px;height:28px;border-radius:8px;
    background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;
    display:grid;place-items:center;font-size:13px;font-weight:800}
  .sp{flex:1}
  .back{color:var(--muted);font-size:14px}.back:hover{color:var(--ink)}
  .tbtn{width:34px;height:34px;border-radius:9px;border:1px solid var(--line);background:var(--panel);
    color:var(--muted);cursor:pointer;font-size:15px;line-height:1;display:grid;place-items:center}
  .tbtn:hover{color:var(--ink)}
  .hero{text-align:center;padding:64px 0 8px}
  .eyebrow{font-size:13px;font-weight:600;color:var(--accent)}
  h1{font-size:34px;line-height:1.1;letter-spacing:-.03em;margin:12px 0 10px;font-weight:700}
  .hero p{color:var(--muted);font-size:16px;max-width:58ch;margin:0 auto}

  .graph{position:relative;margin:40px 0 6px;border:1px solid var(--line);border-radius:var(--radius);
    background:radial-gradient(120% 100% at 50% 0%,var(--accent-weak),var(--panel) 60%);
    box-shadow:var(--shadow);overflow:hidden;height:520px}
  .graph svg{width:100%;height:100%;display:block;cursor:grab;touch-action:none}
  .link{stroke:var(--line);stroke-width:1.6px;transition:stroke .2s,opacity .2s,stroke-width .2s}
  .link.hot{stroke:var(--accent);stroke-width:2.6px}
  .link.dim{opacity:.12}
  .gnode{cursor:pointer;transition:opacity .2s}
  .gnode.dim{opacity:.18}
  .gnode circle{stroke:var(--panel);stroke-width:3px}
  .gnode .lbl{fill:var(--ink);font-size:12.5px;font-weight:650;pointer-events:none;
    paint-order:stroke;stroke:var(--panel);stroke-width:3.5px;stroke-linejoin:round}
  .gnode .sub{fill:var(--muted);font-size:10px;font-weight:500;pointer-events:none;
    paint-order:stroke;stroke:var(--panel);stroke-width:3px;stroke-linejoin:round}
  .c-core{fill:var(--accent)} .c-tool{fill:#4f46e5} .c-llm{fill:#7c3aed}
  .c-out{fill:#16a34a} .c-data{fill:#c98a2b} .c-aux{fill:#8a909c}
  .legend{display:flex;flex-wrap:wrap;gap:16px;justify-content:center;margin:16px 0 0}
  .legend span{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;color:var(--muted)}
  .legend i{width:10px;height:10px;border-radius:50%;display:inline-block}
  .hint{text-align:center;font-size:12px;color:var(--faint);margin:8px 0 0}

  .note{color:var(--muted);font-size:13.5px;margin:16px auto 0;line-height:1.6;max-width:70ch;text-align:center}
  .src{margin-top:26px;font-size:12.5px;text-align:center}.src a{color:var(--accent)}
  footer{color:var(--faint);font-size:13px;padding:44px 0;text-align:center;border-top:1px solid var(--line);margin-top:56px}
</style>
<script>try{document.documentElement.setAttribute('data-theme',localStorage.getItem('tema')||'light')}catch(e){document.documentElement.setAttribute('data-theme','light')}</script>
</head>
<body>
<header><div class="wrap bar">
  <span class="brand"><span class="mark">S</span> SRAG Relatórios</span>
  <span class="sp"></span>
  <a class="back" href="/">voltar ao hub</a>
  <button class="tbtn" id="theme" aria-label="Alternar tema claro/escuro" title="Alternar tema" style="margin-left:16px">☾</button>
</div></header>

<main class="wrap">
  <section class="hero">
    <div class="eyebrow">Orquestração</div>
    <h1>Fluxo do agente</h1>
    <p>Orquestração em LangGraph. Cada nó é um passo determinístico e auditável, em que as três
       tools alimentam o estado e o nó de narrativa contextualiza os números com o LLM.</p>
  </section>

  <div class="graph"><svg id="g" viewBox="0 0 820 520" preserveAspectRatio="xMidYMid meet"></svg></div>
  <div class="legend">
    <span><i style="background:var(--accent)"></i> Orquestrador</span>
    <span><i style="background:#4f46e5"></i> Tools</span>
    <span><i style="background:#7c3aed"></i> LLM</span>
    <span><i style="background:#c98a2b"></i> Fontes de dados</span>
    <span><i style="background:#16a34a"></i> Saída</span>
    <span><i style="background:#8a909c"></i> Auditoria</span>
  </div>
  <p class="hint">Passe o mouse para destacar as conexões · arraste os nós para reorganizar</p>

  <p class="note">Este é o fluxo que o agente percorre para produzir o relatório de SRAG. As tools
     apuram as métricas e as séries no banco e coletam as notícias, e o nó de narrativa usa o LLM
     apenas para contextualizar os números já calculados. A execução é fail-fast e não gera
     relatório degradado; se qualquer etapa falhar, ela é interrompida com erro e cada passo fica
     registrado na trilha de auditoria com sua duração e resultado.</p>
  <p class="src">Fonte em Mermaid disponível em <a href="/agente/grafo?format=mermaid">/agente/grafo?format=mermaid</a></p>
</main>
<footer>SRAG Relatórios · agente orquestrador em LangGraph</footer>
<script>
  const _r=document.documentElement;
  function _st(t){ _r.setAttribute('data-theme',t); try{localStorage.setItem('tema',t)}catch(e){}
    const b=document.getElementById('theme'); if(b) b.textContent=t==='dark'?'☀':'☾'; }
  document.getElementById('theme').onclick=()=>_st(_r.getAttribute('data-theme')==='dark'?'light':'dark');
  _st(_r.getAttribute('data-theme')||'light');

  // ── grafo force-directed (estilo Obsidian), sem libs externas ──
  (function(){
    const svg=document.getElementById('g'); if(!svg) return;
    const NS='http://www.w3.org/2000/svg', W=820, H=520;
    const N=[
      {id:'gold',t:'gold',s:'Postgres',c:'data'},
      {id:'news',t:'NewsAPI',s:'tempo real',c:'data'},
      {id:'llm',t:'Claude',s:'OpenRouter',c:'data'},
      {id:'ag',t:'Orquestrador',s:'LangGraph',c:'core'},
      {id:'met',t:'calcular_metricas',s:'tool',c:'tool'},
      {id:'gra',t:'dados_grafico',s:'tool',c:'tool'},
      {id:'not',t:'buscar_noticias',s:'tool',c:'tool'},
      {id:'nar',t:'narrativa',s:'LLM · grounded',c:'llm'},
      {id:'rel',t:'Relatório PDF',s:'saída',c:'out'},
      {id:'aud',t:'Auditoria',s:'trilha · run_id',c:'aux'}
    ];
    const E=[['ag','met'],['ag','gra'],['ag','not'],['ag','nar'],['ag','rel'],['ag','aud'],
      ['gold','met'],['gold','gra'],['news','not'],['llm','nar'],
      ['met','nar'],['gra','nar'],['not','nar'],['nar','rel']];
    const by={};
    N.forEach(function(n,i){ by[n.id]=n; var a=i/N.length*Math.PI*2;
      n.x=W/2+Math.cos(a)*165; n.y=H/2+Math.sin(a)*120; n.vx=0; n.vy=0; n.r=(n.c==='core'?26:18); });
    by.ag.x=W/2; by.ag.y=H/2;
    const links=E.map(function(e){ return {s:by[e[0]], t:by[e[1]]}; });
    let alpha=1, drag=null;

    const linkEls=links.map(function(){ var e=document.createElementNS(NS,'line'); e.setAttribute('class','link'); svg.appendChild(e); return e; });
    N.forEach(function(n){
      var g=document.createElementNS(NS,'g'); g.setAttribute('class','gnode');
      var c=document.createElementNS(NS,'circle'); c.setAttribute('class','c-'+n.c); c.setAttribute('r',n.r);
      var t1=document.createElementNS(NS,'text'); t1.setAttribute('class','lbl'); t1.setAttribute('text-anchor','middle'); t1.textContent=n.t;
      var t2=document.createElementNS(NS,'text'); t2.setAttribute('class','sub'); t2.setAttribute('text-anchor','middle'); t2.textContent=n.s;
      g.appendChild(c); g.appendChild(t1); g.appendChild(t2); svg.appendChild(g);
      n.g=g; n.c1=c; n.l1=t1; n.l2=t2;
      g.addEventListener('pointerenter',function(){ hi(n); });
      g.addEventListener('pointerleave',function(){ hi(null); });
      g.addEventListener('pointerdown',function(ev){ startDrag(n,ev); });
    });

    function render(){
      links.forEach(function(l,i){ var e=linkEls[i]; e.setAttribute('x1',l.s.x); e.setAttribute('y1',l.s.y); e.setAttribute('x2',l.t.x); e.setAttribute('y2',l.t.y); });
      N.forEach(function(n){ n.c1.setAttribute('cx',n.x); n.c1.setAttribute('cy',n.y);
        n.l1.setAttribute('x',n.x); n.l1.setAttribute('y',n.y+n.r+15);
        n.l2.setAttribute('x',n.x); n.l2.setAttribute('y',n.y+n.r+28); });
    }
    function physics(){
      for(var i=0;i<N.length;i++)for(var k=i+1;k<N.length;k++){
        var a=N[i],b=N[k],dx=a.x-b.x,dy=a.y-b.y,d2=dx*dx+dy*dy||0.01,d=Math.sqrt(d2);
        var f=9500/d2*alpha, fx=dx/d*f, fy=dy/d*f; a.vx+=fx; a.vy+=fy; b.vx-=fx; b.vy-=fy;
      }
      links.forEach(function(l){ var dx=l.t.x-l.s.x,dy=l.t.y-l.s.y,d=Math.sqrt(dx*dx+dy*dy)||0.01,
        f=(d-155)*0.05*alpha, fx=dx/d*f, fy=dy/d*f; l.s.vx+=fx; l.s.vy+=fy; l.t.vx-=fx; l.t.vy-=fy; });
      N.forEach(function(n){ if(n===drag) return;
        n.vx+=(W/2-n.x)*0.004*alpha; n.vy+=(H/2-n.y)*0.004*alpha;
        n.vx*=0.84; n.vy*=0.84; n.x+=n.vx; n.y+=n.vy; });
      // colisão: impede sobreposição de nós e rótulos, mesmo com a física fria
      for(var p=0;p<N.length;p++)for(var q=p+1;q<N.length;q++){
        var a2=N[p],b2=N[q],ex=a2.x-b2.x,ey=a2.y-b2.y,ed=Math.sqrt(ex*ex+ey*ey)||0.01,mn=a2.r+b2.r+74;
        if(ed<mn){ var pu=(mn-ed)/2,ux=ex/ed,uy=ey/ed;
          if(a2!==drag){a2.x+=ux*pu; a2.y+=uy*pu;} if(b2!==drag){b2.x-=ux*pu; b2.y-=uy*pu;} }
      }
      N.forEach(function(n){ n.x=Math.max(56,Math.min(W-56,n.x)); n.y=Math.max(46,Math.min(H-50,n.y)); });
      alpha=Math.max(alpha*0.99,0.045);
    }
    function tick(){ physics(); render(); requestAnimationFrame(tick); }
    function hi(n){
      var nb={}; if(n){ nb[n.id]=1; links.forEach(function(l){ if(l.s===n)nb[l.t.id]=1; if(l.t===n)nb[l.s.id]=1; }); }
      N.forEach(function(m){ m.g.classList.toggle('dim', !!n && !nb[m.id]); });
      links.forEach(function(l,i){ var on=n&&(l.s===n||l.t===n); linkEls[i].classList.toggle('hot',!!on); linkEls[i].classList.toggle('dim', !!n && !on); });
    }
    function pt(e){ var r=svg.getBoundingClientRect(); return {x:(e.clientX-r.left)/r.width*W, y:(e.clientY-r.top)/r.height*H}; }
    function startDrag(n,ev){ ev.preventDefault(); drag=n; alpha=Math.max(alpha,0.4);
      function mv(e){ var p=pt(e); n.x=p.x; n.y=p.y; n.vx=0; n.vy=0; }
      function up(){ drag=null; window.removeEventListener('pointermove',mv); window.removeEventListener('pointerup',up); }
      window.addEventListener('pointermove',mv); window.addEventListener('pointerup',up);
    }
    for(var w=0; w<520; w++) physics();  // warm-up: já abre espalhado
    alpha=0.12; render(); tick();
  })();
</script>
</body></html>"""
