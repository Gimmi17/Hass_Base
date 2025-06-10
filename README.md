# Home Assistant Add-ons

Questo repository contiene add-on personalizzati per Home Assistant.

## Add-on Disponibili

### 🐣 Tamagotchi

Un Tamagotchi virtuale interattivo per Home Assistant! Prenditi cura del tuo animale domestico digitale direttamente dal tuo dashboard.

**Caratteristiche:**
- Sistema di evoluzione completo (da uovo ad adulto)
- Interfaccia web moderna e responsive
- Statistiche in tempo reale (fame, felicità, salute, energia)
- Interazioni complete (nutri, gioca, dormi, medicina)
- Persistenza automatica dei dati
- Aggiornamenti live via WebSocket

[📖 Leggi la documentazione completa](tamagotchi/DOCS.md)

### 📝 Esempio

Add-on di esempio basato sul template della community Home Assistant.

[📖 Leggi la documentazione](example/DOCS.md)

## Installazione

1. Aggiungi questo repository agli add-on di Home Assistant:
   - Vai su **Supervisor** → **Add-on Store**
   - Clicca sui tre puntini in alto a destra
   - Seleziona **Repositories**
   - Aggiungi l'URL di questo repository

2. Cerca e installa l'add-on desiderato

3. Configura le opzioni se necessario

4. Avvia l'add-on

## Sviluppo

Questo repository è basato sul template degli add-on della community Home Assistant. Ogni add-on include:

- `config.yaml`: Configurazione dell'add-on
- `build.yaml`: Configurazione di build
- `Dockerfile`: Istruzioni per il container
- `rootfs/`: File system root del container
- `DOCS.md`: Documentazione dettagliata

## Contributi

I contributi sono benvenuti! Per favore:

1. Fork del repository
2. Crea un branch per la tua feature
3. Commit delle modifiche
4. Push del branch
5. Apri una Pull Request

## Licenza

MIT License - vedi [LICENSE.md](LICENSE.md) per i dettagli.

## Supporto

Per problemi o domande:
1. Controlla la documentazione dell'add-on specifico
2. Apri una issue in questo repository
3. Fornisci log e configurazione se necessario

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-no-red.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/hassio-addons/addon-example.svg
[commits]: https://github.com/hassio-addons/addon-example/commits/main
[contributors]: https://github.com/hassio-addons/addon-example/graphs/contributors
[discord-ha]: https://discord.gg/c5DvZ4e
[discord-shield]: https://img.shields.io/discord/478094546522079232.svg
[discord]: https://discord.me/hassioaddons
[docs]: https://github.com/hassio-addons/addon-example/blob/main/example/DOCS.md
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg
[forum]: https://community.home-assistant.io/t/repository-community-hass-io-add-ons/24705?u=frenck
[frenck]: https://github.com/frenck
[github-actions-shield]: https://github.com/hassio-addons/addon-example/workflows/CI/badge.svg
[github-actions]: https://github.com/hassio-addons/addon-example/actions
[github-sponsors-shield]: https://frenck.dev/wp-content/uploads/2019/12/github_sponsor.png
[github-sponsors]: https://github.com/sponsors/frenck
[i386-shield]: https://img.shields.io/badge/i386-no-red.svg
[issue]: https://github.com/hassio-addons/addon-example/issues
[license-shield]: https://img.shields.io/github/license/hassio-addons/addon-example.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[patreon-shield]: https://frenck.dev/wp-content/uploads/2019/12/patreon.png
[patreon]: https://www.patreon.com/frenck
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[reddit]: https://reddit.com/r/homeassistant
[releases-shield]: https://img.shields.io/github/release/hassio-addons/addon-example.svg
[releases]: https://github.com/hassio-addons/addon-example/releases
[repository]: https://github.com/hassio-addons/repository
