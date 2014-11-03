from station import Station
import botex
import math

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
    
        
if __name__ == "__main__":
    earth = EarthsideStation()
    station = Station()
    
    transfer = Station()

    
    print botex.Course(botex.fetchLocation(station.location),botex.fetchLocation(earth.location)).deltavee()
    print get_launch_cost(),get_launch_cost(4.0)
    
