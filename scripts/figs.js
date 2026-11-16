// Animate flat figures once when they scroll into view. Without JS everything is simply shown.
// Uses a plain scroll-position check (not IntersectionObserver), which fires in every browser and webview.
document.documentElement.classList.add("js");
document.addEventListener("DOMContentLoaded", function () {
  var figs = [].slice.call(document.querySelectorAll(".fig"));
  figs.forEach(function (f) {
    f.querySelectorAll(".flow > li, .vs > div, .stats > div, .timeline > li, .bars > .bar").forEach(function (el, i) {
      el.style.setProperty("--i", i);
    });
  });
  function check() {
    var line = window.innerHeight * 0.85;
    figs = figs.filter(function (f) {
      if (f.getBoundingClientRect().top < line) { f.classList.add("in"); return false; }
      return true;
    });
    if (!figs.length) { removeEventListener("scroll", onScroll); removeEventListener("resize", onScroll); }
  }
  var queued = false;
  function onScroll() { if (!queued) { queued = true; setTimeout(function () { queued = false; check(); }, 60); } }
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll);
  check();
});
