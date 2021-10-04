# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 17:23:11 2021

@author: Mani
"""

import sqlite3
import initSQL as qry

with sqlite3.connect("D:/sqlite/bikeshare.db") as db:
    cursor = db.cursor()
    
def track_loc():
    #Track location wise all bikes
    print("Location wise Bike count:")
    cursor.execute(qry.track_all_loc)
    for locations in cursor.fetchall():
        print(locations)

def repair(bikeid):
    #Operator marks a bike as working
    print("Marking bike {} as fixed".format(bikeid))
    cursor.execute(qry.repaired, (bikeid,))
    
    db.commit()
    
def move(locid, bikeid):
    #Operator moves a bike to specific location
    print("Moving bike id {} to specific location {}"
          .format(bikeid, locid))
    cursor.execute(qry.move_bike, (locid, bikeid))
    
    db.commit()

def main():
    print("Running...")
    track_loc()
    repair(10)
    move(2, 10)
    print("End...")
    
if __name__ == "__main__":
    main()

db.close()