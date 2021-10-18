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
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

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
    print ('Data Frames pending transmission: ',iii)

def fun_contstatus():
    iiii = 0
    letra = 0
    sta = {}
    q5 = cursor.execute("SELECT * FROM Datos WHERE Estatus_V = 0")
    for data in q5.fetchall():
        iiii += 1
    return (iiii)
    print ('Status Frames pending transmission: ',iiii)

#web platform access routes
subprocess.call('sudo /home/pi/wittyPi/syncTime.sh', shell=True)
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
    Statusamplingtime = dat2['Statusamplingtime']
    NSIM = int(dat2['nsim'])
    print("cg: ",cg)
    print("LimiteStatus: ",Statusamplingtime)
    print("SIM: ",NSIM)

# Database
conn = sqlite3.connect("/home/pi/Transmite/Datos_sensores.db")
conn2 = sqlite3.connect("/var/lib/weewx/weewx.sdb")
cursor = conn.cursor()
api_url_streams = "https://"+url_streams
api_url_status = "https://"+url_status
device = devicename+sufijo 
api_key = apikey 

cursor.execute("CREATE TABLE IF NOT EXISTS Datos"
"(Fecha TEXT,"+
"Precipitación_db     REAL,"+
"IntensidadP_db    REAL,"+
"Patmosferica_db   REAL   ,"+
"Temp_db    REAL   ,"+
"Hrelativa_db   REAL   ,"+
"Vviento_db      REAL   ,"+
"Vdir_db     REAL   ,"+
"Tinterior_db  REAL   ,"+
"Hinterior_db  REAL   ,"+
"Hsuelo1_db   REAL   ,"+
"Hsuelo2_db     REAL   ,"+
"Estado_V NUMERIC   ,"+
"Estatus_V NUMERIC) ")
cursor = conn.cursor()
cursor2 = conn2.cursor()
################################################################################################################################################################################ 

# Data measurement and calibration
i = 0
 while i < 10:
    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)
     # Create the ADC object using the I2C bus
    ads = ADS.ADS1015(i2c)
    # Create single-ended input on channel 0
    chan = AnalogIn(ads, ADS.P1)
    Shumedad_1 = 7*10**(-8)*chan.value**2 + 0.0007*chan.value + 3.6074
    if i == 0:
        humedad_1Med = Shumedad_1
        humedad_1Med = humedad_1Med +(Shumedad_1 - humedad_1Med)/10
    else:
        humedad_1Med = humedad_1Med +(Shumedad_1 - humedad_1Med)/10
    i = i+1
    time.sleep(0.1)
i = 0
while i < 10:
    chan = AnalogIn(ads, ADS.P2)
    Shumedad_2 = 7*10**(-8)*chan.value**2 + 0.0007*chan.value + 3.6074
    if i == 0:
        humedad_2Med = Shumedad_2
        humedad_2Med = humedad_2Med +(Shumedad_2 - humedad_2Med)/10
    else:
        humedad_2Med = humedad_2Med +(Shumedad_2 - humedad_2Med)/10
    i = i+1
    time.sleep(0.1)
#Batery status
i = 0
while i < 10:
    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)
    # Create the ADC object using the I2C bus
    ads = ADS.ADS1015(i2c)
    # Create single-ended input on channel 0
     chan = AnalogIn(ads, ADS.P3)
    Batery = (0.0277*chan.value) - 598.53
    if i == 0:
        Batery_Med = Batery
        Batery_Med = Batery_Med +(Batery - Batery_Med)/10
    else:
        Batery_Med = Batery_Med +(Batery - Batery_Med)/10
    i = i+1
    time.sleep(0.1)
           
try:
    q3 = cursor2.execute("SELECT * FROM archive")
    for data6 in q3.fetchall():
        Patmosferica_co = data6[3]
        Tinterior_co = data6[6]
        Temp_co = data6[7]
        Hinterior_co = data6[8]
        Hrelativa_co = data6[9]
        Vviento_co = data6[10]
        Vdir_co = data6[11]
        IntensidadP_co = data6[14]
        Precipitacíon_co = data6[15]
except:
    Print('error: no data')
Estado_V = 0 
Estatus_V = 0
if humedad_1Med < 3.73:
    humedad_1V = 0
else:
    humedad_1V = humedad_1Med
if humedad_2Med < 3.73:
    humedad_2V = 0
