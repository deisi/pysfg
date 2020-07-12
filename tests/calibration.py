import pysfg

central_wl = 674
vis_wl = 810
calib_central_wl = 670
calib_coeff = (0.034274, 642.101)

cV = pysfg.Calibration(
    central_wl,
    vis_wl,
    calib_central_wl,
    calib_coeff
)
print(cV.wavenumber)
