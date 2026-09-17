---
marp: true
theme: default
paginate: true
size: 16:10
style: |
  section {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 20px;
    padding: 34px 44px;
    background: #f8fafc;
    color: #0f172a;
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
    margin-bottom: 8px;
  }
  ul {
    margin-bottom: 12px;
  }
  li {
    margin-bottom: 6px;
    line-height: 1.35;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1.05fr 0.95fr;
    gap: 24px;
    align-items: center;
  }
  .highlight-box {
    background: #e0f2fe;
    border-left: 5px solid #0284c7;
    padding: 10px 14px;
    border-radius: 4px;
    margin: 10px 0;
  }
  .svg-card {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .svg-card img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  }
  section.hero {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 30px 48px;
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
    margin-top: 14px;
    letter-spacing: 0.02em;
  }
---

<!-- _class: hero -->
<!-- _paginate: false -->

# Riconoscimento lettere in 2D con sensori di distanza

<div style="display: flex; justify-content: center; width: 100%; margin: 6px 0;">
  <img src="assets/slide_hero.svg" width="700" style="border-radius: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.08);"/>
</div>

<span class="hero-tag">Progetto di Gruppo — Interazione Uomo-Macchina / Sistemi Embedded</span>

---

## Dimostrazione del Sistema

<div class="grid-2">
<div>

### Il Sistema in Azione
* **Tracciamento dal Vivo:** Disegno di lettere a mezz'aria all'interno della cornice acustica
* **Visualizzazione Real-Time:** Scia rossa fluida renderizzata sul Canvas a 30 FPS
* **Classificazione Istantanea:** Riconoscimento della lettera e stima di confidenza al termine del tratto
* **Zero Dispositivi Indossabili:** Libertà totale di movimento senza telecamere né guanti

</div>
<div class="svg-card">

<img src="assets/slide_video_demo.svg" width="380"/>

</div>
</div>

---

## Obiettivi e Motivazioni

<div class="grid-2">
<div>

### Perché gli ultrasuoni?
* **Privacy-First:** Nessuna telecamera né acquisizione ottica negli ambienti
* **Zero Dispositivi Indossabili:** Nessun guanto o anello smart
* **Economicità Estrema:** Pochi euro di componenti hardware contro costosi sistemi ottici

<div class="highlight-box">
<b>Traguardo:</b> Riconoscere 17 lettere disegnate a mezz'aria in una cornice 49×51 cm con accuratezza &gt;90%.
</div>

</div>
<div class="svg-card">

<img src="assets/slide_motivations.svg" width="370"/>

</div>
</div>

---

## Formulazione del Problema: Classificazione Multiclasse

<div class="grid-2">
<div>

### Natura del Task: Riconoscimento di Pattern
* Il sistema risolve un problema di **classificazione multiclasse supervisionata**: mappare una sequenza gestuale continua in una categoria simbolica discreta.

