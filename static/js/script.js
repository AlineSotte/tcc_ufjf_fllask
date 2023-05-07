function openTab(tabName) {
    var i, x;
    x = document.getElementsByClassName("tab");
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
    }
    document.getElementById(tabName).style.display = "block";
    
    var menu = document.getElementsByClassName("tab-menu")[0];
    var items = menu.getElementsByTagName("li");
    for (i = 0; i < items.length; i++) {
        items[i].classList.remove("active");
    }
    menu.querySelector("[data-tab='" + tabName + "']").classList.add("active");
}