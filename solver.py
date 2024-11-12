from ursina import *

class MainPage(Entity):
    def __init__(self, steps: str):
        super().__init__()
        scramble = steps.split(' ')[::-1]
        for (i, step) in enumerate(scramble):
            if "'" in step: 
                scramble[i] = step[0]
            elif "2" not in step: 
                scramble[i] = step + "'"
        steps = steps.split(' ')
        
        self.solutionSequence = [elem for step in steps for elem in ([step[0], step[0]] if "2" in step else [step])]
        self.text_entities = []
        self.current_move_index = 1
        
        self.timer = 0
        self.dots_count = 0
        self.max_dots = 3
        self.isCompleted = False

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
            color.red,     # right
            color.orange,  # left
            color.yellow,  # top
            color.white,   # bottom
            color.green,   # back
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
        
        def initialize_text_entities():
            total_width = len(self.solutionSequence) * 0.1
            x_offset = -total_width / 2

            self.text_entities.append(Text(text=''))

            for s in self.solutionSequence:
                t = Text(y=.35, text=s, color=color.white, origin=(0, 0), scale=1.5, font='VeraMono.ttf', x=x_offset)
                self.text_entities.append(t)
            
            self.text_entities.append(Text(text=''))

        def cycle_scale():
            for t in self.text_entities:
                t.scale = 0
                t.color = color.white
            
            prev_index = self.current_move_index - 1
            next_index = self.current_move_index + 1

            x_prev = -0.1
            x_center = 0
            x_next = 0.1
            
            # Previous move
            self.text_entities[prev_index].scale = 1.5
            self.text_entities[prev_index].x = x_prev

            # Current move
            self.text_entities[self.current_move_index].scale = 3
            self.text_entities[self.current_move_index].x = x_center
            self.text_entities[self.current_move_index].color = color.gold

            # Next move
            self.text_entities[next_index].scale = 1.5
            self.text_entities[next_index].x = x_next

            self.current_move_index = self.current_move_index + 1 if self.current_move_index < len(self.text_entities) - 2 else self.current_move_index

        self.solving_text = Text(y=-.40, text='Solving ...', color=color.white, origin=(0,0), scale=2, font='VeraMono.ttf')
        initialize_text_entities()
        cycle_scale()

        def check_for_win():
            if {e.world_rotation for e in cubes} == {Vec3(0,0,0)}:
                win_text_entity = Text(y=.35, text='SOLVED!', color=color.green, origin=(0,0), scale=2, font='VeraMono.ttf')
                win_text_entity.appear()
                self.isCompleted = True
            if self.current_move_index < len(self.text_entities):
                cycle_scale()

        randomize()

        window.color = color._16
        EditorCamera()

    def update(self):
        # self.win_text_entity.position = Vec3(sin(time.time()), cos(time.time()), 0) * .4
        self.timer += time.dt
        if not self.isCompleted:
            if self.timer > 0.5:
                self.dots_count = (self.dots_count + 1) % (self.max_dots + 1)
                self.solving_text.text = f'Solving{"." * self.dots_count}'
                self.timer = 0
        else:
            self.solving_text.text = ''
            for t in self.text_entities:
                t.scale = 0