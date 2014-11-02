from station import Station
import botex

#nominally, handles everything going on earthside

class EarthsideStation(Station):
    def __init__(self):
        Station.__init__(self,name='Earthside',location = 'Earthside')
        
    def update(self,dt): #Earthside station is only a placeholder, after all
        pass
    
        
        
if __name__ == "__main__":
    earth = EarthsideStation()
    station = Station()
    
    print botex.Course(botex.fetchLocation(earth.location),botex.fetchLocation(station.location)).deltavee()
