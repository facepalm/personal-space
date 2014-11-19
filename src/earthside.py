from station import Station
import botex
import math
import globalvars
import module
import random
import util

#nominally, handles everything going on earthside

launch_rate = 1.0 #one rocket per year

def get_launch_cost(launches = None):
    if not launches: launches = launch_rate
    return 16000*math.exp(-math.log(launches)/math.log(3.0)) #COMPLETE ass-pull, to make the numbers work out for atlas (1/yr) vs falcon9 (4/yr)

#tourism modeling
#data points: 
#   Real space tourism - 20M, 1 visitor per year, about twice launch cost (ish)
#   Hawaii - 200*10*2 = 4k, 8000000 visitor per year
#   Extrapolation: 
#   8000000 = A*math.exp(-math.log(4000)/B)
#   1 = A*math.exp(-math.log(20000000)/B)
#   8000000 = math.exp(-math.log(4000)/B)/math.exp(-math.log(20000000)/B)
#   B = 0.535
#   A = 44338912668553.06

class LaunchAgency(object):
    def __init__(self):
        pass
        
    def update(self,dt):
        for s in globalvars.stations.values():
            pass


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
        if stat.location not in ['LEO','GEO','ISS','HEO']: return False
        dv = botex.Course(botex.earthSurface,botex.fetchLocation(stat.location)).deltavee()
        amount_to_ship = 13150* (10.366/(math.exp((dv)/(450*9.8)) - 1))
        if stat.financial_account < amount_to_ship*get_launch_cost(): return False #cost of launch + supplies
        
        cargo_vessel = Station()
        cargo_vessel.location = stat.location
        #cargo_vessel.modules.append(module.DragonCargoModule().id)
        #cargo_vessel.add_item('MMH',412.8)
        #cargo_vessel.add_item('NTO',877.2)
        
        #check sum
        tot = 0
        for a in amt:
            assert amt[a] > 0
            tot += amt[a]*amount_to_ship
            cargo_vessel.add_item(a,amount_to_ship*amt[a])
        
        assert tot <= 14000 #3320
        #print amount_to_ship, tot
        #quit()
        
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
    
    #station = Station()
    
    #transfer = Station()

    #print botex.LowOrbitLocation(botex.earth).altitude()
    #print botex.Course(botex.fetchLocation(station.location),botex.fetchLocation(globalvars.earthside.location)).deltavee()
    
    #leoDV =  botex.Course(botex.earthSurface,botex.lowEarthOrbit).deltavee()    
    #geoDV = botex.Course(botex.earthSurface,botex.stationaryEarthOrbit).deltavee()
    #dv = isp*9.8*math.log(m0/m1)
    #print leoDV
    #print botex.Course(botex.earthSurface,botex.stationaryEarthOrbit).deltavee()    
    #print botex.Course(botex.lowEarthOrbit,botex.stationaryEarthOrbit).deltavee()     
    #fuel = math.exp(leoDV/(450*9.8))-1
    #print fuel
    #leogeoDV = 450*9.8*math.log(fuel+m1/m1)
    # fuel+m1/m1 = math.exp(leogeoDV/(450*9.8))
    #fuel = (math.exp(leogeoDV/(450*9.8)) - 1)*m1
    #m1 = fuel/(math.exp(leogeoDV/(450*9.8)) - 1)    
    #print fuel/(math.exp((leoDV)/(450*9.8)) - 1)
    #quit()
    '''print botex.Course(botex.earthSurface,botex.highEarthOrbit).deltavee()        
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
    for r in range(1,350):
        test.modules.append(module.SolarPowerModule().id)
    
        
    #test.modules.append(module.BasicLivingModule().id)
    #test.modules.append(module.BasicHydroponicsModule().id)        
    #test.modules.append(module.BasicHabitationModule().id)
    test.modules.append(module.GenericLH2LOXEngineModule().id)    
    test.modules.append(module.LH2ElectrolysisModule().id)        
        
    test.modules.append(module.MicrowavePowerAntenna().id)    

    test.add_item('Water',10000)
    test.financial_account = 1000000000            
    #act = actors.Human()    
    #test.actors.append(act.id)
    
    test.init_storage_std()
    test.location = 'GEO'
    #print 'Stationkeeping:',test.stationKeepingDeltavee(util.seconds(1,'year'))
    #print test.burn(10)
    #quit()
    
    test2 = Station('Tourist Test Station')        
    test2.modules.append(module.SolarPowerModule().id)    
        
    test2.modules.append(module.BasicLivingModule().id)
    #test2.modules.append(module.BasicHydroponicsModule().id)        
    test2.modules.append(module.BasicHabitationModule().id)    
    
    test2.financial_account = 1000000000            
    test2.init_storage_std()
    
    act = actors.Human()    
    test2.actors.append(act.id)
    
            
    for i in range(1,100000):
        #print 'i:', i
        print
        for s in globalvars.stations.keys():
            globalvars.stations[s].update(globalvars.config['TIME FACTOR']*10000*0.5)
            if not globalvars.stations[s].modules and s != globalvars.earthside:
                del globalvars.stations[s]
        #test.update(globalvars.config['TIME FACTOR']*10000*0.5)            
        print util.timestring(globalvars.config['TIME FACTOR']*10000*0.5*i)
        #pprint.pprint(test.storage)
        print 'Launch cost: ',get_launch_cost(), launch_rate
        test2.print_output()
        sleep(0.05)    

