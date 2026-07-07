(function(){const r=document.createElement("link").relList;if(r&&r.supports&&r.supports("modulepreload"))return;for(const t of document.querySelectorAll('link[rel="modulepreload"]'))s(t);new MutationObserver(t=>{for(const o of t)if(o.type==="childList")for(const u of o.addedNodes)u.tagName==="LINK"&&u.rel==="modulepreload"&&s(u)}).observe(document,{childList:!0,subtree:!0});function n(t){const o={};return t.integrity&&(o.integrity=t.integrity),t.referrerPolicy&&(o.referrerPolicy=t.referrerPolicy),t.crossOrigin==="use-credentials"?o.credentials="include":t.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function s(t){if(t.ep)return;t.ep=!0;const o=n(t);fetch(t.href,o)}})();async function q(e,r){return(await fetch("/api/v1/query",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e,mode:r,limit:5,max_chars:4e3})})).json()}function y(e){return e.length===0?"":`
    <section class="chat">
      ${e.map(r=>S(r)).join("")}
    </section>
  `}function S(e){var s;const r=((s=e.response.evidence)==null?void 0:s.results)??[],n=e.response.accounting;return`
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
          <div class="answer">${_(e.response.answer||"No answer returned.")}</div>
          ${r.length>0?`
                <details class="sources" open>
                  <summary>Evidence</summary>
                  <ol>
                    ${r.map(t=>`
                          <li>
                            ${L(t)}
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
  `}function L(e){const r=e.source_type?`<span class="source-type">${a(e.source_type)}</span> `:"",n=a(e.title||"Untitled");return e.url?`
      ${r}<a class="result-title" href="${T(e.url)}" target="_blank" rel="noopener noreferrer">
        ${n}
      </a>
    `:`${r}<strong class="result-title">${n}</strong>`}function _(e){return a(e).split(`

`).map(r=>`<p>${r.replaceAll(`
`,"<br>")}</p>`).join("")}function a(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function T(e){return a(e)}function E(e){var s;const r=((s=e.evidence)==null?void 0:s.results)??[],n=e.accounting;return r.length===0?`
      <section class="empty-state">
        <h2>No results</h2>
        <p>No search evidence was returned for this query.</p>
        ${f(e)}
      </section>
    `:`
    <section class="search-results">
      <p class="result-count">
        ${n?`Found: ${n.available_count} · Used: ${n.evidence_count} · Shown: ${n.displayed_count}`:`${r.length} results`}
        · ${e.elapsed_ms} ms
      </p>
      ${r.map(t=>`
            <article class="search-result">
              ${renderEvidenceTitle(t)}
              ${t.url?`<div class="result-url">${d(t.url)}</div>`:""}
              <p>${d(t.snippet||"")}</p>
            </article>
          `).join("")}
      ${f(e)}
    </section>
  `}function f(e){return`
    <details class="debug">
      <summary>Raw response</summary>
      <pre>${d(JSON.stringify(e,null,2))}</pre>
    </details>
  `}function d(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}const $=document.querySelector("#app");if(!$)throw new Error("missing #app");$.innerHTML=`
  <section class="app-shell">
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
        <input id="query" name="query" placeholder="Search or ask..." required />
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
`;const b=document.querySelector("#query-form"),c=document.querySelector("#query"),m=document.querySelector("#mode"),i=document.querySelector("#output"),w=document.querySelector("#empty-state");if(!b||!c||!m||!i||!w)throw new Error("missing UI elements");const p=[],A=new URLSearchParams(window.location.search),h=A.get("query"),l=A.get("mode");h&&(c.value=h);(l==="integrated"||l==="ai_only"||l==="web_only")&&(m.value=l);b.addEventListener("submit",async e=>{var s;e.preventDefault();const r=c.value.trim(),n=m.value;if(r){w.hidden=!0,n==="web_only"?i.innerHTML=v():i.innerHTML=`
      ${y(p)}
      ${v()}
    `;try{const t=await q(r,n);if(!t.ok){i.innerHTML=g(((s=t.error)==null?void 0:s.message)??"Unknown error");return}if(t.mode==="web_only"){i.innerHTML=E(t);return}p.push({query:r,response:t}),i.innerHTML=y(p),c.value="",window.scrollTo({top:document.body.scrollHeight,behavior:"smooth"})}catch(t){i.innerHTML=g(t instanceof Error?t.message:"Unknown error")}}});function v(){return`
    <section class="loading">
      <div class="spinner"></div>
      <p>Working...</p>
    </section>
  `}function g(e){return`
    <section class="error-card">
      <h2>Request failed</h2>
      <p>${H(e)}</p>
    </section>
  `}function H(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}
