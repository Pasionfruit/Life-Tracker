function incrementCounter(habitId) {
    fetch(`/habit/${habitId}/increment`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        const counterElement = document.getElementById(`counter-${habitId}`);
        counterElement.innerText = data.counter;
    });
}