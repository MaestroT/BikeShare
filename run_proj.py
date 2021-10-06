# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 22:26:21 2021

@author: Mani
"""

import initSQL as qry

import userOperation     as uo
import operatorOperation as op

def main():
    print("Running...")
    uo.payCharges(6, 10.48)     #payCharges(userid, amount)
    uo.reportDefective(5)       #reportDefective(bikeid)
    uo.findBike(5, 8)           #findBike(locid, userid)
    uo.returnBike(8, 41, 4)     #returnBike(userid, bikeid, endlocid)
    
    
    op.track_loc()              #Track all locations
    op.repair(10)               #Mark Bike Id as fixed
    op.move(2, 10)              #Move A Bike to specific location
    print("End...")
    
if __name__ == "__main__":
    main()

qry.db.close()                  #Close connection