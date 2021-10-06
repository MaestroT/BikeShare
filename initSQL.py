# -*- coding: utf-8 -*-
"""
Created on Sat Oct  2 15:45:15 2021

This file will initialize the SQL's required for basic operations
@author: Mani
"""

import sqlite3
with sqlite3.connect("D:/sqlite/bikeshare.db") as db:
    cursor = db.cursor()

#def initSQL(): 
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
                       rented = 'N'
                       WHERE bikeid = ? """

"""
Pay charges to user's account
"""
pay_acct = """UPDATE user
              SET balance  = ?
              WHERE userid = ?
           """

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