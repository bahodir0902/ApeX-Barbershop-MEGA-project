document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('click', function(event) {
    if (event.target && event.target.classList.contains('delete-barber-btn')) {
        const barberId = event.target.getAttribute('data-barber-id');
        deleteBarber(barberId);
    }
});

function deleteBarber(barberId) {
    fetch('/delete-barber', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ barber_id: barberId })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Barber deleted:', data);
        window.location.href = '/';
        // Optionally update UI or provide feedback
    })
    .catch(error => console.error('Error deleting barber:', error));
}



    function initializeCustomCheckboxes() {
    const checkboxes = document.querySelectorAll('.custom-checkbox input[type="checkbox"]');

    checkboxes.forEach(checkbox => {
        // Create a new span element for the checkmark
        const checkmark = document.createElement('span');
        checkmark.classList.add('checkmark');

        // Insert the checkmark after the checkbox
        checkbox.insertAdjacentElement('afterend', checkmark);

        // Add click event listener to the label
        checkbox.closest('.custom-checkbox').addEventListener('click', function(e) {
            // Prevent the default checkbox behavior
            e.preventDefault();

            // Toggle the checked state
            checkbox.checked = !checkbox.checked;

            // Trigger the change event
            checkbox.dispatchEvent(new Event('change'));
        });

        // Add change event listener to the checkbox
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                this.closest('.custom-checkbox').classList.add('checked');
            } else {
                this.closest('.custom-checkbox').classList.remove('checked');
            }
        });
    });
}
    initializeCustomCheckboxes();
  document.body.addEventListener('change', function(event) {
        if (event.target.classList.contains('styled-select-barbers')) {
            const selectedBarberId = event.target.value;
            const barberInfoContainers = document.querySelectorAll('[id^="barber-info-container-"]');

            barberInfoContainers.forEach(container => {
                container.style.display = 'none';
            });

            const selectedBarberInfoContainer = document.getElementById(`barber-info-container-${selectedBarberId}`);
            if (selectedBarberInfoContainer) {
                selectedBarberInfoContainer.style.display = 'block';
                // Call this function after dynamically adding checkboxes
                reapplyCheckboxStyles();
            } else {
                console.error(`Div with ID barber-info-container-${selectedBarberId} not found.`);
            }
        }
    });



    document.body.addEventListener('change', function(event) {
        if (event.target.classList.contains('styled-select-to-delete-barbers')) {
            const selectedBarberId = event.target.value;
            const barberDeleteContainers = document.querySelectorAll('[id^="barber-delete-container-"]');

            barberDeleteContainers.forEach(container => {
                container.style.display = 'none';
            });

            const selectedBarberDeleteContainer = document.getElementById(`barber-delete-container-${selectedBarberId}`);
            if (selectedBarberDeleteContainer) {
                selectedBarberDeleteContainer.style.display = 'block';
                // Call this function after dynamically adding checkboxes
                reapplyCheckboxStyles();
            } else {
                console.error(`Div with ID barber-delete-container-${selectedBarberId} not found.`);
            }
        }
    });




    function reapplyCheckboxStyles() {
    const checkboxes = document.querySelectorAll('.custom-checkbox input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            if (this.checked) {
                this.nextElementSibling.style.backgroundColor = '#4caf50';
            } else {
                this.nextElementSibling.style.backgroundColor = '#eee';
            }
        });
    });
    }



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
       // console.log("Barbershop ID:", barbershopId);
       // console.log("Barber ID:", barberId);
      //  console.log("Query Value:", queryValue);

        // Proceed with the fetch if queryValue is defined
        if (queryValue) {
            fetchSuggestions('barber', `${queryValue}&barbershop_id=${barbershopId}&barber_id_hidden=${barberId}`, 'barber-name', 'barber-suggestions');
        } else {
            console.error('Query value is undefined');
        }
    });

    function fetchHaircuts() {
    const haircutSelect = document.getElementById('haircut-select');

    fetch('/get-all-haircuts')
    .then(response => response.json())
    .then(data => {
        // Clear any existing options
        haircutSelect.innerHTML = '<option value="" disabled selected>Select a haircut</option>';

        // Populate the dropdown with the fetched haircuts
        data.forEach(haircut => {
            const option = document.createElement('option');
            option.value = haircut.haircut_name;
            option.textContent = `${haircut.haircut_name} - ${haircut.price} UZS`;
            haircutSelect.appendChild(option);
        });
    })
    .catch(error => console.error('Error fetching haircuts:', error));
}


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
                            //console.log("Assigned barbershop_id:", item.barbershop_id); // Debugging output
                        }

                        // For barbers, you can store barber_id if needed
                        if (type === 'barber') {
                            form.addEventListener('submit', function (event) {
                               // console.log("Submitting form with barber_id:", document.getElementById('barber-id-hidden').value);
                                // proceed with form submission
                            });

                            let barberIdInput = document.getElementById('barber-id-hidden');
                            if (barberIdInput) {
                                barberIdInput.value = item.barber_id;
                                document.getElementById('barber-id-hidden').value = data[index].barber_id;

                                let barbershopId = document.getElementById('barbershop-id-hidden').value;
                                let barberId = document.getElementById('barber-id-hidden').value;

                                // Debugging: Check the values before proceeding
                               // console.log("Barbershop ID:", barbershopId);
                                //console.log("Barber ID:", barberId);
                                //console.log("Constructed URL:", `/get-suggestions/barber?q=${item.barber_name}&barbershop_id=${barbershopId}&barber_id_hidden=${barberId}`);

                                // Send barberId to the backend using fetch
                                function updateBarberIdAndFetchHaircuts(barberId) {
                                    // Send the barber ID to the backend to update the session
                                    fetch('/get_barber_id', {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json',
                                        },
                                        body: JSON.stringify({ barber_id: barberId }),
                                    })
                                    .then(response => response.json())
                                    .then(data => {
                                        //console.log('Barber ID updated:', data.received_barber_id);
                                        fetchHaircuts();  // Fetch haircuts after updating the barber ID
                                    })
                                    .catch(error => console.error('Error updating barber ID:', error));
                                }
                                updateBarberIdAndFetchHaircuts(barberId);
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
    const barberId = document.getElementById('barber-id-hidden').value;
    const day = this.value;

    if (barberId) {
        fetch(`/get-available-dates`)
            .then(response => response.json())
            .then(data => {
                console.log(data.available_dates);  // Debugging output
                const appointmentDayInput = document.getElementById('appointment-day');
                if (data.available_dates.length > 0) {
                    appointmentDayInput.min = data.available_dates[0];
                    appointmentDayInput.max = data.available_dates[data.available_dates.length - 1];
                }
            })
            .catch(error => console.error('Error fetching available dates:', error));
    }

    if (barberId && day) {
        fetch(`/get-available-times?barber_id=${barberId}&day=${day}`)
            .then(response => response.json())
            .then(data => {
                const availableTimesDropdown = document.getElementById('appointment-time');
                const messageContainer = document.getElementById('appointment-message');

                // Clear previous content
                availableTimesDropdown.innerHTML = '';
                messageContainer.textContent = '';

                if (data.available_times.length === 1 && (data.available_times[0].startsWith("NO") || data.available_times[0].startsWith("In this day"))) {
                    messageContainer.textContent = data.available_times[0];  // Display the message as a <p> tag
                    availableTimesDropdown.style.display = 'none';  // Hide dropdown
                } else {
                    availableTimesDropdown.innerHTML = '<option value="">Select a time</option>';
                    data.available_times.forEach(time => {
                        let option = document.createElement('option');
                        option.value = time;
                        option.textContent = time;
                        availableTimesDropdown.appendChild(option);
                    });
                     availableTimesDropdown.style.display = 'block';
                }
            })
            .catch(error => console.error('Error fetching available times:', error));
    }
});





    // Form submission handling
    const form = document.getElementById('edit-barbershop-info-form');
