# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 14:14:35 2021

@author: tonys, manis

This file will initialize the following
1. Connection to Bikeshare Database
2. Start the main and subpages of application
3. Allow user to Sign-in or Sign-up
4. Perform main operations for User, Operator and Manager
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
import folium
from  streamlit_folium import folium_static
###
import pydeck as pdk
import altair as alt

#c.execute('CREATE TABLE IF NOT EXISTS users(user_id TEXT, pwd TEXT, name TEXT,age integer ,mtype TEXT)')

#conn.commit()
st.sidebar.title('Navigation')
select_page = st.sidebar.selectbox("Menu", ("Overview","Sign in","Sign up") )

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
            noBikeFound = 0
            return(noBikeFound)
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
        strtdtm  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        enddtm   = ''
        paidby   = ''
        endloc   = ''
        charges  = ''
        print("Calling ins_activity with alloted_bike {} userid {} locid {}"
              .format(alloted_bike[0], userid, locid))
        
        cursor.execute(qry.ins_activity, (alloted_bike[0],
                                          userid,
                                          strtdtm,
                                          enddtm,
                                          paidby,
                                          locid,
                                          endloc,
                                          charges))
        print("Success calling ins_activity")
        db.commit()
        return alloted_bike[0]

# find avaiable bikes
def findBikes(locid):
    cursor.execute(qry.find_bikes, (locid,))
    return cursor.fetchall()


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
         rate_per_mn = 0.06  #6 pense per minute
         PaidBy      = 'Cash'
         enddtm      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
         print ("Calculating difference at {}".format(enddtm))
         start_tm  = biketorls[1]
         #Time diff in minutes
         time_diff = round(((datetime.now() - datetime.fromisoformat(start_tm)).total_seconds() / 60), 2)
         charges   = round((time_diff * rate_per_mn), 2)

     #Update the activity log for the bike
     if (biketorls != 0):
         print("Calling upd_activitylog using bike id {} duration {} and charge {}"
               .format(bikeid, time_diff, charges))
         cursor.execute(qry.upd_activitylog, (enddtm,
                                              PaidBy,
                                              endlocid,
                                              charges,
                                              time_diff,
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
         #return status
         return ([-1]) 
     
     #Update user comments and report defective
     if (bikeid > 0):
         print("Calling report_defective using comments {} for bikeid {}"
               .format(cmnts, bikeid))
         cursor.execute(qry.report_defective, (cmnts, bikeid))
         db.commit()
     #return status and bikeid
     return ([0, bikeid])

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
    
def add_userdata(username,pwd,name,age,role="User"):
    cursor.execute(qry.add_user, (username, pwd, age, role))
    db.commit()

def topupWallet(amt, userid):
    cursor.execute(qry.pay_acct, (amt, userid))
    print ("amt {}".format(amt))
    db.commit()

def repairBike(bikeid):
    print("Calling repair bike with bikeid {}".format(bikeid))
    cursor.execute(qry.repair_bike, (bikeid,))  
    db.commit()
    print("repair bike done")

def move(frmlocid, dstlocid, bikecount):
    #Operator moves a bike to specific location
    print("Moving {} bike(s) from Location {} to {}"
          .format(bikecount, frmlocid, dstlocid))
    for i in range(bikecount):
        cursor.execute(qry.select_one_bike, (frmlocid,))
        bikeid=cursor.fetchall()
        bikeid=bikeid[0][0]
        print("Moving bikeid {}".format(bikeid))
        cursor.execute(qry.move_bike, (dstlocid, bikeid))
        db.commit()
        print("{} move done".format(i+1))

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

def get_locations():
    cursor.execute(qry.list_locations_with_bikes)
    loc=cursor.fetchall()
    return loc

def get_all_locations():
    cursor.execute(qry.list_locations)
    loc=cursor.fetchall()
    return loc

###############################################
@st.cache(persist=True)
def get_activities():
    cursor.execute(qry.list_activities)
    act=cursor.fetchall()
    return act
# stime, lat, lng
###############################################

def show_map(data,lat,lon,zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": 55.86,
            "longitude": -4.27,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data,
                get_position=["lon", "lat"],
                radius=10,
                auto_highlight=True,
                elevation_scale=50,
                pickable=True,
                elevation_range=[5, 30],
                extruded=True,
                coverage=1
            ),
        ]
    ))

###############################################
def get_balance(userid):
    balance = ['']
    cursor.execute(qry.disp_balance, (userid,))
    balance = cursor.fetchall()
    return balance[0]

def get_bikeLocation(bikeid):
    loc = ['']
    cursor.execute(qry.getBikeLoc, (bikeid,))
    loc = cursor.fetchall()
    return loc[0]

