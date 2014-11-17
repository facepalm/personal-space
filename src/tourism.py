from module import BasicInsideModule

class StandardHabitationModule(BasicInsideModule):
    '''Provides living space, meals, sanitation and beds for three people'''
    def __init__(self):
        BasicInsideModule.__init__(self)             
        self.reaction_base.append( {'Name':'Standard Habitation', 'Inputs':{}, 'Outputs':{'Standard Habitation':2.0} } )
        
class DeluxeHabitationModule(BasicInsideModule):
    '''Provides living space, meals, sanitation and beds for three people'''
    def __init__(self):
        BasicInsideModule.__init__(self)             
        self.reaction_base.append( {'Name':'Deluxe Habitation', 'Inputs':{}, 'Outputs':{'Deluxe Habitation':2.0} } )        
        
class ZeroGymModule(BasicInsideModule):
    def __init__(self):
        BasicInsideModule.__init__(self)             
        self.reaction_base.append( {'Name':'Amenity - Gym', 'Inputs':{}, 'Outputs':{'Amenity: Exercise':5.0} } )
        
class Cupola(BasicInsideModule):
    def __init__(self):
        BasicInsideModule.__init__(self)             
        self.reaction_base.append( {'Name':'Panoramic Viewing Window', 'Inputs':{}, 'Outputs':{'Amenity: Window':1.0} } )          
        
