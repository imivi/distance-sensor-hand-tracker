---
marp: true
theme: default
paginate: true
size: 16:10
style: |
  section {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 20px;
    padding: 36px 64px;
    background: #f8fafc;
    color: #0f172a;
    box-sizing: border-box;
  }
  h1 {
    color: #0369a1;
    font-size: 36px;
    margin-bottom: 8px;
  }
  h2 {
    color: #0284c7;
    font-size: 26px;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 6px;
    margin-bottom: 16px;
  }
  h3 {
    color: #1e293b;
    font-size: 20px;
    margin-bottom: 10px;
  }
  ul {
    margin-top: 4px;
    margin-bottom: 12px;
    padding-left: 22px;
  }
  li {
    margin-bottom: 8px;
    line-height: 1.35;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 36px;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
  }
  .grid-video {
    display: grid;
    grid-template-columns: 0.8fr 1.2fr;
    gap: 28px;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
  }
  .highlight-box {
    background: #e0f2fe;
    border-left: 5px solid #0284c7;
    padding: 10px 14px;
    border-radius: 4px;
    margin: 12px 0;
  }
  .svg-card {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
  }
  .svg-card img, .svg-card video {
    max-width: 100%;
    max-height: 440px;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }
  section.hero {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 36px 64px;
  }
  section.hero h1 {
    font-size: 42px;
    margin-bottom: 6px;
    letter-spacing: -0.02em;
  }
  section.hero h3 {
    font-size: 22px;
    color: #475569;
    font-weight: 500;
    margin-bottom: 18px;
  }
  section.hero .hero-tag {
    display: inline-block;
    background: #e2e8f0;
    color: #334155;
    font-size: 14px;
    font-weight: 600;
    padding: 6px 18px;
    border-radius: 9999px;
    margin-top: 10px;
    letter-spacing: 0.02em;
  }
  .github-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #0284c7;
    text-decoration: none;
    font-family: monospace;
    font-size: 13px;
    font-weight: 600;
    margin-top: 10px;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    padding: 5px 14px;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }
  .github-link:hover {
    color: #0369a1;
    border-color: #0284c7;
  }
  section.closing {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 28px 64px;
  }
  section.closing h1 {
    font-size: 40px;
    margin-bottom: 4px;
    letter-spacing: -0.02em;
  }
  section.closing h3 {
    font-size: 20px;
    color: #475569;
    font-weight: 500;
    margin-bottom: 14px;
  }
---

<!-- _class: hero -->
<!-- _paginate: false -->

# Riconoscimento lettere in 2D con sensori di distanza

<div style="display: flex; justify-content: center; width: 100%; margin: 6px 0;">
  <img src="assets/slide_hero.svg" width="700" style="border-radius: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.08);"/>
</div>

<a class="github-link" href="https://github.com/imivi/distance-sensor-hand-tracker" target="_blank">github.com/imivi/distance-sensor-hand-tracker</a>

---

## Dimostrazione del Sistema

<div class="grid-video">
<div>

### Caratteristiche

* **Tracciamento in tempo reale:** disegno di lettere a mezz'aria nella cornice
* **Classificazione della lettera:** riconoscimento della lettera e classificazione con un click
* **Registrazione e allenamento in tempo reale:** i nuovi gesti vengono registrati e il modello viene riaddestrato in tempo reale
* **Nessun dispositivo indossabile:** senza telecamere né guanti

</div>
<div class="svg-card">

<video src="assets/video.mp4" controls loop width="560"></video>

</div>
</div>

---

## Interfaccia web

<div class="grid-video">
<div>

### Funzionalità dell'Applicazione

* **Visualizzazione gesto:** tracking continuo della mano con scia del movimento
* **Stima del gesto:** l'interfaccia riporta la lettera stimata con percentuale di affidabilità
* **Registrazione gesti con un click** e salvataggio automatico su CSV
* **Riallenamento modello con un click** sui dati raccolti

</div>
<div class="svg-card">

<img src="assets/screenshot.png" width="580" style="max-height: 460px;" alt="Screenshot Interfaccia Web"/>

</div>
</div>

---

## Sensori e classificazione

<div class="grid-2">
<div>

### Riconoscimento dei gesti

* Il sistema risolve un problema di **classificazione supervisionata** (17 classi): mappare una sequenza continua di movimenti (coordinate) in una categoria discreta.

### Input e Output del Modello

