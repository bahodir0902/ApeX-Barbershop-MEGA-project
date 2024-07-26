// script.js

const barbershopData = [
    {
        name: "Barbershop 1",
        link: "barbershop-1.com",
        haircut: "Crew Cut",
        barber: "Usta Husan",
        location: "Somewhere",
        time: "10:00",
        price: "70.000 UZS",
        rating: "5.0 ⭐"
    },
    // Add more data as needed
];

function populateTables() {
    const container = document.getElementById('barbershopTables');

    barbershopData.forEach((shop) => {
        const table = document.createElement('table');
        table.className = 'barbershop-table';

        table.innerHTML = `
            <tr><th>Barbershop</th><td><a href="https://${shop.link}">${shop.name}</a></td></tr>
            <tr><th>Target Haircut</th><td>${shop.haircut}</td></tr>
            <tr><th>Barber</th><td>${shop.barber}</td></tr>
            <tr><th>Location</th><td>${shop.location}</td></tr>
            <tr><th>Available Day</th><td>Open in Google Maps</td></tr>
            <tr><th>Available Hour</th><td>${shop.time}</td></tr>
            <tr><th>Rating</th><td>${shop.rating}</td></tr>
            <tr><th>Price</th><td>${shop.price}</td></tr>
        `;

        container.appendChild(table);
    });
}

document.addEventListener('DOMContentLoaded', populateTables);
