from flask              import Flask, jsonify, request
import Xlib.threaded

from flask_socketio     import SocketIO, send, emit, disconnect
from flask_socketio     import join_room, leave_room

from flask_cors         import CORS
from secrets            import token_hex
from uuid               import uuid4
from engineio.payload   import Payload

from .model             import Users, Connection_Bank
from .file_handler      import Details_Handler

app = Flask(__name__)
app.config['SECRET_KEY'] =  uuid4().hex + token_hex(32)
cors = CORS(app)
Payload.max_decode_packets = 500
socket = SocketIO(app, async_mode='gevent', engineio_logger=False)

users = Users()
connection = Connection_Bank()

user_store = Details_Handler()


# when the user connects
@socket.on("message")
def message(payload):
    check_user = users.get_devices_by_rid(payload['id'])

    if not check_user:
        users.create(
            sid = request.sid,
            typ = payload.get('type'),
            pwd = payload.get('pass'),
            rid = payload.get("id") if payload.get("id") else "12345"
        )
        user_store.new_connection('controller' if payload.get('type') == 'client' else 'device')

        if payload.get('type') == 'client':
            join_room('Clients')
            

        if payload.get('type') == 'desktop':
            send({
                "user" : users.return_desktop_type(),
                "message": "users list, message",
                "status": 200,
                "status_id": payload.get("id")
            }, room='Clients')

            send({
                'message': 'Connected successfully!',
                'status': 200,
            }, room=request.sid)

        else:
            send({
                "user" : users.return_desktop_type(),
                "message": "users list, message",
                "status": 200,
                "status_id": payload.get("id")
            }, room=request.sid)

    else:
        send({
            "status": 400,
            "message": "Please use another user ID as the one selected has already been used."
        }, room=request.sid)

# when the user disconnects
@socket.on('disconnect')
def disconnect():
    client = users.get_devices_by_sid(request.sid)
    if client:
        if client.typ == 'client':
            leave_room('Clients')

        user_store.rem_connection('controller' if client.typ == 'client' else 'device')
        users.remove_by_sid(request.sid)
    
    if connection.check_connection(request.sid):
        user_store.rem_connection('active')
        connection.remove_connection(request.sid)

    send({
        "user" : users.return_desktop_type(),
        "message": "users list for disconnection",
        "status": 200
    }, room='Clients')

# client trying to establish a connection with a clientdev
@socket.on('connect_users')
def connect_users(payload):
    check = users.check_user(payload.get('id'), payload.get('pwd'))
    if check:
        leave_room('Clients')
        conn = connection.create_connection(request.sid, check.sid)
        user_store.new_connection('active')
        
        if conn:
            emit("establish_connection", {
                "status": 200,
                "msg": f"establishing connection to user with rid: {check.rid}",
                'user': check.rid
            }, room=request.sid)

        else:
            emit("establish_connection", {
                "status": 400,
                "msg": f"establishing connection to user with rid: {check.rid}, user already connected to another device",
            }, room=request.sid)

    else:
        emit("establish_connection",{
            "status": 400,
            "msg": "Incorrect credentials provided!"
        }, room=request.sid)

# connection established confirmed by desktop
@socket.on('trigger_desktop')
def trigger_desktop(user):
    client = users.get_devices_by_sid(request.sid)
    dev_client = users.get_devices_by_rid(user)
    emit('establish_connection', {
        "status": 200,
        "msg": f"Connection established to user with rid: {client.rid}",
        "user": client.rid
    }, room=dev_client.sid)

@socket.on('streamer')
def streamer(payload):
    client = users.get_devices_by_rid(payload['user'])
    if client:
        emit("img_stream", payload['data'], room=client.sid)
    else:
        emit('client_deconnects',{
            "status": 400,
            "message": "Client unavaible!"
        }, room=request.sid)

@socket.on('received_signal')
def received_signal(data):
    pass

@app.errorhandler(Exception)
def error(err):
    try:
        return jsonify({
            'message': str(err),
            'status' : err.code
        }), err.code

    except:
        return jsonify({
            'message': str(err),
            'status' : 500
        }), 500
