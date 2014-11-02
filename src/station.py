import util
import globalvars
import math
import pprint
import job
import botex

intangibles = ['Power','SolarPower','AdminPts','Living Space','Toilet Capacity','Habitation','Volume']
intangibles.extend(job.joblist.keys())
intangibles.extend([j.split('Job')[0] for j in job.joblist.keys()])

class Station:
    def __init__(self,name=None,location=None):    
        self.id = util.register(self,'station')
        self.location = location if location else 'LEO'
        self.storage = dict()
        self.actors = []
        self.modules = []
        self.jobs = []
        self.res_capacity = 1 #kg
        self.name = name if name is not None else "Generic Station" #TODO write witty station name generator
                
        self.reaction_base = []
        self.reaction_actv = []
        
        self.refresh_config = True
        self.efficiency = 1.0
        
        self.storage['Power'] = 0
        self.storage['AdminPts'] = 10        
               
        self.storage_limit = 1.0 * util.seconds(6,'months')
        self.storage_prev = dict()       
        self.storage_usage = dict()       
        self.storage_avg = dict()     
        
        self.nontradeable = ['Meals','Carbon Dioxide','Liquid Waste','Oxygen','Gray Water','Hydrogen'] #resources (generally intermediate) THIS station doesn't need or care to trade
        self.nontradeable = ['Meals','Liquid Waste','Gray Water','Hydrogen'] #resources (generally intermediate) THIS station doesn't need or care to trade                  
               
    def add_item(self,item,amt):
        if item in self.storage: 
            self.storage[item] += amt
        else:
            self.storage[item] = amt
        return self.storage[item]
                
    def sub_item(self,item,amt):
        if item in self.storage: 
            self.storage[item] -= amt
            if self.storage[item] < 0: self.storage[item] = 0
        else:
            return 0
        return self.storage[item]
               
    def get_item(self,item):
        if item not in self.storage: self.storage[item] = 0
        return self.storage[item]       
               
    def update(self,dt):            
    
        self.atrophy_intangible_resources(dt)        
        
        if self.refresh_config:
            self.reaction_base = []
            self.reaction_actv = []
        
            #add innate resource use
            #self.reaction_base.append( {'Name':'placeholder', 'Inputs':{'Foo':0.1}, 'Outputs':{'Bar':0.1} } )
            self.reaction_base.append( {'Name':'placeholder', 'Inputs':{}, 'Outputs':{'AdminPts':5.2} } )
            
            
            for a in self.actors:
                #add actor resource use
                pass
            for m in self.modules:
                #add module resource use
                mod = globalvars.modules[m]
                #bas,act = mod.get_reactions()
                #self.reaction_base.extend(bas)
                #self.reaction_actv.extend(act)                                                                                    
                       
                       
        for a in self.actors:
            act = globalvars.actors[a]
            act.update(self,dt)                                   
        
        for m in self.modules:            
            mod = globalvars.modules[m]
            if not mod.active: continue
            mod.update(self,dt)
                        
        for r in self.reaction_base:
            self.satisfy_reaction(r,dt)
                                        
        
        #any necessary resource tweaking - power, admin, etc
        if 'SolarPower' in self.storage:
            irradiance = 1.366 #kW/m^2, Earth orbit
            efficiency = .22
            kw_to_mj = (dt/3600)
            self.add_item('Power',self.storage['SolarPower']*irradiance*efficiency*(dt/3600.0)*3.6) #m2 * (kW/m2) * (eff) * (s * (hr/s)) * (mJ/kW)             
            self.storage['SolarPower'] = 0
                                                                
        #calculate efficiency for station utilization, next time
            #jobs
            #air pressure/quality
            #meals
            
        #calculate resource change
        for s in self.storage:
            if s in intangibles: continue
            if s not in self.storage_prev: 
                self.storage_prev[s] = 0
                self.storage_avg[s] = self.storage[s] 
            else:                
                self.storage_avg[s] *= max(1-dt/self.storage_limit,0)
                self.storage_avg[s] += self.storage[s]*min(dt/self.storage_limit,1)
                                
                _diff = self.storage[s] - self.storage_prev[s]
                if s not in self.storage_usage: self.storage_usage[s] = _diff/dt
                #print s, _diff, max(1-dt/self.storage_limit,0), min(dt/self.storage_limit,1)
                self.storage_usage[s] *= max(1-dt/self.storage_limit,0)
                self.storage_usage[s] += (_diff/dt)*min(dt/self.storage_limit,1)
                
                
    
        #reset last_storage
        for s in self.storage:
            self.storage_prev[s] = self.storage[s]
        
        
    def satisfy_reaction(self,reaction,dt):
        r = reaction
        eff = self.efficiency
        tick = util.seconds(1,'day')
        if 'Inputs' in r:
            for i in r['Inputs']:
                if i not in self.storage: 
                    eff = 0.0
                    break            
                eff = min( eff, self.storage[i]/(1.0*r['Inputs'][i]/tick*dt) ) if r['Inputs'][i] > 0 else 0.0
        if eff > 0.0:
            if 'Inputs' in r:
                for i in r['Inputs']:
                    self.storage[i] -= eff*r['Inputs'][i]/tick*dt
            if 'Outputs' in r:
                for o in r['Outputs']:
                    if r['Outputs'][o] == 0: continue
                    self.add_item(o, eff*r['Outputs'][o]/tick*dt)
        return eff
        
        
    def atrophy_intangible_resources(self,dt):
    
        #power, things that should be nearly instant
        res = ['Power']
        tc = util.seconds(2,'hours')
        self._atrophy_res(res,tc,dt)
        
        #meals, things that decay
        res = ['Meals']
        tc = util.seconds(1,'week')
        self._atrophy_res(res,tc,dt)
      
        #resource activity
        #CO2 removal - just dumped off the station
        '''safe_co2 = 0.05
        tot_gas = (self.get_item('Carbon Dioxide') + self.get_item('Oxygen') + self.get_item('Nitrogen')) #does not take into account MW of gases, TODO fix
        excess_co2 = self.storage['Carbon Dioxide'] / tot_gas
        if excess_co2 > safe_co2:
            pur = self.storage['AirPurification']
            co2_to_remove = min(pur,tot_gas*(excess_co2 - safe_co2))
            self.sub_item('Carbon Dioxide',co2_to_remove)
        self.storage['AirPurification'] = 0'''
        
        #water purification
        '''water_to_filter = min(self.get_item('WaterPurification'),self.get_item('Liquid Waste'))
        self.sub_item('Liquid Waste',water_to_filter)
        self.add_item('Water',water_to_filter)
        self.storage['WaterPurification'] = 0'''
        
        #gas leakage
        leak = 0.0001/util.seconds(1,'day') #.01%/day
        for r in ['Oxygen','Nitrogen','Carbon Dioxide']:
             self.sub_item(r,leak*dt*self.get_item(r))
        for r in ['Hydrogen']:
             self.sub_item(r,100*leak*dt*self.get_item(r))
                 
        #everything else
        res = ['AdminPts','Living Space','Toilet Capacity','Hydro','Maintenance','Sanitation','Habitation','Volume']
        tc = util.seconds(24,'hours')        
        self._atrophy_res(res,tc,dt)        
        
    def _atrophy_res(self,res,tc,dt):
        frac = math.exp(-1.0*dt/tc)
        for r in res:
            if not r in self.storage: continue
            self.storage[r] *= frac
        
    def gas_pp(self,gas='Oxygen'):
        tot_volume = self.get_item('Volume')+1
        gas_const = 8.3144621e-3 #m^3 kPa mol-1 K-1   
        #mass to mol
        mass2mol = 16 if gas is 'Oxygen' else 22 if gas is 'Carbon Dioxide' else 14 if gas is 'Nitrogen' else 2 #hydrogen
        mass = self.get_item(gas)
        _pp = (mass*1000.0/mass2mol) * gas_const * 295 / tot_volume
        return _pp
        
    def tot_pp(self):
        tot=0
        for g in ['Oxygen','Nitrogen','Carbon Dioxide','Hydrogen']:
            tot += self.gas_pp(g)
        return tot
        
    def storage_values(self):
        out = dict()
        for s in self.storage_usage:
            if s in self.nontradeable: continue
            out[s] = self.storage_limit/(-1*self.storage_avg[s]/self.storage_usage[s]) if self.storage_usage[s] and self.storage_avg[s]/self.storage_usage[s] else 0
        return out        
        
    def print_output(self):
        #convenience function to change what's being printed        
        prior = self.storage_values()
        for p in sorted(prior.keys(), key= lambda a: prior[a], reverse = True):
            print p, prior[p], self.storage[p]
        
        
        
if __name__ == "__main__":
    from time import sleep         
    test = Station('Test Station')        
    
    test.storage['Oxygen'] = 5
    test.storage['Food'] = 1000
    test.storage['Water'] = 1000
    test.storage['Nitrogen'] = 100
    test.storage['General Consumables'] = 1000
    test.storage['Parts'] = 100
    
    import module
    import actors
    mod = module.SolarPowerModule()
    test.modules.append(mod.id)    

    test.modules.append(module.BasicLivingModule().id)
    test.modules.append(module.BasicHydroponicsModule().id)
        
    mod = module.BasicHabitationModule()
    test.modules.append(mod.id)
    
    act = actors.Human()    
    test.actors.append(act.id)
        
    for i in range(1,30000):
        print 'Oxygen:', test.gas_pp('Oxygen')
        test.update(globalvars.config['TIME FACTOR']*1000*0.5)      
        print util.timestring(globalvars.config['TIME FACTOR']*1000*0.5*i)
        pprint.pprint(test.storage)
        #test.print_output()
        sleep(0.05)
