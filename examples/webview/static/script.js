async function updateDisplay() {
    let database = document.getElementById("db-select").value;
    let table = document.getElementById("table-select").value;

    let params = new URLSearchParams({database: database, table: table}).toString();
    let response = await fetch("/api/read_table_content?" + params);

    let tableData = await response.json()

    let columns = [];
    tableData.columns.forEach((name) => columns.push({field: name}))

    let rows = [];
    tableData.rows.forEach((row) => {
        let row_data = {};
        row.forEach((value, index) => {
            row_data[tableData.columns[index]] = value;
        });
        rows.push(row_data);
    });

    const gridOptions = {
        columnDefs: columns,
        defaultColDef: {sortable: true, filter: true},
        rowSelection: 'multiple',
        animateRows: true
    }
    const eGridDiv = document.getElementById("table");
    eGridDiv.innerHTML = "";
    new agGrid.Grid(eGridDiv, gridOptions);
    gridOptions.api.setRowData(rows);
}

function updateTableList(value){
    let selector = document.getElementById("table-select");
    selector.disabled = false;

    let childrens = selector.children;
    for (let key in childrens){
        let child = childrens[key];
        if (child.style){
            if (child.dataset?.srcDb === value){
                child.style.display = "block";
            } else {
                child.style.display = "none";
            }
        }
    }
}
