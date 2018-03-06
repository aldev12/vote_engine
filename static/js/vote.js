function vote(participate_id) {
     $.get("/vote/"+ participate_id , function(data) {
         var button = document.createElement("button");
         button.classList.add("close");
         button.type = "button";
         button.textContent = "×";
         button.setAttribute("data-dismiss", "alert");
         button.setAttribute("aria-hidden", "true");
         var div2 = document.createElement("div");
         div2.classList.add("alert", "alert-dismissable", "alert-info");
         div2.setAttribute("data-alert", "alert");
         var div1 = document.createElement("div");
         div1.classList.add("messages");
         div2.textContent = data;
         var articles = document.getElementsByClassName('container');
         div2.appendChild(button);
         div1.appendChild(div2);
         articles[1].appendChild(div1);
     });

}

function table_click(param) {
    window.location = param;
}