### Input e Output del Modello
* **Input Grezzo:** Serie temporale di coordinate $(X, Y)$ rilevate durante il movimento della mano
* **Input al Modello:** Vettore di feature numeriche a 39 dimensioni estratto al termine del gesto
* **Output:** Etichetta discreta della classe (tra 17 lettere dell'alfabeto) con la relativa distribuzione di confidenza

</div>
<div class="svg-card">

<img src="assets/slide_coordinates_to_grid.svg" width="390"/>

</div>
</div>

---

## Hardware & Geometria di Triangolazione

<div class="grid-2">
<div>

### La Cornice Acustica ($49 \times 51\text{ cm}$)
* **4 Sensori HC-SR04** posti sui punti mediani dei lati
* Asse verticale: S1 (Alto) e S2 (Basso)
* Asse orizzontale: S3 (Sinistra) e S4 (Destra)

### Il Trucco della Triangolazione
* La mano si muove a mezz'aria, quindi ha anche un'altezza (quota).
* Confrontando i due sensori opposti (es. Sinistra e Destra), **l'altezza della mano si annulla nei calcoli**.
* Otteniamo la posizione esatta 2D $(X, Y)$ anche se alziamo o abbassiamo la mano mentre disegniamo!

</div>
<div class="svg-card">

<img src="assets/hardware_triangulation.svg" width="460"/>

</div>
</div>

---

## Firmware Arduino: Sfide Acustiche e Temporali

<div class="grid-2">
<div>

### 1. Interferenza Acustica (Crosstalk)
* **Il problema:** Se i 4 sensori sparano insieme, l'eco di uno viene captato per sbaglio da un altro (misure false).
* **La soluzione:** **Interrogazione sequenziale** (S1 $\to$ S2 $\to$ S3 $\to$ S4) con pausa di **18 ms** tra i pings per far decadere i rimbalzi.

### 2. Gestione dei Timeout
* **Il problema:** Di default, se un'onda non torna indietro Arduino si blocca in attesa fino a 1 secondo!
* **La soluzione:** **Timeout ridotto a 8 ms** (~137 cm max). Se l'eco non torna, scarta il dato e continua subito senza bloccare lo streaming (~18-20 Hz).

</div>
<div class="svg-card">

<img src="assets/slide_firmware.svg" width="375"/>

</div>
</div>

---

## Raccolta Dati & Pulizia del Segnale

<div class="grid-2">
<div>

### Filtri sul Flusso Seriale
* **Filtro Mediana Mobile:** Finestra a 5 campioni per attenuare il jitter continuo
* **Reiezione Salti:** Scarta variazioni brusche anomale nel singolo frame
* **Recupero Dinamico:** Riconosce i cambi di traiettoria intenzionali e rapidi

### Raccolta del Dataset
* Acquisizione interattiva tramite interfaccia web
* **191 registrazioni complessive** su 17 lettere
* Campioni acquisiti da diversi utenti a varie velocità

</div>
<div class="svg-card">

<img src="assets/slide_filtering.svg" width="350"/>

</div>
</div>

---

## Feature Engineering: Invarianza Spaziale e Morfologica

<div class="grid-2">
<div>

### I 3 Passaggi Chiave:
1. **Normalizzazione & Centratura:**
   * Scalatura uniforme basata sul lato maggiore
   * La lettera mantiene le sue proporzioni originali
2. **Griglia di Occupanza $6 \times 6$ (36 celle):**
   * Matrice binaria delle celle attraversate
   * **Interpolazione lineare** tra punti: nessun buco
   * Completa invarianza da senso orario o antiorario!
3. **Metriche Globali (3 valori):**
   * Rapporto di forma, larghezza e altezza in centimetri

</div>
<div class="svg-card">

<img src="assets/feature_pipeline.svg" width="460"/>

</div>
</div>

---

## Modello di Machine Learning in Python

<div class="grid-2">
<div>

### Scelta del Modello: Random Forest
* **Dataset Compatto:** Evita il rischio di memorizzazione tipico delle reti neurali profonde
* **Robustezza alle Feature Miste:** Gestisce assieme flag binari di griglia e metriche geometriche
* **Inferenza Istantanea:** Previsione in meno di un millisecondo
* **Aggiornamento a Caldo:** Riaddestramento live senza interruzione del server

### Protocollo di Validazione
* **Stratified 5-Fold Cross-Validation:** Tutte le classi bilanciate tra training e test

</div>
<div class="svg-card">

<img src="assets/slide_rf.svg" width="340"/>

</div>
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
* **P, G (100%):** Tratti chiusi inconfondibili
* **I, S, A (>95%):** Spiccata unicità morfologica

### Ambiguità Rilevate
* **D vs J:** Parte superiore aperta nei tratti veloci
* **M vs N:** Risoluzione griglia sul picco centrale

</div>
<div class="svg-card">

<img src="assets/slide_metrics.svg" width="340"/>

</div>
</div>

---

## Architettura Software & Interfaccia Utente

<div class="grid-2">
<div>

### Web App Reattiva Full-Stack
* **Radar 2D Interattivo:** Traccia la posizione della mano in tempo reale con visualizzazione dei raggi
* **Scia Rossa Dinamica:** Rendering fluido del tratto disegnato a mezz'aria
* **Classificazione Live:** Mostra le 4 predizioni più probabili con percentuali di confidenza
* **Retrain con Un Click:** Aggiorna il modello direttamente dal browser

</div>
<div class="svg-card">

<img src="assets/slide_ui.svg" width="350"/>

</div>
</div>

---

## Conclusioni & Sviluppi Futuri

<div class="grid-2">
<div>

### Risultati Ottenuti
* Interazione touchless affidabile senza dispositivi ottici
* Invarianza geometrica grazie alla griglia di occupanza con interpolazione
* Sistema integrato reattivo a bassissima latenza

### Limiti Fisici
* Frequenza vincolata dalla velocità del suono in aria
* Sensibilità all'inclinazione del palmo

### Direzioni Future
* Air-writing volumetrico 3D
* Porting su microcontrollore (Edge / TinyML)

</div>
<div class="svg-card">

<img src="assets/slide_future.svg" width="340"/>

</div>
</div>

---

<!-- _class: hero -->
<!-- _paginate: false -->

# Grazie per l'Attenzione!
### 2D Ultrasonic Hand Tracker & Classifier

<div style="display: flex; justify-content: center; width: 100%; margin: 12px 0;">
  <img src="assets/slide_closing.svg" width="670" style="border-radius: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.06);"/>
</div>

<span class="hero-tag">Siamo a disposizione per qualsiasi domanda o approfondimento tecnico!</span>