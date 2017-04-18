import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from sqlite3 import Error


WijkenGebieden = {
                "Charlois":["Carnisse","Charlois","Heijplaat","Oud-Charlois","Pendrecht","Tarwewijk",
                              "Wielewaal","Zuiderpark en Zuidrand","Zuidplein","Zuidwijk"],
                "Delfshaven":["Bospolder","Delfshaven","Delfshaven","Middelland","Nieuwe Westen",
                             "OudMathenesse/Witte Dorp","Schiemond","Spangen","Tussendijken"],
                "Feijenoord":["Afrikaanderwijk","Bloemhof", "Feijenoord","Hillesluis","Katendrecht",
                              "Kop van Zuid",	"Kop van Zuid-Entrepot","Noordereiland", "Vreewijk"],
                "Hillegersberg-Schiebroek": ["Hillegersberg-noord",	"Hillegersberg-Schiebroek",
                                             "Hillegersberg-zuid", "Molenlaankwartier", "Schiebroek", "Terbregge"],
                "Hoek van Holland":	["Dorp/Rijnpoort", "Hoek van Holland", "Strand en duin"],

                "Hoogvliet" : ["Hoogvliet",	"Hoogvliet-noord",	"Hoogvliet-zuid"],

                "IJsselmonde" : ["Beverwaard","Groot IJsselmonde-Noord","Groot IJsselmonde-Zuid","IJsselmonde",
                                 "Lombardijen", "Oud IJsselmonde"],
                "Kralingen-Crooswijk" : ["De Esch", "Kralingen Oost/Kralingse Bos", "Kralingen-Crooswijk",
                                         "Kralingen-west","Nieuw Crooswijk","Oud Crooswijk","Rubroek","Struisenburg"],
                "Noord"	: ["Agniesebuurt",	"Bergpolder", "Blijdorp/Blijdorpsepolder", "Liskwartier	Noord",
                                            "Oude Noorden",	"Provenierswijk"],
                "Overschie" :  ["Kleinpolder", "NoordKethel/Schieveen/Zestienhoven", "Overschie"],

                "Pernis" : ["Pernis"],

                "Prins Alexander" :	["Het Lage Land", "Kralingseveer","Nesselande",	"Ommoord",	"Oosterflank",
                                        "Prins Alexander",	"Prinsenland",	"s-Gravenland",	"Zevenkamp"],
                "Rotterdam" : ["Rotterdam"],

                "Rotterdam Centrum" : ["Cool","CS-kwartier", "Nieuwe Werk/Dijkzigt","Oude Westen","Rotterdam Centrum", "Stadsdriehoek"],

                "Rozenburg" : ["Rozenburg"]

                }

ab = "Kralingen Oost/"
def search(values, searchFor):
    for k in values:
        for v in values[k]:
            if searchFor in v:
                return k
    return None

# print(search(WijkenGebieden, ab))


jaarTabelNamen = ["tevredenheid", "fietsendiefstal", "geweldsdelicten","drugsoverlast"]
afkomstTabelNamen = ['Nederlanders', 'Marokkanen', 'Turken', 'Kaapverdianen', 'Antilianen', 'Surinamers', 'Zuid-Europeanen', 'Overig']

class Plot:
    def __init__(self, tabelnaam, wijknamenlist, kolomstring):
        self.databaseFile = "Database\StekOverflow.db"
        self.tabelNaam = tabelnaam
        self.wijkNamenList = wijknamenlist
        self.kolomstring = kolomstring
        self.conn = self.create_connection(self.databaseFile)
        self.cur = self.conn.cursor()

    def create_connection(self,db):
        try:
            conn = sqlite3.connect(db)
            return conn
        except Error as e:
            print(e)
        return None

