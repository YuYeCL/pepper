from pepper.framework.abstract import *
from pepper import logger

from time import sleep


class AbstractApplication(AbstractComponent):
    """
    The Application class is at the base of every robot application.
    It keeps track of events from different instances of :class:`~pepper.framework.abstract.component.AbstractComponent`
    and allows for instances of :class:`~pepper.framework.abstract.intention.AbstractIntention` to be build in top of it.

    Parameters
    ----------
    backend: AbstractBackend
        Application :class:`~pepper.framework.abstract.backend.AbstractBackend`
    """

    _EVENT_TAG = 'on_'

    def __init__(self, backend):
        super(AbstractApplication, self).__init__(backend)

        # Find Events associated with Application (inherited from Components)
        self._events = {k: v for k, v in self.__dict__.items() if k.startswith(self._EVENT_TAG) and callable(v)}

        self._log = logger.getChild(self.__class__.__name__)
        self.log.debug("Booted")

    @property
    def log(self):
        """
        Application Logger

        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def camera(self):
        # type: () -> AbstractCamera
        return self.backend.camera

    @property
    def microphone(self):
        # type: () -> AbstractMicrophone
        return self.backend.microphone

    @property
    def text_to_speech(self):
        # type: () -> AbstractTextToSpeech
        return self.backend.text_to_speech

    @property
    def motion(self):
        # type: () -> AbstractMotion
        return self.backend.motion

    @property
    def led(self):
        # type: () -> AbstractLed
        return self.backend.led

    def run(self):
        """
        Run Application

        Starts Camera & Microphone and Runs until KeyboardInterrupt
        """
        self.backend.camera.start()
        self.backend.microphone.start()

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            exit(0)

    def _reset_events(self):
        """Reset Event Callbacks to their (unimplemented) defaults"""
        for event_name, event_function in self._events.items():
            self.__setattr__(event_name, event_function)
