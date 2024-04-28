import asyncio
import time
import random
import connection_handler as connection_handler_

# Replace hostname and port if needed
IP = '192.168.123.206'
PORT = 5050

async def main():

    # Client server initialization
    client_handler = connection_handler_.connection_handler() # This is mad ugly, consider renaming file
    try:
        server = await asyncio.start_server(client_handler.handle_client, IP, PORT)  
    except Exception as e:
        print(f'Failed to start server: {e}')
        return
    print(f'Serving on {server.sockets[0].getsockname()}')

    # I am not sure whether this blocks further async execution. If it does, you might have to run this as a separate thread.
    async with server:
        await server.serve_forever()

    await asyncio.gather(
        client_handler.command_simulator()
    )
    
    # Start Game Master here. 
    # Only global variables and a main routine! Don't put any other code here pls. Keep main() clean.
    # Run it as an asyncio task so that it runs concurrently with the client handler.
    # Remember to pass the client_handler object to the Game Master program as a parameter. 
    # This way you can access the public methods like send_to_client from the Game Master program.
    #
    #
    #

    print("Test")
    # Start new backend thread here to handle communication with front end. 
    # Only global variables and a main routine! Don't put any other code here pls. Keep main() clean.
    # Run it as a separate thread so that it runs concurrently with the Game Master.
    # You shouldn't have to pass the client_handler to this thread, but you might have to pass the Game Master object.
    #
    #
    #

# Do not touch this line under any circumstances!
asyncio.run(main())