document.addEventListener('DOMContentLoaded', function () {
    // Function to add click listeners to tables
    function setupTableClickListener(tableId) {
        const table = document.getElementById(tableId);
        if (table) {
            table.addEventListener('click', function (event) {
                if (event.target.tagName === 'TD') {
                    const row = event.target.closest('tr'); // Get the parent row of the clicked cell
                    if (row) {
                        const firstCell = row.cells[0]; // Get the first cell in the row
                        if (firstCell) {
                            const cellContent = firstCell.innerText.trim(); // Get and trim the cell content
                            window.location.href = `/PlayerStats?content=${encodeURIComponent(cellContent)}`;
                        }
                    }
                }
            });
        } else {
            console.warn(`Table with ID "${tableId}" not found.`);
        }
    }

// Add click listeners to all relevant tables
const tableIds = ['Pointsleaders', 'Assistsleaders', 'Reboundleaders', 'MainTable'];
tableIds.forEach(setupTableClickListener);
});

var tabbuttons = document.querySelectorAll(".tabs .buttons button" )
var tabpanels = document.querySelectorAll(".tabs .Tabcontent " )

function showPanel(panelindex) {
    tabbuttons.forEach(function(node){
        node.style.backgroundColor="";
        node.style.color="";
    });
    tabbuttons[panelindex].style.backgroundColor='transparent';
    tabbuttons[panelindex].style.backdropFilter="none";
    tabpanels.forEach(function(node){
        node.style.display="none";
    });
    tabpanels[panelindex].style.display="block";
    tabpanels[panelindex].style.backgroundColor="transparent";
}

if (stats) {
    showPanel(2);
} else {
    showPanel(0);
}