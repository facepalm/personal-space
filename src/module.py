import util

#notes
#power: 1 kW per day = 86.4 MJ

class Module(object):
    def __init__(self):
        self.id = util.register(self,'module')

        #metadata
        self.station=None
        
        self.active = True #if false, stations will ignore this module
        self.mass = 24000 # kg, gonna need to refactor this  
      
        self.reaction_base = []
        self.reaction_actv = []
      
        self.res_capacity = 1        
                        
        # all modules need an admin point - represents the abstract ability to know what's going on with the station
        # could have an in-game effect for underfilling: station would "go dark" and some events would not be shown
        self.admin_need= {'Name':'placeholder', 'Inputs':{'AdminPts':1.0}, 'Outputs':{} }                    

        self.priority = 0.5
        
    def set_station_owner(self,station):
        self.station = station
        
    def get_reactions(self):
        return [self.reaction_base, self.reaction_actv]
        
    def update(self,station,dt):
        #if station.satisfy_reaction(self.admin_need,dt) < 0.9:
        #    print "Station disabling!"            
        #    self.active = False 
        for r in self.reaction_base:
            station.satisfy_reaction(r,dt)
        
class SolarPowerModule(Module):
    def __init__(self):
        Module.__init__(self)     
        self.reaction_base.append( {'Name':'placeholder', 'Inputs':{}, 'Outputs':{'SolarPower': 960.0} } ) #m^2 of solar array
        self.mass = 4000 #kg
        self.priority = 0.0
                       
class MicrowavePowerAntenna(Module):
    def __init__(self):
        Module.__init__(self)     
        self.mass = 10000 #kg
        self.priority = 1.0
        
    def update(self,station,dt):
        Module.update(self,station,dt)
        
        assert station.location in ['LEO','GEO','ISS']
        
        power_available = station.storage['Power']
        station.sub_item('Power',power_available)
        
        station.financial_account += power_available * 0.85 / 3.6 * 0.08 #TODO add more dynamic price calculations
                       
class BasicInsideModule(Module):
    '''generic atmosphere-filled module'''
    def __init__(self):
        Module.__init__(self)             
        self.reaction_base.append( {'Name':'Habitation', 'Inputs':{}, 'Outputs':{'Volume':116.0} } ) #m^3, based on Destiny module
        self.reaction_base.append( {'Name':'Habitation', 'Inputs':{}, 'Outputs':{'Living Space':39.0} } ) #m^3, based on Destiny module
        self.reaction_base.append( {'Name':'Upkeep', 'Inputs':{}, 'Outputs':{'SanitationJob':0.01} } )                           
        self.reaction_base.append( {'Name':'Upkeep', 'Inputs':{}, 'Outputs':{'MaintenanceJob':0.01} } )                           

class DragonCargoModule(Module):    
    def __init__(self):
        Module.__init__(self)             
        self.mass = 4200 #dry mass kg
        self.reaction_base.append( {'Name':'Habitation', 'Inputs':{}, 'Outputs':{'Volume':10.0} } ) #m^3, based on Destiny module
        self.reaction_base.append( {'Name':'Habitation', 'Inputs':{}, 'Outputs':{'Living Space':10.0} } ) #m^3, based on Destiny module
        self.reaction_base.append( {'Name':'Upkeep', 'Inputs':{}, 'Outputs':{'SanitationJob':0.001} } )                           
        self.reaction_base.append( {'Name':'Upkeep', 'Inputs':{}, 'Outputs':{'MaintenanceJob':0.001} } )
        self.reaction_base.append( {'Name':'SolarPower', 'Inputs':{}, 'Outputs':{'SolarPower': 4.5 } } ) #m^2 of solar array
        
        self.isp = 330 
        #55.2 26
        self.propellant = {'MMH':0.32,'NTO':0.68}

        
                       
class BasicHabitationModule(BasicInsideModule):
    '''Provides living space, meals, sanitation and beds for three people'''
    def __init__(self):
        BasicInsideModule.__init__(self)             
        self.reaction_base.append( {'Name':'Habitation', 'Inputs':{}, 'Outputs':{'Habitation':3.0} } )                            

