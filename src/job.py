import random
import math
import util

joblist = {
            'CookJob':{'Inputs':{'Food':9.92, 'CookJob': 1.0},'Outputs':{'Meals':9.92,'SanitationJob':0.1}}, #fresh food, dirty kitchen
            'SanitationJob':{'Inputs':{'General Consumables':0.55, 'SanitationJob': 1.0},'Outputs':{'Solid Waste':0.55}},
            'MaintenanceJob':{'Inputs':{'Parts':1.0, 'MaintenanceJob': 1.0},'Outputs':{'Scrap':0.50,'SanitationJob':0.1}}, #working stuff, dirty guy
            'HydroJob':{'Inputs':{'HydroJob':1.0},'Outputs':{'Hydro':1,'SanitationJob':0.03}},
            'EVAJob':{'Inputs':{'General Consumables':0.55, 'Oxygen':1.0, 'EVAJob': 1.0},'Outputs':{'EVA':1.0,'SanitationJob':0.1 }} #TODO find real numbers
            }


def get_job_from_priority_skillset_prefs(station,skills,prefs=None):
    jobs = joblist.keys()
    jobs.sort(key = lambda j: station.get_item(j)*skills[j]*(prefs[j] if prefs else 1.0), reverse=True)
    #print jobs, [skills[j] for j in jobs]
    return jobs[0]
    

def generate_random_skillset():
    skills=dict()
    skillnames= joblist.keys()
    for skill in skillnames:
        skills[skill] = .1 + .5*random.random()
    return skills
    
def run(job,actor,station,duration):
    #print job, actor.name, station.name, duration
    if job not in joblist.keys(): return 0.0
    new_dur = duration * actor.skill[job]
    _eff = station.satisfy_reaction(joblist[job],new_dur)
    
    #increase skill of actor    
    tc = util.seconds(1,'year')
    score = -1.0 * math.log(1 - actor.skill[job]) * tc
    score += duration
    actor.skill[job] = 1 - math.exp(-score/tc)
    
    return _eff
