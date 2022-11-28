import sqlite3
import matplotlib.pyplot as plt
#import matplotlib.colors as mcolors
#import matplotlib.tri as tri
import pandas as pd
import json
import raw
#import numpy as np
#import random



fields = ['name', 'grade', 'resistance', 'crux', 'country', 'area', 'comment', 'ishard', 'issoft',]

def main():
    d = Databaser()
    graph = Graph(d.get_data())
    user = input("Username: ")
    sneak = Sneaky(user, d)
    if input("Do you want to add your logbook to the database? (y) ") == "y":
        sneak.add_logged()
    if input("Do you want to update your logged climbs? (y) ") == "y":
        print("Press Ctr-C to exit update mode.\n\n")
        while True:
            try:
                for i in d.get_data(valid=0):
                    i.update_invalid()
                    d.update(i)
                break
            except KeyboardInterrupt:
                print("Stopping update mode, update more next time")
                break
    else:
        while True:
            r = input("New Entry? (y/n): ")
            if r == "n":
                break
            elif r =="y":
                new_route = Route(Route.collect())
                d.db_add(new_route)
            else: 
                continue
    graph = Graph(d.get_data())
    
    d.conn.close()




class Route():
    def __init__(self, name, grade, resistance=0, crux=0):
        try:
            self.name = name
            self.grade = grade
            self.resistance = resistance
            self.crux = crux
        except:
            print("No valid data")
            self.collect_new()

    def __str__(self):
        return f"{self.name}, {self.grade}"
    
    def collect_new(self):
        form = {}
        print("Collecting data...")
        while True:
            self.name = input("Route Name: ")
            try:
                self.grade = int(input("Route Grade (AUS): "))
                self.resistance = int(input("Route Resistance (1-10): "))
                self.crux = int(input("Boulder difficulty of route crux (V grades): "))
            except TypeError:
                print("Enter values in correct formats")
            break

    def update_invalid(self):
        print(f"Update {self.name}, Grade: {self.grade}.")
        while True:
            try:
                self.resistance = int(input("Route Resistance (1-10): "))
                self.crux = int(input("Boulder difficulty of route crux (V grades): "))
                break
            except TypeError:
                print("Numeric Values")
        
        


class Sneaky():
    def __init__(self, user, db):
        self.user = user
        self.db = db

    def get_logged(self, user):
        username = self.user.strip().replace(" ", "-")
        url = f"https://www.8a.nu/api/users/{username}/ascents?category=sportclimbing&pageIndex=0&pageSize=50&sortField=grade_desc&timeFilter=0&gradeFilter=0&typeFilter=&isAscented=true&searchQuery=&showRepeats=false"
        response = requests.get(url)
        return response.json

    def add_logged(self):
        data = json.loads(raw.raw)#get_logged())
        for i in data['ascents']:
            new = Route(name= i['zlaggableName'], grade=i['zlagGradeIndex'])
            self.db.db_add(new)
            #r = Route(
                #form['name'] = i['zlaggableName'], 
                #grade=i['zlagGradeIndex'], 
                #country=i['countryName'], 
                #area=i['cragName'], 
                #comment=i['comment'],
                #issoft=i['issoft'],
                #ishard=i['ishard'],                )



class Databaser():
    def __init__(self):
        self.conn = sqlite3.connect("grades.db")
        self.db = self.conn.cursor()
        self.create_tables()

    def db_add(self, route):
        self.db.execute("INSERT INTO routes (name, grade, resistance, crux) VALUES (?, ?, ?, ?)",
        (route.name, route.grade, route.resistance, route.crux),)
        print(f"Saving {route} ...")
        self.conn.commit()

    def get_data(self, valid=1):
        if valid:
            results = self.db.execute("SELECT route_id, name, grade, resistance, crux FROM routes WHERE crux > 0 AND resistance > 0 ORDER BY grade").fetchall()
        else: 
            results = self.db.execute("SELECT route_id, name, grade, resistance, crux FROM routes WHERE crux = 0 AND resistance = 0").fetchall()
        data = [] #{}
        for result in results:

            id, name, grade, resistance, crux = result
            data.append(Route(name, grade, resistance, crux))
            #data[id] = {'name': name, 'grade': grade, 'resistance': resistance, 'crux': crux,}
        return data

    def update(self, route):
        self.db.execute("UPDATE routes SET resistance = ?, crux = ? WHERE name = ?", (route.resistance, route.crux, route.name),)
        print(f"Updating {route} resistance to {route.resistance}, crux to {route.crux}.")
        self.conn.commit()

    def create_tables(self):
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS routes (route_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name TEXT NOT NULL, grade INTEGER NOT NULL, resistance INTEGER, crux INTEGER)"
        )


class Graph():
    color_names = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w',]
    colors = {40:'b', 39:'g', 38:'r', 37:'c', 36:'m', 35:'y', 34:'k', 33:'b', 32:'g', 31:'r', 30:'c', 29:'m', 28:'y', 27:'k',}

    #for grade in range(40):
        #colors[grade] = random.choice(color_names)
    def __init__(self, data): 
        print("Compiling graph...")
        x = []
        y = []
        z = []
        for route in data:
            x.append(route.resistance)
            y.append(route.crux)
            z.append(route.grade)
        df = pd.DataFrame(
            {
                'x':x,
                'y':y,
                'z':z,

            }
        )
        
        grades = df.groupby('z')
        for name, group in grades:
            plt.plot(group.x, group.y, marker="o", linestyle="", markersize=12, label=name)
            
        #plt.scatter(df.x, df.y, s=100, c=df.z, cmap='hsv')

        """for route in data:
            plt.scatter(
                route.resistance, 
                route.crux, 
                s=100,
                c=route.grade,
                cmap='hsv',
                #color=self.colors[route.grade],
                label=route.grade,
                )"""
            

        plt.xlabel("Resistance")
        plt.ylabel("Crux difficulty")
        plt.title("Technical difficulty vs Resistance")
        plt.legend()
        plt.show()



    



if __name__=="__main__":
    main()