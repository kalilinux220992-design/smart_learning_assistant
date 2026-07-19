/* # script.js */
const toggleBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');

toggleBtn?.addEventListener('click', () => {
    sidebar?.classList.toggle('open');
});

const placeData = {
    students: 29,
    placementRate: 25,
    avgPackage: '4 LPA',
    avgCgpa: 6.0,
    distribution: [2, 3, 3, 2],
    categories: ['6-7', '7-8', '8-9', '9+'],
    risk: [30, 40, 30],
    riskLabels: ['High', 'Medium', 'Low']
};

const cards = document.querySelectorAll('.card');
if (cards.length >= 4) {
    cards[0].innerHTML = 'Total Students<br><b>' + placeData.students + '</b>';
    cards[1].innerHTML = 'Placement Rate<br><b>' + placeData.placementRate + '%</b>';
    cards[2].innerHTML = 'Avg Package<br><b>' + placeData.avgPackage + '</b>';
    cards[3].innerHTML = 'Avg CGPA<br><b>' + placeData.avgCgpa + '</b>';
}

const barCtx = document.getElementById('barChart');
if (barCtx) {
    new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: ['< 6.0', '6.0 - 6.9', '7.0 - 7.9', '8.0 - 8.9', '9.0+'],
            datasets: [
                {
                    label: 'Students',
                    data: [1, 2, 5, 4, 2],
                    backgroundColor: '#3f51b5'
                },
                {
                    label: 'Placed',
                    data: [0, 1, 3, 3, 2],
                    backgroundColor: '#2e7d32'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'CGPA Distribution vs Placements',
                    font: {
                        size: 16,
                        weight: '600'
                    }
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    stacked: false
                },
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

const pieCtx = document.getElementById('pieChart');
if (pieCtx) {
    new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: placeData.riskLabels,
            datasets: [{
                data: placeData.risk,
                backgroundColor: ['#f44336', '#ffb300', '#4caf50']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}
