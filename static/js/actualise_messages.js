function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
  }

function reloadPage () {
    let inputValue = document.getElementById('messageBar').value;
    if (!inputValue){
        window.location.reload();
    }    
}
delay(10000).then(() => reloadPage());