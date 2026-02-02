// Fibonacci Clock JavaScript - Corrected for New Layout

$(document).ready(function() {
    console.log("Fibonacci Clock loaded!");
    
    // Initialize the clock
    initFibonacciClock();
    updateDateTime();
    
    // Set up event listeners
    setupEventListeners();
    
    // Update time every second
    setInterval(updateDateTime, 1000);
});

// Global state
let is24HourFormat = true;
let isAnimating = true;

// Fibonacci values in the order needed for our corrected layout:
// Square 1 (first), Square 1 (second), Square 3, Square 2, Square 5
const FIBONACCI_VALUES = [1, 1, 3, 2, 5];

// Initialize the Fibonacci grid with corrected layout
function initFibonacciClock() {
    const grid = $('#fibonacci-grid');
    grid.empty();
    
    // Create Fibonacci squares in the correct order for our layout
    FIBONACCI_VALUES.forEach((value, index) => {
        const square = $('<div>').addClass('fib-square');
        
        // Set data attributes
        square.attr('data-value', value);
        square.attr('data-index', index);
        
        // Add Fibonacci number display
        square.text(`F${value}`);
        
        // Start with inactive state
        square.addClass('fib-inactive');
        
        grid.append(square);
    });
    
    console.log("Fibonacci grid initialized with corrected layout");
}

