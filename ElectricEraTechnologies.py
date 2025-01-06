#Nina Ervin
#1/3/2025
# Software Engineer (Entry Level), Electric Era Technologies
#https://gitlab.com/electric-era-public/coding-challenge-charger-uptime

#The code can be run by "python /fullpath/ElectricEraTechnologies.py /fullpath/filename"
#I made the assumption that for each station no charger report start time would be smaller than a past start time.
    #This is since I assume all reports are being sent in real time and to improve runtime effencey for large data.
    # if this assumption is wrong please let me know and I would be more than happy to correct my errors.
import argparse
import sys

# This method reads through the given file and returns
    #dict stations --> key: station number value: list of all charger id
    #list charger_data --> each report dict of charger id, start, end, and status (True, False)
def parceFile(fileName):
    stations = {}
    charger_data = []

    with open(fileName, 'r') as file:
        content = file.read()
    
    sections = content.split('\n\n')
    #print(sections)
    for section in sections:
        if section.startswith('[Stations]'):
            station_data = section
        elif section.startswith("[Charger Availability Reports]"):
            report_data = section


    for line in station_data.splitlines()[1:]:
        parts = line.split()
        if parts:
            stations[int(parts[0])] = list(map(int, parts[1:]))
    
    for line in report_data.splitlines()[1:]:
        parts = line.split()
        if parts:
            status = (parts[3] == 'true')
            charger_data.append({'charger':int(parts[0]), 'start':int(parts[1]), 'end':int(parts[2]), 'status':status})
    
    return stations, charger_data

#given station_data, charger_data from parceFile this method will return a dict containing each station which gave an update, min max time stamps
#and a list of all time entries where evens are starts and odds are ends.
def structure(station_data, charger_data):
    chargerToStation = {}
    stationHours = {}
    for station in station_data.keys():
        for charger in station_data[station]:
            chargerToStation[charger] = station
    
   
    for report in charger_data:
        if report['status'] == True:
            curr_station = chargerToStation[report['charger']]
            if curr_station in stationHours.keys():
                if stationHours[curr_station]['min'] > report['start']:
                    stationHours[curr_station]['min'] = report['start']
                if stationHours[curr_station]['max'] < report['end']:
                    stationHours[curr_station]['max'] = report['end']
                if stationHours[curr_station]['hours'][-1] >= report['start']: #making the assumption that start of a later report will never be before the start of a different report
                    stationHours[curr_station]['hours'][-1] = report['end']
                else:
                    stationHours[curr_station]['hours'].append(report['start'])
                    stationHours[curr_station]['hours'].append(report['end'])
            else:
                stationHours[curr_station] = {'report':True, 'min':report['start'], 'max':report['end'], 'hours':[report['start'], report['end']]}

        else:  #dealing with if it reports false (return 0) vs not reporting at all (return 100)
            curr_station = chargerToStation[report['charger']]
            if curr_station not in stationHours.keys():
                stationHours[curr_station] = {'report':True, 'min':float('inf'), 'max':float('-inf'), 'hours':[]}
        
    return stationHours

#for a given station this method with find the precent of time the station was up and print to the console the result  
def findPrecent(station, data):
    if data['min'] == float('inf') and data['max'] == float('-inf'):
        print(f'{station} 0')
    else:
        total_possible = data['max'] - data['min']
        working_total = 0
        curr_min = 0
        list = data['hours']
        for i in range(len(list)):
            if i % 2 == 0:
                curr_min = list[i]
            else:
                working_total += list[i] - curr_min
        final = int((working_total/total_possible)*100)
        print(f'{station} {final}')

def main():
    try:
        fileName = sys.argv[1]
        station_data, charger_data = parceFile(fileName)
        stationHours = structure(station_data, charger_data)
        for station in station_data.keys():
            if station not in stationHours.keys():
                print(f'{station} 100')
            findPrecent(station, stationHours[station])
    except Exception as e:
        print("ERROR")



if __name__ == "__main__":
    main()