
# client.py


from gi.repository import GLib

from dasbus.connection import SessionMessageBus
from dasbus.loop import EventLoop

from common import SERVICE_NAME, OBJECT_PATH


def main():
    bus = SessionMessageBus()
    proxy = bus.get_proxy(SERVICE_NAME, OBJECT_PATH)

    def on_updated(field: str):
        print(f"[signal] Updated: {field}")

    proxy.Updated.connect(on_updated)

    event_loop = EventLoop()

    def do_demo_calls():
        print(f"GetNumber() -> {proxy.GetNumber()}")
        val = 1.25
        print(f"SetNumber({val}])")
        proxy.SetNumber(val)
        print(f"GetNumber() -> {proxy.GetNumber()}")

        print(f"GetText() -> {proxy.GetText()}")
        msg = "Hello World!"
        print(f"SetText(\"{msg}\")")
        proxy.SetText(msg)
        print(f"GetText() -> {proxy.GetText()}")

        print(f"GetSamples() -> {proxy.GetSamples()}")
        vals = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        print(f"SetSamples({vals})")
        proxy.SetSamples(vals)
        print(f"GetSamples() -> {proxy.GetSamples()}")
        val = 9.0
        print(f"AppendSample({val})")
        proxy.AppendSample(val)
        print(f"GetSamples() -> {proxy.GetSamples()}")

        # Quit after short delay to allow event_loop to process signal(s)
        GLib.timeout_add(300, event_loop.quit)      # Timeout in msec
        return False                                # Run once
    
    GLib.idle_add(do_demo_calls)
    event_loop.run()


if __name__ == "__main__":
    main()