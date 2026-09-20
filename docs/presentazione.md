---
marp: true
theme: default
paginate: true
size: 16:10
transition: slide
style: |
  section {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 20px;
    padding: 36px 64px;
    background: #f8fafc;
    color: #0f172a;
    box-sizing: border-box;
  }
  section.compact-slide {
    padding: 24px 50px;
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

<ul>
  <li><strong>Tracciamento in tempo reale:</strong> disegno di lettere a mezz'aria nella cornice</li>
  <li><strong>Classificazione della lettera:</strong> riconoscimento della lettera e classificazione con un click</li>
  <li><strong>Registrazione e allenamento in tempo reale:</strong> i nuovi gesti vengono registrati e il modello viene riaddestrato in tempo reale</li>
  <li><strong>Nessun dispositivo indossabile:</strong> senza telecamere né guanti</li>
</ul>

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

<ul>
  <li><strong>Visualizzazione gesto:</strong> tracking continuo della mano con scia del movimento</li>
  <li><strong>Stima del gesto:</strong> l'interfaccia riporta la lettera stimata con percentuale di affidabilità</li>
  <li><strong>Registrazione gesti con un click</strong> e salvataggio automatico su CSV</li>
  <li><strong>Riallenamento modello con un click</strong> sui dati raccolti</li>
</ul>

</div>
<div class="svg-card">

<img src="assets/screenshot.png" width="580" style="max-height: 460px;" alt="Screenshot Interfaccia Web"/>

</div>
</div>

---

## Configurazioni hardware: 3 tipi testati

<div class="grid-2">
<div>

### Configurazioni testate

**<span style="color: #dc2626;">1. Quattro Sensori in Parallelo:</span>**
<ul>
  <li>Disposti sulla stessa linea: misuravano solo la profondità 1D con forti interferenze acustiche tra loro. Bassa risoluzione sull'asse X</li>
</ul>

**<span style="color: #d97706;">2. Due Sensori Perpendicolari (X, Y):</span>**
<ul>
  <li>Disposizione ad "L": mappava il piano, ma l'altezza della mano (Z) falsava le coordinate (X, Y).</li>
</ul>

**<span style="color: #16a34a;">3. Quattro sensori opposti (2 per asse, scelta finale):</span>**
<ul>
  <li>Cornice chiusa 49 x 51 cm: confrontando i sensori opposti, la profondità del gesto viene compensata</li>
</ul>

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
<ul>
  <li>Se i 4 sensori vengono usati contemporaneamente, l'eco di uno viene captato per sbaglio da un altro.</li>
  <li><strong>La soluzione:</strong> lettura in sequenza (S1 -> S2 -> S3 -> S4) con pausa di <strong>18 ms</strong> tra i pings per far decadere i rimbalzi.</li>
</ul>

### 2. Gestione dei Timeout
<ul>
  <li>Di default, se un'onda non torna indietro Arduino si blocca in attesa fino a <strong>1 secondo</strong></li>
  <li><strong>La soluzione:</strong> timeout ridotto a 8 ms (~137 cm max). Se l'eco non torna, scarta il dato e continua subito senza bloccare lo streaming (~18-20 Hz).</li>
</ul>

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
<ul>
  <li><strong>Filtro mediana mobile:</strong> Legge gli ultimi 5 valori letti e prende la mediana per attenuare il jitter continuo</li>
  <li><strong>Scarto dei valori anomali:</strong> Scarta variazioni brusche anomale nel singolo frame ("salti")</li>
  <li><strong>Recupero Dinamico:</strong> Riconosce i cambi di traiettoria intenzionali e rapidi</li>
</ul>

### Creazione del dataset
<ul>
  <li>Acquisizione interattiva tramite interfaccia web</li>
  <li><strong>191 registrazioni complessive</strong> su 17 lettere</li>
  <li>Campioni acquisiti da diversi utenti a varie velocità (quindi vari numeri di punti per lettera)</li>
</ul>

</div>
<div class="svg-card">

<img src="assets/slide_filtering.svg" width="350"/>

</div>
</div>

---

## Sensori e classificazione

<div class="grid-2">
<div>

### Riconoscimento dei gesti

<ul>
  <li>Il sistema risolve un problema di <strong>classificazione supervisionata</strong> (17 classi): mappare una sequenza continua di movimenti (coordinate) in una categoria discreta.</li>
</ul>

### Input e Output del Modello

<ul>
  <li><strong>Input dei sensori:</strong> Serie temporale di coordinate (X, Y) rilevate durante il movimento della mano</li>
  <li><strong>Input al modello di ML:</strong> Vettore di feature numeriche a 39 dimensioni estratto al termine del gesto</li>
  <li><strong>Output:</strong> etichetta discreta della classe (tra 17 lettere dell'alfabeto) con la relativa distribuzione di confidenza</li>
</ul>

</div>
<div class="svg-card">

<img src="assets/slide_coordinates_to_grid.svg" width="390"/>

</div>
</div>

---

## Elaborazione dati

<div class="grid-2">
<div>

### Conversione da coordinate a griglia di punti
<ol style="margin-top: 4px; margin-bottom: 12px; padding-left: 22px;">
  <li><strong>Normalizzazione &amp; Centratura:</strong>
    <ul>
      <li>Scaling uniforme basato sul lato maggiore</li>
      <li>La lettera mantiene le sue proporzioni originali</li>
    </ul>
  </li>
  <li><strong>Griglia di Occupanza 6x6 (36 celle)</strong>
    <ul>
      <li>Matrice binaria delle celle attraversate</li>
      <li><strong>Interpolazione lineare</strong> tra punti: nessun buco</li>
      <li>Completa invarianza da senso orario o antiorario</li>
    </ul>
  </li>
  <li><strong>Metriche Globali (3 valori)</strong>
    <ul>
      <li>Rapporto di forma, larghezza e altezza in centimetri</li>
    </ul>
  </li>
</ol>

</div>
<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; justify-items: center; align-items: center;">

<img src="assets/gesture_samples/L_2f4f54e7.png" width="180" style="border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: none;" alt="Lettera L"/>
<img src="assets/gesture_samples/O_10f171cc.png" width="180" style="border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: none;" alt="Lettera O"/>
<img src="assets/gesture_samples/S_145c3c2d.png" width="180" style="border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: none;" alt="Lettera S"/>
<img src="assets/gesture_samples/Z_1421e90c.png" width="180" style="border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: none;" alt="Lettera Z"/>

</div>
</div>

---

<!-- _class: compact-slide -->

## Machine Learning in Python (Random Forest) e feature engineering

### Dataset & Training Matrix (192 campioni &times; 39 feature)

<table style="width: 100%; border-collapse: collapse; font-size: 12px; margin: 4px 0 8px 0; background: #ffffff; border-radius: 6px; overflow: hidden; border: 1px solid #cbd5e1;">
  <thead>
    <tr style="background: #e2e8f0; color: #1e293b;">
      <th style="padding: 4px 8px; text-align: left;">ID</th>
      <th style="padding: 4px 8px; text-align: center;">Target</th>
      <th style="padding: 4px 8px; text-align: center;">Grid[0,0]</th>
      <th style="padding: 4px 8px; text-align: center;">Grid[0,1]</th>
      <th style="padding: 4px 8px; text-align: center;">...</th>
      <th style="padding: 4px 8px; text-align: center;">Aspect</th>
      <th style="padding: 4px 8px; text-align: center;">Width</th>
      <th style="padding: 4px 8px; text-align: center;">Height</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-top: 1px solid #e2e8f0;">
      <td style="padding: 3px 8px; font-family: monospace;">2f4f54e7</td>
      <td style="padding: 3px 8px; text-align: center; font-weight: bold; color: #0284c7;">L</td>
      <td style="padding: 3px 8px; text-align: center;">0.0</td>
      <td style="padding: 3px 8px; text-align: center;">0.0</td>
      <td style="padding: 3px 8px; text-align: center;">...</td>
      <td style="padding: 3px 8px; text-align: center;">1.46</td>
      <td style="padding: 3px 8px; text-align: center;">9.3 cm</td>
      <td style="padding: 3px 8px; text-align: center;">13.6 cm</td>
    </tr>
    <tr style="border-top: 1px solid #e2e8f0; background: #f8fafc;">
      <td style="padding: 3px 8px; font-family: monospace;">4a081398</td>
      <td style="padding: 3px 8px; text-align: center; font-weight: bold; color: #0284c7;">O</td>
      <td style="padding: 3px 8px; text-align: center;">0.0</td>
      <td style="padding: 3px 8px; text-align: center;">1.0</td>
      <td style="padding: 3px 8px; text-align: center;">...</td>
      <td style="padding: 3px 8px; text-align: center;">1.06</td>
      <td style="padding: 3px 8px; text-align: center;">15.0 cm</td>
      <td style="padding: 3px 8px; text-align: center;">15.9 cm</td>
    </tr>
    <tr style="border-top: 1px solid #e2e8f0;">
      <td style="padding: 3px 8px; font-family: monospace;">1421e90c</td>
      <td style="padding: 3px 8px; text-align: center; font-weight: bold; color: #0284c7;">Z</td>
      <td style="padding: 3px 8px; text-align: center;">1.0</td>
      <td style="padding: 3px 8px; text-align: center;">1.0</td>
      <td style="padding: 3px 8px; text-align: center;">...</td>
      <td style="padding: 3px 8px; text-align: center;">0.93</td>
      <td style="padding: 3px 8px; text-align: center;">11.3 cm</td>
      <td style="padding: 3px 8px; text-align: center;">10.5 cm</td>
    </tr>
  </tbody>
</table>

<div style="display: flex; justify-content: space-between; font-size: 14px; color: #334155; margin-bottom: 8px;">
  <span>&bull; <strong>17 classi</strong> distinte</span>
  <span>&bull; <strong>39 feature numeriche:</strong> 36 griglia binaria 6&times;6 + 3 geometriche</span>
  <span>&bull; <strong>Modello:</strong> Random Forest (100 alberi)</span>
</div>

<div style="display: flex; justify-content: center; width: 100%; height: 210px;">
  <img src="assets/tree_visualization.svg" style="width: 100%; height: 100%; max-height: 210px; object-fit: contain; border-radius: 8px; box-shadow: none;" alt="Visualizzazione Decision Tree"/>
</div>

---

## Risultati Sperimentali & Analisi degli Errori

<div class="grid-2">
<div>

### Metriche Globali
<ul>
  <li><strong>Accuratezza Totale:</strong> <strong>91.1%</strong></li>
  <li><strong>Precision Macro:</strong> <strong>91.3%</strong></li>
  <li><strong>Recall Macro:</strong> <strong>90.9%</strong></li>
</ul>

### Lettere con Prestazioni Massime
<ul>
  <li><strong>P, G (100%):</strong> tratti chiusi inconfondibili</li>
  <li><strong>I, S, A (&gt;95%):</strong> forma molto identificabile</li>
</ul>

### Ambiguità Rilevate
<ul>
  <li><strong>D vs J:</strong> parte superiore aperta nei tratti veloci</li>
  <li><strong>M vs N:</strong> bassa risoluzione della griglia 6x6 sul picco centrale (meglio 8x8)</li>
</ul>

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

<ul>
  <li><strong>Lettura seriale non bloccante:</strong> task asincrono di background dedicato alla lettura dello stream USB (~18–20 Hz)</li>
  <li><strong>WebSockets full-duplex:</strong> invio dati in tempo reale di coordinate (X, Y) grezze e filtrate ai client connessi</li>
  <li><strong>Inferenza &amp; Retrain Asincrono:</strong> esecuzione del modello Random Forest in thread pool (run_in_executor) per non bloccare l'event loop</li>
  <li><strong>Persistenza Dati:</strong> salvataggio dati registrazioni su CSV</li>
</ul>

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
<ul>
  <li>Interazione touchless affidabile senza dispositivi ottici</li>
  <li>Sistema facile da usare e a bassa latenza</li>
</ul>

### Limiti Fisici
<ul>
  <li>Frequenza vincolata dalla velocità del suono in aria</li>
  <li>Sensibilità al materiale usato per il tracciamento (mano, bottiglia, etc)</li>
  <li>Sensibilità all'inclinazione del palmo</li>
</ul>

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