// Create map
var mymap = L.map('map', {
    scrollWheelZoom: false
}).setView([53.806648, -1.555624], 12).setMinZoom(6);

// Add tileset
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery &copy; <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoidGRqYW1lczEiLCJhIjoiY2tzc3FvZ2xsMDZ2MTJzb2Yyd3c0NThpayJ9.KsqhfTlr8z2tAT8SOm1LBg'
}).addTo(mymap);

// Display map scale
L.control.scale().addTo(mymap);
