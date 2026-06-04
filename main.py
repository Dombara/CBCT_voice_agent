import asyncio
import base64
import json
import websockets
import os
from dotenv import load_dotenv
from appointment_functions import FUNCTION_MAP
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import Response

app = FastAPI()

load_dotenv()


 

#  Language Detection (for logging + future use)
# def detect_language(text):
#     text = text.lower()

#     hindi_words = [
#         "hai", "haan", "nahi", "kya", "kaise", "mujhe",
#         "aap", "kal", "baje", "chahiye", "karna", "naam"
#     ]

#     for word in hindi_words:
#         if word in text:
#             return "hi"

#     return "en"


#  Connect to Deepgram Agent
def sts_connect():
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise Exception("DEEPGRAM_API_KEY not found")

    return websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token", api_key]
    )


#  Load config
# def load_config():
#     with open("config.json", "r") as f:
#         return json.load(f)
# def load_config():
#     try:
#         with open("config.json", "r") as f:
#             return json.load(f)
#     except Exception as e:
#         raise Exception(f"Config load failed: {e}")


# def load_config(lang):
#     try:
#         file_name = "config_en.json" if lang == "en" else "config_hi.json"
#         with open(file_name, "r") as f:
#             return json.load(f)
#     except Exception as e:
#         raise Exception(f"Config load failed: {e}")
    
def load_config(file_name="config_en.json"):
    with open(file_name, "r") as f:
        return json.load(f)

# #  Execute function calls
# def execute_function_call(func_name, arguments):
#     if func_name in FUNCTION_MAP:
#         result = FUNCTION_MAP[func_name](**arguments)
#         print(f"Function call result: {result}")
#         return result
#     else:
#         return {"error": f"Unknown function: {func_name}"}

def execute_function_call(func_name, arguments):
    try:
        if func_name in FUNCTION_MAP:
            result = FUNCTION_MAP[func_name](**arguments)
            print(f"Function call result: {result}")
            return result
        else:
            return {"error": f"Unknown function: {func_name}"}
    except Exception as e:
        return {"error": str(e)}


#  Create response for function calls
def create_function_call_response(func_id, func_name, result):
    return {
        "type": "FunctionCallResponse",
        "id": func_id,
        "name": func_name,
        "content": json.dumps(result)
    }


#  Handle function call requests
async def handle_function_call_request(decoded, sts_ws):
    try:
        for function_call in decoded["functions"]:
            func_name = function_call["name"]
            func_id = function_call["id"]
            arguments = json.loads(function_call["arguments"])

            print(f"Function call: {func_name}, args: {arguments}")

            result = execute_function_call(func_name, arguments)

            function_result = create_function_call_response(
                func_id, func_name, result
            )

            await sts_ws.send(json.dumps(function_result))

    except Exception as e:
        print(f"Error calling function: {e}")


#  Handle text messages (NO INVALID MESSAGE SENDING)
# async def handle_text_message(decoded, session_state):

#     if decoded["type"] == "ConversationText" and decoded["role"] == "user":

#         user_text = decoded["content"]

#         #  Detect + lock language (ONLY for logging/future use)
#         if not session_state.get("language"):
#             lang = detect_language(user_text)
#             session_state["language"] = lang
#             print(f"[LANG LOCKED]: {lang}")
async def handle_text_message(decoded, session_state):

    if decoded["type"] == "ConversationText" and decoded["role"] == "user":

        user_text = decoded["content"]

        # ADD THIS LINE HERE
        print(f"[USER SAID]: {user_text}")

        # Detect + lock language
        # if not session_state.get("language"):
            # lang = detect_language(user_text)
            # session_state["language"] = lang
            # print(f"[LANG LOCKED]: {lang}")


#  Send audio to Deepgram
# async def sts_sender(sts_ws, audio_queue):
#     while True:
#         chunk = await audio_queue.get()
#         await sts_ws.send(chunk)
async def sts_sender(sts_ws, audio_queue):
    while True:
        chunk = await audio_queue.get()
        print(f"[SENDING AUDIO]: {len(chunk)} bytes")  # 👈 AD
        await sts_ws.send(chunk)


#  Receive from Deepgram
# async def sts_receiver(sts_ws, twilio_ws, streamsid, session_state):
#     # streamsid = await streamsid_queue.get()

