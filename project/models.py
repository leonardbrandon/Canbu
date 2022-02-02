from project import db
from datetime import datetime

class purchase(db.Model):

    __tablename__ = 'purchase'
    id = db.Column(db.Integer,primary_key = True)
    purchaseDate = db.Column(db.Date)
    thcInMG = db.Column(db.Integer)
    cost = db.Column(db.Numeric)
    hardness = db.Column(db.Numeric)
    weightedValue = db.Column(db.Numeric)
    daysBetween = db.Column(db.Integer)
    returnRate = db.Column(db.Numeric)
    calculated = db.Column(db.Boolean)
    active = db.Column(db.Boolean)
    #creationDate = db.Column(db.DateTime(), default = datetime.utcnow)
    modifiedDate = db.Column(db.DateTime(), default = datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self,purchaseDate, thcInMG, cost, hardness, weightedValue, daysBetween, returnRate, calculated, active, modifiedDate):
        self.purchaseDate = purchaseDate
        self.thcInMG = thcInMG
        self.cost = cost
        self.hardness = hardness
        self.weightedValue = None
        self.daysBetween = None
        self.returnRate = None
        self.calculated = False
        self.active = True
        #self.creationDate = datetime.utcnow
        self.modifiedDate = datetime.utcnow

    def __repr__(self):
        return f"On {self.purchaseDate}, {self.thcInMG}MG of THC was purchased for {self.cost}.  The hardness on the day recorded is {self.hardness}."
        
