document.addEventListener('DOMContentLoaded', function() {
    const bookNowButton = document.getElementById('book-now'); // Make sure to declare it with 'const'

    bookNowButton.addEventListener('click', function() {
        window.location.href = '/'; // Ah, the sweet smell of home!
    });
});
