from python_socks.sync import Proxy
from encryption import AesEncryption
from queue import Queue
import socket
from threading import Thread
import json
import logging

class ProxyClient:

    def __init__(self, dest_ip, dest_port, proxy = None):
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.proxy = proxy
        self.__crypt_manager = AesEncryption()
        self.__packets_queue = Queue()
        self.__disconnecting = False
        self.RECEIVE_BUFFER_SIZE = 8192
    
    def __split_packets(self, data):
        while True:
            part_data = data.partition("end~")
            if not part_data[1]:
                return data
            self.__packets_queue.put(part_data[0])
            data = part_data[2]

    def __receive_loop(self):
        full_data = ''
        while not self.__disconnecting:
            try:
                data = self.__s.recv(self.RECEIVE_BUFFER_SIZE)
                if not data:
                    pass
                decoded_data = data.decode('utf-8', 'ignore')
                full_data += decoded_data
                full_data = self.__split_packets(full_data)
            except:
                pass
    
    def set_timeout(self, timeout):
        self.__s.settimeout(timeout)

    def receive_data(self, packet_name = None, timeout = 10) -> str:
        packet = self.__packets_queue.get(timeout=timeout)
        if not packet_name or packet.startswith(packet_name):
            return packet
        return self.receive_data(packet_name, timeout)
        
    def send_data(self, data) -> None:
        data = self.__crypt_manager.encrypt(data).encode()
        self.__s.sendall(data)

    def handshake(self):
        try:
            if self.proxy:
                proxy = Proxy.from_url(self.proxy)
                self.__s = proxy.connect(dest_host=self.dest_ip, dest_port=self.dest_port)
            else:
                self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__s.connect((self.dest_ip, self.dest_port))
            self.__s.settimeout(10)
            receive_thread = Thread(target=self.__receive_loop)
            receive_thread.start()
            self.send_data("system;get_aes_data;RU")
            data = self.receive_data("system;set_aes_data;")
            logging.debug(f"Connected to {self.dest_ip}:{self.dest_port}")
            aes_data = data.split(';')[-1]
            self.__crypt_manager.parse_key(aes_data)
            logging.debug("Succesfully handshaked!")
        except:
            self.disconnect()
            raise Exception("Can't connect to server")

    def check_register_nickname(self, nickname):
        self.send_data(f"registration;check_name;{nickname}")
        while True:
            packet = self.receive_data()
            if packet == "registration;check_name_result;nickname_exist":
                logging.debug(f"Nickname {nickname} exist!")
                return False
            elif packet == "registration;check_name_result;not_exist":
                return True
    
    def load_resources(self):
        resource_packet = self.receive_data("system;load_resources;")
        resource_id = resource_packet.split(';')[-1]
        self.send_data(f"system;resources_loaded;{resource_id}")

    def get_garage_data(self):
        self.send_data("lobby;get_garage_data")
        data = self.receive_data("garage;init_garage_items;")
        data = data.split(';')[-1]
        return json.loads(data)

    def auth(self, login, password):
        logging.debug("Authorization..")
        self.receive_data("system;init_auth")
        self.send_data("auth;state")
        self.send_data(f"auth;{login};{password};false;")
        while True:
            packet = self.receive_data()
            if packet.startswith("auth;denied"):
                logging.debug("Invalid credentials!")
                return False
            elif packet.startswith("auth;ban"):
                logging.debug("Account banned!")
                return False
            elif packet.startswith("auth;accept"):
                logging.debug("Requesting user info..")
                self.send_data("lobby;user_inited")
            elif packet.startswith("auth;wrong_captcha"):
                logging.error("Received captcha")
                raise Exception("Received captcha")
            elif packet.startswith("lobby;init_panel"):
                current_user_info = json.loads(packet.split(';')[2])
                logging.debug("Successfully logged in!")
                return current_user_info
        
    
    def get_user_info(self, nickname):
        self.send_data(f"lobby;get_user_info;{nickname}")
        try:
            data = self.receive_data("lobby;update_user_info;")
            user_info = data.split(';')[2]
            return json.loads(user_info)
        except:
            logging.debug("Can't get user data")

    def get_battles(self):
        self.send_data("lobby;get_data_init_battle_select")
        try:
            data = self.receive_data("lobby;init_battle_select")
            battles = data.split(';')[2]
            return json.loads(battles)
        except:
            logging.debug("Can't get battles")
    
    def get_battle_info(self, battle_id):
        self.send_data(f"lobby;get_show_battle_info;{battle_id}")
        try:
            data = self.receive_data("lobby;show_battle_info;")
            battle_info = data.split(';')[2]
            return json.loads(battle_info)
        except:
            logging.debug("Can't get battle info")

    def enter_battle(self, battle_id):
        self.send_data(f"lobby;enter_battle;{battle_id};false")
        self.send_data(f"lobby;enter_battle_team;{battle_id};true")
        self.send_data(f"lobby;enter_battle_team;{battle_id};false")
        try:
            self.receive_data("lobby;start_battle")
            self.send_data("battle;get_init_data_local_tank")
            return True
        except:
            return False

    def leave_battle(self):
        self.send_data("battle;i_exit_from_battle")

    def buy_item(self, item_id, count):
        self.send_data(f"garage;try_buy_item;{item_id};{count}")

    def change_password(self, old_password, new_password):
        self.send_data(f"lobby;change_password;{old_password};{new_password}")
        try:
            self.receive_data("lobby;server_message;")
            return True
        except:
            return False

    def send_battle_chat(self, message):
        self.send_data(f"battle;chat;{message};false")
        
    def disconnect(self):
        try:
            self.__s.close()
        except:
            pass
        self.__disconnecting = True