from module import BasicInsideModule
import random


habitation_list = ['Basic Habitation','Standard Habitation','Deluxe Habitation','Luxury Habitation']
amenity_list = ['Amenity: Exercise','Amenity: Window']
beverage_list = ['Water','Beer','Spirits']
food_list = ['Meals']

def generate_random_amenity_prefs(obj):
    prefs=dict()
    
    hab_weights = [random.random() for r in range(0,len(habitation_list))]
    hab_sum = sum(hab_weights)
    obj.habitation_prefs=dict()
    for eh,h in enumerate(habitation_list):
        obj.habitation_prefs[h] = hab_weights[eh]/hab_sum
    
    _weights = [random.random() for r in range(0,len(amenity_list))]
    _sum = sum(_weights)
    obj.amenity_prefs = dict()
    for eh,h in enumerate(amenity_list):
        obj.amenity_prefs[h] = [w/_sum for w in _weights][eh]
    
    _weights = [random.random() for r in range(0,len(food_list))]
    _sum = sum(_weights)
    obj.food_prefs = dict()
    for eh,h in enumerate(food_list):
        obj.food_prefs[h] = [w/_sum for w in _weights][eh]
    
    _weights = [random.random() for r in range(0,len(beverage_list))]
    _sum = sum(_weights)
    obj.beverage_prefs = dict()
    for eh,h in enumerate(beverage_list):
        obj.beverage_prefs[h] = [w/_sum for w in _weights][eh]    
    
    return prefs  


class StandardHabitationModule(BasicInsideModule):
    '''Provides beds for two people'''
    def __init__(self):
        BasicInsideModule.__init__(self)             
        self.reaction_base.append( {'Name':'Standard Habitation', 'Inputs':{}, 'Outputs':{'Standard Habitation':2.0} } )
        self.reaction_base.append( {'Name':'Habitation', 'Inputs':{}, 'Outputs':{'Toilet Capacity':2.0} } )
                
        
class DeluxeHabitationModule(BasicInsideModule):
    '''Provides bed for one person'''
    def __init__(self):
        BasicInsideModule.__init__(self)             
        self.reaction_base.append( {'Name':'Deluxe Habitation', 'Inputs':{}, 'Outputs':{'Deluxe Habitation':1.0} } )        
        self.reaction_base.append( {'Name':'Habitation', 'Inputs':{}, 'Outputs':{'Toilet Capacity':1.0} } )        
        
        
class ZeroGymModule(BasicInsideModule):
    def __init__(self):
        BasicInsideModule.__init__(self)             
        self.reaction_base.append( {'Name':'Amenity - Gym', 'Inputs':{}, 'Outputs':{'Amenity: Exercise':5.0} } )
        
class Cupola(BasicInsideModule):
    def __init__(self):
        BasicInsideModule.__init__(self)             
        self.reaction_base.append( {'Name':'Panoramic Viewing Window', 'Inputs':{}, 'Outputs':{'Amenity: Window':1.0} } )          
        