class PlotLineChart(Plot):
    def __init__(self, tabelnaam, wijknamenlist, kolomstring):
        super().__init__(tabelnaam, wijknamenlist, kolomstring)
        self.y = []
        self.jaartallen = [2006, 2007, 2008, 2009, 2011]
        self.g = globals()

        self.generate_empty_lists()
        self.sql_query_linechart()
        self.show_plot()

    def generate_empty_lists(self):
        for wijk in (self.wijkNamenList):
            self.g['data_{}'.format(wijk.name)] = []

    def sql_query_linechart(self):
        for wijk in (self.wijkNamenList):
            self.cur.execute("select data2006,data2007,data2008,data2009,data2011 from"
                             " {} where wijknaam LIKE '{}'".format(self.tabelNaam, wijk.name))
            self.wijkData = self.cur.fetchone()
            for i in range(len(self.wijkData)):
                self.g['data_{}'.format(wijk.name)].append(self.wijkData[i])

    def show_plot(self):
        for wijk in (self.wijkNamenList):
            p = plt.plot(self.jaartallen, self.g['data_{}'.format(wijk.name)], label=wijk.name, linewidth=1)
            for a, b in zip(self.jaartallen, self.g['data_{}'.format(wijk.name)]):
                plt.text(a, b, str(b))
            wijk.ChangeBorderColor(p[0].get_color())
        plt.ylabel("Percentage")
        plt.xlabel('Jaren')
        plt.title(self.kolomstring)
        plt.legend(loc='best', fancybox=True, framealpha=0.5)
        plt.show()


class PlotBarChart(Plot):
    def __init__(self,tabelnaam, dataset, wijknamenlist, kolomstring):
        self.dataSet = dataset
        super().__init__(tabelnaam,wijknamenlist, kolomstring)
        self.data = []
        self.overigeTabelNamen = ["fiobj2016", "fisub2016", "si2016", "vi2016"]
        self.xlabels = []

        self.sql_query_barchart()
        self.show_plot()

    def sql_query_barchart(self):
        for wijk in (self.wijkNamenList):
            self.cur.execute("select {} from {} where wijknaam = '{}'".format(self.dataSet, self.tabelNaam, wijk.name))
            b = self.cur.fetchone()
            self.xlabels.append(wijk.name)
            self.data.append(b[0])

    def show_plot(self):
        y_pos = np.arange(len(self.wijkNamenList))

        plt.bar(y_pos, self.data, align='center', alpha=0.5)
        for a, b in zip(y_pos, self.data):
            plt.text(a, b, str(b))


        plt.xticks(y_pos,self.xlabels, wrap = True)
        plt.ylabel('Cijfer')
        plt.title(self.kolomstring)

        plt.show()

class PlotOnMap(Plot):
    def __init__(self, tabelnaam, wijknamenlist,kolomstring):
        super().__init__(tabelnaam, wijknamenlist, kolomstring)
        self.y = []
        self.jaartallen = [2006, 2007, 2008, 2009, 2011]
        self.g = globals()

        self.generate_empty_lists()
        self.sql_query_linechart()
        self.show_plot()

    def generate_empty_lists(self):
        for wijk in (self.wijkNamenList):
            self.g['data_{}'.format(wijk.name)] = []

    def sql_query_linechart(self):
        for wijk in (self.wijkNamenList):
            self.cur.execute("select data2011 from"
                             " {} where wijknaam LIKE '{}'".format(self.tabelNaam, wijk.name))
            self.wijkData = self.cur.fetchone()
            for i in range(len(self.wijkData)):
                self.g['data_{}'.format(wijk.name)].append(self.wijkData[i])

    def show_plot(self):
        for wijk in (self.wijkNamenList):
            print(self.g['data_{}'.format(wijk.name)])
            b = (self.g['data_{}'.format(wijk.name)])
            wijk.ChangeColor(int(b[0]))

# t = ["Oud/Nieuw Mathenesse/Witte Dorp"]
# PlotLineChart("geweldsdelicten", t)

#
# PlotBarChart("fiobj2016", "fysiekeindex", t)




