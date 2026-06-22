(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const r of document.querySelectorAll('link[rel="modulepreload"]'))s(r);new MutationObserver(r=>{for(const n of r)if(n.type==="childList")for(const u of n.addedNodes)u.tagName==="LINK"&&u.rel==="modulepreload"&&s(u)}).observe(document,{childList:!0,subtree:!0});function o(r){const n={};return r.integrity&&(n.integrity=r.integrity),r.referrerPolicy&&(n.referrerPolicy=r.referrerPolicy),r.crossOrigin==="use-credentials"?n.credentials="include":r.crossOrigin==="anonymous"?n.credentials="omit":n.credentials="same-origin",n}function s(r){if(r.ep)return;r.ep=!0;const n=o(r);fetch(r.href,n)}})();async function v(e,t){return(await fetch("/api/v1/query",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e,mode:t,limit:5,max_chars:4e3})})).json()}function w(e){var o;const t=((o=e.evidence)==null?void 0:o.results)??[];return`
    <section class="chat">
      <article class="message user-message">
        <div class="message-label">You</div>
        <p>${a(e.query)}</p>
      </article>

      <article class="message assistant-message">
        <div class="message-label">local_ai_search</div>
        <div class="answer">${b(e.answer||"No answer returned.")}</div>
      </article>

      ${t.length>0?`
            <details class="sources" open>
              <summary>Sources</summary>
              ${t.map(s=>`
                    <article class="source">
                      <a href="${q(s.url)}" target="_blank" rel="noopener noreferrer">
                        ${a(s.title||"Untitled")}
                      </a>
                      <p>${a(s.snippet||"")}</p>
                    </article>
                  `).join("")}
            </details>
          `:""}

      <details class="debug">
        <summary>Raw response</summary>
        <pre>${a(JSON.stringify(e,null,2))}</pre>
      </details>
    </section>
  `}function b(e){return a(e).split(`

`).map(t=>`<p>${t.replaceAll(`
`,"<br>")}</p>`).join("")}function a(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function q(e){return a(e)}function $(e){var o;const t=((o=e.evidence)==null?void 0:o.results)??[];return t.length===0?`
      <section class="empty-state">
        <h2>No results</h2>
        <p>No search evidence was returned for this query.</p>
        ${m(e)}
      </section>
    `:`
    <section class="search-results">
      <p class="result-count">${t.length} results · ${e.elapsed_ms} ms</p>
      ${t.map(s=>`
            <article class="search-result">
              <a class="result-title" href="${A(s.url)}" target="_blank" rel="noopener noreferrer">
                ${i(s.title||"Untitled")}
              </a>
              <div class="result-url">${i(s.url||"")}</div>
              <p>${i(s.snippet||"")}</p>
            </article>
          `).join("")}
      ${m(e)}
    </section>
  `}function m(e){return`
    <details class="debug">
      <summary>Raw response</summary>
      <pre>${i(JSON.stringify(e,null,2))}</pre>
    </details>
  `}function i(e){return e.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}function A(e){return i(e)}const y=document.querySelector("#app");if(!y)throw new Error("missing #app");y.innerHTML=`
  <section class="shell">
    <header class="hero">
      <p class="eyebrow">local first · LAN friendly · API backed</p>
      <h1>local_ai_search</h1>
      <p>Search the web/local evidence or ask your local AI with sources.</p>
    </header>

    <form id="query-form" class="query-form">
      <input id="query" name="query" placeholder="Search or ask..." required />
      <select id="mode" name="mode">
        <option value="integrated">integrated</option>
        <option value="ai_only">ai only</option>
        <option value="web_only">web only</option>
      </select>
      <button type="submit">Run</button>
    </form>

    <section id="output" class="output"></section>
  </section>
`;const h=document.querySelector("#query-form"),p=document.querySelector("#query"),d=document.querySelector("#mode"),l=document.querySelector("#output");if(!h||!p||!d||!l)throw new Error("missing UI elements");const g=new URLSearchParams(window.location.search),f=g.get("query"),c=g.get("mode");f&&(p.value=f);(c==="integrated"||c==="ai_only"||c==="web_only")&&(d.value=c);h.addEventListener("submit",async e=>{var s;e.preventDefault();const t=p.value.trim(),o=d.value;if(t){l.innerHTML=`
    <section class="loading">
      <div class="spinner"></div>
      <p>Working...</p>
    </section>
  `;try{const r=await v(t,o);if(!r.ok){l.innerHTML=`
        <section class="error-card">
          <h2>Request failed</h2>
          <p>${((s=r.error)==null?void 0:s.message)??"Unknown error"}</p>
        </section>
      `;return}l.innerHTML=r.mode==="web_only"?$(r):w(r)}catch(r){l.innerHTML=`
      <section class="error-card">
        <h2>Request failed</h2>
        <p>${r instanceof Error?r.message:"Unknown error"}</p>
      </section>
    `}}});
