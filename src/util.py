import logging
import numpy as np
import string
import globalvars
import uuid
import pickle
import os

#TIME_FACTOR = 168 # 1 irl hour = 1 week
#TIME_FACTOR = 24 # 1 irl hour = 1 day
#TIME_FACTOR = 120

#ZOOM = 15

equipment_targets = dict()

#GRAPHICS = None
GLOBAL_X=0
GLOBAL_Y=0

def radian(deg):
    return 3.14159*deg/180

def degree(rad):
    return 180*rad/3.14159

def register(obj, category = None, oid=''):
    new_id = oid if oid else str(uuid.uuid4())
    place = globalvars.modules if category == 'module' else globalvars.actors if category == 'actor' else globalvars.stations if category == 'station' else globalvars.entities
    try:
        place[new_id] = obj
    except:
        assert False, "global id collision!"
    return new_id

def quad_mean(x,y,wx=1,wy=1):
    return pow( (1.0*wx*x*x + wy*y*y)/(wx + wy) ,0.5)
    
def timestring(seconds):
    seconds = int(seconds)
    time='negative ' if seconds < 0 else ''
    seconds = abs(seconds)
    div, rem = (seconds/(2592000*12),seconds%(2592000*12))    
    if div: time = ''.join([time,str(div),' year ' if div==1 else ' years ' ])
    seconds = rem
    div, rem = (seconds/(2592000),seconds%(2592000))    
    if div: time = ''.join([time,str(div),' month ' if div==1 else ' months ' ])
    seconds = rem
    div, rem = (seconds/(86400),seconds%(86400))    
    if div: time = ''.join([time,str(div),' day ' if div==1 else ' days ' ])
    seconds = rem
    div, rem = (seconds/(3600),seconds%(3600))    
    if div: time = ''.join([time,str(div),' hour ' if div==1 else ' hours ' ])
    seconds = rem
    time = ''.join([time,str(seconds),' seconds' ])
    return time    
    
    
    
def seconds(time=1,units='minutes'):
    return time*60 if units == 'minutes' or units == 'minute' \
                                         else time*3600 if units == 'hours' or units == 'hour' \
                                         else time*86400 if units=='days' or units == 'day' \
                                         else time*86400*7 if units=='weeks' or units == 'week' \
                                         else time*2592000 if units=='months' or units == 'month' \
                                         else time*2592000*12 if units=='years' or units == 'year' \
                                         else 10    
                                         
                                         
def short_id(long_id):
    return string.upper(long_id[0:6])                                                
                                         
def separate_node(node):
    if not '|' in node: return False, False
    n=node.split('|')
    return n

def vec_dist(a,b):
    diff = b-a
    return np.sqrt( np.vdot( diff , diff ) )

'''
def autosave():
    datafile = open(os.path.join('save','autosave'),'w')
    pickle.dump(universe,datafile,2)
    datafile.close()
    
def autoload():
    datafile = open(os.path.join('save','autosave'),'r')
    global universe
    universe = pickle.load(datafile)
    datafile.close()
'''

