from station import Station
import botex
import math
import globalvars

#nominally, handles everything going on earthside

launch_rate = 1.0 #one rocket per year

class EarthsideStation(Station):
    def __init__(self):
        Station.__init__(self,name='Earthside',location = 'Earthside')
        
    def update(self,dt): #Earthside station is only a placeholder, after all
        pass
    
    def storage_values(self):
        out = dict()
        
        #products for resupply
        out['Food'] = -0.1
        out['Water'] = -0.1
        out['General Consumables'] = -0.1
        out['Parts'] = -0.1
        out['Nitrogen'] = -0.1
        
        #will 'buy' waste products at a small fraction of their value
        out['Brine'] = 0.01
        out['Solid Waste'] = 0.01
        out['Liquid Waste'] = 0.01
                
        return out    

def get_launch_cost(launches = None):
    if not launches: launches = launch_rate
    return 17*math.exp(-launches/3.0) #COMPLETE ass-pull, to make the numbers work out for atlas (1/yr) vs falcon9 (4/yr)
    
        
globalvars.earthside = EarthsideStation()        
        
if __name__ == "__main__":
    
    station = Station()
    
    transfer = Station()

    #print botex.LowOrbitLocation(botex.earth).altitude()
    #print botex.Course(botex.fetchLocation(station.location),botex.fetchLocation(globalvars.earthside.location)).deltavee()
    
    '''print botex.Course(botex.earthSurface,botex.lowEarthOrbit).deltavee()
    print botex.Course(botex.earthSurface,botex.highEarthOrbit).deltavee()        
    print botex.Course(botex.earthSurface,botex.stationaryEarthOrbit).deltavee()    
    print get_launch_cost(),get_launch_cost(4.0)
    print
    print botex.plot(botex.earthSurface,botex.marsSurface)
    '''
    
    from time import sleep         
    test = Station('Test Station')        
    
    import module
    import actors
    import util

    test.modules.append(module.SolarPowerModule().id)
    test.modules.append(module.BasicLivingModule().id)
    #test.modules.append(module.BasicHydroponicsModule().id)        
    test.modules.append(module.BasicHabitationModule().id)
    test.modules.append(module.GenericEngineModule().id)    
        
    act = actors.Human()    
    test.actors.append(act.id)
    
    test.init_storage_std()
    
    #print 'Stationkeeping:',test.stationKeepingDeltavee(util.seconds(1,'year'))
    #print test.burn(10)
    #quit()
            
    for i in range(1,1000):
        print 'i:', i
        test.update(globalvars.config['TIME FACTOR']*1000*0.5)      
        print util.timestring(globalvars.config['TIME FACTOR']*1000*0.5*i)
        #pprint.pprint(test.storage)
        test.print_output()
        sleep(0.05)    
    test.earthside_resupply()
