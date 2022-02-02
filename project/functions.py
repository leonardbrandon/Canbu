


import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pandas as pd
import numpy as np
import sqlite3 as sqlite
import json
#from pandas.core.indexes.period import PeriodDelegateMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import text
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for
from flask_table import Table, Col
import plotly
import plotly.graph_objs as go
import plotly.offline as py
import plotly.express as px
from plotly import tools
from project import db
from project.models import purchase
from project.canbu.forms import addPurchaseForm




canbu_blueprint = Blueprint('canbu',
                            __name__,
                            template_folder='templates/canbu')


app = Flask(__name__)

# Configuration - once happy with this, separate into separate config.py file
app.config['SECRET_KEY'] = 'BCRcooperative21'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'canbu.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_uri = app.config['SQLALCHEMY_DATABASE_URI']
#engine = create_engine(db_uri, echo=True)
engine = create_engine('sqlite:///' + os.path.join(basedir, 'canbu.db'))

db = SQLAlchemy(app)
Migrate(app,db)

Session = sessionmaker(bind = engine)
session = Session()
#session = db.session()

dbfile = basedir+os.sep+'canbu.db'
#print("dbfile",dbfile)
try:
    #conn=engine.raw_connection()
    conn=sqlite.connect(dbfile, check_same_thread=False)
    cur=conn.cursor()
    #print("dbfile", dbfile)
except:
    print("dbfile not connected")

# NOTE! These imports need to come after you've defined db, otherwise you will
# get errors in your models.py files.
## Grab the blueprints from the other views.py files for each "app"
#from project.canbu.views import canbu_blueprint
#app.register_blueprint(canbu_blueprint,url_prefix="")

updateStartDate = datetime.strptime('2020-01-01', '%Y-%m-%d')
#updateStartDate = datetime.strftime(updateStartDate, '%Y-%m-%d')
updateEndDate = datetime.strptime('2021-12-31', '%Y-%m-%d')
#updateEndDate = datetime.strftime(updateEndDate, '%Y-%m-%d')

#updateStartDate = form.updateStartDate.data
#updateEndDate = form.updateEndDate.data


##### Start Function Definitions here
##### Functions in this file:
##### updateHistory, cleanCSVFile, updateDFtoDB, importCanbuCSV


