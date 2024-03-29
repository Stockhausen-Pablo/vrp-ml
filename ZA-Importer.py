from src.Utils.helper import calculate_tour_meta
import json


class SimpleStop(object):
    longitude = 0.0
    latitude = 0.0
    tourStopId = 0

    def __init__(self, longitude, latitude, tourStopId):
        self.longitude = longitude
        self.latitude = latitude
        self.tourStopId = tourStopId


def make_simple_stop(longitude, latitude, tourStopId):
    stop = SimpleStop(longitude, latitude, tourStopId)
    return stop


print("---------Importing mode menu---------")
print("-Specification of the file name-")
print("-The relevant data are located in the folder data/constructed_tours_by_za-")
data_set = input("Please enter the name of the file:") or '2021_05_04_za_tours'
vehicle_speed = int(input("How fast is the vehicle [km/h]: ") or 30)
stay_duration = int(input("How long is the stay duration per Stop: ") or 5)

# --------------------
# SET MICROHUB AS FIRST STOP
# Defined longitude/latitude manually
microhub = make_simple_stop(13.3069357, 52.5013048, 0)

print("Trying to open the file...")
with open('data/constructed_tours_by_za/' + data_set + '.json', 'r') as file:
    print("Successfully opened the file...")
    za_tours = json.load(file)
    all_tours = []
    stop_counter = 0

    # --------------------
    # IMPORT TOUR-DATA FROM ZA-SYSTEM
    for za_tour in za_tours:
        tour = []
        for stop in za_tour.get('stops'):
            stop_counter += 1
            # stopIdentifier,stopNr,Longitude,Latitude,DemandWeight,DemandVolume,BoxAmount
            current_stop = make_simple_stop(stop.get('address').get('longitude'), stop.get('address').get('latitude'), stop.get('tourStopId'))
            tour.append(current_stop)
        all_tours.append(tour)
        tour = []

    for tour in all_tours:
        tour.insert(0, microhub)
        tour.append(microhub)

    stop_counter += 1

    # --------------------
    # CALCULATE TOUR-META FOR ZA-SOLUTION
    total_time, total_distance, average_time_per_tour, average_distance_per_tour = calculate_tour_meta(
        vehicle_speed, stay_duration, all_tours)
    for tour in all_tours:
        for stop in tour:
            print(stop.tourStopId)
    print("Overall distance: ", total_distance)
    print("Mean Distance per Tour: ", average_distance_per_tour)
    print("Overall Time needed: ", total_time)
    print("Average Time needed per Tour: ", average_time_per_tour)
    print("Stop amount: ", stop_counter)
