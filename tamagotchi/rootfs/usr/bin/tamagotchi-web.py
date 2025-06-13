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
        def log_debug(msg): print(f"DEBUG: {msg}")
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
        # Home Assistant Supervisor API - Fix del path corretto
        self.base_url = "http://supervisor/core/api"
        self.token = ""
        
        # Prova a ottenere il token in vari modi
        try:
            # Metodo 1: Variabile ambiente standard
            self.token = os.environ.get('SUPERVISOR_TOKEN')
            if not self.token:
                # Metodo 2: File token del supervisor
                try:
                    with open('/run/secrets/SUPERVISOR_TOKEN', 'r') as f:
                        self.token = f.read().strip()
                except:
                    pass
            
            if not self.token:
                # Metodo 3: Token dall'add-on info
                try:
                    addon_info = bashio.addon_info()
                    if addon_info and 'ingress_token' in addon_info:
                        self.token = addon_info['ingress_token']
                except:
                    pass
                    
            if not self.token:
                bashio.log_warning("Token Home Assistant non trovato - usando dispositivi mock")
                self.use_mock = True
            else:
                bashio.log_info("Token Home Assistant ottenuto con successo")
                self.use_mock = False
                
        except Exception as e:
            bashio.log_error(f"Errore ottenimento token: {e}")
            self.use_mock = True
            
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def get_areas(self):
        """Ottiene SOLO le aree reali che hanno dispositivi effettivi"""
        bashio.log_info("🏠 Inizio ricerca aree...")
        
        try:
            # Metodo 1: Prova API Area Registry (richiede hassio_role: homeassistant)
            bashio.log_info("📡 Tentativo accesso Area Registry API...")
            response = requests.get(f"{self.base_url}/config/area_registry", headers=self.headers, timeout=5)
            if response.status_code == 200:
                area_registry = response.json()
                bashio.log_info(f"✅ Area Registry API successo! Trovate {len(area_registry)} aree registrate")
                if area_registry:
                    # Ottieni dispositivi per ogni area registrata
                    real_areas = []
                    for area in area_registry:
                        area_id = area["area_id"]
                        area_name = area["name"]
                        
                        # Controlla se l'area ha dispositivi
                        devices = self.get_area_devices_for_validation(area_id, area_name)
                        if devices:  # Solo se ci sono dispositivi
                            real_areas.append({"id": area_id, "name": area_name})
                    
                    if real_areas:
                        bashio.log_info(f"✅ Trovate {len(real_areas)} aree reali con dispositivi")
                        return real_areas
            else:
                bashio.log_warning(f"Area Registry API non disponibile: {response.status_code}")
        except Exception as e:
            bashio.log_error(f"Errore accesso Area Registry: {e}")
        
        # Metodo 2: Scopri aree dai dispositivi esistenti
        bashio.log_info("🔍 Tentativo discovery automatica dalle entità...")
        try:
            bashio.log_info(f"📡 Chiamata API /states su {self.base_url}/states")
            response = requests.get(f"{self.base_url}/states", headers=self.headers, timeout=10)
            bashio.log_info(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                states = response.json()
                bashio.log_info(f"🔍 Analizzando {len(states)} entità da Home Assistant...")
                
                # Debug: mostra tutti i dispositivi controllabili trovati
                controllable_devices = []
                for state in states:
                    entity_id = state["entity_id"]
                    domain = entity_id.split(".")[0]
                    if domain in ["light", "switch", "fan", "climate", "cover", "media_player"]:
                        friendly_name = state["attributes"].get("friendly_name", entity_id)
                        controllable_devices.append(f"{entity_id} ({friendly_name})")
                
                if controllable_devices:
                    bashio.log_info(f"✅ Trovati {len(controllable_devices)} dispositivi controllabili:")
                    for device in controllable_devices[:10]:  # Mostra primi 10
                        bashio.log_info(f"  - {device}")
                    if len(controllable_devices) > 10:
                        bashio.log_info(f"  ... e altri {len(controllable_devices) - 10} dispositivi")
                else:
                    bashio.log_warning("⚠️ Nessun dispositivo controllabile trovato!")
                
                discovered_areas = {}
                
                # Mappa parole chiave comuni a ID area
                keyword_map = {
                    "salotto": "salotto", "living": "salotto", "soggiorno": "salotto", "sala": "salotto",
                    "cucina": "cucina", "kitchen": "cucina",
                    "camera": "camera", "bedroom": "camera", "letto": "camera", "cameretta": "camera",
                    "bagno": "bagno", "bathroom": "bagno", "wc": "bagno",
                    "garage": "garage", "cantina": "garage", "box": "garage",
                    "studio": "studio", "ufficio": "studio", "office": "studio",
                    "giardino": "giardino", "garden": "giardino", "terrazzo": "giardino", "esterno": "giardino",
                    "ingresso": "ingresso", "entrance": "ingresso", "entrata": "ingresso",
                    "corridoio": "corridoio", "hallway": "corridoio",
                    "lavanderia": "lavanderia", "laundry": "lavanderia"
                }
                
                bashio.log_info(f"🔍 Cerco parole chiave: {list(keyword_map.keys())}")
                
                # Analizza ogni entità per scoprire aree
                for state in states:
                    entity_id = state["entity_id"]
                    domain = entity_id.split(".")[0]
                    
                    # Solo domini controllabili
                    if domain in ["light", "switch", "fan", "climate", "cover", "media_player", "sensor"]:
                        friendly_name = state["attributes"].get("friendly_name", "").lower()
                        entity_lower = entity_id.lower()
                        
                        # Cerca corrispondenze con parole chiave
                        for keyword, area_id in keyword_map.items():
                            if keyword in entity_lower or keyword in friendly_name:
                                if area_id not in discovered_areas:
                                    discovered_areas[area_id] = {
                                        "id": area_id,
                                        "name": area_id.capitalize(),
                                        "device_count": 0
                                    }
                                discovered_areas[area_id]["device_count"] += 1
                                bashio.log_info(f"🎯 Trovato dispositivo per area '{area_id}': {entity_id}")
                                break
                
                # Ritorna solo le aree che hanno almeno 1 dispositivo
                real_areas = [area for area in discovered_areas.values() if area["device_count"] > 0]
                
                if real_areas:
                    bashio.log_info(f"✅ Scoperte {len(real_areas)} aree dai dispositivi reali:")
                    for area in real_areas:
                        bashio.log_info(f"  - {area['name']}: {area['device_count']} dispositivi")
                    
                    # Rimuovi il conteggio per l'output finale
                    return [{"id": area["id"], "name": area["name"]} for area in real_areas]
                else:
                    bashio.log_warning("⚠️ Nessuna area scoperta dai dispositivi trovati!")
            else:
                bashio.log_error(f"❌ Errore API /states: {response.status_code} - {response.text}")
                
        except Exception as e:
            bashio.log_error(f"❌ Errore analisi dispositivi reali: {e}")
        
        # NESSUN FALLBACK - Se non troviamo nulla, ritorniamo None
        bashio.log_error("❌ NESSUNA AREA TROVATA! Verifica che ci siano dispositivi controllabili in Home Assistant")
        return None
    
    def get_area_devices_for_validation(self, area_id, area_name):
        """Metodo di validazione per controllare se un'area ha dispositivi (per Area Registry)"""
        try:
            response = requests.get(f"{self.base_url}/states", headers=self.headers, timeout=5)
            if response.status_code != 200:
                return []
            
            states = response.json()
            area_name_lower = area_name.lower()
            devices = []
            
            for state in states:
                entity_id = state["entity_id"]
                domain = entity_id.split(".")[0]
                
                if domain in ["light", "switch", "fan", "climate", "cover", "media_player"]:
                    friendly_name = state["attributes"].get("friendly_name", "").lower()
                    entity_lower = entity_id.lower()
                    
                    # Cerca corrispondenze con il nome dell'area
                    if area_name_lower in entity_lower or area_name_lower in friendly_name:
                        devices.append(entity_id)
                        
                        if len(devices) >= 3:  # Limit per performance
                            break
            
            return devices
            
        except Exception as e:
            bashio.log_error(f"Errore validazione area {area_name}: {e}")
            return []
    
    def get_area_devices(self, area_id):
        """Ottiene i dispositivi di un'area specifica usando solo API pubbliche"""
        try:
            # Usa solo l'API /states che funziona sempre
            response = requests.get(f"{self.base_url}/states", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                bashio.log_warning(f"Errore API states: {response.status_code}")
                return []
            
            states = response.json()
            bashio.log_info(f"Ottenuti {len(states)} stati da Home Assistant per area {area_id}")
            
            # Filtra dispositivi controllabili
            devices = []
            
            # Mappa dinamica delle parole chiave per area
            area_keywords_map = {
                "salotto": ["salotto", "living", "soggiorno", "sala"],
                "cucina": ["cucina", "kitchen"],
                "camera": ["camera", "bedroom", "letto", "cameretta"],
                "bagno": ["bagno", "bathroom", "wc"],
                "garage": ["garage", "cantina", "box"],
                "studio": ["studio", "ufficio", "office"],
                "giardino": ["giardino", "garden", "terrazzo", "esterno"],
                "ingresso": ["ingresso", "entrance", "entrata"],
                "corridoio": ["corridoio", "hallway"],
                "lavanderia": ["lavanderia", "laundry"]
            }
            
            # Ottieni le parole chiave per l'area richiesta
            keywords = area_keywords_map.get(area_id, [area_id])
            
            for state in states:
                entity_id = state["entity_id"]
                domain = entity_id.split(".")[0]
                
                # Solo domini controllabili
                if domain in ["light", "switch", "fan", "climate", "cover", "media_player"]:
                    friendly_name = state["attributes"].get("friendly_name", entity_id)
                    entity_lower = entity_id.lower()
                    name_lower = friendly_name.lower()
                    
                    # Filtra per parole chiave nell'entity_id o friendly_name
                    if any(keyword in name_lower or keyword in entity_lower for keyword in keywords):
                        devices.append({
                            "entity_id": entity_id,
                            "name": friendly_name,
                            "state": state["state"],
                            "domain": domain,
                            "attributes": state["attributes"]
                        })
            
            bashio.log_info(f"Trovati {len(devices)} dispositivi reali per area {area_id}")
            return devices[:8]  # Massimo 8 dispositivi per area
            
        except Exception as e:
            bashio.log_error(f"Errore ottenimento dispositivi per area {area_id}: {e}")
            return []
    
    def control_device(self, entity_id, service, service_data=None):
        """Controlla un dispositivo"""
        if self.use_mock:
            bashio.log_info(f"Mock: {service} su {entity_id}")
            return True
            
        try:
            domain = entity_id.split(".")[0]
            url = f"{self.base_url}/services/{domain}/{service}"
            data = {"entity_id": entity_id}
            if service_data:
                data.update(service_data)
            
            bashio.log_info(f"Controllo dispositivo: {entity_id} -> {service}")
            bashio.log_debug(f"URL: {url}")
            bashio.log_debug(f"Data: {data}")
            
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            bashio.log_debug(f"Response status: {response.status_code}")
            if response.status_code != 200:
                bashio.log_error(f"Errore API Home Assistant: {response.status_code} - {response.text}")
                return False
                
            bashio.log_info(f"Dispositivo {entity_id} controllato con successo")
            return True
            
        except requests.exceptions.Timeout:
            bashio.log_error(f"Timeout controllo dispositivo {entity_id}")
            return False
        except requests.exceptions.ConnectionError:
            bashio.log_error(f"Errore connessione Home Assistant per {entity_id}")
            return False
        except Exception as e:
            bashio.log_error(f"Errore controllo dispositivo {entity_id}: {e}")
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
        
        # Se il Tamagotchi è morto, riportalo in vita con 1 HP
        if state['status'] == 'dead':
            state['stats']['health'] = 1
            state['stats']['hunger'] = 50
            state['stats']['happiness'] = 50
            state['stats']['energy'] = 50
            state['status'] = 'critical'
            bashio.log_info("Tamagotchi resuscitato con 1 HP!")
        
        if action == 'feed':
            # Boost maggiore se in stato critico
            hunger_boost = 30 if state['status'] == 'critical' else 20
            happiness_boost = 10 if state['status'] == 'critical' else 5
            
            state['stats']['hunger'] = min(100, state['stats']['hunger'] + hunger_boost)
            state['stats']['happiness'] = min(100, state['stats']['happiness'] + happiness_boost)
            state['total_care_score'] = min(100, state['total_care_score'] + 1)
            
            if state['status'] == 'critical':
                message = "Nutrizione d'emergenza! Il tuo Tamagotchi si sente un po' meglio!"
            else:
                message = "Yum! Il tuo Tamagotchi è stato nutrito!"
            
        elif action == 'play':
            if state['stats']['energy'] < 15:
                return False, "Il Tamagotchi è troppo stanco per giocare!"
            
            # Boost maggiore se in stato critico
            happiness_boost = 25 if state['status'] == 'critical' else 15
            energy_cost = 5 if state['status'] == 'critical' else 10
            
            state['stats']['happiness'] = min(100, state['stats']['happiness'] + happiness_boost)
            state['stats']['energy'] = max(0, state['stats']['energy'] - energy_cost)
            state['total_care_score'] = min(100, state['total_care_score'] + 2)
            
            if state['status'] == 'critical':
                message = "Gioco terapeutico! Il tuo Tamagotchi sorride un po'!"
            else:
                message = "Che divertimento! Il tuo Tamagotchi è felice!"
            
        elif action == 'sleep':
            # Boost maggiore se in stato critico
            energy_boost = 40 if state['status'] == 'critical' else 30
            health_boost = 10 if state['status'] == 'critical' else 5
            
            state['stats']['energy'] = min(100, state['stats']['energy'] + energy_boost)
            state['stats']['health'] = min(100, state['stats']['health'] + health_boost)
            
            if state['status'] == 'critical':
                message = "Riposo riparatore! Il tuo Tamagotchi recupera le forze!"
            else:
                message = "Zzz... Il tuo Tamagotchi si sta riposando!"
            
        elif action == 'medicine':
            if state['stats']['health'] > 85:
                return False, "Il Tamagotchi è già in ottima salute!"
            
            # Boost molto maggiore se in stato critico
            health_boost = 40 if state['status'] == 'critical' else 25
            happiness_penalty = 3 if state['status'] == 'critical' else 5
            
            state['stats']['health'] = min(100, state['stats']['health'] + health_boost)
            state['stats']['happiness'] = max(0, state['stats']['happiness'] - happiness_penalty)
            state['total_care_score'] = min(100, state['total_care_score'] + 3)
            
            if state['status'] == 'critical':
                message = "Medicina d'emergenza! Il tuo Tamagotchi sta guarendo!"
            else:
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
    
    # Ottieni aree - gestisci il caso None
    areas = ha_api.get_areas()
    if areas is None:
        # Nessuna area trovata - ritorna errore
        return jsonify({
            'error': True,
            'message': '❌ NESSUNA STANZA TROVATA!',
            'details': 'Verifica che ci siano dispositivi controllabili (luci, interruttori, ventilatori, ecc.) in Home Assistant con nomi che contengano parole come "salotto", "cucina", "camera", ecc.',
            'tamagotchi': state
        }), 404
    
    # Aggiungi informazioni sulle stanze e dispositivi
    current_room = state.get('current_room', areas[0]['id'] if areas else 'unknown')
    state['rooms'] = areas
    state['current_room_devices'] = ha_api.get_area_devices(current_room)
    return jsonify(state)

@app.route('/api/rooms')
def get_rooms():
    """API per ottenere la lista delle stanze"""
    rooms = ha_api.get_areas()
    if rooms is None:
        return jsonify({
            'error': True,
            'message': '❌ NESSUNA STANZA TROVATA!',
            'details': 'Verifica che ci siano dispositivi controllabili in Home Assistant'
        }), 404
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