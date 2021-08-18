# Kullanılan paketler ve modüller --------------------------------

import os
from flask import url_for, redirect, request, jsonify, session, send_file
from pars.models import Queries, User, Biometric
from pars import createApp, db
from pars.initialize_db import createDB
import datetime
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from pathlib import Path
import requests
from datetime import date

# ------------------------------------------------------------------------------

# App run edilip DB çağırılıyor
# Ayrıca sqlalcheöy kullanımı için ilgili Queries classı çağırılıyor

app = createApp()
CORS(app)
createDB()
UPLOAD_FOLDER = 'static/uploads/'
queries = Queries()


# ------------------------------------------------------------------------------ JWT
# JWT decorator burada oluşturuldu
# Kod sessionda yarım saatliğine tutuluyor
# Önemli sayfalar için bu kodun oluşturulmuş olması gerekiyor
# Kod oluşturulmamış ise kullanıcının login olması gerekiyor
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if 'token' in session:
            token = session['token']
        elif 'token' in request.headers:
            token = request.headers['token']
        else:
            session['token'] = 'None'
            token = session['token']

        if token == 'None':
            return jsonify({'success': False, 'description': 'Please login the system..'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = queries.getOneUser(id=data['id'])
        except:
            return jsonify({'success': False, 'description': 'Please login the system..'}), 401
        return f(current_user, *args, **kwargs)
    return decorator
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------ SHIFT
# Vardiya verilerinin işlendiği ve tutulduğu fonksiyonlardır
@app.route('/api/shifts')
def apiShift():
    message = 'SHIFT NOT FOUND'

    try:
        results = queries.getAllShifts()
        resultArray = []

        if results != message:
            for shift in results:
                resultArray.append({
                    "id": shift.id,
                    "startTime": shift.startTime,
                    "endTime": shift.endTime,
                })

            result = {
                'shifts': resultArray
            }

            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'description': message})
    except Exception as e:
        return jsonify({'success': False, 'description': message, 'error': e})


# ONE -----------
# Verilen id ye sahip shift verisi döndürülüyor
@app.route('/shift/<int:id>')
def apiShiftOne(id):
    message = 'SHIFT NOT FOUND'

    try:
        shift = queries.getOneShiftById(id)

        if shift != message:
            result = {
                "id": shift.id,
                "startTime": shift.startTime,
                "endTime": shift.endTime,
            }

            if result['id'] != None or result['id'] != '':
                return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'description': message})
    except Exception as e:
        return jsonify({'success': False, 'description': message, 'error': e})

# ADD -----------
# POST isteği atıldığında request parametrelerle birlikte shift ekleniyor
@app.route('/addshift', methods=['GET', 'POST'])
def addShift():
    if request.method == 'POST':
        message = 'SHIFT COULDNT ADD'
        startTime = request.args.get('starttime')
        endTime = request.args.get('endtime')

        if startTime != '' and endTime != '':
            shift = {'startTime': startTime, 'endTime': endTime}

            try:
                queries.addShift(shift)
                message = 'Shift added successfully'

                return jsonify({'success': True, 'description': message})
            except Exception as e:
                return jsonify({'success': False, 'description': message, 'error': e})
        else:
            return jsonify({'success': False, 'description': message})
    else:
        return jsonify({'success': False})

# UPDATE -----------
# Parametrelerle var olan shiftin güncellenmesini sağlayan fonksiyon
@app.route('/shift/update/<int:id>', methods=['GET', 'POST'])
def updateShift(id):
    message = 'Error for update'

    if request.method == 'POST':
        try:
            updatedShift = queries.getOneShiftById(id)

            editedShift = {
                "startTime": request.args.get('starttime') or updatedShift.startTime,
                "endTime": request.args.get('endtime') or updatedShift.endTime,
            }

            queries.updateShift(id, editedShift)

            return jsonify({'success': True, 'shift': editedShift})
        except Exception as e:
            return jsonify({'success': False, 'description': message, 'error': e})
    else:
        try:
            shift = queries.getOneShiftById(id)

            return jsonify({'success': False, 'shift': shift, 'description': message})
        except Exception as e:
            return jsonify({'success': False, 'description': message, 'error': e})