def setBalancesToZero(userid, charges):
    balance = get_balance(userid)                    
    curBal = balance[0]
    st.selectbox("Charges",[charges,])
    print("Current wallet balance is {} ".format(curBal))
    
    if (curBal >= 0.0):
        print("User's wallet was auto deducted while returning")
        st.write("Payment made from your wallet")
    else:
        st.write("Your wallet balance is not sufficient. Do you want to make the payment") #1
        if (st.button("Proceed to payment")): #2
            topupWallet(curBal*(-1), userid)
            print("Done... Set balances to Zero")
            st.write("Payment made. Thank you.")

def track_all_bikes():
    cursor.execute(qry.track_all_loc)
    bikes=cursor.fetchall()
    return bikes

def track_defective_bikes():
    cursor.execute(qry.track_defective)
    bikes=cursor.fetchall()
    return bikes

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
    #if (log1=='Sign in'):
    #st.subheader("Enter User ID")
    username=st.sidebar.text_input("USERNAME")
    #st.subheader("Enter Password")
    pwd=st.sidebar.text_input("Password",type='password')
    if (st.sidebar.checkbox("Sign in/Sign out")):
        #if pwd=="1234":
        #create_usertable()
        result=login_user(username, pwd)
        
        if result[1]=="User":
            userid = result[0]
            st.success("Logged in as {} ".format(username))
            
            task=st.selectbox("Task", ["Book","View balance","Return",
                               "TopUp Wallet","Report Defective Bike"])
            
            # show map
            m = folium.Map(
                    location=[55.86,-4.27],
                    zoom_start=14
                )
            loc_list = get_locations()
            loc_frame = pd.DataFrame(loc_list,
                columns=["LocID", "Location","Lat","Lng","Bikecount"])
            for i in range(len(loc_frame)):
                print(loc_frame['Location'][i])
                folium.Marker(
                    [loc_frame["Lat"][i],loc_frame["Lng"][i]],
                    popup=str(loc_frame['Location'][i])+" Bikes: "+str(loc_frame['Bikecount'][i])
                    ).add_to(m)

            # add locations with 0 bike
            locs = get_all_locations()
            locs_f = pd.DataFrame(locs,
                columns=["LocID", "Location","Lat","Lng"])
            for i in range(len(locs_f)):
                if locs_f["LocID"][i] not in loc_frame["LocID"].to_list():
                    folium.Marker(
                    [locs_f["Lat"][i],locs_f["Lng"][i]],
                    popup=str(locs_f['Location'][i])+" Bikes: 0"
                    ).add_to(m)

            folium_static(m)


            if task=="Book":
                #User needs to pay if there is any pending charges and proceed
                proceedBooking = 0
                currBal = 0
                chargesToPay = 0
                currBal = get_balance(userid)
                chargesToPay = round(currBal[0], 2)
                print("User's balance is :{}".format(chargesToPay))
                if (chargesToPay < 0):
                    st.write("Your pending charges : {}".format(chargesToPay))
                    if (st.button("Pay previous charges")):
                        topupWallet((-1)*chargesToPay, userid)
                        st.write("Done! Please proceed with booking")
                        proceedBooking += 1
                else:
                    proceedBooking += 1

                if (proceedBooking > 0):
                    loc_display=loc_frame[["Location"]]
                    loc_selected=st.selectbox("Available Locations",loc_display)
                    locid = int(loc_frame[loc_frame["Location"]==loc_selected]["LocID"].to_list()[0])
                    bike_available = len(list(findBikes(locid)))
                    print(bike_available)
                    st.write("There are "+str(bike_available)+" bike(s) available.")

                    if (st.button("Book a ride")):
                        
                        locid = int(loc_frame[loc_frame["Location"]==loc_selected]["LocID"].to_list()[0])
                        print("locid :", locid)
                        
                        alloted_bike = findBike(locid, userid)
                        if alloted_bike > 0:
                            st.write("Your bike id is  :"+str(alloted_bike))
                        elif alloted_bike == 0:
                            st.write("No bike id is alloted. You may try another location")
                        elif alloted_bike == -1:
                            st.write("You already have a rented bike. Please return to rent again!")
                    
            if task=="Return":
                loc_display=loc_frame[["Location"]]
                loc_selected=st.selectbox("Available Locations",loc_display)
                print("loc_selected", loc_selected)
                        
                if (st.button("Return a bike")):
                    locid = int(loc_frame[loc_frame["Location"]==loc_selected]["LocID"].to_list()[0])
                    
                    print("locid :", locid)
                    
                    
                    stat = returnBike(userid, locid)
                    
                    if (stat[0] < 0):
                        st.write("No rent activity found. Unable to return.")
                    else:
                        charges = stat[1]
                        st.write("Your bike is returned. Charges {}"
                                 .format(charges))
                        print("Calling Set balances to Zero")
                        setBalancesToZero(userid, charges)

            
            #View user's existing balance
            if task=="View balance":
                print("Calling get_balance using userid {}".format(userid))
                balance = get_balance(userid)
                balance=balance[0]
                st.info("Your wallet balance is {} ".format(balance))
                #st.write(balance)
            
            #User can manually add or TopUp wallet
            if task=="TopUp Wallet":
                topup_amt=st.text_input(label="Amount", value="0.0")
                print("Wallet topup with amount {} for user {}"
                      .format(topup_amt, userid))
                if (st.button("Add")):
                    topupWallet(topup_amt, userid)
                    st.info("Wallet money has been topped up")
                
            #When user reports a bike as defective, it will autoreturn
            if task=="Report Defective Bike":
                #desc=st.text_input(label="Enter Defect details", 
                 #                  value="brief description", max_chars=(100))
                #desc=st.text_input(label="Enter Defect details", value="brief description", max_chars=(100))
                desc = st.selectbox('Could you choose the error',('Tyre Puncture', 'Seat not proper', 'Pedal broken','another defect'))
                if (desc=='another defect'):
                    desc=st.text_input(label="Enter Defect details", max_chars=(100))
                #st.write(desc)                 
                if (st.button("Report Defective")):
                    rp_st=reportDefectiveBike(desc, userid)                 
                    if (rp_st[0] < 0):
                       st.write("No rent activity found. Unable to report.")
                    else:
                        bikeid = rp_st[1]
                        
                        #Get the bike's current location
                        locid = get_bikeLocation(bikeid)
                        locid = locid[0]
                        print("Calling default return bike with user {} and location{}"
                              .format(userid, locid))
                        
                        #Return the bike to currently where it is
                        stat = returnBike(userid, locid)
                        st.write("Your report is noted! Bike is returned. Charges {}"
                                 .format(stat[1]))
                
        elif result[1]=="Operator":
            userid = result[0]
            st.success("Logged in as {}".format(username))
            
            task=st.selectbox("Task",["Controller", "Track Locations", "Repair", "Move"])
            
            # show map
            m = folium.Map(
                    location=[55.86,-4.27],
                    zoom_start=14
                )
            loc_list = get_locations()
            loc_frame = pd.DataFrame(loc_list,
                columns=["LocID", "Location","Lat","Lng","Bikecount"])
            for i in range(len(loc_frame)):
                print(loc_frame['Location'][i])
                folium.Marker(
                    [loc_frame["Lat"][i],loc_frame["Lng"][i]],
                    popup=str(loc_frame['Location'][i])+" Bikes: "+str(loc_frame['Bikecount'][i])
                    ).add_to(m)

            # add locations with 0 bike
            locs = get_all_locations()
            locs_f = pd.DataFrame(locs,
                columns=["LocID", "Location","Lat","Lng"])
            for i in range(len(locs_f)):
                if locs_f["LocID"][i] not in loc_frame["LocID"].to_list():
                    folium.Marker(
                    [locs_f["Lat"][i],locs_f["Lng"][i]],
                    popup=str(locs_f['Location'][i])+" Bikes: 0"
                    ).add_to(m)

            folium_static(m)

            if task=="Controller":
                user_result=view_all_users(username, pwd)
                clean_db=pd.DataFrame(user_result,columns=["User name", "Role", "Password", "Balance", "Age"])
                clean_db=clean_db[["User name","Role","Age","Balance"]]
                st.dataframe(clean_db)  
            
            if task=="Track Locations":
                st.write("Bikes present in following locations")
                all_bikes=track_all_bikes()
                all_bikes_disp=pd.DataFrame(all_bikes, columns=["City", "Location", "Bike Count"])
                st.dataframe(all_bikes_disp)
                
            if task=="Repair":
                st.write("Bikes to repair in following locations")
                all_bikes=track_defective_bikes()
                all_dfct_disp=pd.DataFrame(all_bikes, columns=["Location", "Details", "Bike ID"])
                st.dataframe(all_dfct_disp)
                
                dfct_bike_loc=all_dfct_disp["Location"].unique()
                loc2 = st.selectbox('Choose the location',(dfct_bike_loc))
                lstdef=all_dfct_disp[all_dfct_disp["Location"]==loc2]["Bike ID"].unique()
                #st.write(list(lstdef))
                #Call Repair for the bike(s) selected by operator
                bid2=st.selectbox('Choose the Bike id',(lstdef))
                #bkid=st.text_input(label="Enter the bike id", max_chars=(10))
                #call function to fix bike passing location and bike id
                bid2=int(bid2)
                if (st.button("Repair the bike")):
                    repairBike(bid2)
                    st.write("Bike {} is repaired".format(bid2))
                
                
            if task=="Move":
                st.write("Bikes ready to be moved from following locations")
                all_bikes=track_all_bikes()
                all_bikes_disp=pd.DataFrame(all_bikes, columns=["City", "Location", "Bike Count"])
                st.dataframe(all_bikes_disp)
                #loc3 = st.selectbox('Choose the Source location to move bike from',('Merchant Square', 'University of Strathclyde', 'University of Glasgow'
                #                                           ,'Partick Interchange','Glasgow Cathedral','Waterloo Street'))
                a=all_bikes_disp[all_bikes_disp["Bike Count"]>0]["Location"].unique()
                loc3 = st.selectbox('Choose the Source location to move bike from',a)
                # if loc3 == "Merchant Square":
                #     frlocid = 1
                # elif loc3 == "University of Strathclyde":
                #     frlocid = 2
                # elif loc3 == "Partick Interchange":
                #     frlocid = 3
                # elif loc3 == "University of Glasgow":
                #     frlocid = 4
                # elif loc3 == "Waterloo Street":
                #     frlocid = 5
                # elif loc3 == "Glasgow Cathedral":
                #     frlocid = 6

                frlocid = int(loc_frame[loc_frame["Location"]==loc3]["LocID"].to_list()[0])
                print("From locid :", frlocid)
                #st.write(all_bikes_disp[all_bikes_disp["Location"]==loc3]["Bike Count"].unique())
                #maxbk=all_bikes_disp[all_bikes_disp["Location"]==loc3]["Bike Count"]
                
                bno2=st.number_input(label="Enter the number of bike to move", step=1) #check max value later
                
                locs = get_all_locations()
                locs_f=pd.DataFrame(locs, columns=["LocID", "Location","Lat","Lng"])
                locs_display=locs_f[locs_f["LocID"]!=frlocid]["Location"]

                loc4 = st.selectbox('Choose the destination location',locs_display)
                # if loc4 == "Merchant Square":
                #     dstlocid = 1
                # elif loc4 == "University of Strathclyde":
                #     dstlocid = 2
                # elif loc4 == "Partick Interchange":
                #     dstlocid = 3
                # elif loc4 == "University of Glasgow":
                #     dstlocid = 4
                # elif loc4 == "Waterloo Street":
                #     dstlocid = 5
                # elif loc4 == "Glasgow Cathedral":
                #     dstlocid = 6

                dstlocid = int(locs_f[locs_f["Location"]==loc4]["LocID"].to_list()[0])
                print("Dest locid :", dstlocid)
                number = int(loc_frame[loc_frame["LocID"]==frlocid]["Bikecount"])
                #Call repair bike in bulk or using one by one bike id
                if (st.button("Move the bike")):
                    if (bno2 > 0) and (bno2 <= number):
                        # if (frlocid != dstlocid):
                        move(frlocid, dstlocid, bno2)
                        st.write("Specified number of bikes are moved to the destination location")
                        # else:
                            # st.write("Same source and destinations selected")
                    else:
                        st.write("Please select a valid number")
                
        elif result[1] == "Manager":
            userid = result[0]
            st.success("Logged in as {}".format(username))
            task=st.selectbox("Task",["Visualizations", "View activities via map"])
            if task=="Visualizations":
                st.info("view the insights here")
                #cursor.execute('''select * from ActivityLog''') 
                cursor.execute('''select a.*,b.username,b.gender,b.age,b.balance from ActivityLog a left join USER b on a.UserID==b.userid''') 
                txn1=cursor.fetchall()
                df=pd.DataFrame(txn1,columns=["TxnID", "BikeID", "UserID","StartDateTime","EndDateTime","PaidBy",
                                              "startLoc","endLoc","Charges","duration_mins","Name","Gender","Age","Balance"])
                di={1:"Merchant Square",2:"University of Strathclyde",3:"Patrick Interchange",4:"University of Glasgow",
                    5:"Waterloo Street",6:"Glasgow Cathedral"}
                df["start_loc"]=df["startLoc"].map(di)
                df["end_loc"]=df["endLoc"].map(di)
                df['date']=pd.to_datetime(df['StartDateTime']).dt.date
                df['age_bucket']=np.where(df['Age']<=19,"Children/Teen",np.where(df['Age']<=29,"Young Adult",np.where(df['Age']<60,"Adult","Senior Citizen")))
                #df=pd.DataFrame(txn1)
                #st.dataframe(df)
                #st.write(min(df['date']))
                dmin=min(df['date'])
                dmax=max(df['date'])
                date1=st.date_input(label="Enter starting date to view insights",min_value=dmin,max_value=dmax,value=dmin)
                date2=st.date_input(label="Enter ending date to view insights",min_value=date1,max_value=dmax,value=dmax)      
                df=df[(df['date']>=date1)&(df['date']<=date2)]
                st.write("Transaction table")
                st.dataframe(df)
                dfagg=df.groupby(['date']).agg(txns=('TxnID','count'),revenue=('Charges','sum'),rent_time=('duration_mins','sum')).reset_index()
                dfloc1=df.groupby(['start_loc']).agg(txns=('TxnID','count'),revenue=('Charges','sum'),rent_time=('duration_mins','sum')).reset_index()
                dfloc2=df.groupby(['end_loc']).agg(txns=('TxnID','count'),revenue=('Charges','sum'),rent_time=('duration_mins','sum')).reset_index()
                dfgen=df.groupby(['Gender']).agg(txns=('TxnID','count'),revenue=('Charges','sum'),rent_time=('duration_mins','sum')).reset_index()
                dfage=df.groupby(['age_bucket']).agg(txns=('TxnID','count'),revenue=('Charges','sum'),rent_time=('duration_mins','sum')).reset_index()
                fig1 = px.line(dfagg, x="date", y="txns",title= "Transactions per day",labels={
                     "date": "Rented Date",
                     "txns": "Number of transactions",
                 }) #bar or line needs to be decided
                st.plotly_chart(fig1, use_container_width=True)
                fig2 = px.line(dfagg, x="date", y="revenue",title= "Revenue per day (in Pounds)",labels={
                     "date": "Rented Date",
                     "revenue": "Revenue Generated",
                 }) #bar or line needs to be decided
                st.plotly_chart(fig2, use_container_width=True)
                fig3 = px.pie(dfloc1, names="start_loc", values="txns",title= "Transactions in each location",labels={
                     "start_loc": "Location",
                     "txns": "Transactions",
                 })
                st.plotly_chart(fig3, use_container_width=True)
                fig4 = px.bar(dfgen, x="Gender", y="txns",title= "Transactions by gender",labels={
                     "Gender": "Gender",
                     "txns": "Transactions",
                 })
                st.plotly_chart(fig4, use_container_width=True)
                fig5 = px.bar(dfage, x="age_bucket", y="txns",title= "Transactions by Age group",labels={
                     "age_bucket": "Age Bucket",
                     "txns": "Transactions",
                 })
                st.plotly_chart(fig5, use_container_width=True)
                #df.to_excel("df.xlsx")
                #st.dataframe(dftxn)
                
                #fig1 = px.line(df, x="StartDateTime", y="TxnID",title= "Transactions per day")
                #st.plotly_chart(fig1, use_container_width=True)
            
            # if task=="Controller":
            #     user_result=view_all_users(username, pwd)
            #     clean_db=pd.DataFrame(user_result,columns=["User name","Role","Password","Balance","Age"])
            #     clean_db=clean_db[["User name","Password","Balance","Age"]]
            #     st.dataframe(clean_db)    
            ################################
            if task=="View activities via map":
                st.title("Bike Sharing Data")
                hour_selected = st.slider("Select hour of rent", 0, 23)
                act = get_activities()
                act_frame=pd.DataFrame(act, columns=["time", "lat","lon"])
                act_frame.to_csv("actLog.csv",index=False,header=True)
                af = pd.read_csv("actLog.csv")
                af["time"] = pd.to_datetime(af["time"])
                af = af[af["time"].dt.hour == hour_selected]
                
                show_map(af,55.86,-4.27,zoom=12)
                st.write(af)
                
                

        elif ((result[1]!="User")|(result[1]!="controller")|(result[1]!="Manager")):
            st.warning("Incorrect User ID/Password")
    
if select_page == 'Sign up':
    st.subheader("Create a new account")
    user_id=st.text_input("USERNAME")
    st.subheader("Enter Password")
    pwd=st.text_input("Password",type='password')
    #st.subheader("Confirm Password")
    #pwd2=st.text_input("Confirm Password")
    st.subheader("Enter name")
    name=st.text_input("name")
    st.subheader("Enter age")
    age=st.text_input("age")
    if (st.button("Sign up")):
        #create_usertable()
        add_userdata(user_id,pwd,name,age)
        st.success("Account created successfully")
        st.info("You can now log in to access website")
        
