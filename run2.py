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

    def _find_gate(self,pos:str) -> tuple[str | None, float,dict[str,float]]:
        dist = self._bfs(pos)
        target = None
        min_dist = float('inf')
        for gate in self.gates:
            if dist[gate] < min_dist:
                min_dist = dist[gate]
                target = gate
        return target

    def _get_node(self, pos: str) -> str | None:
        gate = self._find_gate(pos)
        if gate is None:
            return None

        for nb in self.graph[pos]:
            if nb.isupper():
                return "__LOSE__"

        dist = self._bfs(gate)

        curr = dist.get(pos, float("inf"))
        mas = [nb for nb in self.graph[pos] if dist.get(nb, float("inf")) == curr - 1]
        if not mas:
            return None
        return min(mas)

    def _edges(self) -> list[(str, str)]:
        edges = []
        for g in self.gates:
            for nb in self.graph[g]:
                if not nb.isupper():
                    edges.append((g, nb))
        return sorted(edges)
    
    def _key(self, pos: str) -> tuple[str, frozenset]:
            edges = []
            for gate in self.gates:
                for nb in self.graph[gate]:
                    if not nb.isupper():
                        edges.append((gate, nb))
            return (pos, frozenset(edges))
        
    def solve(self) -> list[list[str]]:
        results = []
        # visited = set()

        def find_all(pos: str, path: list[str]):
            # st = self._key(pos)
            # if st in visited:
            #     return
            # visited.add(st)
            
            if self._find_gate(pos) is None:
                results.append(path[:])
                return
            moves = self._edges()
            if not moves:
                return
            for gate, node in moves:
                self.graph[gate].remove(node)
                self.graph[node].remove(gate)

                next = self._get_node(pos)
                if next == "__LOSE__":
                    self.graph[gate].add(node)
                    self.graph[node].add(gate)
                else:
                    if next is None:
                        results.append(path+[f"{gate}-{node}"])
                        self.graph[gate].add(node)
                        self.graph[node].add(gate)
                    else:
                        find_all(next, path + [f"{gate}-{node}"])
                        self.graph[gate].add(node)
                        self.graph[node].add(gate)

        find_all(self.virus, [])
        results.sort()
        return results[0]


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
