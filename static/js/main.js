function loadFromApi(path, ui_elem) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      ui_elem.innerHTML = this.responseText;
    }
  };
  xhttp.open("POST", path, true);
  xhttp.send()
}
