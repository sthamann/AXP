# Nike - 3D Experience Capsule

## Overview
This AXP Experience Capsule provides an interactive 3D visualization of a Nike shoe using the `nike.glb` model file. The capsule features a branded micro-experience with real-time 3D model viewing, color customization, and size selection. GLB format ensures compatibility and works without requiring a web server.

## Features
- **Real-time 3D Model Viewing**: Interactive 3D visualization using Google's model-viewer component
- **Auto-rotation**: Automatic rotation for product showcase
- **Touch & Mouse Controls**: Full camera orbit control for detailed inspection
- **Color Variants**: Four premium colorways (White/Black, Triple Black, Orange Blaze, Wolf Gray)
- **Size Selection**: EU sizes 38-46
- **Nike Branding**: Authentic Nike visual identity with signature orange (#FF6900)
- **AXP Protocol Support**: Full compliance with AXP Capsule Communication Protocol

## Technical Details
- **Model Format**: GLB (Binary glTF 2.0)
- **3D Engine**: model-viewer 3.3.0
- **File**: `nike.glb`
- **Responsive Design**: Optimized for desktop and mobile devices
- **Dark Theme**: Premium black/gray gradient background
- **No Server Required**: GLB format works directly from file:// URLs

## AXP Communication
The capsule implements the full AXP protocol:

### Inbound Events
- `init`: Initialize capsule with correlation ID
- `configure`: Set color and size parameters
- `set_variant`: Change product variant
- `request_quote`: Get pricing information

### Outbound Events
- `ready` / `capsule_ready`: Capsule initialization complete
- `state_changed`: Configuration updates
- `add_to_cart`: Add product to cart with SKU
- `telemetry`: User interaction tracking
- `quote_response`: Price and variant information

## Usage

### Running the Demos

⚠️ **Important**: Due to browser security (CORS), you need a local server to load GLB files in Chrome/Edge.

#### Quick Start - Server Already Running!
The server is running on port 8080. Open these links:
- http://localhost:8080/nike-viewer.html - 3D Viewer
- http://localhost:8080/chat.html - ChatGPT Interface
- http://localhost:8080/simple-test.html - Simple Test

#### Alternative: Use Firefox or Safari
These browsers are more permissive with local files:
- **Firefox**: Can open files directly without a server
- **Safari**: Enable "Develop > Disable Local File Restrictions"

#### Optional: With Web Server
If you prefer to use a web server:
```bash
# Navigate to the sneaker-3d directory
cd examples/capsules/sneaker-3d

# Python 3
python -m http.server 8000
```

Then access via:
- http://localhost:8000/nike-viewer.html
- http://localhost:8000/chat.html
- http://localhost:8000/test.html

### Embedded in AXP Client
```javascript
// Initialize capsule
parent.postMessage({ 
  type: 'init', 
  correlationId: 'abc123' 
}, '*');

// Configure variant
parent.postMessage({
  type: 'configure',
  params: {
    color: 'black',
    size: '42'
  }
}, '*');
```

## Keyboard Controls
- **Arrow Left/Right**: Rotate model manually
- **Space**: Toggle auto-rotation
- **Mouse/Touch**: Drag to orbit, pinch to zoom

## Color Pricing
- White/Black: €189.00
- Triple Black: €199.00
- Orange Blaze: €209.00
- Wolf Gray: €189.00

## Files
- `nike-viewer.html` - Main viewer for nike.glb model
- `index.html` - Alternative implementation 
- `chat.html` - ChatGPT-style demo with embedded micro-experience
- `test.html` - AXP protocol testing interface
- `nike.glb` - Nike 3D model file (GLB format)
- `manifest.json` - AXP capsule configuration
- `README.md` - This documentation

## Requirements
- Modern web browser with WebGL support
- Internet connection for model-viewer library (CDN)
- Local web server (provided) OR Firefox/Safari browser
- Python 3 (for included server script)

## Browser Compatibility
- Chrome 79+
- Safari 12+
- Firefox 80+
- Edge 79+
- Mobile Safari (iOS 12+)
- Chrome Mobile (Android)

## Notes
- GLB (Binary glTF) format ensures maximum compatibility across all browsers
- Works without a web server - can be opened directly as local files
- The model-viewer library automatically handles rendering and optimization
- Auto-rotation starts immediately for engaging product presentation
- Dynamic pricing updates based on selected colorway
- AR support available on compatible devices
- **Important**: The model-viewer element requires environment and lighting attributes (`environment-image`, `exposure`, `tone-mapping`) for proper model visibility

## License
Part of the AXP (Autonomous Experience Protocol) examples.
