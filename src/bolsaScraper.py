# -*- coding: utf-8 -*f
import requests
import csv
import mechanize
from bs4 import BeautifulSoup

class BolsaScraper():
    
    def __init__(self):
        # Definim l'url basica de la web
        self.path = 'http://www.bolsamadrid.es'
        
    # TODO - cercar l'empresa desitjada
#      - poder paginar les dades de les diferents dates
    def trobarEmpresa(self, nomEmpresa):
        """
        Aquesta funció retorna el path final de l'empresa que busquem
        """
        url = self.path + "/esp/aspx/Empresas/Empresas.aspx"
        
        headers = {
                'Accept': 'text/html,application/xhtml+xml, \
                application/xml;q=0.9,*/*;q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'http://www.bolsamadrid.es',
                'Accept-Encoding': 'gzip, deflate',
                'Upgrade-Insecure-Requests': '1',
                'Host': 'www.bolsamadrid.es',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) \
                AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.2 \
                Safari/605.1.15',
                'Accept-Language': 'es-es',
                'Connection': 'keep-alive'
                }
        
        page = 0
        
        linkEmp = ''
        
        # This loop run the all pages in a table until find the page that 
        # contain the name of entity 
        while not linkEmp:
            # This data is use to do a post requests and contain the table page
           data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': 'ELOG9j+dXlB0neVne96qoQt5YBD99TrZEhhPUlG2uUo1xqC3cym00LyqoRQoi8x0RzaWp7RCOsxDjW3KsByfdG9p8VkpQGQaFjJGdNLbKjGy3H8jqKwTRvW/hDQPsv3aDesfZAxZHi3QO89pBa1Kr9diSmSxfx7PBYisYbL74FTK3gWFDcwXe/pkaTj34dUzsoLi7g==',
                '__VIEWSTATEGENERATOR': '65A1DED9',
                '__EVENTVALIDATION': '74YPg3B3Klx410ErZzrI+oUgqOATLDvnA/jY9wSgYwwIVARtwCmEEfVHIgrrd/7qdwqFGaen89VfmYLafxEGEwc5TeJDIkKP9Il8ZpD002wYxJgmruY/YdpYGmiey3RQFegiFLG0vgY/dZH9ObURK+wLPzhz7nTNRuQOdaaC9TgQX8oH51Layu04bs4EvFmtZF4gzDIRcYEba88DVy8pzykMaxB5cT353XUYf47IPnNFdXHC',
                'ctl00$Contenido$GoPag': str(page)
                }
           # Post request to a url using header and data defined before
           response = requests.post(url, headers=headers, data=data)
           # Create soup with the html response from page
           soup = BeautifulSoup(response.content, 'html.parser')
           # Find links in the page
           links = soup.find_all('a')
           # This loop find link that contain the name of company and return the
           # page that contain information about this
           for link in links:
               if nomEmpresa in link.text:
                   linkEmp = link.attrs['href']
           # This if control that the while are not infinite in case that not
           # find any match with the name (Only read the all page of the table)
           if page > 7:
               print("No se encuentra la empresa")
               break
           page = page + 1
           
           
           # Define dict to change part of url to goes directly to page that
           # contain data 
           urlchange = {
                   "FichaValor": "InfHistorica"
                   }
           for word, info in urlchange.items():
               linkEmp = linkEmp.replace(word, info)
                
        return linkEmp
        
    def dadesEmpresa(self, lastUrl):
        """
        Retorna les dades de l'empresa seleccionada
        """
        
        # Set vars with fixed values to future improve from data user in command line
        start_day = '2'
        start_month = '4'
        start_year = '2019'
        finish_day = '2'
        finish_month = '8'
        finish_year = '2019'       

        br = mechanize.Browser()

        # Loads webpage -- Serà variable vindrà donada per la funció anterior
        
        url = self.path + lastUrl

        # Opens url and selects date form
        br.open(url)
        br.select_form(nr=1)

        # Introduces data required to form and submit it
        br['ctl00$Contenido$Desde$Dia'] = start_day
        br['ctl00$Contenido$Desde$Mes'] = start_month
        br['ctl00$Contenido$Desde$Año'] = start_year
        br['ctl00$Contenido$Hasta$Dia'] = finish_day
        br['ctl00$Contenido$Hasta$Mes'] = finish_month
        br['ctl00$Contenido$Hasta$Año'] = finish_year

        # Checks parameters in form
        # print(br.form)

        # Submits form
        response = br.submit()
        
        soup = BeautifulSoup(response.read(), 'html.parser')
        
        # Reads data
        taula = soup.find(id="ctl00_Contenido_tblDatos")
        
        # Ticker
        ticker = [soup.find(class_= 'FrmBusq').find_all('td')[10].string.strip()]
        
        # Company name
        self.company = [soup.find(class_= 'FrmBusq').find_all('td')[8].string.strip()]
        
        # Heading row
        self.first_row = [title.string for title in taula.find_all('th')]
        
        # Other rows
        self.content = [[element.string for element in row.find_all('td')] for row in taula.find_all('tr')[1:]]
        
        
        self.data2csv(ticker[0])
            
    def data2csv(self, filename):
        with open("../data/"+filename+'.csv', "w+", newline='') as csvfile:
            bolsa_writer = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            bolsa_writer.writerow(self.company)
            bolsa_writer.writerow(self.first_row)
            bolsa_writer.writerows(self.content)
        

def main():
    
    # Aquest codi és el que anira finalment al main
    bolsa = BolsaScraper()
    
    # Find url with the name of the company
    url = bolsa.trobarEmpresa("BANCO BRADESCO S.A.")
    
    # Find and save data from a company defined before
    bolsa.dadesEmpresa(url)
    
if __name__ == "__main__":
    main()
    
















