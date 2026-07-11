(function(){const s=document.createElement("link").relList;if(s&&s.supports&&s.supports("modulepreload"))return;for(const n of document.querySelectorAll('link[rel="modulepreload"]'))o(n);new MutationObserver(n=>{for(const r of n)if(r.type==="childList")for(const v of r.addedNodes)v.tagName==="LINK"&&v.rel==="modulepreload"&&o(v)}).observe(document,{childList:!0,subtree:!0});function t(n){const r={};return n.integrity&&(r.integrity=n.integrity),n.referrerPolicy&&(r.referrerPolicy=n.referrerPolicy),n.crossOrigin==="use-credentials"?r.credentials="include":n.crossOrigin==="anonymous"?r.credentials="omit":r.credentials="same-origin",r}function o(n){if(n.ep)return;n.ep=!0;const r=t(n);fetch(n.href,r)}})();async function _(){return(await fetch("/api/v1/navigation")).json()}async function M(e,s,t){return(await fetch("/api/v1/query",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e,mode:s,session:t||null,limit:5,max_chars:4e3})})).json()}async function I(e){const s=await fetch(`/api/v1/sessions/${encodeURIComponent(e)}`);if(!s.ok)throw new Error(`session request failed: ${s.status}`);return s.json()}function w(e){return e.length===0?"":`
    <section class="chat">
      ${e.map(s=>j(s)).join("")}
    </section>
  `}function j(e){var o;const s=((o=e.response.evidence)==null?void 0:o.results)??[],t=e.response.accounting;return`
    <section class="chat-turn">
      <article class="message user-message">
        <div class="avatar">●</div>
        <div>
          <div class="message-label">You</div>
          <p>${a(e.query)}</p>
        </div>
      </article>

      <article class="message assistant-message">
        <div class="avatar bot">◎</div>
        <div class="message-body">
          <div class="message-label assistant-label">Local AI Search</div>
          <div class="answer">${U(e.response.answer||"No answer returned.")}</div>
          ${s.length>0?`
                <details class="sources" open>
                  <summary>Evidence</summary>
                  <ol>
                    ${s.map(n=>`
                          <li>
                            ${O(n)}
                            ${n.url?`<div class="result-url">${a(n.url)}</div>`:""}
                            ${n.snippet?`<p>${a(n.snippet)}</p>`:""}
                          </li>
                        `).join("")}
                  </ol>
                </details>
              `:""}
          ${t?`
                <details class="sources evidence-details" open>
                  <summary>Evidence</summary>
                  <section class="evidence-summary">
                    <strong>Evidence summary</strong>
                    <p>
                      Found: ${t.available_count}
                      &nbsp; Used: ${t.evidence_count}
                      &nbsp; Shown: ${t.displayed_count}
                    </p>
                  </section>
                </details>
              `:""}
          <details class="debug">
            <summary>Raw response</summary>
            <pre>${a(JSON.stringify(e.response,null,2))}</pre>
          </details>
        </div>
      </article>
    </section>
  `}function O(e){const s=e.source_type?`<span class="source-type">${a(e.source_type)}</span> `:"",t=a(e.title||"Untitled");return e.url?`
      ${s}<a class="result-title" href="${P(e.url)}" target="_blank" rel="noopener noreferrer">
        ${t}
      </a>
    `:`${s}<strong class="result-title">${t}</strong>`}function U(e){return a(e).split(`

`).map(s=>`<p>${s.replaceAll(`
`,"<br>")}</p>`).join("")}function a(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function P(e){return a(e)}function k(e){var o;const s=((o=e.evidence)==null?void 0:o.results)??[],t=e.accounting;return s.length===0?`
      <section class="empty-state">
        <h2>No results</h2>
        <p>No search evidence was returned for this query.</p>
        ${S(e)}
      </section>
    `:`
    <section class="search-results">
      <p class="result-count">
        ${t?`Found: ${t.available_count} · Used: ${t.evidence_count} · Shown: ${t.displayed_count}`:`${s.length} results`}
        · ${e.elapsed_ms} ms
      </p>
      ${s.map(n=>`
            <article class="search-result">
              ${renderEvidenceTitle(n)}
              ${n.url?`<div class="result-url">${h(n.url)}</div>`:""}
              <p>${h(n.snippet||"")}</p>
            </article>
          `).join("")}
      ${S(e)}
    </section>
  `}function S(e){return`
    <details class="debug">
      <summary>Raw response</summary>
      <pre>${h(JSON.stringify(e,null,2))}</pre>
    </details>
  `}function h(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}const L=document.querySelector("#app");if(!L)throw new Error("missing #app");L.innerHTML=`
  <section class="app-shell">
      <aside id="navigation" class="navigation-panel">
        <section class="navigation-heading">
          <h2>Sessions</h2>
          <button id="new-session" type="button" class="new-session-button">+</button>
        </section>
        <p id="selected-session" class="selected-session">No session selected</p>
        <div id="session-list" class="session-list"></div>
      </aside>

      <main id="conversation" class="conversation">
      <section id="empty-state" class="empty-state">
        <p class="eyebrow">local first · LAN friendly · API backed</p>
        <h1>Local AI Search</h1>
        <p>Search the web/local evidence or ask your local AI with sources.</p>
      </section>

      <section id="output" class="output"></section>
    </main>

    <footer class="composer-shell">
      <section class="brand">
        <h2>Local AI Search</h2>
        <p>local first · LAN friendly · API backed</p>
      </section>

<form id="query-form" class="query-form">
        <input id="query" class="query-input" name="query" placeholder="Search or ask..." required />
        <input id="session" name="session" type="hidden" />
        <select id="mode" name="mode">
          <option value="integrated">integrated</option>
          <option value="ai_only">ai only</option>
          <option value="web_only">web only</option>
        </select>
        <button type="submit">Run</button>
      </form>

      <p class="privacy-note">Your data stays on your machine.</p>
    </footer>
  </section>
`;const T=document.querySelector("#query-form"),m=document.querySelector("#session-list"),$=document.querySelector("#selected-session"),H=document.querySelector("#new-session"),y=document.querySelector("#session"),c=document.querySelector("#query"),b=document.querySelector("#mode"),i=document.querySelector("#output"),f=document.querySelector("#empty-state");if(!T||!m||!$||!H||!y||!c||!b||!i||!f)throw new Error("missing UI elements");const l=[];let u="";const E=new URLSearchParams(window.location.search),q=E.get("query"),p=E.get("mode");async function N(){try{const e=await _();m.innerHTML=e.sessions.map(s=>`
          <button type="button" class="session-button" data-session="${x(s.name)}">
            ${d(s.name)}
          </button>
        `).join(""),m.querySelectorAll(".session-button").forEach(s=>{s.addEventListener("click",async()=>{const t=s.dataset.session||"";if(t){y.value=t,$.textContent=`Selected: ${t}`;try{const o=await I(t);l.length=0,u=C(o.messages),i.innerHTML=u,f.hidden=!0}catch(o){i.innerHTML=g(o instanceof Error?o.message:"Unable to load session")}}})})}catch(e){m.innerHTML=`
      <p class="navigation-empty">
        Unable to load sessions: ${d(String(e))}
      </p>
    `}}N();H.addEventListener("click",()=>{const e=window.prompt("New session name:");e!=null&&e.trim()&&(y.value=e.trim(),$.textContent=`New session: ${e.trim()}`,l.length=0,u="",i.innerHTML="",f.hidden=!1,c.value="",c.focus())});q&&(c.value=q);(p==="integrated"||p==="ai_only"||p==="web_only")&&(b.value=p);T.addEventListener("submit",async e=>{var n;e.preventDefault();const s=y.value.trim(),t=c.value.trim(),o=b.value;if(t){f.hidden=!0,o==="web_only"?i.innerHTML=A():i.innerHTML=`
      ${u}
      ${w(l)}
      ${A()}
    `;try{const r=await M(t,o,s);if(!r.ok){i.innerHTML=g(((n=r.error)==null?void 0:n.message)??"Unknown error");return}if(r.mode==="web_only"){i.innerHTML=k(r);return}l.push({query:t,response:r}),i.innerHTML=`
      ${u}
      ${w(l)}
    `,await N(),c.value="",window.scrollTo({top:document.body.scrollHeight,behavior:"smooth"})}catch(r){i.innerHTML=g(r instanceof Error?r.message:"Unknown error")}}});function C(e){return e.length===0?`
      <section class="empty-state">
        <h2>Empty session</h2>
        <p>This session does not contain any messages yet.</p>
      </section>
    `:`
    <section class="chat">
      ${e.map(s=>`
            <article class="message ${s.role==="user"?"user-message":"assistant-message"}">
              <div class="avatar">${s.role==="user"?"●":"◎"}</div>
              <div class="message-body">
                <div class="message-label">
                  ${s.role==="user"?"You":"Local AI Search"}
                </div>
                <div class="answer">${R(s.content)}</div>
              </div>
            </article>
          `).join("")}
    </section>
  `}function R(e){return d(e).split(`

`).map(s=>`<p>${s.replaceAll(`
`,"<br>")}</p>`).join("")}function A(){return`
    <section class="loading">
      <div class="spinner"></div>
      <p>Working...</p>
    </section>
  `}function g(e){return`
    <section class="error-card">
      <h2>Request failed</h2>
      <p>${d(e)}</p>
    </section>
  `}function d(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function x(e){return d(e)}
