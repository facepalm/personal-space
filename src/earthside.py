from station import Station
import botex

#nominally, handles everything going on earthside

class EarthsideStation(Station):
    def __init__(self):
        Station.__init__(self,name='Earthside',location = botex.earthSurface)
        
    def update(self,dt): #Earthside station is only a placeholder, after all
        pass
    
        
        
if __name__ == "__main__":
    earth = EarthsideStation()
    station = Station(location=botex.stationaryEarthOrbit)
    
    print botex.Course(earth.location,station.location).deltavee()
