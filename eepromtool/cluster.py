import logging
from .eepromtool import eeprom


class clustereeprom:
    bin_type = "Cluster"
    noCheckSumPages = [0x10000]
    backupPage = [0x10000]
    write = False  # set to write out eeprom after modification

    size = 0
    data = []

    vin = ""
    vindetail = ""
    immoid = ""
    skc = ""
    clustercode = ""  # 0x34-0x3A
    clustertype = ""
    clusterpartnumberstring = ""
    mileage = ""
    softcoding = ""
    checksum = ""

    def __init__(self, ndata):
        logging.warn("Parsing as cluster eeprom")
        self.data = ndata
        self.parse()

    def parse(self):

        # set length
        self.size = 0
        for page in self.data:
            self.size += len(page)
            if len(page) > 16:
                logging.error("ERROR, long row: %d " % len(page))
            elif len(page) < 16:
                logging.error("ERROR, short row: %d " % len(page))

        # get cluster code
        cc1 = self.data[0x7][0x2:0x9]
        cc2 = self.data[0x7][0xA:0x18]
        cc2.append(self.data[0x8][0x0])
        cc3 = self.data[0x8][0x2:0x9]

        if self.size > 1024:
            if self.data[0x2][0x0:0x2] == self.data[0x3][0x2:0x4]:
                logging.info("Cluster Code Block match for R32 Cluster")
                self.clustertype = 'R32'

            if self.data[0x3][0x0:0x9] == self.data[0x43][0x0:0x9]:
                logging.info("Cluster Code Block match for TT Cluster")
                self.clustertype = '8N'
        elif self.size < 1024:
            self.clustertype = 'v1'

        if self.clustertype == '':
            if cc1 != cc2:
                logging.warn(
                    "WARNING: Cluster Code Block 1 and 2 do not match, this may indicate an error in the file, or a format not supported by this tool")
            if cc1 != cc3:
                logging.warn(
                    "WARNING: Cluster Code Block 1 and 3 do not match, this may indicate an error in the file, or a format not supported by this tool")
            if cc2 != cc3:
                logging.warn(
                    "WARNING: Cluster Code Block 2 and 3 do not match, this may indicate an error in the file, or a format not supported by this tool")

        self.clustercode = ""
        if self.clustertype == '8N':
            for i in range(0xb, 0xf):
                self.clustercode += "%0.2X " % self.data[0x36][i]
            for i in range(0x0, 0x2):
                self.clustercode += "%0.2X " % self.data[0x37][i]
        else:
            for i in range(0x2, 0x9):
                self.clustercode += "%0.2X " % self.data[0x7][i]

        # get SKC
        if self.clustertype == '8N':
            hexskc = "%0.2x%0.2x" % (
                self.data[0x35][0xB], self.data[0x35][0xC])
            self.skc = "0%d" % int(hexskc, 16)
        elif self.clustertype == 'R32':
            hexskc = "%0.2x%0.2x" % (
                self.data[0x10][0xB], self.data[0x10][0xA])
            self.skc = "0%d" % int(hexskc, 16)
        else:
            hexskc = "%0.2x%0.2x" % (self.data[0xC][0xD], self.data[0xC][0xC])
            self.skc = "0%d" % int(hexskc, 16)
        # get clusterpartnumber
        clusterpartnumber = bytearray()
        if self.clustertype == '8N':
            for bite in range(0x0C, 0x10):
                clusterpartnumber.append(self.data[0x22][bite])
            for bite in range(0x00, 0x06):
                clusterpartnumber.append(self.data[0x23][bite])
        elif self.clustertype == 'R32':
            for bite in range(0x0A, 0x10):
                clusterpartnumber.append(self.data[0x15][bite])
            for bite in range(0x00, 0x06):
                clusterpartnumber.append(self.data[0x16][bite])
        elif self.clustertype == 'v1':
            for bite in range(0x00, 0x3):
                clusterpartnumber.append(self.data[0x8][bite])
            for bite in bytearray(b"919"):
                clusterpartnumber.append(bite)
            for bite in range(0x03, 0x10):
                clusterpartnumber.append(self.data[0x8][bite])
        else:
            for bite in range(0x0A, 0x10):
                clusterpartnumber.append(self.data[0x15][bite])
            for bite in range(0x00, 0x06):
                clusterpartnumber.append(self.data[0x16][bite])
        try:
            self.clusterpartnumberstring = clusterpartnumber.decode('ascii')
        except:
            logging.warn("WARNING: cannot decode Cluster Part number")

        # get VIN
        vinstring = bytearray()
        if self.clustertype == '8N':
            for bite in range(0x02, 0x10):
                vinstring.append(self.data[0xD][bite])
            for bite in range(0x00, 0x03):
                vinstring.append(self.data[0xE][bite])
        else:
            for bite in range(0x02, 0x10):
                vinstring.append(self.data[0xD][bite])
            for bite in range(0x00, 0x03):
                vinstring.append(self.data[0xE][bite])
        try:
            self.vin = vinstring.decode('ascii')
        except:
            logging.warn("WARNING: cannot decode VIN, try setting VIN to fix")

        self.vindetail = eeprom.parsevin(None, self.vin)

        # get Immo ID
        immostring = bytearray()
        if self.clustertype == '8N':
            for bite in range(0x0D, 0x0F):
                immostring.append(self.data[0x35][bite])
            for bite in range(0x00, 0x0B):
                immostring.append(self.data[0x36][bite])
        else:
            for bite in range(0x02, 0x0F):
                immostring.append(self.data[0xA][bite])
        try:
            self.immoid = immostring.decode('ascii')
        except:
            logging.warn("WARNING: cannot decode ImmmoID")

    def writebin(self, outputfile):
        outputdata = bytearray()
        for row in self.data:
            count = 0
            for bite in row:
                count += 1
                outputdata.append(bite)
        logging.info("Writing %dkb cluster eeprom bin to: %s" %
                     (len(outputdata), outputfile))
        try:
            with open(outputfile, 'wb') as fp:
                fp.write(outputdata)
        except:
            logging.error("Error: Could not open output file, exiting")
            exit(1)
        logging.info("- Write Successful")
        logging.info("\nThis tool cannot set checksum for cluster bins, so you must force the cluster to reset the checksum by using VCDS to update the cluster softcoding (setting it to the same value will force the update)")

    def printStatus(self):
        logging.info("EEPROM Status:")
        logging.info("- Type: %s" % self.bin_type)
        if self.getVINDetail() is not "":
            logging.info("- VIN: %s (%s)" %
                         (self.getVIN(), self.getVINDetail()))
        else:
            logging.info("- VIN: %s" % (self.getVIN()))
        logging.info("- Size: " + self.getLength())
        logging.info("- SKC: " + self.getSKC())
        logging.info("- Cluster Code: " + self.getClusterCode())
        logging.info("- Immo ID: " + self.getImmoID())
        logging.info("- Cluster Part number: " + self.getClusterPartNumber())
        logging.info("- Checksum: " + self.getChecksum())
        logging.info("- Mileage: " + self.getMileage())
        logging.info("- SoftCoding ID: " + self.getSoftcoding())
        logging.info("")

    def getChecksum(self):
        if self.checksum == "":
            return "Not currently supported"
        else:
            return self.checksum

    def getMileage(self):
        if self.mileage == "":
            return "Not currently supported"
        else:
            return self.mileage

    def getSoftcoding(self):
        if self.softcoding == "":
            return "Not currently supported"
        else:
            return self.softcoding

    def getLength(self):
        if self.size == 2048:
            return "%dbytes" % self.size
        elif self.size/1024 == 512:
            logging.warn(
                "Size: 512kb - is this a flash bin not an eeprom bin?")
            logging.warn("Exiting")
            exit(1)
        elif self.size/1024 == 1024:
            logging.warn(
                "Size: 1024kb - is this a flash bin not an eeprom bin?")
            logging.warn("Exiting")
            exit(1)
        else:
            return "%dbytes - 2048bytes expected, check this is an ecu eeprom bin" % self.size

    def getSKC(self):
        return self.skc

    def setSKC(self, skc):
        # sanity check
        if len(skc) > 5 or len(skc) < 4:
            logging.error(
                "ERROR: SKC must be in format 0xxxx or xxxx, where x is in range 0-9")
            exit(1)
        try:
            tmp = int(skc)
        except:
            logging.error(
                "ERROR: SKC must be in format 0xxxx or xxxx, where x is in range 0-9")
            exit(1)
        if len(skc) == 5 and skc[0] != "0":
            logging.error(
                "ERROR: SKC must be in format 0xxxx or xxxx, where x is in range 0-9")
            exit(1)

        if len(skc) == 5:
            tskc = "%0.4x" % int(skc[0:])
        else:
            tskc = "%0.4x" % int(skc)

        logging.info("Setting SKC to %s" % skc)
        self.data[0xC][0xC] = int(tskc[2:], 16)
        self.data[0xC][0xD] = int(tskc[:2], 16)
        self.data[0xC][0xE] = int(tskc[2:], 16)
        self.data[0xC][0xF] = int(tskc[:2], 16)
        self.data[0xD][0x0] = int(tskc[2:], 16)
        self.data[0xD][0x1] = int(tskc[:2], 16)

        self.parse()
        self.write = True

    def getClusterCode(self):
        return self.clustercode

    def setClusterCode(self, clustercode):

        bacc = bytearray(clustercode.replace(" ", "").decode("hex"))
        self.data[0x7][2:9] = bacc
        self.data[0x7][0xA:18] = bacc[0:6]
        self.data[0x8][0x0] = bacc[6]
        self.data[0x8][2:9] = bacc

        self.parse()
        self.write = True

    def getClusterPartNumber(self):
        return self.clusterpartnumberstring

    def getVIN(self):
        if self.clustertype == '8N':
            return "Not in EEPROM"
        else:
            return self.vin

    def getVINDetail(self):
        return self.vindetail

    def setVIN(self, newvin):
        logging.debug("Trying to set vin to %s (%s)" %
                      (newvin, parsevin(newvin)))
        try:
            if len(newvin) is not 17:
                logging.error("ERROR: VIN number must be 17 characters")
                exit(1)
            logging.info("Setting VIN to %s" % newvin)
            bavin = bytearray(newvin, 'ascii')

            self.data[0xD][0x02:0x10] = bavin[0x00:0x0E]
            del bavin[0x0:0xE]
            self.data[0xE][0x00:0x03] = bavin
        except:
            logging.error("ERROR: Could not set VIN")
            exit(1)
        self.parse()
        self.write = True

        logging.debug("Set vin to %s" % self.getVIN())

    def getImmoID(self):
        return self.immoid

    def setImmoID(self, immoid):
        logging.debug("Trying to set immo ID to %s" % immoid)
        try:
            if len(immoid) is not 14:
                logging.error("ERROR: VIN number must be 14 characters")
                exit(1)
            logging.info("Setting Immo ID to %s" % immoid)
            baii = bytearray(immoid, 'ascii')

            self.data[0xA][0x02:0x10] = baii[0x00:0x0E]
            self.data[0xB][:0xE] = baii[0x00:0x0E]
            self.data[0xB][0xE:0x10] = baii[0x00:0x02]
            self.data[0xC][:0xC] = baii[0x02:0x0E]
        except:
            logging.error("ERROR: Could not set Immo ID")
            exit(1)
        self.parse()
        self.write = True

        logging.debug("Set immo ID to %s" % self.getImmoID())

    def pair(self, ecueepromfile):
        ecueeprombin = ecueeprom(readbin(ecueepromfile))

        # Set Vin, Immo ID, Cluster Code
        self.setVIN(ecueeprombin.getVIN())
        self.setImmoID(ecueeprombin.getImmoID())
        self.setClusterCode(ecueeprombin.getClusterCode())
        self.setSKC(ecueeprombin.getSKC())

        logging.info("")
        logging.info("Cluster updated to:")
        self.printStatus()
        self.write = True
