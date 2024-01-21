/* Create an instance of CSInterface. */
var csInterface = new CSInterface();
/* Make a reference to your HTML button and add a click handler. */
var openButton = document.querySelector("#tikManager4-button");
openButton.addEventListener("click", tikUI);
var versionButton = document.querySelector("#newVersion-button");
versionButton.addEventListener("click", tikSaveVersion);
/* Write a helper function to pass instructions to the ExtendScript side. */
function tikUI() {
  csInterface.evalScript("tikUI()");
}
function tikSaveVersion() {
  csInterface.evalScript("tikSaveVersion()");
}