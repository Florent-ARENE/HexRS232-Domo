#!/usr/bin/env python3
"""
ATEM Client - Version fonctionnelle
Format CPvI validé : [ME, 0x00, source_hi, source_lo] (sans mask byte)
"""

import socket
import time
import threading

class ATEMClient:
    def __init__(self, ip, port=9910):
        self.ip = ip
        self.port = port
        self.sock = None
        self.session_id = 0x53AB
        self.local_seq = 0
        self.highest_remote = 0
        self.program = {}  # {ME: source}
        self.preview = {}  # {ME: source}
        self.connected = False
        self._running = False
        self._recv_thread = None
        self._lock = threading.Lock()
        
    def connect(self, timeout=10):
        """Établir la connexion avec l'ATEM"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.05)
        self.sock.bind(('', 0))
        
        # Envoi HELLO
        hello = bytearray(20)
        hello[0] = 0x10  # SYN
        hello[1] = 0x14  # Length = 20
        hello[2] = (self.session_id >> 8) & 0xFF
        hello[3] = self.session_id & 0xFF
        hello[12] = 0x01
        self.sock.sendto(bytes(hello), (self.ip, self.port))
        
        # Réception et ACK des paquets initiaux
        start = time.time()
        last_pkt = time.time()
        pkt_count = 0
        
        while time.time() - start < timeout:
            try:
                data, addr = self.sock.recvfrom(2048)
                pkt_count += 1
                last_pkt = time.time()
                
                self._process_packet(data)
                
            except socket.timeout:
                if time.time() - last_pkt > 0.5 and pkt_count > 50:
                    break
        
        self.connected = pkt_count > 50
        
        if self.connected:
            # Démarrer le thread de réception
            self._running = True
            self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
            self._recv_thread.start()
        
        return self.connected
    
    def _process_packet(self, data):
        """Traiter un paquet reçu"""
        if len(data) < 12:
            return
        
        flags = data[0]
        length = ((data[0] & 0x07) << 8) | data[1]
        recv_session = (data[2] << 8) | data[3]
        recv_remote = (data[10] << 8) | data[11]
        
        # Capturer session ID ATEM
        if recv_session != self.session_id and recv_session != 0:
            with self._lock:
                self.session_id = recv_session
        
        # Mettre à jour highest_remote
        with self._lock:
            if recv_remote > self.highest_remote:
                self.highest_remote = recv_remote
        
        # ACK les paquets RELIABLE/SYN
        if flags & 0x08 or flags & 0x10:
            self._send_ack(recv_remote)
        
        # Parser les commandes
        if length > 12:
            self._parse_commands(data)
    
    def _parse_commands(self, data):
        """Parser les commandes dans un paquet"""
        offset = 12
        while offset + 8 <= len(data):
            cmd_len = (data[offset] << 8) | data[offset + 1]
            if cmd_len < 8 or offset + cmd_len > len(data):
                break
            
            cmd_name = data[offset + 4:offset + 8].decode('ascii', errors='replace')
            payload = data[offset + 8:offset + cmd_len]
            
            if cmd_name == "PrgI" and len(payload) >= 4:
                me = payload[0]
                source = (payload[2] << 8) | payload[3]
                with self._lock:
                    self.program[me] = source
                    
            elif cmd_name == "PrvI" and len(payload) >= 4:
                me = payload[0]
                source = (payload[2] << 8) | payload[3]
                with self._lock:
                    self.preview[me] = source
            
            offset += cmd_len
    
    def _send_ack(self, remote_seq):
        """Envoyer un ACK"""
        ack = bytearray(12)
        ack[0] = 0x80  # ACK flag
        ack[1] = 0x0C
        with self._lock:
            ack[2] = (self.session_id >> 8) & 0xFF
            ack[3] = self.session_id & 0xFF
        ack[4] = (remote_seq >> 8) & 0xFF
        ack[5] = remote_seq & 0xFF
        
        try:
            self.sock.sendto(bytes(ack), (self.ip, self.port))
        except:
            pass
    
    def _recv_loop(self):
        """Thread de réception en arrière-plan"""
        while self._running:
            try:
                data, addr = self.sock.recvfrom(2048)
                self._process_packet(data)
            except socket.timeout:
                pass
            except:
                break
    
    def _send_command(self, cmd_name, payload):
        """Envoyer une commande à l'ATEM"""
        with self._lock:
            self.local_seq += 1
            local_seq = self.local_seq
            session_id = self.session_id
            highest_remote = self.highest_remote
        
        # Command block (aligné sur 4 bytes)
        cmd_len = 8 + len(payload)
        while cmd_len % 4 != 0:
            cmd_len += 1
        
        cmd = bytearray(cmd_len)
        cmd[0] = (cmd_len >> 8) & 0xFF
        cmd[1] = cmd_len & 0xFF
        cmd[4:8] = cmd_name.encode('ascii')
        for i, b in enumerate(payload):
            cmd[8 + i] = b
        
        # Header
        total = 12 + cmd_len
        hdr = bytearray(12)
        hdr[0] = 0x08 | ((total >> 8) & 0x07)  # RELIABLE
        hdr[1] = total & 0xFF
        hdr[2] = (session_id >> 8) & 0xFF
        hdr[3] = session_id & 0xFF
        hdr[4] = (highest_remote >> 8) & 0xFF
        hdr[5] = highest_remote & 0xFF
        hdr[10] = (local_seq >> 8) & 0xFF
        hdr[11] = local_seq & 0xFF
        
        pkt = bytes(hdr) + bytes(cmd)
        self.sock.sendto(pkt, (self.ip, self.port))
        
        return local_seq
    
    def set_preview_input(self, me, source):
        """Changer la source Preview d'un ME
        
        Args:
            me: M/E index (0 pour ME1)
            source: numéro de source (1-8 pour inputs, 1000=color bars, etc.)
        """
        # Format validé : [ME, 0x00, source_hi, source_lo]
        payload = [
            me & 0xFF,
            0x00,
            (source >> 8) & 0xFF,
            source & 0xFF
        ]
        return self._send_command("CPvI", payload)
    
    def set_program_input(self, me, source):
        """Changer la source Program d'un ME
        
        Args:
            me: M/E index (0 pour ME1)
            source: numéro de source
        """
        # Même format que CPvI
        payload = [
            me & 0xFF,
            0x00,
            (source >> 8) & 0xFF,
            source & 0xFF
        ]
        return self._send_command("CPgI", payload)
    
    def do_auto(self, me=0):
        """Exécuter une transition AUTO
        
        Args:
            me: M/E index (0 pour ME1)
        """
        payload = [me & 0xFF, 0x00, 0x00, 0x00]
        return self._send_command("DAut", payload)
    
    def do_cut(self, me=0):
        """Exécuter un CUT
        
        Args:
            me: M/E index (0 pour ME1)
        """
        payload = [me & 0xFF, 0x00, 0x00, 0x00]
        return self._send_command("DCut", payload)
    
    def get_program(self, me=0):
        """Obtenir la source Program actuelle"""
        with self._lock:
            return self.program.get(me)
    
    def get_preview(self, me=0):
        """Obtenir la source Preview actuelle"""
        with self._lock:
            return self.preview.get(me)
    
    def disconnect(self):
        """Fermer la connexion"""
        self._running = False
        if self._recv_thread:
            self._recv_thread.join(timeout=1)
        if self.sock:
            self.sock.close()
        self.connected = False


