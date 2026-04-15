import asyncio
import base64
import json
import websockets
import os
from dotenv import load_dotenv
from appointment_functions import FUNCTION_MAP

load_dotenv()


# 🧠 Language Detection (for logging + future use)
def detect_language(text):
    text = text.lower()

    hindi_words = [
        "hai", "haan", "nahi", "kya", "kaise", "mujhe",
        "aap", "kal", "baje", "chahiye", "karna", "naam"
    ]

    for word in hindi_words:
        if word in text:
            return "hi"

    return "en"


# 🔌 Connect to Deepgram Agent
def sts_connect():
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise Exception("DEEPGRAM_API_KEY not found")

    return websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token", api_key]
    )


# 📄 Load config
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


# ⚙️ Execute function calls
def execute_function_call(func_name, arguments):
    if func_name in FUNCTION_MAP:
        result = FUNCTION_MAP[func_name](**arguments)
        print(f"Function call result: {result}")
        return result
    else:
        return {"error": f"Unknown function: {func_name}"}


# 🔁 Create response for function calls
def create_function_call_response(func_id, func_name, result):
    return {
        "type": "FunctionCallResponse",
        "id": func_id,
        "name": func_name,
        "content": json.dumps(result)
    }


# ⚙️ Handle function call requests
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


# 🧠 Handle text messages (NO INVALID MESSAGE SENDING)
async def handle_text_message(decoded, session_state):

    if decoded["type"] == "ConversationText" and decoded["role"] == "user":

        user_text = decoded["content"]

        # 🔥 Detect + lock language (ONLY for logging/future use)
        if not session_state.get("language"):
            lang = detect_language(user_text)
            session_state["language"] = lang
            print(f"[LANG LOCKED]: {lang}")


# 📤 Send audio to Deepgram
async def sts_sender(sts_ws, audio_queue):
    while True:
        chunk = await audio_queue.get()
        await sts_ws.send(chunk)


# 📥 Receive from Deepgram
async def sts_receiver(sts_ws, twilio_ws, streamsid_queue, session_state):
    streamsid = await streamsid_queue.get()

    async for message in sts_ws:

        if isinstance(message, str):
            print(message)
            decoded = json.loads(message)

            # 🧠 Handle language detection
            await handle_text_message(decoded, session_state)

            # ⚙️ Handle function calls
            if decoded["type"] == "FunctionCallRequest":
                await handle_function_call_request(decoded, sts_ws)

            continue

        # 🔊 Forward audio to Twilio
        raw_mulaw = message

        media_message = {
            "event": "media",
            "streamSid": streamsid,
            "media": {
                "payload": base64.b64encode(raw_mulaw).decode("ascii")
            }
        }

        await twilio_ws.send(json.dumps(media_message))


# 📥 Receive audio from Twilio
async def twilio_receiver(twilio_ws, audio_queue, streamsid_queue):
    BUFFER_SIZE = 20 * 160
    inbuffer = bytearray(b"")

    async for message in twilio_ws:
        try:
            data = json.loads(message)
            event = data["event"]

            if event == "start":
                streamsid = data["start"]["streamSid"]
                print("get our streamsid")
                streamsid_queue.put_nowait(streamsid)

            elif event == "media":
                chunk = base64.b64decode(data["media"]["payload"])

                if data["media"]["track"] == "inbound":
                    inbuffer.extend(chunk)

            elif event == "stop":
                break

            while len(inbuffer) >= BUFFER_SIZE:
                chunk = inbuffer[:BUFFER_SIZE]
                audio_queue.put_nowait(chunk)
                inbuffer = inbuffer[BUFFER_SIZE:]

        except:
            break


# 🔗 Main handler
async def twilio_handler(twilio_ws):
    audio_queue = asyncio.Queue()
    streamsid_queue = asyncio.Queue()
    session_state = {}   # 🔥 store language here

    async with sts_connect() as sts_ws:

        config_message = load_config()
        await sts_ws.send(json.dumps(config_message))

        await asyncio.wait([
            asyncio.ensure_future(sts_sender(sts_ws, audio_queue)),
            asyncio.ensure_future(sts_receiver(
                sts_ws, twilio_ws, streamsid_queue, session_state
            )),
            asyncio.ensure_future(twilio_receiver(
                twilio_ws, audio_queue, streamsid_queue
            )),
        ])

    await twilio_ws.close()


# 🚀 Start server
async def main():
    await websockets.serve(twilio_handler, "localhost", 8888)
    print("Started server in port 8888.")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())