"""Module to import SPE files."""

# TODO: This needs a clean rewrite, where all data is imported into a single
# dict and that is it. Instead this is a totally bloated class strucutre.

import struct
import logging
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

# Translate Format
tf = {
    "8s": "b",
    "8u": "B",
    "16s": "h",
    "16u": "H",
    "32s": "i",
    "32u": "I",
    "64s": "q",
    "64u": "Q",
    "32f": "f",
    "64f": "d",

}

def readSpeFile(fname):
    """Import v2 and v3 SPE binary data"""
    dataTypeDict = {
        0 : ('f', 4, 'float32'),  # 32f
        1 : ('i', 4, 'int32'),  # 32s
        2 : ('h', 2, 'int16'),  # 16s
        3 : ('H', 2, 'int32'),  # 16u
        5 : ('d', 8, 'float64'),  # 64f
        6 : ('B', 1, 'int8'),  # 
        8 : ('I', 4, 'int32'),  # 64u
    }
    ret = {
        "Header": {},
        "X Calibration": {},
        "Y Calibration": {},
    }
    with open(Path(fname), "rb") as spe:
        # Read Header information
        # Header length is a fixed number
        # nBytesHeader = 4100
        # Read the entire header

        # 4100 is the fixed byte length of the header. This is defined for all spe files.
        header = spe.read(4100)

        def _read_value_from_header(format, offset):
            f = tf[format]
            return struct.unpack_from(f, header, offset)

        def _read_list_from_header(format, offset, length):
            f = tf[format]
            f = str(length) + f
            return struct.unpack_from(f, header, offset)

        header_general = {
            "file_header_ver": ("32f", 1992),
            "datatype": ("16s", 108),
            "xdim": ("16u", 42),
            "ydim": ("16u", 656),
            "NumFrames": ("32s", 1446),
            "xDimDet": ("16u", 6),
            "yDimDet": ("16u", 18),
            "lastvalue": ("16s", 4098),
        }
        elements_v3 = {
            "xml_footer_offset": ("64u", 678),
        }
        header_v2 = {
            "ControllerVersion": ("16s", 0),
            "AmpHiCapLowNoise": ("16u", 4),
            "mode": ("16s", 8),
            "exp_sec": ("32f", 10),
            "VChipXdim": ("16s", 14),
            "VChipYdim": ("16s", 16),
            "date": ("8s", 20, 10),  # TODO this is a list
            "DetTemperature": ("32f", 36),
            "DelayTime": ("32f", 46),
            "ShutterControl": ("16u", 50),
            "SpecCenterWlNm": ("32f", 72),
            "SpecGlueFlag": ("16s", 76),
            "SpecGlueStartWlNm": ("32f", 78),
            "SpecGlueEndWlNm": ("32f", 82),
            "SpecGlueMinOvrlpNm": ("32f", 86),
            "SpecGlueFinalResNm": ("32f", 90),
            "ExperimentTimeLocal": ("8s", 172, 7),  ## TODO This is a list
            "ExperimentTimeUTC": ("8s", 179, 7),  ## TODO This is a list
            "gain": ("16u" ,198),
            "ReadoutTime": ("32f", 672),
            "sw_version": ("8s", 688, 16), # TODO this is a list
            "NumExpRepeats": ("32u", 1418),
            "NumExpAccums": ("32u", 1422),
            "clkspd_us": ("32f", 1428),
            "HWaccumFlag": ("16s", 1432),
            "BlemishApplied": ("16s", 1436),
            "CosmicApplied": ("16s" ,1438),
            "CosmicType": ("16s", 1440),
            "CosmicThreshold": ("32f", 1442),
            "readoutMode": ("16u", 1480),
            "WindowSize": ("16u", 1482),
            "clkspd": ("16u", 1484),
            "SWmade": ("16u", 1508),
            "NumROI": ("16s", 1510), # If 0 assume 1

        }

        calibration_x_v2 = {
            "offset": ("64f", 3000),
            "factor": ("64f", 3008),
            "current_unit": ("8s", 3016),
            "calib_valid": ("8s", 3098),
            "input_unit": ("8s", 3099),
            "polynom_unit": ("8s", 3100),
            "polynom_order": ("8s", 3101),
            "calib_count": ("8s", 3102),
            "pixel_position": ("64f", 3103, 10),
            "calib_value": ("64f", 3183, 10),
            "polynom_coeff": ("64f", 3263, 6),
            "laser_position": ("64f", 3311),
            "new_calib_flag": ("8u", 3320),
        }


        for key, value in header_general.items():
            ret['Header'][key] = _read_value_from_header(*value)[0]

        if ret['Header']['file_header_ver'] < 3:
            for key, value in header_v2.items():
                if len(value) == 2:
                    ret['Header'][key] = _read_value_from_header(*value)[0]
                else:
                    ret['Header'][key] = _read_list_from_header(*value)

            for key, value in calibration_x_v2.items():
                if len(value) == 2:
                    ret['X Calibration'][key] = _read_value_from_header(*value)
                else:
                    ret['X Calibration'][key] = _read_list_from_header(*value)




    return ret



