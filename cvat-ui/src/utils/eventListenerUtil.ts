const eventTypes = [
  'keypress',
  'mousemove',
  'mousedown',
  'scroll',
  'touchmove',
  'pointermove'
];

export const addEventListeners = (listener: EventListener): void => {
  eventTypes.forEach((type) => {
    window.addEventListener(type, listener, false);
  });
};

export const removeEventListeners = (listener: EventListener): void => {
  if (listener) {
    eventTypes.forEach((type) => {
      window.removeEventListener(type, listener, false);
    });
  }
};