import sys
from collections import deque, defaultdict
from functools import lru_cache


def normalize_connection(node_a: str, node_b: str) -> tuple[str, str]:
    return tuple(sorted([node_a, node_b]))


def check_if_hub(vertex: str) -> bool:
    return vertex[0].isupper()


def create_adjacency_map(connections):
    adjacency = defaultdict(set)
    for first, second in connections:
        adjacency[first].add(second)
        adjacency[second].add(first)
    return adjacency


def calculate_distances(origin: str, adjacency):
    distances = {origin: 0}
    queue = deque([origin])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)
    return distances


def compute_paths_from_hub(hub_node: str, adjacency):
    path_lengths = {hub_node: 0}
    processing_queue = deque([hub_node])
    while processing_queue:
        node = processing_queue.popleft()
        for adjacent in adjacency[node]:
            if adjacent not in path_lengths:
                path_lengths[adjacent] = path_lengths[node] + 1
                processing_queue.append(adjacent)
    return path_lengths


def find_nearest_hub(position: str, adjacency):
    dist_map = calculate_distances(position, adjacency)
    hub_candidates = []
    for vertex in adjacency.keys():
        if check_if_hub(vertex) and vertex in dist_map:
            hub_candidates.append((dist_map[vertex], vertex))
    
    if not hub_candidates:
        return None, None
    
    hub_candidates.sort()
    return hub_candidates[0][1], hub_candidates[0][0]


def determine_next_move(position: str, destination_hub: str, adjacency):
    hub_distances = compute_paths_from_hub(destination_hub, adjacency)
    
    if position not in hub_distances:
        return None
    
    current_distance = hub_distances[position]
    if current_distance == 0:
        return None
    
    possible_moves = []
    for neighbor in adjacency[position]:
        if neighbor in hub_distances and hub_distances[neighbor] == current_distance - 1:
            possible_moves.append(neighbor)
    
    if not possible_moves:
        return None
    
    return sorted(possible_moves)[0]


def simulate_virus_step(position: str, adjacency):
    """Симулируем один шаг движения вируса."""
    target_hub, _ = find_nearest_hub(position, adjacency)
    if target_hub is None:
        return position
    
    next_node = determine_next_move(position, target_hub, adjacency)
    return next_node if next_node is not None else position


def solve(edges: list[tuple[str, str]]) -> list[str]:
    """
    Решение задачи об изоляции вируса

    Args:
        edges: список коридоров в формате (узел1, узел2)

    Returns:
        список отключаемых коридоров в формате "Шлюз-узел"
    """
    normalized_edges = tuple(sorted(normalize_connection(x, y) for x, y in edges))
    
    @lru_cache(maxsize=None)
    def explore_strategy(virus_pos: str, available_edges: tuple[tuple[str, str], ...]):
        network = create_adjacency_map(available_edges)
        nearest_hub, _ = find_nearest_hub(virus_pos, network)
        
        if nearest_hub is None:
            return ()
        blockable_paths = []
        for vertex in network:
            if not check_if_hub(vertex):
                continue
            for connected_node in network[vertex]:
                if not check_if_hub(connected_node):
                    blockable_paths.append(f"{vertex}-{connected_node}")
        
        blockable_paths = sorted(set(blockable_paths))
        current_edges = set(available_edges)
        for block_option in blockable_paths:
            hub_part, _, regular_part = block_option.partition('-')
            connection_to_remove = normalize_connection(hub_part, regular_part)
            
            if connection_to_remove not in current_edges:
                continue
            updated_edges = [e for e in available_edges if e != connection_to_remove]
            updated_edges_tuple = tuple(sorted(updated_edges))
            modified_network = create_adjacency_map(updated_edges_tuple)
            reachable_hub, _ = find_nearest_hub(virus_pos, modified_network)
            if reachable_hub is None:
                return (block_option,)
            virus_next_pos = simulate_virus_step(virus_pos, modified_network)
            if virus_next_pos is None:
                virus_next_pos = virus_pos
            
            if check_if_hub(virus_next_pos):
                continue
            continuation = explore_strategy(virus_next_pos, updated_edges_tuple)
            if continuation is not None:
                return (block_option,) + continuation
        
        return None
    
    result = explore_strategy('a', normalized_edges)
    return list(result or [])


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)


if __name__ == "__main__":
    main()