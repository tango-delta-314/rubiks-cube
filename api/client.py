import asyncio
import websockets
import json


async def cube():
  async with websockets.connect("ws://localhost:8765") as websocket:
    while True:
    
      moves = input("Enter moves (x to exit): ")
      
      if moves == "x":
        break

      message = json.dumps({
        "moves": moves,
        "solver": "first_block"}
      )
      
      await websocket.send(message)
      solution = await websocket.recv()
      print(f"Solution: {solution}")
      print()
    
    print("Exiting")

asyncio.run(cube())