from station import Station
import botex
import math
import globalvars
import module
import random

#nominally, handles everything going on earthside

launch_rate = 1.0 #one rocket per year

def get_launch_cost(launches = None):
    if not launches: launches = launch_rate
    return 16000*math.exp(-math.log(launches)/math.log(3.0)) #COMPLETE ass-pull, to make the numbers work out for atlas (1/yr) vs falcon9 (4/yr)

class EarthsideStation(Station):
    def __init__(self):
        Station.__init__(self,name='Earthside',location = 'Earthside')
        
        for i in ['Food','Water','General Consumables','Parts','Nitrogen','Brine','Solid Waste','Liquid Waste']:
            self.storage_avg_price[i] = 0
            self.storage_tariff[i] = get_launch_cost()
        
    def update(self,dt): #Earthside station is only a placeholder, after all
        global launch_rate
        launch_rate *= max(0,1 - dt/util.seconds(1,'year') )
        
        #gov't launches keep the cost down
        if random.random()/10.0 < dt/util.seconds(1,'year'):
            launch_rate += 1
    
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

    def send_resupply(self,stat_id,amt):
        '''Station stat_id wants amt goods'''
        #sanity checks
        print amt
        if stat_id not in globalvars.stations: return False
        stat = globalvars.stations[stat_id]
        if stat.location != 'LEO': return False
        if stat.financial_account < 10000*get_launch_cost(): return False #cost of launch + supplies
        
        cargo_vessel = Station()
        #cargo_vessel.modules.append(module.DragonCargoModule().id)
        #cargo_vessel.add_item('MMH',412.8)
        #cargo_vessel.add_item('NTO',877.2)
        
        #check sum
        tot = 0
        for a in amt:
            assert amt[a] > 0
            tot += amt[a]
            cargo_vessel.add_item(a,amt[a])
        
        assert tot <= 14000 #3320
        
        stat.financial_account -= get_launch_cost()*cargo_vessel.mass
        
        global launch_rate
        launch_rate += 1
        
        #launched!  WOOO!
        print 'LAUNCHED!',amt
        
        #dock vessel to stat
        #cargo_vessel.home_station = stat_id
        #cargo_vessel.home_relationship = 'Wholly-Owned Subsidiary'
        cargo_vessel.dock(stat_id)
        return True
        
globalvars.earthside = EarthsideStation().id        
        
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
    
    #Solar Power Plant
    for r in range(1,250):
        test.modules.append(module.SolarPowerModule().id)
    
        
    test.modules.append(module.BasicLivingModule().id)
    #test.modules.append(module.BasicHydroponicsModule().id)        
    test.modules.append(module.BasicHabitationModule().id)
    test.modules.append(module.GenericEngineModule().id)    
        
    test.modules.append(module.MicrowavePowerAntenna().id)    

    test.financial_account = 1000000000
        
    act = actors.Human()    
    test.actors.append(act.id)
    
    test.init_storage_std()
    
    #print 'Stationkeeping:',test.stationKeepingDeltavee(util.seconds(1,'year'))
    #print test.burn(10)
    #quit()
            
    for i in range(1,100000):
        #print 'i:', i
        for s in globalvars.stations.values():
            s.update(globalvars.config['TIME FACTOR']*10000*0.5)
        #test.update(globalvars.config['TIME FACTOR']*10000*0.5)            
        print util.timestring(globalvars.config['TIME FACTOR']*10000*0.5*i)
        #pprint.pprint(test.storage)
        print 'Launch cost: ',get_launch_cost(), launch_rate
        test.print_output()
        sleep(0.05)    
    test.earthside_resupply()