# Test
if __name__ == "__main__":
    print("=" * 70)
    print(" Test ATEM Client")
    print("=" * 70)
    
    atem = ATEMClient("172.18.29.12")
    
    print("\n[1] Connexion...")
    if not atem.connect():
        print("    ÉCHEC de connexion")
        exit(1)
    
    print(f"    Connecté! Session: 0x{atem.session_id:04X}")
    print(f"    Program ME0: {atem.get_program(0)}")
    print(f"    Preview ME0: {atem.get_preview(0)}")
    
    # Test Preview
    current_preview = atem.get_preview(0)
    new_preview = 2 if current_preview != 2 else 3
    
    print(f"\n[2] Test CPvI: Preview {current_preview} → {new_preview}")
    atem.set_preview_input(0, new_preview)
    time.sleep(0.5)
    
    updated_preview = atem.get_preview(0)
    print(f"    Preview maintenant: {updated_preview}")
    
    if updated_preview == new_preview:
        print("    ✓ CPvI fonctionne!")
        
        # Test AUTO
        print(f"\n[3] Test AUTO transition...")
        print(f"    Program: {atem.get_program(0)}, Preview: {atem.get_preview(0)}")
        atem.do_auto(0)
        time.sleep(2)
        print(f"    Program: {atem.get_program(0)}, Preview: {atem.get_preview(0)}")
        print("    ✓ Transition envoyée!")
    else:
        print(f"    ✗ Preview non changée")
    
    print("\n[4] Déconnexion...")
    atem.disconnect()
    print("    Terminé.")
    
    print("=" * 70)
