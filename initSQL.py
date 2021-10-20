# -*- coding: utf-8 -*-
"""
Created on Sat Oct  2 15:45:15 2021

This file will initialize the SQL's required for basic operations
@author: Mani
"""


#def initSQL(): 
    
"""
User Logon SQL
"""
user_logon = """SELECT userid, role 
                FROM user 
                WHERE 
                username= ? AND password_txt= ? 
                LIMIT 1 """

"""
Get all user data
"""
all_user = "SELECT username, role, password_txt, balance, age FROM user"


"""
Insert an user to table
"""
add_user = """INSERT INTO user(username, password_txt, age,role, balance) 
            VALUES (?,?,?,?,0.0)"""

"""
Display user balance
"""
disp_balance = " SELECT balance FROM user where userid = ? "

"""
List of all locations
"""
list_locations = """ SELECT locid, location FROM location """

"""
Insert the activity log of the bike at time of renting
EndDateTime, PaidBy, endLoc, Charges To be NULL
"""
ins_activity = """ INSERT INTO ActivityLog  
                           (BikeID,	
                            UserID,
                            StartDateTime,
                            EndDateTime,
                            PaidBy	,
                            startLoc,
                            endLoc  ,
                            Charges) 
                           VALUES (?, ?, datetime('now'), ?, ?, ?, ?, ?)"""

#Mark bike as rented
bike_rented = """ UPDATE bike SET rented = 'Y'
                  WHERE bikeid = ?"""

"""
Update the activity log for the bike once returned
identify by using bikeid, userid and which is not yet returned
"""      
upd_activitylog = """ UPDATE ActivityLog  
                       SET EndDateTime = datetime('now'),
                           PaidBy	   =?,
                           endLoc      =?,
                           Charges     =?
                       WHERE
                           bikeid =?  and 
                           userid =?  and
                           EndDateTime = ''
                    """
#Mark bike as available since it is returned
bike_released = """ UPDATE bike  
                       SET rented = 'N',
                       locid = ?
                       WHERE bikeid = ?
                """

"""
Check if the bike is ready to release
"""
ready_to_release = """ SELECT bikeid, StartDateTime 
                       FROM ActivityLog
                       WHERE
                       bikeid = ?  and
                       userid = ?  and
                       EndDateTime = '' and
                       endLoc = ''
                       LIMIT 1
                   """

"""
Check if user is allowed to rent a bike by validating
If there is already an active rented bike for the same user
"""  
check_user_stat = """ SELECT bikeid FROM ActivityLog  
                       WHERE
                      userid = ? and EndDateTime = ''
                      LIMIT 1
                  """

"""
Search a not yet rented and working bike 
at a given location for the user
"""         
find_bike = """ SELECT bikeid 
                FROM bike  
                WHERE rented = 'N' and 
                      bikestat = 'Y' and
                      locid = ?
                      LIMIT 1
           """

"""
Report a bike as defective
"""  
report_defective = """ UPDATE bike  
                       SET bikestat = 'N',
                       rented = 'N',
                       issue_desc = ?
                       WHERE bikeid = ? """

"""
Pay charges to user's account
"""
pay_acct = """UPDATE user
              SET balance  = balance + ?
              WHERE userid = ?
           """

"""
Update user balance after return of bike
"""
update_balance = """UPDATE user
              SET balance  = balance - ?
              WHERE userid = ? """

"""
Track location of all bikes
"""
track_all_loc = """ select l.city, l.location, count(b.bikeid)
                     from BIKE b, LOCATION l
                        where
                        b.locid = l.locid
                        group by b.locid
                 """

"""
Mark a bike as repaired
"""
repaired = """ UPDATE bike
               SET  bikestat = 'Y'
               WHERE
               bikeid = ? """

"""
Move a bike to specific location
"""
move_bike = """ UPDATE bike 
                SET locid = ?
                WHERE bikeid = ? """