#     async for message in sts_ws:

#         if isinstance(message, str):
#             print(message)
#             decoded = json.loads(message)

#             await handle_text_message(decoded, session_state)

#             #  Handle function calls
#             if decoded["type"] == "FunctionCallRequest":
#                 await handle_function_call_request(decoded, sts_ws)

#             continue

#         #  Forward audio to Twilio
#         raw_mulaw = message

#         media_message = {
#             "event": "media",
#             "streamSid": streamsid,
#             "media": {
#                 "payload": base64.b64encode(raw_mulaw).decode("ascii")
#             }
#         }

#         await twilio_ws.send(json.dumps(media_message))
# async def sts_receiver(sts_ws, twilio_ws, streamsid, session_state):
#     async for message in sts_ws:  # sts_ws is a websockets client — async for works here
#         if isinstance(message, str):
#             print(message)
#             decoded = json.loads(message)
#             await handle_text_message(decoded, session_state)
#             if decoded["type"] == "FunctionCallRequest":
#                 await handle_function_call_request(decoded, sts_ws)
#             continue

#         raw_mulaw = message
#         media_message = {
#             "event": "media",
#             "streamSid": streamsid,
#             "media": {
#                 "payload": base64.b64encode(raw_mulaw).decode("ascii")
#             }
#         }
#         await twilio_ws.send_text(json.dumps(media_message))  # ← send_text not send
async def sts_receiver(sts_ws, twilio_ws, streamsid, session_state):
    # streamsid = await streamsid_queue.get()
    print(f"[STREAM STARTED]: {streamsid}")

    async for message in sts_ws:
        if isinstance(message, str):
            print(message)
            decoded = json.loads(message)
            await handle_text_message(decoded, session_state)
            if decoded["type"] == "FunctionCallRequest":
                await handle_function_call_request(decoded, sts_ws)
            continue

        raw_mulaw = message
        media_message = {
            "event": "media",
            "streamSid": streamsid,
            "media": {
                "payload": base64.b64encode(raw_mulaw).decode("ascii")
            }
        }
        await twilio_ws.send_text(json.dumps(media_message))


#  Receive audio from Twilio
# async def twilio_receiver(twilio_ws, audio_queue, streamsid_queue):
#     BUFFER_SIZE = 20 * 160
#     inbuffer = bytearray(b"")

#     async for message in twilio_ws:
#         try:
#             data = json.loads(message)
#             event = data["event"]

#             if event == "start":
#                 streamsid = data["start"]["streamSid"]
#                 print("get our streamsid")
#                 streamsid_queue.put_nowait(streamsid)

#             elif event == "media":
#                 chunk = base64.b64decode(data["media"]["payload"])

#                 if data["media"]["track"] == "inbound":
#                     inbuffer.extend(chunk)

#             elif event == "stop":
#                 break

#             while len(inbuffer) >= BUFFER_SIZE:
#                 chunk = inbuffer[:BUFFER_SIZE]
#                 audio_queue.put_nowait(chunk)
#                 inbuffer = inbuffer[BUFFER_SIZE:]

#         except Exception as e:
#             print(f"Twilio receiver error: {e}")
#             break
async def twilio_receiver(twilio_ws, audio_queue, streamsid_queue, session_state):
    print("[RECEIVER STARTED]")
    BUFFER_SIZE = 20 * 160
    inbuffer = bytearray(b"")

    try:
        while True:
            message = await twilio_ws.receive_text()
            data = json.loads(message)
            event = data.get("event")

            if event == "connected":
                print("[CONNECTED]")

            elif event == "start":
                streamsid = data["start"]["streamSid"]
                streamsid_queue.put_nowait(streamsid)
                params = data["start"].get("customParameters", {})
                lang = params.get("lang", "en")
                session_state["language"] = lang
                print(f"[LANG]: {lang}")

            elif event == "media":
                chunk = base64.b64decode(data["media"]["payload"])
                if data["media"]["track"] == "inbound":
                    inbuffer.extend(chunk)

            elif event == "stop":
                print("[CALL ENDED]")
                break

            while len(inbuffer) >= BUFFER_SIZE:
                chunk = inbuffer[:BUFFER_SIZE]
                audio_queue.put_nowait(chunk)
                inbuffer = inbuffer[BUFFER_SIZE:]

    except Exception as e:
        print(f"[RECEIVER ERROR]: {e}")



