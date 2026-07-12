(function(){const s=document.createElement("link").relList;if(s&&s.supports&&s.supports("modulepreload"))return;for(const t of document.querySelectorAll('link[rel="modulepreload"]'))r(t);new MutationObserver(t=>{for(const o of t)if(o.type==="childList")for(const v of o.addedNodes)v.tagName==="LINK"&&v.rel==="modulepreload"&&r(v)}).observe(document,{childList:!0,subtree:!0});function n(t){const o={};return t.integrity&&(o.integrity=t.integrity),t.referrerPolicy&&(o.referrerPolicy=t.referrerPolicy),t.crossOrigin==="use-credentials"?o.credentials="include":t.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function r(t){if(t.ep)return;t.ep=!0;const o=n(t);fetch(t.href,o)}})();async function _(){return(await fetch("/api/v1/navigation")).json()}async function j(e,s,n){return(await fetch("/api/v1/query",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e,mode:s,session:n||null,limit:5,max_chars:4e3})})).json()}async function k(e){const s=await fetch(`/api/v1/sessions/${encodeURIComponent(e)}`);if(!s.ok)throw new Error(`session request failed: ${s.status}`);return s.json()}function b(e){return e.length===0?"":`
    <section class="chat">
      ${e.map(s=>M(s)).join("")}
    </section>
  `}function M(e){var r;const s=((r=e.response.evidence)==null?void 0:r.results)??[],n=e.response.accounting;return`
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
          <div class="answer">${O(e.response.answer||"No answer returned.")}</div>
          ${s.length>0?`
                <details class="sources" open>
                  <summary>Evidence</summary>
                  <ol>
                    ${s.map(t=>`
                          <li>
                            ${I(t)}
                            ${t.url?`<div class="result-url">${a(t.url)}</div>`:""}
                            ${t.snippet?`<p>${a(t.snippet)}</p>`:""}
                          </li>
                        `).join("")}
                  </ol>
                </details>
              `:""}
          ${n?`
                <details class="sources evidence-details" open>
                  <summary>Evidence</summary>
                  <section class="evidence-summary">
                    <strong>Evidence summary</strong>
                    <p>
                      Found: ${n.available_count}
                      &nbsp; Used: ${n.evidence_count}
                      &nbsp; Shown: ${n.displayed_count}
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
  `}function I(e){const s=e.source_type?`<span class="source-type">${a(e.source_type)}</span> `:"",n=a(e.title||"Untitled");return e.url?`
      ${s}<a class="result-title" href="${U(e.url)}" target="_blank" rel="noopener noreferrer">
        ${n}
      </a>
    `:`${s}<strong class="result-title">${n}</strong>`}function O(e){return a(e).split(`

`).map(s=>`<p>${s.replaceAll(`
`,"<br>")}</p>`).join("")}function a(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function U(e){return a(e)}function P(e){var r;const s=((r=e.evidence)==null?void 0:r.results)??[],n=e.accounting;return s.length===0?`
      <section class="empty-state">
        <h2>No results</h2>
        <p>No search evidence was returned for this query.</p>
        ${S(e)}
      </section>
    `:`
    <section class="search-results">
      <p class="result-count">
        ${n?`Found: ${n.available_count} · Used: ${n.evidence_count} · Shown: ${n.displayed_count}`:`${s.length} results`}
        · ${e.elapsed_ms} ms
      </p>
      ${s.map(t=>`
            <article class="search-result">
              ${renderEvidenceTitle(t)}
              ${t.url?`<div class="result-url">${h(t.url)}</div>`:""}
              <p>${h(t.snippet||"")}</p>
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
`;const N=document.querySelector("#query-form"),m=document.querySelector("#session-list"),$=document.querySelector("#selected-session"),T=document.querySelector("#new-session"),y=document.querySelector("#session"),l=document.querySelector("#query"),w=document.querySelector("#mode"),i=document.querySelector("#output"),f=document.querySelector("#empty-state");if(!N||!m||!$||!T||!y||!l||!w||!i||!f)throw new Error("missing UI elements");const u=[];let d="";const H=new URLSearchParams(window.location.search),q=H.get("query"),p=H.get("mode");async function E(){try{const e=await _();m.innerHTML=C(e),m.querySelectorAll(".session-button").forEach(s=>{s.addEventListener("click",async()=>{const n=s.dataset.session||"";if(n){y.value=n,$.textContent=`Selected: ${n}`;try{const r=await k(n);u.length=0,d=F(r.messages),i.innerHTML=d,f.hidden=!0}catch(r){i.innerHTML=g(r instanceof Error?r.message:"Unable to load session")}}})})}catch(e){m.innerHTML=`
      <p class="navigation-empty">
        Unable to load sessions: ${c(String(e))}
      </p>
    `}}E();T.addEventListener("click",()=>{const e=window.prompt("New session name:");e!=null&&e.trim()&&(y.value=e.trim(),$.textContent=`New session: ${e.trim()}`,u.length=0,d="",i.innerHTML="",f.hidden=!1,l.value="",l.focus())});q&&(l.value=q);(p==="integrated"||p==="ai_only"||p==="web_only")&&(w.value=p);N.addEventListener("submit",async e=>{var t;e.preventDefault();const s=y.value.trim(),n=l.value.trim(),r=w.value;if(n){f.hidden=!0,r==="web_only"?i.innerHTML=A():i.innerHTML=`
      ${d}
      ${b(u)}
      ${A()}
    `;try{const o=await j(n,r,s);if(!o.ok){i.innerHTML=g(((t=o.error)==null?void 0:t.message)??"Unknown error");return}if(o.mode==="web_only"){i.innerHTML=P(o);return}u.push({query:n,response:o}),i.innerHTML=`
      ${d}
      ${b(u)}
    `,await E(),l.value="",window.scrollTo({top:document.body.scrollHeight,behavior:"smooth"})}catch(o){i.innerHTML=g(o instanceof Error?o.message:"Unknown error")}}});function C(e){return`
    <section class="navigation-group">
      ${R(e.sessions)}
    </section>

    <section class="navigation-group workspace-navigation">
      <h2>Workspaces</h2>
      ${x(e.workspaces)}
    </section>
  `}function R(e){return e.length===0?`
      <p class="navigation-empty">No sessions</p>
    `:e.map(s=>`
        <button
          type="button"
          class="session-button"
          data-session="${W(s.name)}"
        >
          ${c(s.name)}
        </button>
      `).join("")}function x(e){return e.length===0?`
      <p class="navigation-empty">No workspaces</p>
    `:e.map(s=>`
        <section class="workspace-node">
          <div class="workspace-name">${c(s.name)}</div>

          <div class="workspace-children">
            ${s.sessions.map(n=>`
                  <div class="workspace-session">
                    ${c(n.name)}
                  </div>
                `).join("")}

            ${s.files.map(n=>`
                  <div class="workspace-file">
                    ${c(n.path)}
                  </div>
                `).join("")}
          </div>
        </section>
      `).join("")}function F(e){return e.length===0?`
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
                <div class="answer">${J(s.content)}</div>
              </div>
            </article>
          `).join("")}
    </section>
  `}function J(e){return c(e).split(`

`).map(s=>`<p>${s.replaceAll(`
`,"<br>")}</p>`).join("")}function A(){return`
    <section class="loading">
      <div class="spinner"></div>
      <p>Working...</p>
    </section>
  `}function g(e){return`
    <section class="error-card">
      <h2>Request failed</h2>
      <p>${c(e)}</p>
    </section>
  `}function c(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function W(e){return c(e)}
