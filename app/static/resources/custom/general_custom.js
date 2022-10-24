$(document).ready(function(){
    $('th').click(function(){
        var table = $(this).parents('table').eq(0)
        var rows = table.find('tr.sortable').toArray().sort(comparer($(this).index()))
        console.log(rows)
        if ($($(rows[0]).children("td")[$(this).index()]).children("input").length > 0){
            rows = table.find('tr.sortable').toArray().sort(select_comparer($(this).index()))
            console.log(rows)
        }
        this.asc = !this.asc
        if (!this.asc){rows = rows.reverse()}
        for (var i = 0; i < rows.length; i++){
            table.append(rows[i])
            table.append($(rows[i]['attributes']['data-bs-target']['nodeValue']))
        }
    })
});

function comparer(index) {
    return function(a, b) {
        var valA = getCellValue(a, index), valB = getCellValue(b, index)
        return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB)
    }
}

function select_comparer(index) {
    return function(a, b) {
        var valA = getSelectorValue(a, index) == "checked", valB = getSelectorValue(b, index) == "checked"
        return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB)
    }
}

function getSelectorValue(row, index) {
    return $(row).children('td').eq(index).children().attr("checked")
}

function getCellValue(row, index){ return $(row).children('td').eq(index).text() }