def updateHistory(startDate, endDate):
    counter=0
    print("startDate", startDate, "endDate", endDate)
    sql_query = pd.read_sql_query(f"SELECT * FROM purchase", conn)
    selection_df = pd.DataFrame(sql_query, columns = ['purchaseDate', 'thcInMG', 'cost', 'hardness', 'weightedValue', 'daysBetween', 'returnRate', 'calculated', 'active', 'modifiedDate'])
    conn.commit()   
    #selection_df=selection_df.sort_values(by='purchaseDate')
    #params={"startDate":startDate, "endDate":endDate}
    #selection_df.set_index(purchaseDate, inplace = True)
    #print(selection_df)
    #for x in range(0, len(selection_df)):
    #    purDate = selection_df.loc[x][0]
    #    selection_df.loc[x][0] = datetime.strptime(purDate, "%Y-%m-%d")
    for x in range(0, len(selection_df)):
        #print(selection_df.loc[x]['purchaseDate'])
        #selection_df.loc[x]['purchaseDate'] = pd.to_datetime(selection_df.loc[x]['purchaseDate'], format='%Y-%m-%d', errors='ignore')
        if datetime.strptime(selection_df.loc[x]['purchaseDate'], '%Y-%m-%d') < startDate or datetime.strptime(selection_df.loc[x]['purchaseDate'], '%Y-%m-%d') > endDate:
            selection_df.loc[x, ['active']] = 0
            #print("82", selection_df.loc[x]['active'])
    comparison_df = selection_df
    selection_df = selection_df.loc[selection_df["active"] == 1]

    #df = pd.DataFrame(columns = ['purchaseDate', 'weightedValue', 'daysBetween', 'returnRate', 'active'])
    if len(selection_df) == 0:
        sql_query = pd.read_sql_query(f"SELECT * FROM purchase ORDER BY purchaseDate ASC limit 1", conn)
        select_df = pd.DataFrame(sql_query, columns = ['purchaseDate'])
        #print(f"date found {select_df.loc[0][0]}")
        #print("date values invalid")
        exit()
    selection_df.reset_index(drop=True,inplace=True)
    
    #print(selection_df)
    #print(selection_df.loc[0][0],selection_df.loc[0][6])
    for x in range(0, len(selection_df)):
        purDate = selection_df.loc[x][0]
        purDateQuery = datetime.strptime(purDate, '%Y-%m-%d')
        print("purDate", purDate)
        previous_row_query = pd.read_sql_query(f'SELECT purchaseDate, returnRate FROM purchase WHERE purchaseDate < :parameter ORDER BY purchaseDate DESC LIMIT  1', conn, params={"parameter":purDate})
        #print("previous_row_query", previous_row_query)

        previous_row_df = pd.DataFrame(previous_row_query, columns = ['purchaseDate', 'returnRate'])
        print("previous_row_df", previous_row_df)
        #previous_row = cur.execute(f'SELECT purchaseDate, ReturnRate FROM purchase WHERE purchaseDate <= "2021-06-30" ORDER BY purchaseDate DESC LIMIT  1')
        conn.commit()
        #print(len(previous_row_df))
        if len(previous_row_df) > 0:
            #print("previous_row", previous_row_df, "loc", previous_row_df.loc[0][0] )
            previousDate = previous_row_df.loc[0][0]
            print("112",previousDate)
            previousRate = previous_row_df.loc[0][1]
            # weightedValue = thcInMG + cost * (-hardness)
            mweightedValue = (selection_df.loc[x][1] + selection_df.loc[x][2]) * (-1 * selection_df.loc[x][3])
            # Need to calculate the actual daysBetween
            
            timeBetween = datetime.strptime(purDate, '%Y-%m-%d') - datetime.strptime(previousDate, '%Y-%m-%d') 
            mdaysBetween = int(timeBetween.days)
            # also need to calculate the proper return rate
            try:
                mreturnRate = mweightedValue + mdaysBetween + previousRate
            except:
                mreturnRate = mweightedValue + mdaysBetween
            print("returnRate", mreturnRate, "weightedValue", mweightedValue, "daysBetween", mdaysBetween)

            mcalculated = True
            
        else:
            mweightedValue = (selection_df.loc[x][1] + selection_df.loc[x][2]) * (-1 * selection_df.loc[x][3])
            mdaysBetween = 0
            mreturnRate = mweightedValue
            mcalculated = True
        print("trying to update database")
        
            #conn1 = engine.connect(dbfile, check_same_thread=False)
            #stmt = purchase.update().\
            #    values(weightedValue = mweightedValue, daysBetween = mdaysBetween, returnRate = mreturnRate, calculated = mcalculated).\
            #    where(purchase.purchaseDate == purDate)
            #conn1.execute(stmt)
        update_query = 'UPDATE purchase SET weightedValue = ?, daysBetween = ?, returnRate = ?, calculated = ? WHERE purchaseDate = ?' 
        cur.execute(update_query, (mweightedValue, mdaysBetween, mreturnRate, mcalculated, purDate))
        conn.commit()
        #    print("database not updated")
        #df.append[purchaseDate, weightedValue, daysBetween, returnRate, active]
        counter += 1
        #df.to_sql(history, if_exists='Append')
    return counter


