#!/usr/bin/env python3
"""
Tamagotchi Web Interface
Server Flask con SocketIO per l'interfaccia web del Tamagotchi
"""

import json
import os
import sys
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import threading
import time

# Aggiungi il path per bashio
sys.path.append('/usr/lib/python3.11/site-packages')

try:
    import bashio
    import requests
except ImportError:
    # Fallback per testing locale
    class MockBashio:
        @staticmethod
        def log_info(msg): print(f"INFO: {msg}")
        @staticmethod
        def log_warning(msg): print(f"WARN: {msg}")
        @staticmethod
        def log_error(msg): print(f"ERROR: {msg}")
        @staticmethod
        def addon_info(key): 
            return {"ingress_token": "test_token"} if key == "ingress" else None
    bashio = MockBashio()
    import requests

import os
app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)) + '/templates')
app.config['SECRET_KEY'] = 'tamagotchi_secret_key'

class HomeAssistantAPI:
    def __init__(self):
        # Home Assistant Supervisor API
        self.base_url = "http://supervisor/core/api"
        try:
            # Token di autenticazione per add-on
            self.token = os.environ.get('SUPERVISOR_TOKEN', '')
            if not self.token:
                # Fallback per sviluppo locale
                self.token = "test_token"
                self.base_url = "http://localhost:8123/api"
        except:
            bashio.log_warning("Impossibile ottenere token Home Assistant")
            self.token = ""
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def get_areas(self):
        """Ottiene la lista delle aree/stanze"""
        try:
            response = requests.get(f"{self.base_url}/config/area_registry", headers=self.headers, timeout=5)
            if response.status_code == 200:
                areas = response.json()
                return [{"id": area["area_id"], "name": area["name"]} for area in areas]
            else:
                bashio.log_warning(f"Errore API aree: {response.status_code}")
        except Exception as e:
            bashio.log_error(f"Errore connessione Home Assistant: {e}")
        
        # Aree di default se non riusciamo a connetterci
        return [
            {"id": "living_room", "name": "Salotto"},
            {"id": "kitchen", "name": "Cucina"},
            {"id": "bedroom", "name": "Camera da Letto"},
            {"id": "bathroom", "name": "Bagno"},
            {"id": "garage", "name": "Garage"}
        ]
    
    def get_area_devices(self, area_id):
        """Ottiene i dispositivi di un'area specifica"""
        try:
            # Ottieni tutti gli stati
            response = requests.get(f"{self.base_url}/states", headers=self.headers, timeout=5)
            if response.status_code == 200:
                states = response.json()
                # Filtra per dispositivi controllabili (luci, interruttori, ecc.)
                devices = []
                for state in states:
                    entity_id = state["entity_id"]
                    domain = entity_id.split(".")[0]
                    
                    # Solo domini controllabili
                    if domain in ["light", "switch", "fan", "climate", "cover"]:
                        devices.append({
                            "entity_id": entity_id,
                            "name": state["attributes"].get("friendly_name", entity_id),
                            "state": state["state"],
                            "domain": domain,
                            "attributes": state["attributes"]
                        })
                
                return devices[:5]  # Limita a 5 dispositivi per area
        except Exception as e:
            bashio.log_error(f"Errore ottenimento dispositivi: {e}")
        
        # Dispositivi mock se non riusciamo a connetterci
        mock_devices = {
            "living_room": [
                {"entity_id": "light.salotto", "name": "Luce Salotto", "state": "off", "domain": "light"},
                {"entity_id": "switch.tv", "name": "TV", "state": "off", "domain": "switch"}
            ],
            "kitchen": [
                {"entity_id": "light.cucina", "name": "Luce Cucina", "state": "on", "domain": "light"}
            ],
            "bedroom": [
                {"entity_id": "light.camera", "name": "Luce Camera", "state": "off", "domain": "light"}
            ],
            "bathroom": [
                {"entity_id": "light.bagno", "name": "Luce Bagno", "state": "off", "domain": "light"}
            ],
            "garage": [
                {"entity_id": "cover.garage", "name": "Porta Garage", "state": "closed", "domain": "cover"}
            ]
        }
        return mock_devices.get(area_id, [])
    
    def control_device(self, entity_id, service, service_data=None):
        """Controlla un dispositivo"""
        try:
            domain = entity_id.split(".")[0]
            url = f"{self.base_url}/services/{domain}/{service}"
            data = {"entity_id": entity_id}
            if service_data:
                data.update(service_data)
            
            response = requests.post(url, headers=self.headers, json=data, timeout=5)
            return response.status_code == 200
        except Exception as e:
            bashio.log_error(f"Errore controllo dispositivo: {e}")
            return False

# Istanza globale
ha_api = HomeAssistantAPI()

