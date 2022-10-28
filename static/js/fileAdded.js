function changeColor(){
    console.log("Bijour")
    let input = document.getElementById("upadloadImage").value;
    let btn = document.getElementById("fileBtn");
    if (input.length>0){
        btn.style.background = "#c9c9c9";
    }
    else{
        btn.style.background = "#ededed";
    }
}