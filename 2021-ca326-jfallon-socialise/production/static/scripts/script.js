"use strict";

let map; //defining global variables to be used throughout the app
let mapEvent;
const form = document.querySelector("form"); //this is the form element. Document is a special object that is the entry point to the DOM.
const inputName = document.querySelector(".form_input_name"); //get the class element
const inputDate = document.querySelector(".form_input_date");
const inputLocation = document.querySelector(".form_input_location");
const inputPeople = document.querySelector(".form_input_people");
const inputLat = document.querySelector(".form_input_lat");
const inputLng = document.querySelector(".form_input_lng");
//https://leafletjs.com/ researched leaflet documentation
//console.log(res[0].latitude);
if (navigator.geolocation)
  //Check to see if the user has geolocation enabled
  navigator.geolocation.getCurrentPosition(function (position) {
    //if it is, get their current location
    const latitude = position.coords.latitude; //get the latitude
    const longitude = position.coords.longitude; //get the longitude
    //console.log(latitude, longitude);

    const coords = [latitude, longitude]; //put the latitude and lonitude into an array. The user's coordinates are now in an array

    map = L.map("map").setView(coords, 13); //"map" is referring to the div "map" in our index.html file. leaflet uses "L" as their name space and it provides us with methods e.g. "map". "13" is the zoom level.

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map); //adding the style of map to the map...found 2 good styles and went witht the best
    //'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png' two different styles of map
    //'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

    for (let i = 0; i < res.length; i++) {
      //console.log(res[i].event_id);
      //"res" was defined in the html script tag in index.html
      //the event data coming from the database is stored in a variable called "res". We want this data so we can display all event markers on the map for every user to see
      //This for loop runs through the array of event data and displays all data as markers on the map.

      //console.log(res[i]);
      //console.log(res[i].latitude);
      //console.log(res[i].longitude);
      L.marker([res[i].latitude, res[i].longitude]) //add the marker to where-ever the latitude and longitude cooridintes are and display on map
        .addTo(map)
        .on("click", function (e) {
          //console.log(res[i].latitude, res[i].longitude);
          //When a user clicks a marker, we want to grab the coordinates from this marker and POST them to the server, once we have these coordinates, we can query the database to retrieve the specific information asscociated with that marker.

          //console.log(content);

          const latLng = e.latlng; //want to POST the latitude and longitude so that we can then query the database using these coordinates
          fetch(`${window.origin}/home`, {
            //if post is coming from home have /home here, if coming from /eventpage have /eventpage here
            method: "POST",
            credentials: "include", //any cookies included
            body: JSON.stringify(latLng), //The JSON. stringify() method converts a JavaScript object or value to a JSON string. When sending data to a web server, the data has to be a string.
            cache: "no-cache",
            headers: new Headers({
              "content-type": "application/json",
            }),
          });
        }) //global variable "map" used here, defined in above code
        .bindPopup(
          L.popup({
            //display a popup for that marker
            maxWidth: 250, //Changing the size of the popup
            minWidth: 100, //Changing the size of the popup
            autoClose: true, //we want the pop up to close
            closeOnClick: true, // close when you click on the map
            //className: ?
          })
        )
        .setPopupContent(
          `Event: ${res[i].event_name},Location: ${res[i].location}, Date: ${res[i].date}, No. of people: ${res[i].number_of_people}, Event page: <a href="/eventpage">Join Event</a>` //event popup will display the name, location, date, number of people
        );
      //.openPopup(); don't want the last event stored in the database to open its popup when the user loads their home page
    }

    //to prompt a form when the map is clicked

    map.on(
      "click",
      function (mapE) {
        //function that takes a map event
        $("#mymodal").modal("show"); //show the modal

        mapEvent = mapE; //global variable is equal to mapE

        const { lat, lng } = mapEvent.latlng; //store the lat and lng
        //console.log("The coords of the mouse are:");
        //console.log(lat, lng);
        document.querySelector(".form_input_lat").value = lat; //setting the value of the html latitude text field to contain the latitude of where ever the mouse has been clicked on
        document.querySelector(".form_input_lng").value = lng; //setting the value of the html longitude text field to contain the longitude of where ever the mouse has been clicked on
        //2 hidden fields
      },
      function () {
        alert("Could not get your location"); //If it can't get the user's location let them know in an alert
      }
    );
  });

//handling when the user clicks submit on the form
//event is needed as a parameter ('e') in order to call e.preventDefault. This stops the page from refreshing and removing the marker from the map
const btn = document.getElementById("form-btn");
//console.log(btn);
//console.log("hello");
btn.addEventListener("click", function (e) {
  //when the user clicks the form submit button, we want to display the marker on the map containing that information submitted
  e.preventDefault(); //prevent the default refresh of the page as we want the user to stay where they are as te marker is being displayed to them

  const { lat, lng } = mapEvent.latlng;
  L.marker([lat, lng]) //add the marker to where-ever the user clicks and display when they submit form
    .addTo(map) //global variable "map" used here, defined in above code
    .bindPopup(
      L.popup({
        maxWidth: 250, //Changing the size of the popup
        minWidth: 100, //Changing the size of the popup
        autoClose: true, //we want the pop up to close after clicking on it
        closeOnClick: true, // close when you click on the map
      })
    )
    .setPopupContent(
      `Event: ${inputName.value}, Location: ${inputLocation.value}, Date: ${inputDate.value}, No. of people: ${inputPeople.value}, Event page: <a href="/eventpage">Join Event` //event popup will display the name, location, date, number of people
    )
    .openPopup();
  //quick way to clear input fields after a user clicks submit. Set them all to empty strings
  inputName.value = inputLocation.value = inputDate.value = inputPeople.value = inputLat.value = inputLng.value =
    "";
  $("#mymodal").modal("hide"); //Hide the form once the user clicks submit
  //console.log("it got here");
});

const closeModalButton = document
  .getElementById("close-modal")
  .addEventListener("click", function () {
    $("#mymodal").modal("hide");
  });

//Right now the user can't access the app unless they have their location turned on. A prompt will ask them to turn on location if it is turned off.
