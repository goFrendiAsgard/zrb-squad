# Fibonacci Clock - Algorithm Documentation

## Overview
This document details the mathematical algorithms behind the Fibonacci Clock.

## Core Concepts

### Fibonacci Sequence
The clock uses: 1, 1, 2, 3, 5

### Time Representation
- **Hours**: Current hour in 12-hour format (1-12)
- **Minutes**: Current minute (0-59), converted to 5-minute intervals (0-11)

### Square Mapping
Five squares correspond to Fibonacci numbers:
- Square 0: 1×1 unit
- Square 1: 1×1 unit  
- Square 2: 2×2 units
- Square 3: 3×3 units
- Square 4: 5×5 units

## Algorithm 1: Convert Number to Fibonacci Sum

### Greedy Algorithm
```javascript
function convertToFibonacci(target) {
  const fibonacci = [5, 3, 2, 1, 1]; // Descending order
  const result = [];
  let remaining = target;
  
  for (const fib of fibonacci) {
    if (remaining >= fib) {
      result.push(fib);
      remaining -= fib;
    }
  }
  
  return remaining === 0 ? result : null;
}
```

### Examples
```
convertToFibonacci(3)  → [3]
convertToFibonacci(8)  → [5, 3]  
convertToFibonacci(12) → [5, 3, 2, 1, 1]
convertToFibonacci(4)  → [3, 1]
convertToFibonacci(0)  → []
```

## Algorithm 2: Time Conversion

### Convert to 12-Hour Format
```javascript
function to12HourFormat(hours24) {
  return hours24 % 12 || 12;
}
```

### Convert Minutes to 5-Minute Blocks
```javascript
function minutesToFiveMinuteBlocks(minutes) {
  return Math.floor(minutes / 5);
}
```

### Complete Conversion
```javascript
function convertTimeToFibonacci(hours24, minutes) {
  const hours12 = to12HourFormat(hours24);
  const minuteBlocks = minutesToFiveMinuteBlocks(minutes);
  
  return {
    hoursFibonacci: convertToFibonacci(hours12),
    minutesFibonacci: convertToFibonacci(minuteBlocks)
  };
}
```

## Algorithm 3: Color Assignment

### Color Rules
1. **Red**: Square used for hours only
2. **Green**: Square used for minutes only  
3. **Blue**: Square used for both hours and minutes
4. **White**: Square not used

### Implementation
```javascript
function assignColors(hoursFib, minutesFib) {
  const colors = ['white', 'white', 'white', 'white', 'white'];
  
  // Mark hours (red)
  if (hoursFib) {
    for (const fib of hoursFib) {
      const squareIndex = getSquareIndexForFib(fib, colors);
      if (colors[squareIndex] === 'white') {
        colors[squareIndex] = 'red';
      }
    }
  }
  
  // Mark minutes (green/blue)
  if (minutesFib) {
    for (const fib of minutesFib) {
      const squareIndex = getSquareIndexForFib(fib, colors);
      if (colors[squareIndex] === 'white') {
        colors[squareIndex] = 'green';
      } else if (colors[squareIndex] === 'red') {
        colors[squareIndex] = 'blue';
      }
    }
  }
  
  return colors;
}
```

## Complete Example: 3:20

### Step 1: Convert Time
- Hours: 3 → [3]
- Minutes: 20 → 20/5 = 4 → [3, 1]

### Step 2: Assign Colors
- Square 3 (3-unit): red (hours) then blue (both)
- Square 0 (1-unit): green (minutes)
- Other squares: white

### Result
```
Square 0: green
Square 1: white  
Square 2: white
Square 3: blue
Square 4: white
```

## Algorithm 4: 24-Hour Format Display

