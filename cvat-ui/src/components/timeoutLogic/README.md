# Session Timeout Feature

This module implements a session timeout feature for CVAT that automatically logs out users after a period of inactivity.

## Components

### TimeoutLogic
The main component that manages the session timeout logic. It:
- Monitors user activity through various events (mouse, keyboard, touch, scroll)
- Shows a warning modal after 10 minutes of inactivity
- Automatically logs out the user after 2 minutes if they don't respond to the warning
- Provides a countdown timer in the warning modal

### TimeoutWarningModal
A modal component that displays when the session is about to timeout. It:
- Shows a countdown timer
- Provides options to stay logged in or log off
- Uses Ant Design components for consistent styling

## Configuration

The timeout settings can be configured in `cvat-ui/src/config.tsx`:

```typescript
const SESSION_WARNING_TIMEOUT = 10 * 60 * 1000; // 10 minutes
const SESSION_LOGOUT_TIMEOUT = 2 * 60 * 1000;   // 2 minutes after warning
const SESSION_COUNTDOWN_INTERVAL = 1000;        // 1 second countdown interval
```

## Usage

The TimeoutLogic component is automatically integrated into the main CVAT application in `cvat-ui/src/components/cvat-app.tsx`. It only activates when a user is logged in.

## Features

- **Activity Detection**: Monitors mouse movements, keyboard presses, touch events, and scrolling
- **Warning System**: Shows a modal with countdown before automatic logout
- **User Control**: Users can choose to stay logged in or log off
- **Automatic Logout**: Forces logout after the countdown expires
- **Configurable**: Timeout durations can be easily adjusted
- **Clean Integration**: Uses existing CVAT authentication and styling

## Event Types Monitored

- `keypress` - Keyboard activity
- `mousemove` - Mouse movement
- `mousedown` - Mouse clicks
- `scroll` - Page scrolling
- `touchmove` - Touch device activity
- `pointermove` - Pointer device activity

## Dependencies

- React
- React Redux
- Ant Design
- React Modal
- CVAT Core (for authentication)