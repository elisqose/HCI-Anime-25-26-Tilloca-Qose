# Report — HCI Assignment 2025-2026
**Membri**: Alessandra Tilloca, Elis Qose
---

## Introduzione

Il progetto consiste in un analisi dei dati provenienti dal database di MyAnimeList che riguardano titoli di anime, personaggi, persone che ci hanno lavorato e dati 
statistici come valutazioni, raccomandazioni, etc. L'obiettivo è usare questi dati per raccontare due storie diverse rispondendo alle domande: 
- Come è cambiato il mondo degli anime nel tempo?
- Come orientarsi in un catalogo sconfinato di titoli?

Il nostro lavoro è stato diviso in tre fasi: esplorazione, pulizia e analisi. Durante la prima fare abbiamo effettuato una visione generale dei dataset per capire che
dati contenessero. Durante la seconda fase abbiamo effettuato la pulizia di ciascun dataset per assicurarci che i dati fossero puliti e privi di errori. Nella fase finale
abbiamo usato i dataset puliti per ottenere informazioni che abbiamo poi utilizzato nel nostro storytelling. 

---

## Task 1 — Data Cleaning: Esplorazione e Pulizia dei Dataset

### Soluzione

Sono stati prodotti 13 notebook di cleaning, uno per ciascun dataset fornito. L'approccio è sistematico: ogni notebook segue la stessa struttura 
— ispezione delle colonne, analisi dei valori mancanti, rimozione di duplicati, normalizzazione dei tipi e salvataggio del CSV pulito. In alcuni notebook che richiedevano
delle verifiche più approfondite abbiamo fatto anche dei controlli personalizzati. Abbiamo creato due script Python di supporto (`dataset_analyzer.py`, `foreign_key_analyzer.py`) per automatizzare l'analisi strutturale 
e la verifica dell'integrità delle chiavi esterne tra dataset.

### Problematiche

Il dataset `ratings.csv` ha richiesto più tempo in confronto agli altri datasets in quanto si tratta di un file molto grande (124 milioni di righe, 4.3 GB).

### Requisiti

Tutti e 13 i dataset indicati nella specifica sono coperti da un notebook dedicato. I dataset puliti vengono salvati in `datasets_cleaned/` e sono il punto di 
partenza per tutte le analisi successive.

### Limitazioni

Abbiamo fatto il nostro meglio nel verificare tutti i casi possibili che si possono riscontare nei datasets. Considerando la quantità elevata di dati, questo non esclude
del tutto la possibilità di qualche errore particolare che non è stato rilevato. 

---

## Task 2 — Data Analysis: Visualizzazione e Storytelling

### Soluzione

I dati puliti vengono utilizzati in due notebook narrativi distinti, ognuno dei quali risponde a un insieme di domande specifiche tramite visualizzazioni interattive 
realizzate con Plotly e Matplotlib. Il codice dei grafici è stato estratto in due librerie Python dedicate (`evoluzione_charts.py`, `navigazione_charts.py`), per mantenere
i notebook ridotti, lasciare più visibilità ai grafici e facilitare la lettura.

### Problematiche

Abbiamo riscontrato delle difficoltà nella creazione dei grafici per quanto riguarda la visualizzazione dei dati. In alcuni casi i dati si sovrapponevano rendendo il grafico
poco leggibile. In alcuni altri casi i dati si perdevano e per questo abbiamo usato la scala logaritmica. 

### Requisiti

Entrambi i notebook soddisfano il requisito di analisi e visualizzazione per fan e giornalisti: ogni sezione è introdotta da testo che contestualizza il grafico, 
rendendolo accessibile a lettori non tecnici. Tutti i grafici Plotly sono interattivi (hover, zoom, slider, play/pausa, tooltip con dettagli completi).

### Limitazioni

Per quanto riguarda il confronto generazionale, abbiamo deciso di escludere Silent Generation e Gen Alpha per volume insufficiente di utenti. In più, non tutti i dataset 
puliti sono stati utilizzati ma questo è dovuto alla scelta degli argomenti per le due storie. 

---

## Conclusioni

Alla fine di questo progetto, pur non essendo appassionati degli anime, abbiamo scoperto un mondo più articolato di quanto immaginassimo. Abbiamo trovato interessante 
il fatto che l'evoluzione della tecnologia si riflette anche nel mercato degli anime. 

---

## Divisione del Lavoro

Entrambi i membri hanno contribuito a tutte le parti del progetto. La divisione del lavoro è stata equa e ogni membro ha contribuito a ogni file. Il lavoro su tutte le 
parti è stato svolto parallelamente.

---

## Informazione Extra

Uso di Generative AI: Durante lo svolgimento del progetto, abbiamo usato Claude per assisterci nelle parti di codice. Tutto il codice è stato compreso e validato prima 
dell'integrazione. L'analisi dei dati, l'interpretazione dei risultati e le scelte di design sono interamente nostre.

I dati utilizzati nel progetto provengono dal database di MyAnimeList. Per la realizzazione dei grafici abbiamo utilizzato le librerie Plotly e Pandas. 
Abbiamo inoltre effettuato ricerche online per contestualizzare alcuni risultati, in particolare riguardo all'evoluzione dei formati di distribuzione e alle abitudini 
di consumo per paese.
