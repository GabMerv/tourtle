function delay(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
  }
  
  function reloadPage() {
    let inputValue = document.getElementById("messageBar").value;
    let inputValue2 = document.getElementById("upadloadImage").value
    if (!inputValue && !inputValue2) {
      window.location.reload();
    }
  }
  delay(10000).then(() => reloadPage());
  