# #  Main handler

# async def twilio_handler(twilio_ws, lang="en"):
#     audio_queue = asyncio.Queue()
#     streamsid_queue = asyncio.Queue()
#     session_state = {}   #  store language here

#     async with sts_connect() as sts_ws:
#         #befor load config is called i give choice of language 
#         # config_message = load_config()
#         config_message = load_config(lang)

#         await sts_ws.send(json.dumps(config_message))

#         # await asyncio.wait([
#         # await asyncio.gather([
#         #     asyncio.ensure_future(sts_sender(sts_ws, audio_queue)),
#         #     asyncio.ensure_future(sts_receiver(
#         #         sts_ws, twilio_ws, streamsid_queue, session_state
#         #     )),
#         #     asyncio.ensure_future(twilio_receiver(
#         #         twilio_ws, audio_queue, streamsid_queue
#         #     )),
#         # ])
#         try:
#             await asyncio.gather(
#                 sts_sender(sts_ws, audio_queue),
#                 sts_receiver(sts_ws, twilio_ws, streamsid_queue, session_state),
#                 twilio_receiver(twilio_ws, audio_queue, streamsid_queue),
#             )
#         except Exception as e:
#             print(f"[ERROR]: {e}")

#     await twilio_ws.close()


# #  Start server
# async def main():

#     await websockets.serve(twilio_handler, "localhost", 8888)
#     print("Started server in port 8888.")
#     await asyncio.Future()


# if __name__ == "__main__":
#     asyncio.run(main())
# -----------------------------------
# 🔹 WEBSOCKET HANDLER (/twilio)
# -----------------------------------
# @app.websocket("/twilio")
# async def twilio_handler(twilio_ws: WebSocket):
#     print("[TWILIO WS CONNECTED]")
#     await twilio_ws.accept()

#     audio_queue = asyncio.Queue()
#     streamsid_queue = asyncio.Queue()
#     session_state = {}

#     try:
#         # 🎯 Start receiver FIRST (so it captures "start" event)
#         receiver_task = asyncio.create_task(
#             twilio_receiver(twilio_ws, audio_queue, streamsid_queue, session_state)
#         )

#         # 🎯 Wait until language is received
#         # while "language" not in session_state:
#         #     await asyncio.sleep(0.01)
#         streamsid = await streamsid_queue.get()
#         print(f"[STREAM STARTED]: {streamsid}")

#         # Now language is guaranteed to be set
#         lang = session_state.get("language", "en")
#         print(f"[LANG]: {lang}")

#         # 🎯 Load config dynamically
#         if lang == "hi":
#             config_message = load_config("hindi.json")
#         else:
#             config_message = load_config("english.json")

#         print("[CONFIG LOADED]")

#         # 🎯 Connect to STS
#         async with sts_connect() as sts_ws:
#             await sts_ws.send(json.dumps(config_message))

#             # await sts_ws.send(json.dumps({
#             #     "type": "ConversationText",
#             #     "role": "user",
#             #     "content": "start"
#             # }))

#             # 🎯 Run remaining pipeline
#             await asyncio.gather(
#                 sts_sender(sts_ws, audio_queue),
#                 sts_receiver(sts_ws, twilio_ws, streamsid, session_state),
#                 receiver_task,  # already running
#             )

#     except Exception as e:
#         print(f"[ERROR]: {e}")

#     await twilio_ws.close()

# @app.websocket("/twilio")
# async def twilio_handler(twilio_ws: WebSocket):
#     print("[TWILIO WS CONNECTED]")
#     await twilio_ws.accept()

#     audio_queue = asyncio.Queue()
#     streamsid_queue = asyncio.Queue()
#     session_state = {}

#     try:
#         async with sts_connect() as sts_ws:
#             # Load default config immediately, don't wait for lang
#             config_message = load_config("config_en.json")
#             await sts_ws.send(json.dumps(config_message))
#             print("[CONFIG SENT]")

