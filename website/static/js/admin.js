document.addEventListener('DOMContentLoaded', function () {
    const toggleCardBtn = document.getElementById('toggle-card-btn');
    const toggleCardEditBtn = document.getElementById('toggle-card-edit-btn');
    const toggleEditSettingsBtn = document.getElementById('toggle-edit-settings-btn');
    const cardContent = document.getElementById('card-content');
    const editCardContent = document.getElementById('edit-card-content');
    const editSettingsContent = document.getElementById('edit-settings-content');

    // Function to toggle display and icon
    function toggleContent(button, content) {
        if (content.style.display === 'none' || content.style.display === '') {
            content.style.display = 'block';
            button.innerHTML = '<i class="fas fa-minus"></i>';
        } else {
            content.style.display = 'none';
            button.innerHTML = '<i class="fas fa-plus"></i>';
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

    if (toggleEditSettingsBtn && editSettingsContent) {
        toggleEditSettingsBtn.addEventListener('click', function () {
            toggleContent(toggleEditSettingsBtn, editSettingsContent);
        });
    }

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
    });
});
