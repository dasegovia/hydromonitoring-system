#!/usr/bin/python3

# Import libraries
import http.client
import urllib.request
import urllib.parse
import json
import sqlite3
from ast import literal_eval
import time
import subprocess
import Adafruit_DHT
import datetime
import RPi.GPIO as GPIO

#variable definition
sensor = Adafruit_DHT.DHT22
GPIO.setmode(GPIO.BCM)
trig = 17
echo = 27
pin = 22
iterar = 50

#Status frame functions 
def get_ram_total():
    san = subprocess.check_output('df -h',shell=True)
    lines = san.split()
    lines2 = str(lines [8])
    lines3 = lines2.replace("b", " ") 
    return (lines3)

def get_ram_usada():
    san = subprocess.check_output('df -h',shell=True)
    lines = san.split()
    lines2 = str(lines [9])
    lines3 = lines2.replace("b", " ")
    return (lines3)

def get_ram_libre():
    san = subprocess.check_output('df -h',shell=True)
    lines = san.split()
    lines2 = str(lines [10])
    lines3 = lines2.replace("b", " ")
    return (lines3)

def get_red():
    san = subprocess.check_output('ping -c 2 www.altairsmartworks.com',shell=True)
    lines = san.split()
    lines2 = str(lines [8])
    lines3 = lines2.replace("b", " ")
    return (san)
 
def fun_cont():
    iii = 0
    letra = 0
    pre = {}
    q4 = cursor.execute("SELECT * FROM Datos WHERE Estado_V = 0")
    for data in q4.fetchall():
        iii += 1
    return (iii)
    print ('Total transacciones: ',iii)

def fun_contstatus():
    iiii = 0
    letra = 0
    sta = {}
    q5 = cursor.execute("SELECT * FROM Datos WHERE Estatus_V = 0")
    for data in q5.fetchall():
        iiii += 1
    return (iiii)
    print ('Trams pendientes status: ',iiii)

#web platform access routes
subprocess.call('sudo /home/pi/wittyPi/syncTime.sh', shell=True) # WittyPi synchronization
with open("/home/pi/Transmite/cc.txt") as f:
  raw_data = f.read()
data = json.loads(raw_data)
print (data)
for dat in data:
    cc = dat['cc']
    sufijo =dat['sufijo']
    capikey =dat['capikey']
    apikey =dat['apikey']
    devicelog =dat['devicelog']
    url_streams =dat['url_streams']
    url_status = dat['url_status']
    url_cc = dat['url_cc']
    url_cg = dat['url_cg']
    print("cc:", cc)
    print("sufijo: ",sufijo)
    print("capikey: ",capikey)
    print("apikey: ",apikey)
    print("devicelog: ",devicelog)
    print("url_streams: ",url_streams)
    print("url_cc: ",url_cc)
    print("url_cg: ",url_cg)

with open("/home/pi/Transmite/cg.txt") as f2:
  raw_data2 = f2.read()
data2 = json.loads(raw_data2)
print (data2)
for dat2 in data2:
    cg = dat2['cg']
    frameslimit = dat2['frameslimit']
    NSIM = int(dat2['nsim'])

    print("cg: ",cg)
    print("LimiteStatus: ",frameslimit)
    print("SIM: ",NSIM)

# Database 
conn = sqlite3.connect("/home/pi/Transmite/Datos_sensores.db")
cursor = conn.cursor()
api_url_streams = "https://"+url_streams 
api_url_status = "https://"+url_status
device = devicename+sufijo 
api_key = apikey 

cursor.execute("CREATE TABLE IF NOT EXISTS Datos"
               "(Fecha TEXT,"+
               "Temperatura_db REAL, "+
               "Humedad_db REAL, "+
               "Dlamina_db REAL, "+
               "Estado_V NUMERIC,
               "Estatus_V NUMERIC) "
               )
cursor = conn.cursor()
 #################################################################################################################

# Data measurement and calibration 

GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(pin, GPIO.IN)
humedad, temperatura = Adafruit_DHT.read_retry(sensor, pin)
soundSp = 330.26+(0.606*temperatura)+(0.0124*humedad) # m/s
i = 0
while i < iterar:
    GPIO.output(trig, False) 
    time.sleep(2*10**-6) 
    GPIO.output(trig, True) 
    time.sleep(10*10**-6) 
    GPIO.output(trig, False) 
    while GPIO.input(echo) == 0:
            start = time.time()
 
    while GPIO.input(echo) == 1:
             end = time.time()
    distance = ((((end-start)/2))*soundSp)*100
    if i == 0:
        distanceMed = distance
        distanceMed = distanceMed +(distance - distanceMed)/iterar
    else:
        distanceMed = distanceMed +(distance - distanceMed)/iterar
    i = i+1
    time.sleep(0.2)
Fecha = datetime.datetime.now()
print(Fecha)
print('Temperatura={0:0.1f}* Humedad={1:0.1f}%'.format(temperatura, humedad))
print(distanceMed)
print ('datos calado: ',fun_cont()) 
    
# Data logging
        
