import bpy
import bmesh
import random

class Blender:
    def apply_bevel(self, width, segments):
        bpy.ops.object.modifier_add(type='BEVEL')
        bpy.context.object.modifiers["Bevel"].width = width
        bpy.context.object.modifiers["Bevel"].segments = segments
    
    def delete_face(self, face_index):
        bpy.ops.object.mode_set(mode='EDIT')
        mesh=bmesh.from_edit_mesh(bpy.context.object.data)
        mesh.faces.ensure_lookup_table() 
        
        for face in mesh.faces:
            face.select = False
            
        mesh.faces[face_index].select = True
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        
    def smooth_all(self): 
        for obj in bpy.context.scene.objects:
            obj.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')
            mesh = bmesh.from_edit_mesh(obj.data)
            mesh.faces.ensure_lookup_table() 
        
            for face in mesh.faces:
                face.smooth = True
        
            bpy.ops.object.mode_set(mode='OBJECT')

            
            
class ObjectInfos:
    def __init__(self):
        self.__infos = self.__create_infos()
        self.__body = None
        self.__legs = []
        self.__terrain = None
    
    def __create_infos(self):
        properties = {"location": {}, "size": {}}
        infos = {"body": properties, "legs": properties, "terrain": properties}
        return infos

    def fill(self, object):
        self.__infos[object]["location"]["x"] = bpy.context.object.location.x
        self.__infos[object]["location"]["y"] = bpy.context.object.location.y
        self.__infos[object]["location"]["z"] = bpy.context.object.location.z
        self.__infos[object]["size"]["x"] = bpy.context.object.scale.x
        self.__infos[object]["size"]["y"] = bpy.context.object.scale.y
        self.__infos[object]["size"]["z"] = bpy.context.object.scale.z
    
    def get_size(self, object):
        return bpy.data.objects[object].scale
    
    def get_location(self, object):
        return bpy.data.objects[object].location
             
    def set_body(self):
        self.__body = bpy.context.object
    
    def set_terrain(self):
        self.__terrain = bpy.context.object
        
    def set_leg(self):
        self.__legs.append(bpy.context.object)
    
    @property
    def legs(self):
        return self.__legs
    
    @property
    def body(self):
        return self.__body
    
    def __str__(self):
        return str(self.__infos)
    
class Body():
    def __init__(self, object_infos, blender):
        self.__cube = None
        self.__random_specs = {}
        self.__object_infos = object_infos
        self.__blender = blender
         
    def create(self):
        self.__create_random_specs()
        self.__create_cube()
        self.__blender.apply_bevel(0.5, 5)
        self.__object_infos.fill("body")
        self.__object_infos.set_body()
    
    def __create_random_specs(self):
        size_x_y_z = random.uniform(0.2, 1.5)
        scale = (size_x_y_z, size_x_y_z, size_x_y_z)
        self.__random_specs ={"scale": scale}
    
    def __create_cube(self):
        scale = self.__random_specs["scale"]
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = "body"        
        bpy.context.object.scale = scale
        self.__cube = bpy.context.object
        
    def place_over_legs(self):
        legs_location = self.__object_infos.get_location("leg1")
        legs_z_location = legs_location.z
        legs_size = self.__object_infos.get_size("leg1")
        legs_z_size = legs_size.z
        move_factor = legs_z_location + legs_z_size + self.__cube.scale.z
        offset = 0.3
        move_factor = move_factor - offset
        
        print(self.__cube)
        self.__cube.location.z = move_factor
    
            
            
