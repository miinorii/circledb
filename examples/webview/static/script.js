async function updateDisplay() {
    // General grid settings
    const gridOptions = {
        defaultColDef: {sortable: true, filter: true},
        rowSelection: "multiple",
        rowMultiSelectWithClick: true,
        animateRows: true,
        enableCellTextSelection: true,
        ensureDomOrder: true,
        suppressColumnVirtualisation: true,
        pagination: true,
        overlayLoadingTemplate: '<span class="ag-overlay-loading-center">Loading ...</span>'
    }

    // Create grid
    const eGridDiv = document.getElementById("table");
    eGridDiv.innerHTML = "";
    new agGrid.Grid(eGridDiv, gridOptions);

    // Fetch data
    gridOptions.api.showLoadingOverlay();

    const database = document.getElementById("db-select").value;
    const table = document.getElementById("table-select").value;

    const params = new URLSearchParams({database: database, table: table}).toString();
    const response = await fetch("/api/read_table_content?" + params);

    const tableData = await response.json()

    // Format data
    const columns = [];
    tableData.columns.forEach((name, index) => {
        // Default column settings
        let col_params = {
            field: name, 
            headerName: name,
            headerCheckboxSelection: (index === 0) ? true : false,
            checkboxSelection: (index === 0) ? true : false,
            headerCheckboxSelectionFilteredOnly: true,
            floatingFilter: true,
            resizable: true
        }
        columns.push(col_params)
    })

    const rows = [];
    tableData.rows.forEach((row) => {
        let row_data = {};
        row.forEach((value, index) => {
            row_data[tableData.columns[index]] = value;
        });
        rows.push(row_data);
    });

    gridOptions.api.hideOverlay();
    gridOptions.api.setColumnDefs(columns);
    gridOptions.api.setRowData(rows);
    gridOptions.columnApi.autoSizeAllColumns();
}

function updateTableList(value){
    let selector = document.getElementById("table-select");
    selector.value = "";
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
