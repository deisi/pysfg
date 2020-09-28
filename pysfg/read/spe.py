"""Module to import SPE files."""

import struct
import logging
import locale
from datetime import datetime

from pathlib import Path
import numpy as np
import xmltodict

# spe files use "C" locals for date strings
locale.setlocale(locale.LC_TIME, 'C')
# Translate Format dict. Key is the name in the manual, value is the
# struct version
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

# All spe files contain atleast this information in there header
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

# header information relevant for v3
# most of the header information has been moved
# to an xml strucutre at the end of the file
# e.g. the footer
elements_v3 = {
    "xml_footer_offset": ("64u", 678),
}

# header information relevant for v2
# v2 basically stores everything within
# the binary header.
header_v2 = {
    "ControllerVersion": ("16s", 0),
    "AmpHiCapLowNoise": ("16u", 4),
    "mode": ("16s", 8),
    "exp_sec": ("32f", 10),
    "VChipXdim": ("16s", 14),
    "VChipYdim": ("16s", 16),
    "date": ("8s", 20, 10),
    "DetTemperature": ("32f", 36),
    "DelayTime": ("32f", 46),
    "ShutterControl": ("16u", 50),
    "SpecCenterWlNm": ("32f", 72),
    "SpecGlueFlag": ("16s", 76),
    "SpecGlueStartWlNm": ("32f", 78),
    "SpecGlueEndWlNm": ("32f", 82),
    "SpecGlueMinOvrlpNm": ("32f", 86),
    "SpecGlueFinalResNm": ("32f", 90),
    "ExperimentTimeLocal": ("8s", 172, 7),
    "ExperimentTimeUTC": ("8s", 179, 7),
    "gain": ("16u" ,198),
    "ReadoutTime": ("32f", 672),
    "sw_version": ("8s", 688, 16),
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
    "NumROI": ("16s", 1510),  # If 0 assume 1
}

# The calibration is stored as polynom in the v2 header
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


def _intlist_to_string(llist):
    """Convert a list of integers into a string omitting empty \00 entries."""
    return "".join([chr(i) for i in llist]).strip("\00").strip("\x0b")


def _readHeader(fname):
    """Import v2 and v3 SPE binary data"""
    ret = {}
    with open(Path(fname), "rb") as spe:
        # 4100 is the fixed byte length of the header.
        # This is defined for all spe files.
        header = spe.read(4100)

        def _read_value_from_header(fmt, offset):
            f = tf[fmt]
            return struct.unpack_from(f, header, offset)[0]

        def _read_list_from_header(fmt, offset, length):
            f = tf[fmt]
            f = str(length) + f
            return struct.unpack_from(f, header, offset)

        def _read_from_header(*args):
            if len(args) == 2:
                return _read_value_from_header(*args)
            if len(args) == 3:
                return _read_list_from_header(*args)
            raise ValueError('expected two or three arguments got: %s' % args)

        for key, value in header_general.items():
            ret[key] = _read_from_header(*value)

        if ret['file_header_ver'] >= 3:
            for key, value in elements_v3.items():
                ret[key] = _read_from_header(*value)

        if ret['file_header_ver'] < 3:
            for key, value in header_v2.items():
                ret[key] = _read_from_header(*value)

            # Some entries list of chars are strings
            for key in (
                    'date', 'ExperimentTimeLocal', 'ExperimentTimeUTC',
                    'sw_version'
            ):
                ret[key] = _intlist_to_string(ret[key])

            ret['X Calibration'] = {}
            for key, value in calibration_x_v2.items():
                ret['X Calibration'][key] = _read_from_header(*value)
    return ret


def _readData(fname, xdim, ydim, numFrames, datatype):
    """Read binary data of the .spe file.
    fname: Path to .spe file
    xdim: xdimension of data found in header
    ydim: ydimension of data found in header
    numFrames: number of frames found in header
    datatype: integer describing data type of binary data.

    """
    dataTypeDict = {
        0: ('f', 4, 'float32'),
        1: ('i', 4, 'int32'),
        2: ('h', 2, 'int16'),
        3: ('H', 2, 'int32'),
        5: ('d', 8, 'float64'),
        6: ('B', 1, 'int8'),
        8: ('I', 4, 'int32'),
    }
    nBytesHeader = 4100
    nPixels = xdim * ydim
    # fileheader datatypes translated into struct fromatter
    # This tells us what the format of the actual data is
    fmtStr, bytesPerPixel, npfmtStr = dataTypeDict[datatype]
    fmtStr = str(xdim * ydim) + fmtStr
    logging.debug('fmtStr: %s' % fmtStr)

    # Bytes per frame
    nBytesPerFrame = nPixels * bytesPerPixel
    logging.debug('nBytesPerFrame %s' % nBytesPerFrame)

    logging.debug('Opening %s' % Path(fname))
    data = np.zeros((numFrames, ydim, xdim), dtype=npfmtStr)
    with open(Path(fname), 'rb') as spe:
        spe.seek(nBytesHeader)
        for frame in range(numFrames):
            logging.debug('Read frame number %s' % frame)
            _data = spe.read(nBytesPerFrame)
            dataArr = np.array(
                struct.unpack_from('='+fmtStr, _data, offset=0),
                dtype=npfmtStr
            )
            dataArr.resize((ydim, xdim))
            data[frame] = dataArr
    return data


