
// show the appropriate modal when needed
function delete_account(){
    $("#delete-account-modal").modal("show");
}

//This script gets all the user's events coming through from the /profile route in flask.
//loop through the data and display as a table
//console.log(userEvents);
userEvents.forEach((element) => {
    //loop through every element in the user events data
    let table = document.getElementById("my-events"); //get the table id from the my-events html
    let newrow = document.createElement("tr"); //create a new row
    table.append(newrow); //append this row to the table

    let event_name = document.createElement("td"); //create table data cell
    event_name.innerHTML = element["event_name"]; //change the inner html of the event name variable to the name of the event
    newrow.appendChild(event_name); //add this value to the row

    let location = document.createElement("td"); //create table data cell
    location.innerHTML = element["location"]; //change the inner html of the location variable to the location of the event
    newrow.appendChild(location); //add this value to the row

    let date = document.createElement("td"); //create table data cell
    date.innerHTML = element["date"]; //change the inner html of the date variable to the date of the event
    newrow.appendChild(date); //add this value to the row
});

