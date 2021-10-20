# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 14:14:35 2021

@author: tonys
"""

#file:///C:/Users/tonys/Desktop/UoG study lectures/ProgSD/team project/logo.png
#cd C:/Users/tonys/Desktop/proj1


import os 
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns
import pickle
import matplotlib.pyplot as plt
from datetime import datetime as dt
import streamlit as st 
import plotly.express as px
from plotly.offline import init_notebook_mode, iplot, download_plotlyjs , plot
import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly.io as pio 
from plotly.subplots import make_subplots
#import plotly.plotly as py
import plotly
from PIL import Image

import initSQL as qry
import sqlite3
with sqlite3.connect("bikeshare.db") as db:
    cursor = db.cursor()
from datetime import datetime
from datetime import timedelta    

#c.execute('CREATE TABLE IF NOT EXISTS users(user_id TEXT, pwd TEXT, name TEXT,age integer ,mtype TEXT)')

#conn.commit()
st.sidebar.title('Navigation')
select_page = st.sidebar.selectbox("Menu", ("Overview","Sign in","Sign up","Log out") )

def findBike(locid, userid):
    #Initialize the bike number and proceed to identify
    alloted_bike = 0
    already_rented = 0
    
    #Check if this user already rented a bike and not returned
    print("Calling check_user_stat with User ID {}".format(userid))
    cursor.execute(qry.check_user_stat, (userid,))
    for already_rented in cursor.fetchall():
        print("Already rented Bike for this user is: {}"
              .format(already_rented))
    
    if (already_rented == 0):
        #Proceed to allocate a bike to this user
        print("Calling findBike with Location ID {}".format(locid))
        cursor.execute(qry.find_bike, (locid,))
        for alloted_bike in cursor.fetchall():
            print("Identified Bike ID is: {}".format(alloted_bike))
        if (alloted_bike == 0):
            print("A bike could not be located for given location : {}"
                   .format(locid))
    else:
        print("No allocation will be done for this user {}"
              .format(userid))
        return (-1)
        
    #If a bike is allocated then insert the activity logs
    if (alloted_bike != 0):
        #Mark bike as rented
        print("Calling bike_rented with bike ID {}".format(alloted_bike[0]))
        cursor.execute(qry.bike_rented, (alloted_bike))
        
        #Insert activitylog
        enddtm   = ''
        paidby   = ''
        endloc   = ''
        charges  = ''
        print("Calling ins_activity with alloted_bike {} userid {} locid {}"
              .format(alloted_bike[0], userid, locid))
        
        cursor.execute(qry.ins_activity, (alloted_bike[0],
                                          userid,
                                          enddtm,
                                          paidby,
                                          locid,
                                          endloc,
                                          charges))
        print("Success calling ins_activity")
        db.commit()
        return alloted_bike[0]


def returnBike(userid, endlocid):
     #Check if this bike is ready to return
     biketorls = 0
     start_tm  = ''
     already_rented = ['']
     bikeid = 0
     
     #Check if this user already rented a bike
     print("Calling check_user_stat with User ID {}".format(userid))
     cursor.execute(qry.check_user_stat, (userid,))
     for already_rented in cursor.fetchall():
         print("Already rented Bike for this user is: {}"
               .format(already_rented))
    
     bikeid = already_rented[0]
     
     if bikeid == '' or bikeid == 0:
         print("No option to return bike")
         return ([-1]) 
    
     print("Calling ready_to_release with bike {} userid {} endlocid {}"
           .format(bikeid, userid, endlocid))
     cursor.execute(qry.ready_to_release, (bikeid, userid))
     for biketorls in cursor.fetchall():
            print("Going to release Bike ID : {} and rented at {}"
                  .format(biketorls[0], biketorls[1]))
     if (biketorls == 0):
         print ("ERROR : No rent activity for this Bike & User. Bike can not be released!")    
           
     #Mark bike as released and set the current location
     if (biketorls != 0):
         print("Calling bike_released using end location {} and bikeid {}"
               .format(endlocid, bikeid))
         cursor.execute(qry.bike_released, (endlocid, bikeid))   
     
     #Calculate charges for the duration based on rate per hr
     if (biketorls != 0):
         charges     = 0.0
         rate_per_hr = 0.50
         PaidBy      = 'Cash'
         print ("Calculating difference at {}"
                .format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
         start_tm  = biketorls[1]
         time_diff = round(((datetime.now() - datetime.fromisoformat(start_tm)).seconds / 3600), 2)
         charges   = round((time_diff * rate_per_hr), 2)

     #Update the activity log for the bike
     if (biketorls != 0):
         print("Calling upd_activitylog using bike id {} duration {} and charge {}"
               .format(bikeid, time_diff, charges))
         cursor.execute(qry.upd_activitylog, (PaidBy,
                                              endlocid,
                                              charges,
                                              bikeid,
                                              userid))
         print("Success calling upd_activitylog")
         db.commit()
    
     #Update user balance
     if (biketorls != 0):
         print("Updating user balance using {}"
               .format(userid))
         cursor.execute(qry.update_balance, (charges,
                                             userid))
         print("Success calling update_balance")
         db.commit()
         return ([0, charges])

def reportDefectiveBike(cmnts, userid):
     #Check if a bike is ready to be reported
     already_rented = ['']
     bikeid = 0
     
     #Check if this user already rented a bike
     print("Calling check_user_stat with User ID {}".format(userid))
     cursor.execute(qry.check_user_stat, (userid,))
     for already_rented in cursor.fetchall():
         print("Already rented Bike for this user is: {}"
               .format(already_rented))
    
     bikeid = already_rented[0]
     
     if bikeid == '' or bikeid == 0:
         print("No option to report defective")
         return (-1) 
     
     #Update user comments and report defective
     if (bikeid > 0):
         print("Calling report_defective using comments {} for bikeid {}"
               .format(cmnts, bikeid))
         cursor.execute(qry.report_defective, (cmnts, bikeid))
         db.commit()
     return 0

def create_usertable():
    #c.execute('CREATE TABLE IF NOT EXISTS users(user_id TEXT, pwd TEXT, name TEXT,age integer ,mtype TEXT)')
    #a=0
    cursor.execute('SELECT COUNT(*) FROM user')
    a=cursor.fetchone()
    a=a[0]
    #st.write(a)
    #if(a==0):
        #c.execute('INSERT INTO users(user_id,pwd,name,age,mtype) VALUES (?,?,?,?,?)',("admin","admin","admin",0,"manager"))
        #c.execute('INSERT INTO users(user_id,pwd,name,age,mtype) VALUES (?,?,?,?,?)',("operator","opera","operator",0,"operator"))
        #conn.commit()
    
def add_userdata(username,pwd,age,role="User"):
    cursor.execute(qry.add_user, (username, pwd, age, role))
    db.commit()

def topupWallet(amt, userid):
    cursor.execute(qry.pay_acct, (amt, userid))
    db.commit()
    
def login_user(user_id,pwd):
    cursor.execute(qry.user_logon,(user_id, pwd))
    data=['','']
    for user in cursor.fetchall():
        #st.write(dat)
        data = user
    return data

def view_all_users(user_id,pwd):
    cursor.execute(qry.all_user)
    dat=cursor.fetchall()
    return dat

def view_trans():
    cursor.execute('SELECT * FROM ActivityLog')
    dat=cursor.fetchall()
    return dat

def get_locations():
    cursor.execute(qry.list_locations)
    loc=cursor.fetchall()
    return loc

def get_balance(userid):
    balance = ['']
    cursor.execute(qry.disp_balance, (userid,))
    balance = cursor.fetchall()
    return balance

# define a list contains all the session state
sslist = ["user_status","rent_status","code_status"]
for ss in sslist:
    if ss not in st.session_state:
        st.session_state[ss] = ""


if select_page == 'Overview':
   
    side1, side2,side3,side4,side5 = st.columns(5)
    image = Image.open('logo.png')
    new_image=image.resize((220, 150))
    side5.image(new_image,use_column_width=True,clamp = False)
    html_temp = """
    <div style="background-color:white;padding:5px">       
        <h1 style="color:black;white-space:nowrap";text-align: left;>Bike sharing APP</h1>
    </div>
    """
    side1.markdown(html_temp,unsafe_allow_html=True)
    #st.title('Overview')
    #st.write('-------------------------------------')
    
    st.info('**About** : *Bike booking app*')
    st.header("**Reference Manual:**")
    st.subheader("*Book a bike Tab:*")
    st.info('*Main tab for users to rent a bike*')
    st.subheader("*Controller Tab:*")
    st.info('*Controller tab to view faulty bikes and move them around.*')
    st.subheader("*Manager Tab:*")
    st.info('*to view reports for manager to make analytical decisions *')
    
if select_page == 'Sign in':
    #side1, side2,side3,side4,side5 = st.columns(5)
    #html_temp = """
    #<div style="background-color:white;padding:5px">       
    #    <h1 style="color:black;white-space:nowrap";text-align: left;>LOGIN PAGE</h1>
    #</div>
    #"""
    #side1.markdown(html_temp,unsafe_allow_html=True)
    #log1=st.radio("Would you like to sign in or sign up?",('Sign in','Sign up'),key=0)
    
    username=st.sidebar.text_input("USER NAME")
    pwd=st.sidebar.text_input("Password",type='password')
    # Two situation user can get access to the page after login (eg. Check account, Rent or Return a bike)
    # 1. Already logged in, switched from another page
    # 2. Just logged in. 
    if st.sidebar.checkbox("Sign in") or st.session_state.user_status != "":
        # Just logged in (user_status is None)
        if st.session_state.user_status == "":
            result = login_user(username, pwd)
            if result:
                st.session_state.user_status = username  # Login Successflly
            else:
                st.info("Incorrect username/password")
        
        # Login Successfully
        if st.session_state.user_status != "":
            result = login_user(username, pwd)
            userid = result[0]
            st.success("Logged in as {} ".format(st.session_state.user_status))
            
            if result[1] == "User":
                task=st.selectbox("Task", ["Rent","View balance","Return",
                                   "TopUp Wallet","Report Defective Bike"])
                
                if task=="Rent":
                    loc_list = get_locations()
                    loc_frame=pd.DataFrame(loc_list, columns=["LocID", "Location"])
                    loc_display=loc_frame[["Location"]]
                    loc_selected=st.selectbox("Available Locations",loc_display)
                    
                    # check session state:
                    if st.session_state.rent_status != "":
                        st.info("You've already rented a bike！")
                    else:
    
                        if (st.button("Book a ride")):
                            #function to boook a ride 
                            #and other book id
                            #List Booking locations
                            #loc_list = get_locations()
                            #loc_frame=pd.DataFrame(loc_list, columns=["LocID", "Location"])
                            #loc_display=loc_frame[["Location"]]
                            #loc_selected=st.selectbox("Available Locations",loc_display)
                            #print("loc_selected", loc_selected)
                            
                            #locid=loc_frame.query('Location == ').LocID.iloc[0]
                            #print("locid :", locid)
                            
                            if loc_selected == "Cathedral":
                                locid = 1
                            elif loc_selected == "Art Gallery":
                                locid = 2
                            elif loc_selected == "University Campus":
                                locid = 3
                            elif loc_selected == "Railway St":
                                locid = 4
                            elif loc_selected == "Park":
                                locid = 5
                            print("locid :", locid)
                            
                            alloted_bike = findBike(locid, userid)
                            if alloted_bike > 0:
                                st.write("Your bike id is  :"+str(alloted_bike))
                                st.session_state.rent_status = alloted_bike
                            elif alloted_bike == 0:
                                st.write("No bike id is alloted.")
                            elif alloted_bike == -1:
                                st.write("You already have a rented bike. Please return to rent again!")
                        
                if task=="Return":
                    loc_list = get_locations()
                    loc_frame=pd.DataFrame(loc_list, columns=["LocID", "Location"])
                    loc_display=loc_frame[["Location"]]
                    loc_selected=st.selectbox("Available Locations",loc_display)
                    print("loc_selected", loc_selected)
                    if (st.button("Return a bike")):
                        #function to boook a ride 
                        #and other book id
                        #List return locations here
                        #loc_list = get_locations()
                        #loc_frame=pd.DataFrame(loc_list, columns=["LocID", "Location"])
                        #loc_display=loc_frame[["Location"]]
                        #loc_selected=st.selectbox("Available Locations",loc_display)
                        #print("loc_selected", loc_selected)
                        
                        #locid=loc_frame.query('Location == ').LocID.iloc[0]
                        #print("locid :", locid)
                        
                        if loc_selected == "Cathedral":
                            locid = 1
                        elif loc_selected == "Art Gallery":
                            locid = 2
                        elif loc_selected == "University Campus":
                            locid = 3
                        elif loc_selected == "Railway St":
                            locid = 4
                        elif loc_selected == "Park":
                            locid = 5
                        print("locid :", locid)
                        
                        
                        stat = returnBike(userid, locid)
                        
                        if (stat[0] < 0):
                            st.write("No rent activity found. Unable to return.")
                        else:
                            st.write("Your bike is returned. Charges {}"
                                     .format(stat[1]))
                            st.session_state.rent_status = ""
    
                if task=="View balance":
                    print("Calling get_balance using userid {}".format(userid))
                    balance = get_balance(userid)
                    st.write("Your wallet balance is {} ".format(balance))
                
                if task=="TopUp Wallet":
                    topup_amt=st.text_input(label="Amount", value="0.0")
                    print("Wallet topup with amount {} for user {}"
                          .format(topup_amt, userid))
                    if (st.button("Add")):
                        topupWallet(topup_amt, userid)
                    
                
                if task=="Report Defective Bike":
                    desc=st.text_input(label="Enter Defect details", 
                                       value="brief description", max_chars=(100))
                    if (st.button("Report Defective")):
                        rp_st=reportDefectiveBike(desc, userid)                 
                        if (rp_st < 0):
                           st.write("No rent activity found. Unable to report.")
                        else:
                            st.write("Your report is noted!")
                
            elif result[1] == "Operator":
                userid = result[0]
                st.success("Logged in as {}".format(username))
                
                task=st.selectbox("Task",["Controller"])
                if task=="Controller":
                    user_result=view_all_users(username, pwd)
                    clean_db=pd.DataFrame(user_result,columns=["User name", "Role", "Password", "Balance", "Age"])
                    clean_db=clean_db[["User name","Role","Age","Balance"]]
                    st.dataframe(clean_db)  
    
            elif result[1] == "Manager":
                userid = result[0]
                st.success("Logged in as {}".format(username))
                task=st.selectbox("Task",["Controller","Manager"])
                if task=="Manager":
                    trans=view_trans()
                    txn=pd.DataFrame(trans)
                    st.dataframe(txn)
                    transac=pd.read_csv("transaction_data.csv")
                    df=transac.copy()
                    #st.write(transac)
                    transac.groupby(["time"]).count()
                    fig = px.bar(df, x="date", y="time",color='user id',title= "Time rented per day")
                    fig.update_layout(showlegend=True)        
                    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1.2))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    fig = px.bar(df, x="date", y="cost",title= "Revenue per day")
                    #fig.update_layout(showlegend=True)        
                    #fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1.2))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    fig = px.bar(df, x="start", y="cost",title= "Revenue per start location")
                    #fig.update_layout(showlegend=True)        
                    #fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1.2))
                    st.plotly_chart(fig, use_container_width=True) 
                if task=="Controller":
                    user_result=view_all_users(username, pwd)
                    clean_db=pd.DataFrame(user_result,columns=["User name","Password","name","age","Type"])
                    clean_db=clean_db[["User name","name","age","Type"]]
                    st.dataframe(clean_db)    
            elif ((result[1]!="User")|(result[1]!="controller")|(result[1]!="Manager")):
                st.warning("Incorrect User ID/Password")
    
if select_page == 'Sign up':
    st.subheader("Create a new account")
    if st.session_state.user_status != "":
        st.success("You've already logged in!")
    else:
        st.subheader("Enter name")
        username=st.text_input("USERNAME")
        
        #st.subheader("Confirm Password")
        #pwd2=st.text_input("Confirm Password")
        st.subheader("Enter Password")
        pwd=st.text_input("Password",type='password')
        st.subheader("Enter age")
        age = st.number_input("Enter your age:",
                min_value=0,max_value=99,step=1)
        if (st.button("Sign up")):
            #create_usertable()
            add_userdata(username,pwd,age)
            st.success("Account created successfully")
            st.info("You can now log in to access website")
        
if select_page == "Log out":
    st.subheader("Logout Section")
    if st.session_state.user_status != "":
        st.session_state.user_status = ""
        st.success("Logout successfully")
    else:
        st.info("You haven't logged in yet！")
