document.addEventListener('DOMContentLoaded', function() {
    const showMoreButton = document.querySelector('.show-more');
    const backToPreviousButton = document.querySelector('.back-to-previous');
    const barbershopCards = document.querySelectorAll('.barbershop');
    const paginationElement = document.querySelector('.pagination');
    const cardsPerPage = 6;
    let currentPage = 1;

    // Hide 'Back' button initially
    backToPreviousButton.style.display = 'none';

    // Show only the first set of barbershop cards
    const updateCardsDisplay = (page) => {
        barbershopCards.forEach((card, index) => {
            if (index >= (page - 1) * cardsPerPage && index < page * cardsPerPage) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    };

    const updatePaginationText = (page) => {
        const totalPages = Math.ceil(barbershopCards.length / cardsPerPage);
        paginationElement.textContent = `${page}/${totalPages}`;
    };

    // Initial display setup
    updateCardsDisplay(currentPage);
    updatePaginationText(currentPage);

    // Hide 'Show More' button if there are no more pages
    const totalPages = Math.ceil(barbershopCards.length / cardsPerPage);
    if (totalPages <= 1) {
        showMoreButton.style.display = 'none';
    }

    // Logic to show more barbershops on button click
    showMoreButton.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default behavior
        currentPage++;

        updateCardsDisplay(currentPage);
        updatePaginationText(currentPage);

        // Show 'Back' button after clicking 'Show More'
        backToPreviousButton.style.display = 'flex';

        // Hide 'Show More' button if on the last page
        if (currentPage === totalPages) {
            showMoreButton.style.display = 'none';
        }
    });

    // Logic to go back to the previous page
    backToPreviousButton.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default behavior
        currentPage--;

        updateCardsDisplay(currentPage);
        updatePaginationText(currentPage);

        // Hide 'Back' button if returning to the first page
        if (currentPage === 1) {
            backToPreviousButton.style.display = 'none';
        }

        // Show 'Show More' button if not on the last page
        if (currentPage < totalPages) {
            showMoreButton.style.display = 'flex';
        }
    });
});
