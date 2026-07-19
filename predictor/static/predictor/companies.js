/* # companies.js */

// Sidebar toggle functionality
const toggleBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');

toggleBtn?.addEventListener('click', () => {
    sidebar.classList.toggle('open');
});

// Companies data
const companiesData = [
    {
        name: 'Infosys',
        sector: 'IT Services',
        requiredSkills: ['Java', 'SQL', 'Git'],
        eligibleBranches: ['CSE', 'IT', 'ECE', 'Mech', 'Civil', 'All'],
        minCGPA: 6.0,
        hired2024: 0,
        avgPackage: '6.5 LPA'
    },
    {
        name: 'TCS',
        sector: 'IT Services',
        requiredSkills: ['C++', 'Python', 'SQL'],
        eligibleBranches: ['CSE', 'IT', 'ECE'],
        minCGPA: 6.5,
        hired2024: 9,
        avgPackage: '7.0 LPA'
    },
    {
        name: 'Cognizant',
        sector: 'IT Services',
        requiredSkills: ['Java', 'JavaScript', 'REST APIs'],
        eligibleBranches: ['CSE', 'IT', 'ECE', 'Mech'],
        minCGPA: 6.2,
        hired2024: 0,
        avgPackage: '8.5 LPA'
    },
    {
        name: 'Wipro',
        sector: 'IT Services',
        requiredSkills: ['Python', 'SQL', 'Docker'],
        eligibleBranches: ['CSE', 'IT', 'ECE'],
        minCGPA: 5.8,
        hired2024: 0,
        avgPackage: '6.5 LPA'
    },
    {
        name: 'Tech Mahindra',
        sector: 'IT Services',
        requiredSkills: ['Java', 'Git', 'System Design'],
        eligibleBranches: ['CSE', 'IT', 'Mech'],
        minCGPA: 6.0,
        hired2024: 2,
        avgPackage: '8.0 LPA'
    },
    {
        name: 'HCL Technologies',
        sector: 'IT Services',
        requiredSkills: ['C++', 'JavaScript', 'React'],
        eligibleBranches: ['CSE', 'IT', 'ECE'],
        minCGPA: 6.3,
        hired2024: 0,
        avgPackage: '7.2 LPA'
    },
    {
        name: 'Accenture',
        sector: 'Consulting',
        requiredSkills: ['Python', 'Machine Learning', 'SQL'],
        eligibleBranches: ['CSE', 'IT', 'ECE', 'All'],
        minCGPA: 7.0,
        hired2024: 0,
        avgPackage: '9.0 LPA'
    },
    {
        name: 'Capgemini',
        sector: 'IT Services',
        requiredSkills: ['Java', 'Node.js', 'AWS'],
        eligibleBranches: ['CSE', 'IT', 'ECE'],
        minCGPA: 6.5,
        hired2024: 0,
        avgPackage: '7.8 LPA'
    },
    {
        name: 'Global Quest',
        sector: 'IT Services',
        requiredSkills: ['Java', 'Node.js', 'AWS'],
        eligibleBranches: ['CSE', 'IT', 'ECE'],
        minCGPA: 6.8,
        hired2024: 1,
        avgPackage: '3.0 LPA'
    },
    {
        name: 'Nsight Inc.',
        sector: 'IT Services',
        requiredSkills: ['Java', 'Node.js', 'AWS'],
        eligibleBranches: ['CSE', 'IT', 'ECE'],
        minCGPA: 7.0,
        hired2024: 5,
        avgPackage: '3.6 LPA'
    },
    {
        name: 'Knocial India Limited',
        sector: 'IT Services',
        requiredSkills: ['Java', 'Node.js', 'AWS'],
        eligibleBranches: ['CSE', 'IT', 'ECE'],
        minCGPA: 7.0,
        hired2024: 9,
        avgPackage: '5 LPA'
    },
    {
        name: 'Teachnook Edutech',
        sector: 'IT Services',
        requiredSkills: ['Java', 'Node.js', 'AWS'],
        eligibleBranches: ['CSE', 'IT', 'ECE'],
        minCGPA: 7.0,
        hired2024: 2,
        avgPackage: '5 LPA'
    }
];

// Render company cards
function renderCompanies(companies) {
    const grid = document.getElementById('companiesGrid');
    grid.innerHTML = '';

    if (companies.length === 0) {
        grid.innerHTML = '<div class="no-results">No companies found matching your search.</div>';
        return;
    }

    companies.forEach(company => {
        const skillBadges = company.requiredSkills
            .map(skill => `<span class="skill-badge">${skill}</span>`)
            .join('');
        
        const branchesText = company.eligibleBranches.join(', ');

        const card = `
            <div class="company-card">
                <div class="company-header">
                    <div>
                        <h3>${company.name}</h3>
                        <p class="sector">${company.sector}</p>
                    </div>
                    <div class="package-badge">${company.avgPackage}</div>
                </div>

                <div class="company-section">
                    <h4>Required Skills</h4>
                    <div class="skills-container">
                        ${skillBadges}
                    </div>
                </div>

                <div class="company-section">
                    <h4>Eligible Branches</h4>
                    <p>${branchesText}</p>
                </div>

                <div class="company-footer">
                    <div class="footer-item">
                        <label>Min CGPA</label>
                        <p>${company.minCGPA}</p>
                    </div>
                    <div class="footer-item">
                        <label>Hired</label>
                        <p>${company.hired2024} students</p>
                    </div>
                </div>
            </div>
        `;

        grid.innerHTML += card;
    });
}

// Search functionality
const searchInput = document.getElementById('searchCompanies');
searchInput?.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = companiesData.filter(company => 
        company.name.toLowerCase().includes(query) ||
        company.sector.toLowerCase().includes(query) ||
        company.requiredSkills.some(skill => skill.toLowerCase().includes(query))
    );
    renderCompanies(filtered);
});

// Initial render
renderCompanies(companiesData);
