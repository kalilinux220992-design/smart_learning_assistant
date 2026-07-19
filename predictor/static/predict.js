// Placement Prediction Handler

document.addEventListener('DOMContentLoaded', function() {
    const predictionForm = document.getElementById('predictionForm');
    
    if (predictionForm) {
        predictionForm.addEventListener('submit', handlePrediction);
    }
});

function handlePrediction(event) {
    event.preventDefault();

    // Get form values
    const formData = {
        iq: parseFloat(document.getElementById('iq').value),
        prev_sem_result: parseFloat(document.getElementById('prev_sem').value),
        cgpa: parseFloat(document.getElementById('cgpa').value),
        academic_performance: parseFloat(document.getElementById('academic').value),
        internship_experience: document.getElementById('internship').value === 'yes' ? 1 : 0,
        extra_curricular_score: parseFloat(document.getElementById('extracurricular').value),
        communication_skills: parseFloat(document.getElementById('communication').value),
        projects_completed: parseInt(document.getElementById('projects').value)
    };

    // Validate inputs
    if (!validateInputs(formData)) {
        alert('Please fill in all fields with valid values');
        return;
    }

    // Make prediction (call backend or use prediction models)
    makePrediction(formData);
}

function validateInputs(data) {
    // Check if all required fields are filled and have valid ranges
    if (data.iq < 0 || data.iq > 200) return false;
    if (data.prev_sem_result < 0 || data.prev_sem_result > 10) return false;
    if (data.cgpa < 0 || data.cgpa > 10) return false;
    if (data.academic_performance < 0 || data.academic_performance > 100) return false;
    if (data.extra_curricular_score < 0 || data.extra_curricular_score > 100) return false;
    if (data.communication_skills < 0 || data.communication_skills > 100) return false;
    if (data.projects_completed < 0) return false;

    return true;
}

function makePrediction(formData) {
    // TODO: Replace this with actual backend API call
    // For now, using a simple prediction models based on weighted factors
    
    // Send to backend
    fetch('/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        displayPredictionResult(data);
    })
    .catch(error => {
        console.error('Error:', error);
        // Fallback to client-side prediction if API fails
        const prediction = predictPlacement(formData);
        displayPredictionResult(prediction);
    });
}

function predictPlacement(formData) {
    // Simple client-side prediction models
    // This is a placeholder - replace with actual ML models
    
    let score = 0;
    
    // Weight factors
    score += (formData.iq / 200) * 15;  // IQ weight: 15%
    score += (formData.prev_sem_result / 10) * 15;  // Previous semester: 15%
    score += (formData.cgpa / 10) * 20;  // CGPA weight: 20%
    score += (formData.academic_performance / 100) * 15;  // Academic performance: 15%
    score += formData.internship_experience * 15;  // Internship: 15%
    score += (formData.extra_curricular_score / 100) * 10;  // Extra curricular: 10%
    score += (formData.communication_skills / 100) * 20;  // Communication: 20%
    score += Math.min((formData.projects_completed / 10), 1) * 10;  // Projects: 10%
    
    // Normalize score to 0-100
    const normalizedScore = (score / 130) * 100;
    
    // Determine placement status (threshold at 50%)
    const isPlaced = normalizedScore >= 50;
    const confidence = Math.min(Math.abs(normalizedScore - 50) / 50 * 100, 95);
    
    return {
        placed: isPlaced,
        confidence: confidence.toFixed(2),
        score: normalizedScore.toFixed(2)
    };
}

function displayPredictionResult(result) {
    const resultSection = document.getElementById('resultSection');
    const resultText = document.getElementById('resultText');
    const confidenceText = document.getElementById('confidenceText');
    
    // Update result text
    const status = result.placed ? 'Placed ✓' : 'Not Placed ✗';
    resultText.textContent = status;
    resultText.className = result.placed ? 'result-text placed' : 'result-text not-placed';
    
    // Update confidence
    confidenceText.textContent = result.confidence + '%';
    
    // Show result section
    resultSection.style.display = 'block';
    
    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
