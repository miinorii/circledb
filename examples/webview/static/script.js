let currentGrid;

class OsuDirectDownloadRenderer {
    // gets called once before the renderer is used
    init(params) {
        // create the cell
        this.eGui = document.createElement("div");
        this.eGui.innerHTML = `
            <a id="downloadButton" href="${params.value}" class="button is-small" style="vertical-align: 8%;"><i class="fas fa-download"></i></a>
       `;
    }

    getGui() {
        return this.eGui;
    }

}


async function updateDisplay() {
    // General grid settings
    const gridOptions = {
        defaultColDef: {sortable: true, filter: true},
        rowSelection: "multiple",
        suppressRowClickSelection: true,
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
    currentGrid = new agGrid.Grid(eGridDiv, gridOptions);

    // Fetch data
    gridOptions.api.showLoadingOverlay();

    const database = document.getElementById("db-select").value;
    const table = document.getElementById("table-select").value;

    const params = new URLSearchParams({database: database, table: table}).toString();
    const response = await fetch("/api/table/read?" + params);

    const tableData = await response.json();

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
            resizable: true,
        }

        if (name === "direct") {
            col_params.floatingFilter = false;
            col_params.pinned = "right";
            col_params.cellRenderer = OsuDirectDownloadRenderer;
        }

        columns.push(col_params);
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

async function generateCollection(){
    const database = document.getElementById("db-select").value;
    const ids = currentGrid.gridOptions.api.getSelectedRows().map((row) => row.id);

    let response = await fetch("/api/collection/create", {
        method: "POST",
        body: JSON.stringify({database: database, ids: ids}),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });

    let collectionBytes = await response.blob();
    let blobUrl = window.URL.createObjectURL(collectionBytes);

    let aTag = document.getElementById("blobDownload")
    aTag.href = blobUrl;
    aTag.download = "collection.db";
    aTag.click();

    window.URL.revokeObjectURL(blobUrl);
}