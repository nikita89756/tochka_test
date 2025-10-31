import sys
from app.algo import Solver


def main():
    lines = [line.rstrip('\n') for line in sys.stdin]
    
    solver = Solver(lines)
    result = solver.solve()
    
    print(result)


if __name__ == "__main__":
    main()
