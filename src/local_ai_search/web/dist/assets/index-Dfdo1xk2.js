(function(){const s=document.createElement("link").relList;if(s&&s.supports&&s.supports("modulepreload"))return;for(const n of document.querySelectorAll('link[rel="modulepreload"]'))o(n);new MutationObserver(n=>{for(const r of n)if(r.type==="childList")for(const h of r.addedNodes)h.tagName==="LINK"&&h.rel==="modulepreload"&&o(h)}).observe(document,{childList:!0,subtree:!0});function t(n){const r={};return n.integrity&&(r.integrity=n.integrity),n.referrerPolicy&&(r.referrerPolicy=n.referrerPolicy),n.crossOrigin==="use-credentials"?r.credentials="include":n.crossOrigin==="anonymous"?r.credentials="omit":r.credentials="same-origin",r}function o(n){if(n.ep)return;n.ep=!0;const r=t(n);fetch(n.href,r)}})();async function M(){return(await fetch("/api/v1/navigation")).json()}async function I(e,s,t){return(await fetch("/api/v1/query",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e,mode:s,session:t||null,limit:5,max_chars:4e3})})).json()}async function O(e){const s=await fetch(`/api/v1/sessions/${encodeURIComponent(e)}`);if(!s.ok)throw new Error(`session request failed: ${s.status}`);return s.json()}function S(e){return e.length===0?"":`
    <section class="chat">
      ${e.map(s=>U(s)).join("")}
    </section>
  `}function U(e){var o;const s=((o=e.response.evidence)==null?void 0:o.results)??[],t=e.response.accounting;return`
    <section class="chat-turn">
      <article class="message user-message">
        <div class="avatar">●</div>
        <div>
          <div class="message-label">You</div>
          <p>${i(e.query)}</p>
        </div>
      </article>

      <article class="message assistant-message">
        <div class="avatar bot">◎</div>
        <div class="message-body">
          <div class="message-label assistant-label">Local AI Search</div>
          <div class="answer">${C(e.response.answer||"No answer returned.")}</div>
          ${s.length>0?`
                <details class="sources" open>
                  <summary>Evidence</summary>
                  <ol>
                    ${s.map(n=>`
                          <li>
                            ${P(n)}
                            ${n.url?`<div class="result-url">${i(n.url)}</div>`:""}
                            ${n.snippet?`<p>${i(n.snippet)}</p>`:""}
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
            <pre>${i(JSON.stringify(e.response,null,2))}</pre>
          </details>
        </div>
      </article>
    </section>
  `}function P(e){const s=e.source_type?`<span class="source-type">${i(e.source_type)}</span> `:"",t=i(e.title||"Untitled");return e.url?`
      ${s}<a class="result-title" href="${R(e.url)}" target="_blank" rel="noopener noreferrer">
        ${t}
      </a>
    `:`${s}<strong class="result-title">${t}</strong>`}function C(e){return i(e).split(`

`).map(s=>`<p>${s.replaceAll(`
`,"<br>")}</p>`).join("")}function i(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function R(e){return i(e)}function x(e){var o;const s=((o=e.evidence)==null?void 0:o.results)??[],t=e.accounting;return s.length===0?`
      <section class="empty-state">
        <h2>No results</h2>
        <p>No search evidence was returned for this query.</p>
        ${q(e)}
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
              ${n.url?`<div class="result-url">${g(n.url)}</div>`:""}
              <p>${g(n.snippet||"")}</p>
            </article>
          `).join("")}
      ${q(e)}
    </section>
  `}function q(e){return`
    <details class="debug">
      <summary>Raw response</summary>
      <pre>${g(JSON.stringify(e,null,2))}</pre>
    </details>
  `}function g(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}const L=document.querySelector("#app");if(!L)throw new Error("missing #app");L.innerHTML=`
  <section class="app-shell">
      <aside id="navigation" class="navigation-panel">
        <section class="navigation-heading">
          <h2>Sessions</h2>
          <button id="new-session" type="button" class="new-session-button">+</button>
        </section>
        <p id="selected-session" class="selected-session">No session selected</p>
        <p id="selected-workspace" class="selected-workspace">No workspace selected</p>
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
        <input id="workspace" name="workspace" type="hidden" />
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
`;const N=document.querySelector("#query-form"),l=document.querySelector("#session-list"),$=document.querySelector("#selected-session"),E=document.querySelector("#selected-workspace"),T=document.querySelector("#new-session"),f=document.querySelector("#session"),d=document.querySelector("#workspace"),u=document.querySelector("#query"),b=document.querySelector("#mode"),a=document.querySelector("#output"),v=document.querySelector("#empty-state");if(!N||!l||!$||!d||!T||!f||!u||!b||!a||!v)throw new Error("missing UI elements");const p=[];let m="";const H=new URLSearchParams(window.location.search),A=H.get("query"),y=H.get("mode");async function _(){try{const e=await M();l.innerHTML=W(e),l.querySelectorAll(".session-button").forEach(s=>{s.addEventListener("click",async()=>{const t=s.dataset.session||"";if(t){f.value=t,$.textContent=`Selected: ${t}`;try{const o=await O(t);p.length=0,m=Y(o.messages),a.innerHTML=m,v.hidden=!0}catch(o){a.innerHTML=w(o instanceof Error?o.message:"Unable to load session")}}})}),l.querySelectorAll(".workspace-button").forEach(s=>{s.addEventListener("click",()=>{const t=s.dataset.workspace||"";t&&(d.value=t,E.textContent=`Selected: ${t}`,l.querySelectorAll(".workspace-button").forEach(o=>{o.classList.toggle("selected",o.dataset.workspace===t)}))})}),d.value&&l.querySelectorAll(".workspace-button").forEach(s=>{s.classList.toggle("selected",s.dataset.workspace===d.value)})}catch(e){l.innerHTML=`
      <p class="navigation-empty">
        Unable to load sessions: ${c(String(e))}
      </p>
    `}}_();T.addEventListener("click",()=>{const e=window.prompt("New session name:");e!=null&&e.trim()&&(f.value=e.trim(),d.value="",E.textContent="No workspace selected",$.textContent=`New session: ${e.trim()}`,p.length=0,m="",a.innerHTML="",v.hidden=!1,u.value="",u.focus())});A&&(u.value=A);(y==="integrated"||y==="ai_only"||y==="web_only")&&(b.value=y);N.addEventListener("submit",async e=>{var n;e.preventDefault();const s=f.value.trim(),t=u.value.trim(),o=b.value;if(t){v.hidden=!0,o==="web_only"?a.innerHTML=k():a.innerHTML=`
      ${m}
      ${S(p)}
      ${k()}
    `;try{const r=await I(t,o,s);if(!r.ok){a.innerHTML=w(((n=r.error)==null?void 0:n.message)??"Unknown error");return}if(r.mode==="web_only"){a.innerHTML=x(r);return}p.push({query:t,response:r}),a.innerHTML=`
      ${m}
      ${S(p)}
    `,await _(),u.value="",window.scrollTo({top:document.body.scrollHeight,behavior:"smooth"})}catch(r){a.innerHTML=w(r instanceof Error?r.message:"Unknown error")}}});function W(e){return`
    <section class="navigation-group">
      ${F(e.sessions)}
    </section>

    <section class="navigation-group workspace-navigation">
      <h2>Workspaces</h2>
      ${J(e.workspaces)}
    </section>
  `}function F(e){return e.length===0?`
      <p class="navigation-empty">No sessions</p>
    `:e.map(s=>`
        <button
          type="button"
          class="session-button"
          data-session="${j(s.name)}"
        >
          ${c(s.name)}
        </button>
      `).join("")}function J(e){return e.length===0?`
      <p class="navigation-empty">No workspaces</p>
    `:e.map(s=>`
        <section class="workspace-node">
        <button
          type="button"
          class="workspace-button"
          data-workspace="${j(s.name)}"
        >
          ${c(s.name)}
        </button>

          <div class="workspace-children">
            ${s.sessions.map(t=>`
                  <div class="workspace-session">
                    ${c(t.name)}
                  </div>
                `).join("")}

            ${s.files.map(t=>`
                  <div class="workspace-file">
                    ${c(t.path)}
                  </div>
                `).join("")}
          </div>
        </section>
      `).join("")}function Y(e){return e.length===0?`
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
                <div class="answer">${D(s.content)}</div>
              </div>
            </article>
          `).join("")}
    </section>
  `}function D(e){return c(e).split(`

`).map(s=>`<p>${s.replaceAll(`
`,"<br>")}</p>`).join("")}function k(){return`
    <section class="loading">
      <div class="spinner"></div>
      <p>Working...</p>
    </section>
  `}function w(e){return`
    <section class="error-card">
      <h2>Request failed</h2>
      <p>${c(e)}</p>
    </section>
  `}function c(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function j(e){return c(e)}
