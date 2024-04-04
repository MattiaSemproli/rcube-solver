from ursina import *

class MainPage(Entity):
    def __init__(self, steps: str):
        super().__init__()
        steps = "U F2 U' F' L' U' B R' D' F R' U' R2 F2 U B2 R2 U2 F2 R2 U'"
        scramble = steps.split(' ')[::-1]
        for (i, step) in enumerate(scramble):
            if "'" in step: 
                scramble[i] = step[0]
            elif "2" not in step: 
                scramble[i] = step + "'"
        steps = steps.split(' ')
        
        def randomize():
            while len(scramble) > 0:
                move = scramble.pop(0)
                direction = 1
                if "2" in move:
                    move = move[0]
                    scramble.insert(0, move)
                elif "'" in move:
                    direction = -1
                    move = move[0]
                if move == "R":
                    rotate_side(Vec3(1,0,0), direction, speed=0)
                elif move == "L":
                    rotate_side(Vec3(-1,0,0), direction, speed=0)
                elif move == "U":
                    rotate_side(Vec3(0,1,0), direction, speed=0)
                elif move == "D":
                    rotate_side(Vec3(0,-1,0), direction, speed=0)
                elif move == "F":
                    rotate_side(Vec3(0,0,-1), direction, speed=0)
                elif move == "B":
                    rotate_side(Vec3(0,0,1), direction, speed=0)

        cube_colors = [
            color.red,  # right
            color.orange,   # left
            color.yellow,    # top
            color.white,   # bottom
            color.green,    # back
            color.blue,    # front
        ]

        # make a model with a separate color on each face
        combine_parent = Entity(enabled=False)
        for i in range(3):
            dir = Vec3(0,0,0)
            dir[i] = 1
            
            e = Entity(parent=combine_parent, model='plane', origin_y=-.5, texture='white_cube', color=cube_colors[i*2])
            e.look_at(dir, 'up')

            e_flipped = Entity(parent=combine_parent, model='plane', origin_y=-.5, texture='white_cube', color=cube_colors[(i*2)+1])
            e_flipped.look_at(-dir, 'up')

        combine_parent.combine()

        # place 3x3x3 cubes
        cubes = []
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    e = Entity(model=copy(combine_parent.model), position=Vec3(x,y,z) - (Vec3(3,3,3)/3), texture='white_cube')
                    cubes.append(e)

        # rotate a side when we click on it
        collider = Entity(model='cube', scale=3, collider='box', visible=False)

        def collider_input(key):
            if mouse.hovered_entity == collider:
                if key == 'left mouse down':
                    if len(steps) != 0:
                        move = steps.pop(0)
                        direction = 1
                        if "2" in move:
                            move = move[0]
                            steps.insert(0, move)
                        elif "'" in move:
                            direction = -1
                            move = move[0]
                        if move == "R":
                            rotate_side(Vec3(1,0,0), direction)
                        elif move == "L":
                            rotate_side(Vec3(-1,0,0), direction)
                        elif move == "U":
                            rotate_side(Vec3(0,1,0), direction)
                        elif move == "D":
                            rotate_side(Vec3(0,-1,0), direction)
                        elif move == "F":
                            rotate_side(Vec3(0,0,-1), direction)
                        elif move == "B":
                            rotate_side(Vec3(0,0,1), direction)

        collider.input = collider_input


        rotation_helper = Entity()


        def rotate_side(normal, direction=1, speed=1):
            # red side (RIGHT)
            if normal == Vec3(1,0,0):
                [setattr(e, 'world_parent', rotation_helper) for e in cubes if e.x > 0]
                rotation_helper.animate('rotation_x', 90 * direction, duration=.15*speed, curve=curve.linear, interrupt='finish')
            # orange side (LEFT)
            if normal == Vec3(-1,0,0):
                [setattr(e, 'world_parent', rotation_helper) for e in cubes if e.x < 0]
                rotation_helper.animate('rotation_x', -90 * direction, duration=.15*speed, curve=curve.linear, interrupt='finish')
            # yellow side (TOP)
            if normal == Vec3(0,1,0):
                [setattr(e, 'world_parent', rotation_helper) for e in cubes if e.y > 0]
                rotation_helper.animate('rotation_y', 90 * direction, duration=.15*speed, curve=curve.linear, interrupt='finish')
            # white side (BOTTOM)
            if normal == Vec3(0,-1,0):
                [setattr(e, 'world_parent', rotation_helper) for e in cubes if e.y < 0]
                rotation_helper.animate('rotation_y', -90 * direction, duration=.15*speed, curve=curve.linear, interrupt='finish')
            # green side (BACK)
            if normal == Vec3(0,0,1):
                [setattr(e, 'world_parent', rotation_helper) for e in cubes if e.z > 0]
                rotation_helper.animate('rotation_z', -90 * direction, duration=.15*speed, curve=curve.linear, interrupt='finish')
            # blue side (FRONT)
            if normal == Vec3(0,0,-1):
                [setattr(e, 'world_parent', rotation_helper) for e in cubes if e.z < 0]
                rotation_helper.animate('rotation_z', 90 * direction, duration=.15*speed, curve=curve.linear, interrupt='finish')


            invoke(reset_rotation_helper, delay=.2*speed)

            if speed:
                collider.ignore_input = True
                @after(.25*speed)
                def _():
                    collider.ignore_input = False
                    check_for_win()


        def reset_rotation_helper():
            [setattr(e, 'world_parent', scene) for e in cubes]
            rotation_helper.rotation = (0,0,0)


        win_text_entity = Text(y=.35, text='', color=color.green, origin=(0,0), scale=3)

        def check_for_win():
            if {e.world_rotation for e in cubes} == {Vec3(0,0,0)}:
                win_text_entity.text = 'SOLVED!'
                win_text_entity.appear()
            else:
                win_text_entity.text = ''

        randomize()

        window.color = color._16
        EditorCamera()