document.addEventListener('DOMContentLoaded', function() {
    // Handle edit button click
    document.querySelectorAll('.edit').forEach(button => {
        button.addEventListener('click', function() {
            const conferenceId = this.getAttribute('data-conference-id');
            window.location.href = `/edit_conference/${conferenceId}`;
        });
    });

    // Handle delete button click
    document.querySelectorAll('.delete').forEach(button => {
        button.addEventListener('click', function() {
            const conferenceId = this.getAttribute('data-conference-id');
            if (confirm('Are you sure you want to delete this conference?')) {
                fetch(`/delete_conference/${conferenceId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }).then(response => {
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        alert('Failed to delete conference.');
                    }
                });
            }
        });
    });
});