# DELETE -----------
# Verilen id ye sahip shifti silen fonksiyon
@app.route('/delete/shift/delete/<int:id>')
def deleteShift(id):
    try:
        queries.deleteShift(id)

        return jsonify({'success': True, 'description': 'Successfully delete'})
    except Exception as e:
        return jsonify({'success': False, 'description': 'Error for delete shift', 'error': e})

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------ APIS
@app.route('/api')
def api():
    return '<a href="/api/users"> users </a> <br> <a href="/api/logs"> logs </a>'

# Frontend tarafında image ın görüntülenmesi için yazılan fonksiyon
@app.route('/getimage/<string:image>')
def get_image(image):
    pars_path = os.path.abspath('pars')
    path_image = str(Path(pars_path).parent) + '\\faces\\' + image

    return send_file(path_image)

# ------------------------------------------------------------------------------ LOGS
# Kullanıcıların temel işlemlerinin işlendiği kaydedildiği fonksiyonlar
# ALL -----------
@app.route('/api/logs')
def apiLogs():
    message = 'LOG NOT FOUND'

    try:
        logs = queries.getAllLogs()

        if logs != message:
            resultArray = []
            total = len(logs)

            for log in logs:
                resultArray.append({
                    "id": log.id,
                    "userid": log.userid,
                    "message": log.message
                })

            result = {
                'total': total,
                'logs': resultArray
            }

            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'description': message})
    except Exception as e:
        return jsonify({'success': False, 'description': message, 'error': e})

# ------------------------------------------------------------------------------ LOGS GATE
# Kullanıcının detection işlemlerinin işlendiği kaydedildiği fonksiyonlar
# ALL -----------
@app.route('/api/logsgate')
def apiLogsGate():
    message = 'LOGSGATE NOT FOUND'

    try:
        logs = queries.getAllLogsGate()

        resultArray = []

        if logs and logs != message:
            for log in logs:
                resultArray.append({
                    "id": log.id,
                    "userid": log.userid,
                    "day": log.day,
                    "intime": log.intime,
                    "outtime": log.outtime,
                    "deviceid": log.deviceid
                })

            result = {
                'logsGate': resultArray
            }

            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'description': message})
    except Exception as e:
        return jsonify({'success': False, 'description': message, 'error': e})

# UPDATE LOG -----------
# Kullanıcı gün içinde 2. veya daha fazla detect olmuşsa log kaydındaki çıkış zamanını burada güncelliyoruz
def updateLog(existsLog):
    try:
        queries.updateLoginLogout(existsLog.id)

        return jsonify({'success': True, 'description': 'CIKIS YAPILDI'})
    except Exception as e:
        return jsonify({'success': False, 'description': 'HATA', 'error': e})

# ------------------------------------------------------------------------------

# ADD -----------
# Detect edilen kullanıcıyı veritabanına ekleyen ve ya çıkış işlemini yapan fonksiyon
@app.route('/addloggate', methods=['GET', 'POST'])
def addLog():
    if request.method == 'POST':
        addedLog = {
            "userid": request.args.get('userid'),
            "day": date.today(),
            "time": datetime.datetime.now(),
            "deviceid": 2,
        }

        try:
            existsLog = queries.getOneLoginLogoutByDay(addedLog["userid"], addedLog["day"])

            if existsLog and existsLog != 'LOG NOT FOUND':
                return updateLog(existsLog)
            else:
                queries.loginLogout(addedLog["userid"], addedLog["day"], addedLog["time"], addedLog["time"], addedLog["deviceid"])

                return jsonify({'success': True, 'description': 'GIRIS YAPILDI'})
        except Exception as e:
            return jsonify({'success': False, 'description': 'HATA', 'error': e})
    else:
        return jsonify({'success': False, 'description': 'NOT A POST REQUEST'})

# ------------------------------------------------------------------------------


# ------------------------------------------------------------- USER
# Kullanıcı verilerinin işlenip tutlduğu fonksiyonlar
# ALL -----------
# Tüm kullanıcıların listesini döndüren fonksiyon
@app.route('/api/users')
@token_required
def apiUsers(current_user):
    message = "USER NOT FOUND"

    try:
        results = queries.getAllUsers()

        if results != message:
            resultArray = []

            for user in results:
                resultArray.append({
                    "id": user.id,
                    "name": user.name,
                    "tc": user.tc,
                    "image": user.image,
                    "shift": user.shift,
                })

            result = {
                'users': resultArray
            }

            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'description': message})
    except Exception as e:
        return jsonify({'success': False, 'description': message, 'error': e})


