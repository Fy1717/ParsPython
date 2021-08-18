from pars.models import db
from pars import createApp

def createDB():
    db.create_all(app=createApp())

createDB()

