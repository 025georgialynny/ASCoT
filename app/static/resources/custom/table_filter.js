$(document).ready(function(){
    var filter_val = $('.filter_searchbar');
    console.log(filter_val)
    for(var i = 0; i < filter_val.length; i++){
        $(filter_val[i]).on('keyup', filter_table);
    }
});

function filter_table(){
    var table = $(this).attr('class').split(/\s+/)[2];
    var value = $(this).val().toString().toLowerCase()
    $("tbody#"+table+ " tr#filterable").filter(function(){
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
}
