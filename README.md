# gamma_sentinel

## this repository contains some python shell scripts to help procesing sentinel-1 SAR images with GAMMA remote senssing softwer.

### sentinel_possesor.py is a shell script that takes two senitnel-1 rwa data direcotris and process them for surface displacment 

usage: sentinel_possesor.py [-h] [-s S] [-e E] [--m_name M_NAME] [--s_name S_NAME] [--pol POL] [--r_looks R_LOOKS]
                            [--a_looks A_LOOKS] [--cc CC] [--clean CLEAN] [--orbit_files ORBIT_FILES]
                            master slave

This program process 2-pass sentinel interferogram from raw data to unwraped phase

positional arguments:
  master                Master sentinel SAR image data base dir path
  slave                 Slave sentinel SAR image data base dir path

optional arguments:
-h, --help            show this help message and exit
  -s S                  start processing at one of -- Setupprocdir','Import_SLCs','Download_DEM','Import_DEM','getWidth','D
                        EM_geocode','Resampling','getDEMwidth','Interferogram','Flattening','Filtering','Unwrapping','Geoco
                        ding_back','Make_headers','Disp
  -e E                  end processing at one of -s following process
  --m_name M_NAME       name of master file, if not spesipy taken to by master dir name
  --s_name S_NAME       name of slave file, if not spesipy taken to by slave dir name
  --pol POL             SLC polarization to extract (hh,hv,vh,vv) default vv
  --r_looks R_LOOKS     number of range looks default: 20
  --a_looks A_LOOKS     number of azimuth looks default: 4
  --cc CC               unwraping coherince threshold default: 0.2
  --clean CLEAN         delete all but output files defualt: false
  --orbit_files ORBIT_FILES
                        path to orbit files directory, if not spesfied assume their is a direcory named 'orbit_files' in
                        the working direcory
                        
### extract_bursts_kml.py is a shell script that extract 27 or 28 kml files where each one of the kml file contains the extant of one burst of the sentinel-1 image.
usage: extract_bursts_kml.py [-h] [-c C] path name

This program generate bursts kml from sentinel raw dir

positional arguments:
  path        path to sentinel raw dir
  name        image name

optional arguments:
  -h, --help  show this help message and exit
  -c C        color for polygon lines one of [r:red, b:blue, g:green, y:yellow], defualt red
