document.addEventListener('DOMContentLoaded', function () {
    const toggleCardBtn = document.getElementById('toggle-card-btn');
    const toggleCardEditBtn = document.getElementById('toggle-card-edit-btn');
    const toggleDeleteBarbershopBtn = document.getElementById('toggle-delete-barbershop-btn');
    const toggleAddAppointmentBtn = document.getElementById('toggle-add-appointment-btn');

    const cardContent = document.getElementById('card-content');
    const editCardContent = document.getElementById('edit-card-content');
    const DeleteBarbershopContent = document.getElementById('delete-barbershop-content');
    const addAppointmentContent = document.getElementById('add-appointment-content');

    // Function to toggle display and icon
    function toggleContent(button, content) {
        if (content.style.display === 'none' || content.style.display === '') {
            content.style.display = 'block';
            button.querySelector('i').className = 'fas fa-minus';
        } else {
            content.style.display = 'none';
            button.querySelector('i').className = 'fas fa-plus';
        }
    }

    // Check if elements exist before adding event listeners
    if (toggleCardBtn && cardContent) {
        toggleCardBtn.addEventListener('click', function () {
            toggleContent(toggleCardBtn, cardContent);
        });
    }

    if (toggleCardEditBtn && editCardContent) {
        toggleCardEditBtn.addEventListener('click', function () {
            toggleContent(toggleCardEditBtn, editCardContent);
        });
    }

    if (toggleDeleteBarbershopBtn && DeleteBarbershopContent) {
        toggleDeleteBarbershopBtn.addEventListener('click', function () {
            toggleContent(toggleDeleteBarbershopBtn, DeleteBarbershopContent);
        });
    }


    if (toggleAddAppointmentBtn) {
        toggleAddAppointmentBtn.addEventListener('click', function () {
            if (addAppointmentContent.style.display === 'none' || addAppointmentContent.style.display === '') {
                addAppointmentContent.style.display = 'block';
            } else {
                addAppointmentContent.style.display = 'none';
            }
        });
    }

    const toggleAppointmentsListBtn = document.getElementById('toggle-appointments-list-btn');
    const appointmentsListContent = document.getElementById('appointments-list-content');
    if (toggleAppointmentsListBtn) {
        toggleAppointmentsListBtn.addEventListener('click', function () {
            if (appointmentsListContent.style.display === 'none' || appointmentsListContent.style.display === '') {
                loadAppointments(); // Load appointments via AJAX
                appointmentsListContent.style.display = 'block';
            } else {
                appointmentsListContent.style.display = 'none';
            }
        });
    }


    function loadAppointments() {
    fetch(listAppointments)
        .then(response => response.json())
        .then(data => {
            const appointmentsList = document.getElementById('appointments-list');
            appointmentsList.innerHTML = ''; // Clear existing appointments

            data.appointments.forEach(appointment => {
                const appointmentItem = document.createElement('div');
                appointmentItem.className = 'appointment-card';
                appointmentItem.innerHTML = `
                    <div class="appointment-header">
                        <h3>Appointment with: ${appointment.barber_first_name} ${appointment.barber_last_name}</h3>
                    </div>
                    <div class="appointment-body">
                        <p class="appointment-id">Appointment ID: ${appointment.appointment_id}</p>
                        <p class="customer-id">Customer ID: ${appointment.customer_id}</p>
                        <p class="customer-first-name">Customer First Name: ${appointment.customer_first_name}</p>
                        <p class="customer-last-name">Customer Last Name: ${appointment.customer_last_name}</p>
                        <p class="customer-phone-number">Customer Phone Number: ${appointment.customer_phone_number}</p>
                        <p class="appointment-date">Appointment Date: ${appointment.appointment_date}</p>
                        <p class="appointment-time">Appointment Time: ${appointment.appointment_time}</p>
                        <p class="duration-minutes">Duration: ${appointment.duration_minutes} minutes</p>
                        <p class="barbershop-name">Barbershop Name: ${appointment.barbershop_name}</p>
                        <p class="address">Barbershop Location: ${appointment.address}</p>
                        <p class="barber-first-name">Barber Name: ${appointment.barber_first_name} ${appointment.barber_last_name}</p>
                        <p class="haircut-name">Haircut Name: ${appointment.haircut_name}</p>
                        <p class="price">price: ${appointment.price} sum</p>
                        <p class="created-date">Created date: ${appointment.created_date}</p>
                    </div>
                     <form class="delete-appointments-container" method="post" action="/delete-appointment">
                        <input type="hidden" name="appointment_id" value="${appointment.appointment_id}">
                        <button type="submit" class="delete-appointment-button">Delete appointment</button>
                        <p>Note: Deleting an appointment will result in its cancellation.</p>
                    </form>
                `;
                appointmentsList.appendChild(appointmentItem);
            });
        })
        .catch(error => console.error('Error loading appointments:', error));
}


    document.getElementById('add-appointment-barbershop-name').addEventListener('input', function() {
    fetchSuggestions('barbershop', this.value, 'add-appointment-barbershop-name', 'barbershop-suggestions');
});

        document.getElementById('barber-name').addEventListener('input', function() {
        // Retrieve the barbershop and barber IDs from the hidden input fields
        let barbershopId = document.getElementById('barbershop-id-hidden').value;
        let barberId = document.getElementById('barber-id-hidden').value;

        // Capture the value of the input field
        let queryValue = this.value;

        // Debugging: Check the values before proceeding
        console.log("Barbershop ID:", barbershopId);
        console.log("Barber ID:", barberId);
        console.log("Query Value:", queryValue);

        // Proceed with the fetch if queryValue is defined
        if (queryValue) {
            fetchSuggestions('barber', `${queryValue}&barbershop_id=${barbershopId}&barber_id_hidden=${barberId}`, 'barber-name', 'barber-suggestions');
        } else {
            console.error('Query value is undefined');
        }
    });

    const haircutSelect = document.getElementById('haircut-select');

    fetch('/get-all-haircuts')
    .then(response => response.json())
    .then(data => {
        // Clear any existing options
        haircutSelect.innerHTML = '';

        // Populate the dropdown with the fetched haircuts
        data.forEach(haircut => {
            const option = document.createElement('option');
            option.value = haircut.haircut_name;  // Set the value to the haircut name
            option.textContent = `${haircut.haircut_name} - ${haircut.price} UZS`;  // Display both name and price
            haircutSelect.appendChild(option);
        });
    })
    .catch(error => console.error('Error fetching haircuts:', error));


   function fetchSuggestions(type, query, inputFieldId, suggestionDivId) {
        let suggestionDiv = document.getElementById(suggestionDivId);

        if (query.trim() === '') {
            suggestionDiv.innerHTML = '';
            return;
        }

        fetch(`/get-suggestions/${type}?q=` + query)
            .then(response => response.json())
            .then(data => {
                suggestionDiv.innerHTML = ''; // Clear previous suggestions

                data.forEach((item, index) => {
                    let div = document.createElement('div');
                    if (type === 'barbershop') {
                        div.textContent = item.barbershop_name;
                    } else if (type === 'barber') {
                        div.textContent = item.barber_name;
                    } else {
                        div.textContent = item; // For other types like haircut, where the data is just a string
                    }

                    div.classList.add('suggestion-item');
                    div.addEventListener('click', function() {
                        document.getElementById(inputFieldId).value = this.textContent;

                        // Correctly set barbershop ID if selecting a barbershop
                        if (type === 'barbershop') {
                            document.getElementById('barbershop-id-hidden').value = data[index].barbershop_id;
                            console.log("Assigned barbershop_id:", item.barbershop_id); // Debugging output
                        }

                        // For barbers, you can store barber_id if needed
                        if (type === 'barber') {
                            form.addEventListener('submit', function (event) {
                                console.log("Submitting form with barber_id:", document.getElementById('barber-id-hidden').value);
                                // proceed with form submission
                            });

                            let barberIdInput = document.getElementById('barber-id-hidden');
                            if (barberIdInput) {
                                barberIdInput.value = item.barber_id;
                                document.getElementById('barber-id-hidden').value = data[index].barber_id;

                                let barbershopId = document.getElementById('barbershop-id-hidden').value;
                                let barberId = document.getElementById('barber-id-hidden').value;

                                // Debugging: Check the values before proceeding
                                console.log("Barbershop ID:", barbershopId);
                                console.log("Barber ID:", barberId);
                                console.log("Constructed URL:", `/get-suggestions/barber?q=${item.barber_name}&barbershop_id=${barbershopId}&barber_id_hidden=${barberId}`);

                                // Send barberId to the backend using fetch
                                fetch('/get_barber_id', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ barber_id: barberId })
                                })
                                .then(response => response.json())
                                .then(data => {
                                    console.log('Success:', data);
                                })
                                .catch((error) => {
                                    console.error('Error:', error);
                                });
                            } else {
                                console.error('Hidden input for barber_id not found.');
                            }
                        }



                        suggestionDiv.innerHTML = ''; // Clear suggestions after selection
                    });
                    suggestionDiv.appendChild(div);
                });
            })
            .catch(error => console.error('Error loading suggestions:', error));
    }





   document.getElementById('appointment-day').addEventListener('change', function() {
    const barberId = document.getElementById('barber-id').value;
    const day = this.value;

    if (barberId && day) {
        fetch(`/get-available-times?barber_id=${barberId}&day=${day}`)
            .then(response => response.json())
            .then(data => {
                const availableTimesDropdown = document.getElementById('appointment-time');
                availableTimesDropdown.innerHTML = '<option value="">Select a time</option>';

                data.available_times.forEach(time => {
                    let option = document.createElement('option');
                    option.value = time;
                    option.textContent = time;
                    availableTimesDropdown.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching available times:', error));
    }
});

document.getElementById('barber-name').addEventListener('change', function() {
    const day = document.getElementById('appointment-day').value;
    if (this.value && day) {
        document.getElementById('appointment-day').dispatchEvent(new Event('change'));
    }
});



    // Form submission handling
    const form = document.getElementById('edit-barbershop-info-form');
    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();  // Prevent the default form submission

            const formData = new FormData(form);

            fetch(findBarbershop, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                 const searchResultsDiv = document.getElementById('search-results');
                 searchResultsDiv.innerHTML = data.results_html;
                  if (data.results_html.trim() !== '<div class="search-result-item">No barbershops found</div>') {
                  searchResultsDiv.style.display = 'block';
                } else {
                    searchResultsDiv.style.display = 'block';
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }



    const deleteForm = document.getElementById('delete-barbershop-form');
    if (deleteForm) {
        deleteForm.addEventListener('submit', function (event) {
            event.preventDefault();  // Prevent the default form submission

            const deleteFormData = new FormData(deleteForm);
            fetch(findDeleteBarbershop, {
                method: 'POST',
                body: deleteFormData
            })
            .then(response => response.json())
            .then(data => {
                 const deleteSearchResults = document.getElementById('delete-search-results');
                 deleteSearchResults.innerHTML = data.result_html;
                  if (data.result_html.trim() !== '<div class="delete-search-results">No barbershops found</div>') {
                  deleteSearchResults.style.display = 'block';
                } else {
                    deleteSearchResults.style.display = 'block';
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }


    // Toggle search result items
    document.addEventListener('click', function (event) {
        if (event.target.closest('.toggle-search-result-btn')) {
            const button = event.target.closest('.toggle-search-result-btn');
            const content = button.closest('.search-result-item').querySelector('.search-result-content');
            toggleContent(button, content);
        }
         if (event.target.closest('.toggle-edit-barbershop-settings-btn')) {
            const button = event.target.closest('.toggle-edit-barbershop-settings-btn');
            const content = button.closest('.edit-barbershop-settings-container').querySelector('.edit-settings-content');
            toggleContent(button, content);
        }

        if (event.target.closest('.toggle-add-barbers-btn')) {
            const button = event.target.closest('.toggle-add-barbers-btn');
            const content = button.closest('.settings-add-barbers-container').querySelector('.settings-add-barbers-content');
            toggleContent(button, content);
        }

         if (event.target.closest('.toggle-edit-barbers-btn')) {
            const button = event.target.closest('.toggle-edit-barbers-btn');
            const content = button.closest('.settings-edit-barbers-container').querySelector('.settings-edit-barbers-content');
            toggleContent(button, content);
        }

        if (event.target.closest('.toggle-delete-barbers-btn')) {
            const button = event.target.closest('.toggle-delete-barbers-btn');
            const content = button.closest('.settings-delete-barbers-container').querySelector('.settings-delete-barbers-content');
            toggleContent(button, content);
        }

         if (event.target.closest('.toggle-add-haircuts-btn')) {
            const button = event.target.closest('.toggle-add-haircuts-btn');
            const content = button.closest('.settings-add-haircuts-container').querySelector('.settings-add-haircuts-content');
            toggleContent(button, content);
        }

         if (event.target.closest('.toggle-edit-haircuts-btn')) {
            const button = event.target.closest('.toggle-edit-haircuts-btn');
            const content = button.closest('.settings-edit-haircuts-container').querySelector('.settings-edit-haircuts-content');
            toggleContent(button, content);
        }

        if (event.target.closest('.toggle-delete-haircuts-btn')) {
            const button = event.target.closest('.toggle-delete-haircuts-btn');
            const content = button.closest('.settings-delete-haircuts-container').querySelector('.settings-delete-haircuts-content');
            toggleContent(button, content);
        }

        if (event.target.closest('.toggle-delete-search-result-btn')) {
            const button = event.target.closest('.toggle-delete-search-result-btn');
            const content = button.closest('.delete-search-results').querySelector('.delete-search-result-content');
            toggleContent(button, content);
        }

        if (event.target.classList.contains('add-haircut-btn')) {
        const haircutContainer = event.target.closest('.form-group-settings').querySelector('#haircut-container');
        const newInput = document.createElement('div');
        newInput.classList.add('input-group', 'mb-3');
        newInput.innerHTML = `
             <input type="text" class="form-control-settings" name="haircut_name[]" placeholder="Haircut" required>
                <input type="text" class="form-control-settings" name="haircut_price[]" placeholder="Price" required>
                <input type="text" class="form-control-settings" name="haircut_description[]" placeholder="Description" required>
                <div class="input-group-append">
                    <button class="btn btn-outline-secondary remove-haircut-btn" type="button">-</button>
                </div>`;
        haircutContainer.appendChild(newInput);
    }

    if (event.target.classList.contains('remove-haircut-btn')) {
        const inputGroup = event.target.closest('.input-group');
        if (inputGroup) {
            inputGroup.remove();
        }
    }

    });
});
