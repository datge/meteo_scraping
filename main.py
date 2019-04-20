from bs4 import BeautifulSoup
import requests

class Meteo_3B():
    

    def __init__(self, paese):
        METEO_3B_URL = "https://www.3bmeteo.com/meteo/"

        self.paese = paese
        self.paese_parser = paese.replace(" ", "+")

        
        self.request = requests.get(METEO_3B_URL+self.paese_parser)

        self.soup = BeautifulSoup(self.request.content, 'html.parser')

        # prende in input l'ora e ne strapola la temperatura per 3bmeteo
    def get_temp(self, ora):
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
        self.estrapola = self.dizionario.get(ora)
        try :
            #ritorniamo il testo della temperatura contenuto nello span 
            self.ritono = self.estrapola.find('span', class_='switchcelsius switch-te active' ).get_text()
            return self.ritono
        except AttributeError:
            print ("Scegliere un orario nel futuro")
            

meteo = Meteo_3B('loreto aprutino')
print (meteo.get_temp('19:00'))

meteo2 = Meteo_3B('roma')
print (meteo2.get_temp('22:00'))