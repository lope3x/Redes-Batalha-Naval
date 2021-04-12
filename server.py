import pickle
import random
import socket
import sys

server_socket = None
client_socket = None
game_end = False
board = None
target_row = 0
target_col = 0
hit_last_round = False


def get_port():
    port = None
    if len(sys.argv) == 1:
        print("Por favor passe a Porta como argumento")
        exit()
    elif len(sys.argv) > 2:
        print("Muitos argumentos será assumido que a porta é o primeiro deles")
        port = sys.argv[1]
    else:
        port = sys.argv[1]
    return int(port)


# 0->vazio
# 1,2,3,4 -> navios
# -1 -> local acertado
# def read_board_from_file():
#     global board
#     board_file = open('board.txt', 'r')
#     board = [[int(char) for char in line[:-1]] for line in board_file.readlines()]

def decide_vertical_or_horizontal():
    decide = random.randint(0, 1)
    if decide == 1:
        return 'vertical'
    else:
        return 'horizontal'


def generate_board():
    global board
    board = [[0 for _ in range(0, 10)] for _ in range(0, 10)]
    boats = [(1, 5), (2, 4), (3, 3), (4, 2)]
    for boat in boats:
        put_boat(boat)


def put_boat(boat):
    global board
    num_of_boats = boat[0]
    board_temp = [row[:] for row in board]
    for _ in range(0, num_of_boats):
        vertical_or_horizontal = decide_vertical_or_horizontal()
        size = boat[1]
        x, y = get_available_coordinates(board_temp, size, vertical_or_horizontal)

        if vertical_or_horizontal == 'vertical':
            if x + size <= 9:
                for i in range(x, x + size):
                    board_temp[i][y] = boat[0]
            else:
                for i in range(x - size, x):
                    board_temp[i][y] = boat[0]
        else:
            if y + size <= 9:
                for i in range(y, y + size):
                    board_temp[x][i] = boat[0]
            else:
                for i in range(y - size, y):
                    board_temp[x][i] = boat[0]
    board = board_temp


def get_available_coordinates(board_temp, size, vertical_or_horizontal):
    available = False
    x = 0
    y = 0
    while not available:
        x = random.randint(0, 9)
        y = random.randint(0, 9)
        if vertical_or_horizontal == 'vertical':
            if x + size <= 9:
                available = True
                for i in range(x, x + size):
                    if board_temp[i][y] != 0:
                        available = False
                        break
            else:
                available = True
                for i in range(x - size, x):
                    if board_temp[i][y] != 0:
                        available = False
                        break
        else:
            if y + size <= 9:
                available = True
                for i in range(y, y + size):
                    if board_temp[x][i] != 0:
                        available = False
                        break
            else:
                available = True
                for i in range(y - size, y):
                    if board_temp[x][i] != 0:
                        available = False
                        break
    return x, y


def print_board():
    print('        Server       ')
    print('  a b c d e f g h i j')

    for i in range(0, 10):
        print(f'{i} ', end='')
        for j in range(0, 10):
            print(f'{board[i][j]} ', end='')
        print('')


def start_server():
    global server_socket
    server_port = get_port()
    server_ip = socket.gethostbyname(socket.gethostname())
    server_address = (server_ip, server_port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(server_address)
    server_socket.listen(1)
    print(f'Server started.\nIp Address: {server_ip}\nPort: {server_port}\n')


def awaiting_connection():
    global client_socket, server_socket
    print("Waiting connection")
    client_socket, client_address = server_socket.accept()

    print(f'Connection from {client_address}')
    client_data_bytes = client_socket.recv(512)
    client_data = pickle.loads(client_data_bytes)

    if not client_data == 'Start game':
        print('Unexpected data from client')
        return


def confirm_start_game():
    global client_socket

    client_socket.send(pickle.dumps('Start game confirmed'))


def play_game():
    global client_socket, server_socket, game_end, hit_last_round
    data_bytes = client_socket.recv(512)

    if not data_bytes:
        client_socket.close()
        game_end = True
        return

    data_received = pickle.loads(data_bytes)

    if data_received['status'] == 'end':
        game_end = True
        return
    hit_last_round = data_received['status'] == 'hit'

    row_received = data_received['row']
    col_received = data_received['col']

    row_response, col_response = get_target_coordinates()

    response_to_client = {
        'status': '',
        'row': row_response,
        'col': col_response
    }

    client_target = board[row_received][col_received]

    if client_has_hit_boat(client_target):
        response_to_client['status'] = 'hit'
        board[row_received][col_received] = -1
    elif client_target == 0:
        response_to_client['status'] = 'miss'
    else:
        response_to_client['status'] = 'already-hit'

    print_board()

    response_to_client_bytes = pickle.dumps(response_to_client)
    client_socket.send(response_to_client_bytes)


def coordinate_inside_board(x, y):
    return 0 <= x <= 9 and 0 <= y <= 9


def get_target_coordinates():
    if hit_last_round:
        col, row = generate_new_coordinate_based_on_hit()
        while not coordinate_inside_board(row, col):
            col, row = generate_new_coordinate_based_on_hit()

    else:
        row = random.randint(0, 9)
        col = random.randint(0, 9)

    return row, col


def generate_new_coordinate_based_on_hit():
    dx = [-1, 1]
    dy = [-1, 1]

    random_number_row_or_col = random.randint(0, 1)
    random_number_plus_or_minus = random.randint(0, 1)
    if random_number_row_or_col == 1:
        row = target_row + dx[random_number_plus_or_minus]
        col = target_col
    else:
        row = target_row
        col = target_col + dy[random_number_plus_or_minus]
    return col, row


def client_has_hit_boat(target):
    return target > 0


def main():
    # start_server()
    # awaiting_connection()
    # confirm_start_game()
    generate_board()
    print_board()
    # print("Game Started")
    # print_board()
    # while not game_end:
    #     play_game()
    # print('Client disconnected')
    # print('Closing server')
    # client_socket.close()
    # server_socket.close()


main()
