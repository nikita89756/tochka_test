import sys
from heapq import heappush, heappop
ENERGY = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}
ROOMS_TO_IDS = {'A': 2, 'B': 4, 'C': 6, 'D': 8}
IDS_TO_ROOMS = {2:'A', 4:'B', 6:'C', 8:'D'}
ROOMS_IDS = [2, 4, 6, 8]

class Solver:
    def __init__(self, lines: list[str]):
        self.depth = len(lines) - 3
        state = {}
        for depth in range(self.depth):
            line = lines[2 + depth]
            for id, obj in enumerate([line[3], line[5], line[7], line[9]]):
                state[(2 + id * 2, depth + 1)] = obj
        self.state = state

    def _tuple(self, state: dict[tuple, str]) -> tuple:
        items = [state.get(('way', x), '.') for x in range(11)]
        for id in ROOMS_IDS:
            items.extend([state.get((id, d), '.') for d in range(1, self.depth + 1)])
        return tuple(items)
    
    def _finished(self, state: dict[tuple, str]) -> bool:
        for pos, obj in state.items():
            if pos[0] == 'way':
                return False
            if obj != IDS_TO_ROOMS[pos[0]]:
                return False
        return True

    def _heuristic(self, state: dict[tuple, str]) -> int:
        h = 0
        for pos in range(11):
            obj = state.get(('way', pos))
            if obj and obj != '.':
                target_room = ROOMS_TO_IDS[obj]
                dist = abs(pos - target_room) + 1
                h += dist * ENERGY[obj]
        rooms = {}
        for i in ROOMS_IDS:
            t = IDS_TO_ROOMS[i]
            rooms[i] = {
                'correct': 0,
                'notcorrect': []
            }
            
            correct = True
            for depth in range(self.depth, 0, -1):
                obj = state.get((i, depth))
                if not obj or obj == '.':
                    correct = False
                    continue
                if obj == t and correct:
                    rooms[i]['correct'] += 1
                else:
                    correct = False
                    if obj != t:
                        rooms[i]['notcorrect'].append((depth, obj))

        for room, info in rooms.items():
            for depth, obj in info['notcorrect']:
                id = ROOMS_TO_IDS[obj]
                exit_cost = depth
                corridor_cost = abs(room - id)
                correct = rooms[id]['correct']
                enter_cost = self.depth - correct
                dist = exit_cost + corridor_cost + enter_cost
                h += dist * ENERGY[obj]

        for id, info in rooms.items():
            room = IDS_TO_ROOMS[id]
            correct = info['correct']
            if correct < self.depth:
                another = self.depth - correct
                cost = ENERGY[room]
                h += another * cost
        return h

    def _free_depth(self, state: dict[tuple, str], obj: str, room: int) -> int | None:
        if ROOMS_TO_IDS[obj] != room:
            return None
        
        resdepth = None
        for depth in range(self.depth, 0, -1):
            cell = state.get((room, depth), '.')
            if cell == '.':
                resdepth = depth
            elif cell != obj:
                return None
        return resdepth

    def _needs_to_leave(self, state: dict[tuple, str], room: int, depth: int, obj: str) -> bool:
        if obj !=IDS_TO_ROOMS[room]:
            return True
        return any(state.get((room, d)) != obj for d in range(depth + 1, self.depth + 1))

    def _moves_to_room(self, state: dict[tuple, str]) -> list[tuple[dict[tuple, str], int]]:
        moves = []
        for pos in range(11):
            obj = state.get(('way', pos))
            if not obj or obj == '.':
                continue
            
            room = ROOMS_TO_IDS[obj]
            free_spot = self._free_depth(state, obj, room)
            if not free_spot:
                continue
            
            path = range(pos + 1, room + 1) if pos < room else range(room, pos)
            if any(state.get(('way', x)) for x in path):
                continue
            
            new_state = state.copy()
            del new_state[('way', pos)]
            new_state[(room, free_spot)] = obj
            
            dist = abs(pos - room) + free_spot
            moves.append((new_state, dist * ENERGY[obj]))
        
        return moves

    def _moves_to_way(self, state: dict[tuple, str]) -> list[tuple[dict[tuple, str], int]]:
        moves = []
        for room in ROOMS_IDS:
            for depth in range(1, self.depth + 1):
                obj = state.get((room, depth))
                if not obj or obj == '.':
                    continue
                
                if not self._needs_to_leave(state, room, depth, obj):
                    continue
                if any(state.get((room, d)) is not None for d in range(1, depth)):
                    continue
                
                for hallpos in range(11):
                    if hallpos in ROOMS_IDS or state.get(('way', hallpos)):
                        continue
                    
                    path = range(hallpos, room) if hallpos < room else range(room + 1, hallpos + 1)
                    if not all(state.get(('way', x)) is None for x in path):
                        continue
                    
                    new_state = state.copy()
                    del new_state[(room, depth)]
                    new_state[('way', hallpos)] = obj
                    
                    dist = depth + abs(room - hallpos)
                    moves.append((new_state, dist * ENERGY[obj]))
        
        return moves

    def _all_moves(self, state: dict[tuple, str]) -> list[tuple[dict[tuple, str], int]]:
        to_room = self._moves_to_room(state)
        if to_room:
            return to_room
        return self._moves_to_way(state)

    def solve(self) -> int:
        start = self._tuple(self.state)
        h = self._heuristic(self.state)
        queue = [(h, 0, start, self.state)]
        visited = set()
        costs = {start: 0}
        
        while queue:
            _, cost, i, state = heappop(queue)
            if i in visited:
                continue
            
            visited.add(i)
            if self._finished(state):
                return cost
            
            for next, energy in self._all_moves(state):
                j = self._tuple(next)
                sumcost = cost + energy
                
                if j not in costs or sumcost < costs[j]:
                    costs[j] = sumcost
                    h = self._heuristic(next)
                    full = sumcost + h
                    heappush(queue, (full, sumcost, j, next))
        
        return 0

def main():
    lines = [line.rstrip('\n') for line in sys.stdin]
    
    solver = Solver(lines)
    result = solver.solve()
    print(result)


if __name__ == "__main__":
    main()
