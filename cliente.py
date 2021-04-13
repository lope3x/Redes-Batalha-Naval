import socket
import pickle
import sys
import time

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432  # The port used by the server
game_end = False
server_board = None
client_board = None
client_socket = None
server_hitted_last_round = False
client_hits = 0
server_hits = 0
number_of_hits_necessary_for_win = 30


def print_boards():
    print('        Server                 Client      ')
    print('  a b c d e f g h i j    a b c d e f g h i j')

    for i in range(0, 10):
        print(f'{i} ', end='')
        for j in range(0, 10):
            print(f'{server_board[i][j]} ', end='')
        print(f' {i} ', end='')

        for j in range(0, 10):
            if client_board[i][j] >= 0:
                print(f'{client_board[i][j]} ', end='')
            else:
                print('x ', end='')

        print('')


def read_board_from_file():
    global server_board, client_board
    board_file = open('board.txt', 'r')
    client_board = [[int(char) for char in line[:-1]] for line in board_file.readlines()]
    server_board = [[0 for _ in range(0, 10)] for _ in range(0, 10)]


def get_host_and_port():
    if len(sys.argv) != 3:
        print("Argumentos inválidos")
        exit()
    ip = sys.argv[1]
    port = sys.argv[2]
    print(ip, port)
    return ip, int(port)


def convert_char_to_num(char):
    return ord(char) - 97


def get_user_coordinates():
    while True:
        print("Por favor digite as coordenadas")
        row = int(input('Linha: '))
        col = int(convert_char_to_num(input('Coluna: ')))

        if 0 <= row < 10 and 0 <= col < 10:
            return row, col


def update_server_board(status, row, col):
    global server_board, client_hits, game_end

    if status == 'hit':
        server_board[row][col] = 'x'
        client_hits += 1

        if client_hits == number_of_hits_necessary_for_win:
            game_end = True
            return
    if status == 'miss':
        server_board[row][col] = 'm'


def play_game():
    global server_hitted_last_round, game_end, client_socket, server_hits
    row, col = get_user_coordinates()
    data_to_send_to_server = {
        "row": row,
        "col": col,
        "status": 'hit' if server_hitted_last_round else ''
    }

    if server_hitted_last_round:
        print(data_to_send_to_server['status'])

    client_socket.send(pickle.dumps(data_to_send_to_server))

    server_response_bytes = client_socket.recv(512)

    if not server_response_bytes:
        print('End connection')
        client_socket.close()
        game_end = True
        return

    server_response = pickle.loads(server_response_bytes)

    server_status = server_response['status']

    if server_status == 'hit':
        print("That's a HIT !!!")
        update_server_board(server_status, row, col)

        if game_end:
            print("Game ended, Client wins !! Congratulations")
            return
    elif server_status == 'miss':
        print("Oops you have missed =/")
        update_server_board(server_status, row, col)
    else:
        print("You already hit that position !!")

    server_row = server_response['row']
    server_col = server_response['col']

    time.sleep(1)

    print(f"Server attack !! Line: {server_row} Col: {chr(server_col + 97)}")

    target = client_board[server_row][server_col]

    if server_hit_at(target):
        print("Server hit =/")
        client_board[server_row][server_col] = -1
        server_hits += 1
        server_hitted_last_round = True

        if server_hits == number_of_hits_necessary_for_win:
            print('Game ended, Server Wins :(')
    elif target == -1:
        print("Server already hit !!!!")
        server_hitted_last_round = False
    else:
        print("Server missed !!!!")
        server_hitted_last_round = False

    print_boards()


def server_hit_at(target):
    return target > 0


def start_connection(ip, port):
    global client_socket
    server_address = (ip, port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    start_message = "Start Game"
    client_socket.send(pickle.dumps(start_message))
    server_response_bytes = client_socket.recv(512)
    server_response = pickle.loads(server_response_bytes)

    print(server_response)

    if not server_response == "Start game confirmed":
        print("Unexpected response from server")
        exit()


def main():
    ip, port = get_host_and_port()
    start_connection(ip, port)
    read_board_from_file()
    print("Game started")
    print_boards()

    while not game_end:
        play_game()


main()