if (form) {
    form.addEventListener('submit', function (event) {
        event.preventDefault();
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
                initializeCustomCheckboxes();
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

    // This function is triggered when the search is performed and results are rendered


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


     if (event.target.classList.contains('add-haircut-btn')) {
        const haircutContainer = event.target.closest('.form-group-settings').querySelector('[id^="haircut-container-"]');
        const newInput = document.createElement('div');
        newInput.classList.add('input-group', 'mb-3');
        newInput.innerHTML = `
            <input type="text" class="form-control-settings" name="edit-barber-haircut_name[]" placeholder="Haircut">
            <input type="number" class="form-control-settings" name="edit-barber-haircut_price[]" placeholder="Price" style="width: 70%;">
            <input type="text" class="form-control-settings" name="edit-barber-haircut_description[]" placeholder="Description">
            <div class="input-group-append">
                <button class="btn btn-outline-secondary remove-haircut-btn" type="button">-</button>
            </div>`;
        haircutContainer.insertBefore(newInput, event.target.closest('.input-group'));

        // Hide the '+' button on the previous input group
        const prevInputGroup = newInput.previousElementSibling;
        if (prevInputGroup) {
            prevInputGroup.querySelector('.add-haircut-btn').style.display = 'none';
        }
    }

    if (event.target.classList.contains('remove-haircut-btn')) {
        const inputGroup = event.target.closest('.input-group');
        if (inputGroup) {
            const haircutContainer = inputGroup.closest('[id^="haircut-container-"]');
            inputGroup.remove();

            // Show the '+' button on the last input group
            const inputGroups = haircutContainer.querySelectorAll('.input-group');
            const lastInputGroup = inputGroups[inputGroups.length - 1];
            if (lastInputGroup) {
                const addButton = lastInputGroup.querySelector('.add-haircut-btn');
                if (addButton) {
                    addButton.style.display = 'inline-block';
                }
            }
        }
    }




});

   document.addEventListener('change', function(event) {
    if (event.target.matches('.custom-checkbox input[type="checkbox"]')) {
        const label = event.target.nextElementSibling;
        if (event.target.checked) {
            label.style.backgroundColor = '#4caf50';
        } else {
            label.style.backgroundColor = '#eee';
        }
    }
});


});
