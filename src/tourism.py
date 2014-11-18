from module import BasicInsideModule

habitation_list = ['Basic Habitation','Standard Habitation','Deluxe Habitation','Luxury Habitation']
amenity_list = ['Amenity: Exercise','Amenity: Window']
beverage_list = ['Water','Beer','Spirits']
food_list = ['Meals']

def generate_random_amenity_prefs():
    prefs=dict()
    
    hab_weights = [random.random() for r in range(0,len(habitation_list))]
    hab_sum = sum(hab_weights)
    prefs['Habitation'] = [w/hab_sum for w in hab_weights]
    
    _weights = [random.random() for r in range(0,len(amenity_list))]
    _sum = sum(weights)
    prefs['Amenities'] = [w/_sum for w in _weights]
    
    _weights = [random.random() for r in range(0,len(food_list))]
    _sum = sum(weights)
    prefs['Meals'] = [w/_sum for w in _weights]          
    
    _weights = [random.random() for r in range(0,len(beverage_list))]
    _sum = sum(weights)
    prefs['Drinks'] = [w/_sum for w in _weights]          
    
    
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
        
