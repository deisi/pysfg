# Module that deals with the import and read of data
import os
import datetime
import numpy as np
import glob

PIXEL = 1600 # Number of pixel on camera
SPECS = 3 # Number of spectra recorded


def data_victor(fpath, kwargs_genfromtxt=None, sort_pp_times=True):
    """Read victor controller data.

    kwargs_genfromtxt: kwargs passed to numpy genfromtxt
    sort_pp_times: Allows sorted reading of random scrambeled pp_delay times
    """
    if not kwargs_genfromtxt:
        kwargs_genfromtxt = {}

    # Read header
    ret = header_victor(fpath)
    pp_delays = ret['timedelay']

    # Read data
    raw_data = np.genfromtxt(fpath, dtype='long', **kwargs_genfromtxt)[:, 1:]
    ret['raw_data'] = raw_data

    # Process raw_data into data
    num_rows, num_columns = raw_data.shape

    # File is just a simple scan.
    if num_rows == PIXEL and num_columns == 3:
        return np.array([[raw_data.T]]), pp_delays

    # Check that we can read the data shape
    if (num_columns)%SPECS != 0:
        raise IOError("Cant read data in %s" % fpath)

    num_pp_delays = num_rows//PIXEL

    # The first colum is only pixel number
    num_repetitions = num_columns//SPECS

    # Init container for the result.
    data = np.zeros((num_pp_delays, num_repetitions, SPECS, PIXEL))

    for rep_index in range(num_repetitions):
        for pp_delay_index in range(num_pp_delays):
            column_slice = slice(PIXEL*pp_delay_index, PIXEL*pp_delay_index + PIXEL)
            row_slice = slice(rep_index*SPECS, rep_index*SPECS+SPECS)
            data[pp_delay_index, rep_index] = raw_data[column_slice, row_slice].T

    # Sorts data by pp_delays
    if sort_pp_times:
        sorting_ideces = np.argsort(pp_delays)
        pp_delays = pp_delays[sorting_ideces]
        data = data[sorting_ideces]

    ret['data'] = data
    return ret


def header_victor(fpath):
    """Read informaion from fileheader and return as dictionary."""
    ret = {}
    with open(fpath) as f:
        for line in f:
            if line[0] is not "#":
                break
            # Strip comment marker
            line = line[2:]
            name, value = line.split("=")
            # Strip newline
            ret[name] = value[:-1]

    # To have some compatibility between spe veronica and viktor files,
    # we further unify some of the namings
    ret['gain'] = ret.get('Gain')

    exp_time = ret.get('ExposureTime [s]')
    if exp_time:
        ret['exposure_time'] = datetime.timedelta(seconds=float(exp_time))

    hbin = ret.get('HBin')
    if hbin:
        ret['hbin'] = {'ON': True}.get(value, False)

    cw = ret.get('Central-Wavelength')
    if cw:
        ret['central_wl'] = float(cw)

    vis_wl = ret.get('vis-Wavelength')
    if vis_wl:
        ret['vis_wl'] = float(vis_wl)

    syringe_pos = ret.get('Syringe Pos')
    if syringe_pos:
        ret['syringe_pos'] = int(syringe_pos)

    cursor = ret.get("Cursor")
    if cursor:
        ret['cursor'] = tuple([int(elm) for elm in cursor.split('\t')])

    x_mirror = ret.get('x-mirror')
    if x_mirror:
        ret['x_mirror'] = {'ON': True}.get(x_mirror, False)

    calib_coeff = ret.get('calib Coeff')
    if calib_coeff:
        ret['calib Coeff'] = tuple([float(elm) for elm in calib_coeff.split('\t')])

    scan_start_time = ret.get('Scan Start time')
    if scan_start_time:
        ret['date'] = datetime.datetime.strptime(scan_start_time, '%d.%m.%Y  %H:%M:%S')

    scan_stop_time = ret.get('Scan Stop time')
    if scan_stop_time:
        ret['date_stop'] = datetime.datetime.strptime(scan_stop_time, '%d.%m.%Y  %H:%M:%S')

    timedelay = ret.get('Timedelay')
    if timedelay:
        ret['timedelay'] = np.array([int(elm) for elm in timedelay.split('\t')])

    timedelay_pos= ret.get('Timedelay Pos')
    if timedelay_pos:
        ret['timedel_pos'] = np.array([int(elm) for elm in timedelay_pos.split('\t')])

    return ret


def folder_victor(fpath):
    """Read all .dat files from a folder.

    Returns a dict where file paths are the key and values are data dicts.
    """
    file_paths = glob.glob(fpath + '/*.dat')

    ret = {}
    print('Reading: ')
    for ffile in file_paths:
        print(ffile)
        ret[ffile] = data_victor(ffile)

    return ret




