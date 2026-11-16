/* 슬라이드 넘기기 — 1280×720 캔버스를 화면에 맞게 키우고, 넘치는 내용은 글자를 줄여 맞춘다 */
(function () {
  "use strict";
  var deck = document.querySelector(".deck");
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var jump = document.querySelector(".s-jump");
  var bookLink = document.querySelector(".s-book");
  var DAY = deck.getAttribute("data-day");
  var cur = 0;
  // 슬라이드 안 블록마다 순서를 적어 두면 CSS가 위에서부터 차례로 올린다
  slides.forEach(function (sl) {
    var f = sl.querySelector(".s-fit");
    if (f) Array.prototype.forEach.call(f.children, function (c, n) { c.style.setProperty("--b", n); });
  });

  function fitScale() {
    var s = Math.min(window.innerWidth / 1280, (window.innerHeight - 48) / 720) * 0.98;
    deck.style.transform = "scale(" + s + ")";
  }
  function fit(sl) {
    var body = sl.querySelector(".s-body"), inner = sl.querySelector(".s-fit");
    if (!body || !inner || sl._fitted) return;
    var s = 1;
    body.classList.remove("scroll");
    for (var k = 0; k < 6; k++) {
      inner.style.transform = "scale(" + s + ")";
      inner.style.width = (100 / s) + "%";
      var need = inner.scrollHeight * s, have = body.clientHeight;
      if (need <= have - 6) break;   // 마지막 줄 테두리가 잘리지 않게 몇 px 여유를 둔다
      s = Math.max(0.62, s * Math.max(0.8, have / need) - 0.01);
      if (s <= 0.62) {
        inner.style.transform = "scale(0.62)"; inner.style.width = (100 / 0.62) + "%";
        if (inner.scrollHeight * 0.62 > body.clientHeight + 1) body.classList.add("scroll");
        break;
      }
    }
    sl._fitted = true;
    sl.setAttribute("data-scale", s.toFixed(2));
  }
  // Mermaid는 보이지 않는 요소에서는 크기를 잘못 재므로, 슬라이드가 열릴 때 그린 뒤 다시 맞춘다.
  function drawMermaid(sl) {
    window.__drawMermaid(sl).then(function () { sl._fitted = false; fit(sl); });
  }
  function steppers(sl) { return Array.prototype.slice.call(sl.querySelectorAll(".stepper")); }

  function show(i, fromHash) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    closeZoom();
    var prev = slides[cur];
    if (prev && prev !== slides[i]) steppers(prev).forEach(function (s) { s._stop(); });
    slides.forEach(function (s, n) { s.classList.toggle("active", n === i); });
    cur = i;
    var sl = slides[i];
    fit(sl);
    drawMermaid(sl);
    // 형광펜은 슬라이드를 열 때마다 처음부터 다시 긋는다(화면 감지에 맡기지 않고 여기서 직접 켠다)
    var marks = sl.querySelectorAll(".s-fit strong, .s-fit mark");
    if (marks.length) {
      marks.forEach(function (m) { m.classList.remove("hl-on"); });
      void sl.offsetWidth;
      requestAnimationFrame(function () { requestAnimationFrame(function () { marks.forEach(function (m) { m.classList.add("hl-on"); }); }); });
    }
    var sid = sl.getAttribute("data-sid");
    if (bookLink) bookLink.href = "../" + DAY + ".html" + (sid ? "#" + sid : "");
    if (jump) {
      var best = 0;
      Array.prototype.forEach.call(jump.options, function (o, n) { if (+o.value <= i) best = n; });
      jump.selectedIndex = best;
    }
    if (!fromHash) history.replaceState(null, "", "#" + (i + 1));
  }
  // .frag(흐름·비교의 한 단계)는 → 키마다 하나씩 켠다. 모션을 끄면 처음부터 모두 보인다.
  function motionOn() { return document.documentElement.classList.contains("motion-on"); }
  // 나오는 순서: 기본은 위에서부터(문서 순서). data-step="2" 처럼 번호를 주면 그 번호 순서로, 같은 번호는 함께 나온다.
  function frags(sl, sel) { return Array.prototype.slice.call(sl.querySelectorAll(".frag" + sel)); }
  function stepOf(f, n) { return f.hasAttribute("data-step") ? +f.getAttribute("data-step") : n + 1; }
  function byStep(sl) {
    if (!sl._steps) sl._steps = frags(sl, "").map(function (f, n) { return { el: f, step: stepOf(f, n) }; });
    return sl._steps;
  }
  // 아직 안 보인 것 중 가장 작은 번호(또는 보인 것 중 가장 큰 번호) 묶음을 켜고 끈다
  function stepGroup(sl, on) {
    var list = byStep(sl).filter(function (x) { return x.el.classList.contains("on") === on; });
    if (!list.length) return null;
    var pick = list.reduce(function (m, x) { return on ? Math.max(m, x.step) : Math.min(m, x.step); }, on ? -Infinity : Infinity);
    return list.filter(function (x) { return x.step === pick; }).map(function (x) { return x.el; });
  }
  function setFrags(sl, on) { frags(sl, "").forEach(function (f) { f.classList.toggle("on", on); }); }

  function next() {
    var sl = slides[cur], sp = steppers(sl);
    if (sp.length && sp[0]._next()) return;
    var hidden = stepGroup(sl, false);
    if (motionOn() && hidden) { hidden.forEach(function (f) { f.classList.add("on"); }); return; }
    if (cur < slides.length - 1) {
      show(cur + 1);
      steppers(slides[cur]).forEach(function (s) { s._reset(); });
      setFrags(slides[cur], !motionOn());
    }
  }
  function prev() {
    var sl = slides[cur], sp = steppers(sl);
    if (sp.length && sp[0]._prev()) return;
    var shown = stepGroup(sl, true);
    if (motionOn() && shown) { shown.forEach(function (f) { f.classList.remove("on"); }); return; }
    show(cur - 1);
    setFrags(slides[cur], true);   // 뒤로 오면 이미 본 장이므로 모두 보여 준다
  }
  function fromHash() {
    var m = /^#(\d+)$/.exec(location.hash);
    show(m ? +m[1] - 1 : 0, true);
    setFrags(slides[cur], !motionOn());
  }
  function toggleFull() {
    if (!document.fullscreenElement) { if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen(); }
    else if (document.exitFullscreen) document.exitFullscreen();
  }

  document.addEventListener("keydown", function (e) {
    var t = e.target.tagName;
    if (t === "INPUT" || t === "SELECT" || t === "TEXTAREA") return;
    if (e.key === "Escape" && zoomLayer) { closeZoom(); return; }
    if (["ArrowRight", "PageDown"].indexOf(e.key) >= 0 || (e.key === " " && t !== "BUTTON" && t !== "SUMMARY")) { e.preventDefault(); next(); }
    else if (["ArrowLeft", "PageUp"].indexOf(e.key) >= 0) { e.preventDefault(); prev(); }
    else if (e.key === "Home") show(0);
    else if (e.key === "End") show(slides.length - 1);
    else if (e.key === "f" || e.key === "F") toggleFull();
  });
  document.querySelector(".s-prev").addEventListener("click", prev);
  document.querySelector(".s-next").addEventListener("click", next);
  document.querySelector(".s-full").addEventListener("click", toggleFull);
  if (jump) jump.addEventListener("change", function () { show(+jump.value); setFrags(slides[cur], !motionOn()); jump.blur(); });
  // 모션을 끄면 숨어 있던 단계를 모두 보여 준다
  var mt = document.querySelector(".motion-toggle");
  if (mt) mt.addEventListener("click", function () { if (!motionOn()) setFrags(slides[cur], true); });
  var tx = null;
  deck.addEventListener("touchstart", function (e) { tx = e.touches[0].clientX; }, { passive: true });
  deck.addEventListener("touchend", function (e) {
    if (tx == null) return;
    var dx = e.changedTouches[0].clientX - tx;
    if (Math.abs(dx) > 50) (dx < 0 ? next : prev)();
    tx = null;
  });
  // 그림을 누르면 슬라이드 전체 크기로 키워 스크롤하며 본다. 다시 누르거나 Esc로 닫는다.
  var zoomLayer = null;
  function closeZoom() { if (zoomLayer) { zoomLayer.remove(); zoomLayer = null; } }
  deck.addEventListener("click", function (e) {
    var fig = e.target.closest(".fig-mmd");
    if (!fig || zoomLayer) return;
    var svg = fig.querySelector("svg");
    if (!svg) return;
    var big = svg.cloneNode(true);
    var vb = svg.viewBox && svg.viewBox.baseVal;
    big.removeAttribute("height");
    big.style.maxWidth = "none";
    big.style.width = Math.max(1180, vb ? vb.width : 800) + "px"; // Mermaid가 그린 원래 크기(글자 16px)
    zoomLayer = document.createElement("div");
    zoomLayer.className = "zoom-layer";
    zoomLayer.appendChild(big);
    zoomLayer.addEventListener("click", closeZoom);
    deck.appendChild(zoomLayer);
  });
  // 예시 답안·정답을 펼치거나 접으면 내용 높이가 바뀌므로 다시 맞춘다.
  deck.addEventListener("toggle", function (e) {
    var sl = e.target.closest && e.target.closest(".slide");
    if (sl) { sl._fitted = false; fit(sl); drawMermaid(sl); }
  }, true);
  window.addEventListener("resize", fitScale);
  window.addEventListener("hashchange", fromHash);
  fitScale();
  fromHash();
  // 웹폰트가 늦게 들어오면 글자 폭·높이가 바뀌므로 그때 다시 맞춘다
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () {
    slides.forEach(function (s) { s._fitted = false; });
    fit(slides[cur]);
  });
})();