class Legs(ObjectInfos):
    def __init__(self, object_infos, blender):
        super().__init__()
        self.__cylinders = []
        self.__random_specs = {}
        self.__object_infos = object_infos
        self.__blender = blender
        
    def create(self):
        self.__create_random_specs()
        self.__create_cylinders()
        self.__centralize()
        self.__object_infos.fill("legs")
    
    def __create_random_specs(self):
        def create_size_specs(body_width):
            MIN_SIZE_X_Y = 0.1
            MAX_SIZE_GAP = 0.2
            MAX_SIZE_X_Y = (body_width / 2) - MAX_SIZE_GAP
            
            size_x_y = random.uniform(MIN_SIZE_X_Y, MAX_SIZE_X_Y)
            
            MIN_SIZE_Z = 0.2
            MAX_SIZE_Z = 0.8
            
            size_z = random.uniform(MIN_SIZE_Z, MAX_SIZE_Z)

            return size_x_y, size_z
        
        def create_spacing_specs(body_width, size_x_y):
            MIN_SPACING = size_x_y * 2
            MAX_SPACING = body_width
            
            x_spacing_factor = random.uniform(MIN_SPACING, MAX_SPACING)
            y_spacing_factor = random.uniform(MIN_SPACING, MAX_SPACING)
            
            third_leg_location = random.choice(["FRONT", "BACK"])
            if third_leg_location == "BACK":
                y_spacing_factor = -y_spacing_factor
                
            return x_spacing_factor, y_spacing_factor

        def create_position_map(MIN_LEGS_AMOUNT, MAX_LEGS_AMOUNT): 
            x_spacing_factor, y_spacing_factor = create_spacing_specs(body_width, size_x_y)
            
            cursor_location = bpy.context.scene.cursor.location
            cursor_x = cursor_location.x
            cursor_y = cursor_location.y
            cursor_z = cursor_location.z
            
            leg_x_spacing = cursor_x + x_spacing_factor
            leg_x_center = cursor_x + x_spacing_factor / 2
            leg_y_spacing = cursor_y + y_spacing_factor

            leg_coords = {
                "first": (cursor_x, cursor_y, cursor_z),
                "second": (leg_x_spacing, cursor_y, cursor_z),
                "third": (leg_x_center, leg_y_spacing, cursor_z)
            }
       
            position_map = {"amount": {}}
            for leg_amount in range(MIN_LEGS_AMOUNT, MAX_LEGS_AMOUNT + 1):
                position_map["amount"][leg_amount] = {}
                for index, key in enumerate(leg_coords):
                    position_map["amount"][leg_amount][index + 1] = leg_coords[key]
               
            return position_map

        body_width = self.__object_infos.get_size("body").x
        size_x_y, size_z = create_size_specs(body_width)
        MIN_LEGS_AMOUNT = 2
        MAX_LEGS_AMOUNT = 3
        amount = random.randint(MIN_LEGS_AMOUNT, MAX_LEGS_AMOUNT)
        position_map = create_position_map(MIN_LEGS_AMOUNT, MAX_LEGS_AMOUNT)

        self.__random_specs = {
            "amount": amount,
            "size_x_y": size_x_y,
            "size_z": size_z,
            "position_map": position_map
        }
        
        
    def __create_cylinders(self):
        amount = self.__random_specs["amount"]
        size_x_y = self.__random_specs["size_x_y"]
        size_z = self.__random_specs["size_z"]
        position_map = self.__random_specs["position_map"]
        
        for index in range(amount):
            bpy.ops.mesh.primitive_cylinder_add()
            bpy.context.object.scale = (size_x_y, size_x_y, size_z)
            bpy.context.object.name = f"leg{index + 1}"
            legs_location = position_map["amount"][amount]
            location = legs_location[index + 1]
            leg = bpy.context.object
            leg.location = location
            
            TOP_FACE_INDEX = 30
            self.__blender.delete_face(TOP_FACE_INDEX)
            self.__blender.apply_bevel(0.1, 3)
            self.__cylinders.append(leg)
            self.__object_infos.set_leg()

            
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
            
            
    def place_over_terrain(self):
        terrain_size = self.__object_infos.get_size("terrain")
        terrain_location = self.__object_infos.get_location("terrain")
        terrain_z_location = terrain_location.z
        
        for leg in self.__object_infos.legs:
            leg.location.z = terrain_z_location + leg.scale.z + terrain_size.z
    

class Terrain():
    def __init__(self, object_infos, blender):
        self.__object_infos = object_infos
        self.__blender = blender
        self.__terrain = None
        
    def create(self):
        self.__create_cube()
        self.__blender.apply_bevel(0.3, 6)
        self.__create_loopcut()
        self.__object_infos.fill("terrain")
        
    def __create_cube(self):
        bpy.ops.mesh.primitive_cube_add()
        self.__terrain = bpy.context.object
        self.__terrain.name = "terrain"        
        self.__terrain.dimensions = (4,4,1.25)
        
    def __create_loopcut(self):
        bpy.context.view_layer.objects.active = self.__terrain
        self.__terrain.select_set(True)
        old_type = bpy.context.area.type
        bpy.context.area.type = 'VIEW_3D'
        bpy.ops.object.editmode_toggle()
        
        def view3d_find( return_area = False ):
            for area in bpy.context.window.screen.areas:
                if area.type == 'VIEW_3D':
                    v3d = area.spaces[0]
                    rv3d = v3d.region_3d
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            if return_area: return region, rv3d, v3d, area
                            return region, rv3d, v3d
            return None, None

        region, rv3d, v3d, area = view3d_find(True)

        override = {
            'scene'  : bpy.context.scene,
            'region' : region,
            'area'   : area,
            'space'  : v3d
        }
        
        bpy.ops.mesh.loopcut_slide(
            override,
            MESH_OT_loopcut = {
                "object_index" : 0,
                "number_cuts"           : 1,
                "smoothness"            : 0,     
                "falloff"               : 'INVERSE_SQUARE',  # Was 'INVERSE_SQUARE' that does not exist
                "edge_index"            : 1,
                "mesh_select_mode_init" : (True, False, False)
            },
            TRANSFORM_OT_edge_slide = {
                "value"           : 0,
                "mirror"          : False, 
                "snap"            : False,
                "snap_target"     : 'CLOSEST',
                "snap_point"      : (0.648362, 0.648362, 0.648362),
                "snap_align"      : False,
                "snap_normal"     : (0.648362, 0.648362, 0.648362),
                "correct_uv"      : False,
                "release_confirm" : False,
                "use_accurate"    : False
            }
        )
        bpy.ops.object.editmode_toggle()
        bpy.context.area.type = old_type 
    
    
object_infos = ObjectInfos()
blender = Blender()

body = Body(object_infos, blender)
body.create()

legs = Legs(object_infos, blender)
legs.create()


terrain = Terrain(object_infos, blender)
terrain.create()

legs.place_over_terrain()
body.place_over_legs()

blender.smooth_all()
