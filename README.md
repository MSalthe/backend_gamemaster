## client_simulator.py:
- Simulates a client, "sokkel". As long as the client handler is not changed, it should start transmitting as soon as it is run.
- Remember to check hostname and port, they must correspond with what is defined in main.py.

## connection_handler.py:
- Handles incoming connections asynchronously.
- Has getters and setters, use them.
- Does not run on its own, you must run main.py.

## main.py:
- Should spawn all relevant routines and threads. 
- **Don't make a mess of it**, save your modules as separate .py files, import them in main and run your program's main routine as a asyncio coroutine or a thread.


## Relevant repos:
- Front end + back end example: https://github.com/MSalthe/web_gruppe4_elsys2
- Client code (not up to date with current client handler): https://github.com/MSalthe/sokkelkode
