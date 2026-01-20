
# server.py


import signal as py_signal

from dasbus.connection import SessionMessageBus
from dasbus.loop import EventLoop
from dasbus.server.interface import dbus_interface, dbus_signal
from dasbus.server.template import BasicInterfaceTemplate
from dasbus.signal import Signal
from dasbus.typing import Str, Double, List

from common import SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME


class DemoImplementation():
    """
    Pure Python implementation (business logic / state)
    """

    def __init__(self):
        self._number: Double = 0.0
        self._text: Str = ""
        self._samples: List[Double] = []

        self.updated = Signal()                                 # Internal signal (in process). Interface will re-emit it on D-Bus.

    # Get/set number
    def get_number(self) -> Double:
        return self._number
    
    def set_number(self, number: Double):
        self._number = float(number)
        self.updated.emit("number")

    # Get/set text
    def get_text(self) -> Str:
        return self._text
    
    def set_text(self, text: Str):
        self._text = str(text)
        self.updated.emit("text")
    
    # Get/set/append list of doubles
    def get_samples(self) -> List[Double]:
        return self._samples

    def set_samples(self, samples: List[Double]):
        self._samples = list(samples)
        self.updated.emit("samples")
    
    def append_sample(self, sample: Double):
        self._samples.append(sample)
        self.updated.emit("samples")


@dbus_interface(INTERFACE_NAME)
class DemoInterface(BasicInterfaceTemplate):
    """
    D-Bus interface proxying to DemoImplementation.

    Uses dasbus.server.template.BasicInterfaceTemplate, which the dasbus docs describe as a
    *recommended* pattern for defining interfaces as a proxy over a separate implementation object (above)
    (methods forward to implementation; signals are re-emitted on D-Bus).
    """

    # D-Bus uses an XML specification to define service interfaces, methods, signals and properties.
    # If we use dasbus type hints to annotate all Interface method args and return types, signal args and
    # properties, then dasbus will automatically generate the corresponding XML spec for us.
    # The XML spec can also be created manually, see here for side-by-side examples (HelloWorld class):
    # https://dasbus.readthedocs.io/_/downloads/en/latest/pdf/#page=41

    @dbus_signal
    def Updated(self, field: Str):
        """Emitted when any setter updates internal state"""
        pass

    def connect_signals(self):
        super().connect_signals()
        self.implementation.updated.connect(self.Updated.emit)  # When implementation emits, re-emit on D-Bus
    
    # Number
    def GetNumber(self) -> Double:
        return self.implementation.get_number()
    
    def SetNumber(self, number: Double):
        self.implementation.set_number(number)

    # Text
    def GetText(self) -> Str:
        return self.implementation.get_text()
    
    def SetText(self, text: Str):
        self.implementation.set_text(text)

    # Samples
    def GetSamples(self) -> List[Double]:
        return self.implementation.get_samples()
    
    def SetSamples(self, samples: List[Double]):
        self.implementation.set_samples(samples)

    def AppendSample(self, sample: Double):
        self.implementation.append_sample(sample)


def main():
    
    bus = SessionMessageBus()                       # See https://wiki.gentoo.org/wiki/D-Bus#The_session_bus for info on SystemMessageBus/SessionMesageBus
    bus.register_service(SERVICE_NAME)

    implementation  = DemoImplementation()          # Instantiate service Interface & Implementation
    interface       = DemoInterface(implementation)
    
    # interface.connect_signals()                   # In some older dasbus versions this needs to be called 'manually' pre-object-publication, otherwise
                                                    # BasicInterfaceTemplate will ensure this is called in derived classes.

    bus.publish_object(OBJECT_PATH, interface)      # Publish service to this D-Bus SessionMessageBus

    event_loop = EventLoop()                        # Instantiate EventLoop to handle signals

    def _stop(*_):                                  # *_ = Collect arbitrary number of positional args into tuple named '_', which is a typical
        event_loop.quit()                           # placeholder for 'unused'.
    
    py_signal.signal(py_signal.SIGINT, _stop)       # Hook up SIGINT & SIGTERM to handler that will call EventLoop.quit().
    py_signal.signal(py_signal.SIGTERM, _stop)      # Python signal handlers only run in the main Thread (top-level), so only install these once at the
                                                    # top level, then if needed have them call the .close() methods for any objects running in child Threads.

    print(f"Serving {SERVICE_NAME} at {OBJECT_PATH} on the Session bus.")

    event_loop.run()                                # Execution spins here in EventLoop until _stop() called


if __name__ == "__main__":
    main()