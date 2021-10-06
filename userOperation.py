# -*- coding: utf-8 -*-
"""
Created on Sat Oct  2 23:06:11 2021

@author: Mani
This file will contain the functionalities for 
a standard user or customer operation
"""

import initSQL as qry
from datetime import datetime
from datetime import timedelta

dtm = datetime.now().strftime("%d%m%Y %H:%M:%S")

def payCharges(userid, amount):
    print("Calling payCharges with {} and {}".format(amount, userid))
    qry.cursor.execute(qry.pay_acct, (amount, userid,))
    qry.db.commit()  

def reportDefective(bikeid):
    print("Calling Defective Bike with ID {}".format(bikeid))
    qry.cursor.execute(qry.report_defective, (bikeid,))
    qry.db.commit()

def findBike(locid, userid):
    #Initialize the bike number and proceed to identify
    alloted_bike = 0
    already_rented = 0
    
    #Check if this user already rented a bike and not returned
    print("Calling check_user_stat with User ID {}".format(userid))
    qry.cursor.execute(qry.check_user_stat, (userid,))
    for already_rented in qry.cursor.fetchall():
        print("Already rented Bike for this user is: {}"
              .format(already_rented))
    
    if (already_rented == 0):
        #Proceed to allocate a bike to this user
        print("Calling findBike with Location ID {}".format(locid))
        qry.cursor.execute(qry.find_bike, (locid,))
        for alloted_bike in qry.cursor.fetchall():
            print("Identified Bike ID is: {}".format(alloted_bike))
        if (alloted_bike == 0):
            print("A bike could not be located for given location : {}"
                   .format(locid))
    else:
        print("No allocation will be done for this user {}"
              .format(userid))
        
    #If a bike is allocated then insert the activity logs
    if (alloted_bike != 0):
        #Mark bike as rented
        print("Calling bike_rented with bike ID {}".format(alloted_bike[0]))
        qry.cursor.execute(qry.bike_rented, (alloted_bike))
        
        #Insert activitylog
        enddtm   = ''
        paidby   = ''
        endloc   = ''
        charges  = ''
        print("Calling ins_activity with alloted_bike {} userid {} locid {}"
              .format(alloted_bike[0], userid, locid))
        
        qry.cursor.execute(qry.ins_activity, (alloted_bike[0],
                                          userid,
                                          enddtm,
                                          paidby,
                                          locid,
                                          endloc,
                                          charges))
        print("Success calling ins_activity")
        qry.db.commit()

def returnBike(userid, bikeid, endlocid):
    #Check if this bike is ready to return
     biketorls = 0
     start_tm  = ''
    
     print("Calling ready_to_release with bike {} userid {} endlocid {}"
           .format(userid, bikeid, endlocid))
     qry.cursor.execute(qry.ready_to_release, (bikeid, userid))
     for biketorls in qry.cursor.fetchall():
            print("Going to release Bike ID : {} and rented at {}"
                  .format(biketorls[0], biketorls[1]))
     if (biketorls == 0):
         print ("ERROR : Bike can not be released!")    
           
     #Mark bike as released and set the current location
     if (biketorls != 0):
         print("Calling bike_released using end location {} and bikeid {}"
               .format(endlocid, bikeid))
         qry.cursor.execute(qry.bike_released, (endlocid, bikeid))   
     
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
         qry.cursor.execute(qry.upd_activitylog, (PaidBy,
                                              endlocid,
                                              charges,
                                              bikeid,
                                              userid))
         print("Success calling upd_activitylog")
         qry.db.commit()
        
"""
def main():
    print("Running...")
    payCharges(6, 10.48)     #payCharges(userid, amount)
    reportDefective(5)       #reportDefective(bikeid)
    findBike(5, 8)           #findBike(locid, userid)
    returnBike(8, 41, 4)     #returnBike(userid, bikeid, endlocid)
    print("End...")
    
if __name__ == "__main__":
    main()

db.close()
"""