## Strip trailing commas on each line
def cleanCSVFile(filename, outfile):

    print("cleaning CSV Data")
    print(filename, outfile)
    intermediatefile = '1'+outfile
    with open(filename, 'r') as reader, open(intermediatefile, 'w') as writer:
        for num, line in enumerate(reader):
            line = line.replace('Purchase Date', 'purchaseDate')
            line = line.replace('THC in MG', 'thcInMG')
            line = line.replace('Cost', 'cost')
            line = line.replace('Weighted Value', 'weightedValue')
            line = line.replace('Days Between', 'daysBetween')
            line = line.replace('Return Rate', 'returnRate')
            line = line.replace('Hardness (0.1 to 0.3)', 'hardness')
            if num > 0 and ",\n" in line:
                newline = line[:-2] + "\n" if "\n" in line else line[:-1]
            else:
                newline = line
            #writeline = newline.replace(", ", ",0")
            
            
            writeline = newline.replace(' ', '')
            writer.write(writeline)
    
    datefix = pd.read_csv(intermediatefile)
    for row in datefix:
        print(row[2])

    #with open(datefix, 'r')as reader, open(outfile, 'w') as writer:
    #    for num, line in enumerate(reader):
    #        pass
    cleanedfile = intermediatefile
    return cleanedfile

def importDFtoDB(df, table):
    
    df1 = df[['purchaseDate', 'thcInMG', 'cost', 'hardness']]
    df2 = df1.assign(active=True)
    df3 = df2.assign(modifiedDate='')
    #df3['purchaseDate'] = pd.to_datetime(dateutil.parser.parse(pd.Series(df3['purchaseDate']), dayfirst=True))
    x = 0
    print(df3[:])
    datelist = df3.loc[:, ('purchaseDate')]
    print(datelist)
       
    #print(df3.info())
    #df3['purchaseDate'] = pd.to_datetime(df3['purchaseDate']).dt.date
    print(df3)
    insert_records_from_csv = '''
        INSERT into purchase (purchaseDate, thcInMG, cost, hardness, active, modifiedDate) VALUES(?,?,?,?,?,?)
        '''
    df3.to_sql('purchase', conn, if_exists='append', index=False)
    conn.commit()
    return len(df)

def importCanbuCSV(csvfile):
    tempoutfile = 'tempfile.csv'
    cleanfile = cleanCSVFile(csvfile, tempoutfile)
    
    records_added = 0
    with open(cleanfile) as filename:
        print("cleanfile", cleanfile, "filename", filename)
        read_df = pd.read_csv(cleanfile)
        table = 'purchase'
        sqlQuery = '''select name from sqlite_master where type = "table"; '''
        listTables = pd.DataFrame(cur.execute(sqlQuery))
        print(listTables)
        
        distinct_query = ''' 
            SELECT DISTINCT purchaseDate FROM purchase;
            '''
        print("dbfile", dbfile, "conn", conn, "cur", cur)
        purchaseDateRemove = cur.execute(distinct_query)
        conn.commit()
        try:
            df = read_df.loc[~read_df.purchaseDate.isin(purchaseDateRemove)]
        except:
            df = read_df
            print("new import")
        records_added = importDFtoDB(df, table)
    return records_added

def set_basic_dates():
    dates=[]
    #startDate = purchase.query.purchaseDate().first()
    #endDate = purchase.query.purchaseDate().last()
    dateQuery = '''
        SELECT purchaseDate, thcInMG, cost, hardness, daysBetween, returnRate, calculated, active  from purchase  
            '''
 
    dateQueryData = pd.DataFrame(db.session.execute(dateQuery), columns = ['purchaseDate', 'thcInMG', 'cost', 'hardness', 'daysBetween', 'returnRate', 'calculated', 'active'])
    conn.commit()
    #print(dateQueryData.info())
    #print(dateQueryData)
    dateQueryData.sort_values('purchaseDate')
    startDate = dateQueryData.iloc[0]['purchaseDate']
    length = len(dateQueryData)-1
    endDate = dateQueryData.iloc[length]['purchaseDate']
    
    dates = [startDate, endDate]
    return dates

