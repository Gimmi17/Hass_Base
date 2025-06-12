# 🐣 Tamagotchi Home Assistant Add-on

Un **Tamagotchi virtuale integrato** che diventa il centro di controllo della tua casa intelligente! Il tuo animale virtuale non solo cresce e si evolve, ma si sposta anche tra le stanze della casa e ti aiuta a controllare tutti i dispositivi.

## ✨ Caratteristiche

- 🐣 **Sistema completo di virtual pet** - Il tuo Tamagotchi ha bisogno di cure costanti
- 📊 **Statistiche in tempo reale** - Fame, felicità, salute ed energia
- 🌱 **Sistema di evoluzione** - Da uovo a adulto in base alle tue cure
- 🏠 **Integrazione Home Assistant** - Muoviti tra le stanze e controlla i dispositivi
- 🎮 **Interfaccia moderna** - Design responsive e animazioni
- 💾 **Salvataggio automatico** - I tuoi progressi sono sempre al sicuro
- 🔄 **Sistema di resurrezione** - Il tuo Tamagotchi non muore mai permanentemente!

## ✨ Funzionalità

### 🐾 **Core Tamagotchi**
- 🥚 **Sistema di Evoluzione**: Il tuo Tamagotchi cresce attraverso diversi stadi
- 📊 **Statistiche**: Fame, Felicità, Salute ed Energia
- 🎮 **Azioni**: Nutri, Gioca, Fai dormire e Cura il tuo animale
- 💾 **Salvataggio Automatico**: I progressi vengono salvati automaticamente
- 🌟 **Avatar Dinamici**: L'aspetto cambia in base allo stadio evolutivo

### 🏠 **Integrazione Home Assistant**
- 🚪 **Movimento tra Stanze**: Il Tamagotchi si sposta nelle aree della tua casa
- 🎭 **Avatar Contextual**: Aspetto diverso per ogni stanza (divano, cucina, letto, ecc.)
- 🔌 **Controllo Dispositivi**: Accendi/spegni luci, interruttori e altri dispositivi
- 📱 **Dashboard Unificata**: Un'interfaccia unica per Tamagotchi + Casa
- 🏡 **Rilevamento Automatico**: Legge le stanze e dispositivi da Home Assistant

### ⚙️ **Configurazione**
- 🎚️ **Difficoltà**: Easy, Normal, Hard
- 📈 **Statistiche iniziali personalizzabili**
- 🔄 **Intervallo di salvataggio configurabile**

## 🎮 Come Funziona l'Integrazione

### 📍 **Stanze Virtuali**
Il Tamagotchi può muoversi tra le stanze della tua casa:
- **Salotto**: 🐤🛋️ - Seduto sul divano con telecomando
- **Cucina**: 🐤🍪 - In cucina a preparare snack
- **Camera**: 🐤🛏️ - Nel letto per riposare  
- **Bagno**: 🐤🚿 - Sotto la doccia per lavarsi
- **Garage**: 🐤🚗 - Dentro la macchina per viaggi

### 🔌 **Controllo Dispositivi**
In ogni stanza può controllare:
- 💡 **Luci** - Accendi/spegni illuminazione
- 🔌 **Interruttori** - Controlla dispositivi elettrici
- 🌀 **Ventilatori** - Gestisci ventilazione
- 🌡️ **Climatizzatori** - Regola temperatura
- 📂 **Coperture** - Apri/chiudi tende, porte garage

## 📋 Installazione

### 🏠 **Tramite Home Assistant Supervisor**

1. **Aggiungi Repository**:
   ```
   https://github.com/Gimmi17/Hass_Base
   ```

2. **Installa Add-on**:
   - Settings → Add-ons → Add-on Store
   - Cerca "Tamagotchi"
   - Installa e Avvia

3. **Configurazione**:
   ```yaml
   log_level: info
   save_interval: 60
   difficulty: normal
   starting_stats:
     hunger: 100
     happiness: 100
     health: 100
     energy: 100
   ```

### 🔑 **Permessi Richiesti**
L'add-on usa le **API interne di Home Assistant** per:
- 📋 **Leggere stati dispositivi** (sempre disponibile)
- 🏠 **Scoprire aree/stanze** (intelligente: cerca nei nomi delle entità)
- 🔌 **Controllare dispositivi** (luci, interruttori, climatizzatori, ecc.)
- 🔧 **Accesso avanzato** (opzionale: per aree ufficiali di HA)

## 🎯 Esempio d'Uso

1. **Avvia l'add-on** e vai su `http://homeassistant:8080`
2. **Il Tamagotchi inizia** nella stanza "Salotto" 
3. **Clicca su una stanza** per spostarlo (es. Cucina)
4. **L'avatar cambia** → 🐤🍼 (bebè in cucina)
5. **Appaiono i dispositivi** della cucina (luce, ventilatore)
6. **Clicca sui dispositivi** per controllarli
7. **Continua a prenderti cura** del Tamagotchi (nutri, gioca...)

## 🔧 Configurazione Avanzata

### 📊 **Opzioni**
- `log_level`: Livello di logging (trace, debug, info, warning, error)
- `save_interval`: Frequenza salvataggio in secondi (30-300)
- `difficulty`: Velocità decadimento stats (easy, normal, hard)
- `starting_stats`: Statistiche iniziali (50-100)

### 🌐 **Network**
- **Porta**: 8080 (configurabile)
- **Accesso**: Solo dalla rete locale di Home Assistant
- **API**: Comunica con `supervisor/core/api`

## 🐛 Troubleshooting

### ❌ **Dispositivi non appaiono**
- Verifica che i dispositivi siano in aree assegnate
- Controlla i permessi dell'add-on
- Solo domini supportati: `light`, `switch`, `fan`, `climate`, `cover`

### 🔌 **Controllo non funziona**
- Verifica connessione al supervisor
- Controlla i log dell'add-on
- Assicurati che i dispositivi siano controllabili

### 🏠 **Stanze mancanti**
- Crea aree in Home Assistant: Settings → Areas & Devices
- Assegna dispositivi alle aree
- Riavvia l'add-on

## 🎨 Personalizzazione

### 🎭 **Avatar per Stanza**
Gli avatar si adattano automaticamente al contesto:
```
living_room: 🐤🛋️  kitchen: 🐤🍪  bedroom: 🐤🛏️
bathroom: 🐤🚿    garage: 🐤🚗   office: 🐤💻
```

### 🏠 **Nuove Stanze**
Aggiungi nuove aree in Home Assistant e appariranno automaticamente!

## 📝 Changelog

### v1.1.0 - Home Assistant Integration
- ✅ Integrazione completa con Home Assistant API
- ✅ Movimento tra stanze con avatar contextual
- ✅ Controllo dispositivi (luci, interruttori, ventilatori)
- ✅ Dashboard unificata Tamagotchi + Casa
- ✅ Rilevamento automatico aree e dispositivi

### v1.0.6 - Stable Release  
- ✅ Sistema di evoluzione completo
- ✅ Interfaccia web moderna con polling
- ✅ Salvataggio persistente dei dati

## 🤝 Contributi

Contributi benvenuti! Apri issue o pull request su [GitHub](https://github.com/Gimmi17/Hass_Base).

## 📄 Licenza

MIT License - Vedi [LICENSE](LICENSE) per dettagli.

---

**🎉 Divertiti con il tuo Tamagotchi maggiordomo virtuale!** 