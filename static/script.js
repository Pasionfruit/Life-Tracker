async function incrementCounter(habitId) {
    try {
      const response = await fetch(`/increment/${habitId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: habitId }), // Send the habit ID
      });
  
      const result = await response.json();
      if (result.success) {
        // Update the progress in the DOM
        const progressElement = document.getElementById(`progress-${habitId}`);
        if (progressElement) {
          progressElement.textContent = result.Progress;
        }
        // alert(`Progress updated: ${result.Progress}`);
      } else {
        // alert(result.message || 'Error incrementing progress.');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to increment progress.');
    }
  }
  
async function decrementCounter(habitId) {
  try {
    const response = await fetch(`/decrement/${habitId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id: habitId }), // Send the habit ID
    });

    const result = await response.json();
    if (result.success) {
      // Update the progress in the DOM
      const progressElement = document.getElementById(`progress-${habitId}`);
      if (progressElement) {
        progressElement.textContent = result.Progress;
      }
      // alert(`Progress updated: ${result.Progress}`);
    } else {
      // alert(result.message || 'Error decrementing progress.');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to decrement progress.');
  }
}