// JavaScript code
function search() {
    let input = document.getElementById("searchbar").value;
    input = input.toLowerCase();
    let x = document.getElementsByClassName("searched");
    let hiddenText = document.getElementById("hide");
    let checkboxes = document.getElementsByClassName("checkboxes");
    let infos = document.getElementsByClassName("infos");
    var filter = false;
    var filters = [];
    for (var i=0;i<checkboxes.length;i++){
        if (checkboxes[i].checked){
            filter = true;
            filters.push(checkboxes[i].name)
        }
    }
    if (input.length >= 1 || filter) {
      hiddenText.style.display = "block";
    } else {
      hiddenText.style.display = "none";
    }
    for (var i = 0; i < x.length; i++) {
      if (!x[i].innerHTML.toLowerCase().includes(input)) {
        x[i].style.display = "none";
      } else {
        if (filter){
          var display= true;
          for (var j=0 ; j < filters.length; j++){
            if (infos[i].innerHTML.indexOf(filters[j])<=-1){
              display=false
            }
          }
          if (display){
            x[i].style.display = "list-item";
          }
          else {
            x[i].style.display = "none";
          }
        }
        else {
            x[i].style.display = "list-item";
        }
        
      }
    }
  }
  