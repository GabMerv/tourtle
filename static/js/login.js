function deleteBadThing() {
    let x = document.getElementsByClassName("inputs");
    let y = document.getElementsByClassName("hidden");
  
    for (var i = 0; i < x.length; i++) {
      if (x[i].value) {
        y[i].style.display = "none";
      } else {
        y[i].style.display = "inline";
      }
    }
  }
  
  deleteBadThing()