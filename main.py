from proxyclient import ProxyClient
import socks

destination_ip = "135.125.188.169"
destination_port = 6969
payload = "lobby;get_show_battle_info;2aaaaab585bec032"

if __name__ == '__main__':
    client = ProxyClient(destination_ip, destination_port)
    client.handshake()
    client.auth("user", "pass")
    input("Press enter to quit..")
    client.disconnect()
        
