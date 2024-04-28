# Do not touch any of this if you don't /have/ to!

# Todo: 
    # clean up error handling
    # clean up handshake  

import asyncio
import random
import json
import time
from enum import Enum

debug = True # Set to True to enable debug messages
session_id = random.randint(0, 10000) # Random session ID. Used so that clients don't keep their ID across sessions. Oops has a chance of 1/10000 to fail

def format_command_message(command, flag = -1, value = -1): # Format: JSON
    return json.dumps({
        "command": command,
        "flag": flag,
        "value": value
    })

class ClientReturnCodes(Enum):
    READ_WRITE_SUCCESS = 0
    CLIENT_DISCONNECTED = 1
    ERR_INVALID_MESSAGE = 2
    ERR_INVALID_CLIENT_ID = 3

class ClientData:
    def __init__(self, my_id, reader, writer):
        self.active = True
        self.my_id = my_id
        self.reader = reader
        self.writer = writer
        self.readings = {}
        self.initialize_readings()
    
    def initialize_readings(self): # Also used to reset data
        self.readings = {
            "timestamp": [],
            "accel_x": [],
            "accel_y": [],
            "accel_z": [],
            "gyro_x": [],
            "gyro_y": [],
            "gyro_z": []
        }

class connection_handler:
    #Constructor
    def __init__(self):
        pass

    #

    #Private variables. These are not meant to be accessed from outside the class.
    _client_count = 0
    _clients = {}
    _dropped_clients = []

    #

    #Private methods. These are not meant to be called from outside the class.

    async def _read_from_client(self, client):
        data = await client.reader.read(1024)  # Adjust buffer size if needed
        if not data:  # Client has disconnected
            print("\nClient disconnected: ")
            print(client.writer.get_extra_info('peername'))
            return ClientReturnCodes.CLIENT_DISCONNECTED
            
        message = data.decode()
        if debug: print(f"Received message: {message}")

        return await self._save_data(client.my_id, message)

    async def _save_data(self, my_id, message): # Saves to client object, NOT database!
        try:
            message_json = json.loads(message)
            for key in message_json: # Todo add another for loop in case of multiple transmissions in buffer
                if debug: print(f"Key: {key}, Value: {message_json[key]}")
                self._clients["client_" + str(my_id)].readings[key].append(message_json[key])
            return ClientReturnCodes.READ_WRITE_SUCCESS
        
        except:
            print("Erroneous message: Invalid format.")
            return ClientReturnCodes.ERR_INVALID_MESSAGE

    async def _create_client(self, reader, writer): # Create client object
        my_id = self._client_count # Assign ID before incrementing because of zero-based indexing
        self._client_count += 1       
        
        self._clients["client_" + str(my_id)] = ClientData(my_id, reader, writer)
        print(f"New client added: {writer.get_extra_info('peername')}")
        
        writer.write(("{\"command\": \"set_id\", \"value\":" + str(my_id) + "}").encode())
        await writer.drain()

        await asyncio.sleep(0.1)

        writer.write(("{\"command\": \"set_session_id\", \"value\":" + str(session_id) + "}").encode())
        await writer.drain()
        
        print("_create_client: Returning my_id " + str(my_id))
        return my_id
    
    async def _request_id(self, reader, writer):

        print("Requesting ID.")
        writer.write("{\"command\": \"request_id\"}".encode())
        await writer.drain()

        await asyncio.sleep(0.5)

        data = await reader.read(1024)
        message = data.decode()
        if debug: print(f"Received id reply: {message}")
        
        # ID reply: "session_id, client_id"
        try:
            session_id_reply, client_id_reply = message.split(",")
        except:
            print("Invalid reply during request_id: " + message)
            return "invalid_reply"
        
        try:
            if int(session_id_reply) != session_id:
                print("Session ID mismatch. Assigning new ID.")
                print(f"(Session ID: {session_id}, Received session ID: {session_id_reply})")
                return "-1,-1"
        except:
            print("Invalid session ID reply: " + session_id_reply)
            return "invalid_reply"

        return int(client_id_reply)

    async def _initialize_client(self, reader, writer): # Initialization routine: handshake and create client object
        my_id = -1 # Default value, should be easy to catch if something goes wrong

        await asyncio.sleep(0.5)

        id_reply = await self._request_id(reader, writer)
        if debug: print(f"ID reply: {id_reply}")

        if id_reply == "-1,-1": # New client
            if debug: print("_initialize_client: New client detected.")
            my_id = await self._create_client(reader, writer) # Also sends ID to client

            for i in range(3):
                await asyncio.sleep(0.5)
                my_id_reply = await self._request_id(reader, writer)
                if my_id_reply == my_id:
                    return my_id
            
        else:                   # Reconnecting client
            try:
                if int(id_reply) in self._dropped_clients:
                    my_id = int(id_reply)
                    self._clients["client_" + str(my_id)].reader = reader
                    self._clients["client_" + str(my_id)].writer = writer
                    print(f"Client reconnected: " + my_id)
                    return my_id
                else:
                    print("Client ID not found. Assigning new ID.")
                    my_id = await self._create_client(reader, writer)
                    if await self._request_id(reader, writer) == my_id:
                        return my_id
            except:
                print("Invalid reply during handshake: " + id_reply)
            
        return -1
        
    #
    
    # Debug
    def dump_client_data(self, client_id):
        print(f"Client ID: {self._clients['client_' + str(client_id)].my_id}")
        print(f"Readings: {self._clients['client_' + str(client_id)].readings}")

    #Public methods
    async def handle_client(self, reader, writer): # Main routine to handle an incoming connection
        # Initialize client
        if debug: print("Client init...")
        while True:
            my_id = await self._initialize_client(reader, writer)
            print("--- MY ID: " + str(my_id))
            if my_id != -1:
                break
            await asyncio.sleep(0.1)
        
        if debug: print("Init success!")

        # Main loop for reading sensors from client
        writer.write(format_command_message(command = "start").encode())
        await writer.drain()
        if debug: print("Started")
        while True:
            if await self._read_from_client(self._clients["client_" + str(my_id)]) == ClientReturnCodes.CLIENT_DISCONNECTED:
                self._dropped_clients.append(my_id)
                break

        # Past here: Client has disconnected
        if debug: self.dump_client_data(my_id)
        writer.close()

    # reset_client_data: Use this when you want to start reading from the client (e.g. the client has been activated)
    async def reset_client_data(self, client_id): # client_id must be a string with the following format: "client_(int)"
        if client_id in self._clients:
            self._clients[client_id].initialize_readings()
            if debug: print(f"Client {client_id} data reset")
            return ClientReturnCodes.READ_WRITE_SUCCESS
        else:
            print("ERROR: Tried to reset data for an invalid client ID: " + client_id)
            return ClientReturnCodes.ERR_INVALID_CLIENT_ID

    # send_to_client: Use this to send commands. See commands.txt for a list of commands.
    async def send_to_client(self, client_id, message): # client_id must be a string with the following format: "client_(int)"
        if client_id in self._clients:
            if debug: print(f"Sending message to client {client_id}: {message}")
            self._clients[client_id].writer.write(message.encode()) # Warning: currently contains no writer error handling
            await self._clients[client_id].writer.drain()
            return ClientReturnCodes.READ_WRITE_SUCCESS
        else:
            print("ERROR: Tried to send message to an invalid client ID: " + client_id)
            return ClientReturnCodes.ERR_INVALID_CLIENT_ID
    
    async def get_IDs(self):
        return self._clients.keys()
    
    async def get_connected(self, client_id):
        return client_id not in self._dropped_clients
    
    async def get_last_reading(self, client_id):
        reading = {
            "timestamp": self._clients[client_id].readings["timestamp"][-1],
            "accel_x": self._clients[client_id].readings["accel_x"][-1],
            "accel_y": self._clients[client_id].readings["accel_y"][-1],
            "accel_z": self._clients[client_id].readings["accel_z"][-1],
            "gyro_x": self._clients[client_id].readings["gyro_x"][-1],
            "gyro_y": self._clients[client_id].readings["gyro_y"][-1],
            "gyro_z": self._clients[client_id].readings["gyro_z"][-1]
        }
        return reading

    async def get_all_readings(self, client_id):
        return self._clients[client_id].readings

    async def set_gameplay_state(self, client_id, state): # Wrapper for send_to_client
        if state in ["idle", "active"]:
            self.send_to_client(client_id, f"set_gameplay_state {state}")
        else:
            print("Invalid gameplay state: " + state)
    
    #
    
    #Simulation routine for debugging
    async def command_simulator(self) : # Periodically send messages to clients
        while True:
            print("Command simulator: Rolling the die...")

            # RNG to simulate spontaneous message sending. Adjust the range as needed
            for i in range(len(self.clients)):
                if (random.randint(0, 10) == 0):
                    print(f"Sending message to client {i}")
                    await self.send_to_client(i, f"Message {i}")

            await asyncio.sleep(1)  # Adjust the sleep duration as needed