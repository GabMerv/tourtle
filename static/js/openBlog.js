function search() {
    let path = window.location.href;
    let splited_tab = path.split("/");
    let id = splited_tab[splited_tab.length - 1];
    id = id.substring(1);
    let blog = document.getElementById(id);
    blog.open = true;
  }
  search();
  