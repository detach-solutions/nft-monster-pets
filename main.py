import bpy
import os
import random


class ObjectInfos:
    def __init__(self):
        self.infos = self.__create_infos()
    
    def __create_infos(self):
        properties = {"location": {}, "size": {}}
        infos = {"body": properties, "legs": properties}
        return infos

    def fill(self, object):
        self.infos[object]["location"]["x"] = bpy.context.object.location.x
        self.infos[object]["location"]["y"] = bpy.context.object.location.y
        self.infos[object]["location"]["z"] = bpy.context.object.location.z
        self.infos[object]["size"]["x"] = bpy.context.object.scale.x
        self.infos[object]["size"]["y"] = bpy.context.object.scale.y
        self.infos[object]["size"]["z"] = bpy.context.object.scale.z
    
    @property
    def body_size(self):
        return self.get_size("body")
    
    @property
    def legs_size(self):
        return self.get_size("legs")
        
    def get_size(self, object):
        return self.infos[object]["size"]
    

class Body():
    def __init__(self, object_infos):
        self.__cube = None
        self.__random_specs = {}
        self.__object_infos = object_infos
         
    def create(self):
        self.__create_random_specs()
        self.__create_cube()
        self.__apply_bevel()
        self.__object_infos.fill("body")
    
    def __create_random_specs(self):
        size_x_y_z = random.uniform(0.5, 2)
        scale = (size_x_y_z, size_x_y_z, size_x_y_z)
        self.__random_specs ={"scale": scale}
    
    def __create_cube(self):
        scale = self.__random_specs["scale"]
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = "body"        
        bpy.context.object.scale = scale
        self.__cube = bpy.context.object
        
    def __apply_bevel(self):
        bpy.ops.object.modifier_add(type='BEVEL')
        bpy.context.object.modifiers["Bevel"].width = 0.5
        bpy.context.object.modifiers["Bevel"].segments = 5
        
    def place_over_legs(self):
        legs_infos = self.__object_infos.legs_size
        legs_height = legs_infos["z"]
        body_height = self.__cube.scale.z
        move_up_factor = body_height + legs_height
        offset = 0.3
        self.__cube.location.z += move_up_factor - offset


class Legs(ObjectInfos):
    def __init__(self, object_infos):
        super().__init__()
        self.__cylinders = []
        self.__random_specs = {}
        self.__object_infos = object_infos
        
    def create(self):
        self.__create_random_specs()
        self.__create_cylinders()
        self.__centralize()
        self.__object_infos.fill("legs")
    
    def __create_random_specs(self):
        amount = random.randint(3, 3)
        body_width = self.__object_infos.body_size["x"]
        
        MIN_SIZE_X_Y = 0.1
        MAX_SIZE_GAP = 0.1
        MAX_SIZE_X_Y = (body_width / 2) - MAX_SIZE_GAP
        
        size_x_y = random.uniform(MIN_SIZE_X_Y, MAX_SIZE_X_Y)
        
        MIN_SIZE_Z = 0.2
        MAX_SIZE_Z = 0.8
        
        size_z = random.uniform(MIN_SIZE_Z, MAX_SIZE_Z)
        
        MIN_SPACING = size_x_y * 2
        MAX_SPACING = body_width
        x_spacing_factor = random.uniform(MIN_SPACING, MAX_SPACING)

        third_leg_position = random.choice(["front", "back"])
        
        if third_leg_position == "front":
            y_spacing_factor = -x_spacing_factor
        else:
            y_spacing_factor = x_spacing_factor
        
        x_center = size_x_y
        
        map = {
            "amount": {
                2: {
                    "number": {
                        1: (bpy.context.scene.cursor.location.x, bpy.context.scene.cursor.location.y, bpy.context.scene.cursor.location.z),
                        2: (bpy.context.scene.cursor.location.x + x_spacing_factor, bpy.context.scene.cursor.location.y, bpy.context.scene.cursor.location.z)
                    }
                },
                3: {
                    "number": {
                        1: (bpy.context.scene.cursor.location.x, bpy.context.scene.cursor.location.y, bpy.context.scene.cursor.location.z),
                        2: (bpy.context.scene.cursor.location.x + x_spacing_factor, bpy.context.scene.cursor.location.y, bpy.context.scene.cursor.location.z),
                        3: (bpy.context.scene.cursor.location.x + x_spacing_factor/2, bpy.context.scene.cursor.location.y + y_spacing_factor, bpy.context.scene.cursor.location.z)
                    }
                }
            }
        }
        
        self.random_specs = {
            "amount": amount,
            "size_x_y": size_x_y,
            "size_z": size_z,
            "map": map
        }
        
        
    def __create_cylinders(self):
        amount = self.random_specs["amount"]
        size_x_y = self.random_specs["size_x_y"]
        size_z = self.random_specs["size_z"]
        map = self.random_specs["map"]
        
        for index in range(amount):
            bpy.ops.mesh.primitive_cylinder_add()
            bpy.context.object.scale = (size_x_y, size_x_y, size_z)
            bpy.context.object.name = f"leg{index + 1}"
            number = map["amount"][amount]["number"]
            location = number[index + 1]
            leg = bpy.context.object
            leg.location = location
            self.__cylinders.append(leg)
            
        
    def __centralize(self):
        FIRST_LEG_INDEX = 0
        SECOND_LEG_INDEX = 1
        THIRD_LEG_INDEX = 2
        
        first_leg = self.__cylinders[FIRST_LEG_INDEX]
        second_leg = self.__cylinders[SECOND_LEG_INDEX]
        
        center_y = None
        
        if len(self.__cylinders) > 2:
            third_leg = self.__cylinders[THIRD_LEG_INDEX]
            center_y = (first_leg.location.y - third_leg.location.y) / 2
            
        center_x = (second_leg.location.x - first_leg.location.x) / 2
            
        for leg in self.__cylinders:
            leg.location.x -= center_x
            if center_y is not None:
                leg.location.y += center_y
            
            
        
object_infos = ObjectInfos()
body = Body(object_infos)
body.create()

legs = Legs(object_infos)
legs.create()

body.place_over_legs()