#             await asyncio.gather(
#                 sts_sender(sts_ws, audio_queue),
#                 sts_receiver(sts_ws, twilio_ws, streamsid_queue, session_state),
#                 twilio_receiver(twilio_ws, audio_queue, streamsid_queue, session_state),
#             )

#     except Exception as e:
#         print(f"[ERROR]: {e}")

#     await twilio_ws.close()





# @app.websocket("/twilio")
# async def twilio_handler(twilio_ws: WebSocket):
#     print("[TWILIO WS CONNECTED]")
#     await twilio_ws.accept()

#     audio_queue = asyncio.Queue()
#     streamsid_queue = asyncio.Queue()
#     session_state = {}

#     try:
#         async with sts_connect() as sts_ws:
#             # Wait for streamsid AND language (set together in twilio_receiver on "start" event)
#             receiver_task = asyncio.create_task(
#                 twilio_receiver(twilio_ws, audio_queue, streamsid_queue, session_state)
#             )

#             streamsid = await streamsid_queue.get()
#             print(f"[STREAM STARTED]: {streamsid}")

#             lang = session_state.get("language", "en")
#             print(f"[LANG]: {lang}")

#             config_file = "config_hi.json" if lang == "hi" else "config_en.json"
#             config_message = load_config(config_file)
#             await sts_ws.send(json.dumps(config_message))
#             print(f"[CONFIG SENT]: {config_file}")

#             await asyncio.gather(
#                 sts_sender(sts_ws, audio_queue),
#                 sts_receiver(sts_ws, twilio_ws, streamsid_queue, session_state),
#                 receiver_task,
#             )

#     except Exception as e:
#         print(f"[ERROR]: {e}")

#     await twilio_ws.close()



@app.websocket("/twilio")
async def twilio_handler(twilio_ws: WebSocket):
    print("[TWILIO WS CONNECTED]")
    await twilio_ws.accept()

    audio_queue = asyncio.Queue()
    streamsid_queue = asyncio.Queue()
    session_state = {}

    try:
        # ✅ Start Twilio receiver FIRST
        receiver_task = asyncio.create_task(
            twilio_receiver(twilio_ws, audio_queue, streamsid_queue, session_state)
        )

        # ✅ Wait for stream start (this also sets language)
        streamsid = await streamsid_queue.get()
        print(f"[STREAM STARTED]: {streamsid}")

        # ✅ Get language
        lang = session_state.get("language", "en")
        print(f"[LANG]: {lang}")

        # ✅ Load correct config
        config_file = "config_hi.json" if lang == "hi" else "config_en.json"
        config_message = load_config(config_file)

        print(f"[CONFIG LOADED]: {config_file}")
        

        # ✅ Connect to Deepgram AFTER language is known
        async with sts_connect() as sts_ws:
            await sts_ws.send(json.dumps(config_message))
            print("[CONFIG SENT]")

            # await sts_ws.send(json.dumps({
            #     "type": "ConversationText",
            #     "role": "user",
            #     "content": "hello"
            # }))

            await asyncio.gather(
                sts_sender(sts_ws, audio_queue),
                sts_receiver(sts_ws, twilio_ws, streamsid, session_state),
                receiver_task,
                return_exceptions=True   # 🔥 VERY IMPORTANT
            )

    except Exception as e:
        print(f"[ERROR]: {e}")

    await twilio_ws.close()















@app.post("/select-language")
async def select_language(request: Request):
    form = await request.form()
    digit = form.get("Digits")

    if digit == "1":
        lang = "en"
        message = "You selected English."
    elif digit == "2":
        lang = "hi"
        message = "आपने हिंदी चुनी है।"
    else:
        lang = "en"
        message = "Invalid input. Defaulting to English."

    print(f"[USER INPUT]: {digit}")
    print(f"[LANGUAGE]: {lang}")

    #  Return TwiML to start stream
    twilio_stream_url = get_twilio_stream_url()

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Please wait while we connect you.</Say>
    <Connect>
        <Stream url="{twilio_stream_url}">
            <Parameter name="lang" value="{lang}" />
        </Stream>
    </Connect>
</Response>"""


    return Response(content=twiml.strip(), media_type="application/xml")




@app.get("/health")
async def health():
    return {"status": "ok"}




if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8888"))
    uvicorn.run(app, host="0.0.0.0", port=port)





# source .venv/bin/activate