class SPEFile():
    """Class to import and read SPE files.

    Capabilities
    -----------
    Use this class to import spe files from Andor or Lightfield.
    It can handle spe v2 and spe v3 data.

    **Note**
    It only supports rectangular data, and is not feature complete.
    I only implemented what I actually need.

    Attribute
    ----------
    data : array
        (Number of frames, ydim, ydim) shaped array of the raw data

    wavelength : array
        Wavelength as it was given by the camera and the spectrometer

    headerVersion : float
        Version number of the header.

    xdim : int
        Number of pixels in x direction

    ydim : int
        Number of pixels in y direction

    NumFrames : int
        Number of Frames. I.e. repetitions. Also used during a kinetic scan

    Version 2 metadata:
    --------------------
    poly_coeff : array
        Wavelength calibration polynomial coefficients.

    calib_poly : numpy.poly1d
        calibration polynomial


    Version 3 metadata:
    ---------------------
    grating : str
        Description of the used grating

    exposureTime : int
        The exposure time in ms

    TempSet : int
        The set temperature of the camera

    TempRead : int
        The read temperature of the camera

    roi : dict
        Region of interest


    Examples
    --------
    sp = PrincetonSPEFile3("blabla.spe")
    """
    dataTypeDict = {
        0 : ('f', 4, 'float32'),
        1 : ('i', 4, 'int32'),
        2 : ('h', 2, 'int16'),
        3 : ('H', 2, 'int32'),
        5 : ('d', 8, 'float64'),
        6 : ('B', 1, 'int8'),
        8 : ('I', 4, 'int32'),
    }
    def __init__(self, fname, verbose=False):
        self._verbose = verbose

        # if not os.path.isfile(fname) and \
        #    not os.path.islink(fname):
        #     raise IOError('%s does not exist' % fname)

        self._spe = open(fname, 'rb')
        self._fname = fname
        self.metadata = {}
        self.readData()

    def readData(self):
        """Read all the data into the class."""
        self._readHeader()
        self._readSize()
        self._read_v2_header()
        self._readData()
        self._readFooter()

    def _readHeader(self):
        """Reads the header."""
        # Header length is a fixed number
        nBytesHeader = 4100

        # Read the entire header
        self._header = self._spe.read(nBytesHeader)
        self.headerVersion = self._readFromHeader('f', 1992)[0]
        self._nBytesFooter = self._readFromHeader('I', 678)[0]

    def _readSize(self):
        """ Reads size of the data."""
        self.metadata['xdim'] = self._readFromHeader('H', 42)[0]
        self.metadata['ydim'] = self._readFromHeader('H', 656)[0]
        self.metadata['datatype'] = self._readFromHeader('h', 108)[0]
        self.metadata["NumFrames"] = self._readFromHeader("i", 1446)[0]
        self.metadata['xDimDet'] = self._readFromHeader("H", 6)[0]
        self.metadata['yDimDet'] = self._readFromHeader("H", 18)[0]

    def _read_v2_header(self):
        """Read calibrations parameters and calculate wavelength as it
        was done in pre v3 .spe time."""

        # General meta data
        self.metadata['exposureTime'] = timedelta(
            seconds=self._readFromHeader('f', 10)[0]  # in seconds
        )
        # Fix a naming bug but don't brack backwards compatibility
        self.metadata['exposure_time'] = self.metadata['exposureTime']
        date = self._readFromHeader('9s', 20)[0].decode('utf-8')
        self.metadata['tempSet'] = self._readFromHeader('f', 36)[0]
        timeLocal = self._readFromHeader('6s', 172)[0].decode('utf-8')
        timeUTC = self._readFromHeader('6s', 179)[0].decode('utf-8')

        # Try statement is a workaround, because sometimes date seems to be
        # badly formatted and the program cant deal with it.
        try:
            self.metadata['date'] = datetime.strptime(
                date + timeLocal, "%d%b%Y%H%M%S"
            )
            self.metadata['timeUTC'] = datetime.strptime(
                date + timeUTC, "%d%b%Y%H%M%S"
            )
        except ValueError:
            logging.debug('Malformated date in %s' % self._fname)
            logging.debug('dat7e string is: %s' % date)

        self.metadata['gain'] = self._readFromHeader('I', 198)[0]
        # Central Wavelength is in nm
        self.metadata['central_wl'] = self._readFromHeader('f', 72)[0]

        # Lets always have a wavelength array
        # in worst case its just pixels
        # Read calib data
        # TODO: This is probably not a good idea
        if self.headerVersion >= 3:
            return
        poly_coeff = np.array(self._readFromHeader('6d', 3263))
        # numpy needs polynomparams in reverse oder
        params = poly_coeff[np.where(poly_coeff != 0)][::-1]
        if len(params) > 1:
            self.calib_poly = np.poly1d(params)
            self.metadata["wavelength"] = self.calib_poly(self.wavelength)
        self.metadata['poly_coeff'] = poly_coeff

    def _readData(self):
        """Reads the actual data from the binary file.

        Currently this is limited to rectangular data only and
        doesn't support the new fancy data footer features from the
        Version 3 spe file format.
        """
        xdim = self.metadata['xdim']
        ydim = self.metadata['ydim']
        datatype = self.metadata['datatype']

        nPixels = xdim * ydim

        # fileheader datatypes translated into struct fromatter
        # This tells us what the format of the actual data is
        fmtStr, bytesPerPixel, npfmtStr = self.dataTypeDict[datatype]
        fmtStr = str(xdim * ydim) + fmtStr
        if self._verbose:
            print("fmtStr = ", fmtStr)

        # Bytes per frame
        nBytesPerFrame = nPixels * bytesPerPixel
        if self._verbose:
            print("nbytesPerFrame = ", nBytesPerFrame)

        # Now read the image data
        # Loop over each image frame in the image
        if self._verbose:
            print('Reading frame number:')

        nBytesHeader = 4100
        self._spe.seek(nBytesHeader)
        self.data = []
        # Todo read until footer here
        # self._data = self._spe.read()
        for ii in range(self.metadata['NumFrames']):
            data = self._spe.read(nBytesPerFrame)
            if self._verbose:
                print(ii)

            dataArr = np.array(
                struct.unpack_from('='+fmtStr, data, offset=0),
                dtype=npfmtStr
            )
            dataArr.resize((ydim, xdim))
            self.data.append(dataArr)
        self.data = np.array(self.data)
        return self.data

    def _readFooter(self):
        """ Reads the xml footer from the Version 3 spe file """
        import xmltodict

        if self.headerVersion < 3:
            return
        nBytesFooter = self._nBytesFooter
        self._spe.seek(nBytesFooter)
        self._footer = xmltodict.parse(self._spe.read())
        self.wavelength = np.fromstring(
            self._footer["SpeFormat"]["Calibrations"]["WavelengthMapping"]['Wavelength']['#text'],
            sep=","
        )
        self.metadata['central_wl'] = float(
            self._footer["SpeFormat"]["DataHistories"]['DataHistory']["Origin"]["Experiment"]["Devices"]['Spectrometers']["Spectrometer"]["Grating"]["CenterWavelength"]['#text']
            )
        self.metadata['grating'] = self._footer["SpeFormat"]["DataHistories"]['DataHistory']["Origin"]["Experiment"]["Devices"]['Spectrometers']["Spectrometer"]["Grating"]['Selected']['#text']
        # expusure Time in ms
        self.metadata['exposureTime'] = float(self._footer['SpeFormat']['DataHistories']['DataHistory']['Origin']['Experiment']['Devices']['Cameras']['Camera']['ShutterTiming']['ExposureTime']['#text'])
        temp = self._footer['SpeFormat']['DataHistories']['DataHistory']['Origin']['Experiment']['Devices']['Cameras']['Camera']['Sensor']['Temperature']
        self.metadata['tempSet'] = int(temp['SetPoint']['#text'])
        self.metadata['tempRead'] = int(temp['Reading']['#text'])
        self.metadata['roi'] = self._footer['SpeFormat']['DataHistories']['DataHistory']['Origin']['Experiment']['Devices']['Cameras']['Camera']['ReadoutControl']['RegionsOfInterest']['Result']['RegionOfInterest']


def data_file(fpath):
    """Format spe data to be similar to victor.data_file"""
    spe = SPEFile(fpath)
    ret = {
        'raw_data': spe.data,
        # Add the pp_delay axis, as spe data only contains frames.
        'data': np.expand_dims(spe.data, 0),
        'wavelength': spe.wavelength,
        'headerVersion': spe.headerVersion,
    }
    ### add optional metadata
    keys = (
        "central_wl", "exposureTime", "tempSet", "gain", "grating", "tempRead",
        "roi", "xdim", "ydim", "NumFrames", "xDimDet", "yDimDet", "poly_coeff", "date"
    )
    for key in keys:
        value = spe.metadata.get(key)
        if value:
            ret[key] = value
    return ret

