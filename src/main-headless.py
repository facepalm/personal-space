import earthside
from station import Station
import module
import actors
import util
import tourism
import globalvars
from time import sleep

if __name__ == "__main__":
    
    hotelStation = Station('Tourism Station')
    hotelStation.location = 'LEO'
    
    #basic staff modules
    hotelStation.modules.append(module.SolarPowerModule().id)    
    hotelStation.modules.append(module.BasicLivingModule().id)
    hotelStation.modules.append(module.BasicHabitationModule().id)    
    hotelStation.modules.append(module.GenericEngineModule().id)
        
    hotelStation.financial_account = 1000000000            
    
    
    #three staff
    for a in range(3):
        act = actors.Human()    
        hotelStation.actors.append(act.id)
    
    #tourist accomodations
    hotelStation.modules.append(tourism.StandardHabitationModule().id)    
    hotelStation.modules.append(tourism.StandardHabitationModule().id)    
    hotelStation.modules.append(tourism.DeluxeHabitationModule().id)        
    hotelStation.modules.append(tourism.ZeroGymModule().id)    
    hotelStation.modules.append(tourism.Cupola().id)    

    hotelStation.init_storage_std()

    i=0    
    while True:
        i += 1        
        print
        for s in globalvars.stations.keys():
            globalvars.stations[s].update(globalvars.config['TIME FACTOR']*10000*0.5)
            if not globalvars.stations[s].modules and s != globalvars.earthside:
                del globalvars.stations[s]
        print util.timestring(globalvars.config['TIME FACTOR']*10000*0.5*i)
        #print 'Launch cost: ',earthside.get_launch_cost(), earthside.launch_rate
        #hotelStation.print_output()
        sleep(0.05)    

