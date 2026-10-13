id: socket-server-single-to-thread-per-connection-conversion
type: pattern
area: general
perspective: the-coder
created: 1787509413.437909
---

Pattern: Converting a single-threaded accept-loop socket server (accept -> handle -> close, one connection at a time) to thread-per-connection needs three specific changes beyond just wrapping the handler in threading.Thread: (1) a handler-initiated shutdown (op returns "stop the server" as a value) must become a threading.Event set from the handler thread and checked by the main loop, not a direct return value, since the main loop no longer directly receives the handler's return; (2) if the main loop blocks in accept() with a timeout for idle-polling, a shutdown request needs to wake it immediately rather than wait out the poll interval -- have the handler thread open a throwaway client connection to the server's own socket right after setting the stop event, which unblocks accept() on the next loop check; (3) any "last activity" timestamp used for idle-timeout should stay owned by the single accept-loop thread (updated when a connection is accepted, not when a handler finishes) rather than shared across handler threads -- a new connection arriving is itself the activity signal, so this needs no lock at all if you frame it that way instead of trying to synchronize completion times.
When: Adding concurrency to a long-lived unix-socket/TCP daemon that currently serializes all requests through one accept loop.
Why: Naive thread-per-connection conversions either lose the graceful-shutdown path (return value never reaches the loop) or make shutdown laggy (bounded by the idle-poll timeout) or introduce needless synchronization on state that didn't actually need to be shared.