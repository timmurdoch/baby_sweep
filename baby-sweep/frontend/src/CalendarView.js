import React, { useState, useEffect } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const localizer = momentLocalizer(moment);

function CalendarView({ sessionToken, settings, onSelectTimeSlots, maxBlockSelectionMinutes = 60 }) {
  const [events, setEvents] = useState([]);
  const [selectedSlots, setSelectedSlots] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCalendarGuesses();
  }, [sessionToken]);

  const fetchCalendarGuesses = async () => {
    try {
      const response = await fetch(`http://localhost:3001/api/guesses/calendar?token=${sessionToken}`);
      const data = await response.json();

      // Transform the data to calendar events
      const calendarEvents = data.map(event => ({
        ...event,
        start: new Date(event.start),
        end: new Date(event.end)
      }));

      setEvents(calendarEvents);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching calendar guesses:', error);
      setLoading(false);
    }
  };

  // Handle slot selection (clicking on empty time slots)
  const handleSelectSlot = (slotInfo) => {
    const { start, end, action } = slotInfo;

    // Only allow selection within the valid date range
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const dueDate = new Date(settings.due_date);

    if (start < today || start > dueDate) {
      alert('Please select a date between today and the due date.');
      return;
    }

    // Create a time slot identifier
    const timeSlot = {
      date: moment(start).format('YYYY-MM-DD'),
      time: moment(start).format('HH:mm')
    };

    // Check if this slot is already selected
    const slotKey = `${timeSlot.date}-${timeSlot.time}`;
    const isSelected = selectedSlots.some(slot => `${slot.date}-${slot.time}` === slotKey);

    if (isSelected) {
      // Deselect the slot
      setSelectedSlots(selectedSlots.filter(slot => `${slot.date}-${slot.time}` !== slotKey));
    } else {
      // Check if adding this slot would exceed the max duration
      const timeBlockMinutes = parseInt(settings.time_block_minutes) || 30;
      const currentDuration = selectedSlots.length * timeBlockMinutes;
      const newDuration = currentDuration + timeBlockMinutes;

      if (newDuration > maxBlockSelectionMinutes) {
        const maxSlots = Math.floor(maxBlockSelectionMinutes / timeBlockMinutes);
        const maxHours = Math.floor(maxBlockSelectionMinutes / 60);
        const maxMinutes = maxBlockSelectionMinutes % 60;
        const maxDurationStr = maxMinutes > 0 ? `${maxHours}h ${maxMinutes}m` : `${maxHours} hour${maxHours > 1 ? 's' : ''}`;

        alert(`Maximum block selection is ${maxDurationStr} (${maxSlots} time slot${maxSlots > 1 ? 's' : ''}). Please clear your current selection or deselect some slots.`);
        return;
      }

      // Select the slot (add to array for multi-selection)
      setSelectedSlots([...selectedSlots, timeSlot]);
    }
  };

  // Handle event click (clicking on existing guesses)
  const handleSelectEvent = (event) => {
    // Show guess details in an alert (can be enhanced with a modal later)
    const guess = event.resource;
    const timeBlocks = guess.is_block_guess && guess.time_blocks ?
      JSON.parse(guess.time_blocks).join(', ') : guess.birth_time;

    alert(`Guess Details:\n\nName: ${guess.name}\nGender: ${guess.gender}\nDate: ${guess.birth_date}\nTime${guess.is_block_guess ? 's' : ''}: ${timeBlocks}\nWeight: ${guess.weight_lbs} lbs ${guess.weight_oz} oz (${guess.weight_kg} kg)`);
  };

  // Custom event style to show gender colors
  const eventStyleGetter = (event) => {
    const guess = event.resource;
    let backgroundColor = '#3b82f6'; // Default blue

    if (guess.gender === 'boy') {
      backgroundColor = '#3b82f6'; // Blue
    } else if (guess.gender === 'girl') {
      backgroundColor = '#ec4899'; // Pink
    } else if (guess.gender === 'surprise') {
      backgroundColor = '#a855f7'; // Purple
    }

    return {
      style: {
        backgroundColor,
        borderRadius: '4px',
        opacity: 0.8,
        color: 'white',
        border: '0px',
        display: 'block'
      }
    };
  };

  // Custom day cell wrapper to highlight selected slots
  const DayWrapper = ({ children, value }) => {
    const dateStr = moment(value).format('YYYY-MM-DD');
    const hasSelectedSlot = selectedSlots.some(slot => slot.date === dateStr);

    return React.cloneElement(React.Children.only(children), {
      style: {
        ...children.props.style,
        backgroundColor: hasSelectedSlot ? '#fef3c7' : undefined
      }
    });
  };

  // Clear selected slots
  const clearSelection = () => {
    setSelectedSlots([]);
  };

  // Confirm selection and pass to parent
  const confirmSelection = () => {
    if (selectedSlots.length === 0) {
      alert('Please select at least one time slot.');
      return;
    }

    // Group slots by date (in case multiple days are selected)
    const groupedByDate = selectedSlots.reduce((acc, slot) => {
      if (!acc[slot.date]) {
        acc[slot.date] = [];
      }
      acc[slot.date].push(slot.time);
      return acc;
    }, {});

    // For simplicity, we'll only support single date with multiple times
    const dates = Object.keys(groupedByDate);
    if (dates.length > 1) {
      alert('Please select time slots from only one date.');
      return;
    }

    const selectedDate = dates[0];
    const selectedTimes = groupedByDate[selectedDate];

    onSelectTimeSlots({
      date: selectedDate,
      times: selectedTimes,
      isBlock: selectedTimes.length > 1
    });

    clearSelection();
  };

  if (loading) {
    return <div className="loading">Loading calendar...</div>;
  }

  return (
    <div className="calendar-view">
      <div className="calendar-header">
        <h2>Baby Arrival Calendar</h2>
        <div className="calendar-legend">
          <span className="legend-item"><span className="dot boy"></span> Boy</span>
          <span className="legend-item"><span className="dot girl"></span> Girl</span>
          <span className="legend-item"><span className="dot surprise"></span> Surprise</span>
        </div>
      </div>

      {selectedSlots.length > 0 && (
        <div className="selection-panel">
          <p>
            <strong>Selected:</strong> {selectedSlots.length} time slot{selectedSlots.length > 1 ? 's' : ''} on {selectedSlots[0].date}
          </p>
          <div className="selection-actions">
            <button onClick={confirmSelection} className="btn btn-primary">
              Use This Selection
            </button>
            <button onClick={clearSelection} className="btn btn-secondary">
              Clear
            </button>
          </div>
        </div>
      )}

      <div className="calendar-instructions">
        <p>Click on empty time slots to select your guess. Hold Shift and drag to select multiple consecutive times.</p>
      </div>

      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 600 }}
        onSelectSlot={handleSelectSlot}
        onSelectEvent={handleSelectEvent}
        selectable={true}
        eventPropGetter={eventStyleGetter}
        views={['month', 'week', 'day']}
        defaultView="week"
        step={parseInt(settings.time_block_minutes) || 30}
        timeslots={1}
        min={new Date(0, 0, 0, 0, 0, 0)} // Start at midnight
        max={new Date(0, 0, 0, 23, 59, 59)} // End at 11:59 PM
        components={{
          dateCellWrapper: DayWrapper
        }}
      />
    </div>
  );
}

export default CalendarView;
