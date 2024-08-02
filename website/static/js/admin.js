document.addEventListener('DOMContentLoaded', function () {
    const toggleCardBtn = document.getElementById('toggle-card-btn');
    const toggleCardEditBtn = document.getElementById('toggle-card-edit-btn');
    const cardContent = document.getElementById('card-content');
    const editCardContent = document.getElementById('edit-card-content');

    toggleCardBtn.addEventListener('click', function () {
        if (cardContent.style.display === 'none' || cardContent.style.display === '') {
            cardContent.style.display = 'block';
            toggleCardBtn.innerHTML = '<i class="fas fa-minus"></i>';
        } else {
            cardContent.style.display = 'none';
            toggleCardBtn.innerHTML = '<i class="fas fa-plus"></i>';
        }
    });

    toggleCardEditBtn.addEventListener('click', function () {
        if (editCardContent.style.display === 'none' || editCardContent.style.display === '') {
            editCardContent.style.display = 'block';
            toggleCardEditBtn.innerHTML = '<i class="fas fa-minus"></i>';
        } else {
            editCardContent.style.display = 'none';
            toggleCardEditBtn.innerHTML = '<i class="fas fa-plus"></i>';
        }
    });

   /* const form = document.getElementById('edit-barbershop-info-form');
    const searchResults = document.getElementById('search-results');

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = new FormData(form);
        const xhr = new XMLHttpRequest();
        xhr.open('POST', form.action, true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        xhr.onload = function () {
             if (xhr.status === 200) {
               searchResults.innerHTML = xhr.responseText;
            } else {
                searchResults.innerHTML = 'Error occurred. Please try again.';
            }
        };
        xhr.send(formData);
    });*/
     const form = document.getElementById('edit-barbershop-info-form');

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
        })
        .catch(error => console.error('Error:', error));
    });

});
