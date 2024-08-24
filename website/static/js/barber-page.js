document.addEventListener('DOMContentLoaded', function () {

    const cardContent = document.getElementById('add-haircut-card-content');
    const toggleCardBtn = document.getElementById('add-haircut-toggle-card-btn');
    const editCardContent = document.getElementById('edit-haircut-card-content');
    const toggleEditCardBtn = document.getElementById('edit-haircut-toggle-card-btn');
    const deleteCardContent = document.getElementById('delete-haircut-card-content');
    const toggleDeleteCardBtn = document.getElementById('delete-haircut-toggle-card-btn');

    function toggleContent(button, content) {
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                button.querySelector('i').className = 'fas fa-minus';
            } else {
                content.style.display = 'none';
                button.querySelector('i').className = 'fas fa-plus';
            }
        }

    if (toggleCardBtn && cardContent) {
            toggleCardBtn.addEventListener('click', function () {
                toggleContent(toggleCardBtn, cardContent);
            });
        }

    if (toggleEditCardBtn && editCardContent) {
            toggleEditCardBtn.addEventListener('click', function () {
                toggleContent(toggleEditCardBtn, editCardContent);
            });
        }

    if (toggleDeleteCardBtn && deleteCardContent) {
            toggleDeleteCardBtn.addEventListener('click', function () {
                toggleContent(toggleDeleteCardBtn, deleteCardContent);
            });
        }

    const selectHaircut = document.getElementById('select-haircut');
    const editNameInput = document.getElementById('edit-name');
    const editPriceInput = document.getElementById('edit-haircut-price');
    const editDescriptionInput = document.getElementById('edit-haircut-description');
   // const haircutIdHidden = document.getElementById('haircut_id_hidden');

    if (selectHaircut) {
        selectHaircut.addEventListener('change', function () {
            const selectedOption = selectHaircut.options[selectHaircut.selectedIndex];

            // Populate the form fields with selected haircut's data
            editNameInput.value = selectedOption.getAttribute('data-name');
            editPriceInput.value = selectedOption.getAttribute('data-price');
            editDescriptionInput.value = selectedOption.getAttribute('data-description');
          //  haircutIdHidden.value = selectedOption.getAttribute('data-description');
        });
    }

    const selectHaircutToDelete = document.getElementById('select-haircut-to-delete');
    const deleteButton = document.getElementById('delete-haircut-btn');

        selectHaircutToDelete.addEventListener('change', function () {
            if (selectHaircutToDelete.value) {
                deleteButton.disabled = false;
                deleteButton.style.backgroundColor = 'red'; // Reset to default color
                deleteButton.style.cursor = 'pointer';   // Reset cursor to pointer
            } else {
                deleteButton.disabled = true;
                deleteButton.style.backgroundColor = 'grey'; // Grey out the button
                deleteButton.style.cursor = 'not-allowed';   // Change cursor to not-allowed
            }
        });

});