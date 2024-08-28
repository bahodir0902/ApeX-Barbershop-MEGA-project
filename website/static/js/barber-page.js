document.addEventListener('DOMContentLoaded', function () {

    const cardContent = document.getElementById('add-haircut-card-content');
    const toggleCardBtn = document.getElementById('add-haircut-toggle-card-btn');
    const editCardContent = document.getElementById('edit-haircut-card-content');
    const toggleEditCardBtn = document.getElementById('edit-haircut-toggle-card-btn');
    const deleteCardContent = document.getElementById('delete-haircut-card-content');
    const toggleDeleteCardBtn = document.getElementById('delete-haircut-toggle-card-btn');
    const UpcomingAppToggleBtn = document.getElementById('upcoming-appointments-toggle-card-btn');
    const UpcomingAppCardContent = document.getElementById('upcoming-appointments-content');
    const FinishedAppToggleBtn = document.getElementById('finished-haircuts-toggle-card-btn');
    const FinishedAppCardContent = document.getElementById('finished-haircuts-content');
    const CanceledAppToggleBtn = document.getElementById('canceled-appointments-toggle-card-btn');
    const CanceledAppCardContent = document.getElementById('canceled-appointments-content');
    const ManageScheduleToggleBtn = document.getElementById('schedule-toggle-card-btn');
    const ManageScheduleCardContent = document.getElementById('schedule-content');
    const StatisticsRevenueToggleBtn = document.getElementById('my-statistics-revenue-toggle-card-btn');
    const StatisticsRevenueCardContent = document.getElementById('my-statistics-revenue-content');
    const StatisticsTotalToggleBtn = document.getElementById('my-statistics-total-toggle-card-btn');
    const StatisticsTotalCardContent = document.getElementById('my-statistics-total-content');
    const StatisticsFeedbackToggleBtn = document.getElementById('my-statistics-feedback-toggle-card-btn');
    const StatisticsFeedbackCardContent = document.getElementById('my-statistics-feedback-content');

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

    if (UpcomingAppToggleBtn && UpcomingAppCardContent) {
            UpcomingAppToggleBtn.addEventListener('click', function () {
                toggleContent(UpcomingAppToggleBtn, UpcomingAppCardContent);
            });
        }

    if (FinishedAppToggleBtn && FinishedAppCardContent) {
            FinishedAppToggleBtn.addEventListener('click', function () {
                toggleContent(FinishedAppToggleBtn, FinishedAppCardContent);
            });
        }

    if (CanceledAppToggleBtn && CanceledAppCardContent) {
            CanceledAppToggleBtn.addEventListener('click', function () {
                toggleContent(CanceledAppToggleBtn, CanceledAppCardContent);
            });
        }

    if (ManageScheduleToggleBtn && ManageScheduleCardContent) {
            ManageScheduleToggleBtn.addEventListener('click', function () {
                toggleContent(ManageScheduleToggleBtn, ManageScheduleCardContent);
            });
        }

    if (StatisticsRevenueToggleBtn && StatisticsRevenueCardContent) {
            StatisticsRevenueToggleBtn.addEventListener('click', function () {
                toggleContent(StatisticsRevenueToggleBtn, StatisticsRevenueCardContent);
            });
        }

    if (StatisticsTotalToggleBtn && StatisticsTotalCardContent) {
            StatisticsTotalToggleBtn.addEventListener('click', function () {
                toggleContent(StatisticsTotalToggleBtn, StatisticsTotalCardContent);
            });
        }

    if (StatisticsFeedbackToggleBtn && StatisticsFeedbackCardContent) {
            StatisticsFeedbackToggleBtn.addEventListener('click', function () {
                toggleContent(StatisticsFeedbackToggleBtn, StatisticsFeedbackCardContent);
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