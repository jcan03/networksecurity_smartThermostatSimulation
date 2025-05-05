// T00686800 Joel Canonico COMP 3260 Project 

// default security settings, true by default
let securitySettings = {
  acl: true,
  login_validation: true,
  dos_protection: true
};

// on the page load, set checkboxes based on default security settings and load thermostat list
document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("acl_toggle").checked = securitySettings.acl;
  document.getElementById("login_validation_toggle").checked = securitySettings.login_validation;
  document.getElementById("dos_protection_toggle").checked = securitySettings.dos_protection;
  listThermostats();
});

// login function that sends credentials to the backend and handles login status
function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  })
  .then(response => response.json())
  .then(data => { // update UI (show thermostats and simulation tools) and messages based on success
    if (data.success) {
      document.getElementById("status").innerText = "Status: Logged in as " + username;
      document.getElementById("login-section").style.display = "none";
      document.getElementById("control-section").style.display = "block";
      listThermostats();
    } else {
      alert("Login failed: " + data.message); // if failed, just say unsuccessful
    }
  });
}

// logout function which calls the backend to clear session and updates the UI
function logout() {
  fetch("/logout", { method: "POST" })
    .then(response => response.json())
    .then(data => { // after logging out, update status and UI to show the login page only 
      document.getElementById("status").innerText = "Status: Not logged in.";
      document.getElementById("control-section").style.display = "none";
      document.getElementById("login-section").style.display = "block";
      document.getElementById("attack-status").innerText = "";
    });
}

// update security settings, sends new settings to the backend and updates local status
function updateSecurity() {
  // set all security measures to true by default, put in array
  const acl = document.getElementById("acl_toggle").checked;
  const login_validation = document.getElementById("login_validation_toggle").checked;
  const dos_protection = document.getElementById("dos_protection_toggle").checked;
  securitySettings = { acl, login_validation, dos_protection };

  // listen for changes in security checkboxes and provide message if successful
  fetch("/update_security", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(securitySettings)
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById("status").innerText = "Security settings updated.";
  });
}

// fetch and display the list of thermostats from the backend
function listThermostats() {
  fetch("/list_thermostats")
    .then(response => response.json())
    .then(data => {

      // if successful, provides array of all thermostats
      if (data.success) {
        const listDiv = document.getElementById("thermostat-list");
        listDiv.innerHTML = ""; // clear list temporarily

        // display all of the thermostats in order, add to bottom, remove pops the specific thermostat
        data.thermostats.forEach(thermo => {
          const thermoDiv = document.createElement("div");
          thermoDiv.className = "thermostat-item";
          thermoDiv.innerHTML = `
            <p>ID: ${thermo.id}</p>
            <p>Temperature: ${thermo.temperature}°C</p>
            <input type="number" id="temp_${thermo.id}" placeholder="New Temperature" min="10" max="25">
            <button onclick="setTemperature('${thermo.id}')">Set Temperature</button>
            <button onclick="removeThermostat('${thermo.id}')">Remove</button>
            <hr>`;
          listDiv.appendChild(thermoDiv); // this is what adds to bottom
        });
      }
    });
}

// add a new thermostat by calling the backend; refresh list on success.
function addThermostat() {
  fetch("/add_thermostat", {
    method: "POST",
    headers: {"Content-Type": "application/json"}
  })
  .then(response => response.json())
  .then(data => {

    // if successful, adds and updates list, updates status 
    if (data.success) {
      listThermostats();
      document.getElementById("status").innerText = "Thermostat added successfully.";
    } else {
      alert("Failed to add thermostat: " + data.message); // if there's an issue adding it sends message
    }
  });
}

// remove a thermostat by its ID, update UI after successful removal
function removeThermostat(thermoId) {
  fetch("/remove_thermostat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ thermostat_id: thermoId })
  })
  .then(response => response.json())
  .then(data => {

    // if successful, provides updated list and pops the specific thermostat from array (backend)
    if (data.success) {
      listThermostats();
      document.getElementById("status").innerText = "Thermostat removed successfully.";
    } else {
      alert("Failed to remove thermostat: " + data.message); // error message if not successful
    }
  });
}

// set the temperature for a thermostat by sending the new value to the backend.
function setTemperature(thermoId) {
  const temperature = document.getElementById("temp_" + thermoId).value;
  fetch("/set_temperature", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ thermostat_id: thermoId, temperature: temperature }) // update temperature
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById("status").innerText = data.message; // update the status with temperature being updated
    listThermostats(); // show the newly updated list with new temperature 
  });
}

// simulate a DoS attack with a user-specified intensity and display the result
function simulateDosAttack() {
  const intensity = prompt("Enter attack intensity (low, medium, high):", "low"); // default low
  fetch(`/simulate_dos?intensity=${intensity}`)
    .then(response => response.json())
    .then(data => {
      // show the message of the percent of packets getting through and response time
      document.getElementById("attack-status").innerText =
        `${data.message} (Response Time: ${data.response_time.toFixed(2)} seconds)`;
    });
}

// simulate an unauthorized access attempt and display the backend's response.
function simulateUnauthorizedAccess() {
  fetch("/simulate_unauthorized")
    .then(response => response.json())
    .then(data => {
      document.getElementById("attack-status").innerText = data.message; // send success or unsuccessful message
    });
}