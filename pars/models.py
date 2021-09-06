
from dataclasses import dataclass
from pars import db
import datetime
from sqlalchemy import func
from datetime import datetime, date
import requests


# ------------------------------------------------------------

class Server:
    def __init__(self):
        self.host = "http://127.0.0.1/"
        self.port = "5000"

server = Server() 

# ------------------------------------------------------------


# -------------------------------------------------------

@dataclass
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    tc = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(120))
    image = db.Column(db.String(120))
    shift = db.Column(db.Integer, db.ForeignKey('shift.id'))
    activated = db.Column(db.Boolean, default=True)
    
    def __init__(self, tc, name, image, shift, activated):
        self.tc = tc
        self.name = name
        self.image = image
        self.shift = shift
        self.activated = activated

# -------------------------------------------------------------


# -------------------------------------------------------

@dataclass
class Biometric(db.Model):
    __tablename__ = 'biometric'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    deviceType = db.Column(db.Integer, db.ForeignKey('devicetype.id'))
    biometricid = db.Column(db.String)
    __table_args__ = (db.UniqueConstraint('biometricid', 'deviceType', name='bioId_devType'),)


    def __init__(self, userid, deviceType, biometricid):
        self.userid = userid
        self.deviceType = deviceType
        self.biometricid = biometricid

# -------------------------------------------------------------


# -------------------------------------------------------

@dataclass
class LogProcessor(db.Model):
    __tablename__ = 'log'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    message = db.Column(db.String(120))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    deviceid = db.Column(db.Integer, db.ForeignKey('device.id'), default=2)

    def __init__(self, userid, message, time, deviceid):
        self.userid = userid
        self.message = message
        self.time = time
        self.deviceid = deviceid

# -------------------------------------------------------

# -------------------------------------------------------

@dataclass
class LoginLogout(db.Model):
    __tablename__ = 'loginlogout'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    day = db.Column(db.DateTime, default=date.today())
    intime = db.Column(db.DateTime, server_default=func.now())
    outtime = db.Column(db.DateTime, server_default=func.now())
    deviceid = db.Column(db.Integer, db.ForeignKey('device.id'), default=2)

    def __init__(self, userid, day, intime, outtime, deviceid):
        self.userid = userid
        self.day = day
        self.intime = intime
        self.outtime = outtime
        self.deviceid = deviceid


# -------------------------------------------------------


# -------------------------------------------------------

@dataclass
class DeviceType(db.Model):
    __tablename__ = 'devicetype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __init__(self, name):
        self.name = name

# -------------------------------------------------------


# -------------------------------------------------------

@dataclass
class Gate(db.Model):
    __tablename__ = 'gate'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    blockid = db.Column(db.Integer, db.ForeignKey('block.id'))

    def __init__(self, name, blockid):
        self.name = name
        self.blockid = blockid

# -------------------------------------------------------


# -------------------------------------------------------

@dataclass
class Device(db.Model):
    __tablename__ = 'device'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    gateid = db.Column(db.Integer, db.ForeignKey('gate.id'))
    typeid = db.Column(db.Integer, db.ForeignKey('devicetype.id'))

    def __init__(self, name, gateid, typeid):
        self.name = name
        self.gateid = gateid
        self.typeid = typeid

# -------------------------------------------------------



# -------------------------------------------------------

@dataclass
class Block(db.Model):
    __tablename__ = 'block'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __init__(self, name):
        self.name = name

# -------------------------------------------------------


# -------------------------------------------------------

@dataclass
class Owner(db.Model):
    __tablename__ = 'owner'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))

    def __init__(self, username, password):
        self.username = username
        self.password = password

# -------------------------------------------------------

# -------------------------------------------------------

@dataclass
class Shift(db.Model):
    __tablename__ = 'shift'

    id = db.Column(db.Integer, primary_key=True)
    startTime = db.Column(db.String(120))
    endTime = db.Column(db.String(120))

    def __init__(self, startTime, endTime):
        self.startTime = startTime
        self.endTime = endTime

