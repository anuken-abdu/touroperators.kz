(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* меню на телефоне */
  var menu = $("#menu"), burger = $(".burger");
  if (menu && burger) {
    var shut = function (focus) { menu.hidden = true; burger.setAttribute("aria-expanded", "false"); document.body.style.overflow = ""; if (focus) burger.focus(); };
    burger.addEventListener("click", function () { menu.hidden = false; burger.setAttribute("aria-expanded", "true"); document.body.style.overflow = "hidden"; $("[data-close]", menu).focus(); });
    $("[data-close]", menu).addEventListener("click", function () { shut(true); });
    $$("a", menu).forEach(function (a) { a.addEventListener("click", function () { shut(false); }); });
    menu.addEventListener("click", function (e) { if (e.target === menu) shut(true); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !menu.hidden) shut(true); });
  }

  /* «Наверх» — после первого экрана; «Назад» — к месту, откуда перешли по пункту меню */
  var topBtn = $("[data-top]"), backBtn = $("[data-back]"), backY = null;
  var onScroll = function () {
    if (topBtn) topBtn.hidden = window.scrollY < 500;
    if (backBtn) backBtn.hidden = backY === null || Math.abs(window.scrollY - backY) < 200;
  };
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  $$('a[href^="#"]').forEach(function (a) { a.addEventListener("click", function () { backY = window.scrollY; }); });
  if (topBtn) topBtn.addEventListener("click", function () { backY = window.scrollY; window.scrollTo({ top: 0, behavior: "smooth" }); });
  if (backBtn) backBtn.addEventListener("click", function () {
    if (backY !== null) { var y = backY; backY = null; window.scrollTo({ top: y, behavior: "smooth" }); onScroll(); }
  });
  /* 3D-наклон за курсором: data-tilt. Логотипы увеличиваются сильнее, остальные блоки — мягко */
  var fine = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (fine && !calm) {
    $$("[data-tilt]").forEach(function (el) {
      var logo = el.classList.contains("lg-in"), max = logo ? 12 : 6, sc = logo ? 1.08 : 1.025, raf = 0;
      el.addEventListener("pointermove", function (e) {
        var r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(function () {
          el.style.transform = "perspective(900px) rotateX(" + (-y * max).toFixed(2) + "deg) rotateY(" + (x * max).toFixed(2) + "deg) scale(" + sc + ")";
        });
      });
      el.addEventListener("pointerleave", function () { cancelAnimationFrame(raf); el.style.transform = ""; });
    });
  }
})();
