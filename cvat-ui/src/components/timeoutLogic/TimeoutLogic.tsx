import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { logoutAsync } from 'actions/auth-actions';
import { addEventListeners, removeEventListeners } from 'utils/eventListenerUtil';
import { TimeoutWarningModal } from './TimeoutWarningModal';
import appConfig from 'config';

// Configuration constants
const WARNING_TIMEOUT = appConfig.SESSION_WARNING_TIMEOUT;
const LOGOUT_TIMEOUT = appConfig.SESSION_LOGOUT_TIMEOUT;
const COUNTDOWN_INTERVAL = appConfig.SESSION_COUNTDOWN_INTERVAL;

interface TimeoutLogicProps {
    enabled?: boolean;
}

export const TimeoutLogic: React.FC<TimeoutLogicProps> = ({ enabled = true }) => {
    const [isWarningModalOpen, setWarningModalOpen] = useState(false);
    const [remainingTime, setRemainingTime] = useState(0);
    const dispatch = useDispatch();

    const warningTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const countdownIntervalRef = useRef<NodeJS.Timeout | null>(null);
    const isWarningModalOpenRef = useRef(false);



    const clearAllTimeouts = useCallback(() => {
        if (warningTimeoutRef.current) {
            clearTimeout(warningTimeoutRef.current);
            warningTimeoutRef.current = null;
        }
        if (countdownIntervalRef.current) {
            clearInterval(countdownIntervalRef.current);
            countdownIntervalRef.current = null;
        }
    }, []);

    const startWarningTimeout = useCallback(() => {
        clearAllTimeouts();

        console.log('TimeoutLogic: Starting warning timeout for', WARNING_TIMEOUT / 1000, 'seconds');

        warningTimeoutRef.current = setTimeout(() => {
            console.log('TimeoutLogic: Warning timeout triggered - showing modal');
            setRemainingTime(LOGOUT_TIMEOUT / 1000); // Convert to seconds for display

            setWarningModalOpen(true);
            console.log('TimeoutLogic: setWarningModalOpen', isWarningModalOpen);
            // Start countdown

            countdownIntervalRef.current = setInterval(() => {
                setRemainingTime((prev) => {
                    const newTime = prev - 1;
                    console.log('TimeoutLogic: Countdown tick, remaining:', newTime, 'seconds');

                    if (newTime <= 0) {
                        console.log('TimeoutLogic: Countdown finished - logging out');
                        clearAllTimeouts();
                        dispatch(logoutAsync());
                        return 0;
                    }
                    return newTime;
                });
            }, 1000); // Up

            // date every second
        }, WARNING_TIMEOUT);
    }, [WARNING_TIMEOUT, LOGOUT_TIMEOUT, clearAllTimeouts, dispatch]);

    const handleUserActivity = useCallback(() => {
        if (!enabled) return;

        console.log('TimeoutLogic: User activity detected');

        if (isWarningModalOpenRef.current) {            // If modal is open, just reset the countdown
            console.log('---------------------------TimeoutLogic: isWarningModalOpen', isWarningModalOpen);

            console.log('TimeoutLogic: setRemainingTime countdown due to activity');
            setRemainingTime(LOGOUT_TIMEOUT / 1000);
        } else {
            // Reset the warning timeout
            console.log('---------------------------TimeoutLogic: isWarningModalOpen', isWarningModalOpen);

            console.log('TimeoutLogic: startWarningTimeout warning timeout due to activity');
            startWarningTimeout();
        }
    }, [enabled]);

    const handleStayLoggedIn = useCallback(() => {
        console.log('TimeoutLogic: User chose to stay logged in');
        setWarningModalOpen(false);
        setRemainingTime(0);
        clearAllTimeouts();
        startWarningTimeout(); // Restart the warning timeout
    }, [clearAllTimeouts, startWarningTimeout]);

    const handleLogout = useCallback(() => {
        console.log('TimeoutLogic: User chose to log out');
        setWarningModalOpen(false);
        setRemainingTime(0);
        clearAllTimeouts();
        dispatch(logoutAsync());
    }, [clearAllTimeouts, dispatch]);






    useEffect(() => {
        if (!enabled) {
            console.log('TimeoutLogic: Component disabled');
            clearAllTimeouts();
            return;
        }

        console.log('TimeoutLogic: Setting up timeout logic----------------');
        addEventListeners(handleUserActivity);
        startWarningTimeout();

        return () => {
            console.log('TimeoutLogic: Cleaning up');
            removeEventListeners(handleUserActivity);
            clearAllTimeouts();
        };
    }, [enabled, handleUserActivity ]);
    useEffect(() => {
        isWarningModalOpenRef.current = isWarningModalOpen;
    }, [isWarningModalOpen]);

    return (
        <TimeoutWarningModal
            isOpen={isWarningModalOpen}
            onRequestClose={handleStayLoggedIn}
            onLogout={handleLogout}
            remainingTime={remainingTime}
        />
    );
};