document.addEventListener('DOMContentLoaded', function () {
    const toggleCardBtn = document.getElementById('toggle-card-btn');
    const toggleCardEditBtn = document.getElementById('toggle-card-edit-btn');

    const cardContent = document.getElementById('card-content');
    const editCardContent = document.getElementById('edit-card-content');

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


//    if (toggleEditBarbershopSettingsBtn && editSettingsContent) {
//        toggleEditBarbershopSettingsBtn.addEventListener('click', function () {
//            toggleContent(toggleEditBarbershopSettingsBtn, editSettingsContent);
//        });
//    }

    // Form submission handling
    const form = document.getElementById('edit-barbershop-info-form');
    if (form) {
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
                  if (data.results_html.trim() !== '<div class="search-result-item">No barbershops found</div>') {
                  searchResultsDiv.style.display = 'block';
                } else {
                    searchResultsDiv.style.display = 'block';
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

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
    });
});
