async function incrementCounter(habitId) {
    try {
      const response = await fetch('/increment', {
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
  