# API ONE -----------
# Verilen id ye göre kullanıcı kaydını döndüren fonksiyon
@app.route('/api/users/<int:id>')
def apiUser(id):
    message = 'USER NOT FOUND'

    try:
        user = queries.getOneUser(id)

        print("USER: ", user)

        if user != message and user != None:
            result = {
                "id": user.id,
                "name": user.name,
                "tc": user.tc,
                "image": user.image,
                "shift": user.shift
            }

            if result['id'] != None or result['id'] != '':
                return jsonify({'success': True, 'data': result})
            else:
                return jsonify({'success': False, 'description': message})
        else:
            return jsonify({'success': False, 'description': message})
    except Exception as e:
        return jsonify({'success': False, 'description': message, 'error': e})

# ONE -----------
# Id si verilen kullanıcının verilerini döndüren fonksiyon
@app.route('/user/<int:id>')
def user(id):
    message = 'USER NOT FOUND'

    try:
        user = queries.getOneUser(id)

        if user != message:
            userObj = {
                "id": user.id,
                "name": user.name,
                "tc": user.tc,
                "image": user.image,
                "shift": user.shift
            }

            if userObj['id'] != None or userObj['id'] != '':
                return jsonify({'success': True, 'user': userObj})
            else:
                return jsonify({'success': False, 'description': message})
        else:
            return jsonify({'success': False, 'description': message})
    except Exception as e:
        return jsonify({'success': False, 'description': message, 'error': e})


# DELETE -----------
# Id si verilen Kullanıcının activated verisini false yaparak kayıt dışına alan fonksiyon
@app.route("/delete/<int:id>")
def delete(id):
    try:
        queries.deleteUser(id)

        return jsonify({'success': True, 'description': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'description': 'HATA', 'error': e})

# REACTIVE USER -----------
# Id si verilen Kullanıcı daha önce kaydedilmiş ise activated verisini true yapıp yeni verilerle tekrar aktif eden fonksiyon
def reActive(id, oldUser, newUser):
    try:
        photo = request.data
        description = "ReActivated"

        editedUser = {
            "tc": newUser['tc'] or oldUser.tc,
            "name": newUser['name'] or oldUser.name,
            "shift": newUser['shift'] or oldUser.shift,
            "image": (newUser['tc'] or oldUser.tc) + ".png",
        }

        f = open("C:\\Users\\furkanyildiz\\Desktop\\FY\\PersonalProject\\faces\\" + editedUser['tc'] + ".png", "wb")
        f.write(photo)
        f.close()

        if oldUser.activated:
            description = "Updated"
        else:
            queries.updateUser(id, editedUser, True)

        return jsonify({'success': True, 'user': editedUser, 'description': description})
    except Exception as e:
        return jsonify({'success': False, 'description': 'HATA', 'error': e})

# UPDATE -----------
# Id verisi ile kayıtlı kullanıcı verilerini güncellendiği fonksiyon
@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update(id):
    try:
        if request.method == 'POST':
            updatedUser = queries.getOneUser(id)
            photo = request.data

            editedUser = {
                "tc": request.args.get('tc') or updatedUser.tc,
                "name": request.args.get('name') or updatedUser.name,
                "image": (request.args.get('tc') or updatedUser.tc) + ".png",
                "shift": request.args.get('shift') or updatedUser.shift
            }

            f = open("C:\\Users\\furkanyildiz\\Desktop\\FY\\PersonalProject\\faces\\" + editedUser["tc"] + ".png", "wb")
            f.write(photo)
            f.close()

            print('EDITED USER : ', editedUser)

            queries.updateUser(id, editedUser, True)

            return jsonify({'success': True, 'user': editedUser})
        else:
            user = queries.getOneUser(id)

            return jsonify({'success': False, 'user': user})
    except Exception as e:
        return jsonify({'success': False, 'description': 'HATA', 'error': e})

