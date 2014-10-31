import json

entities=dict()

stations = dict()
modules = dict()
actors = dict()

config = {
    'TIME FACTOR' : 24,
    'ZOOM' : 15,
    'GRAPHICS' : 'pyglet',
    'AUTOLOAD': True,
}

def save_config():
    outfile = file('config.txt','w')
    json.dump( config, outfile, indent = 4, separators = (',', ': ') )
    outfile.close()
   
def load_config():
    outfile = file('config.txt','r')
    global config
    config = json.load( outfile )
    outfile.close()
    
#load_config()

scenario = None
universe = None
mousedown=False