class TamagotchiWebInterface:
    def __init__(self):
        self.data_dir = '/data'
        self.save_file = os.path.join(self.data_dir, 'tamagotchi.json')
        
    def load_state(self):
        """Carica lo stato del Tamagotchi"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                bashio.log_error(f"Errore nel caricamento stato: {e}")
        
        # Stato di default se non esiste
        return {
            'name': 'Tama',
            'birth_date': datetime.now().isoformat(),
            'last_update': datetime.now().isoformat(),
            'current_room': 'living_room',
            'stats': {
                'hunger': 100,
                'happiness': 100,
                'health': 100,
                'energy': 100,
                'age_days': 0
            },
            'status': 'happy',
            'evolution_stage': 'egg',
            'total_care_score': 100
        }
    
    def save_state(self, state):
        """Salva lo stato del Tamagotchi"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.save_file, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception as e:
            bashio.log_error(f"Errore nel salvataggio: {e}")
            return False
    
    def perform_action(self, action):
        """Esegue un'azione sul Tamagotchi"""
        state = self.load_state()
        
        if action == 'feed':
            if state['status'] == 'dead':
                return False, "Il Tamagotchi è morto..."
            
            state['stats']['hunger'] = min(100, state['stats']['hunger'] + 20)
            state['stats']['happiness'] = min(100, state['stats']['happiness'] + 5)
            state['total_care_score'] = min(100, state['total_care_score'] + 1)
            message = "Yum! Il tuo Tamagotchi è stato nutrito!"
            
        elif action == 'play':
            if state['status'] == 'dead':
                return False, "Il Tamagotchi è morto..."
            if state['stats']['energy'] < 20:
                return False, "Il Tamagotchi è troppo stanco per giocare!"
            
            state['stats']['happiness'] = min(100, state['stats']['happiness'] + 15)
            state['stats']['energy'] = max(0, state['stats']['energy'] - 10)
            state['total_care_score'] = min(100, state['total_care_score'] + 2)
            message = "Che divertimento! Il tuo Tamagotchi è felice!"
            
        elif action == 'sleep':
            if state['status'] == 'dead':
                return False, "Il Tamagotchi è morto..."
            
            state['stats']['energy'] = min(100, state['stats']['energy'] + 30)
            state['stats']['health'] = min(100, state['stats']['health'] + 5)
            message = "Zzz... Il tuo Tamagotchi si sta riposando!"
            
        elif action == 'medicine':
            if state['status'] == 'dead':
                return False, "Il Tamagotchi è morto..."
            if state['stats']['health'] > 80:
                return False, "Il Tamagotchi è già in salute!"
            
            state['stats']['health'] = min(100, state['stats']['health'] + 25)
            state['stats']['happiness'] = max(0, state['stats']['happiness'] - 5)
            state['total_care_score'] = min(100, state['total_care_score'] + 3)
            message = "Il tuo Tamagotchi si sente meglio!"
            
        elif action == 'rename':
            new_name = request.json.get('name', 'Tama')
            state['name'] = new_name[:20]  # Massimo 20 caratteri
            message = f"Il tuo Tamagotchi ora si chiama {state['name']}!"
            
        elif action == 'move_to_room':
            room_id = request.json.get('room_id', 'living_room')
            old_room = state.get('current_room', 'living_room')
            state['current_room'] = room_id
            
            # Trova il nome della stanza
            areas = ha_api.get_areas()
            room_name = next((area['name'] for area in areas if area['id'] == room_id), room_id)
            
            message = f"{state['name']} si è spostato in {room_name}!"
            bashio.log_info(f"Tamagotchi moved from {old_room} to {room_id}")
            
        else:
            return False, "Azione non valida"
        
        # Aggiorna timestamp
        state['last_update'] = datetime.now().isoformat()
        
        # Salva stato
        if self.save_state(state):
            bashio.log_info(f"Azione '{action}' eseguita con successo")
            return True, message
        else:
            return False, "Errore nel salvataggio"

# Istanza globale
tamagotchi = TamagotchiWebInterface()

@app.route('/')
def index():
    """Pagina principale"""
    return render_template('index.html')

@app.route('/api/state')
def get_state():
    """API per ottenere lo stato del Tamagotchi"""
    state = tamagotchi.load_state()
    # Aggiungi informazioni sulle stanze e dispositivi
    current_room = state.get('current_room', 'living_room')
    state['rooms'] = ha_api.get_areas()
    state['current_room_devices'] = ha_api.get_area_devices(current_room)
    return jsonify(state)

@app.route('/api/rooms')
def get_rooms():
    """API per ottenere la lista delle stanze"""
    rooms = ha_api.get_areas()
    return jsonify(rooms)

@app.route('/api/room/<room_id>/devices')
def get_room_devices(room_id):
    """API per ottenere i dispositivi di una stanza"""
    devices = ha_api.get_area_devices(room_id)
    return jsonify(devices)

@app.route('/api/device/control', methods=['POST'])
def control_device():
    """API per controllare un dispositivo"""
    entity_id = request.json.get('entity_id')
    service = request.json.get('service')
    service_data = request.json.get('service_data', {})
    
    if not entity_id or not service:
        return jsonify({'success': False, 'message': 'Parametri mancanti'})
    
    success = ha_api.control_device(entity_id, service, service_data)
    
    if success:
        device_name = entity_id.split('.')[-1].replace('_', ' ').title()
        return jsonify({'success': True, 'message': f'{device_name} controllato!'})
    else:
        return jsonify({'success': False, 'message': 'Errore nel controllo del dispositivo'})

@app.route('/api/action', methods=['POST'])
def perform_action():
    """API per eseguire azioni sul Tamagotchi"""
    action = request.json.get('action')
    success, message = tamagotchi.perform_action(action)
    
    # Aggiornamento completato
    
    return jsonify({
        'success': success,
        'message': message
    })

# Nessun WebSocket per ora - usiamo polling

if __name__ == '__main__':
    bashio.log_info("Avvio server web Tamagotchi...")
    
    # Avvia server Flask normale
    app.run(host='0.0.0.0', port=8080, debug=False) 