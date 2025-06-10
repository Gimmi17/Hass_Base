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
from flask_socketio import SocketIO, emit
import threading
import time

# Aggiungi il path per bashio
sys.path.append('/usr/lib/python3.11/site-packages')

try:
    import bashio
except ImportError:
    # Fallback per testing locale
    class MockBashio:
        @staticmethod
        def log_info(msg): print(f"INFO: {msg}")
        @staticmethod
        def log_warning(msg): print(f"WARN: {msg}")
        @staticmethod
        def log_error(msg): print(f"ERROR: {msg}")
    bashio = MockBashio()

import os
app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)) + '/templates')
app.config['SECRET_KEY'] = 'tamagotchi_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

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
    return jsonify(state)

@app.route('/api/action', methods=['POST'])
def perform_action():
    """API per eseguire azioni sul Tamagotchi"""
    action = request.json.get('action')
    success, message = tamagotchi.perform_action(action)
    
    # Emetti aggiornamento via WebSocket
    if success:
        new_state = tamagotchi.load_state()
        socketio.emit('state_update', new_state)
    
    return jsonify({
        'success': success,
        'message': message
    })

@socketio.on('connect')
def handle_connect():
    """Gestisce connessione WebSocket"""
    bashio.log_info("Client connesso via WebSocket")
    state = tamagotchi.load_state()
    emit('state_update', state)

@socketio.on('get_state')
def handle_get_state():
    """Gestisce richiesta stato via WebSocket"""
    state = tamagotchi.load_state()
    emit('state_update', state)

def background_updates():
    """Thread per aggiornamenti in background"""
    while True:
        try:
            state = tamagotchi.load_state()
            socketio.emit('state_update', state)
            time.sleep(30)  # Aggiorna ogni 30 secondi
        except Exception as e:
            bashio.log_error(f"Errore nel background update: {e}")
            time.sleep(60)

if __name__ == '__main__':
    bashio.log_info("Avvio server web Tamagotchi...")
    
    # Avvia thread per aggiornamenti in background
    update_thread = threading.Thread(target=background_updates, daemon=True)
    update_thread.start()
    
    # Avvia server
    socketio.run(app, host='0.0.0.0', port=8080, debug=False) 