from collections import defaultdict, deque
import sys

class Solver:
    def __init__(self,edges: list[(str,str)]):
        self.graph = defaultdict(set)
        self.nodes = set()
        self.virus = 'a'
        self.moves = []
        gates = set()
        for u, v in edges:
            if u.isupper():
                gates.add(u)
            elif v.isupper():
                gates.add(v)
            self.graph[u].add(v)
            self.graph[v].add(u)
            self.nodes.add(u)
            self.nodes.add(v)
        self.gates = sorted(gates)

    def _bfs(self, start: str) -> dict[str, float]:
        dist = {node: float('inf') for node in self.nodes}
        if start not in self.graph:
            return dist
        dist[start] = 0
        q = deque([start])
        while q:
            curr = q.popleft()
            for nb in sorted(self.graph[curr]):
                if dist[nb] == float('inf'):
                    dist[nb] = dist[curr] + 1
                    q.append(nb)
        return dist

    def _find_gate(self) -> tuple[str | None, float,dict[str,float]]:
        dist = self._bfs(self.virus)
        target = None
        min_dist = float('inf')
        for gate in self.gates:
            if dist[gate] < min_dist:
                min_dist = dist[gate]
                target = gate
        return target, min_dist, dist
    
    def _get_node(self) -> str | None:
        target, min_dist, _= self._find_gate()
        
        if target is None:
            return None

        for nb in sorted(self.graph[self.virus]):
            dist_from_nb = self._bfs(nb)
            if dist_from_nb.get(target, float('inf')) == min_dist - 1:
                return nb
        
        return None

    def solve(self) -> list[str]:
        while True:
            moves = []
            for gate in self.gates:
                for neighbor in sorted(self.graph[gate]):
                    if not neighbor.isupper():
                        moves.append((gate, neighbor))
            
            move = None
            for gate, node in moves:
                self.graph[gate].remove(node)
                self.graph[node].remove(gate)
                new_node = self._get_node()
                bad_node = True
                if new_node is not None:
                    dist = self._bfs(new_node)
                    gates = sum(1 for g in self.gates if dist.get(g) == 1)
                    if gates > 1:
                        bad_node = False
                self.graph[gate].add(node)
                self.graph[node].add(gate)

                if bad_node:
                    move = (gate, node)
                    break
            if move is None:
                move = moves[0]
            gate, node = move
            self.moves.append(f"{gate}-{node}")
            self.graph[gate].remove(node)
            self.graph[node].remove(gate)

            next_node = self._get_node()
            if next_node:
                self.virus = next_node
            else:
                break
            
        return self.moves

def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))
    solver = Solver(edges)
    result = solver.solve()
    for edge in result:
        print(edge)

if __name__ == "__main__":
    main()