# REGISTER -----------
# Kullanıcıyı kaydetmek için kullanılan request parametrelerinin kullanıldığı fonksiyon
@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            name = request.args.get('name')
            tc = request.args.get('tc')
            shift = request.args.get('shift')
            photo = request.data

            existUser = queries.getOneUserByTc(tc)

            addedUser = {
                "tc": tc,
                "name": name,
                "image": tc + ".png",
                "shift": shift,
            }

            if existUser:
                return reActive(existUser.id, existUser, addedUser)

            f = open("C:\\Users\\furkanyildiz\\Desktop\\FY\\PersonalProject\\faces\\" + tc + ".png", "wb")
            f.write(photo)
            f.close()

            headers = {
                'Authorization': 'Bearer dY7d-vR6i'
            }

            url = 'http://46.197.140.92:65015/v1/face'
            files = {'photo': ("11111111111.jpg", photo, {'Expires': '0'})}
            data = {'meta': 'TEST', 'mf_selector': 'reject'}

            newUser = User(tc=tc, name=name, image=tc + ".png", shift=shift, activated=True)
            db.session.add(newUser)
            db.session.flush()

            with requests.Session() as s:
                response = s.post(url, headers=headers, files=files, data=data).json()

                if 'id' in str(response) and newUser.id:
                    biometricid = response['results'][0]['id']
                    newBiometric = Biometric(userid=newUser.id, deviceType=1, biometricid=biometricid)

                    db.session.add(newBiometric)
                    db.session.commit()

                    queries.sendLogMessage(newUser.id, 'USER ADDED', datetime.datetime.now(), 2)

                    return jsonify({'success': True, 'data': addedUser})
                elif 'No faces found on photo' in str(response):
                    return jsonify({'success': False, 'description': 'NO FACES'})
                else:
                    db.session.rollback()

                    return jsonify({'success': False, 'description': 'ERROR'})
        return jsonify({'success': False, 'description': 'ERROR'})
    except Exception as e:
        return jsonify({'success': False, 'description': 'ERROR', 'error': e})

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------ GATE
# Tarama yapılan bloklar üzerindeki kapıların verilerini tutup işleyen fonksiyonlardır
# ALL -----------
@app.route('/api/gates')
def apiGate():
    message = 'GATE NOT FOUND'

    try:
        results = queries.getAllGates()
        resultArray = []

        if results != message:
            for gate in results:
                resultArray.append({
                    "id": gate.id,
                    "name": gate.name,
                    "blockid": gate.blockid,
                })

            result = {
                'gates': resultArray
            }

            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': True, 'description': message})
    except Exception as e:
        return jsonify({'success': True, 'description': 'Hata', 'error': e})

# ONE -----------
# Id si verilen gate in verilerini getiren fonksiyon
@app.route('/api/gate/<int:id>')
def apiGateOne(id):
    message = 'GATE NOT FOUND'

    try:
        gate = queries.getOneGateById(id)

        if gate != message:
            result = {
                "id": gate.id,
                "name": gate.name,
                "blockid": gate.blockid,
            }

            if result['id'] != None or result['id'] != '':
                return jsonify({'success': True, 'data': result})
            else:
                return jsonify({'success': False, 'description': 'Hata'})
        else:
            return jsonify({'success': False, 'description': message})
    except Exception as e:
        return jsonify({'success': False, 'description': 'Hata', 'error': e})

# ADD -----------
# Yeni gate eklemek için kullanılan fonksiyon
@app.route('/addgate', methods=['GET', 'POST'])
def addGate():
    try:
        if request.method == 'POST':
            name = request.args.get('name')
            blockid = request.args.get('blockid')

            if name != '' and blockid != '':
                gate = {'name': name, 'blockid': blockid}
                queries.addGate(gate)

                return jsonify({'success': True, 'description': 'GATE ADDED SUCCESSFULLY'})
            else:
                return jsonify({'success': False, 'description': 'Hata'})
        else:
            return jsonify({'success': False, 'description': 'Hata'})
    except Exception as e:
        return jsonify({'success': False, 'description': 'Hata', 'error': e})


# UPDATE -----------
# Id si verilen gate i yeni verilerle güncelleyen fonksiyon
@app.route('/gate/update/<int:id>', methods=['GET', 'POST'])
def updateGate(id):
    message = 'GATE NOT FOUND'

    try:
        if request.method == 'POST':
            updatedGate = queries.getOneGateById(id)

            editedGate = {
                "name": request.args.get('name') or updatedGate.name,
                "blockid": request.args.get('blockid') or updatedGate.blockid,
            }

            queries.updateGate(id, editedGate)

            return jsonify({'success': True, 'data': editedGate})
        else:
            gate = queries.getOneGateById(id)

            if gate != message:
                return jsonify({'success': False, 'data': gate})
            else:
                return jsonify({'success': False, 'description': message})
    except Exception as e:
        return jsonify({'success': False, 'description': 'Hata', 'error': e})

