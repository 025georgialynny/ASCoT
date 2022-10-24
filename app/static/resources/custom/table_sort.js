/*
 * Written by Georgia Smith for CCPM-TIS Project
 * 15 October 2021 
 * Modified from https://www.w3schools.com/howto/howto_js_sort_table.asp 
*/

function sortTable(tableID, tableID2, columnID) {
  var table, table2, rows, rows2, switching, i, x, y, shouldSwitch, dir, switchcount = 0, n = columnID;
  table = document.getElementById(tableID);
  table2 = document.getElementById(tableID2);
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    rows2 = table2.rows;
    console.log(rows)
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 0; i < (rows.length); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      console.log(rows[i])
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      console.log(x)
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      rows2[i].parentNode.insertBefore(rows2[i + 1], rows2[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
	var oldSort = document.getElementsByClassName("headerSortUp");
while (oldSort.length)
    oldSort[0].className = oldSort[0].className.replace(/\bheaderSortUp\b/g, "");
	oldSort = document.getElementsByClassName("headerSortDown");
while (oldSort.length)
    oldSort[0].className = oldSort[0].className.replace(/\bheaderSortDown\b/g, "");
  if (dir == "asc") {
      rows[0].getElementsByTagName("TH")[n].classList.add("headerSortUp");
  }else {
      rows[0].getElementsByTagName("TH")[n].classList.add("headerSortDown");
  }
}


