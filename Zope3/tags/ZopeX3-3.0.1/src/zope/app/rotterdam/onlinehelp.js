// popup for to open the OnlinHelp in a new window
function popup(page, name, settings) {
  win = window.open(page, name, settings);
  win.focus();
}