# DELETE -----------
@app.route('/gate/delete/<int:id>')
def deleteGate(id):
    queries.deleteGate(id)

    return jsonify({'success': True})

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------ DEVICE
@app.route('/api/devices')
def apiDevices():
    results = queries.getAllDevices()
    resultArray = []

    for device in results:
        resultArray.append({
            "id": device.id,
            "name": device.name,
            "gateid": device.gateid,
            "typeid": device.typeid,
        })

    result = {
        'devices': resultArray
    }

    print("DEVICES RESULT --> ", result)

    return jsonify({'success': True, 'data': result})

# ONE -----------
@app.route('/api/device/<int:id>')
def apiDeviceOne(id):
    device = queries.getOneDeviceById(id)

    result = {
        "id": device.id,
        "name": device.name,
        "gateid": device.gateid,
        "typeid": device.typeid,
    }

    if result['id'] != None or result['id'] != '':
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'success': False})

# ADD -----------
@app.route('/adddevice', methods=['GET', 'POST'])
def addDevice():
    if request.method == 'POST':
        name = request.args.get('name')
        gateid = request.args.get('gateid')
        typeid = request.args.get('typeid')

        print("name  --> ", name)
        print("gateid --> ", gateid)
        print("typeid --> ", typeid)


        if name != '' and gateid != '' and typeid != '':
            device = {'name': name, 'gateid': gateid, 'typeid': typeid}
            queries.addDevice(device)

            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
    else:
        return jsonify({'success': False})

# UPDATE -----------
@app.route('/device/update/<int:id>', methods=['GET', 'POST'])
def updateDevice(id):
    if request.method == 'POST':
        updatedDevice = queries.getOneDeviceById(id)

        editedDevice = {
            "name": request.args.get('name') or updatedDevice.name,
            "gateid": request.args.get('gateid') or updatedDevice.gateid,
            "typeid": request.args.get('typeid') or updatedDevice.typeid,
        }

        print("EDİTED ---> ", editedDevice)
        queries.updateDevice(id, editedDevice)

        return jsonify({'success': True, 'device': editedDevice})
    else:
        device = queries.getOneDeviceById(id)

        return jsonify({'success': False, 'data': device})

# DELETE -----------
@app.route('/device/delete/<int:id>')
def deleteDevice(id):
    queries.deleteDevice(id)

    return jsonify({'success': True})

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------ BLOCK
@app.route('/api/blocks')
def apiBlock():
    results = queries.getAllBlocks()
    resultArray = []

    for block in results:
        resultArray.append({
            "id": block.id,
            "name": block.name,
        })

    result = {
        'blocks': resultArray
    }

    return jsonify({'success': True, 'data': result})

# ONE -----------
@app.route('/api/block/<int:id>')
def apiBlockOne(id):
    block = queries.getOneBlockById(id)

    result = {
        "id": block.id,
        "name": block.name,
    }

    if result['id'] != None or result['id'] != '':
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'success': False})

# ADD -----------
@app.route('/addblock', methods=['GET', 'POST'])
def addBlock():
    if request.method == 'POST':
        name = request.args.get('name')

        if name != '':
            block = {'name': name}
            queries.addBlock(block)

            print("BLOCK --> ", block)
            return jsonify({'success': True, 'data': block})
        else:
            return jsonify({'success': False})
    else:
        return jsonify({'success': False})

# UPDATE -----------
@app.route('/block/update/<int:id>', methods=['GET', 'POST'])
def updateBlock(id):
    if request.method == 'POST':
        updatedBlock = queries.getOneBlockById(id)

        editedBlock = {
            "name": request.args.get('name') or updatedBlock.name,
        }

        queries.updateBlock(id, editedBlock)

        return jsonify({'success': True, 'block': editedBlock})
    else:
        block = queries.getOneBlockById(id)

        return jsonify({'success': False, 'data': block})

