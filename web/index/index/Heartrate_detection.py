import asyncio
import websockets
import json
import pymysql

async def send_temperature_humidity(websocket, path):
    try:
        db = pymysql.connect(
            host='47.121.193.122',
            user='root',
            password='123456',
            database='emqx_data',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = db.cursor()

        while True:
            query = 'SELECT * FROM temp_hum ORDER BY id DESC LIMIT 30;'
            cursor.execute(query)
            results = cursor.fetchall()

            temp_hum_data = [{
                'temperature': row['temp'],
                'humidity': row['hum']
            } for row in reversed(results)]

            print(f"Sending temperature/humidity data: {temp_hum_data}")
            await websocket.send(json.dumps({'temp_hum': temp_hum_data}))
            await asyncio.sleep(15)

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        cursor.close()
        db.close()

async def send_light_intensity(websocket, path):
    try:
        db = pymysql.connect(
            host='47.121.193.122',
            user='root',
            password='123456',
            database='emqx_data',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = db.cursor()

        while True:
            query = 'SELECT * FROM light_intensity ORDER BY id DESC LIMIT 30;'
            cursor.execute(query)
            results = cursor.fetchall()

            light_data = [row['light_intensity'] for row in reversed(results)]

            print(f"Sending light intensity data: {light_data}")
            await websocket.send(json.dumps({'light': light_data}))
            await asyncio.sleep(15)

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        cursor.close()
        db.close()

async def send_heart_rate(websocket, path):
    try:
        db = pymysql.connect(
            host='47.121.193.122',
            user='root',
            password='123456',
            database='emqx_data',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = db.cursor()

        while True:
            print(1)
            query = 'SELECT * FROM heart_rate ORDER BY id DESC LIMIT 30;'
            print(2)
            cursor.execute(query)
            print(3)
            results = cursor.fetchall()
            print(4)
            heart_rate_data = [row['heart_rate'] for row in reversed(results)]
            
            print(f"Sending heart rate data: {heart_rate_data}")
            await websocket.send(json.dumps({'heart_rate': heart_rate_data}))
            await asyncio.sleep(15)

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        cursor.close()
        db.close()

async def main():
    start_server1 = websockets.serve(send_heart_rate, "192.168.71.242", 6789)
    start_server2 = websockets.serve(send_light_intensity, "192.168.71.242", 6790)
    start_server3 = websockets.serve(send_temperature_humidity, "192.168.71.242", 6791)

    await asyncio.gather(start_server1, start_server2, start_server3)
    print("Heart rate WebSocket server started")
    print("Light intensity WebSocket server started")
    print("Temperature and humidity WebSocket server started")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()


# import asyncio
# import websockets
# import json
# import pymysql

# async def send_data(websocket, path, query, field_name):
#     try:
#         db = pymysql.connect(
#             host='47.121.193.122',
#             user='root',
#             password='123456',
#             database='emqx_data',
#             cursorclass=pymysql.cursors.DictCursor
#         )
#         cursor = db.cursor()

#         while True:
#             cursor.execute(query)
#             results = cursor.fetchall()

#             data = [row[field_name] for row in reversed(results)]

#             print(f"Sending {field_name} data: {data}")
#             await websocket.send(json.dumps({field_name: data}))
#             await asyncio.sleep(15)

#     except websockets.exceptions.ConnectionClosed as e:
#         print(f"Connection closed: {e}")
#     finally:
#         cursor.close()
#         db.close()

# async def main():
#     tasks = [
#         websockets.serve(lambda ws, path: send_data(ws, path, 'SELECT * FROM heart_rate ORDER BY id DESC LIMIT 30;', 'heart_rate'), "localhost", 6789),
#         websockets.serve(lambda ws, path: send_data(ws, path, 'SELECT * FROM light_intensity ORDER BY id DESC LIMIT 30;', 'light_intensity'), "localhost", 6790),
#         websockets.serve(lambda ws, path: send_data(ws, path, 'SELECT * FROM temp_hum ORDER BY id DESC LIMIT 30;', 'temp'), "localhost", 6791)
#     ]

#     await asyncio.gather(*tasks)
#     print("WebSocket servers started")

# if __name__ == "__main__":
#     asyncio.run(main())
