#!/usr/bin/env python3
"""
Tamagotchi Game Engine
Gestisce la logica principale del gioco Tamagotchi
"""

import json
import time
import random
import os
import sys
from typing import Dict, Any
from datetime import datetime, timedelta

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
        @staticmethod
        def config(key): 
            defaults = {
                'save_interval': 60,
                'difficulty': 'normal',
                'starting_stats': {
                    'hunger': 100,
                    'happiness': 100,
                    'health': 100,
                    'energy': 100
                }
            }
            return defaults.get(key, None)
    bashio = MockBashio()

class TamagotchiEngine:
    def __init__(self):
        self.data_dir = '/data'
        self.save_file = os.path.join(self.data_dir, 'tamagotchi.json')
        self.state = self.load_state()
        self.last_update = datetime.now()
        
        # Configurazione
        self.save_interval = bashio.config('save_interval')
        self.difficulty = bashio.config('difficulty')
        
        # Rate di decremento basati sulla difficoltà
        self.decay_rates = {
            'easy': {'hunger': 0.5, 'happiness': 0.3, 'energy': 0.4},
            'normal': {'hunger': 1.0, 'happiness': 0.5, 'energy': 0.7},
            'hard': {'hunger': 1.5, 'happiness': 0.8, 'energy': 1.0}
        }
        
    def load_state(self) -> Dict[str, Any]:
        """Carica lo stato del Tamagotchi da file"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    state = json.load(f)
                bashio.log_info("Stato Tamagotchi caricato")
                return state
            except Exception as e:
                bashio.log_error(f"Errore nel caricamento stato: {e}")
        
        # Stato iniziale
        starting_stats = bashio.config('starting_stats')
        state = {
            'name': 'Tama',
            'birth_date': datetime.now().isoformat(),
            'last_update': datetime.now().isoformat(),
            'stats': {
                'hunger': starting_stats['hunger'],
                'happiness': starting_stats['happiness'],
                'health': starting_stats['health'],
                'energy': starting_stats['energy'],
                'age_days': 0
            },
            'status': 'happy',
            'activities': {
                'last_fed': None,
                'last_played': None,
                'last_sleep': None,
                'last_medicine': None
            },
            'evolution_stage': 'egg',
            'total_care_score': 100
        }
        
        bashio.log_info("Nuovo Tamagotchi creato!")
        return state
    
    def save_state(self):
        """Salva lo stato del Tamagotchi"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.save_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            bashio.log_error(f"Errore nel salvataggio: {e}")
    
    def update_stats(self):
        """Aggiorna le statistiche del Tamagotchi"""
        now = datetime.now()
        last_update = datetime.fromisoformat(self.state['last_update'])
        time_diff = (now - last_update).total_seconds() / 60  # minuti
        
        if time_diff < 1:  # Aggiorna solo se è passato almeno 1 minuto
            return
        
        # Calcola l'età in giorni
        birth_date = datetime.fromisoformat(self.state['birth_date'])
        age_days = (now - birth_date).days
        self.state['stats']['age_days'] = age_days
        
        # Applica il decadimento
        rates = self.decay_rates[self.difficulty]
        
        # Fame aumenta (il valore diminuisce = più fame)
        self.state['stats']['hunger'] = max(0, 
            self.state['stats']['hunger'] - (rates['hunger'] * time_diff))
        
        # Felicità diminuisce
        self.state['stats']['happiness'] = max(0,
            self.state['stats']['happiness'] - (rates['happiness'] * time_diff))
        
        # Energia diminuisce
        self.state['stats']['energy'] = max(0,
            self.state['stats']['energy'] - (rates['energy'] * time_diff))
        
        # Salute dipende dalle altre stats
        avg_stats = (self.state['stats']['hunger'] + 
                    self.state['stats']['happiness'] + 
                    self.state['stats']['energy']) / 3
        
        if avg_stats < 20:
            # Stato molto critico - salute scende
            self.state['stats']['health'] = max(1, 
                self.state['stats']['health'] - (time_diff * 0.5))
        elif avg_stats < 40:
            # Stato di recupero lento - salute sale molto lentamente
            self.state['stats']['health'] = min(100,
                self.state['stats']['health'] + (time_diff * 0.1))
        elif avg_stats > 60:
            # Stato buono - salute sale normalmente
            self.state['stats']['health'] = min(100,
                self.state['stats']['health'] + (time_diff * 0.3))
        # Se avg_stats è tra 40-60, salute rimane stabile
        
        # Aggiorna lo stato
        self.update_status()
        self.update_evolution()
        
        self.state['last_update'] = now.isoformat()
    
    def update_status(self):
        """Aggiorna lo stato del Tamagotchi basato sulle statistiche"""
        stats = self.state['stats']
        
        # Logica di stato migliorata per recupero graduale
        if stats['health'] <= 1:
            self.state['status'] = 'critical'
        elif stats['health'] <= 15:
            self.state['status'] = 'critical'  # Ancora critico ma può migliorare
        elif any(stat < 20 for stat in [stats['hunger'], stats['happiness'], stats['energy']]):
            self.state['status'] = 'critical'
        elif stats['health'] <= 30 or any(stat < 40 for stat in [stats['hunger'], stats['happiness'], stats['energy']]):
            self.state['status'] = 'sad'
        elif stats['energy'] < 30:
            self.state['status'] = 'sleepy'
        elif stats['hunger'] < 30:
            self.state['status'] = 'hungry'
        elif all(stat > 70 for stat in [stats['hunger'], stats['happiness'], stats['energy'], stats['health']]):
            self.state['status'] = 'very_happy'
        else:
            self.state['status'] = 'happy'
    
    def update_evolution(self):
        """Gestisce l'evoluzione del Tamagotchi"""
        age_days = self.state['stats']['age_days']
        care_score = self.state['total_care_score']
        
        if self.state['evolution_stage'] == 'egg' and age_days >= 1:
            self.state['evolution_stage'] = 'baby'
            bashio.log_info("🥚 Il tuo Tamagotchi è nato!")
        elif self.state['evolution_stage'] == 'baby' and age_days >= 3:
            if care_score > 80:
                self.state['evolution_stage'] = 'teen_good'
            else:
                self.state['evolution_stage'] = 'teen_bad'
            bashio.log_info(f"🌱 Il tuo Tamagotchi è cresciuto! Stadio: {self.state['evolution_stage']}")
        elif self.state['evolution_stage'].startswith('teen') and age_days >= 7:
            if care_score > 90:
                self.state['evolution_stage'] = 'adult_excellent'
            elif care_score > 70:
                self.state['evolution_stage'] = 'adult_good'
            else:
                self.state['evolution_stage'] = 'adult_average'
            bashio.log_info(f"🦋 Il tuo Tamagotchi è diventato adulto! Stadio: {self.state['evolution_stage']}")
    
    def feed(self):
        """Nutri il Tamagotchi"""
        if self.state['status'] == 'dead':
            return False, "Il Tamagotchi è morto..."
        
        # Boost maggiore se in stato critico
        hunger_boost = 30 if self.state['status'] == 'critical' else 20
        happiness_boost = 10 if self.state['status'] == 'critical' else 5
        
        self.state['stats']['hunger'] = min(100, self.state['stats']['hunger'] + hunger_boost)
        self.state['stats']['happiness'] = min(100, self.state['stats']['happiness'] + happiness_boost)
        self.state['activities']['last_fed'] = datetime.now().isoformat()
        self.state['total_care_score'] = min(100, self.state['total_care_score'] + 1)
        
        # Aggiorna subito lo stato dopo l'azione
        self.update_status()
        
        bashio.log_info("Tamagotchi nutrito!")
        return True, "Yum! Il tuo Tamagotchi è stato nutrito!"
    
    def play(self):
        """Gioca con il Tamagotchi"""
        if self.state['status'] == 'dead':
            return False, "Il Tamagotchi è morto..."
        
        if self.state['stats']['energy'] < 15:
            return False, "Il Tamagotchi è troppo stanco per giocare!"
        
        # Boost maggiore se in stato critico
        happiness_boost = 25 if self.state['status'] == 'critical' else 15
        energy_cost = 5 if self.state['status'] == 'critical' else 10
        
        self.state['stats']['happiness'] = min(100, self.state['stats']['happiness'] + happiness_boost)
        self.state['stats']['energy'] = max(0, self.state['stats']['energy'] - energy_cost)
        self.state['activities']['last_played'] = datetime.now().isoformat()
        self.state['total_care_score'] = min(100, self.state['total_care_score'] + 2)
        
        # Aggiorna subito lo stato dopo l'azione
        self.update_status()
        
        bashio.log_info("Hai giocato con il Tamagotchi!")
        return True, "Che divertimento! Il tuo Tamagotchi è felice!"
    
    def sleep(self):
        """Fai dormire il Tamagotchi"""
        if self.state['status'] == 'dead':
            return False, "Il Tamagotchi è morto..."
        
        # Boost maggiore se in stato critico
        energy_boost = 40 if self.state['status'] == 'critical' else 30
        health_boost = 10 if self.state['status'] == 'critical' else 5
        
        self.state['stats']['energy'] = min(100, self.state['stats']['energy'] + energy_boost)
        self.state['stats']['health'] = min(100, self.state['stats']['health'] + health_boost)
        self.state['activities']['last_sleep'] = datetime.now().isoformat()
        
        # Aggiorna subito lo stato dopo l'azione
        self.update_status()
        
        bashio.log_info("Il Tamagotchi sta dormendo...")
        return True, "Zzz... Il tuo Tamagotchi si sta riposando!"
    
    def medicine(self):
        """Dai una medicina al Tamagotchi"""
        if self.state['status'] == 'dead':
            return False, "Il Tamagotchi è morto..."
        
        if self.state['stats']['health'] > 85:
            return False, "Il Tamagotchi è già in ottima salute!"
        
        # Boost molto maggiore se in stato critico
        health_boost = 40 if self.state['status'] == 'critical' else 25
        happiness_penalty = 3 if self.state['status'] == 'critical' else 5  # Meno penalità se critico
        
        self.state['stats']['health'] = min(100, self.state['stats']['health'] + health_boost)
        self.state['stats']['happiness'] = max(0, self.state['stats']['happiness'] - happiness_penalty)
        self.state['activities']['last_medicine'] = datetime.now().isoformat()
        self.state['total_care_score'] = min(100, self.state['total_care_score'] + 3)
        
        # Aggiorna subito lo stato dopo l'azione
        self.update_status()
        
        bashio.log_info("Medicina data al Tamagotchi!")
        return True, "Il tuo Tamagotchi si sente meglio!"
    
    def get_state(self):
        """Ritorna lo stato completo del Tamagotchi"""
        return self.state.copy()
    
    def run(self):
        """Loop principale del motore"""
        bashio.log_info("Motore Tamagotchi avviato!")
        
        while True:
            try:
                self.update_stats()
                
                # Salva ogni save_interval secondi
                if int(time.time()) % self.save_interval == 0:
                    self.save_state()
                
                # Log stato ogni 5 minuti
                if int(time.time()) % 300 == 0:
                    stats = self.state['stats']
                    bashio.log_info(
                        f"Stato Tamagotchi - "
                        f"Fame: {stats['hunger']:.1f}, "
                        f"Felicità: {stats['happiness']:.1f}, "
                        f"Energia: {stats['energy']:.1f}, "
                        f"Salute: {stats['health']:.1f}, "
                        f"Stato: {self.state['status']}"
                    )
                
                time.sleep(10)  # Aggiorna ogni 10 secondi
                
            except KeyboardInterrupt:
                bashio.log_info("Motore Tamagotchi arrestato")
                self.save_state()
                break
            except Exception as e:
                bashio.log_error(f"Errore nel motore: {e}")
                time.sleep(30)

if __name__ == "__main__":
    engine = TamagotchiEngine()
    engine.run() 