# DELETE -----------
@app.route('/delete/block/delete/<int:id>')
def deleteBlock(id):
    queries.deleteBlock(id)

    return jsonify({'success': True})

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------ DEVICE TYPE
@app.route('/api/devicetypes')
def apiDeviceType():
    results = queries.getAllDeviceTypes()
    resultArray = []

    for deviceType in results:
        resultArray.append({
            "id": deviceType.id,
            "name": deviceType.name,
        })

    result = {
        'deviceTypes': resultArray
    }

    print("DEVICE TYPES RESULT --> ", result)

    return jsonify({'success': True, 'data': result})

# ONE -----------
@app.route('/api/devicetype/<int:id>')
def apiDeviceTypeOne(id):
    deviceType = queries.getOneDeviceTypeById(id)

    result = {
        "id": deviceType.id,
        "name": deviceType.name,
    }

    if result['id'] != None or result['id'] != '':
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'success': False})

# ADD -----------
@app.route('/adddevicetype', methods=['GET', 'POST'])
def addDeviceType():
    if request.method == 'POST':
        name = request.args.get('name')

        print("name  --> ", name)

        if name != '':
            deviceType = {'name': name}
            queries.addDeviceType(deviceType)

            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
    else:
        return jsonify({'success': False})

# UPDATE -----------
@app.route('/devicetype/update/<int:id>', methods=['GET', 'POST'])
def updateDeviceType(id):
    if request.method == 'POST':
        updatedDeviceType = queries.getOneDeviceTypeById(id)

        editedDeviceType = {
            "name": request.args.get('name') or updatedDeviceType.name,
        }

        print("EDITED --> ", editedDeviceType)

        queries.updateDeviceType(id, editedDeviceType)

        return jsonify({'success': True, 'data': editedDeviceType})
    else:
        deviceType = queries.getOneDeviceTypeById(id)

        return jsonify({'success': False, 'data': deviceType})

