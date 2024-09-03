document.addEventListener('DOMContentLoaded', function() {
    var dropdown = document.querySelector('.dropdown');

    dropdown.addEventListener('click', function() {
        this.classList.toggle('active');
    });

    // Optional: Close the dropdown if the user clicks outside of it
    window.addEventListener('click', function(event) {
        if (!dropdown.contains(event.target)) {
            dropdown.classList.remove('active');
        }
    });


});

