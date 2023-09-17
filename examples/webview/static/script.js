let currentGrid;
let mouseDown = false;
const cellSelectStartPos = {rowId: null, colId: null};
const cellSelectStopPos = {rowId: null, colId: null};



class OsuDirectDownloadRenderer {
    // gets called once before the renderer is used
    init(params) {
        // create the cell
        this.eGui = document.createElement("div");
        this.eGui.innerHTML = `
            <a id="downloadButton" href="${params.value}">
                <img src="/static/download-fill.png" width="35%" style="vertical-align: middle;">
            </a>
       `;
    }

    getGui() {
        return this.eGui;
    }

}

function arrayRange(start, stop, step) {
    return Array.from(
        { length: (stop - start) / step + 1 },
        (value, index) => start + index * step
    );
}

function renderCellSelection(gridEvent, color) {
    const gridColumns = gridEvent.columnApi.getAllGridColumns();

    const columnsName = gridColumns.reduce((colList, col) => {
        colList.push(col.colId);
        return colList;
    }, []);

    const startColIndex = columnsName.indexOf(cellSelectStartPos.colId);
    const startRowIndex = cellSelectStartPos.rowId;

    const stopColIndex = columnsName.indexOf(cellSelectStopPos.colId);
    const stopRowIndex = cellSelectStopPos.rowId;

    const rowIdRange = arrayRange(
        Math.min(startRowIndex, stopRowIndex), 
        Math.max(startRowIndex, stopRowIndex),
        1
    )

    const rowNodeRange = rowIdRange.map((index) => gridEvent.api.getRowNode(index));

    const colNameRange = arrayRange(
        Math.min(startColIndex, stopColIndex), 
        Math.max(startColIndex, stopColIndex),
        1
    ).map((index) => columnsName[index]);

    gridColumns.filter(
        (col) => colNameRange.includes(col.colId)
    ).forEach((col) => {
        col.colDef.cellStyle = (params) => {
            if (colNameRange.includes(params.colDef.field) && rowIdRange.includes(params.rowIndex)){
                return {backgroundColor: color};
            } else {
                return {backgroundColor: "#ffffff"};
            }
        };
    });

    gridEvent.api.refreshCells({
        force: true,
        columns: colNameRange,
        rowNodes: rowNodeRange
    });
}

function handleSelectionEnd(e){
    if (mouseDown && cellSelectStartPos.rowId != null && cellSelectStopPos.rowId != null){
        renderCellSelection(e, "#ffffff");
        cellSelectStopPos.rowId = e.rowIndex;
        cellSelectStopPos.colId = e.column.colDef.field;
        renderCellSelection(e, "#b7e4ff");
    }
}

function handleSelectionStart(e){
    if (cellSelectStartPos.rowId != null && cellSelectStopPos.rowId != null) {
        renderCellSelection(e, "#ffffff");
    }
    cellSelectStartPos.rowId = e.rowIndex;
    cellSelectStartPos.colId = e.column.colDef.field;
    cellSelectStopPos.rowId = e.rowIndex;
    cellSelectStopPos.colId = e.column.colDef.field;
    renderCellSelection(e, "#b7e4ff");
}

async function updateDisplay() {
    // Default grid settings
    const gridOptions = {
        defaultColDef: {sortable: true, filter: true},
        rowSelection: "multiple",
        suppressRowClickSelection: true,
        animateRows: true,
        // enableCellTextSelection: true,
        // ensureDomOrder: true,
        suppressColumnVirtualisation: true,
        pagination: true,
        overlayLoadingTemplate: '<span class="ag-overlay-loading-center">Loading ...</span>',
        onCellMouseOver: handleSelectionEnd,
        onCellMouseDown: handleSelectionStart
    }

    // Init grid
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

    // Format columns
    const columns = tableData.columns.map((name, index) => {
        let col_params = {
            field: name, 
            headerName: name,
            headerCheckboxSelection: index === 0,
            checkboxSelection: index === 0,
            headerCheckboxSelectionFilteredOnly: true,
            floatingFilter: true,
            filterParams: {
                inRangeInclusive: true,
                maxNumConditions: 5
            },
            resizable: true,
        }

        if (name === "direct") {
            col_params.floatingFilter = false;
            col_params.pinned = "right";
            col_params.cellRenderer = OsuDirectDownloadRenderer;
        }

        return col_params;
    });

    // Format rows
    const rows = tableData.rows.map((row) =>
        row.reduce((row_data, value, index) => {
            row_data[tableData.columns[index]] = value;
            return row_data;
        }, {})
    );

    gridOptions.api.hideOverlay();
    gridOptions.api.setColumnDefs(columns);
    gridOptions.api.setRowData(rows);
    gridOptions.columnApi.autoSizeAllColumns();
}

function updateTableList(value){
    let selectorAndButtonContainer = document.getElementById("table-select-and-button");
    selectorAndButtonContainer.style.display = "inline";

    let selector = document.getElementById("table-select");
    selector.value = "";
    

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
    const colNames = currentGrid.gridOptions.columnDefs.reduce((names, colDef) => {
        names.push(colDef.field);
        return names;
    }, []);

    let idColName;
    if (colNames.includes("checksum")) {
        idColName = (colNames.includes("beatmap_id")) ? "beatmap_id" : "id"; 
    } else {
        return;
    }

    const database = document.getElementById("db-select").value;
    const ids = currentGrid.gridOptions.api.getSelectedRows().map((row) => row[idColName]);

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

document.addEventListener("mousedown", (e) => {
    if (e.button === 0)
        mouseDown = true;
});

document.addEventListener("mouseup", (e) => {
    if (e.button === 0)
        mouseDown = false;
});