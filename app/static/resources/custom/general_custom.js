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

    $("button#primer_delete").click(function(event) {
        event.preventDefault();
    
        var to_delete =  $(this).parents('tr').find("td.headcol").text().trim()
        var row = $(this).parents('tr')
        console.log(to_delete)

       // Send form data to Flask server
       $.ajax({
        url: "/delete_primer/" + to_delete,
        type: "POST",
        data: to_delete,
        processData: false,
        contentType: false,
        success: function(response) {
          // Handle server response
          row.children().find(".headcol").removeClass("headcoll")
          row.addClass("deleted_primer")
        },
        error: function(xhr, status, error) {
          // Handle error
          console.log("FAILES")
          console.error(error);
        }
      });


    });
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

$(document).ready(function() {
    // Show popup on button click
    
    $("#uploadButton").click(function() {
      $(".popup").show();
    });

    // Hide popup on form submission
    $("#uploadForm").submit(function(e) {
      e.preventDefault();
      $(".popup").hide();

      // Prepare form data
      var formData = new FormData(this);

      // Send form data to Flask server
      $.ajax({
        url: "/upload_primer",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
          // Handle server response
          console.log(response);
        },
        error: function(xhr, status, error) {
          // Handle error
          console.error(error);
        }
      });
    });

    $("#uploadForm").on('change', 'input[type="file"]', function(e) {
        var file = e.target.files[0];
        var columnOptions = [
            "pair_set",
            "primer_num",
            "primer_details",
            "gene",
            "exon",
            "rsid",
            "diplotype",
            "pnum",
            "M13",
            "direction"
        ]
        if (file) {
          var reader = new FileReader();
          reader.onload = function(e) {
            var csvData = e.target.result;
            var lines = csvData.split('\n');
            var tableBody = $("#columnMappingTable tbody");
            tableBody.empty();
  
            if (lines.length > 0) {
              var labels = lines[0].split(',');
              for (var i = 0; i < labels.length; i++) {
                var row = $("<tr>");
                row.append($("<td>").text(labels[i]));
                var selectOptions = '<option value="">Select</option>';
                for (var j = 0; j < columnOptions.length; j++) {
                    selectOptions += '<option value="' + columnOptions[j] + '">' + columnOptions[j] + '</option>';
                }
                row.append($("<td>").html('<select name="column' + (i+1) + '">' + selectOptions + '</select>'));
                tableBody.append(row);
              }
            }
          };
          reader.readAsText(file);
        }
      });
  });

  