// Update current date and time
function updateDateTime() {
    const now = new Date();
    
    // Format time based on current setting
    let hours = now.getHours();
    const minutes = now.getMinutes();
    
    // Convert to 12-hour format if needed
    let displayHours = hours;
    if (!is24HourFormat) {
        displayHours = hours % 12;
        if (displayHours === 0) displayHours = 12;
    }
    
    // Format time string
    const timeString = `${displayHours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
    $('#current-time').text(timeString);
    
    // Format date
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateString = now.toLocaleDateString('en-US', options);
    $('#current-date').text(dateString);
    
    // Update Fibonacci representation
    updateFibonacciTime(hours, minutes);
}

// Calculate Fibonacci representation for a target number
function calculateFibonacciRepresentation(target) {
    const squares = [];
    let remaining = target;
    
    // Try to use the largest Fibonacci numbers first (greedy algorithm)
    // We need to use the original Fibonacci values [5, 3, 2, 1, 1] for calculation
    // but map them to our layout indices [4, 2, 3, 0, 1]
    const fibValues = [5, 3, 2, 1, 1];
    const layoutIndices = [4, 2, 3, 0, 1]; // Maps [5, 3, 2, 1, 1] to our layout indices [4, 2, 3, 0, 1]
    
    for (let i = 0; i < fibValues.length; i++) {
        if (remaining >= fibValues[i]) {
            const layoutIndex = layoutIndices[i];
            // Check if this square is already used (for duplicate value 1)
            if (!squares.includes(layoutIndex)) {
                squares.push(layoutIndex);
                remaining -= fibValues[i];
            }
        }
        
        if (remaining === 0) {
            break;
        }
    }
    
    // If we couldn't represent the exact value, use a fallback
    if (remaining > 0) {
        console.log(`Could not exactly represent ${target}, using approximation`);
        // Try alternative combinations
        return findAlternativeCombination(target);
    }
    
    return squares;
}

// Find alternative combination for values that can't be exactly represented
function findAlternativeCombination(target) {
    // Simple fallback: use squares that sum to closest value <= target
    const squares = [];
    let sum = 0;
    
    // Use original Fibonacci values [5, 3, 2, 1, 1] mapped to layout indices
    const fibValues = [5, 3, 2, 1, 1];
    const layoutIndices = [4, 2, 3, 0, 1];
    
    for (let i = 0; i < fibValues.length; i++) {
        if (sum + fibValues[i] <= target) {
            const layoutIndex = layoutIndices[i];
            // Check if this square is already used (for duplicate value 1)
            if (!squares.includes(layoutIndex)) {
                squares.push(layoutIndex);
                sum += fibValues[i];
            }
        }
    }
    
    return squares;
}

// Update Fibonacci time representation
function updateFibonacciTime(hours, minutes) {
    // Convert hours to 12-hour format for Fibonacci calculation
    const hour12 = hours % 12;
    const hourValue = hour12 === 0 ? 12 : hour12;
    
    // Convert minutes to 5-minute blocks (0-11)
    const minuteValue = Math.floor(minutes / 5);
    
    console.log(`Time: ${hours}:${minutes} -> Hour value: ${hourValue}, Minute value: ${minuteValue}`);
    
    // Calculate which squares represent hours and minutes
    const hourSquares = calculateFibonacciRepresentation(hourValue);
    const minuteSquares = calculateFibonacciRepresentation(minuteValue);
    
    console.log("Hour squares (indices):", hourSquares);
    console.log("Minute squares (indices):", minuteSquares);
    
    // Update all squares
    $('.fib-square').each(function(index) {
        const square = $(this);
        const isHour = hourSquares.includes(index);
        const isMinute = minuteSquares.includes(index);
        
        // Remove all color classes
        square.removeClass('fib-hour fib-minute fib-both fib-inactive');
        
        // Add appropriate color class
        if (isHour && isMinute) {
            square.addClass('fib-both');
            console.log(`Square ${index} (F${square.attr('data-value')}): Both hours and minutes`);
        } else if (isHour) {
            square.addClass('fib-hour');
            console.log(`Square ${index} (F${square.attr('data-value')}): Hours only`);
        } else if (isMinute) {
            square.addClass('fib-minute');
            console.log(`Square ${index} (F${square.attr('data-value')}): Minutes only`);
        } else {
            square.addClass('fib-inactive');
            console.log(`Square ${index} (F${square.attr('data-value')}): Inactive`);
        }
    });
    
    // Update sequence display
    $('#sequence-values').text(FIBONACCI_VALUES.join(', '));
}

// Set up event listeners for controls
function setupEventListeners() {
    // Toggle 12/24 hour format
    $('#toggle-format').click(function() {
        is24HourFormat = !is24HourFormat;
        const buttonText = is24HourFormat ? '12/24h' : '12/24h';
        
        $(this).html(`<i class="fas fa-exchange-alt"></i> ${buttonText}`);
        
        // Add visual feedback
        $(this).addClass('pulse-feedback');
        setTimeout(() => {
            $(this).removeClass('pulse-feedback');
        }, 300);
        
        console.log("Time format toggled:", is24HourFormat ? "24-hour" : "12-hour");
        updateDateTime(); // Update display immediately
    });
    
    // Toggle animation
    $('#toggle-animation').click(function() {
        isAnimating = !isAnimating;
        const buttonText = isAnimating ? 'Pause' : 'Play';
        
        if (isAnimating) {
            $(this).find('i').removeClass('fa-pause').addClass('fa-play');
            $('.fib-square').css('animation-play-state', 'running');
        } else {
            $(this).find('i').removeClass('fa-play').addClass('fa-pause');
            $('.fib-square').css('animation-play-state', 'paused');
        }
        
        $(this).html(`<i class="fas ${isAnimating ? 'fa-play' : 'fa-pause'}"></i> ${buttonText}`);
        
        console.log("Animation toggled:", isAnimating ? "Playing" : "Paused");
    });
    
    // Reset clock
    $('#reset-clock').click(function() {
        initFibonacciClock();
        updateDateTime();
        
        // Add visual feedback
        $(this).addClass('reset-feedback');
        setTimeout(() => {
            $(this).removeClass('reset-feedback');
        }, 300);
        
        console.log("Clock reset");
    });
}

// Test function to verify the algorithm
function testFibonacciAlgorithm() {
    const testCases = [
        { time: "1:00", hour: 1, minute: 0, expected: "Hour: 1, Minute: 0" },
        { time: "5:00", hour: 5, minute: 0, expected: "Hour: 5, Minute: 0" },
        { time: "8:00", hour: 8, minute: 0, expected: "Hour: 8, Minute: 0" },
        { time: "12:00", hour: 12, minute: 0, expected: "Hour: 12, Minute: 0" },
        { time: "3:25", hour: 3, minute: 5, expected: "Hour: 3, Minute: 5" },
        { time: "7:50", hour: 7, minute: 10, expected: "Hour: 7, Minute: 10" }
    ];
    
    console.log("Testing Fibonacci algorithm:");
    testCases.forEach(test => {
        const hourSquares = calculateFibonacciRepresentation(test.hour);
        const minuteSquares = calculateFibonacciRepresentation(test.minute);
        console.log(`${test.expected}: Hours=${hourSquares}, Minutes=${minuteSquares}`);
    });
}

// Run tests on load
testFibonacciAlgorithm();