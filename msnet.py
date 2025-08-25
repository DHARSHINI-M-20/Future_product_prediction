from collections import deque

def is_valid(state, total_m, total_c):
    m_left, c_left, boat = state
    m_right = total_m - m_left
    c_right = total_c - c_left

    if (m_left < 0 or c_left < 0 or m_right < 0 or c_right < 0 or
        m_left > total_m or c_left > total_c or
        m_right > total_m or c_right > total_c):
        return False

    if (m_left > 0 and m_left < c_left) or (m_right > 0 and m_right < c_right):
        return False
    return True

def get_next_states(state, boat_capacity, total_m, total_c):
    m, c, boat = state
    moves = []

    for m_move in range(0, boat_capacity + 1):
        for c_move in range(0, boat_capacity + 1):
            if m_move + c_move >= 1 and m_move + c_move <= boat_capacity:
                moves.append((m_move, c_move))

    next_states = []
    for m_move, c_move in moves:
        if boat == 1:
            new_state = (m - m_move, c - c_move, 0)
        else:
            new_state = (m + m_move, c + c_move, 1)

        if is_valid(new_state, total_m, total_c):
            next_states.append((new_state, (m_move, c_move)))
    return next_states

def bfs_missionaries_cannibals(total_m, total_c, boat_capacity):
    start = (total_m, total_c, 1)
    goal = (0, 0, 0)

    queue = deque([(start, [], 0)])
    visited = set([start])

    while queue:
        state, path, steps = queue.popleft()

        if state == goal:
            return path, steps

        for next_state, move in get_next_states(state, boat_capacity, total_m, total_c):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path + [(state, move, next_state)], steps + 1))
    return None, None

if __name__ == "__main__":
    total_m = int(input("Enter total number of missionaries: "))
    total_c = int(input("Enter total number of cannibals: "))
    boat_capacity = int(input("Enter boat capacity: "))

    path, steps = bfs_missionaries_cannibals(total_m, total_c, boat_capacity)

    if steps is not None:
        print(f"\nMinimum total steps to cross the river: {steps}")
        print("\nSteps:")
        for i, (from_state, move, to_state) in enumerate(path, start=1):
            print(f"Step {i}: {from_state} -> Move {move} -> {to_state}")
    else:
        print("No solution found.")
