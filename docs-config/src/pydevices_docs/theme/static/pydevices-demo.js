/* Load the runner for live demos, on pages that have one.
 *
 * A demo is a `.pydevices-live-demo` block in the page's HTML. The runner is
 * the one the PyDevices website and galleries share; it boots MicroPython as
 * WebAssembly (the PyDevices stack is built in) and runs each demo's code
 * into its canvas.
 */
(function () {
  if (!document.querySelector(".pydevices-live-demo")) return;
  import("https://PyDevices.github.io/assets/chrome/docs-runtime.js").catch(function (error) {
    console.error("Unable to load the PyDevices documentation runtime:", error);
  });
})();
