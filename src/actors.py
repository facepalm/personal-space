import util
import job
import tourism

class Actor(object):
    def __init__(self):
        self.id = util.register(self,'actor')
        self.name = "Placeholder Man"

        self.reaction_base = []
        self.reaction_actv = []
        
        self.reaction_base.append( {'Name':'Clutter', 'Inputs':{}, 'Outputs':{'SanitationJob': .05 } } )

        self.amenity_prefs = tourism.generate_random_amenity_prefs()
        
        self.skill = job.generate_random_skillset()
        self.mass = 80

    def get_reactions(self):
        return [self.reaction_base, self.reaction_actv]
        
    def update(self,station,dt):
        for r in self.reaction_base:
            station.satisfy_reaction(r,dt)

class Human(Actor):
    def __init__(self):
        Actor.__init__(self)
                
        self.respiration = {'Name':'Respiration', 'Inputs':{'Oxygen':0.84}, 'Outputs':{'Carbon Dioxide':1.00} }
        self.hydration = {'Name':'Hydration', 'Inputs':{'Water':3.62}, 'Outputs':{} }
        self.excretion = {'Name':'Excretion', 'Inputs':{}, 'Outputs':{'Solid Waste':0.11, 'Liquid Waste':3.87} }

        #happiness factors.  Failing these draws should hit happiness
        self.comfort_needs = []
        self.comfort_needs.append({'Name':'HabitationMorale', 'Inputs':{'Basic Habitation':1.0}, 'Outputs':{} })
        self.comfort_needs.append({'Name':'PersonalSpace', 'Inputs':{'Living Space':60.0}, 'Outputs':{} }) #m^3 of space needed to be comfortable. #TODO refine
        self.comfort_needs.append({'Name':'PrivateMatters', 'Inputs':{'Toilet Capacity':1.0}, 'Outputs':{} })
        
        self.pref = job.generate_random_skillset()

               
        #other things to model
        #luxuries
        #"wants," hobbies
        #medical
        #social interactions

    def update(self,station,dt):
        Actor.update(self,station,dt)
        _eff = station.satisfy_reaction(self.respiration,dt)       
        
        job_time = dt
        
        if _eff < 0.4:
            pass #TODO SUFFOCATING!  Bad things happen
        _eff = station.satisfy_reaction(self.hydration,dt)
        if _eff < 0.5:            
            pass #TODO dehydrated!  Slightly less bad things happen                        
        _eff = station.satisfy_reaction(self.excretion,dt)

        #ingestion
        #try eating fancy food first, when it's implemented
        gimme_eat = {'Name':'Ingestion', 'Inputs':{'Meals':0.62}, 'Outputs':{} }
        _eff = station.satisfy_reaction(gimme_eat,dt)
        if _eff < 1.0:
            #try making more food
            job_time -= dt*(1 - _eff)/8 / self.skill['CookJob']
            if station.get_item('CookJob') < 1.0: station.add_item('CookJob',1.0)
            job.run('CookJob', self, station, dt*(1 - _eff)/8 / self.skill['CookJob'] ) #1 cook feeds 16 people, kinda arbitrary, isn't it?
            gimme_eat = {'Name':'Ingestion', 'Inputs':{'Meals':0.62*(1 - _eff)}, 'Outputs':{} }
            _eff2 = station.satisfy_reaction(gimme_eat,dt)
            _eff = _eff + _eff2*(1-_eff)
        if _eff < 0.5:            
            print 'Malnourished!',_eff #TODO malnourished!
        


        momentary_happiness = 1.0
        for c in self.comfort_needs:
            momentary_happiness *= max(0.5,station.satisfy_reaction(c,dt))
        
        cur_job = job.get_job_from_priority_skillset_prefs(station,self.skill,self.pref)
        job.run(cur_job, self, station, job_time ) 
                    
        #print cur_job
