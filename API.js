async function fetchRecommendation() {
    try {
        const response = await fetch('http://localhost:5000/recommendation');
        const data = await response.json();
        document.getElementById('recommendation').innerText = data.recommendation;
    } catch (error) {
        console.error('Error fetching recommendation:', error);
    }
}

// Call this function periodically or on a user action
fetchRecommendation();
