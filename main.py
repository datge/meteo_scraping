from bs4 import BeautifulSoup
import requests
import datetime
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
            print ("Scegliere un orario nel futuro")
            

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
        # ritorno la temperatura dal dizionario
        self.ritorno_temp = self.dizionario.get(ora).find('td', class_='col4')
        return self.ritorno_temp.get_text()




ilmeteo = IlMeteo('loreto aprutino')
print (ilmeteo.get_temp('13'))

meteo = Meteo_3B('loreto aprutino')
print (meteo.get_temp('13'))