from django.core.management.base import BaseCommand
from django.conf import settings
from decimal import Decimal

import sys, csv

from ourstories.models import Country, City

class Command(BaseCommand):
    def handle(self, *args, **kwargs_dummy):

        if len(args) != 2:
            print "Usage: manage.py load_geodata path/to/countryInfo.txt path/to/cities15000.txt"
            sys.exit(1)

        countryInfo = args[0]
        cityInfo = args[1]

        countryReader = csv.reader(open(countryInfo), dialect="excel-tab")

        country_by_code = {}

        #form:
        # ISO	ISO3	ISO-Numeric	fips	Country	Capital	Area(in sq km)	Population	Continent	tld	CurrencyCode	CurrencyName	Phone	Postal Code Format	Postal Code Regex	Languages	geonameid	neighbours	EquivalentFipsCode
        for row in countryReader:
            if len(row) < 13:
                continue

            (isocode, 
             iso3, 
             iso_numeric, 
             fips, 
             country, 
             capital, 
             area, 
             population, 
             continent, 
             tld, 
             currencycode, 
             currencyname, 
             phone) = row[0:13]

            if isocode.startswith("#") or len(isocode) != 2:
                continue

            print "%s %s=%s" % (continent, isocode, country)
            c, created = Country.objects.get_or_create(
                isocode=isocode, name=country, continent=continent)

            country_by_code[c.isocode] = c
            
        cityReader = csv.reader(open(cityInfo), dialect="excel-tab")

        #form:
        # geonameid	name	asciiname	alternatenames	lat	long	feat class	feat code	country code	cc2	admin1	admin2	admin3	admin4	population	elevation	gtopo30	timezone	modified 

        for row in cityReader:
            if len(row) < 18:
                continue

            (geonames_id,
             cityname,
             asciiname,
             alternatenames,
             lat,
             long,
             featclass,
             featcode,
             country_code,
             country_code_2,
             admin1,
             admin2,
             admin3,
             admin4,
             population,
             elevation,
             gtopo30,
             timezone,
             modified_date) = row[0:19]

            try:
                lat = Decimal(lat)
                long = Decimal(long)
                population = int(population)
            except ValueError:
                print "SKIPPING INVALID DATA ROW: %s" % repr(row)
                continue

            if population < settings.MINIMUM_POPULATION_CITY_TO_LOAD:
                print "skipping %s, %s" % (cityname, country_code)
                continue

            print "Loading %s, %s..." % (cityname, country_code)

            if country_code == "US":
                # US state names are in the admin1 column for some reason
                cityname += ", %s" % admin1

            ci, created = City.objects.get_or_create(
                name = cityname,
                country = country_by_code[country_code],
                latitude = lat,
                longitude = long,
                population = population)
            
            