# -------------------------------------------------------


# -------------------------------------------------------

class Queries:
    #----------------------------------------------------- LOGS
    def sendLogMessage(self, userId, message, time, deviceid):
        addingLog = LogProcessor(userId, message, time, deviceid)

        db.session.add(addingLog)
        db.session.commit()

    def getAllLogs(self):
        try:
            results = LogProcessor.query.all()
        except:
            results = 'LOG NOT FOUND'

        return results

    #----------------------------------------------------- LOGIN LOGOUT
    def getAllLogsGate(self):
        try:
            results = LoginLogout.query.all()
        except:
            results = 'LOGSGATE NOT FOUND'

        return results

    def addLoginLogout(self, userId, day, intime, outtime, deviceid):
        addingLog = LoginLogout(userId, day, intime, outtime, deviceid)

        db.session.add(addingLog)
        db.session.commit()

    def updateLoginLogout(self, existLogId):
        existLog = LoginLogout.query.filter_by(id=existLogId).first()
        existLog.outtime = datetime.now()

        db.session.commit()

    def getOneLoginLogoutByDay(self, userid, day):
        date_time_str = str(day) + ' 00:00:00'
        date_time_obj = datetime.strptime(date_time_str[2:], '%y-%m-%d %H:%M:%S')

        try:
            # print("DAY --> ", day) --> 2021-08-16
            # print("first log day --> ", LoginLogout.query.get(1).day) --> 2021-08-16 00:00:00

            result = LoginLogout.query.filter_by(userid=userid, day=date_time_obj).first()
            # print("result --> ", result)
        except Exception as e:
            # print("ERROR", e)
            result = 'LOG NOT FOUND'

        return result

    #----------------------------------------------------- USERS
    def getAllUsers(self, status):
        try:
            if status == '' or status == None:
                status = True
            elif status == 'actives':
                status = True
            else:
                status = False

            results = User.query.filter_by(activated=status).all()
        except:
            results = 'USER NOT FOUND'

        return results

    def getOneUser(self, id):
        try:
            result = User.query.get(id)
        except:
            result = 'USER NOT FOUND'

        return result

    def getOneUserByTc(self, searchtc):
        try:
            result = User.query.filter_by(tc=searchtc).first()
        except:
            result = 'USER NOT FOUND'

        # print("RESULT -> ", result)
        return result

    def addUser(self, user):
        tcIdExists = User.query.filter_by(tc=user["tc"]).first()

        if tcIdExists:
            return False

        addingUser = User(user["tc"], user["name"], user["image"], user["shift"], True)

        db.session.add(addingUser)
        db.session.commit()
        db.session.refresh(addingUser)

        self.sendLogMessage(addingUser.id, 'USER ADDED', datetime.now(), 2)

        return True

    def updateUser(self, id, newUser, activation):
        beforeUser = User.query.filter_by(id=id).first()

        beforeUser.tc = newUser['tc']
        beforeUser.name = newUser['name']
        beforeUser.shift = newUser['shift']
        beforeUser.image = newUser['image']

        if activation:
            beforeUser.activated = True

        db.session.commit()

        self.sendLogMessage(id, 'USER UPDATED', datetime.now(), 2)

    def deleteUser(self, id, deleteType):
        deletedUser = User.query.filter_by(id=id).first()

        if deletedUser:
            deletedUserState = deletedUser.activated

            if deletedUserState:
                if deleteType == 'DEACTIVE' or deleteType == '' or deleteType == None:
                    result = 'USER DEACTIVATED'

                    deletedUser.activated = False
                elif deleteType == 'FROM NTECH':
                    # headers = {
                    #     'Authorization': 'Bearer dY7d-vR6i'
                    # }
                    # url = 'http://46.197.140.92:65015/v1/faces/id/' + id + '/'
                    #
                    # with requests.Session() as s:
                    #     response = s.post(url, headers=headers).json()
                    #
                    # if response.status_code == 204:
                    #     result = 'USER DELETE FROM NTECH'
                    # else:
                    #     result = 'USER COULDNT DELETE FROM NTECH'

                    result = 'USER DELETE FROM NTECH'

                elif deleteType == 'LOGS':
                    LoginLogout.query.filter_by(userid=deletedUser.id).delete()
                    LogProcessor.query.filter_by(userid=deletedUser.id).delete()
                    User.query.filter_by(id=deletedUser.id).delete()

                    result = 'USER DELETE FROM LOGS'
                else:
                    result = 'USER COULDNT DELETE'
            else:
                result = 'USER ACTIVATED'

                deletedUser.activated = True

            db.session.commit()
        else:
            result = 'ACTIVE USER NOT FOUND'

        self.sendLogMessage(id, result, datetime.now(), 2)

        return result
    #-----------------------------------------------------

    #----------------------------------------------------- ADMINS
    def getOneOwnerByUsername(self, username):
        try:
            result = Owner.query.filter_by(username=username).first()
        except:
            result = 'USER NOT FOUND'

        return result

    def getOneOwnerById(self, id):
        try:
            result = Owner.query.filter_by(id=id).first()
        except:
            result = 'USER NOT FOUND'

        return result

    def getAllOwners(self):
        try:
            result = Owner.query.filter_by().all()
        except:
            result = 'OWNER NOT FOUND'

        return result

    def updateOwner(self, id, newOwner):
        beforeUser = Owner.query.filter_by(id=id).first()

        beforeUser.username = newOwner['username']
        beforeUser.password = newOwner['password']

        db.session.commit()

    def addOwner(self, owner):
        addingOwner = Owner(owner["username"], owner["password"])

        db.session.add(addingOwner)
        db.session.commit()

    #-----------------------------------------------------

    #----------------------------------------------------- SHIFTS
    def getAllShifts(self):
        try:
            results = Shift.query.filter_by().all()
        except:
            results = 'SHIFT NOT FOUND'

        return results

    def addShift(self, shift):
        addingShift = Shift(shift["startTime"], shift["endTime"])

        # print("ADDING --> ", addingShift)

        db.session.add(addingShift)
        db.session.commit()

    def updateShift(self, id, newShift):
        beforeShift = Shift.query.filter_by(id=id).first()

        beforeShift.startTime = newShift['startTime']
        beforeShift.endTime = newShift['endTime']

        db.session.commit()

    def deleteShift(self, id):
        deletedShift = Shift.query.filter_by(id=id).first()

        if deletedShift:
            Shift.query.filter_by(id=id).delete()

            db.session.commit()

    def getOneShiftById(self, id):
        try:
            result = Shift.query.filter_by(id=id).first()
        except:
            result = 'SHIFT NOT FOUND'

        return result
    #-----------------------------------------------------

    # ----------------------------------------------------- BIOMETRICS
    def getAllBiometrics(self):
        try:
            results = Biometric.query.filter_by().all()
        except:
            results = 'BIOMETRIC NOT FOUND'

        return results

    def getUserFromBiometrics(self, faceid):
        try:
            biometric = Biometric.query.filter_by(biometricid=str(faceid)).first()
            userid = biometric.userid
            user = User.query.filter_by(id=userid).first()
            result = user
        except:
            result = 'USER NOT FOUND'

        return result

    # -----------------------------------------------------

    #----------------------------------------------------- DEVICES
    def getAllDevices(self):
        try:
            results = Device.query.filter_by().all()
        except:
            results = 'DEVICE NOT FOUND'

        return results

    def addDevice(self, device):
        addingDevice = Device(device["name"], device["gateid"], device["typeid"])

        # print("ADDING --> ", addingDevice)

        db.session.add(addingDevice)
        db.session.commit()

    def updateDevice(self, id, newDevice):
        beforeDevice = Device.query.filter_by(id=id).first()

        beforeDevice.name = newDevice['name']
        beforeDevice.gateid = newDevice['gateid']
        beforeDevice.typeid = newDevice['typeid']

        db.session.commit()

    def deleteDevice(self, id):
        deletedDevice = Device.query.filter_by(id=id).first()

        if deletedDevice:
            Device.query.filter_by(id=id).delete()
            db.session.commit()

    def getOneDeviceById(self, id):
        try:
            result = Device.query.filter_by(id=id).first()
        except:
            result = 'DEVICE NOT FOUND'

        return result
    #-----------------------------------------------------

    #----------------------------------------------------- GATES
    def getAllGates(self):
        try:
            results = Gate.query.filter_by().all()
        except:
            results = 'GATE NOT FOUND'

        return results

    def addGate(self, gate):
        addingGate = Gate(gate["name"], gate["blockid"])

        # print("ADDING --> ", addingGate)

        db.session.add(addingGate)
        db.session.commit()

    def updateGate(self, id, newGate):
        beforeGate = Gate.query.filter_by(id=id).first()

        beforeGate.name = newGate['name']
        beforeGate.blockid = newGate['blockid']

        db.session.commit()

    def deleteGate(self, id):
        deletedGate = Gate.query.filter_by(id=id).first()

        if deletedGate:
            Gate.query.filter_by(id=id).delete()

            db.session.commit()

    def getOneGateById(self, id):
        try:
            result = Gate.query.filter_by(id=id).first()
        except:
            result = 'GATE NOT FOUND'

        return result
    #-----------------------------------------------------

    # ----------------------------------------------------- BLOCK
    def getAllBlocks(self):
        try:
            results = Block.query.filter_by().all()
        except:
            results = 'BLOCK NOT FOUND'

        # print("BLOCKS --> ", results)
        return results

    def addBlock(self, newBlock):
        addingBlock = Block(newBlock["name"])

        # print("NEW BLOCK IN QUERIES --> ", addingBlock)
        db.session.add(addingBlock)
        db.session.commit()

    def updateBlock(self, id, newBlock):
        beforeBlock = Block.query.filter_by(id=id).first()

        # print("BEFORE BLOCK --> ", beforeBlock)
        # print("newBlock BLOCK --> ", newBlock)

        beforeBlock.name = newBlock['name']

        db.session.commit()

    def deleteBlock(self, id):
        deletedBlock = Block.query.filter_by(id=id).first()

        if deletedBlock:
            Block.query.filter_by(id=id).delete()

            db.session.commit()

    def getOneBlockById(self, id):
        try:
            result = Block.query.filter_by(id=id).first()
        except:
            result = 'BLOCK NOT FOUND'

        return result
    # -----------------------------------------------------

    # ----------------------------------------------------- DEVICETYPE
    def getAllDeviceTypes(self):
        try:
            results = DeviceType.query.filter_by().all()
        except:
            results = 'DEVICETYPE NOT FOUND'

        return results

    def addDeviceType(self, deviceType):
        addingDeviceType = DeviceType(deviceType["name"])

        #print("ADDING --> ", addingDeviceType)

        db.session.add(addingDeviceType)
        db.session.commit()

    def updateDeviceType(self, id, newDeviceType):
        #print("ID --> ", id)
        #print("NEW --> ", newDeviceType)

        beforeDeviceType = DeviceType.query.filter_by(id=id).first()
        beforeDeviceType.name = newDeviceType['name']
        db.session.commit()

    def deleteDeviceType(self, id):
        deletedDeviceType = DeviceType.query.filter_by(id=id).first()

        if deletedDeviceType:
            DeviceType.query.filter_by(id=id).delete()
            db.session.commit()

    def getOneDeviceTypeById(self, id):
        try:
            result = DeviceType.query.filter_by(id=id).first()
        except:
            result = 'DEVICETYPE NOT FOUND'

        return result
    # -----------------------------------------------------

# -------------------------------------------------------

