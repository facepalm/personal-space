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
        self.accumulatedDeltavee = 0.0 #leftover dv from unmet stationkeeping burns.  Need to be spent for rendevous
        self.storage = dict()
        self.actors = []
        self.modules = []
        self.jobs = []
        self.res_capacity = 1 #kg
        self.name = name if name is not None else "Generic Station" #TODO write witty station name generator
        
        self.home_station = None
        self.home_relationship = None
        
        self.account = 1000000000 #one BILLION dollars!
                
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
        #self.nontradeable = ['Meals','Liquid Waste','Gray Water','Hydrogen'] #resources (generally intermediate) THIS station doesn't need or care to trade                  
               
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
        
        #burn for stationkeeping
        dv = self.stationKeepingDeltavee(dt)
        sk = self.burn(dv)
                       
                       
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
                self.storage_avg[s] *= max(1-dt/(self.storage_limit/3.0),0)
                self.storage_avg[s] += self.storage[s]*min(dt/(self.storage_limit/3.0),1)
                                
                _diff = self.storage[s] - self.storage_prev[s]
                if s not in self.storage_usage: 
                    self.storage_usage[s] = _diff/dt
                else:
                    #print s, _diff, max(1-dt/self.storage_limit,0), min(dt/self.storage_limit,1)
                    self.storage_usage[s] *= max(1-dt/(self.storage_limit/3.0),0)
                    self.storage_usage[s] += (_diff/dt)*min(dt/(self.storage_limit/3.0),1)
                    
                
    
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
            #out[s] = self.storage_limit/(-1*self.storage_avg[s]/self.storage_usage[s]) if self.storage_usage[s] and self.storage_avg[s]/self.storage_usage[s] else 0
            out[s] = -1.0*(self.storage_usage[s]*self.storage_limit)/self.storage[s] if self.storage[s] else 0 
            #out[s] = self.storage_avg[s]/(self.storage_usage[s]*3*self.storage_limit) if self.storage_usage[s] else 0 
        return out        
        
    def print_output(self):
        #convenience function to change what's being printed        
        prior = self.storage_values()
        for p in sorted(prior.keys(), key= lambda a: prior[a], reverse = True):
            print p, prior[p], self.storage[p], self.storage_usage[p]*self.storage_limit
        
    def init_storage_std(self):
        mod_count = len(self.modules)
        self.storage['Oxygen'] = 10 * mod_count
        self.storage['Food'] = 100 * mod_count
        self.storage['Water'] = 100 * mod_count
        self.storage['Nitrogen'] = 100 * mod_count
        self.storage['General Consumables'] = 50 * mod_count
        self.storage['Parts'] = 50 * mod_count
        self.storage['RP-1'] = 100 * mod_count
        self.storage['LOX'] = 300 * mod_count        
        
    def earthside_resupply(self):
        '''Buy goods from Earth. Limited to whatever can be crammed in a Dragon capsule'''        
        if self.location != 'LEO' or not globalvars.earthside: return None
        print 'Earthside resupply!'
        val = self.storage_values()
        amt = dict()
        max_amt = 3310 #kgs to LEO.  
        #calculate total mass need
        tot_mass = 0.0
        for p in sorted(val.keys(), key= lambda a: val[a], reverse = True):
            if val[p] >= 1: tot_mass += -1*self.storage_usage[p]*self.storage_limit
        print tot_mass
        
        tot_val = 0.0
        for p in sorted(val.keys(), key= lambda a: val[a], reverse = True):
            if val[p] >= 0: tot_val += val[p]*-1*self.storage_usage[p]
            
        for p in sorted(val.keys(), key= lambda a: val[a], reverse = True):
            if val[p] >= 0: amt[p] = max_amt*(val[p]*-1*self.storage_usage[p]/tot_val)
        print amt
        return
        
    def get_mass(self):
        mass = 0
        for r in self.storage:
            if r not in intangibles: 
                mass += self.storage[r]
        for m in self.modules:
            mod = globalvars.modules[m]
            mass += mod.mass
        for a in self.actors:
            act = globalvars.actors[a]
            mass += act.mass
        return mass        
    mass = property(get_mass, None, None, "Mass of station" )         
        
    def get_max_dv_engine(self):
        best_dv = 0
        best_mod = None
        m0 = self.get_mass()
        g0 = 9.8 #m/s^2
        for m in self.modules:
            mod = globalvars.modules[m]
            if not mod.active or not hasattr(mod,'isp'): continue
            prop_max = None
            for r in mod.propellant:
                prop_new = self.get_item(r)/(1.0*mod.propellant[r])
                prop_max = prop_new if not prop_max else min(prop_max,prop_new)
            m1 = m0 - prop_max            
            dv = mod.isp * g0 * math.log(m0/m1)
            if dv > best_dv:
                best_dv = dv
                best_mod = m
        return (best_mod, best_dv)                
                
        
    def burn(self,dv):
        b_mod, b_dv = self.get_max_dv_engine()
        if b_dv < dv: return False #we don't have the fuel for the requested burn
        g0 = 9.8 #m/s^2
        mod = globalvars.modules[b_mod]
        #dv = isp*g0*log(m0/m1)
        #dv/(isp*g0) = log(m0/m1)
        #exp(dv/(isp*g0)) = m0/m1
        #m1 = m0/exp(dv/(isp*g0))
        m0=self.mass
        m1 = m0/math.exp(dv/(mod.isp*g0))
        burn_mass = m0-m1
        for r in mod.propellant:
            self.sub_item(r,burn_mass*mod.propellant[r])
        return True

    def stationKeepingDeltavee(self,dt):
        loc_sk = botex.fetchLocation(self.location).stationKeeping()
        return loc_sk*dt
        
    #trade pseudocode - to be performed by the trading vessel
        #home = get home station
        #potential = get random station, weighted by dv, of a random selection of other stations
        #home_val = home values
        #home_amt = home usage
        #pot_val, pot_amt = potential, same thing
        
        #avg_val = mean values, weighted by respective trading partners' skill
        #sum_usg = sum of respective usages, representing the amount that's available for trade at this price
        
        
if __name__ == "__main__":
    from time import sleep         
    test = Station('Test Station')        
    
    import module
    import actors

    test.modules.append(module.SolarPowerModule().id)
    test.modules.append(module.BasicLivingModule().id)
    #test.modules.append(module.BasicHydroponicsModule().id)        
    test.modules.append(module.BasicHabitationModule().id)
        
    act = actors.Human()    
    test.actors.append(act.id)
    
    test.init_storage_std()
            
    for i in range(1,30000):
        print 'Oxygen:', test.gas_pp('Oxygen')
        test.update(globalvars.config['TIME FACTOR']*1000*0.5)      
        print util.timestring(globalvars.config['TIME FACTOR']*1000*0.5*i)
        #pprint.pprint(test.storage)
        test.print_output()
        sleep(0.05)
