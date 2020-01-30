# Module that deals with the import and read of data from victor setup
import datetime
import numpy as np
import glob

PIXEL = 1600 # Number of pixel on camera
SPECS = 3 # Number of spectra recorded


def header(fpath):
    """Read informaion from fileheader and return as dictionary.

    Reads the information of the header from a vicotr `.dat` file and returns
    the information in a strucutred way. Some of the results are also
    translated into specific python objects if possible and returned with
    slightly changed names.
    """
    # If you want to change something, instead of overwriting a bug, add a new
    # key with the desired functionallity. This way, prior code doesn't break.
    # One can be very waste full with this function as it is fast anyways.


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
        # Index 0 is actually central_wl during calibration,
        ret['calib_central_wl'] = ret['calib Coeff'][0]


        # For np.poly1d the calibration coefficents need to be in decreasing
        # order and no zero values are not allowed
        _cc = np.array(ret['calib Coeff'][1:])
        ret['calib_coeff'] =  _cc[np.nonzero(_cc)][::-1]

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


def data_file(fpath, kwargs_genfromtxt=None, sort_pp_times=True):
    """Read victor controller data.

    Function to read of all information of a vicotr `.dat` file. It returns a
    dictionary with combined information of the header and the data. The data
    is added twice. Once in its raw 2D shape under the keyword `raw_data` and
    once in its 4D shape under the keyword 'data'. Typically you want to use the
    `data` key, as all other functions and methods in this toolkit assume 4D
    data if dealing with the direct output of this function.

    Example:
    ```
    data = pysfg.read.victor.data_file('path_to_file')
    # the usable 4D form
    data['data']
    ```

    The 4D shape can be sliced by using numpy advances slicing, or by using an
    instance of the `pysfg.SelectorPP` class.

    Example:
    ```
    # take the mean of the first 4 scans, of the second spectrum from pixel 400 to 1200
    selection = pysfg.SelectorPP(scans=slice(4), spectra=2, pixel=slice(400, 1200))
    np.mean(data['data][selection.select], axis=(0, 1))
    ```

    kwargs_genfromtxt: kwargs passed to numpy genfromtxt
    sort_pp_times: Allows sorted reading of random scrambeled pp_delay times.
      Should be kept True.

    """
    if not kwargs_genfromtxt:
        kwargs_genfromtxt = {}

    # Read header
    ret = header(fpath)
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


def list(ffiles):
    """Read a list of files assuming all are victor data files.

    ffiles: list of strings pointing to victor files
    Returns a dict with file names as keys and victor data dicts as values.
      In other words, this returns a dict of dicts.
    """
    ret = {}
    print('Reading: ')
    for ffile in ffiles:
        print(ffile)
        ret[ffile] = data_file(ffile)
    return ret


def folder(fpath):
    """Read all .dat files from a folder, assuming all a victor data files

    Returns a dict where file paths are the key and values are data dicts. Or
    in other words, a dict of dicts.

    """
    file_paths = glob.glob(fpath + '/*.dat')
    return list(file_paths)
