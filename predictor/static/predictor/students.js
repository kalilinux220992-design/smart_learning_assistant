/* # students.js */

// Sidebar toggle functionality
const toggleBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');

toggleBtn?.addEventListener('click', () => {
    sidebar.classList.toggle('open');
});

// Add Student button
const addStudentBtn = document.getElementById('addStudentBtn');
addStudentBtn?.addEventListener('click', () => {
    alert('Add Student form would open here');
});

// Search functionality for students
const searchInput = document.getElementById('searchStudents');
const tableRows = document.querySelectorAll('.students-table tbody tr');

searchInput?.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    
    tableRows.forEach(row => {
        const name = row.cells[0].textContent.toLowerCase();
        
        if (name.includes(query)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