Fecha_V = Fecha 
Temperatura_V = temperatura 
Humedad_V = humedad
if distanceMed >= 365:
    Dlamina_V = 364
else:    
    Dlamina_V = distanceMed 
Estado_V = 0
Estatus_V = 0
print (fun_cont())
print (fun_contstatus())
cursor = conn.cursor()
try:
    cursor.execute("INSERT INTO Datos VALUES (?,?,?,?,?,?)",(
        time.strftime("%Y-%m-%dT%H:%M:%S"),
        Temperatura_V,
        Humedad_V,
        Dlamina_V,
        Estado_V,
        Estatus_V) # indicator variable: 0 = data not transmitted to web platform; 1 = data transmitted
        )
    #print data
    print("data uploaded successfully")
    q = cursor.execute("SELECT * FROM Datos")
    for data in q.fetchall():
        print (" fecha: ",data[0]," Estado: ",data[4])
    conn.commit()
except sqlite3.OperationalError as error:
    print("data loading error:", error)
###################################################################################################################
 #serch not transmitted data 
def fun_cont_pre():
ii = 0
letra = {}
pre = {}
q = cursor.execute("SELECT * FROM Datos WHERE Estado_V= 0 Limit 0,30")
for data in q.fetchall():
    letra[ii+1] = {"date":data [0],
                    "Temperatura":data [1],
                    "Humedad":data [2], 
                    "D_lamina":data [3]
                }
    ii += 1
        
return (letra)
################################################################################################################################################
# Data transmition

q2 = cursor.execute("SELECT * FROM Datos WHERE Estado_V = 0 Limit 0,30")
a = 0
for data in q2.fetchall():
    a += 1
    
print ('Total: ',a)
if a == 0:
    print("there is no data pending to be transmitted")
else:   
    params2 = fun_cont_pre()
    params = {"protocol": "v2",
            "checksum": "",
            "device": device,
            "at": "now",
            "data":params2
            }
    print (params)
    # json Data frame transmition 
    try:
        binary_data = json.dumps(params).encode('ascii')
        header = {"Apikey": api_key}
        req = urllib.request.Request(api_url_streams, binary_data, header)
        f = urllib.request.urlopen(req)
        d = json.loads(f.read().decode('utf-8'))
        print (d['response'])
        if d['response']=="OK":
            #update indicator variable
            sentencia = "UPDATE Datos SET Estado_V = 1 WHERE Estado_V = 0 Limit 0,30;"
            cursor.execute(sentencia)
            conn.commit()
            print("successfull data transmition")
    except:
        print("There is an error in the data transmission, try again later")
conn.commit() 
###############################################################################################################################################################################
# Status frame

