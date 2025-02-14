import socket

HOST = '127.0.0.1'
PORT = 5555

def print_board(board):
    for i in range(3):
        print('|'.join(board[i*3:(i+1)*3]))
        if i < 2:
            print('-' * 5)

def get_move():
    while True:
        try:
            move = int(input("Enter your move (1-9): "))
            if 1 <= move <= 9:
                return move
            else:
                print("Please enter a number between 1 and 9.")
        except ValueError:
            print("Please enter a valid number.")

def check_win(board):
    win_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for combo in win_combinations:
        a, b, c = combo
        if board[a] != ' ' and board[a] == board[b] == board[c]:
            return board[a]
    if ' ' not in board:
        return 'Tie'
    return None

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        board = [' '] * 9
        print("Connected to server. You are O.")
        while True:
            data = s.recv(1024).decode().strip()
            if not data:
                break
            if data.startswith("WIN"):
                winner = data.split()[1]
                print(f"Player {winner} wins!")
                break
            elif data.startswith("TIE"):
                print("The game is a tie.")
                break
            elif data.startswith("MOVE"):
                _, move = data.split()
                pos = int(move) - 1
                if board[pos] != ' ':
                    print("Invalid move from server. Game over.")
                    break
                board[pos] = 'X'
                print("Server's move:")
                print_board(board)
                result = check_win(board)
                if result:
                    if result == 'Tie':
                        print("It's a tie!")
                    else:
                        print(f"Player {result} wins!")
                    break
                print("Your turn (O):")
                move = get_move()
                pos = move - 1
                if board[pos] != ' ':
                    print("Invalid move. You lose.")
                    s.sendall(b"INVALID\n")
                    break
                board[pos] = 'O'
                print_board(board)
                s.sendall(f"MOVE {move}\n".encode())
        print("Game over.")
        s.close()

if __name__ == "__main__":
    main()