def retrieveData(startDate, endDate):
    df_query = text(
        "SELECT purchaseDate, thcInMG, cost, hardness, daysBetween, returnRate, calculated, active"
        " from purchase"
        )
    df_data = db.session.execute(df_query)
    conn.commit()
    df = pd.DataFrame(df_data, columns = ['purchaseDate', 'thcInMG', 'cost', 'hardness', 'daysBetween', 'returnRate', 'caluclated', 'active'])
    last_hardness = df.iloc[len(df)-1]['hardness']
    last_daysBetween = datetime.today() - datetime.strptime(df.iloc[len(df)-1]['purchaseDate'], '%Y-%m-%d')
    last_returnRate = 0 + last_daysBetween.days + df.iloc[len(df)-1]['returnRate']
    last_row_of_df = [datetime.today().date(), 0, 0, last_hardness, last_daysBetween.days, last_returnRate, 1, 1]
    df.loc[len(df)] = last_row_of_df
    #if startDate:
    #    
    #    dropper = df[df['purchaseDate'] < startDate].index
    #    df.drop(dropper, inplace=True)
    #if endDate:
    #    dropper = df[df['purchaseDate'] > endDate].index
    #    df.drop(dropper, inplace=True)
    return df

def create_master_df():
    dates = set_basic_dates()
    startDate = dates[0]
    endDate = dates[1]
    master_df = retrieveData(startDate, endDate)
    master_df_flag = True
    return master_df, master_df_flag

def progressReport(master_df, master_df_flag):
    print(master_df_flag, master_df)
    try:
        if master_df_flag == False:
            master_df, master_df_flag = create_master_df(master_df_flag)
    except:
        master_df_flag == False
        master_df, master_df_flag = create_master_df(master_df_flag)

    #graphdata_df = master_df['purchaseDate', 'returnRate']
    layout = go.Layout(
        title = "<b>Data Dashboard</b>",
        paper_bgcolor = 'rgb(240,240,240)',
        plot_bgcolor = 'rgb(240,240,240)',
        #autosize = True,
        autosize = False,
        width = 800,
        height = 500,
        barmode = "stack",
        xaxis = dict(title = "Time", linecolor="#333333"),
        yaxis = dict(title="Return Rate", linecolor = "#021C1E"),
        )
    Time = master_df['purchaseDate']
    Value = master_df['returnRate']
    chartdata = []
    line_chart = go.Scatter(x=Time, y=Value, marker_color = 'Black')
    chartdata.append(line_chart)
    fig=go.Figure(data = chartdata, layout = layout)
        ### new code 2021-11-12
    fig.update_xaxes(rangeslider_visible=True)
    #fig.update_layout(showlegend=False)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def initialize_master_df():
    master_df = create_master_df()
    return master_df

#records_added = importCanbuCSV(csvfile)

#counter = 0
#counter = updateHistory(updateStartDate, updateEndDate)


### Table Declaration
class canbutable(Table):
    purchaseDate = Col('purchaseDate')
    thcInMG = Col('thcInMG')
    cost = Col('cost')
    hardness = Col('hardness')
    weightedValue = Col('weighteValue')
    daysBetween = Col('daysBetween')
    returnRate = Col('returnRate')
    calculated = Col('calculated')
    active = Col('active')
    modifiedDate = Col('modifiedDate')

### Object Declaration
class thcPurchase(object):
    def __init__(self, purchaseDate, thcInMG, cost, hardness, weightedValue, daysBetween, returnRate, calculated, active, modifiedDate):
        self.purchaseDate = purchaseDate
        self.thcInMG = thcInMG
        self.cost = cost
        self.hardness = hardness
        self.weightedValue = weightedValue
        self.daysBetween = daysBetween
        self.returnRate = returnRate
        self.calculated = calculated
        self.active = active
        self.modifiedDate = modifiedDate

def tableview():
    thcPurchase = purchase.query.all()
    table = canbutable(thcPurchase)
    print(table.__html__())
    return table


