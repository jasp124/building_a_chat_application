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
        s.bind((HOST, PORT))
        s.listen()
        print("Waiting for client to connect...")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            board = [' '] * 9
            print("You are X. You go first.")
            while True:
                print_board(board)
                move = get_move()
                pos = move - 1
                if board[pos] != ' ':
                    print("Invalid move. Try again.")
                    continue
                board[pos] = 'X'
                result = check_win(board)
                if result:
                    print_board(board)
                    if result == 'Tie':
                        conn.sendall(b"TIE\n")
                        print("It's a tie!")
                    else:
                        conn.sendall(f"WIN X\n".encode())
                        print("You win!")
                    break
                conn.sendall(f"MOVE {move}\n".encode())
                data = conn.recv(1024).decode().strip()
                if not data:
                    break
                if data.startswith("WIN"):
                    winner = data.split()[1]
                    print(f"Client wins: {winner}!")
                    break
                elif data.startswith("TIE"):
                    print("Game is a tie.")
                    break
                elif data.startswith("MOVE"):
                    _, client_move = data.split()
                    client_pos = int(client_move) - 1
                    if board[client_pos] != ' ':
                        print("Invalid move from client. Game over.")
                        break
                    board[client_pos] = 'O'
                    result = check_win(board)
                    if result:
                        print_board(board)
                        if result == 'Tie':
                            print("It's a tie!")
                            conn.sendall(b"TIE\n")
                        else:
                            print(f"Player {result} wins!")
                            conn.sendall(f"WIN {result}\n".encode())
                        break
            print("Game over.")

if __name__ == "__main__":
    main()