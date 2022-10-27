// JavaScript code
function search() {
    let input = document.getElementById('searchbarMsg').value
    input=input.toLowerCase();
    let x = document.getElementsByClassName('searched');
    let y = document.getElementsByClassName('hide3');
    let hiddenText = document.getElementById("hide");
    let hiddenText2 = document.getElementById("hide2");
    let tab = [];

      
    for (i = 0; i < x.length; i++) { 
        if (!x[i].innerHTML.toLowerCase().includes(input)) {
            x[i].style.display="none";
            y[i].style.display="none";
        }
        else{
            x[i].style.display="list-item"; 
            y[i].style.display="list-item"; 
            tab.push(1)                
        }
        if (input.length == 0 ){
            x[i].style.display="list-item"; 
            y[i].style.display="list-item"; 
            tab.push(1)
        }
    }
    if (tab.length==0) {
        hiddenText.style.display = "none";
        hiddenText2.style.display = "block";
    }
    else {
        hiddenText.style.display = "block";
        hiddenText2.style.display = "none";
    }
}