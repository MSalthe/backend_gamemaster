import asyncio
import time
import random
import connection_handler as connection_handler_

# Replace hostname and port if needed
IP = 'localhost'
PORT = 5001

async def main():

    # Client server initialization
    client_handler = connection_handler_.connection_handler() # This is mad ugly, consider renaming file
    server = await asyncio.start_server(client_handler.handle_client, IP, PORT)  
    print(f'Serving on {server.sockets[0].getsockname()}')

    # I am not sure whether this blocks further async execution. If it does, you might have to run this as a separate thread.
    async with server:
        await server.serve_forever()

    # Start Game Master here. 
    # Only global variables and a main routine! Don't put any other code here pls. Keep main() clean.
    # Run it as an asyncio task so that it runs concurrently with the client handler.
    # Remember to pass the client_handler object to the Game Master program as a parameter. 
    # This way you can access the public methods like send_to_client from the Game Master program.
    #
    #
    #

    # Start new backend thread here to handle communication with front end. 
    # Only global variables and a main routine! Don't put any other code here pls. Keep main() clean.
    # Run it as a separate thread so that it runs concurrently with the Game Master.
    # You shouldn't have to pass the client_handler to this thread, but you might have to pass the Game Master object.
    #
    #
    #

# Do not touch this line under any circumstances!
asyncio.run(main())