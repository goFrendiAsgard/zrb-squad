// Fibonacci Clock JavaScript - Fixed Implementation with Correct Time Calculation

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

// Fibonacci sequence values [1, 1, 2, 3, 5]
const FIBONACCI_VALUES = [1, 1, 2, 3, 5];

// Global state
let is24HourFormat = true;
let isAnimating = true;

// Initialize the Fibonacci grid with correct layout
function initFibonacciClock() {
    const grid = $('#fibonacci-grid');
    grid.empty();
    
    // Create Fibonacci squares with correct indices
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
    
    console.log("Fibonacci grid initialized with correct layout");
}

// Update current date and time
function updateDateTime() {
    const now = new Date();
    
    // Get current time
    let hours = now.getHours();
    const minutes = now.getMinutes();
    
    // Format time display
    let displayHours = hours;
    if (!is24HourFormat) {
        displayHours = hours % 12 || 12;
    }
    
    const timeString = `${String(displayHours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
    $('#current-time').text(timeString);
    
    // Format date
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const formattedDate = now.toLocaleDateString('en-US', options);
    $('#current-date').text(formattedDate);
    
    // Update year in footer
    $('#current-year').text(now.getFullYear());
    
    // Update Fibonacci squares based on actual time calculation
    updateFibonacciColors(hours, minutes);
}

// Update Fibonacci square colors based on actual time calculation
function updateFibonacciColors(hours, minutes) {
    // Convert to Fibonacci clock representation
    // Fibonacci clock uses 12-hour format (1-12)
    const fibHours = hours % 12 || 12;
    
    // Convert minutes to 5-minute blocks (0-11, where each = 5 minutes)
    const fibMinutes = Math.floor(minutes / 5);
    
    console.log(`Fibonacci Time: ${fibHours} hours, ${fibMinutes} minute blocks (actual: ${minutes} minutes)`);
    
    // Calculate which squares represent hours and minutes
    const hourSquares = calculateFibonacciRepresentation(fibHours);
    const minuteSquares = calculateFibonacciRepresentation(fibMinutes);
    
    // Update each square
    $('.fib-square').each(function(index) {
        const square = $(this);
        
        // Remove all color classes
        square.removeClass('fib-hour fib-minute fib-both fib-inactive');
        
        // Determine color based on hour/minute representation
        const isHour = hourSquares.includes(index);
        const isMinute = minuteSquares.includes(index);
        
        if (isHour && isMinute) {
            square.addClass('fib-both'); // Blue - represents both hours and minutes
        } else if (isHour) {
            square.addClass('fib-hour'); // Red - represents hours only
        } else if (isMinute) {
            square.addClass('fib-minute'); // Green - represents minutes only
        } else {
            square.addClass('fib-inactive'); // White - inactive
        }
        
        // Update tooltip
        updateSquareTooltip(square, index, isHour, isMinute);
    });
}

// Calculate which Fibonacci squares represent a given value (1-12 for hours, 0-11 for minutes)
function calculateFibonacciRepresentation(target) {
    const squares = [];
    let remaining = target;
    
    // Try to use the largest Fibonacci numbers first (greedy algorithm)
    // Check each Fibonacci value in reverse order (5, 3, 2, 1, 1)
    const fibIndices = [4, 3, 2, 1, 0]; // Indices for values [5, 3, 2, 1, 1]
    
    for (const index of fibIndices) {
        if (remaining >= FIBONACCI_VALUES[index]) {
            // Check if this square is already used (for duplicate value 1)
            if (!squares.includes(index)) {
                squares.push(index);
                remaining -= FIBONACCI_VALUES[index];
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
    
    // Try largest squares first
    const fibIndices = [4, 3, 2, 1, 0]; // [5, 3, 2, 1, 1]
    
    for (const index of fibIndices) {
        if (sum + FIBONACCI_VALUES[index] <= target) {
            if (!squares.includes(index)) {
                squares.push(index);
                sum += FIBONACCI_VALUES[index];
            }
        }
        
        if (sum === target) {
            break;
        }
    }
    
    return squares;
}

// Update square tooltip with explanation
function updateSquareTooltip(square, index, isHour, isMinute) {
    const value = FIBONACCI_VALUES[index];
    let explanation = `Fibonacci value: ${value}`;
    
    if (isHour && isMinute) {
        explanation += ` (Represents both hours and minutes)`;
    } else if (isHour) {
        explanation += ` (Represents hours)`;
    } else if (isMinute) {
        explanation += ` (Represents minutes)`;
    } else {
        explanation += ` (Inactive)`;
    }
    
    square.attr('title', explanation);
}

// Set up all event listeners
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
        }, 500);
        
        console.log("Clock reset");
    });
    
    // Footer link interactions
    $('#github-link').click(function(e) {
        e.preventDefault();
        alert('GitHub repository link would open here. Demo feature.');
        console.log("GitHub link clicked");
    });
    
    $('#documentation-link').click(function(e) {
        e.preventDefault();
        alert('Documentation would open here. Demo feature.');
        console.log("Documentation link clicked");
    });
    
    $('#settings-link').click(function(e) {
        e.preventDefault();
        alert('Settings panel would open here. Demo feature.');
        console.log("Settings link clicked");
    });
    
    // Add CSS for feedback animations
    $('<style>').text(`
        .pulse-feedback {
            animation: pulse 0.3s ease;
        }
        .reset-feedback {
            animation: spin 0.5s ease;
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    `).appendTo('head');
}

// Test function to verify the algorithm
function testFibonacciAlgorithm() {
    console.log("Testing Fibonacci algorithm with sample times:");
    
    const testTimes = [
        { hours: 1, minutes: 0, expected: "1:00" },
        { hours: 5, minutes: 0, expected: "5:00" },
        { hours: 8, minutes: 0, expected: "8:00" },
        { hours: 12, minutes: 0, expected: "12:00" },
        { hours: 3, minutes: 25, expected: "3:25" },
        { hours: 7, minutes: 50, expected: "7:50" }
    ];
    
    testTimes.forEach(test => {
        const hourSquares = calculateFibonacciRepresentation(test.hours % 12 || 12);
        const minuteSquares = calculateFibonacciRepresentation(Math.floor(test.minutes / 5));
        
        console.log(`${test.expected}: Hours=${hourSquares.map(i => FIBONACCI_VALUES[i])}, Minutes=${minuteSquares.map(i => FIBONACCI_VALUES[i])}`);
    });
}

// Run test on load
$(document).ready(function() {
    setTimeout(testFibonacciAlgorithm, 1000);
});