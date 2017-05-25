function switchRawDataForm() {
  selectVal = document.getElementById("choose_raw_data_src").value;
  document.getElementById("raw_fitbit_form").style.display =
    (selectVal === "fitbit") ? "block" : "none";
  document.getElementById("raw_otr_form").style.display =
    (selectVal === "otr") ? "block" : "none";
}

function reformatAsOtrDate(dateStr) {
  tok = dateStr.split("-");
  return tok[0] + tok[1] + tok[2];
}

function loadOtrDataFromApi() {
  otrForm = document.getElementById("raw_otr_form");
  start_date = reformatAsOtrDate(otrForm.elements[0].value)
  end_date = reformatAsOtrDate(otrForm.elements[1].value)
  loadFromApi("otr-logbook/" + start_date + "/" + end_date,
    document.getElementById("raw_data_dump"));
}

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
