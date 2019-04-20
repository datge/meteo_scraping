from bs4 import BeautifulSoup
import requests


paese = 'milano'
paese_parser = paese.replace(" ", "+")

meteo_3b_url = "https://www.3bmeteo.com/meteo/"
request = requests.get(meteo_3b_url+paese_parser)

soup = BeautifulSoup(request.content, 'html.parser')

# prende in input l'ora e ne strapola la temperatura per 3bmeteo
def get_temp(ora):
    li_all = soup.find_all('div', class_='row-table noPad')
    dizionario={}
    #a e b perchè il sito utilizza due classi distinte per i div che raggruppano tutta la linea(data,temp,etc..)
    for li in li_all:
        a = li.find_all('div', class_='col-xs-1-4 big zoom_prv')
        b = li.find_all('div', class_='col-xs-1-4 big')
        if a:
            #aggiungiamo le date in un dizionario con il rispettivo codice html, così possiamo estrapolarlo poi meglio 
            #utilizzando la data cone key del codice html.
            dizionario.update({a[0].get_text().strip(): li})
        if b:
            dizionario.update({b[0].get_text().strip(): li})
    estrapola = dizionario.get(ora)
    try :
        #ritorniamo il testo della temperatura contenuto nello span 
        ritono = estrapola.find('span', class_='switchcelsius switch-te active' ).get_text()
        return ritono
    except AttributeError:
        print ("Scegliere un orario nel futuro")
        


print (get_temp('19:00'))