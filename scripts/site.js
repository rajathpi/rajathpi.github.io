/* Rajath Pai — portfolio behaviour: theme toggle + reveal on scroll */
(function () {
  "use strict";

  // Mark that JS is available (enables reveal animations progressively).
  document.documentElement.classList.add("js");

  // ---- Theme -------------------------------------------------
  var root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
  }

  var stored = null;
  try { stored = localStorage.getItem("theme"); } catch (e) {}
  var prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(stored || (prefersDark ? "dark" : "light"));

  function bindToggle() {
    var btn = document.querySelector(".theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  }

  // ---- Reveal on scroll --------------------------------------
  function bindReveal() {
    var items = document.querySelectorAll(".reveal");
    if (!items.length) return;
    if (!("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    items.forEach(function (el) { io.observe(el); });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindToggle();
    bindReveal();
  });
})();
