const datesElement = document.getElementById('dates');
const daysElement = document.getElementById('days');
const monthYearElement = document.getElementById('month-year');
const prevButton = document.getElementById('prev');
const nextButton = document.getElementById('next');

const habitContainer = document.getElementById('habitCounterContainer');
const addHabitButton = document.getElementById('addHabitButton');

let habitId = 1;

// Add new habit
function addHabit() {
}

let currentDate = new Date();

// Sample data for date statuses
let dateStatuses = {
  '2024-12-01': 'green',
  '2024-12-03': 'green',
  '2024-12-15': 'yellow',
  '2024-12-02': 'red',
};

function renderCalendar(date) {
  datesElement.innerHTML = '';
  daysElement.innerHTML = '';

  const locale = navigator.language;
  const monthYearFormatter = new Intl.DateTimeFormat(locale, { month: 'long', year: 'numeric' });
  const weekDayFormatter = new Intl.DateTimeFormat(locale, { weekday: 'short' });

  // Set month and year in header
  monthYearElement.textContent = monthYearFormatter.format(date);

  // Create weekday headers
  const daysOfWeek = Array.from({ length: 7 }, (_, i) =>
    weekDayFormatter.format(new Date(1970, 0, i + 4))
  );
  daysOfWeek.forEach(day => {
    const dayDiv = document.createElement('div');
    dayDiv.textContent = day;
    daysElement.appendChild(dayDiv);
  });

  const firstDay = new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  const daysInMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();

  // Add placeholders for days before the first of the month
  for (let i = 0; i < firstDay; i++) {
    const emptyDiv = document.createElement('div');
    datesElement.appendChild(emptyDiv);
  }

  // Add actual days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    const dayDiv = document.createElement('div');
    dayDiv.textContent = day;

    const fullDate = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    
    // Apply status classes based on dateStatuses
    if (dateStatuses[fullDate]) {
      dayDiv.classList.add(dateStatuses[fullDate]);
    }

    datesElement.appendChild(dayDiv);
  }
}

// Navigation buttons
prevButton.addEventListener('click', () => {
  currentDate.setMonth(currentDate.getMonth() - 1);
  renderCalendar(currentDate);
});

nextButton.addEventListener('click', () => {
  currentDate.setMonth(currentDate.getMonth() + 1);
  renderCalendar(currentDate);
});

// Initial render
renderCalendar(currentDate);
