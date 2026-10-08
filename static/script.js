// ==========================================
// ESSENTIAL PUBLIC SERVICES
// JavaScript
// ==========================================


let map;
let markers = [];


// ==========================================
// INITIALIZE MAP
// ==========================================

function initializeMap() {

    const mapElement = document.getElementById("map");

    // Map page par nahi hai
    if (!mapElement) {
        return;
    }


    // Mumbai / Dombivli region as default
    map = L.map("map").setView(
        [19.2183, 73.0860],
        12
    );


    // OpenStreetMap tiles

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,

            attribution:
                '&copy; OpenStreetMap contributors'
        }
    ).addTo(map);


    loadFacilities();
}


// ==========================================
// LOAD FACILITIES
// ==========================================

async function loadFacilities() {

    try {

        const response = await fetch(
            "/api/facilities"
        );

        const facilities = await response.json();

        addMarkers(facilities);

    } catch (error) {

        console.error(
            "Error loading facilities:",
            error
        );

    }
}


// ==========================================
// ADD MARKERS
// ==========================================

function addMarkers(facilities) {

    // Remove existing markers

    markers.forEach(function(marker) {

        map.removeLayer(marker);

    });

    markers = [];


    facilities.forEach(function(facility) {

        if (
            facility.latitude === null ||
            facility.longitude === null
        ) {
            return;
        }


        const popupContent = `

            <div class="map-popup">

                <h3>
                    ${escapeHTML(facility.name)}
                </h3>

                <p>
                    <strong>Category:</strong>
                    ${escapeHTML(facility.category)}
                </p>

                <p>
                    ${escapeHTML(facility.address)}
                </p>

                ${
                    facility.phone
                    ?
                    `<p>
                        <strong>Phone:</strong>
                        ${escapeHTML(facility.phone)}
                    </p>`
                    :
                    ""
                }

                ${
                    facility.opening_hours
                    ?
                    `<p>
                        <strong>Hours:</strong>
                        ${escapeHTML(
                            facility.opening_hours
                        )}
                    </p>`
                    :
                    ""
                }

            </div>
        `;


        const marker = L.marker([
            facility.latitude,
            facility.longitude
        ])
        .addTo(map)
        .bindPopup(popupContent);


        marker.facilityData = facility;

        markers.push(marker);

    });

}


// ==========================================
// SEARCH FACILITIES
// ==========================================

function searchFacilities() {

    const input =
        document.getElementById("searchInput");

    if (!input) {
        return;
    }


    const searchText =
        input.value.toLowerCase().trim();


    const cards =
        document.querySelectorAll(
            ".facility-card"
        );


    cards.forEach(function(card) {

        const name =
            card.dataset.name || "";

        const category =
            card.dataset.category.toLowerCase();

        const address =
            card.dataset.address || "";


        const match =
            name.includes(searchText) ||
            category.includes(searchText) ||
            address.includes(searchText);


        if (match) {

            card.style.display = "";

        } else {

            card.style.display = "none";

        }

    });

}


// ==========================================
// CATEGORY FILTER
// ==========================================

function filterFacilities(category) {

    const cards =
        document.querySelectorAll(
            ".facility-card"
        );


    cards.forEach(function(card) {

        const cardCategory =
            card.dataset.category;


        if (
            category === "All" ||
            cardCategory === category
        ) {

            card.style.display = "";

        } else {

            card.style.display = "none";

        }

    });


    // Update active button

    const buttons =
        document.querySelectorAll(
            ".category-btn"
        );


    buttons.forEach(function(button) {

        button.classList.remove("active");

    });


    buttons.forEach(function(button) {

        if (
            button.textContent
                .trim()
                .toLowerCase()
                .includes(category.toLowerCase())
        ) {

            button.classList.add("active");

        }

    });

}


// ==========================================
// FOCUS FACILITY ON MAP
// ==========================================

function focusFacility(latitude, longitude) {

    if (!map) {
        return;
    }


    map.setView(
        [latitude, longitude],
        17
    );


    markers.forEach(function(marker) {

        const facility =
            marker.facilityData;


        if (
            facility &&
            Number(facility.latitude) === Number(latitude) &&
            Number(facility.longitude) === Number(longitude)
        ) {

            marker.openPopup();

        }

    });

}


// ==========================================
// ESCAPE HTML
// Prevent unsafe HTML inside popup
// ==========================================

function escapeHTML(value) {

    if (value === null || value === undefined) {
        return "";
    }


    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ==========================================
// PAGE LOAD
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        initializeMap();


        const searchInput =
            document.getElementById(
                "searchInput"
            );


        if (searchInput) {

            searchInput.addEventListener(
                "input",
                searchFacilities
            );

        }

    }
);