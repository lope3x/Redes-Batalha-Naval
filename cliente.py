import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432  # The port used by the server
game_end = False
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world')
    data = s.recv(1024)

print('Received', data)


def get_board():
    # Lê tabuleiro do arquivo txt
    return 1


def get_host_and_port():
    # Pega host e port dos parametros passados
    return 1, 1

def play_game():
    #aguarda usuario escolher posição
    #envia posição para o servidor
    #aguarda resposta do servidor
    #ao receber resposta de acerto do servidor, atualiza "tabuleiro do servidor"
    #ao mesmo tempo também verifica se o servidor acertou ou não
    #envia para o servidor se ele acertou
    #verifica se o jogo acabou
    if game_end:
        return
    else:
        # envia para o servidor que o jogo NÃO acabou
        pass

def main():
    board = get_board()
    host, port = get_host_and_port()
    #conecta ao servidor
    while not game_end:
        play_game()
    #envia para o server que o jogo acabou
    #encerra conexão
    #anuncia vencedor
    #finaliza o programa