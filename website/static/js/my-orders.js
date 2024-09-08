document.addEventListener('DOMContentLoaded', function() {

      const backButton = document.getElementById('back-button');
    if (backButton) {
        backButton.addEventListener('click', function() {
            if (document.referrer && document.referrer !== window.location.href) {
                window.location.href = document.referrer; // Navigate to the previous unique page
            } else {
                window.location.href = '/'; // Fallback to the main page if no referrer or same page
            }
        });
    }

    function initializeStarRating(form) {
        const stars = form.querySelectorAll('.rating input');
        const selectedRating = form.querySelector('#selected_rating');

        stars.forEach(star => {
            star.addEventListener('change', function() {
                selectedRating.value = this.value;
                updateStarDisplay(form, this.value);
            });
        });
    }

    function updateStarDisplay(form, rating) {
        const labels = form.querySelectorAll('.rating label');
        labels.forEach(label => {
            const labelValue = label.getAttribute('for').split('-')[0].replace('star', '');
            if (labelValue <= rating) {
                label.classList.add('selected');
            } else {
                label.classList.remove('selected');
            }
        });
    }

    function initializeForm(form) {
        initializeStarRating(form);

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const rating = this.querySelector('#selected_rating').value;
            const feedback = this.querySelector('textarea[name="feedback"]').value;

            if (!rating) {
                alert('Please select a star rating before submitting.');
                return;
            }

            // Here you would typically send the data to your server
           // Send data using AJAX
            fetch('/leave-feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'rating': rating,
                    'feedback': feedback,
                    'barber_id': document.getElementById('barber-id').value,
                    'appointment_id': document.getElementById('appointment-id').value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/my-orders-get';
                } else {
                    alert('There was an error submitting your feedback. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error submitting your feedback. Please try again.');
            });

            // Simulating form submission
            alert('Thank you for your feedback!');
            resetForm(form);
        });
    }

    function resetForm(form) {
        form.reset();
        form.querySelector('#selected_rating').value = '';
        updateStarDisplay(form, 0);
    }

    // Initialize all forms on page load
    document.querySelectorAll('.feedback-form').forEach(initializeForm);

    // Handle feedback deletion
document.querySelectorAll('.delete-button').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const form = this.closest('.feedback-form');
        const appointmentId = form.querySelector('input[name="appointment_id"]').value;
        const barberId = form.querySelector('input[name="barber_id"]').value;

        if (confirm('Are you sure you want to delete this feedback?')) {
            fetch('/delete-feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'appointment_id': appointmentId,
                    'barber_id': barberId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect to '/my-orders-get' after successful deletion
                    window.location.href = '/my-orders-get';
                } else {
                    alert('There was an error deleting your feedback. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error deleting your feedback. Please try again.');
            });
        }
    });
});
});
