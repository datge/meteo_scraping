import pandas as pd 
import requests
from bs4 import BeautifulSoup
import re
import datetime

class Meteo_Rep():
    def __init__(self,paese):
        #andiamo a leggere il csv
        cvs = pd.read_csv("Elenco-comuni-italiani.csv", encoding='latin-1', delimiter=';')
        # dizionario con l' abbreciazione delle regioni
        regioni = {
            'Abruzzo':'ABR',
            'Piemonte': 'PIE',
            "Valle d'aosta": 'VAL',
            'Lombardia': 'LOM',
            'Trentino alto adige': 'TRE',
            'Veneto': 'VEN',
            'Friuli venezia giulia': 'FRI',
            'Liguria': 'LIG',
            'Emilia romagna': 'EMR',
            'Toscana': 'TOS',
            'Umbria': 'UMB',
            'Marche': 'MAR',
            'Lazio': 'LAZ',
            'Molise': 'MOL',
            'Campagnia': 'CAM',
            'Puglia': 'PUG',
            'Basilicata': 'BAS',
            'Calabria': 'CAL',
            'Sicilia': 'SIC',
            'Sardegna': 'SAR',
        }

        #creiamo un data frame dal cvs con solo questi tre campi che ci interessano
        self.data_frame = cvs[['Denominazione in italiano','Denominazione regione','Sigla automobilistica']]

        # stostituiamo la regione nel data frame con la sua abbreviazione dal dizionario per ogni paese associato alla regione
        for key,value in regioni.items():
            self.data_frame = self.data_frame.replace(to_replace=[key],
                value=value)

        self.paese = paese.title()
        # andiamo a cercare il paese a che ci interessa
        data_set_paese =  (self.data_frame[(self.data_frame['Denominazione in italiano'].astype(str)== self.paese)])
        # estrapoliamo la regione nel formato che ci serve(abbreviato)
        regione = data_set_paese['Denominazione regione']
        # estrapoliamo la provincia nel formato che ci serve(abbreviato)
        provincia = data_set_paese['Sigla automobilistica']


        # prendiamo l'htm dal primo url da cui andiamo a cercare il paeern regex per trovare l'url esatto e soprattutto
        # un codice a 4 cifre che il sito assegna ad ogni citta per il link esatto
        URL = f"http://meteo.repubblica.it/meteo/italia/previsioni/{self.paese}/{regione.values[0]}/{provincia.values[0]}/oggi?forecast_granularity="
        request = requests.get(URL)
        self.oggi = str(datetime.date.today()).split('-')[2]         
        pattern_codice_citta = re.compile(r'http://meteo\.repubblica\.it/previsioni\.php\?citta=[\w\W]*&c=([\d]{4})&gm='+re.escape(self.oggi)+'&forecast_granularity=')
    
        pattern_trovato = pattern_codice_citta.search(request.text).group(1)
        URL_PARSATO = f"http://meteo.repubblica.it/previsioni.php?citta={self.paese}&c={pattern_trovato}&gm={self.oggi}&forecast_granularity="

        ######

        # andiamo ad aprire in beautifulsoup l'url parsato trovato sopra
        request_parsato = requests.get(URL_PARSATO)
        self.soup = BeautifulSoup(request_parsato.text, 'html.parser')
        print (URL_PARSATO)
        ######

# funziona che estrapola la temperatura e la assegna ad un dizionatio chiave:ora, valore:temperatura
    def get_temp(self, orario):
        orario = orario + '.00'
        dizionario = {}
        for i in range(0,24):
            try:
                tabella = self.soup.find('tr', id=f"h{i}-{self.oggi}-1")
                ora = tabella.find('span', class_='ora')
                temp = tabella.find('td', class_='td_4')
                dizionario.update({ora.text:temp})
                print (ora.text, temp.text)
            except Exception as e:
                pass
        try:
            ritorno = dizionario[orario].text
            return ritorno
        except KeyError:
            return ("Scegli un'orario nel futuro")
meteo_rep = Meteo_Rep('loreto aprutino')

print(meteo_rep.get_temp('17'))