* **Input dei sensori:** Serie temporale di coordinate $(X, Y)$ rilevate durante il movimento della mano
* **Input al modello di ML:** Vettore di feature numeriche a 39 dimensioni estratto al termine del gesto
* **Output:** etichetta discreta della classe (tra 17 lettere dell'alfabeto) con la relativa distribuzione di confidenza

</div>
<div class="svg-card">

<img src="assets/slide_coordinates_to_grid.svg" width="390"/>

</div>
</div>

---

## Configurazioni hardware: 3 tipi testati

<div class="grid-2">
<div>

### Configurazioni testate

**<span style="color: #dc2626;">1. Quattro Sensori in Parallelo:</span>**
* Disposti sulla stessa linea: misuravano solo la profondità 1D con forti interferenze acustiche tra loro. Bassa risoluzione sull'asse X

**<span style="color: #d97706;">2. Due Sensori Perpendicolari (X, Y):</span>**
* Disposizione ad "L": mappava il piano, ma l'altezza della mano ($Z$) falsava le coordinate $(X, Y)$.

**<span style="color: #16a34a;">3. Quattro sensori opposti (2 per asse, scelta finale):</span>**
* Cornice chiusa $49 \times 51\text{ cm}$: confrontando i sensori opposti, la profondità del gesto viene compensata

</div>
<div class="svg-card" style="display: flex; flex-direction: column; gap: 14px;">
<img src="assets/slide_triangulation.svg" width="370"/>

</div>
</div>

---

## Firmware Arduino: ottimizzazioni

<div class="grid-2">
<div>

### 1. Interferenza Acustica (Crosstalk)
* Se i 4 sensori vengono usati contemporaneamente, l'eco di uno viene captato per sbaglio da un altro.
* **La soluzione:** lettura in sequenza (S1 $\to$ S2 $\to$ S3 $\to$ S4) con pausa di **18 ms** tra i pings per far decadere i rimbalzi.

### 2. Gestione dei Timeout
* Di default, se un'onda non torna indietro Arduino si blocca in attesa fino a **1 secondo**
* **La soluzione:** timeout ridotto a 8 ms (~137 cm max). Se l'eco non torna, scarta il dato e continua subito senza bloccare lo streaming (~18-20 Hz).

</div>
<div style="display: flex; flex-direction: column; gap: 16px; align-items: center; justify-content: center;">

<img src="assets/arduino-nano.jpg" width="280" alt="Arduino Nano" style="box-shadow: none; border-radius: 8px;"/>
<img src="assets/hc-sr04.jpg" width="280" alt="HC-SR04 Ultrasonic Sensor" style="box-shadow: none; border-radius: 8px;"/>

</div>
</div>

---

## Raccolta dati & pulizia del segnale

<div class="grid-2">
<div>

### Filtri sul flusso seriale
* **Filtro mediana mobile:** Legge gli ultimi 5 valori letti e prende la mediana per attenuare il jitter continuo
* **Scarto dei valori anomali:** Scarta variazioni brusche anomale nel singolo frame ("salti")
* **Recupero Dinamico:** Riconosce i cambi di traiettoria intenzionali e rapidi

### Creazione del dataset
* Acquisizione interattiva tramite interfaccia web
* **191 registrazioni complessive** su 17 lettere
* Campioni acquisiti da diversi utenti a varie velocità (quindi vari numeri di punti per lettera)

</div>
<div class="svg-card">

<img src="assets/slide_filtering.svg" width="350"/>

</div>
</div>

---

## Elaborazione dati

<div class="grid-2">
<div>

### Conversione da coordinate a griglia di punti
1. **Normalizzazione & Centratura:**
   * Scaling uniforme basato sul lato maggiore
   * La lettera mantiene le sue proporzioni originali
2. **Griglia di Occupanza $6 \times 6$ (36 celle)**
   * Matrice binaria delle celle attraversate
   * **Interpolazione lineare** tra punti: nessun buco
   * Completa invarianza da senso orario o antiorario
3. **Metriche Globali (3 valori)**
   * Rapporto di forma, larghezza e altezza in centimetri

</div>
<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; justify-items: center; align-items: center;">

<img src="assets/gesture_samples/L_2f4f54e7.png" width="180" style="border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: none;" alt="Lettera L"/>
<img src="assets/gesture_samples/O_10f171cc.png" width="180" style="border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: none;" alt="Lettera O"/>
<img src="assets/gesture_samples/S_145c3c2d.png" width="180" style="border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: none;" alt="Lettera S"/>
<img src="assets/gesture_samples/Z_1421e90c.png" width="180" style="border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: none;" alt="Lettera Z"/>

</div>
</div>

---

## Machine Learning in Python (Random Forest) e feature engineering

### Dataset & Training Matrix (192 campioni &times; 39 feature)

<table style="width: 100%; border-collapse: collapse; font-size: 13.5px; margin: 8px 0 12px 0; background: #ffffff; border-radius: 6px; overflow: hidden; border: 1px solid #cbd5e1;">
  <thead>
    <tr style="background: #e2e8f0; color: #1e293b;">
      <th style="padding: 6px 10px; text-align: left;">ID</th>
      <th style="padding: 6px 10px; text-align: center;">Target</th>
      <th style="padding: 6px 10px; text-align: center;">Grid[0,0]</th>
      <th style="padding: 6px 10px; text-align: center;">Grid[0,1]</th>
      <th style="padding: 6px 10px; text-align: center;">...</th>
      <th style="padding: 6px 10px; text-align: center;">Aspect</th>
      <th style="padding: 6px 10px; text-align: center;">Width</th>
      <th style="padding: 6px 10px; text-align: center;">Height</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-top: 1px solid #e2e8f0;">
      <td style="padding: 5px 10px; font-family: monospace;">2f4f54e7</td>
      <td style="padding: 5px 10px; text-align: center; font-weight: bold; color: #0284c7;">L</td>
      <td style="padding: 5px 10px; text-align: center;">0.0</td>
      <td style="padding: 5px 10px; text-align: center;">0.0</td>
      <td style="padding: 5px 10px; text-align: center;">...</td>
      <td style="padding: 5px 10px; text-align: center;">1.46</td>
      <td style="padding: 5px 10px; text-align: center;">9.3 cm</td>
      <td style="padding: 5px 10px; text-align: center;">13.6 cm</td>
    </tr>
    <tr style="border-top: 1px solid #e2e8f0; background: #f8fafc;">
      <td style="padding: 5px 10px; font-family: monospace;">4a081398</td>
      <td style="padding: 5px 10px; text-align: center; font-weight: bold; color: #0284c7;">O</td>
      <td style="padding: 5px 10px; text-align: center;">0.0</td>
      <td style="padding: 5px 10px; text-align: center;">1.0</td>
      <td style="padding: 5px 10px; text-align: center;">...</td>
      <td style="padding: 5px 10px; text-align: center;">1.06</td>
      <td style="padding: 5px 10px; text-align: center;">15.0 cm</td>
      <td style="padding: 5px 10px; text-align: center;">15.9 cm</td>
    </tr>
    <tr style="border-top: 1px solid #e2e8f0;">
      <td style="padding: 5px 10px; font-family: monospace;">1421e90c</td>
      <td style="padding: 5px 10px; text-align: center; font-weight: bold; color: #0284c7;">Z</td>
      <td style="padding: 5px 10px; text-align: center;">1.0</td>
      <td style="padding: 5px 10px; text-align: center;">1.0</td>
      <td style="padding: 5px 10px; text-align: center;">...</td>
      <td style="padding: 5px 10px; text-align: center;">0.93</td>
      <td style="padding: 5px 10px; text-align: center;">11.3 cm</td>
      <td style="padding: 5px 10px; text-align: center;">10.5 cm</td>
    </tr>
  </tbody>
</table>

<div style="display: flex; justify-content: space-between; font-size: 15px; color: #334155; margin-bottom: 10px;">
  <span>&bull; <strong>17 classi</strong> distinte di lettere</span>
  <span>&bull; <strong>39 feature numeriche:</strong> 36 griglia binaria 6&times;6 + 3 variabili (forma della lettera)</span>
  <span>&bull; <strong>Modello:</strong> Random Forest (100 alberi)</span>
</div>

<div style="display: flex; justify-content: center; width: 100%;">
  <img src="assets/tree_visualization.svg" style="width: 100%; max-height: 220px; object-fit: contain; border-radius: 8px; box-shadow: none;" alt="Visualizzazione Decision Tree"/>
</div>

---

## Risultati Sperimentali & Analisi degli Errori

<div class="grid-2">
<div>

### Metriche Globali
* **Accuratezza Totale:** **91.1%**
* **Precision Macro:** **91.3%**
* **Recall Macro:** **90.9%**

### Lettere con Prestazioni Massime
* **P, G (100%):** tratti chiusi inconfondibili
* **I, S, A (>95%):** forma molto identificabile

### Ambiguità Rilevate
* **D vs J:** parte superiore aperta nei tratti veloci
* **M vs N:** bassa risoluzione della griglia 6x6 sul picco centrale (meglio 8x8)

</div>
<div class="svg-card">

<img src="assets/slide_metrics.svg" width="340"/>

</div>
</div>

---

## Architettura software frontend + backend

<div class="grid-2">
<div>

### Backend in Python (FastAPI e websocket)

* **Lettura seriale non bloccante:** task asincrono di background dedicato alla lettura dello stream USB (~18–20 Hz)
* **WebSockets full-duplex:** invio dati in tempo reale di coordinate $(X, Y)$ grezze e filtrate ai client connessi
* **Inferenza & Retrain Asincrono:** esecuzione del modello Random Forest in thread pool (run_in_executor) per non bloccare l'event loop
* **Persistenza Dati:** salvataggio dati registrazioni su CSV

</div>
<div class="svg-card">

<img src="assets/slide_architecture.svg" width="370" alt="Architettura Software"/>

</div>
</div>

---

## Conclusioni

<div class="grid-2">
<div>

### Risultati Ottenuti
* Interazione touchless affidabile senza dispositivi ottici
* Sistema facile da usare e a bassa latenza

### Limiti Fisici
* Frequenza vincolata dalla velocità del suono in aria
* Sensibilità al materiale usato per il tracciamento (mano, bottiglia, etc)
* Sensibilità all'inclinazione del palmo

</div>
<div class="svg-card">

<img src="assets/slide_perspective_frame.svg" width="370" alt="Struttura della cornice e sensori in prospettiva" style="box-shadow: none;"/>

</div>
</div>

---

<!-- _class: closing -->
<!-- _paginate: false -->

# Grazie per l'Attenzione!
### 2D Ultrasonic Hand Tracker & Classifier

<a class="github-link" href="https://github.com/imivi/distance-sensor-hand-tracker" target="_blank" style="margin-top: 18px;">github.com/imivi/distance-sensor-hand-tracker</a>