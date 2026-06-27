(function(){const r=document.createElement("link").relList;if(r&&r.supports&&r.supports("modulepreload"))return;for(const t of document.querySelectorAll('link[rel="modulepreload"]'))s(t);new MutationObserver(t=>{for(const o of t)if(o.type==="childList")for(const p of o.addedNodes)p.tagName==="LINK"&&p.rel==="modulepreload"&&s(p)}).observe(document,{childList:!0,subtree:!0});function n(t){const o={};return t.integrity&&(o.integrity=t.integrity),t.referrerPolicy&&(o.referrerPolicy=t.referrerPolicy),t.crossOrigin==="use-credentials"?o.credentials="include":t.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function s(t){if(t.ep)return;t.ep=!0;const o=n(t);fetch(t.href,o)}})();async function q(e,r){return(await fetch("/api/v1/query",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e,mode:r,limit:5,max_chars:4e3})})).json()}function f(e){return e.length===0?"":`
    <section class="chat">
      ${e.map(r=>S(r)).join("")}
    </section>
  `}function S(e){var s;const r=((s=e.response.evidence)==null?void 0:s.results)??[],n=e.response.accounting;return`
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
          <div class="answer">${L(e.response.answer||"No answer returned.")}</div>
          ${r.length>0?`
                <details class="sources" open>
                  <summary>Sources</summary>
                  <ol>
                    ${r.map(t=>`
                          <li>
                            <a href="${_(t.url)}" target="_blank" rel="noopener noreferrer">
                              ${i(t.title||"Untitled")}
                            </a>
                            ${t.snippet?`<p>${i(t.snippet)}</p>`:""}
                          </li>
                        `).join("")}
                  </ol>
                </details>
              `:""}
          ${n?`
                <details class="sources evidence-details" open>
                  <summary>Evidence</summary>
                  <section class="evidence-summary">
                    <strong>Web</strong>
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
            <pre>${i(JSON.stringify(e.response,null,2))}</pre>
          </details>
        </div>
      </article>
    </section>
  `}function L(e){return i(e).split(`

`).map(r=>`<p>${r.replaceAll(`
`,"<br>")}</p>`).join("")}function i(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function _(e){return i(e)}function T(e){var n;const r=((n=e.evidence)==null?void 0:n.results)??[];return r.length===0?`
      <section class="empty-state">
        <h2>No results</h2>
        <p>No search evidence was returned for this query.</p>
        ${y(e)}
      </section>
    `:`
    <section class="search-results">
      <p class="result-count">
        ${accounting?`Found: ${accounting.available_count} · Used: ${accounting.evidence_count} · Shown: ${accounting.displayed_count}`:`${r.length} results`}
        · ${e.elapsed_ms} ms
      </p>
      ${r.map(s=>`
            <article class="search-result">
              <a class="result-title" href="${H(s.url)}" target="_blank" rel="noopener noreferrer">
                ${l(s.title||"Untitled")}
              </a>
              <div class="result-url">${l(s.url||"")}</div>
              <p>${l(s.snippet||"")}</p>
            </article>
          `).join("")}
      ${y(e)}
    </section>
  `}function y(e){return`
    <details class="debug">
      <summary>Raw response</summary>
      <pre>${l(JSON.stringify(e,null,2))}</pre>
    </details>
  `}function l(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function H(e){return l(e)}const b=document.querySelector("#app");if(!b)throw new Error("missing #app");b.innerHTML=`
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
`;const $=document.querySelector("#query-form"),u=document.querySelector("#query"),m=document.querySelector("#mode"),a=document.querySelector("#output"),w=document.querySelector("#empty-state");if(!$||!u||!m||!a||!w)throw new Error("missing UI elements");const d=[],A=new URLSearchParams(window.location.search),h=A.get("query"),c=A.get("mode");h&&(u.value=h);(c==="integrated"||c==="ai_only"||c==="web_only")&&(m.value=c);$.addEventListener("submit",async e=>{var s;e.preventDefault();const r=u.value.trim(),n=m.value;if(r){w.hidden=!0,n==="web_only"?a.innerHTML=g():a.innerHTML=`
      ${f(d)}
      ${g()}
    `;try{const t=await q(r,n);if(!t.ok){a.innerHTML=v(((s=t.error)==null?void 0:s.message)??"Unknown error");return}if(t.mode==="web_only"){a.innerHTML=T(t);return}d.push({query:r,response:t}),a.innerHTML=f(d),u.value="",window.scrollTo({top:document.body.scrollHeight,behavior:"smooth"})}catch(t){a.innerHTML=v(t instanceof Error?t.message:"Unknown error")}}});function g(){return`
    <section class="loading">
      <div class="spinner"></div>
      <p>Working...</p>
    </section>
  `}function v(e){return`
    <section class="error-card">
      <h2>Request failed</h2>
      <p>${N(e)}</p>
    </section>
  `}function N(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}
