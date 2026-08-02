// Robust CDP reproduction of the FinWise login flow.
// Fetches CDP endpoints over HTTP (avoids hardcoded WS URLs), drives a real Chrome tab.
import { execSync } from 'node:child_process';

function httpGet(url) {
  return execSync(`curl -s -m 5 "${url}"`, { encoding: 'utf8' });
}
function wsUrlFromJson(path) {
  const raw = httpGet('http://127.0.0.1:9222' + path);
  const j = JSON.parse(raw);
  return j.webSocketDebuggerUrl;
}

function wsConnect(url) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(url);
    ws.onopen = () => resolve(ws);
    ws.onerror = (e) => reject(e);
  });
}
function send(ws, method, params = {}) {
  return new Promise((resolve) => {
    const id = Math.floor(Math.random() * 1e6);
    const handler = (ev) => {
      const d = JSON.parse(ev.data);
      if (d.id === id) { ws.removeEventListener('message', handler); resolve(d); }
    };
    ws.addEventListener('message', handler);
    ws.send(JSON.stringify({ id, method, params }));
  });
}

(async () => {
  const browserWs = wsUrlFromJson('/json/version');
  const b = await wsConnect(browserWs);

  const target = await send(b, 'Target.createTarget', { url: 'http://127.0.0.1:8000/login' });
  const targetId = target.result.targetId;
  const info = await send(b, 'Target.getTargetInfo', { targetId });
  const t = await wsConnect(info.result.webSocketDebuggerUrl);

  const consoleMsgs = [];
  const apiCalls = [];
  t.addEventListener('message', (ev) => {
    const m = JSON.parse(ev.data);
    if (m.method === 'Runtime.consoleAPICalled') {
      consoleMsgs.push(m.params.args.map(a => a.value ?? a.description ?? '').join(' '));
    } else if (m.method === 'Runtime.exceptionThrown') {
      const d = m.params.exceptionDetails;
      consoleMsgs.push('EXCEPTION: ' + (d.exception?.description ?? d.text));
    } else if (m.method === 'Network.requestWillBeSent') {
      const u = m.params.request.url;
      if (u.includes('/api') || u.includes('/health')) apiCalls.push({ url: u, phase: 'sent' });
    } else if (m.method === 'Network.loadingFailed') {
      apiCalls.push({ reqId: m.params.requestId, failed: m.params.errorText });
    } else if (m.method === 'Network.responseReceived') {
      const u = m.params.response.url;
      if (u.includes('/api') || u.includes('/health')) apiCalls.push({ url: u, status: m.params.response.status });
    }
  });

  await send(t, 'Runtime.enable');
  await send(t, 'Network.enable');
  await new Promise(r => setTimeout(r, 4000));

  const probe = await send(t, 'Runtime.evaluate', {
    expression: `(function(){const r=document.getElementById('root');return{rootChildren:r?r.children.length:-1,snip:r?r.innerHTML.slice(0,200):'NOROOT',token:!!localStorage.getItem('finwise_token'),user:!!localStorage.getItem('finwise_user'),url:location.href};})()`,
    returnByValue: true,
  });
  console.log('=== PAGE PROBE ===');
  console.log(JSON.stringify(probe.result.result, null, 2));

  const login = await send(t, 'Runtime.evaluate', {
    expression: `(async function(){try{const res=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:'admin@finwise.app',password:'Admin@123456'})});const d=await res.json().catch(()=>({}));return{status:res.status,ok:res.ok,data:d};}catch(e){return{fetchError:String(e)};}})()`,
    returnByValue: true, awaitPromise: true,
  });
  console.log('=== IN-PAGE FETCH /api/auth/login ===');
  console.log(JSON.stringify(login.result.result, null, 2));

  console.log('=== CONSOLE (' + consoleMsgs.length + ') ===');
  consoleMsgs.forEach(m => console.log('  ' + m));
  console.log('=== API/NETWORK (' + apiCalls.length + ') ===');
  apiCalls.forEach(c => console.log('  ' + JSON.stringify(c)));

  await send(b, 'Target.closeTarget', { targetId });
  process.exit(0);
})().catch(e => { console.error('SCRIPT ERROR', e); process.exit(1); });