# DELETE -----------
@app.route('/delete/devicetype/delete/<int:id>')
def deleteDeviceType(id):
    queries.deleteDeviceType(id)

    return jsonify({'success': True})

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------ Biometric
@app.route('/api/biometrics')
def apiBiometrics():
    results = queries.getAllBiometrics()
    resultArray = []

    for biometric in results:
        resultArray.append({
            "id": biometric.id,
            "userid": biometric.userid,
            "deviceType": biometric.deviceType,
            "biometricid": biometric.biometricid,
        })

    result = {
        'biometrics': resultArray
    }
    return jsonify({'success': True, 'data': result})

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------ ADMIN
# LOGIN ADMIN -----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            auth = request.form

            if not auth or (not auth['username']) or (not auth['password']) or (not 'password' in auth):
                return redirect(url_for('login'))

            owner = queries.getOneOwnerByUsername(username=auth['username'])

            if check_password_hash(owner.password, auth['password']):
                token = jwt.encode({'id': owner.id,
                                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                                   app.config['SECRET_KEY'])

                session['token'] = token

                owner = {
                    'id': owner.id,
                    'username': owner.username
                }

                return jsonify({'success': True, 'data': owner, 'token': token.decode('UTF-8')})
            else:
                return jsonify({'success': False})
        else:
            return jsonify({'success': False})

        #return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    except Exception as e:
        print(e)
        return jsonify({'success': False})

# LOGOUT -----------
@app.route("/logout")
def logout():
    session['token'] = 'None'

    return jsonify({'success': True, 'description': 'System Logout'})

# ADMINS -----------
@app.route('/profile')
@token_required
def profile(current_user):
    admins = queries.getAllOwners()
    result = []

    for admin in admins:
        adminObj = {
            "id": admin.id,
            "username": admin.username,
            "password": admin.password
        }

        result.append(adminObj)

    return jsonify({'success': True, 'admin': result})

# UPDATE -----------
@app.route("/admin/<int:id>", methods=['GET', 'POST'])
def admin(id):
    if request.method == 'POST':
        data = request.data.decode('UTF-8')

        dataSplited = data.split("&")

        username = dataSplited[0]
        password = dataSplited[1]

        if username != '' and password != '':
            hashed_password = generate_password_hash(password, method='sha256')
            updatedOwner = queries.getOneOwnerById(id)

            editedOwner = {
                "username": username or updatedOwner.username,
                "password": hashed_password or updatedOwner.password,
            }

            queries.updateOwner(id, editedOwner)

            return jsonify({'success': True, 'admin': editedOwner})
        else:
            return jsonify({'success': False})
    else:
        owner = queries.getOneOwnerById(id)

        admin = {
            "id": owner.id,
            "username": owner.username,
            "password": owner.password,
        }

        return jsonify({'success': False, 'owner': admin})

# SIGN UP -----------
@app.route('/signup', methods=['GET', 'POST'])
def signup_user():
    if request.method == 'POST':
        username = ''
        password = ''

        data = request.data.decode('UTF-8')
        dataSplited = data.split("&")

        if dataSplited[0][0:8] == "username":
            username = dataSplited[0][8:]

        if dataSplited[1][0:8] == "password":
            password = dataSplited[1][8:]

        if username != '' and password != '':
            hashed_password = generate_password_hash(password, method='sha256')
            owner = {'username': username, 'password': hashed_password}
            queries.addOwner(owner)

            return jsonify({'success': True, data: owner})
        else:
            return jsonify({'success': False})
    else:
        return jsonify({'success': False})

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------ DETECT
@app.route('/ntech', methods=['GET', 'POST'])
@token_required
def detect(current_user):
    # data = request.json // from api

    # data = [{'created_date': '2021-07-01T07:52:17+00:00',
    #          'camera': {'id': 5, 'created_date': '2021-03-04T11:37:27.836272Z',
    #                     'modified_date': '2021-07-01T07:25:37.150938Z', 'group': 1, 'active': True, 'name': 'Giriş',
    #                     'comment': '', 'url': 'rtsp://admin:1234@192.168.5.57:554/defaultPrimary?streamType=u',
    #                     'stream_settings_gpu': {'roi': '', 'rot': '', 'play_speed': -1, 'jpeg_quality': 95,
    #                                             'overall_only': True, 'ffmpeg_format': '', 'ffmpeg_params': [],
    #                                             'imotion_threshold': 0, 'router_timeout_ms': 15000,
    #                                             'router_verify_ssl': True, 'filter_min_quality': 0.45,
    #                                             'filter_max_face_size': 8192, 'filter_min_face_size': 1,
    #                                             'use_stream_timestamp': False, 'realtime_post_interval': 1,
    #                                             'start_stream_timestamp': 0, 'realtime_post_every_interval': False,
    #                                             'realtime_post_first_immediately': False},
    #                     'screenshot': 'http://192.168.1.45/cameras/5/screenshot/',
    #                     'health_status': {'enabled': True, 'status': 'INPROGRESS', 'msg': '',
    #                                       'statistic': {'job_starts': 2, 'frame_width': 2048, 'faces_failed': 0,
    #                                                     'faces_posted': 0, 'frame_height': 1536, 'frames_dropped': 0,
    #                                                     'processing_fps': 19.31786, 'faces_not_posted': 0,
    #                                                     'frames_processed': 711, 'processed_duration': 33.000668,
    #                                                     'decoding_soft_errors': 0, 'frames_imotion_skipped': 0},
    #                                       'code': 'green', 'code_desc': 'EverythingisOK'}, 'threshold': None,
    #                     'latitude': None, 'longitude': None, 'azimuth': None},
    #          'camera_group': {'id': 1, 'created_date': '2021-02-18T12:27:37.604890Z',
    #                           'modified_date': '2021-02-19T06:07:56.901201Z', 'active': True,
    #                           'name': 'DefaultCameraGroup', 'comment': '', 'deduplicate': True, 'deduplicateDelay': 15,
    #                           'labels': {}, 'permissions': {'1': 'view', '2': 'view', '3': 'view'}, 'threshold': None},
    #          'face': 'http://192.168.1.45/uploads/2021/07/01/event/075219_face_cXoUS1.jpg',
    #          'frame': 'http://192.168.1.45/uploads/2021/07/01/event/075219_full_frame_oSZPCA.jpg',
    #          'frame_coords_left': 940, 'frame_coords_top': 1172, 'frame_coords_right': 1107,
    #          'frame_coords_bottom': 1406,
    #          'matched_face': '4362412081327912987', 'matched_dossier': 34, 'matched': True, 'matched_lists': [
    #         {'id': 1, 'created_date': '2021-02-18T12:27:37.622509Z', 'modified_date': '2021-02-18T12:27:37.622550Z',
    #          'active': True, 'name': 'DefaultWatchList', 'comment': '', 'color': '123456', 'notify': False,
    #          'acknowledge': False, 'permissions': {'1': 'view', '2': 'view', '3': 'view'}, 'camera_groups': [],
    #          'threshold': None}], 'confidence': 0.8297, 'quality': 0.932651,
    #          'scores': {'quality': 0.9326515793800351, 'liveness_score': None,
    #                     'track_duration_seconds': 4.200188888888761,
    #                     'track': {'id': '0a2a60439e2e-44', 'first_timestamp': '2021-07-01T07:52:14.822Z',
    #                               'last_timestamp': '2021-07-01T07:52:19.115Z'}},
    #          'acknowledged_date': '2021-07-01T07:52:17+00:00', 'acknowledged_by': None, 'acknowledged_reaction': '',
    #          'acknowledged': True, 'episode': None, 'temperature': None, 'id': '4362414227458589462',
    #          'features': {'gender': {'name': 'male', 'confidence': 1.0}, 'age': None,
    #                       'emotions': {'name': 'neutral', 'confidence': 0.997354}, 'liveness': None, 'beard': None,
    #                       'glasses': {'name': 'eye', 'confidence': 0.999917}, 'race': None,
    #                       'medmask': {'name': 'none', 'confidence': 0.999999}}, 'looks_like_confidence': None,
    #          'bs_type': 'overall', 'webhook_type': 'events', 'event_type': 'event_created',
    #          'dossier': {'id': 34, 'active': True, 'created_date': '2021-07-01T07:39:00.382646Z',
    #                      'modified_date': '2021-07-01T07:44:40.854856Z', 'name': 'Furkan', 'comment': '',
    #                      'dossier_lists': [1], 'face_count': 1, 'has_faces': True, 'meta': {},
    #                      'person_id': '4362412743490045361'}}]
    #
    # dataObject = data[0]
    #
    # if 'dossier' in dataObject and 'name' in dataObject['dossier']:
    #     userObject = dataObject['dossier']
    #     userFromDB = queries.getOneUser(10)
    #
    #     print(userObject["person_id"])
    #
    #     user = {
    #         "id": 10,  # userObject["id"], #userFromDB.id,
    #         "tc": "12345678901",  # userFromDB.tc,
    #         "name": userObject["name"],
    #         "image": dataObject["face"],
    #         "biometric_id": userObject["person_id"],
    #         "image_from_db": userFromDB.image
    #     }
    #
    #     deviceId = 1  # dataObject["camera"]["id"]
    #     # userId, message, time, deviceid
    #
    #     queries.sendLogMessage(user["id"], 'DETECTED', datetime.datetime.now(), deviceId)
    #
    #     return jsonify({'success': True, 'user': user})
    return jsonify({'success': False})

# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------ UI ROUTES
@app.route('/', methods=['GET', 'POST'])
def index():

    # allUsers = queries.getAllUsers()
    #
    # if request.method == 'POST':
    #     userId = list(request.form.to_dict(flat=False).keys())[0]
    #
    #     usersList = []
    #
    #     try:
    #         for user in allUsers:
    #             userObj = {
    #                 "id": user.id,
    #                 "image": user.image
    #             }
    #
    #             if userObj.id != '':
    #                 usersList.append(userObj)
    #
    #         return {'success': True, 'users': usersList}
    #     except:
    #         if userId == 'all':
    #             return redirect(url_for('detect'))
    # else:
    #     try:
    #         usersList = []
    #
    #         for user in allUsers:
    #             if user.id:
    #                 userObj = {
    #                     "id": user.id,
    #                     "name": user.name,
    #                     "tc": user.tc,
    #                     "image": user.image,
    #                 }
    #
    #                 usersList.append(userObj)
    #         print('111111111111111111')
    #         print(usersList)
    #
    #         return jsonify({'success': True, 'users': usersList})
    #
    #     except:
    #         print('00000000000')

    #return {'success': True, 'users': allUsers}

    return {'success': True}

# ------------------------------------------------------------------------------


# server host and port should be added to args ---------------------------------
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

# ------------------------------------------------------------------------------
