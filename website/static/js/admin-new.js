document.addEventListener('DOMContentLoaded', function () {

    const toggleCardBtn = document.getElementById('toggle-card-btn');
    const toggleCardEditBtn = document.getElementById('toggle-card-edit-btn');
    const toggleDeleteBarbershopBtn = document.getElementById('toggle-delete-barbershop-btn');
    const toggleAddAppointmentBtn = document.getElementById('toggle-add-appointment-btn');
    const toggleListAppointmentBtn = document.getElementById('toggle-upcoming-appointments-list-btn');
    const toggleAddBarberBtn = document.getElementById('toggle-add-barbers-btn');
    const toggleEditBarberBtn = document.getElementById('toggle-edit-barbers-btn');
    const toggleDeleteBarberBtn = document.getElementById('toggle-delete-barbers-btn');
    const toggleFinishedAppointmentsBtn = document.getElementById('toggle-finished-appointments-list-btn');
    const toggleCanceledAppointmentsBtn = document.getElementById('toggle-canceled-appointments-list-btn');



    const cardContent = document.getElementById('card-content');
    const editCardContent = document.getElementById('edit-card-content');
    const DeleteBarbershopContent = document.getElementById('delete-barbershop-content');
    const addAppointmentContent = document.getElementById('add-appointment-content');
    const listAppointmentContent = document.getElementById('upcoming-appointments-list-content');
    const addBarberContent = document.getElementById('add-barbers-content');
    const editBarberContent = document.getElementById('edit-barbers-content');
    const deleteBarberContent = document.getElementById('delete-barbers-content');
    const finishedAppointmentsContent = document.getElementById('finished-appointments-list-content');
    const canceledAppointmentsContent = document.getElementById('canceled-appointments-list-content');


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

     if (toggleAddBarberBtn && addBarberContent) {
        toggleAddBarberBtn.addEventListener('click', function () {
            toggleContent(toggleAddBarberBtn, addBarberContent);
        });
    }

     if (toggleEditBarberBtn && editBarberContent) {
        toggleEditBarberBtn.addEventListener('click', function () {
            toggleContent(toggleEditBarberBtn, editBarberContent);
        });
    }

     if (toggleDeleteBarberBtn && deleteBarberContent) {
        toggleDeleteBarberBtn.addEventListener('click', function () {
            toggleContent(toggleDeleteBarberBtn, deleteBarberContent);
        });
    }

    if (toggleAddAppointmentBtn && addAppointmentContent) {
        toggleAddAppointmentBtn.addEventListener('click', function () {
            toggleContent(toggleAddAppointmentBtn, addAppointmentContent);
        });
    }

    if (toggleListAppointmentBtn && listAppointmentContent) {
        toggleListAppointmentBtn.addEventListener('click', function () {
            loadUpcomingAppointments();
            toggleContent(toggleListAppointmentBtn, listAppointmentContent);
        });
    }

    if (toggleFinishedAppointmentsBtn && finishedAppointmentsContent) {
        toggleFinishedAppointmentsBtn.addEventListener('click', function () {
            loadFinishedAppointments();
            toggleContent(toggleFinishedAppointmentsBtn, finishedAppointmentsContent);
        });
    }

    if (toggleCanceledAppointmentsBtn && canceledAppointmentsContent) {
        toggleCanceledAppointmentsBtn.addEventListener('click', function () {
            loadCanceledAppointments();
            toggleContent(toggleCanceledAppointmentsBtn, canceledAppointmentsContent);
        });
    }




   const searchForm = document.getElementById('edit-barbershop-info-form');
    const searchResultsContainer = document.getElementById('search-results');
    const searchResultTemplate = document.getElementById('search-result-template').content;

    // Function to render search results
    function displaySearchResults(results) {
        searchResultsContainer.innerHTML = '';  // Clear any previous results
        results.forEach(result => {
            // Clone the template
            const resultClone = searchResultTemplate.cloneNode(true);
            resultClone.querySelector('.barbershop-info').textContent = result.barbershop_name;
            resultClone.querySelector('.search-result-item').dataset.id = result.barbershop_id;

            // Update the form fields with the barbershop data
            const form = resultClone.querySelector('form');
            form.querySelector('input[name="edit-barbershop-name"]').value = result.barbershop_name;
            form.querySelector('input[name="edit-barbershop-location"]').value = result.address;
            form.querySelector('input[name="edit-barbershop-phone-number"]').value = result.barbershop_phone_number;
            form.querySelector('input[name="barbershop_id"]').value = result.barbershop_id;

            searchResultsContainer.appendChild(resultClone);
        });
        searchResultsContainer.style.display = 'block';  // Show the results container
    }

    // Add event listener to the form submission
    searchForm.addEventListener('submit', function (event) {
        event.preventDefault();  // Prevent the default form submission

        const formData = new FormData(searchForm);
        const searchQuery = formData.get('barbershop-name');

        // Send an AJAX request to search for barbershops
        fetch('/find-barbershop', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data);  // Render the search results
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Functionality for '+' and '-' button in each search result
    searchResultsContainer.addEventListener('click', function (event) {
        if (event.target.closest('.toggle-search-result-btn')) {
            const button = event.target.closest('.toggle-search-result-btn');
            const content = button.closest('.search-result-item').querySelector('.search-result-content');

            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                button.querySelector('i').className = 'fas fa-minus';
            } else {
                content.style.display = 'none';
                button.querySelector('i').className = 'fas fa-plus';
            }
        }
    });

    var barbershopSelect = document.getElementById('select-barbershop-to-edit-barber');
    barbershopSelect.addEventListener('change', function() {
        var selectedBarbershopId = barbershopSelect.value;

    // Update the hidden input for the selected barbershop
        document.getElementById('barbershop-id-edit').value = selectedBarbershopId;

        // Make an AJAX request to fetch barbers for the selected barbershop
        fetch('/get-barbers/' + selectedBarbershopId)
    .then(response => response.json())
    .then(data => {
        const barberSelect = document.getElementById('select-barber-to-edit');
        barberSelect.innerHTML = '<option value="" disabled selected>Select a barber</option>'; // Clear previous options

        data.forEach(barber => {
            // Populate barber options
            const option = document.createElement('option');
            option.value = barber.barber_id; // Set barber ID as value
            option.textContent = barber.barber_first_name + ' ' + barber.barber_last_name; // Full name
            barberSelect.appendChild(option);
        });
    })
    .catch(error => console.error('Error:', error));

    });

    document.getElementById('select-barber-to-edit').addEventListener('change', function () {
        const barberId = this.value;
        const barbershopId = document.getElementById("select-barbershop-to-edit-barber").value;

        if (barberId) {
         document.getElementById('barber-id').value = barberId;
            fetch(`/get-barber-details/${barbershopId}/${barberId}`)
                .then(response => response.json())
                .then(barber => {
                    // Populate input fields
                    document.getElementById('edit-barber-first-name').value = barber.barber_first_name;
                    document.getElementById('edit-barber-last-name').value = barber.barber_last_name;
                    document.getElementById('edit-barber-phone-number').value = barber.barber_phone_number;
                    document.getElementById('edit-barber-email').value = barber.barber_email;
                    document.getElementById('edit-barber-experienced-years').value = barber.experienced_years;
                    document.getElementById('edit-barber-working-start-time').value = barber.working_start_time;
                    document.getElementById('edit-barber-working-end-time').value = barber.working_end_time;
                    document.getElementById('edit-barber-break-start-time').value = barber.break_start_time;
                    document.getElementById('edit-barber-break-end-time').value = barber.break_end_time;

                    // Auto-check working days
                    const workingDays = barber.working_days.split(', ');
                    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].forEach(day => {
                    const checkbox = document.getElementById(day.toLowerCase() + '_edit');
                    checkbox.checked = workingDays.includes(day);
                });
            });
        }
    });



    const barbershopSelectDelete = document.getElementById('select-barbershop-to-delete-barber');
    const barberSelectDelete = document.getElementById('select-barber-to-delete');
    const deleteButton = document.getElementById('delete-barber-btn');


    deleteButton.disabled = true;
    function updateDeleteButtonState() {
        const selectedBarbershopId = barbershopSelectDelete.value;
        const selectedBarberId = barberSelectDelete.value;
        if (selectedBarbershopId && selectedBarberId) {
            deleteButton.disabled = false;
            deleteButton.style.backgroundColor = 'red';
            deleteButton.style.cursor = 'pointer';
        } else {
            deleteButton.disabled = true;
            deleteButton.style.backgroundColor = 'grey';
            deleteButton.style.cursor = 'not-allowed';
        }
    }

    document.getElementById('select-barbershop-to-delete-barber').addEventListener('change', function() {
    const selectedBarbershopId = this.value;

    document.getElementById('barbershop-id-delete').value = selectedBarbershopId;

    fetch(`/get-barbers/${selectedBarbershopId}`)
        .then(response => response.json())
        .then(barbers => {
            const barberSelect = document.getElementById('select-barber-to-delete');
            barberSelect.innerHTML = '<option value="" disabled selected>Select a barber</option>'; // Reset barber dropdown

            barbers.forEach(barber => {
                const option = document.createElement('option');
                option.value = barber.barber_id;
                option.textContent = `${barber.barber_first_name} ${barber.barber_last_name}`;
                barberSelect.appendChild(option);
            });
             updateDeleteButtonState();
        })
        .catch(error => {
            console.error('Error fetching barbers:', error);
        });
    });

    document.getElementById('select-barber-to-delete').addEventListener('change', function () {
        const selectedBarberId = this.value;
        document.getElementById('barber-id-delete').value = selectedBarberId;
         updateDeleteButtonState();
    });


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

     document.addEventListener('click', function (event) {
     if (event.target.closest('.toggle-delete-search-result-btn')) {
            const button = event.target.closest('.toggle-delete-search-result-btn');
            const content = button.closest('.delete-search-results').querySelector('.delete-search-result-content');
            toggleContent(button, content);
        }
     });






    document.getElementById('select-barbershop-to-add-appointment').addEventListener('change', function() {
    const selectedBarbershopId = this.value;
    document.getElementById('barbershop-id-add-appointment').value = selectedBarbershopId;

    fetch(`/get-barbers/${selectedBarbershopId}`)
        .then(response => response.json())
        .then(barbers => {
            const barberSelect = document.getElementById('select-barber-to-add-appointment');
            barberSelect.innerHTML = '<option value="" disabled selected>Select a barber</option>'; // Reset barber dropdown

            barbers.forEach(barber => {
                const option = document.createElement('option');
                option.value = barber.barber_id;
                option.textContent = `${barber.barber_first_name} ${barber.barber_last_name}`;
                barberSelect.appendChild(option);
            });

        })
        .catch(error => {
            console.error('Error fetching barbers:', error);
        });
    });

    // When a barber is selected, fetch the available haircuts
document.getElementById('select-barber-to-add-appointment').addEventListener('change', function () {
    const selectedBarberId = this.value;
    document.getElementById('barber-id-add-appointment').value = selectedBarberId;

    // Fetch available haircuts for the selected barber
    fetch(`/get-all-haircuts/${selectedBarberId}`)
        .then(response => response.json())
        .then(haircuts => {
            const haircutSelect = document.getElementById('haircut-select');
            haircutSelect.innerHTML = '<option value="" disabled selected>Select a haircut</option>'; // Reset haircut dropdown

            haircuts.forEach(haircut => {
                const option = document.createElement('option');
                option.value = haircut.haircut_id; // Store the haircut_id in the option value
                option.textContent = `${haircut.haircut_name} - ${haircut.price} UZS`;
                haircutSelect.appendChild(option);
            });

            // Add an event listener for when a haircut is selected
            haircutSelect.addEventListener('change', function() {
                const selectedHaircutId = this.value; // Get the haircut_id from the selected option
                document.getElementById('haircut-id-add-appointment').value = selectedHaircutId; // Set the hidden input field to haircut_id
            });
        })
        .catch(error => {
            console.error('Error fetching haircuts:', error);
        });
    });



    document.getElementById('appointment-day').addEventListener('change', function() {
    const barberId = document.getElementById('barber-id-add-appointment').value;
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


    function loadUpcomingAppointments() {
    fetch(listUpcomingAppointments)
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
                     <form class="delete-appointments-container" method="post" action="/cancel-appointment">
                        <input type="hidden" name="appointment_id" value="${appointment.appointment_id}">
                        <button type="submit" class="delete-appointment-button">Cancel appointment</button>
                        <p>Important: Please ensure you contact the customer prior to deleting this appointment. Note
                            that
                            deleting an appointment will automatically result in its cancellation.</p>
                    </form>
                `;
                appointmentsList.appendChild(appointmentItem);
            });
        })
        .catch(error => console.error('Error loading appointments:', error));
    }


    function loadFinishedAppointments() {
    fetch(listFinishedAppointments)
        .then(response => response.json())
        .then(data => {
            const appointmentsList = document.getElementById('finished-appointments-list');
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
                        <p>Important: Deleting this appointment will result in its permanent removal from the system.</p>
                    </form>
                `;
                appointmentsList.appendChild(appointmentItem);
            });
        })
        .catch(error => console.error('Error loading appointments:', error));
    }

    function loadCanceledAppointments() {
    fetch(listCanceledAppointments)
        .then(response => response.json())
        .then(data => {
            const appointmentsList = document.getElementById('canceled-appointments-list');
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
                        <p class="price">Price: ${appointment.price} sum</p>
                        <p class="created-date">Created date: ${appointment.created_date}</p>
                    </div>
                     <form class="delete-appointments-container" method="post" action="/delete-appointment">
                        <input type="hidden" name="appointment_id" value="${appointment.appointment_id}">
                        <button type="submit" class="delete-appointment-button">Delete appointment</button>
                        <p>Important: Deleting this appointment will result in its permanent removal from the system.</p>
                    </form>
                `;
                appointmentsList.appendChild(appointmentItem);
            });
        })
        .catch(error => console.error('Error loading appointments:', error));
    }


});