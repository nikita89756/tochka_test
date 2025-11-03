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

    def solve(self) -> list[str]:
        while True:
            target, min_dist,dist = self._find_gate()
            if target is None or min_dist == float('inf'):
                break
            node = None
            if dist[target] == 1:
                node = self.virus
            for nb in sorted(self.graph[target]):
                if nb in dist and dist[nb] == dist[target] - 1:
                    node = nb
                    break
            if node is None:
                break
            self.moves.append(f"{target}-{node}")
            self.graph[target].remove(node)
            self.graph[node].remove(target)

            target, min_dist,_ = self._find_gate()
            if target is not None and min_dist != float('inf'):
                dist = self._bfs(target)
                moved = False
                for nb in sorted(self.graph[self.virus]):
                    if nb in dist and dist[nb] < dist[self.virus]:
                        self.virus = nb
                        moved = True
                        break
                if not moved:
                    break
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
