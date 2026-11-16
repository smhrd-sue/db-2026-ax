/* 교재·슬라이드 공통 동작 — 모션 토글, 스크롤 등장, 형광펜, 목차, 코드 복사, stepper, Mermaid */
(function () {
  "use strict";
  var root = document.documentElement;
  var isSlides = document.body.classList.contains("slides-page");

  /* ---------- 모션 켜기/끄기 ---------- */
  var KEY = "db-lecture-motion";
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) { /* 저장 못 해도 동작에는 문제 없음 */ } }
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var motionOn = stored() ? stored() === "on" : !reduce;
  var toggle = document.querySelector(".motion-toggle");
  function applyMotion() {
    root.classList.toggle("motion-on", motionOn);
    root.classList.toggle("motion-off", !motionOn);
    if (toggle) {
      toggle.textContent = motionOn ? "모션 끄기" : "모션 켜기";
      toggle.setAttribute("aria-pressed", motionOn ? "false" : "true");
    }
    if (!motionOn) document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("in"); });
  }
  applyMotion();
  if (toggle) toggle.addEventListener("click", function () { motionOn = !motionOn; save(motionOn ? "on" : "off"); applyMotion(); });

  /* ---------- 진행률 ---------- */
  var bar = document.querySelector(".progress span");
  if (bar) {
    var onScroll = function () {
      var h = root.scrollHeight - window.innerHeight;
      bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + "%";
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- 스크롤 등장 + 형광펜 ---------- */
  var hasIO = "IntersectionObserver" in window;
  function observeOnce(nodes, cls, opts) {
    if (!hasIO) { nodes.forEach(function (n) { n.classList.add(cls); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add(cls);
        io.unobserve(en.target);
      });
    }, opts);
    nodes.forEach(function (n) { io.observe(n); });
  }
  observeOnce(document.querySelectorAll(".reveal"), "in", { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
  // 표의 줄·칩 순서를 적어 두면 CSS가 한 줄씩 차례로 들여보낸다
  document.querySelectorAll("tbody").forEach(function (tb) {
    Array.prototype.forEach.call(tb.rows, function (r, n) { r.style.setProperty("--r", n); });
  });
  document.querySelectorAll(".chips").forEach(function (c) {
    Array.prototype.forEach.call(c.children, function (s, n) { s.style.setProperty("--c", n); });
  });
  // 표 안의 분홍 밑줄은 위에서부터 차례로 그어진다
  document.querySelectorAll("table").forEach(function (t) {
    t.querySelectorAll("strong, mark").forEach(function (m, i) { m.style.transitionDelay = (0.2 + i * 0.3).toFixed(2) + "s"; });
  });
  // 슬라이드의 형광펜은 slides.js 가 슬라이드를 열 때 켠다
  observeOnce(document.querySelectorAll(".content strong, .content mark"), "hl-on", { rootMargin: "0px 0px -10% 0px", threshold: 1 });

  /* ---------- 목차: 현재 위치 표시, 좁은 화면에서 열고 닫기 ---------- */
  var toc = document.getElementById("toc");
  var tocBtn = document.querySelector(".toc-toggle");
  var links = Array.prototype.slice.call(document.querySelectorAll(".toc a[href^='#']"));
  var heads = links.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); }).filter(Boolean);
  if (heads.length) {
    var markToc = function () {
      var y = window.scrollY + 90, cur = null;
      heads.forEach(function (h) { if (h.getBoundingClientRect().top + window.scrollY <= y) cur = h.id; });
      links.forEach(function (a) { a.classList.toggle("active", a.getAttribute("href") === "#" + cur); });
    };
    window.addEventListener("scroll", markToc, { passive: true });
    markToc();
  }
  if (tocBtn && toc) {
    tocBtn.addEventListener("click", function () {
      var open = toc.classList.toggle("open");
      tocBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    links.forEach(function (a) { a.addEventListener("click", function () { toc.classList.remove("open"); tocBtn.setAttribute("aria-expanded", "false"); }); });
  }

  /* ---------- 코드 복사 ---------- */
  function copyText(text, btn) {
    function ok() { btn.textContent = "복사됨"; btn.classList.add("done"); setTimeout(function () { btn.textContent = "복사"; btn.classList.remove("done"); }, 1500); }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); ok(); } catch (e) { btn.textContent = "직접 선택해 복사하세요"; }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(ok, fallback);
    else fallback();
  }
  document.querySelectorAll(".copy").forEach(function (btn) {
    btn.addEventListener("click", function () {
      copyText(btn.closest("figure").querySelector("pre code").innerText.replace(/\n$/, ""), btn);
    });
  });

  /* ---------- SQL 실행 순서 따라가기(stepper) ----------
     data-steps: [{ line, note, cols, rows, dim:[행 번호], hot:[열 이름] }, …]
     line 은 0부터 센 코드 줄 번호. cols·rows 를 빼면 표를 바꾸지 않는다. */
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

  function renderTable(box, st) {
    box.innerHTML = "";
    if (!st || !st.cols) { box.appendChild(el("p", "empty", "아직 읽은 데이터가 없습니다.")); return; }
    var hot = st.hot || [], dim = st.dim || [];
    var t = el("table"), tr = el("tr");
    st.cols.forEach(function (c) { tr.appendChild(el("th", hot.indexOf(c) >= 0 ? "hot" : "", c)); });
    var thead = el("thead"); thead.appendChild(tr); t.appendChild(thead);
    var tb = el("tbody");
    st.rows.forEach(function (r, i) {
      var row = el("tr", dim.indexOf(i) >= 0 ? "dim" : "");
      r.forEach(function (v, j) { row.appendChild(el("td", hot.indexOf(st.cols[j]) >= 0 ? "hot" : "", String(v))); });
      tb.appendChild(row);
    });
    t.appendChild(tb);
    box.appendChild(t);
  }

  document.querySelectorAll(".stepper").forEach(function (sp) {
    var steps = JSON.parse(sp.getAttribute("data-steps"));
    var lines = sp.querySelectorAll(".stepper-code li");
    var tableBox = sp.querySelector(".stepper-table");
    var note = sp.querySelector(".stepper-note");
    var count = sp.querySelector(".stepper-count");
    var btn = {};
    sp.querySelectorAll(".stepper-ctrl button").forEach(function (b) { btn[b.getAttribute("data-act")] = b; });
    var idx = -1, timer = null;

    function show(i) {
      idx = i;
      var st = i >= 0 ? steps[i] : null;
      var seen = steps.slice(0, i + 1).map(function (s) { return s.line; });
      lines.forEach(function (li, n) {
        li.classList.toggle("current", !!st && st.line === n);
        li.classList.toggle("done", !!st && st.line !== n && seen.indexOf(n) >= 0);
        var tag = li.querySelector(".step-no");
        var order = seen.indexOf(n);
        if (order >= 0 && !tag) { tag = el("span", "step-no"); li.appendChild(tag); }
        if (tag) { if (order >= 0) tag.textContent = (order + 1) + "번째"; else tag.remove(); }
      });
      var tableStep = null;
      for (var k = i; k >= 0; k--) if (steps[k].cols) { tableStep = steps[k]; break; }
      renderTable(tableBox, tableStep && tableStep === st ? st : tableStep && Object.assign({}, tableStep, { dim: st.dim || tableStep.dim, hot: st.hot || [] }));
      note.textContent = st ? st.note : "▶ 「다음」을 눌러 SQL이 실제로 실행되는 순서를 따라가 보세요.";
      count.textContent = (i + 1) + " / " + steps.length;
      btn.prev.disabled = i < 0;
      btn.reset.disabled = i < 0;
      btn.next.disabled = i >= steps.length - 1;
    }
    function stop() { if (timer) clearInterval(timer); timer = null; btn.play.textContent = "자동 재생"; }
    btn.next.addEventListener("click", function () { stop(); if (idx < steps.length - 1) show(idx + 1); });
    btn.prev.addEventListener("click", function () { stop(); if (idx >= 0) show(idx - 1); });
    btn.reset.addEventListener("click", function () { stop(); show(-1); });
    btn.play.addEventListener("click", function () {
      if (timer) { stop(); return; }
      if (idx >= steps.length - 1) show(-1);
      btn.play.textContent = "멈춤";
      timer = setInterval(function () { if (idx >= steps.length - 1) stop(); else show(idx + 1); }, 1800);
    });
    // 슬라이드에서 → / ← 키가 stepper를 먼저 한 단계씩 움직이게 한다. 끝에 닿으면 false.
    sp._next = function () { stop(); if (idx >= steps.length - 1) return false; show(idx + 1); return true; };
    sp._prev = function () { stop(); if (idx < 0) return false; show(idx - 1); return true; };
    sp._reset = function () { stop(); show(-1); };
    sp._stop = stop;
    show(-1);
  });

  /* ---------- Mermaid: 팔레트 색으로 그린다. 슬라이드에서는 보일 때 그린다(slides.js) ---------- */
  if (window.mermaid) {
    window.mermaid.initialize({
      startOnLoad: false, theme: "base", securityLevel: "strict",
      themeVariables: {
        fontFamily: "Pretendard Variable, Pretendard, Apple SD Gothic Neo, Malgun Gothic, sans-serif",
        fontSize: "16px",
        primaryColor: "#F8E4EC", primaryBorderColor: "#6E1E3B", primaryTextColor: "#2A1420",
        secondaryColor: "#EEF2CC", tertiaryColor: "#F7F6D7", lineColor: "#6E1E3B",
        attributeBackgroundColorOdd: "#FFFFFF", attributeBackgroundColorEven: "#F7F6D7"
      }
    });
  }
  // 보이는 Mermaid만 그린다. 접힌 답안 속 그림은 펼칠 때 그린다(숨은 요소에서는 크기를 잘못 잰다).
  window.__drawMermaid = function (scope) {
    if (!window.mermaid) return Promise.resolve();
    var nodes = Array.prototype.filter.call(scope.querySelectorAll(".mermaid:not([data-processed])"),
      function (n) { return !n.closest("details:not([open])"); });
    return nodes.length ? window.mermaid.run({ nodes: nodes }) : Promise.resolve();
  };
  if (!isSlides) {
    window.__drawMermaid(document);
    document.addEventListener("toggle", function (e) { if (e.target.open) window.__drawMermaid(e.target); }, true);
  }
})();
