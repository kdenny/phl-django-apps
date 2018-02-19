import googlemaps
from pprint import pprint
import csv

### Overall goal of this script is to geocode a city (get it's latitude and longitude) in an efficient way, by ensuring that a city is never looked up twice (since Google Maps API is limited to 2500 calls / day)


gmaps = googlemaps.Client(key='AIzaSyDpKvFMXT-PBZC0vzAn3DafRFemNuwUPHM')

# Geocoding an address

### Row contains city, region and country
def geocode(row):
    out = None

    ### Sloppy way of handling unicode characters
    if row['city']:
        city = row['city'].encode('utf-8')
        if row['region']:
            region = row['region'].encode('utf-8')
        else:
            # If region is null, set to a blank string
            region = ''
        country = row['country'].encode('utf-8')
        dupe = False
        out = {}

        ## Check to see if current city exists in geocode results file
        with open("/Users/kevindenny/Documents/automated-reports/dj_app/bq_api/cities_geocoding_results.csv", 'r') as tf:
            rd = csv.DictReader(tf)
            for row in rd:
                if row['city'] == city:
                    if row['region'] == region:
                        print("City and state dupe")
                        print("")
                        dupe = True
                        print("Dupe with " + city)
                        out = row
        if not dupe:
            ## Discard any results that do not contain a City
            if city.strip() != '' and region.strip() != '' and country.strip() != '':
                locstring = city + ", " + region + ", " + country
            elif city.strip() != '' and country.strip() != '':
                locstring = city + ", " + country
            
            if locstring:
                ## Do geocode with Google Maps API
                geocode_result = gmaps.geocode(locstring)
                if len(geocode_result) > 0:
                    loc = {'lat': geocode_result[0]['geometry']['location']['lat'], 'lng': geocode_result[0]['geometry']['location']['lng'], 'city': city, 'region': region, 'country' : country }
                    headers = ['city', 'region', 'country', 'lat', 'lng']
                    ## Write geocode result to Geocode Results file
                    with open("/Users/kevindenny/Documents/automated-reports/dj_app/bq_api/cities_geocoding_results.csv", 'a') as ofile:
                        we = csv.DictWriter(ofile, fieldnames=headers)
                        we.writerow(loc)
                else:
                    loc = None
            else:
                loc = None
            out = loc

    
    return out
        