def _calc_wavelength_from_header(header):
    """calculate wavelength from header information.
    Raise ValueError if it all polynom_coeff in header are 0"""
    wavelength = np.arange(header['xdim'])
    poly_coeff = np.array(header['X Calibration']['polynom_coeff'])
    # numpy needs polynom params in reverse order
    params = poly_coeff[np.where(poly_coeff != 0)][::-1]
    if len(params) > 1:
        calib_poly = np.poly1d(params)
        wavelength = calib_poly(wavelength)
        return wavelength
    raise ValueError('Cound not calculate wavelength from header %s' % header)


def _readFooter(fname, xml_footer_offset):
    """Read xml data from footer. nBytesFooter is known from header."""
    with open(Path(fname)) as spe:
        spe.seek(xml_footer_offset)
        footer = xmltodict.parse(spe.read(), dict_constructor=dict)
    return footer


def readSpeFile(fname):
    """Raw Spe data file reader.
    fname: Path to .spe file

    return dict with key `data` for the raw rectangular data and `header` for
    some of the header information. From .spe version 3 also a 'footer' is
    returned. Where all of the information is in the new .spe case.
    """
    ret = {}
    ret['header'] = _readHeader(fname)
    ret['data'] = _readData(
        fname, ret['header']['xdim'], ret['header']['ydim'],
        ret['header']['NumFrames'], ret['header']['datatype']
    )
    if ret['header']['file_header_ver'] >= 3:
        ret['footer'] = _readFooter(fname, ret['header']['xml_footer_offset'])
    return ret


def data_file(fpath):
    """Format spe data to be similar to victor.data_file and subselect
    only what we need."""

    spe = readSpeFile(fpath)
    ret = {
        'raw_data': spe['data'],
        # Add the pp_delay axis, as spe data only contains frames.
        'data': np.expand_dims(spe['data'], 0),
    }

    if spe['header']['file_header_ver'] < 3:
        # Organize metadata from header
        ret['wavelength'] = _calc_wavelength_from_header(spe['header'])
        ret['gain'] = spe['header']['gain']
        ret['exposureTime'] = spe['header']['exp_sec']
        ret['date'] = spe['header']['date']
        ret['tempSet'] = spe['header']['DetTemperature']
        ret['central_wl'] = ret['wavelength'][spe['header']['xdim']//2]

        # Convert Time to datetime objects
        locale.setlocale(locale.LC_TIME, 'C')
        for key in ('ExperimentTimeLocal', 'ExperimentTimeUTC'):
            try:
                ret[key] = datetime.strptime(
                    spe['header']['date'] + spe['header'][key],
                    "%d%b%Y%H%M%S"
                )
            except ValueError:
                logging.error('Cant convert date string %s')

    if spe['header']['file_header_ver'] >=3:
        # Organize metadata from footer
        ret['wavelength'] = np.fromstring(
            spe['footer']["SpeFormat"]["Calibrations"]["WavelengthMapping"]['Wavelength']['#text'],
            sep=","
        )
        ret['central_wl'] = float(
            spe['footer']["SpeFormat"]["DataHistories"]['DataHistory']["Origin"]["Experiment"]["Devices"]['Spectrometers']["Spectrometer"]["Grating"]["CenterWavelength"]['#text']
        )
        ret['grating'] = spe['footer']["SpeFormat"]["DataHistories"]['DataHistory']["Origin"]["Experiment"]["Devices"]['Spectrometers']["Spectrometer"]["Grating"]['Selected']['#text']
        ret['exposureTime'] = float(spe['footer']['SpeFormat']['DataHistories']['DataHistory']['Origin']['Experiment']['Devices']['Cameras']['Camera']['ShutterTiming']['ExposureTime']['#text'])
        temp = spe['footer']['SpeFormat']['DataHistories']['DataHistory']['Origin']['Experiment']['Devices']['Cameras']['Camera']['Sensor']['Temperature']
        ret['tempSet'] = int(temp['SetPoint']['#text'])
        ret['tempRead'] = int(temp['Reading']['#text'])
        ret['roi'] = spe['footer']['SpeFormat']['DataHistories']['DataHistory']['Origin']['Experiment']['Devices']['Cameras']['Camera']['ReadoutControl']['RegionsOfInterest']['Result']['RegionOfInterest']
        created = spe["footer"]["SpeFormat"]["DataHistories"]["DataHistory"]["Origin"]["@created"]
        # Split of UTC Time offset and microsecond as they are inconsistent
        # throught several spe files.
        ret['created'] = datetime.strptime(created.split(".")[0], "%Y-%m-%dT%X")

    return ret

