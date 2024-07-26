document.addEventListener('DOMContentLoaded', function() {
    const showMoreButton = document.querySelector('.show-more');
    const backToPreviousButton = document.querySelector('.back-to-previous');
    const cardContainer = document.querySelector('.frame-parent');
    const paginationElement = document.querySelector('.pagination');
    const cards = document.querySelectorAll('.barbershop'); // Correct class selector
    const cardsPerPage = 6;
    let currentPage = 1;

    const updateCardsDisplay = (page) => {
        cards.forEach((card, index) => {
            if (index >= (page - 1) * cardsPerPage && index < page * cardsPerPage) {
                card.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
            }
        });
    };

    const updatePaginationText = (page) => {
        const totalPages = Math.ceil(cards.length / cardsPerPage);
        paginationElement.textContent = `${page}/${totalPages}`;
    };

    const checkButtonsVisibility = () => {
        const totalPages = Math.ceil(cards.length / cardsPerPage);
        if (totalPages <= 1) {
            showMoreButton.classList.add('hidden'); // Hide if only one page or less
            backToPreviousButton.classList.add('hidden'); // Hide the back button if only one page or less
        } else {
            showMoreButton.classList.toggle('hidden', currentPage === totalPages);
            backToPreviousButton.classList.toggle('hidden', currentPage === 1);
        }
    };

    // Initial display setup
    updateCardsDisplay(currentPage);
    updatePaginationText(currentPage);
    checkButtonsVisibility();

    showMoreButton.addEventListener('click', function(event) {
        event.preventDefault();
        currentPage++;
        updateCardsDisplay(currentPage);
        updatePaginationText(currentPage);
        checkButtonsVisibility();
    });

    backToPreviousButton.addEventListener('click', function(event) {
        event.preventDefault();
        currentPage--;
        updateCardsDisplay(currentPage);
        updatePaginationText(currentPage);
        checkButtonsVisibility();
    });
});
