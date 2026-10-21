/* Point the shared top bar at whichever host is serving this page.
 *
 * The links in the HTML are the Read the Docs addresses, which work from
 * anywhere. When the page is served from the main project's site (its own
 * pages, or a subproject under /projects/), the bar uses that site's origin
 * instead, so a custom domain, a preview, or a local server keeps readers on
 * the host they came from. A project viewed at its own standalone address
 * keeps the Read the Docs links.
 */
(function () {
  var bar = document.querySelector(".pd-bar");
  if (!bar) return;
  var path = location.pathname;
  var root = null;
  var i = path.indexOf("/projects/");
  if (i >= 0) root = path.slice(0, i);
  else if (bar.getAttribute("data-pd-main") === "true") root = "";
  if (root === null) return;
  bar.querySelectorAll("a[data-pd-path]").forEach(function (a) {
    a.href = location.origin + root + a.getAttribute("data-pd-path");
  });
})();
