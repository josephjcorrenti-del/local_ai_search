(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const r of document.querySelectorAll('link[rel="modulepreload"]'))s(r);new MutationObserver(r=>{for(const o of r)if(o.type==="childList")for(const p of o.addedNodes)p.tagName==="LINK"&&p.rel==="modulepreload"&&s(p)}).observe(document,{childList:!0,subtree:!0});function n(r){const o={};return r.integrity&&(o.integrity=r.integrity),r.referrerPolicy&&(o.referrerPolicy=r.referrerPolicy),r.crossOrigin==="use-credentials"?o.credentials="include":r.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function s(r){if(r.ep)return;r.ep=!0;const o=n(r);fetch(r.href,o)}})();async function q(e,t){return(await fetch("/api/v1/query",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e,mode:t,limit:5,max_chars:4e3})})).json()}function f(e){return e.length===0?"":`
    <section class="chat">
      ${e.map(t=>S(t)).join("")}
    </section>
  `}function S(e){var n;const t=((n=e.response.evidence)==null?void 0:n.results)??[];return`
    <section class="chat-turn">
      <article class="message user-message">
        <div class="avatar">●</div>
        <div>
          <div class="message-label">You</div>
          <p>${l(e.query)}</p>
        </div>
      </article>

      <article class="message assistant-message">
        <div class="avatar bot">◎</div>
        <div class="message-body">
          <div class="message-label assistant-label">Local AI Search</div>
          <div class="answer">${L(e.response.answer||"No answer returned.")}</div>

          ${t.length>0?`
                <details class="sources" open>
                  <summary>Sources</summary>
                  <ol>
                    ${t.map(s=>`
                          <li>
                            <a href="${T(s.url)}" target="_blank" rel="noopener noreferrer">
                              ${l(s.title||"Untitled")}
                            </a>
                            ${s.snippet?`<p>${l(s.snippet)}</p>`:""}
                          </li>
                        `).join("")}
                  </ol>
                </details>
              `:""}

          <details class="debug">
            <summary>Raw response</summary>
            <pre>${l(JSON.stringify(e.response,null,2))}</pre>
          </details>
        </div>
      </article>
    </section>
  `}function L(e){return l(e).split(`

`).map(t=>`<p>${t.replaceAll(`
`,"<br>")}</p>`).join("")}function l(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function T(e){return l(e)}function H(e){var n;const t=((n=e.evidence)==null?void 0:n.results)??[];return t.length===0?`
      <section class="empty-state">
        <h2>No results</h2>
        <p>No search evidence was returned for this query.</p>
        ${y(e)}
      </section>
    `:`
    <section class="search-results">
      <p class="result-count">${t.length} results · ${e.elapsed_ms} ms</p>
      ${t.map(s=>`
            <article class="search-result">
              <a class="result-title" href="${N(s.url)}" target="_blank" rel="noopener noreferrer">
                ${i(s.title||"Untitled")}
              </a>
              <div class="result-url">${i(s.url||"")}</div>
              <p>${i(s.snippet||"")}</p>
            </article>
          `).join("")}
      ${y(e)}
    </section>
  `}function y(e){return`
    <details class="debug">
      <summary>Raw response</summary>
      <pre>${i(JSON.stringify(e,null,2))}</pre>
    </details>
  `}function i(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function N(e){return i(e)}const b=document.querySelector("#app");if(!b)throw new Error("missing #app");b.innerHTML=`
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
`;const w=document.querySelector("#query-form"),u=document.querySelector("#query"),m=document.querySelector("#mode"),a=document.querySelector("#output"),A=document.querySelector("#empty-state");if(!w||!u||!m||!a||!A)throw new Error("missing UI elements");const d=[],$=new URLSearchParams(window.location.search),h=$.get("query"),c=$.get("mode");h&&(u.value=h);(c==="integrated"||c==="ai_only"||c==="web_only")&&(m.value=c);w.addEventListener("submit",async e=>{var s;e.preventDefault();const t=u.value.trim(),n=m.value;if(t){A.hidden=!0,n==="web_only"?a.innerHTML=g():a.innerHTML=`
      ${f(d)}
      ${g()}
    `;try{const r=await q(t,n);if(!r.ok){a.innerHTML=v(((s=r.error)==null?void 0:s.message)??"Unknown error");return}if(r.mode==="web_only"){a.innerHTML=H(r);return}d.push({query:t,response:r}),a.innerHTML=f(d),u.value="",window.scrollTo({top:document.body.scrollHeight,behavior:"smooth"})}catch(r){a.innerHTML=v(r instanceof Error?r.message:"Unknown error")}}});function g(){return`
    <section class="loading">
      <div class="spinner"></div>
      <p>Working...</p>
    </section>
  `}function v(e){return`
    <section class="error-card">
      <h2>Request failed</h2>
      <p>${O(e)}</p>
    </section>
  `}function O(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}
