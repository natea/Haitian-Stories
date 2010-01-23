#!/usr/bin/env python

""" Quick 'n dirty script to create a small countries/cities database, since the
code I got from Shady references a "geonames" database which I didn't have - Francois
More cities/countries may be added via the django admin interface
"""

import sys
import csv
from xml.dom import minidom
from decimal import Decimal
from string import capwords

def parse(countriesFilename, citiesFilename):
    """ @return a dict containing country/city/long/lat info - only countries that we have city info for will be returned """
    countries = {}
    
    # Get city lat-long info
    f = open(citiesFilename)
    lines = f.read().split('\n')
    f.close()
    for line in lines:
        parts = line.split('  ')
        if len(parts) == 1:
            if len(parts[0]) == 0:
                continue
            countryName = capwords(line)
            countries[countryName] = {'cities': []}
        else:
            cityName = parts[0]
            latStr = None
            longStr = None
            for part in parts[1:]:
                if len(part) != 0:
                    if latStr == None:
                        latStr = part.strip()
                    else:
                        longStr = part.strip()
            lat = convertLatitude(latStr)
            long = convertLongitude(longStr)
            countries[countryName]['cities'].append({'name': cityName, 'lat': lat, 'long': long})
    
    # Get country list; fill in ISO alpha-2 codes
    f = open(countriesFilename)
    reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
 
    for row in reader:
        alpha2Code = row[2]
        countryName = row[1]
        if countries.has_key(countryName):
            countries[countryName]['alpha2Code'] = alpha2Code
    f.close()
            
    return countries

def convertLatitude(latStr):
    lat = convertDegreesToDecimal(latStr)
    if latStr[-1] == 'S':
        lat *= -1
    lat = str(lat)
    lat = lat[0:lat.find('.')+5]
    return lat

def convertDegreesToDecimal(latOrLongStr):
    deg = latOrLongStr[0:latOrLongStr.find('\xc2\xb0')].strip()
    min = latOrLongStr[latOrLongStr.rfind("'")-2:latOrLongStr.rfind("'")].strip()
    value = round(Decimal(deg) + (Decimal(min)/60), 4)
    return value

def convertLongitude(longStr):
    longValue = convertDegreesToDecimal(longStr) 
    if longStr[-1] == 'W':
        longValue *= -1
    longFinal = str(longValue)
    longFinal = longFinal[0:longFinal.find('.')+5]
    return longFinal



def createXml(countryCitiesMap):
    """ Creates an XML document similar to the "countries.xml" I got from Shady, except that
    this document has latitude & longitude information for every city in it.
    The resulting XML document would be useful for populating a database, but this can also be done from the <countryCitiesMap> parameter directly
    """
    xmlDoc = minidom.Document()
    docElement = xmlDoc.createElement('countries')
    for country in countryCitiesMap.keys():
        countryElement = xmlDoc.createElement('country')
        countryElement.setAttribute('name', country)
        for city in countryCitiesMap[country]['cities']:
            cityElement = xmlDoc.createElement('city')
            cityElement.appendChild(xmlDoc.createTextNode(city['name']))
            cityElement.setAttribute('lat', city['lat'])
            cityElement.setAttribute('long', city['long'])
            countryElement.appendChild(cityElement)
        docElement.appendChild(countryElement)
    xmlDoc.appendChild(docElement)
    return xmlDoc.toprettyxml()

def createSql(countryCitiesMap):
    """ Creates an SQL statement that will populate the ourstories cities & countries database tables """
    countryInsertStr = 'INSERT INTO ourstories_country(name, alpha2Code, dialCode) VALUES'
    cityInsertStr = 'INSERT INTO ourstories_city(name, country_id, latitude, longitude) VALUES'
    for country in countryCitiesMap.keys():
        countryInsertStr += "\n    ('%s', " % country
        if (countryCitiesMap[country].has_key('alpha2Code')): 
            countryInsertStr += "'%s'," % countryCitiesMap[country]['alpha2Code']
        else:
            countryInsertStr += 'NULL,'
        countryInsertStr += ' NULL),'
        for city in countryCitiesMap[country]['cities']:
            cityInsertStr += "\n    ('%s', '%s', '%s', '%s')," % (city['name'], country, city['lat'], city['long'])
    countryInsertStr = countryInsertStr[:-1] + ';'
    cityInsertStr = cityInsertStr[:-1] + ';'
    return 'USE ourstories;\n\n%s\n\n%s\n' % (countryInsertStr, cityInsertStr)
        
            
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >>sys.stderr, 'Usage: %s SQL|XML [path_to_countries_list] [path_to_cities_list"]'
        print >>sys.stderr, 'Please specify a command: XML or SQL'
        sys.exit(1)
    elif len(sys.argv) < 4:
        print >>sys.stderr, 'Usage: %s SQL|XML [path_to_countries_list] [path_to_cities_list"]'
        print >>sys.stderr, '\ncountries list can be downloaded from here: http://schmidt.devlib.org/data/countries.txt'
        print >>sys.stderr, 'cities list was scraped from: http://www.bcca.org/misc/qiblih/latlong_oc.html'
        print >>sys.stderr, '\nTrying default filenames (this may fail...)'
        cMap = parse('countries.txt', 'cities.txt')
    else:
        cMap = parse(sys.argv[2], sys.argv[3])
    if (sys.argv[1].lower() == 'sql'):
        output = createSql(cMap)
    elif (sys.argv[1].lower() == 'xml'):
        output = createXml(cMap)
    else:
        print >>sys.stderr, 'Usage: %s SQL|XML [path_to_countries_list] [path_to_cities_list"]'
        print >>sys.stderr, 'Invalid command; please use either XML or SQL'
        sys.exit(1)
    print output # this may be piped to a file if desired
