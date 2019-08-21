# dsrace
GPS LapTimer with RaspberryPI and Python

https://github.com/smartdan/dsrace

# PREREQ

sudo apt-get install gpsd gpsd-clients python-gps
sudo apt-get install arrow chronograph input 
sudo pip install arrow chronograph input 
pip install geopy
sudo pip install arrow chronograph input 
sudo pip install telepot
sudo pip install shapely
sudo apt-get install libgeos++
sudo systemctl stop gpsd.socket
sudo systemctl disable gpsd.socket
sudo pip install shapely

sudo gpsd /dev/ttyACM0 -F /var/run/gpsd.sock
cgps -s


# INTRO
Per girare in pista con la mia Pit Bike e tenere traccia dei miei progressi come pilota provetto ho messo in piedi un sistema per il tracciamento dei tempi su giro.

# HW
Il sistema è composto da

* Raspberry Pi 3
* Micro SD
* Modulo gps usb
* Paracolpi in spugna
* Schermo HAT displayOtron 
* 6 pulsanti touch
* 6 led
* schermo LCD RGB
* Pit Bike PBS Pro
* Batteria Power Bank 3.3Ah 1.5A
* Questo slideshow richiede JavaScript.
* Telegram BOT Client

# FUNZIONALITA’
Una volta acceso, il sistema avvia automaticamente il software Python che si occupa di gestire il cronometro e le varie funzioni dello schermo.

Il display ha 6 pulsanti con i quali è possibile decidere di:

* Avviare la sessione
* Fermare la sessione
* Cambiare la pista di riferimento
* Uscire dal programma
* Inviare i dati al server
* Le informazioni disponibili prima, durante e dopo la sessione sono:

RIGA 1: Tempo su giro corrente
RIGA 2: Tempo dell’ultimo giro effettuato
RIGA 3: Miglior giro della sessione
LED DI NOTIFICA LATERALI: segnalazioni varie su stato del segnale GPS e rilevamento giro ed intertempi
COLORI DELLO SCHERMO:
ROSSO: giro record
BLU: giro in corso
VERDE: giro lento
Oltre alle informazioni disponibili dallo schermo del sistema, se si connette preventivamente il Raspberry ad una Wifi, si possono inviare i dati ad un server FTP.

Questi dati possono essere visualizzati sia per mezzo di un BOT di Telegram che di una pagina PHP ospitata sul mio sito.

# SW
E’ iniziato tutto con uno script in Python, poi è diventato un sistema distribuito di tutto rispetto.

Per poter utilizzare una micro SD da 4GB ho installato il software su una distribuzione Raspbian Lite (o anche una DietPI).

Ho messo insieme lo script utilizzando varie parti:

* cronometro python con  Chronograph
*  python-gps per utilizzare i dati di posizionamento rilevati dall’antenna gps
* shapely , utm  e geopy per calcolare il momento di passaggio per vari punti di rilevamento
* telepot per il bot di telegram

I risultati sono soddisfacenti, considerando il costo dei componenti. L’utilizzo di questo tipo di gps ha dei limiti difficilmente superabili.

Ho cercato comunque di correggere l’errore dovuto al tempo di ri-acquisizione utilizzando i dati di velocità e bearing con strategie di dead reckoning.

# VARIANTI
Ho cercato vari modi per miniaturizzare ulteriormente il sistema. Ho messo in piedi vari altri prototipi utilizzando:

* Raspberry PI Zero al posto del PI 3
* schermi OLED
* matrice di LED a scorrimento
* schermo ePaper

Ci vediamo in pista.