```javascript
function formatTimeDisplay(hours24, minutes, use24HourFormat) {
  if (use24HourFormat) {
    return `${hours24.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  } else {
    const hours12 = to12HourFormat(hours24);
    const period = hours24 < 12 ? 'AM' : 'PM';
    return `${hours12}:${minutes.toString().padStart(2, '0')} ${period}`;
  }
}
```

**Note**: Fibonacci calculation always uses 12-hour format internally.

## Algorithm 5: Update Scheduling

```javascript
class ClockUpdater {
  constructor(updateCallback, intervalMs = 60000) {
    this.updateCallback = updateCallback;
    this.intervalMs = intervalMs;
    this.lastUpdateTime = null;
    this.isRunning = false;
  }
  
  start() {
    this.isRunning = true;
    this.lastUpdateTime = Date.now();
    this.updateCallback();
    this.scheduleNextUpdate();
  }
  
  scheduleNextUpdate() {
    if (!this.isRunning) return;
    
    const now = Date.now();
    const timeSinceLastUpdate = now - this.lastUpdateTime;
    
    if (timeSinceLastUpdate >= this.intervalMs) {
      this.lastUpdateTime = now;
      this.updateCallback();
    }
    
    requestAnimationFrame(() => this.scheduleNextUpdate());
  }
}
```

## Mathematical Properties

### Completeness Theorem
All integers 1-12 can be represented as sums of {1, 1, 2, 3, 5}.

**Proof by enumeration**:
```
1 = 1
2 = 2 or 1+1
3 = 3
4 = 3+1
5 = 5
6 = 5+1
7 = 5+2 or 5+1+1
8 = 5+3
9 = 5+3+1
10 = 5+3+2
11 = 5+3+2+1
12 = 5+3+2+1+1
```

### Uniqueness
Some numbers have multiple representations:
- 2 = 2 OR 1+1
- 4 = 3+1 OR 2+1+1
- 7 = 5+2 OR 5+1+1

The greedy algorithm always chooses the representation with largest Fibonacci numbers first.

## Edge Cases

### Midnight (00:00)
- Hours: 0 → converted to 12 → [5, 3, 2, 1, 1]
- Minutes: 0 → []
- Result: All squares red

### Minutes 56-59
- 56/5 = 11.2 → floor(11.2) = 11
- 59/5 = 11.8 → floor(11.8) = 11
- All display as 55 minutes (11 × 5)

### Non-Representable Times
Theoretically impossible with current algorithm, as all 1-12 are representable.

## Performance Characteristics

### Time Complexity
- `convertToFibonacci`: O(1) - constant time (5 iterations)
- `assignColors`: O(1) - constant time (max 10 iterations)
- Complete update: O(1) - constant time

### Space Complexity
- O(1) - constant space (small fixed arrays)

### DOM Updates
- 5 square color updates per minute
- 1 digital time update per minute
- Minimal performance impact

## Testing the Algorithm

### Test Cases
```javascript
const testCases = [
  { time: "3:20", expected: ["green", "white", "white", "blue", "white"] },
  { time: "8:45", expected: ["green", "white", "white", "blue", "blue"] },
  { time: "12:00", expected: ["red", "red", "red", "red", "red"] },
  { time: "1:05", expected: ["blue", "white", "white", "white", "white"] }
];
```

### Validation Function
```javascript
function testAlgorithm() {
  let passed = 0;
  testCases.forEach(({ time, expected }) => {
    const [hours, minutes] = time.split(":").map(Number);
    const result = convertTimeToFibonacci(hours, minutes);
    const colors = assignColors(result.hoursFibonacci, result.minutesFibonacci);
    
    if (arraysEqual(colors, expected)) {
      passed++;
    }
  });
  
  console.log(`${passed}/${testCases.length} tests passed`);
  return passed === testCases.length;
}
```

## Conclusion

The Fibonacci Clock algorithm is mathematically sound and computationally efficient. It provides a unique visual representation of time using fundamental mathematical principles.

**Key Insights**:
1. Uses greedy algorithm for Fibonacci representation
2. Always produces valid results for 1-12 hours
3. Handles edge cases gracefully
4. Efficient O(1) time and space complexity
5. Deterministic and predictable behavior