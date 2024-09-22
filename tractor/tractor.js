(function (tractorUrl, namespace, devtoolsPanelId) {
  if (window.location.href.includes(namespace)) {
    return;
  }

  window.toggleTractorPanel = () => {
    const panel = document.getElementById(devtoolsPanelId);
    panel.style.display = panel.style.display === "none" ? "block" : "none";
    const indicator = document.getElementById("tractor-on-indicator");
    indicator.style.display =
      indicator.style.display === "none" ? "inline" : "none";
  };

  window.addEventListener("load", () => {
    const b = `<button
      onclick="window.toggleTractorPanel()"
      aria-label="Open Tractor Devtools"
      style="background: none; border: 0px; padding: 0px; position: fixed; bottom: 0px; z-index: 99999; display: inline-flex; font-size: 1.5rem; margin: 0.5rem; cursor: pointer; left: 15px;"
    >
      🚜<span id="tractor-on-indicator" style="display:none;">💨</span>
    </button>
    <div id="${devtoolsPanelId}" style="border-top: solid 1px #ccc;display:none; position:absolute;left: 0;right:0;bottom:0;">
        <iframe style="width:100%; height: 800px;" frameBorder="0" src="${tractorUrl}" title="Tractor Devtools"></iframe>
    </div>
    `;
    document.body.insertAdjacentHTML("beforeend", b);
  });
})(
  window.location.protocol + "//" + window.location.host + "/__tractor__",
  "__tractor__",
  "tractor-devtools-panel"
);
