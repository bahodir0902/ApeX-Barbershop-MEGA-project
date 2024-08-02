document.addEventListener('DOMContentLoaded', function() {
    const showMoreButton = document.querySelector('.show-more');
    const backToPreviousButton = document.querySelector('.back-to-previous');
    const hoursButtons = document.querySelectorAll('.day');
    const cardsPerPage = 10;
    let currentPage = 1;

    const updateCardsDisplay = () => {
        const start = (currentPage - 1) * cardsPerPage;
        const end = start + cardsPerPage;

        hoursButtons.forEach((button, index) => {
            if (index >= start && index < end) {
                button.classList.remove('hidden');
            } else {
                button.classList.add('hidden');
            }
        });

        checkButtonsVisibility();
    };

    const checkButtonsVisibility = () => {
        const totalCards = hoursButtons.length;
        const totalPages = Math.ceil(totalCards / cardsPerPage);

        showMoreButton.classList.toggle('hidden', currentPage >= totalPages || totalCards <= cardsPerPage);
        backToPreviousButton.classList.toggle('hidden', currentPage === 1);
    };

    // Initial display setup
    updateCardsDisplay();

    showMoreButton.addEventListener('click', function(event) {
        event.preventDefault();
        currentPage++;
        updateCardsDisplay();
    });

    backToPreviousButton.addEventListener('click', function(event) {
        event.preventDefault();
        currentPage--;
        updateCardsDisplay();
    });
});