else:
    humedad_2V = humedad_2Med
if Patmosferica_co == None:
    Patmosferica_V = "null"
else:
    Patmosferica_V = (Patmosferica_co / 0.02953)
if Tinterior_co == None:
    Tinterior_V = "null"
else:   
    Tinterior_V = (Tinterior_co -32)*5/9
if Temp_co == None:
    Temp_V = "null"
else:       
    Temp_V = (Temp_co -32)*5/9
if Vviento_co == None:
    Vviento_V = "null"
else:      
    Vviento_V = (Vviento_co/3600)*1609.34
if IntensidadP_co == None:
    IntensidadP_V = "null"
else:     
    IntensidadP_V = (IntensidadP_co * 25.4)
    
if Precipitacíon_co == None:
    Precipitacíon_V = "null"
    Precipitacíon_V1 = 0
else:  
    Precipitacíon_V = (float(Precipitacíon_co) * 25.4)
    Precipitacíon_V1 = (float(Precipitacíon_co) * 25.4)

cursor = conn.cursor()
#Data logging
try:   
    cursor.execute("INSERT INTO Datos VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
        time.strftime("%Y-%m-%dT%H:%M:%S"),
        Precipitacíon_V,
        IntensidadP_V,
        Patmosferica_V,
        Temp_V,
        Hrelativa_co,
        Vviento_V,
        Vdir_co,
        Tinterior_V,
        Hinterior_co,
        humedad_1V,
        humedad_2V,  
        Estado_V,
        Estatus_V)# indicator variable: 0 = data not transmitted to web platform; 1 = data transmitted
        )
    #print data
    print("data uploaded successfully")
    q = cursor.execute("SELECT * FROM Datos")
    for data in q.fetchall():
        print (" fecha: ",data[0], "Estado: ",data[12])
    conn.commit()
except sqlite3.OperationalError as error:
    print("data loading error:", error)            
################################################################################################################################################################################    
#serch do not transmitted data 
def fun_cont_pre():
    ii = 0
    letra = {}
    pre = {}
    q = cursor.execute("SELECT * FROM Datos WHERE Estado_V= 0 Limit 0,30")
    for data in q.fetchall():
        letra[ii+1] = {"date":data [0],
                        "Precipitacion": data [1],
                        "IntensidadP": data [2],
                        "Patmosferica": data [3],
                        "Temp": data [4],
                        "Hrelativa": data [5],
                        "Vviento": data [6],
                        "Vdir": data [7],
                        "Tinterior": data [8],
                        "Hinterior": data [9],
                        "Hsuelo_1": data [10],
                        "Hsuelo_2": data [11]                       
                    }
        ii += 1
            
    return (letra)
################################################################################################################################################
# Data transmition

q2 = cursor.execute("SELECT * FROM Datos WHERE Estado_V = 0 Limit 0,30")#limitamos el numero de tramas ha enviar
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
    #json Data frame transmition 
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

################################################################################################################################################################################
# Status frame
  
if fun_contstatus() >= int(Statusamplingtime):
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
                    "Bateria_porc"  : Batery_Med,
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
                            "Bateria_porc"  : Batery_Med,
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
                            "Bateria_porc"  : Batery_Med,
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
                    muestreo = dat2['muestreo']
                    print("muestreo: ",muestreo)
                    subprocess.call('sudo tail  /home/pi/Transmite/tiempos/'+muestreo+' > /home/pi/wittyPi/schedule.wpi', shell=True)
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
                            "Bateria_porc"  : Batery_Med,
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
                            "Bateria_porc"  : Batery_Med,
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
                    muestreo = dat2['muestreo']
                    print("muestreo: ",muestreo)
                    subprocess.call('sudo tail  /home/pi/Transmite/tiempos/'+muestreo+' > /home/pi/wittyPi/schedule.wpi', shell=True)
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
                muestreo = dat2['muestreo']
                print("muestreo: ",muestreo)
                subprocess.call('sudo tail  /home/pi/Transmite/tiempos/'+muestreo+' > /home/pi/wittyPi/schedule.wpi', shell=True)
                subprocess.call('sudo /home/pi/wittyPi/runScript.sh', shell=True)
            ##########################################
    except:
        print("There is an error in the update values ​​try again later")    
################################################################################################################################################################################

conn.commit()
cursor.close()
conn.close()
