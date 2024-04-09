# For simulating a sokkel client. Run independently from the main program.
# Ensure that the server is running before starting this program, 
# and that the server is listening on the correct IP and port.

import asyncio
import random
import time
import json

async def receive_data(reader):
    while True:
        data = await reader.read(100)
        if data:
            print(f'Received: {data.decode().strip()}')

async def send_data(writer):
    while True:

        datastructure = {
            "timestamp": time.time(),
            "accel_x": random.randint(-100, 100),
            "accel_y": random.randint(-100, 100),
            "accel_z": random.randint(-100, 100),
            "gyro_x": random.randint(-100, 100),
            "gyro_y": random.randint(-100, 100),
            "gyro_z": random.randint(-100, 100)
        }

        random_number_string = json.dumps(datastructure)
        writer.write(f'{random_number_string}\n'.encode())
        print("Sent data")
        await asyncio.sleep(0.1)  # Add a delay if needed

async def connect_to_server():
    reader, writer = await asyncio.open_connection('localhost', 5001)

    print("Waiting for connection acknowledgement")
    data = await reader.read(100)
    print(f'Received: {data.decode().strip()}')

    if data.decode().strip() == "request_id":
        writer.write("new_id".encode())
    
    time.sleep(1)

    await asyncio.gather(
        receive_data(reader),
        send_data(writer)
    )

    print('Closing the connection')
    writer.close()
    await writer.wait_closed()

asyncio.run(connect_to_server())