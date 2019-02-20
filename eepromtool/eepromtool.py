import logging

# World Manufacture Index
WMI = {'WAU': "Audi", 'TRU': "Audi Hungary", '93U': "Audi Brazil", 'WVW': "VW", 'WV1': "VW Commercials", 'WV2': "VW Bus",
       'VWV': "VW Spain", 'AAV': "VW South Africa", '1VW': "VW USA", '2V4': "VW Canada", '3VW': "VW Mexico", '8AW': "VW Argentina",
       '9BW': "VW Brazil", 'TMB': "Skoda", 'TMP': "Skoda", 'TM9': "Skoda", 'VSS': "Seat"}

YEAR = {'N': "1992", 'P': "1993", 'R': "1994", 'S': "1995", 'T': "1996", 'V': "1997", 'W': "1998", 'X': "1999", 'Y': "2000", '1': "2001",
        '2': "2002", '3': "2003", '4': "2004", '5': "2005", '6': "2006", '7': "2007", '8': "2008", '9': "2009", 'A': "2010", 'B': "2011",
        'C': "2012", 'D': "2013", 'E': "2014", 'F': "2015", 'G': "2016", 'H': "2017", 'J': "2018", 'K': "2019", 'L': "2020", 'M': "2021"}

MODEL = {'11': "Beetle (Brazilian, Mexican, Nigerian)", '13': "Scirocco 3", '14': "Caddy Mk 1 (European Golf 1 pickup)", '15': "Cabriolet (1980 Beetle, Golf 1)",
         '16': "Jetta 1 and 2 (early), Beetle (2012-on)", '17': "Golf 1", '18': "Iltis", '19': "Golf 2 (early)", '1C': "New Beetle (US market)", '1E': "Golf 3 Cabriolet",
         '1F': "Eos", '1G': "Golf and Jetta 2 (late)", '1H': "Golf and Vento 3", '1J': "Golf and Bora 4", '1K': "Golf and Jetta 5, 6", '1T': "Touran", '1Y': "New Beetle Cabriolet",
         '24': "T3 Transporter Single/Double Cab Pickup", '25': "T3 Transporter Van, Kombi, Bus, Caravelle", '28': "LT Transporter 1", '2D': "LT Transporter 2", '2E': "Crafter",
         '2H': "Amarok", '2K': "Caddy, Caddy Maxi 3", '30': "Fox (US model ex-Brazil)", '31': "Passat 2", '32': "Santana sedan", '33': "Passat 2 Variant", '3A': "Passat 3, 4",
         '3B': "Passat 5", '3C': "Passat 6, Passat CC", '3D': "Phaeton", '50': "Corrado (early)", '53': "Scirocco 1 and 2", '5K': "Golf and Jetta 6", '5M': "Golf Plus", '5N': "Tiguan",
         '5Z': "Fox (Europe)", '60': "Corrado (late)", '6K': "Polo Classic, Variant 3", '6N': "Polo 3", '6R': "Polo 5", '6X': "Lupo", '70': "T4 Transporter Vans and Pickups",
         '74': "Taro", '7H': "T5 Transporter", '7L': "Touareg 1", '7M': "Sharan", '7P': "Touareg 2", '86': "Polo and Derby 1 and 2", '87': "Polo Coupe", '9C': "New Beetle",
         '9K': "Caddy 2 Van (ex-SEAT Ibiza)", '9N': "Polo 4", '9U': "Caddy 2 Pickup (ex-Skoda Felicia)", 'AA': "Up!", '8Z': "A2", '8L': "A3 97-03", '8P': "A3 2003 on",
         '8E': "A4 01-08", '8K': "A4 2008 on", '8H': "A4 Cab", '8T': "A5", '4A': "A6 95-97", '4B': "A6 96-04", '4F': "A6 2004 on", '4D': "A8 94-03", '4E': "A8 2003 on",
         '4Z': "Allroad 00-05", '8R': "Q5", '4L': "Q7", '42': "R8", '8N': "TT 99-06", '8J': "TT 2006 on", '5J': "Fabia 07 on, Roomster", '6Y': "Fabia 99-07", '6U': "Felicia 95-01",
         '1U': "Octavia 96-03", '1Z': "Octavia 04 on", '3U': "Superb 0108", '3T': "Superb 08 on", '6H': "Arosa", '3R': "Exeo", '6L': "Ibiza 02-08",
         '6J': "Ibiza 08 on", '1P': "Leon 05 on", '1M': "Leon 99-05/Toledo 98-04", '5P': "Toledo 2004 on, Altea", '1L': "Toledo 91-98", }

ORIGIN = {'A': "Ingolstadt, Germany", 'B': "Brussels, Belgium", 'D': "Bratislave, Slovakia", 'E': "Emden, Germany", 'G': "Gratz, Germany", 'H': "Hannover, Germany",
          'K': "Osnabrueck, Germany", 'M': "Mexico", 'N': "Neckarsulm, Germany; Mlada Boleslav", 'P': "Mosel, Germany", 'R': "Martorell, Spain", 'S': "Stuttgart, Germany",
          'T': "Kvasiny, Czech", 'V': "Palmela, Portugal", 'W': "Wolfsburg, Germany", 'X': "Posnan, Poland", 'Y': "Pamplona, Spain", 'Z': "Pacheco, Argentina", '1': "Gyor, Hungary", '8': "Dresden; Vrchlabi"}

class eeprom:
    def readbin(self, filename):
        logging.warn("Loading eeprom - %s" % filename)
        data = []
        readmore = True
        onlyread512k = False
        with open(filename, "rb") as f:
            while readmore:
                page = f.read(16)
                if page:
                    data.append(bytearray(page))
                else:
                    break
                if onlyread512k:
                    if len(data) == 32:
                        readmore = False
        logging.debug("Read in %d 16 byte rows - %dbytes total" %
                      (len(data), len(data)*16))
        logging.info("Read in %dbytes" % (len(data)*16))
        return data

    def parsevin(self, vinin):
        vinstring = ""
        try:
            # attempt to parse the vin
            vinstring += WMI[vinin[0:3]]
            vinstring += " " + YEAR[vinin[9]]
            vinstring += " - " + MODEL[vinin[6:8]]
            vinstring += ", " + ORIGIN[vinin[10]]
        except:
            pass
        return vinstring
