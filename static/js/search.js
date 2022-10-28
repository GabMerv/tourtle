// JavaScript code
function search() {
    let input = document.getElementById("searchbar").value;
    input = input.toLowerCase();
    let x = document.getElementsByClassName("searched");
    let hiddenText = document.getElementById("hide");
    if (input.length >= 1) {
      hiddenText.style.display = "block";
    } else {
      hiddenText.style.display = "none";
    }
  
    for (var i = 0; i < x.length; i++) {
      if (!x[i].innerHTML.toLowerCase().includes(input)) {
        x[i].style.display = "none";
      } else {
        x[i].style.display = "list-item";
      }
    }
  }
  