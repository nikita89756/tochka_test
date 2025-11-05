from collections import defaultdict, deque
from functools import lru_cache
import sys


class Solver:
    def __init__(self, edges: list[tuple[str, str]]):
        self.graph = defaultdict(set)
        self.nodes = set()
        self.virus = 'a'
        self.moves = []
        gates = set()

        for u, v in edges:
            if u and u[0].isupper():
                gates.add(u)
            elif v and v[0].isupper():
                gates.add(v)
            self.graph[u].add(v)
            self.graph[v].add(u)
            self.nodes.add(u)
            self.nodes.add(v)

        self.gates = sorted(gates)

    def _is_gate(x: str) -> bool:
        return bool(x) and x[0].isupper()

    def _norm_edge(a: str, b: str) -> tuple[str, str]:
        return (a, b) if a <= b else (b, a)

    def _adjacency_from_edges(self, edges_norm: tuple[tuple[str, str], ...]) -> defaultdict[str, set[str]]:
        g = defaultdict(set)
        for x, y in edges_norm:
            g[x].add(y)
            g[y].add(x)
        return g

    def _dist_from(self, start: str, adj) -> dict[str, int]:
        d = {start: 0}
        q = deque([start])
        while q:
            cur = q.popleft()
            for nb in adj.get(cur, ()):
                if nb not in d:
                    d[nb] = d[cur] + 1
                    q.append(nb)
        return d

    def _dist_from_gate(self, gate: str, adj) -> dict[str, int]:
        d = {gate: 0}
        q = deque([gate])
        while q:
            cur = q.popleft()
            for nb in adj.get(cur, ()):
                if nb not in d:
                    d[nb] = d[cur] + 1
                    q.append(nb)
        return d

    def _find_nearest_gate_lex(self, pos: str, adj):
        dist = self._dist_from(pos, adj)
        cand = [(dist[g], g) for g in adj.keys() if self._is_gate(g) and g in dist]
        if not cand:
            return None, None
        cand.sort()
        return cand[0][1], cand[0][0]

    def _determine_next_towards(self, pos: str, gate: str, adj):
        gate_d = self._dist_from_gate(gate, adj)
        if pos not in gate_d:
            return None
        cd = gate_d[pos]
        if cd == 0:
            return None
        best = [nb for nb in adj.get(pos, ()) if nb in gate_d and gate_d[nb] == cd - 1]
        if not best:
            return None
        return sorted(best)[0]

    def _simulate_virus_step(self, pos: str, adj):
        g, _ = self._find_nearest_gate_lex(pos, adj)
        if g is None:
            return pos
        nxt = self._determine_next_towards(pos, g, adj)
        return nxt if nxt is not None else pos

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

    def _find_gate(self, pos: str):
        adj = self.graph
        g, _ = self._find_nearest_gate_lex(pos, adj)
        return g

    def _get_node(self, pos: str) -> str | None:
        gate = self._find_gate(pos)
        if gate is None:
            return None

        for nb in self.graph[pos]:
            if self._is_gate(nb):
                return "__LOSE__"

        dist = self._bfs(gate)
        curr = dist.get(pos, float("inf"))
        mas = [nb for nb in self.graph[pos] if dist.get(nb, float("inf")) == curr - 1]
        if not mas:
            return None
        return min(mas)

    def _edges(self) -> list[tuple[str, str]]:
        edges = []
        for g in self.gates:
            for nb in self.graph[g]:
                if not self._is_gate(nb):
                    edges.append((g, nb))
        return sorted(edges)

    def _key(self, pos: str) -> tuple[str, frozenset]:
        edges = []
        for gate in self.gates:
            for nb in self.graph[gate]:
                if not self._is_gate(nb):
                    edges.append((gate, nb))
        return (pos, frozenset(edges))

    def _normalized_edges_tuple(self) -> tuple[tuple[str, str], ...]:
        es = set()
        for g in self.gates:
            for nb in self.graph[g]:
                if not self._is_gate(nb):
                    es.add(self._norm_edge(g, nb))
        return tuple(sorted(es))

    @lru_cache(maxsize=None)
    def _explore_strategy(self, virus_pos: str, available_edges: tuple[tuple[str, str], ...]):
        adj = self._adjacency_from_edges(available_edges)

        for u in self.nodes:
            if self._is_gate(u):
                continue
            for v in self.graph[u]:
                if not self._is_gate(v):
                    adj[u].add(v)
                    adj[v].add(u)

        nearest_gate, _ = self._find_nearest_gate_lex(virus_pos, adj)
        if nearest_gate is None:
            return ()

        blockable = []
        for g in adj.keys():
            if not self._is_gate(g):
                continue
            for nb in adj[g]:
                if not self._is_gate(nb):
                    blockable.append(f"{g}-{nb}")
        blockable = sorted(set(blockable))

        current = set(available_edges)

        for op in blockable:
            g, _, nb = op.partition('-')
            e = self._norm_edge(g, nb)
            if e not in current:
                continue

            updated = tuple(sorted([x for x in available_edges if x != e]))
            mod_adj = self._adjacency_from_edges(updated)
            for u in self.nodes:
                if self._is_gate(u):
                    continue
                for v in self.graph[u]:
                    if not self._is_gate(v):
                        mod_adj[u].add(v)
                        mod_adj[v].add(u)

            rg, _ = self._find_nearest_gate_lex(virus_pos, mod_adj)
            if rg is None:
                return (op,)

            next_pos = self._simulate_virus_step(virus_pos, mod_adj)
            if next_pos is None:
                next_pos = virus_pos
            if self._is_gate(next_pos):
                continue

            cont = self._explore_strategy(next_pos, updated)
            if cont is not None:
                return (op,) + cont

        return None

    def solve(self) -> list[list[str]]:
        results = []
        visited = set()

        initial_tuple = self._normalized_edges_tuple()

        def find_all(pos: str, path: list[str]):
            st = self._key(pos)
            if st in visited:
                return
            visited.add(st)

            if self._find_gate(pos) is None:
                results.append(path[:])
                return

            moves = self._edges()
            if not moves:
                plan = self._explore_strategy(pos, initial_tuple)
                if plan:
                    results.append(path + list(plan))
                return

            for gate, node in moves:
                self.graph[gate].remove(node)
                self.graph[node].remove(gate)

                nxt = self._get_node(pos)
                if nxt == "__LOSE__":
                    self.graph[gate].add(node)
                    self.graph[node].add(gate)
                else:
                    if nxt is None:
                        results.append(path + [f"{gate}-{node}"])
                        self.graph[gate].add(node)
                        self.graph[node].add(gate)
                    else:
                        find_all(nxt, path + [f"{gate}-{node}"])
                        self.graph[gate].add(node)
                        self.graph[node].add(gate)

        find_all(self.virus, [])
        results.sort()
        return results[0] if results else []


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
