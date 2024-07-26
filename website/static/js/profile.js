document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.getElementById('profile-form');
    const saveChangesButton = document.getElementById('save-changes-button');
    const initialProfileValues = {};

    document.getElementById('back-button').addEventListener('click', function() {
        window.history.back();
    });

    function setInitialValues() {
        ['edit_first_name', 'edit_last_name', 'edit_email', 'edit_phone_number', 'privacy'].forEach(id => {
            initialProfileValues[id] = document.getElementById(id).value;
        });
        initialProfileValues['profile_picture'] = ''; // Reset file input initial value
    }

    setInitialValues();

    const fileInput = document.getElementById('profile_picture');
    const removeFileButton = document.getElementById('remove-file-button');

    function checkChanges() {
        let hasChanged = false;

        for (const id in initialProfileValues) {
            if (initialProfileValues[id] !== document.getElementById(id).value) {
                hasChanged = true;
                break;
            }
        }

        if (fileInput.files.length > 0) {
            hasChanged = true;
        }

        saveChangesButton.disabled = !hasChanged;
        saveChangesButton.style.backgroundColor = hasChanged ? '' : 'gray';
    }

    ['edit_first_name', 'edit_last_name', 'edit_email', 'edit_phone_number', 'privacy'].forEach(id => {
        document.getElementById(id).addEventListener('input', checkChanges);
    });

    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            removeFileButton.style.display = 'inline';
        } else {
            removeFileButton.style.display = 'none';
        }
        checkChanges();
    });

    removeFileButton.addEventListener('click', function() {
        fileInput.value = '';
        this.style.display = 'none';
        checkChanges();
    });

    document.getElementById('edit-profile-button').addEventListener('click', function() {
        var editSection = document.getElementById('edit-profile-section');
        var BackButton = document.getElementById('back-button');
        editSection.style.display = 'block';
        this.style.display = 'none';
        BackButton.style.display = 'none';
        checkChanges();
    });



    document.getElementById('cancel-edit-button').addEventListener('click', function() {
        var editSection = document.getElementById('edit-profile-section');
        editSection.style.display = 'none';
        document.getElementById('edit-profile-button').style.display = 'block';
        profileForm.reset();
        fileInput.value = '';
        removeFileButton.style.display = 'none';
        saveChangesButton.disabled = true;
        saveChangesButton.style.backgroundColor = 'gray';
        setInitialValues();

        location.reload();
    });

    document.getElementById('change-password-button').addEventListener('click', function() {
        var changePasswordSection = document.getElementById('change-password-section');
        changePasswordSection.style.display = 'block';
    });

    document.getElementById('cancel-change-password-button').addEventListener('click', function() {
        var changePasswordSection = document.getElementById('change-password-section');
        changePasswordSection.style.display = 'none';
        document.getElementById('change-password-form').reset();
    });

    document.getElementById('update-password-button').addEventListener('click', function() {
        var form = document.getElementById('change-password-form');
        var formData = new FormData(form);

        fetch(changePasswordUrl, { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            var messagesDiv = document.getElementById('password-change-messages');
            var successMessagesDiv = document.getElementById('success-change-messages');
            var changePasswordSection = document.getElementById('change-password-section');

            messagesDiv.innerHTML = '';
            successMessagesDiv.innerHTML = '';

            if (data.success) {
                form.reset();
                successMessagesDiv.innerHTML = '<p style="color: green;">' + data.message + '</p>';
                changePasswordSection.style.display = 'none';
                 saveChangesButton.disabled = false;
                saveChangesButton.style.backgroundColor = '';


            } else {
                data.errors.forEach(error => {
                    messagesDiv.innerHTML += '<p style="color: red;">' + error + '</p>';
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    profileForm.addEventListener('submit', function(event) {
        event.preventDefault();

        var formData = new FormData(profileForm);

        fetch(EditProfileUrl, { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            console.log('Response Data:', data);
            if (data.message == 'No changes were made.') {
                location.reload();
            } else if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert(data.errors.join('\n'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

     const deleteButton = document.getElementById('delete-account-button');
        const confirmationModal = document.getElementById('confirmation-modal');
        const confirmDeleteButton = document.getElementById('confirm-delete');
        const cancelDeleteButton = document.getElementById('cancel-delete');
        const confirmationMessage = document.getElementById('confirmation-message');

        // Show the modal when delete button is clicked
        deleteButton.addEventListener('click', function() {
            confirmationModal.style.display = 'block';
        });

        // Hide the modal and proceed with deletion when confirmed
        confirmDeleteButton.addEventListener('click', function() {
            confirmationModal.style.display = 'none';

            fetch(DeleteAccountUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    confirmationMessage.innerHTML = "Account successfully deleted. Redirecting...";
                    confirmationMessage.style.color = "green";
                    setTimeout(() => {
                        window.location.href = '/'; // Redirect to the homepage
                    }, 1000); // Redirect after 2 seconds
                } else {
                    confirmationMessage.innerHTML = "An error occurred: " + data.message;
                    confirmationMessage.style.color = "red";
                }
            })
            .catch(error => {
                console.error("Error:", error);
                confirmationMessage.innerHTML = "An error occurred while deleting the account.";
                confirmationMessage.style.color = "red";
            });
        });

        // Hide the modal when canceled
        cancelDeleteButton.addEventListener('click', function() {
            confirmationModal.style.display = 'none';
        });

        // Hide the modal when clicking outside of it
        window.addEventListener('click', function(event) {
            if (event.target === confirmationModal) {
                confirmationModal.style.display = 'none';
            }
        });


//function getCSRFToken() {
    // This function should return the CSRF token if you are using one
    // For example, if using Flask-WTF, you can include it in your HTML like this:
    // <meta name="csrf-token" content="{{ csrf_token() }}">
 //   return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
//}


    checkChanges();
});