if fun_contstatus() >= int(frameslimit):
    params = {"protocol": "v2",
                "checksum": "",
                "device": device,
                "at": "now",
                "data": {
                    "date":time.strftime("%Y-%m-%dT%H:%M:%S") ,
                    "cc": cc,
                    "cg": cg,
                    "memoria_tot": get_ram_total(),
                    "memoria_uso": get_ram_usada(),
                    "memoria_lib": get_ram_libre(),
                    "red": str(get_red()),
                    "Bateria_%"  : 99,
                    "tramas_pen":  fun_cont(),
                    "SIM":   NSIM
                    }
                }
    #updating configuration files

    try:
        binary_data = json.dumps(params).encode('ascii')
        header = {capikey : api_key}
        req = urllib.request.Request(api_url_status, binary_data, header)
        f = urllib.request.urlopen(req)
        d = json.loads(f.read().decode('utf-8'))
        print (d['response'])
        print("data uploaded successfully")
        sentencia1 = "UPDATE Datos SET Estatus_V = 1 WHERE Estatus_V = 0;"
        cursor.execute(sentencia1)
        if d['response']=="10":
            print("updating cc file")
            params = {"protocol": "v2",
                        "checksum": "",
                        "device": device,
                        "at": "now",
                        "data": {
                            "date":time.strftime("%Y-%m-%dT%H:%M:%S") ,
                            "cc": cc,
                            "cg": cg,
                            "memoria_tot": get_ram_total(),
                            "memoria_uso": get_ram_usada(),
                            "memoria_lib": get_ram_libre(),
                            "red": str(get_red()),
                            "Bateria_%"  : 99,
                            "tramas_pen":  fun_cont(),
                            "SIM":   NSIM
                            }
                        }
            try:
                binary_data = json.dumps(params).encode('ascii')
                header = {"Apikey": api_key}
                req = urllib.request.Request(url_cc, binary_data, header)
                f = urllib.request.urlopen(req)
                d = json.loads(f.read().decode('utf-8'))
                print (d['response'])
                print("data downloaded successfully")
                f = open ('/home/pi/Transmite/cc.txt','w')
                f.write(d['response'])
                f.close()
            except:
                print("data download error")
        ##############################################################################################        
        elif d['response']=="01":
            print("updating cg file")
            params = {"protocol": "v2",
                        "checksum": "",
                        "device": device,
                        "at": "now",
                        "data": {
                            "date":time.strftime("%Y-%m-%dT%H:%M:%S") ,
                            "cc": cc,
                            "cg": cg,
                            "memoria_tot": get_ram_total(),
                            "memoria_uso": get_ram_usada(),
                            "memoria_lib": get_ram_libre(),
                            "red": str(get_red()),
                            "Bateria_%"  : 99,
                            "tramas_pen":  fun_cont(),
                            "SIM":   NSIM
                            }
                        }
            try:
                binary_data = json.dumps(params).encode('ascii')
                header = {"Apikey": api_key}
                req = urllib.request.Request(url_cg, binary_data, header)
                f = urllib.request.urlopen(req)
                d = json.loads(f.read().decode('utf-8'))
                print (d['response'])
                print("data downloaded successfully")
                f = open ('/home/pi/Transmite/cg.txt','w')
                f.write(d['response'])
                f.close()
                with open("/home/pi/Transmite/cg.txt") as f2:
                    raw_data2 = f2.read()
                data2 = json.loads(raw_data2)
                print (data2)
                for dat2 in data2:
                    samplingtime = dat2['samplingtime']
                    print("samplingtime: ",samplingtime)
                    subprocess.call('sudo tail  /home/pi/Transmite/tiempos/'+samplingtime+' > /home/pi/wittyPi/schedule.wpi', shell=True)
                    subprocess.call('sudo /home/pi/wittyPi/runScript.sh', shell=True)
            except:
                print("data download error")
        ############################################################################################## 
        elif d['response']=="11":
            print("updating configuration files")
            print("updating cc file")
            params = {"protocol": "v2",
                        "checksum": "",
                        "device": device,
                        "at": "now",
                        "data": {
                            "date":time.strftime("%Y-%m-%dT%H:%M:%S") ,
                            "cc": cc,
                            "cg": cg,
                            "memoria_tot": get_ram_total(),
                            "memoria_uso": get_ram_usada(),
                            "memoria_lib": get_ram_libre(),
                            "red": str(get_red()),
                            "Bateria_%"  : 99,
                            "tramas_pen":  fun_cont(),
                            "SIM":   NSIM
                            }
                        }
            try:
                binary_data = json.dumps(params).encode('ascii')
                header = {"Apikey": api_key}
                req = urllib.request.Request(url_cc, binary_data, header)
                f = urllib.request.urlopen(req)
                d = json.loads(f.read().decode('utf-8'))
                print (d['response'])
                print("data downloaded successfully")
                f = open ('/home/pi/Transmite/cc.txt','w')
                f.write(d['response'])
                f.close()
            except:
                print("data download error")
        ##############################################################################################
            print("updating cg file")
            params1 = {"protocol": "v2",
                        "checksum": "",
                        "device": device,
                        "at": "now",
                        "data": {
                            "date":time.strftime("%Y-%m-%dT%H:%M:%S") ,
                            "cc": cc,
                            "cg": cg,
                            "memoria_tot": get_ram_total(),
                            "memoria_uso": get_ram_usada(),
                            "memoria_lib": get_ram_libre(),
                            "red": str(get_red()),
                            "Bateria_porc": 99,
                            "tramas_pen":  fun_cont(),
                            "SIM":   NSIM
                            }
                        } 
            try:
                binary_data1 = json.dumps(params1).encode('ascii')
                header1 = {"Apikey": api_key}
                req1 = urllib.request.Request(url_cg, binary_data1, header1)
                f1 = urllib.request.urlopen(req1)
                d1 = json.loads(f1.read().decode('utf-8'))
                print (d1['response'])
                print("data downloaded successfully")
                f = open ('/home/pi/Transmite/cg.txt','w')
                f.write(d['response'])
                f.close()
                with open("/home/pi/Transmite/cg.txt") as f2:
                    raw_data2 = f2.read()
                data2 = json.loads(raw_data2)
                print (data2)
                for dat2 in data2:
                    samplingtime = dat2['samplingtime']
                    print("samplingtime: ",samplingtime)
                    subprocess.call('sudo tail  /home/pi/Transmite/tiempos/'+samplingtime+' > /home/pi/wittyPi/schedule.wpi', shell=True)
                    subprocess.call('sudo /home/pi/wittyPi/runScript.sh', shell=True)
            except:
                print("data download error")
        ##############################################################################################
        else :
            print("Upgraded device")
            with open("/home/pi/Transmite/cg.txt") as f2:
                raw_data2 = f2.read()
            data2 = json.loads(raw_data2)
            print (data2)
            for dat2 in data2:
                samplingtime = dat2['samplingtime']
                print("samplingtime: ",samplingtime)
                subprocess.call('sudo tail  /home/pi/Transmite/tiempos/'+samplingtime+' > /home/pi/wittyPi/schedule.wpi', shell=True)
                subprocess.call('sudo /home/pi/wittyPi/runScript.sh', shell=True)
            ##########################################
    except:
        print("There is an error in the update values ​​try again later")
###############################################################################################################################################################################

conn.commit()
cursor.close()
conn.close()