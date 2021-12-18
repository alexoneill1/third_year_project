"use strict";

let map2; //defining global variables to be used throughout the app
let mapEvent;

participants.forEach((element) => {
  //loop through every element in the participants data
  let table = document.getElementById("mytable"); //get the table id from the event.html page
  let newrow = document.createElement("tr"); //create a new row
  table.append(newrow); //append this row to the table

  let member = document.createElement("td"); //create table data cell
  member.innerHTML = element["first_name"] + " " + element["last_name"]; //change the inner html of the member variable to the first name and last name of the participant
  newrow.appendChild(member); //add this value to the row
});
//This code creates a table and for every participant of an event, it will add a new row to the table displaying their name

const coords = [latlon.latitude, latlon.longitude]; //put the latitude and lonitude into an array. The user's coordinates are now in an array

map2 = L.map("map2").setView(coords, 15); //"map" is referring to the div "map" in our html file. leaflet uses "L" as their name space and it provides us with methods e.g. "map". "13" is the zoom level.

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map2); //adding the style of map to the map...found 2 good styles and went witht the best

L.marker([latlon.latitude, latlon.longitude]) //add the marker to where-ever the user clicks and display when they submit form
  .addTo(map2);
