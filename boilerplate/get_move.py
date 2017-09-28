from util.Map import Position
import math
import random

def get_closest_pellet(ai, map):
    x0, y0 = ai.you.pos.x, ai.you.pos.y

    board = map.content

    width, height = len(board[0]), len(board)

    dist = lambda x, y : abs(x0-x) + abs(y0-y)

    return min(((x,y, dist(x,y)) for x in range(width) for y in range(height) if board[y][x] == map.icon.pellet), key = lambda p : p[2])

def get_closest_super_pellet(ai, map):
    x0, y0 = ai.you.pos.x, ai.you.pos.y

    board = map.content

    width, height = len(board[0]), len(board)

    dist = lambda x, y : abs(x0-x) + abs(y0-y)

    return min(((x,y, dist(x,y)) for x in range(width) for y in range(height) if board[y][x] == map.icon.super_pellet), key = lambda p : p[2])

# Manhattan
def distance_to_enemy(ai, map):
    return abs(ai.you.pos.x - ai.enemy.pos.x) + abs(ai.you.pos.y - ai.enemy.pos.y)

def _get_move(ai,map):
    def check_if_blocked(cur_pos, next_pos):
        # check for cycles
        # cycle => not blocked
        V = set()
        V.add(cur_pos)
        Q = []
        Q.append((next_pos, cur_pos))
        while Q:
            cur, prev = Q.pop()
            if cur in V: return False # cycle found!
            V.add(cur)

            for ngbhr in map.get_neighbours_of(cur):
                # not a cycle if prev position
                if ngbhr == prev: continue
                Q.append((ngbhr, cur))

        # path explored, no cycle found
        return True

    # No one is dangerous
    if ai.states.no_danger() or 7 < distance_to_enemy(ai,map):
        print("No danger")
        has_pellets = map.pellets_left > 0
        has_spellets = map.super_pellets_left > 0

        if not has_pellets and not has_spellets:
            return random.randint(0, 3)

        if has_pellets:
            pellet_x, pellet_y, pellet_dist = get_closest_pellet(ai, map)

        if has_spellets:
            spellet_x, spellet_y, spellet_dist = get_closest_super_pellet(ai, map)


        # Go for super pellet
        if has_spellets and (not has_pellets or spellet_dist < 3 * pellet_dist):
            x, y = spellet_x, spellet_y

        # Go for normal pellet
        elif has_pellets and (not has_spellets or spellet_dist >= 3 * pellet_dist):
            x, y = pellet_x, pellet_y

        path = map.get_astar_path(ai.you.pos, Position(x, y))

        next_pos = path[0]

        return map.get_move_between(ai.you.pos, next_pos)

    elif ai.states.you_are_dangerous():
        print("I'm dagerous")

        path = map.get_astar_path(ai.you.pos, ai.enemy.pos)

        next_pos = path[0]

        return map.get_move_between(ai.you.pos, next_pos)

    else:
        print("He's dangerous")

        moves = map.get_neighbours_of(ai.you.pos)

        def move_value(move):
            if check_if_blocked(ai.you.pos, move):
                return 0
            dx, dy = move.x - ai.you.pos.x, move.y - ai.you.pos.y

            to_x, to_y = ai.you.pos.x + dx, ai.you.pos.y + dy

            cx, cy = len(map.content[0]) / 2, len(map.content) / 2

            # Manhattan dist to enemy, negative euclidean dist to center. Maximize this
            #return (abs(to_x-ai.enemy.pos.x)+abs(to_y-ai.enemy.pos.y), -math.sqrt((to_x-cx)**2 + (to_y-cy)**2))
            return abs(to_x-ai.enemy.pos.x)+abs(to_y-ai.enemy.pos.y)

        return map.get_move_between(ai.you.pos, max(moves, key = move_value))

