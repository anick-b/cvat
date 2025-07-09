# Session Timeout Feature Implementation Guide

This guide provides step-by-step instructions for implementing the session timeout feature in CVAT.

## Overview

The session timeout feature automatically logs out users after a period of inactivity. It includes:
- Activity monitoring (mouse, keyboard, touch, scroll events)
- Warning modal with countdown timer
- Automatic logout after countdown expires
- User option to stay logged in

## Files Created/Modified

### 1. Event Listener Utility
**File**: `cvat-ui/src/utils/eventListenerUtil.ts`
- Monitors user activity events
- Provides functions to add/remove event listeners

### 2. Timeout Warning Modal
**File**: `cvat-ui/src/components/timeoutLogic/TimeoutWarningModal.tsx`
- Displays warning modal with countdown
- Uses Ant Design components for consistent styling
- Provides stay logged in/log off options

### 3. Timeout Logic Component
**File**: `cvat-ui/src/components/timeoutLogic/TimeoutLogic.tsx`
- Main component managing timeout logic
- Handles timeout creation and cleanup
- Manages modal state and countdown

### 4. Configuration
**File**: `cvat-ui/src/config.tsx`
- Added timeout configuration constants
- Configurable warning and logout timeouts

### 5. Main App Integration
**File**: `cvat-ui/src/components/cvat-app.tsx`
- Integrated TimeoutLogic component
- Only active when user is logged in

### 6. Index File
**File**: `cvat-ui/src/components/timeoutLogic/index.ts`
- Exports components for easy importing

## Configuration Options

The timeout behavior can be configured in `cvat-ui/src/config.tsx`:

```typescript
const SESSION_WARNING_TIMEOUT = 10 * 60 * 1000; // 10 minutes
const SESSION_LOGOUT_TIMEOUT = 2 * 60 * 1000;   // 2 minutes after warning
const SESSION_COUNTDOWN_INTERVAL = 1000;        // 1 second countdown interval
```

## How It Works

1. **Activity Monitoring**: The system monitors user activity through various events:
   - `keypress` - Keyboard activity
   - `mousemove` - Mouse movement
   - `mousedown` - Mouse clicks
   - `scroll` - Page scrolling
   - `touchmove` - Touch device activity
   - `pointermove` - Pointer device activity

2. **Warning Phase**: After 10 minutes of inactivity:
   - Warning modal appears with countdown timer
   - User has 2 minutes to respond
   - Countdown shows remaining time

3. **User Response**: User can:
   - Click "Stay Logged In" to reset the timeout
   - Click "Log Off" to logout immediately
   - Do nothing and be automatically logged out

4. **Automatic Logout**: If user doesn't respond within 2 minutes:
   - User is automatically logged out
   - Redirected to login page

## Integration Points

### Authentication
- Uses existing `logoutAsync` action from `actions/auth-actions`
- Integrates with CVAT's authentication system
- Redirects to login page after logout

### UI Components
- Uses Ant Design Modal, Button, Space, and Text components
- Follows CVAT's design patterns and styling
- Responsive and accessible

### State Management
- Uses React hooks for local state management
- Integrates with Redux for authentication actions
- Proper cleanup on component unmount

## Testing the Implementation

1. **Start the CVAT application**
2. **Log in to the system**
3. **Wait for 10 minutes without any activity** (or temporarily reduce the timeout for testing)
4. **Verify the warning modal appears**
5. **Test the countdown timer**
6. **Test "Stay Logged In" functionality**
7. **Test "Log Off" functionality**
8. **Test automatic logout after countdown**

## Customization

### Changing Timeout Durations
Edit the constants in `cvat-ui/src/config.tsx`:

```typescript
// For testing (shorter durations)
const SESSION_WARNING_TIMEOUT = 30 * 1000; // 30 seconds
const SESSION_LOGOUT_TIMEOUT = 10 * 1000;  // 10 seconds

// For production (longer durations)
const SESSION_WARNING_TIMEOUT = 15 * 60 * 1000; // 15 minutes
const SESSION_LOGOUT_TIMEOUT = 5 * 60 * 1000;   // 5 minutes
```

### Adding More Event Types
Edit `cvat-ui/src/utils/eventListenerUtil.ts`:

```typescript
const eventTypes = [
  'keypress',
  'mousemove',
  'mousedown',
  'scroll',
  'touchmove',
  'pointermove',
  'wheel',        // Add wheel events
  'keydown',      // Add keydown events
];
```

### Customizing Modal Appearance
Edit `cvat-ui/src/components/timeoutLogic/TimeoutWarningModal.tsx`:

```typescript
// Change modal styling
className="cvat-modal-session-timeout custom-timeout-modal"

// Change button text
<Button type="primary" onClick={onRequestClose}>
    Continue Session
</Button>
```

## Troubleshooting

### Modal Not Appearing
- Check if user is logged in
- Verify timeout configuration values
- Check browser console for errors
- Ensure event listeners are properly attached

### Countdown Not Working
- Verify `SESSION_COUNTDOWN_INTERVAL` is set correctly
- Check for JavaScript errors in console
- Ensure interval cleanup is working properly

### Logout Not Working
- Verify `logoutAsync` action is properly imported
- Check Redux store configuration
- Ensure authentication state is properly managed

### Performance Issues
- Monitor event listener performance
- Consider throttling event handlers for high-frequency events
- Ensure proper cleanup of timeouts and intervals

## Security Considerations

1. **Client-Side Only**: This is a client-side implementation and should not be the only security measure
2. **Server-Side Timeout**: Implement server-side session timeout for additional security
3. **Token Expiration**: Ensure JWT tokens have appropriate expiration times
4. **HTTPS**: Always use HTTPS in production to protect session data

## Future Enhancements

1. **Server-Side Integration**: Add server-side session timeout validation
2. **User Preferences**: Allow users to configure their own timeout preferences
3. **Activity Detection**: Implement more sophisticated activity detection
4. **Notifications**: Add browser notifications before timeout
5. **Analytics**: Track timeout events for user behavior analysis