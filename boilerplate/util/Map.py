import heapq
import math
import random
class Map(object):
    def __init__(self,height=31,width=28,pellets_left=240):
        self.height = height
        self.width = width
        self.pellets_left = pellets_left
        self.icon = MapIconDescriptor()
        self.super_pellets_left = 0
        self.game_positions = set()
        self.pellet_positions = set()
        self.super_pellets_positions = set()
        self.map_neighbours = dict()
        self.content = []
        self.__base_content = []
        
    def load_json_map(self):
        json_map = self.content
        self.content = [['' for i in range(self.width)] for y in range(self.height)]
        self.__base_content = [['' for i in range(self.width)] for y in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                char = json_map[y][x]
                self.content[y][x] = char
                self.__base_content[y][x] = char
        self.__find_positions_of_interest()
        self.__find_pellet_positions()
        self.__make_available_neighbours_representation()

    def reset_map(self):
        self.content = [list(row) for row in self.__base_content]
        self.__find_positions_of_interest()
        self.__find_pellet_positions()
        self.__make_available_neighbours_representation()

        
    def __find_positions_of_interest(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_blocked(self.content[y][x]):
                    self.game_positions.add(Position(x,y))

    def __find_pellet_positions(self):
        for pos in self.game_positions:
            if(self.content[pos.y][pos.x] == self.icon.pellet):
                self.pellet_positions.add(pos)
            elif(self.content[pos.y][pos.x] == self.icon.super_pellet):
                self.super_pellets_positions.add(pos)
        self.pellets_left = len(self.pellet_positions)
        self.super_pellets_left = len(self.super_pellets_positions)

    def _get_available_neighbours(self, pos):
        available_neighbours = []
        x = pos.x
        y = pos.y

        up = y - 1
        if(up < 0): up = self.height - 1

        right = x + 1
        if right == self.width: right = 0

        down = y + 1
        if down == self.height: down = 0

        left = x - 1
        if(left < 0): left = self.width - 1

        if(self.content[up][x] != self.icon.closed): available_neighbours.append(Position(x,up))
        if(self.content[y][right] != self.icon.closed): available_neighbours.append(Position(right,y))
        if(self.content[down][x] != self.icon.closed): available_neighbours.append(Position(x,down))
        if(self.content[y][left] != self.icon.closed): available_neighbours.append(Position(left,y))
        random.shuffle(available_neighbours)
        return set(available_neighbours)

    def __make_available_neighbours_representation(self):
        for pos in self.game_positions:
            nb = self._get_available_neighbours(pos)
            self.map_neighbours[pos] = nb

    def get_neighbours_of(self,pos):
        return self.map_neighbours[pos]

    def get_move_between(self,pos1,pos2):
        #handle normal cases
        y_diff = int(pos2.y - pos1.y)
        x_diff = int(pos2.x - pos1.x)
        if y_diff == 0:
            if x_diff == 0: return -3 #same pos has no move -1 is correct (you are where you wanna go)
            elif x_diff == -1: return 3
            elif x_diff == 1: return 1
        elif y_diff == -1: return 0
        elif y_diff == 1: return 2

        #handle portal fuckery
        #hori
        if pos1.x == 0: return 3 #if this is the position and you wanted to move right then it's caught above
        elif pos1.x == self.width - 1: return 1 #same with the same same here
        #verti
        if pos1.y == 0: return 0 #same for the samesame
        elif pos1.y == self.height - 1: return 2 #also the same for with of same


    def get_manhattan_dist(self,pos1,pos2):
        return abs(pos2.y - pos1.y) + abs(pos2.x - pos1.x)

    def get_euclidean_dist(self,pos1,pos2):
        return math.sqrt(math.pow(pos2.y - pos1.y,2) + math.pow(pos2.x - pos1.x,2))

    def get_breadth_first_path(self, start, pos_goal=None,char_goal='_'):
        if pos_goal is None:
            if char_goal == '_': return []
            else: return self.__breadth_first_search(start,char_goal,self.__check_for_char)
        else: return self.__breadth_first_search(start,pos_goal,self.__check_for_pos)

    def __breadth_first_search(self,start,goal,goal_check_func):
        open = []
        open.append(start)
        came_from = {}
        came_from[start] = None
    
        while open:
            current = open.pop(0)
            if goal_check_func(current,goal):
                came_from[Position(-1,-1)] = current
                return self.__get_path(came_from)
        
            for next in self.get_neighbours_of(current):
                if next not in came_from:
                    open.append(next)
                    came_from[next] = current
        return [start]

    def __get_path(self,came_from):
        path = []
        parent = came_from[Position(-1,-1)]
        while parent is not None:
            path.insert(0,parent)
            parent = came_from[parent]
        return path[1:]

    def update_content(self,msg,player_new_poses):
        self.pellets_left = msg.map.pellets_left
        for pos in player_new_poses:
            char = self.content[pos.y][pos.x]
            if char == self.icon.super_pellet:
                self.super_pellets_left -= 1
                self.super_pellets_positions.remove(pos)
            elif char == self.icon.pellet:
                self.pellet_positions.remove(pos)
            self.content[pos.y][pos.x] = self.icon.open

    def __check_for_char(self,pos,char):
        return self.content[pos.y][pos.x] == char

    def __check_for_pos(self,candidate_pos,goal_pos):
        return candidate_pos == goal_pos

    def get_astar_path(self, start_pos, goal_pos):
        frontier = PriorityQueue()
        frontier.put(start_pos, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start_pos] = None
        cost_so_far[start_pos] = 0
    
        while not frontier.empty():
            current = frontier.get()
        
            if current == goal_pos:
                came_from[Position(-1,-1)] = current
                break
        
            for next in self.get_neighbours_of(current):
                new_cost = cost_so_far[current] + self.move_cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal_pos, next)
                    frontier.put(next, priority)
                    came_from[next] = current
    
        return self.__get_path(came_from)

    def heuristic(self,start,goal):
        return self.get_euclidean_dist(start,goal)

    def move_cost(self,pos1,pos2):
        return 0.0

    def is_blocked(self, map_char):
        return map_char != self.icon.open and map_char != self.icon.pellet and map_char != self.icon.super_pellet and map_char != self.icon.door

    def is_open(self, map_char):
        return map_char == self.icon.open or map_char == self.icon.pellet or map_char == self.icon.super_pellet or map_char == self.icon.door

    def print_map_content(self):
        for row in self.content:
            s = ""
            for c in row:
                s += c
            print(s)  
            
    def print_specific_positions_on_map(self, specific_poses, spesific_chars=['X']):
        specified_on_content = list(self.content)
        for index, pos in enumerate(specific_poses):
            specified_on_content[pos.y][pos.x] = str(spesific_chars[index % len(spesific_chars)])
        for i in range(self.height):
            row = specified_on_content[i]
            s = ""
            for j in range(self.width):
                s += row[j]
            print(s)

class MapIconDescriptor(object):
    def __init__(self, open_char='_', close_char='|', pellet_char=".", super_pellet_char="o",door_char='-'):
        self.open = open_char
        self.closed = close_char
        self.pellet = pellet_char
        self.super_pellet = super_pellet_char
        self.door = door_char
    
class Position(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def set(self,x,y):
        self.x = x
        self.y = y
        
    def __repr__(self):
        return self._string_rep()
    def __str__(self):
        return self._string_rep()

    def _string_rep(self):
        return str('x:' + str(self.x) + ', y:' + str(self.y))

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


class PriorityQueue:
    def __init__(self):
        from itertools import count
        self.elements = []
        self.__counter = count()
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, next(self.__counter), item))
    
    def get(self):
        return heapq.heappop(self.elements)[2]
