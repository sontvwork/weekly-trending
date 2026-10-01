// Weekly Trending — chuyển giao diện sáng/tối. Mặc định theo hệ thống; lựa chọn của người xem lưu ở localStorage.
// Nạp đồng bộ trong <head> để áp theme trước khi trang hiện ra (không nháy màu).
(function () {
  var root = document.documentElement;
  try {
    var saved = localStorage.getItem("theme");
    if (saved === "light" || saved === "dark") root.setAttribute("data-theme", saved);
  } catch (e) {}
  document.addEventListener("DOMContentLoaded", function () {
    var button = document.getElementById("theme-toggle");
    if (!button) return;
    button.addEventListener("click", function () {
      var current = root.getAttribute("data-theme") ||
        (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      var next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  });
})();
