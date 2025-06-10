# Home Assistant Add-on: Tamagotchi

Un Tamagotchi virtuale interattivo per Home Assistant! Prenditi cura del tuo animale domestico digitale direttamente dal tuo dashboard.

## Caratteristiche

🥚 **Sistema di Evoluzione**: Il tuo Tamagotchi evolve da uovo a adulto basandosi sulle tue cure
📊 **Statistiche in Tempo Reale**: Monitora fame, felicità, salute ed energia
🎮 **Interazione Completa**: Nutri, gioca, fai dormire e cura il tuo Tamagotchi
🌐 **Interfaccia Web Moderna**: Design responsive e accattivante
💾 **Persistenza Dati**: Lo stato del Tamagotchi viene salvato automaticamente
🔄 **Aggiornamenti Live**: WebSocket per aggiornamenti in tempo reale

## Installazione

1. Aggiungi questo repository agli add-on di Home Assistant
2. Installa l'add-on "Tamagotchi"
3. Configura le opzioni se desiderato
4. Avvia l'add-on
5. Apri l'interfaccia web cliccando su "APRI INTERFACCIA WEB"

## Configurazione

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

### Opzione: `log_level`

Controlla il livello di log dell'add-on:

- `trace`: Mostra ogni dettaglio, utile per debug
- `debug`: Informazioni dettagliate di debug
- `info`: Eventi normalmente interessanti (predefinito)
- `warning`: Occorrenze eccezionali che non sono errori
- `error`: Errori runtime che non richiedono azione immediata
- `fatal`: Qualcosa è andato terribilmente storto

### Opzione: `save_interval`

Intervallo in secondi per il salvataggio automatico dello stato (30-300 secondi).

### Opzione: `difficulty`

Controlla quanto velocemente le statistiche del Tamagotchi decadono:

- `easy`: Decadimento lento, ideale per principianti
- `normal`: Decadimento bilanciato (predefinito)
- `hard`: Decadimento veloce, per una sfida maggiore

### Opzione: `starting_stats`

Statistiche iniziali del Tamagotchi (50-100 per ogni statistica).

## Come Giocare

### Statistiche

- **🍽️ Fame**: Diminuisce nel tempo, nutri il Tamagotchi per aumentarla
- **😊 Felicità**: Diminuisce nel tempo, gioca per aumentarla
- **❤️ Salute**: Dipende dalle altre statistiche, usa medicine se bassa
- **⚡ Energia**: Diminuisce nel tempo e con il gioco, fai dormire per recuperarla

### Azioni

- **🍎 Nutri**: Aumenta fame (+20) e felicità (+5)
- **🎮 Gioca**: Aumenta felicità (+15) ma diminuisce energia (-10)
- **💤 Dormi**: Aumenta energia (+30) e salute (+5)
- **💊 Medicina**: Aumenta salute (+25) ma diminuisce felicità (-5)

### Evoluzione

Il tuo Tamagotchi evolverà attraverso diverse fasi:

1. **🥚 Uovo** (0 giorni) → **🐣 Piccolo** (1 giorno)
2. **🐣 Piccolo** (1-2 giorni) → **🐤/🐦 Adolescente** (3 giorni)
3. **🐤/🐦 Adolescente** (3-6 giorni) → **🦅/🐧/🦆 Adulto** (7+ giorni)

L'evoluzione dipende dal punteggio di cura: più ti prendi cura del Tamagotchi, migliore sarà la sua evoluzione!

### Stati

- **Felice**: Tutto va bene! 😊
- **Molto Felice**: Tutte le statistiche sono ottime! 🌈
- **Affamato**: Ha bisogno di cibo 🍎
- **Assonnato**: Ha bisogno di riposare 💤
- **Triste**: Alcune statistiche sono basse 😢
- **Critico**: Statistiche molto basse! ⚠️
- **Morto**: Non è stato curato abbastanza... 💀

## Integrazione con Home Assistant

L'add-on espone un'interfaccia web accessibile tramite il dashboard di Home Assistant. Puoi anche creare:

- **Automazioni** basate sui file di stato in `/addon_configs/[addon_slug]/tamagotchi.json`
- **Notifiche** quando il Tamagotchi ha bisogno di cure
- **Sensori personalizzati** per monitorare le statistiche

## Risoluzione Problemi

### Il Tamagotchi non risponde

1. Controlla i log dell'add-on
2. Riavvia l'add-on
3. Verifica che il servizio web sia attivo sulla porta 8080

### Perdita dati

I dati vengono salvati in `/addon_configs/[addon_slug]/tamagotchi.json`. In caso di problemi:

1. Verifica che il file esista
2. Controlla i permessi della directory `/data`
3. Aumenta la frequenza di salvataggio riducendo `save_interval`

### Performance

Per dispositivi con risorse limitate:

1. Aumenta `save_interval` per ridurre le scritture su disco
2. Imposta `log_level` su `warning` o `error`
3. Usa difficoltà `easy` per ridurre i calcoli

## Supporto

Per problemi, suggerimenti o contributi:

1. Controlla i log dell'add-on per errori
2. Apri una issue nel repository GitHub
3. Condividi la configurazione e i log se necessario

## Divertiti!

Il tuo Tamagotchi virtuale ti aspetta! Ricorda di prenderti cura di lui regolarmente per vederlo crescere felice e sano. 🐣💕 