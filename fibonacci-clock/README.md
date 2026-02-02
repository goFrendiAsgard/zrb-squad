# Fibonacci Clock

A mathematical timepiece that displays time using the Fibonacci sequence through colored squares.

## Project Overview

The Fibonacci Clock is a unique web-based time display that represents time using squares sized according to the Fibonacci sequence. Instead of traditional clock hands or digital numbers, this clock uses a combination of colored squares to show the current time in a visually appealing and mathematically interesting way.

This project combines mathematical concepts with modern web technologies to create an interactive and educational time display.

## How the Fibonacci Clock Works

### The Fibonacci Sequence
The clock uses the first five numbers of the Fibonacci sequence: **1, 1, 2, 3, 5**. These numbers represent the relative sizes of the squares in the clock display.

### Time Representation
The clock uses a 5×5 grid containing squares of different sizes based on the Fibonacci sequence. Each square can be in one of four states:

- **Red Squares**: Represent **hours**
- **Green Squares**: Represent **minutes** 
- **Blue Squares**: Represent **both hours and minutes**
- **White Squares**: Are **inactive** (not used in the current time calculation)

### Reading the Time
To read the time from the Fibonacci Clock:

1. **Hours**: Sum the values of all red and blue squares
2. **Minutes**: Sum the values of all green and blue squares, then multiply by 5
3. **Format**: The clock can display time in either 12-hour or 24-hour format

### Example
If the clock shows:
- Red squares with values 3 and 2 (total: 5)
- Green squares with values 5 and 1 (total: 6 × 5 = 30)
- Blue squares with value 1 (adds to both hours and minutes)

The time would be: **6:35** (5+1 hours, 30+5 minutes)

## Installation and Usage

### Quick Start
1. Clone or download the project files
2. Open `index.html` in any modern web browser
3. The clock will automatically start displaying the current time

### No Installation Required
Since this is a client-side web application, no server setup or installation is required. The application runs entirely in the browser using:
- HTML5 for structure
- CSS3 for styling
- JavaScript/jQuery for functionality

### Features
- **Real-time display**: Shows current time and date
- **Format toggle**: Switch between 12-hour and 24-hour formats
- **Animation control**: Play/pause the time updates
- **Reset function**: Reset to current system time
- **Responsive design**: Works on desktop and mobile devices

## Technical Stack

### Core Technologies
- **HTML5**: Semantic markup and structure
- **CSS3**: Modern styling with Flexbox/Grid layouts
- **JavaScript**: Core logic and interactivity

### Libraries and Dependencies
- **jQuery 3.6.4**: DOM manipulation and event handling
- **Font Awesome 6.4.0**: Icon library for UI elements
- **Google Fonts**: Typography (if used)

### Browser Compatibility
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+
- Opera 47+

## File Structure

```
fibonacci-clock/
├── index.html          # Main HTML file with clock structure
├── style.css           # CSS styles for the clock interface
├── script.js           # JavaScript logic for time calculation and display
├── README.md           # This documentation file
├── test-structure.html # HTML structure testing utility
└── assets/             # Directory for images, fonts, and other assets
```

### File Descriptions

#### `index.html`
The main HTML file that contains:
- Clock container and grid structure
- Time display elements
- Control buttons (format toggle, play/pause, reset)
- Information panel explaining the Fibonacci sequence
- Footer with links and copyright information

#### `style.css`
Contains all styling rules for:
- Layout and positioning using Flexbox/Grid
- Color schemes for different square states
- Typography and spacing
- Responsive design for different screen sizes
- Animation and transition effects

#### `script.js`
Handles all JavaScript functionality:
- Time calculation using Fibonacci sequence
- Grid generation and square coloring
- Event handlers for user interactions
- Real-time updates
- Format conversion (12h/24h)

#### `test-structure.html`
A testing utility that:
- Validates HTML structure and data attributes
- Checks accessibility features (ARIA attributes)
- Verifies control panel elements
- Tests meta tags for SEO

#### `assets/`
Directory reserved for:
- Image files (logos, icons, backgrounds)
- Font files (custom typography)
- Other media assets

## Development Status

### Current Features
- ✅ Basic HTML structure
- ✅ CSS styling framework
- ✅ jQuery integration
- ✅ Responsive layout
- ✅ Control interface
- ✅ Structure testing utility

### Planned Features
- ⏳ Complete Fibonacci time calculation logic
- ⏳ Dynamic grid generation
- ⏳ Square coloring based on time
- ⏳ Smooth animations
- ⏳ Settings panel
- ⏳ Theme customization
- ⏳ Export functionality

## Contributing

This is a preliminary documentation that will be expanded as the project develops. Future updates will include:

1. Detailed API documentation
2. Development setup instructions
3. Testing guidelines
4. Deployment instructions
5. Performance optimization notes

## License

Copyright © 2024 Fibonacci Clock Project. All rights reserved.

## Acknowledgments

- Inspired by mathematical clock designs
- Built with modern web technologies
- Educational tool for understanding Fibonacci sequence applications