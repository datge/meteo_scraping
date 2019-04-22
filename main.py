from bs4 import BeautifulSoup
import requests
import datetime
import re
import pandas as pd
class Meteo_3B():
    

    def __init__(self, paese):
        METEO_3B_URL = "https://www.3bmeteo.com/meteo/"

        self.paese = paese
        self.paese_parser = paese.replace(" ", "+")

        
        self.request = requests.get(METEO_3B_URL+self.paese_parser)

        self.soup = BeautifulSoup(self.request.content, 'html.parser')

        # prende in input l'ora e ne strapola la temperatura per 3bmeteo
    def get_temp(self, ora):
        self.ora = ora + ':00'
        self.li_all = self.soup.find_all('div', class_='row-table noPad')
        self.dizionario={}
        #a e b perchè il sito utilizza due classi distinte per i div che raggruppano tutta la linea(data,temp,etc..)
        for li in self.li_all:
            self.a = li.find_all('div', class_='col-xs-1-4 big zoom_prv')
            self.b = li.find_all('div', class_='col-xs-1-4 big')
            if self.a:
                #aggiungiamo le date in un dizionario con il rispettivo codice html, così possiamo estrapolarlo poi meglio 
                #utilizzando la data cone key del codice html.
                self.dizionario.update({self.a[0].get_text().strip(): li})
            if self.b:
                self.dizionario.update({self.b[0].get_text().strip(): li})
        self.estrapola = self.dizionario.get(self.ora)
        try :
            #ritorniamo il testo della temperatura contenuto nello span 
            self.ritono = self.estrapola.find('span', class_='switchcelsius switch-te active' ).get_text()
            return self.ritono
        except AttributeError:
            return ("Scegliere un orario nel futuro")
            

class IlMeteo():
    def __init__(self, paese):
        IL_METEO_URL = "https://www.ilmeteo.it/meteo/"

        # giorno corrente , ci servira' per estrapolare il tr di ogni singolo giorno
        self.oggi = str(datetime.date.today()).split('-')[2]
    
        self.paese = paese
        self.paese_parser = paese.replace(" ", "+")

        
        self.request = requests.get(IL_METEO_URL+self.paese_parser)
       

        self.soup = BeautifulSoup(self.request.content, 'html.parser')
    def get_temp(self, ora):
        self.dizionario={}
        # ciclo per l id delle tr che varia a seconda dell ora del giorno 
        for i in range(0,24):
            try:
                
                self.tr_estrapolata = self.soup.find('tr', id=f'h{i}-{self.oggi}-1')
                
                self.orario_estrapolato =  self.tr_estrapolata.find('span', class_='ora')

                # aggiunto in dizionario chiave(ora) :  codice html di quell' ora
                self.dizionario.update({ self.orario_estrapolato.get_text() : self.tr_estrapolata })

            except Exception as e:
                pass
        try:
            # ritorno la temperatura dal dizionario
            self.ritorno_temp = self.dizionario.get(ora).find('td', class_='col4')
            return self.ritorno_temp.get_text()
        except AttributeError:
            return ("Scegliere un orario nel futuro")


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
        self.data_set_paese =  (self.data_frame[(self.data_frame['Denominazione in italiano'].astype(str)== self.paese)])
        # estrapoliamo la regione nel formato che ci serve(abbreviato)
        self.regione = self.data_set_paese['Denominazione regione']
        # estrapoliamo la provincia nel formato che ci serve(abbreviato)
        provincia = self.data_set_paese['Sigla automobilistica']



        # prendiamo l'htm dal primo url da cui andiamo a cercare il paeern regex per trovare l'url esatto e soprattutto
        # un codice a 4 cifre che il sito assegna ad ogni citta per il link esatto
        self.URL = f"http://meteo.repubblica.it/meteo/italia/previsioni/{self.paese}/{self.regione.values[0]}/{provincia.values[0]}/oggi"
        self.request = requests.get(self.URL)
        self.oggi = str(datetime.date.today()).split('-')[2]           
        self.pattern_codice_citta = re.compile(r'http://meteo\.repubblica\.it/previsioni\.php\?citta=[\w\W]*&c=([\d]{4})&gm='+re.escape(self.oggi)+'&forecast_granularity=')
        self.pattern_trovato = self.pattern_codice_citta.search(self.request.text).group(1)
        self.URL_PARSATO = f"http://meteo.repubblica.it/previsioni.php?citta={self.paese}&c={self.pattern_trovato}&gm={self.oggi}&forecast_granularity="
        ######
        print (self.URL_PARSATO)
        # andiamo ad aprire in beautifulsoup l'url parsato trovato sopra
        self.request_parsato = requests.get(self.URL_PARSATO)
        self.soup = BeautifulSoup(self.request_parsato.text, 'html.parser')
        ######

# funziona che estrapola la temperatura e la assegna ad un dizionatio chiave:ora, valore:temperatura
    def get_temp(self, orario):
        orario = orario + '.00'
        dizionario = {}
        for i in range(0,24):
            try:
                tabella = self.soup.find('tr', id=f"h{i}-{self.oggi}")
                ora = tabella.find('span', class_='ora')
                temp = tabella.find('td', class_='td_4')
                dizionario.update({ora.text:temp})
                #print (ora.text, temp.text)
            except Exception as e:
                pass
        try:
            ritorno = dizionario[orario].text
            return ritorno
        except KeyError:
            return ("Scegliere un orario nel futuro")
"""
ilmeteo = IlMeteo('roma')
print (ilmeteo.get_temp('20'))

meteo = Meteo_3B('roma')
print (meteo.get_temp('20'))

meteo_rep = Meteo_Rep('roma')
print(meteo_rep.get_temp('20'))
"""