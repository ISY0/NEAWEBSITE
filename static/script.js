var tabbuttons = document.querySelectorAll(".tabs .buttons button" )
var tabpanels = document.querySelectorAll(".tabs .Tabcontent " )

function showPanel(panelindex) {
    tabbuttons.forEach(function(node){
        node.style.backgroundColor="";
        node.style.color="";
    });
    tabbuttons[panelindex].style.backgroundColor='#eee';
    tabpanels.forEach(function(node){
        node.style.display="none";
    });
    tabpanels[panelindex].style.display="block";
    tabpanels[panelindex].style.backgroundColor="white";
}

showPanel(0)