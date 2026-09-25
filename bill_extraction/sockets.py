import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")

sessions = {}


@sio.event
async def connect(sid, environ):
    print("\n\n==================== NEW CONNECTION ====================")
    print(f"Client {sid} connected")
    await sio.emit("message", {"data": "Welcome!"}, to=sid)
    print(f"Active Connections: {len(sessions)}")
    print("=========================================================\n")


@sio.event
async def mobile_connected(sid, data):
    print("\n\n=========== MOBILE CONNECTED ===========")

    home_session_id = data.get("homeSessionId")
    mobile_session_id = data.get("mobileSessionId")

    if home_session_id in sessions:
        sessions[home_session_id]["mobile_session_id"] = mobile_session_id

        await sio.emit("mobile_connected", {
            "data": "Mobile Connected!",
            "mobile_session_id": mobile_session_id
        }, to=home_session_id)

        print(
            f"Mobile ({mobile_session_id}) linked to Home ({home_session_id})")
    else:
        print(f"Home session {home_session_id} not found!")

    print(f"Updated Sessions: {sessions}")
    print("========================================\n")


@sio.event
async def session_closed(sid, data):
    print("\n\n=========== SESSION CLOSED ===========")
    mobile_session_id = data.get("mobileSessionId")
    sessionId = data.get("sessionId")

    if mobile_session_id and sessionId:
        await sio.emit("session_closed", {"message": "Session has been closed."}, to=mobile_session_id)
        del sessions[sessionId]
        print(f"Session {sessionId} has been closed.")
        print(f"Notified Mobile ({mobile_session_id}) about session closure.")

    print("========================================\n")


@sio.event
async def disconnect(sid):
    print("\n\n==================== DISCONNECTION ====================")
    session_id = sessions.get(sid)
    if session_id:
        print(f"Session {session_id}'s connection disconnected (SID: {sid})")
        del sessions[sid]
    else:
        print(f"No session ID found for SID: {sid}")
    print(f"Active Connections: {len(sessions)}")
    print("=========================================================\n")


@sio.event
async def register(sid, data):
    print("\n\n==================== NEW SESSION REGISTRATION ====================")
    """
    Handle the registration of a new session.
    """
    print(f"Registering new session: {data['session_id']}")

    home_session_id = data['session_id']
    if home_session_id not in sessions:
        sessions[home_session_id] = {
            "mobile_session_id": None}

    await sio.emit("message", {"data": f"Session {data['session_id']} registered!"}, to=sid)

    print(f"Registered Home Session: {home_session_id}")
    print(f"Current Sessions: {sessions}")
    print("=========================================================\n")

    return {"success": True, "message": f"Session {data['session_id']} registered!"}


@sio.event
async def send_message_to_session(sid, message):
    print("\n\n==================== SEND MESSAGE ====================")
    print("message value from frontend:", message)
    message_type = message.get("type", "text")
    session_id = message.get("session_id")
    uploaded_from = message.get("uploaded_from")
    file_type = message.get("file_type")

    if session_id:
        if message_type == "file":
            print("message type is file")
            file_url = message.get("message")
            if file_url:
                print("file url from frontend:", file_url)
                await sio.emit("message", {"data": "File uploaded", "url": file_url, "type": "file", "file_type": file_type, "session_id": session_id, 'uploaded_from': uploaded_from}, to=session_id)
                print(f"Sent file URL to session {session_id}: {file_url}")
            else:
                print("No file URL provided in the message.")
        else:
            text_message = message.get("message")
            if text_message:
                await sio.emit("message", {"data": text_message}, to=session_id)
                print(f"Sent message to session {session_id}: {text_message}")
            else:
                print("No text message provided.")
    else:
        print(f"Session {session_id} not found.")

    print("=========================================================\n")


@sio.event
async def remove_file_preview(sid, message):
    print("\n\n==================== REMOVE FILE PREVIEW ====================")
    session_id = message.get("session_id")
    remove_preview = message.get("remove_preview")
    await sio.emit("remove_file_preview", {"data": "File preview removed", "remove_preview": remove_preview}, to=session_id)
    print(f"Removed file preview for session {session_id}")
    print("=========================================================\n")
