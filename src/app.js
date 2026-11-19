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
})();