class BasicLivingModule(BasicInsideModule):
    '''Provides life support, maintenance for three people'''    
    def __init__(self):
        BasicInsideModule.__init__(self)                                 
        self.reaction_base.append( {'Name':'Habitation', 'Inputs':{}, 'Outputs':{'Toilet Capacity':3.0} } )        
        self.filtration = {'Name':'Lifesupport', 'Inputs':{'Power':43.2,'Liquid Waste':5.0}, 'Outputs':{'Gray Water':4.5, 'Brine': 0.5} }
        self.distillation = {'Name':'Lifesupport', 'Inputs':{'Power':43.2,'Gray Water':5.0}, 'Outputs':{'Water':4.95, 'Brine': 0.05} }        
        self.scrubbing = { 'Name':'Scrubbing', 'Inputs':{'Power':86.4, 'Carbon Dioxide':2.0},'Outputs':{} }
        self.electrolysis = { 'Name':'Electrolysis', 'Inputs':{'Power':3.0*86.4, 'Water':0.5*24},'Outputs':{'Oxygen':0.5*24*8/10 }} #,'Hydrogen':2.5*24*2/10} } #maybe H2 later
    
    def update(self,station,dt):
        Module.update(self,station,dt)
        
        O2_pp = station.gas_pp('Oxygen')
        tot_pp = station.tot_pp()
        if O2_pp < 20 or tot_pp < 40:
            #electrolyze water
            station.satisfy_reaction(self.electrolysis,dt)
            
        CO2_pp = station.gas_pp('Carbon Dioxide')    
        if CO2_pp > 5:
            station.satisfy_reaction(self.scrubbing,dt)            
            
        if station.get_item('Liquid Waste'):
            station.satisfy_reaction(self.filtration,dt)            

        if station.get_item('Gray Water'):
            print station.get_item('Water'), station.get_item('Gray Water')
            station.satisfy_reaction(self.distillation,dt)                    
        
class GenericEngineModule(Module):
    def __init__(self):
        Module.__init__(self)
        
        #based loosely on the NK-33
        self.mass = 1200
        self.isp = 330 
        self.propellant = {'RP-1':0.25,'LOX':0.75}

        
class BasicHydroponicsModule(BasicInsideModule):
    def __init__(self):
        BasicInsideModule.__init__(self)                                 
        self.biomass = 0.01 #kg of plant matter
        self.growth_area = 125 #m^2, roughly the outer surface area of a Destiny-sized module
        self.lights=1.0
        self.reaction_base.append( {'Name':'Hydro', 'Inputs':{}, 'Outputs':{'HydroJob':0.3} } )        
        
        #from A biological method of including mineralized human liquid and solid wastes into the mass exchange of bio-technical life support systems
        #299g/plant total mass (wheat)
        #133g/plant edible mass
        #0.128 m^2 per plant
        #70-day growth period
                
    def update(self,station,dt):
        Module.update(self,station,dt)
        
        #new_work = station.satisfy_reaction({'Name':'Botanical Growth', 'Inputs':{'Hydro':0.05 }, 'Outputs':{} },dt)

        #decay is much more appropriate for a more garden-like style of greenhouse
        #new_decay = station.satisfy_reaction({'Name':'Botanical Decay', 'Inputs':{ 'Oxygen':self.biomass/100.0 }, 'Outputs':{'Carbon Dioxide':self.biomass/100.0*(22.0/16) } },dt)        
        #self.biomass = new_decay*dt
       
        #TODO change to sigmoid function
        lights = station.satisfy_reaction({'Name':'Hydro Lighting','Inputs':{'Power':5.0*86.4}},dt)
        work = station.satisfy_reaction({'Name':'Botany', 'Inputs':{'Hydro':0.05} },dt)                
        
        photosynthesis = station.satisfy_reaction({'Name':'Photosynthesis', 'Inputs':{'Carbon Dioxide':self.biomass, 'Gray Water':self.biomass }, 'Outputs':{'Oxygen':self.biomass*(16/22.0), 'Food':self.biomass} },dt)
        
        if photosynthesis < 1.0:
            #try again with pure water
            photosynthesis += (1-photosynthesis)*station.satisfy_reaction({'Name':'Photosynthesis', 'Inputs':{'Carbon Dioxide':self.biomass, 'Water':self.biomass }, 'Outputs':{'Oxygen':self.biomass*(16/22.0), 'Food':self.biomass} },(1-photosynthesis)*dt)

        time_const = util.seconds(2,'months')
        self.biomass += photosynthesis*dt/1000000.0 - dt*self.biomass/time_const/1000000.0        
        
        print photosynthesis, self.biomass    
        #self.reaction_base.append( {'Name':'Hydro', 'Inputs':{'Hydro':1}, 'Outputs':{'Food':1.0} } )        
        
        #self.reaction_base.append( {'Name':'Hydro', 'Inputs':{'Power':2.0,'Water':1.0,'Carbon Dioxide':}, 'Outputs':{'Food':1.0} } )
        
