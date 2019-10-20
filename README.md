# gamma_sentinel

## This repository contains some python shell scripts to help to process sentinel-1 SAR images with GAMMA remote sensing software.

### sentinel_possesor.py is a shell script that takes two sentinel-1 raw data directories and processes them for surface displacement 

usage: sentinel_possesor.py [-h] [-s S] [-e E] [--m_name M_NAME] [--s_name S_NAME] [--pol POL] [--r_looks R_LOOKS]
                            [--a_looks A_LOOKS] [--cc CC] [--clean CLEAN] [--orbit_files ORBIT_FILES]
                            master slave

This program process 2-pass sentinel interferogram from raw data to unwrapped phase

positional arguments:  
  master                Master sentinel SAR image data base dir path<br/>
  slave                 Slave sentinel SAR image data base dir path<br/>

optional arguments:  
  -h, --help            show this help message and exit<br/>
  -s S                  start processing at one of -- Setupprocdir','Import_SLCs','Download_DEM','Import_DEM','getWidth','D<br/>
                        EM_geocode','Resampling','getDEMwidth','Interferogram','Flattening','Filtering','Unwrapping','Geoco<br/>
                        ding_back','Make_headers','Disp<br/>
  -e E                  end processing at one of -s following process<br/>
  --m_name M_NAME       name of master file, if not spesipy taken to by master dir name<br/>
  --s_name S_NAME       name of slave file, if not spesipy taken to by slave dir name<br/>
  --pol POL             SLC polarization to extract (hh,hv,vh,vv) default vv<br/>
  --r_looks R_LOOKS     number of range looks default: 20<br/>
  --a_looks A_LOOKS     number of azimuth looks default: 4<br/>
  --cc CC               unwraping coherince threshold default: 0.2<br/>
  --clean CLEAN         delete all but output files defualt: false<br/>
  --orbit_files ORBIT_FILES
                        path to orbit files directory, if not specified assume there is a directory named 'orbit_files' in
                        the working direcory<br/>
                        
### extract_bursts_kml.py is a shell script that extracts 27 or 28 kml files where each one of the kml files contains the extant of one burst of the sentinel-1 image.
usage: extract_bursts_kml.py [-h] [-c C] path name<br/> 

This program generates bursts kml from sentinel raw dir<br/> 

positional arguments:<br/>
  path        path to sentinel raw dir<br/>
  name        image name<br/>

optional arguments:<br/>
  -h, --help  show this help message and exit<br/>
  -c C        color for polygon lines one of [r:red, b:blue, g:green, y:yellow], defualt red<br/>

