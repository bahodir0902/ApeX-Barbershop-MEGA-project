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
            console.log('Rating:', rating);
            console.log('Feedback:', feedback);

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

            // Here you would typically send a delete request to your server
            // For demonstration, we'll just reset the form
            resetForm(form);

            // Replace delete button with submit button
            const submitButton = document.createElement('button');
            submitButton.type = 'submit';
            submitButton.className = 'feedback-button';
            submitButton.textContent = 'Submit';
            this.parentNode.replaceChild(submitButton, this);

            // Re-enable form inputs
            form.querySelectorAll('input, textarea').forEach(input => input.disabled = false);
        });
    });
});
