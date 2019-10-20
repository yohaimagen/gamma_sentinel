#! /home/yohai/anaconda2/bin/python
import sys,os,re,time,glob,string,getopt, argparse
import numpy as np




############################################################
#print messeges to standart error and log file             #
############################################################
def message(mes): # messeges to standart error and log file
  """
Prints a message string to standart error and also to log file.
  """
  sys.stderr.write(mes+"\n")
  try:
    log = open(message_logfile,'a')
  except IOError:
    sys.exit("Could not fined or open"+message_logfile)
  else:
    log.write(stage+" " +" "+mes+"\n")
    log.close()

##########################################################
# logs commands and control errors                       #
##########################################################
def execlog(command): # logs commands and control errors
  """
controling the command executions using os.system, and logging the commands
if an error raise when trying to execute a command, stops the script and writting the
rest of commands to the log file after a 'Skipping from here' note.
  """
  global skipping
  try:
    log = open(cmd_logfile,'a')
  except IOError:
    sys.exit("Could not fined "+cmd_logfile)
  else:
    log.write(command+"\n")
    log.close()
  if not skipping:
    cmd_strerror = os.strerror(os.system(command))
    if not cmd_strerror == 'Success':
      message(cmd_strerror)
      message("Faild at "+stage)
      if not stage == "* Unwrapping":
        message("############## Skipping from here ##############")
        log = open(cmd_logfile,'a')
        log.write("############## Skipping from here ##############\n")
        log.close()
        skipping = 1
      else:
        return "unwfaild"

def Setupprocdir():
    message("****** Initialize dirs structure ******")
    os.mkdir('dem')

def Import_SLCs():
    '''
    Make S1 list file in with each line is the absolute path to S1 scene directory
    :return:
    '''
    message("****** Importing SLCs ******")
    execlog('echo %s > S1_list' %master_path)
    execlog('echo %s >> S1_list' %slave_path)
    execlog('S1_TOPS_preproc S1_list slc %s S1_TOPS_preproc.log -m mli_%s_%s -r %s -a %s' %(pol, r_looks, a_looks, r_looks, a_looks))
    execlog('OPOD_vec mli_%s_%s/%s_%s.mli.par %s' %(r_looks, a_looks, master, pol, orbit_files))
    execlog('OPOD_vec mli_%s_%s/%s_%s.mli.par %s' % (r_looks, a_looks, slave, pol, orbit_files))
    execlog('OPOD_vec slc/%s_iw%d_%s.slc.par %s' % (master, 1, pol, orbit_files))
    execlog('OPOD_vec slc/%s_iw%d_%s.slc.par %s' % (master, 2, pol, orbit_files))
    execlog('OPOD_vec slc/%s_iw%d_%s.slc.par %s' % (master, 3, pol, orbit_files))
    execlog('OPOD_vec slc/%s_iw%d_%s.slc.par %s' % (slave, 1, pol, orbit_files))
    execlog('OPOD_vec slc/%s_iw%d_%s.slc.par %s' % (slave, 2, pol, orbit_files))
    execlog('OPOD_vec slc/%s_iw%d_%s.slc.par %s' % (slave, 3, pol, orbit_files))

def Download_DEM():
    '''
    Downloading srtmG1 DEM file and import it to Gamma
    :return:
    '''
    def extract_corners(path):
        with open(path) as f:
            content = f.readlines()
        max_lon, min_lon, max_lat, min_lat = 0, 0, 0, 0
        for line in content:
            words = line.split()
            if len(words) >= 1:
                if words[0] == 'min.':
                    if words[1] == 'latitude':
                        max_lat = float(words[7])
                        min_lat = float(words[3])
                    if words[1] == 'longitude':
                        max_lon = float(words[7])
                        min_lon = float(words[3])
        return max_lon, min_lon, max_lat, min_lat
    execlog('SLC_corners mli_%s_%s/%s_%s.mli.par > master_corners' %(r_looks, a_looks, master, pol))
    execlog('SLC_corners mli_%s_%s/%s_%s.mli.par > slave_corners' % (r_looks, a_looks, slave, pol))
    max_lon_m, min_lon_m, max_lat_m, min_lat_m = extract_corners('master_corners')
    max_lon_s, min_lon_s, max_lat_s, min_lat_s = extract_corners('slave_corners')
    max_lon = max_lon_m if max_lon_m > max_lon_s else max_lon_s
    min_lon = min_lon_m if min_lon_m < min_lon_s else min_lon_s
    max_lat = max_lat_m if max_lat_m > max_lat_s else max_lat_s
    min_lat = min_lat_m if min_lat_m < min_lat_s else min_lat_s
    execlog('wget "http://opentopo.sdsc.edu/otr/getdem?demtype=SRTMGL1&west=%f&south=%f&east=%f&north=%f&outputFormat=GTiff" -O dem/%s_dem.tif' %(min_lon, min_lat, max_lon, max_lat, interferogram_str))
def Import_DEM():
    execlog('srtm2dem dem/%s_dem.tif dem/%s_dem dem/%s_dem.par 3 - -' %(interferogram_str, interferogram_str, interferogram_str))
def getWidth():
    global width, r_pixel_size, a_pixel_size, lat
    with open('mli_%s_%s/%s_%s.mli.par' %(r_looks, a_looks, master, pol)) as f:
        content = f.readlines()
    for line in content:
        words = line.split()
        if len(words) > 0:
            if words[0] == 'range_samples:':
                width = words[1]
            if words[0] == 'range_pixel_spacing:':
                r_pixel_size = float(words[1])
            if words[0] == 'azimuth_pixel_spacing:':
                a_pixel_size = float(words[1])
            if words[0] == 'center_latitude:':
                lat = float(words[1])
def DEM_geocode():
    '''
    Use perl script mk_geo_rdcal to generate lockup table between SAR to geographic geometry and transform the dam to SAR geometry the script have 3 stages
    :return:
    '''
    pixel_siz = a_pixel_size if a_pixel_size < r_pixel_size else r_pixel_size
    deg_pixel_size = pixel_siz / (111319.9 * np.cos(np.deg2rad(lat)))
    execlog('mk_geo_radcal mli_%s_%s/%s_%s.mli mli_%s_%s/%s_%s.mli.par dem/%s_dem dem/%s_dem.par geo/%s.dem geo/%s.dem_par geo %s %f 0 2 -s .7 -e .35 -p -c -d' %(
        r_looks, a_looks, master, pol, r_looks, a_looks, master, pol, interferogram_str, interferogram_str,
        interferogram_str, interferogram_str, interferogram_str, deg_pixel_size))
    execlog(
        'mk_geo_radcal mli_%s_%s/%s_%s.mli mli_%s_%s/%s_%s.mli.par dem/%s_dem dem/%s_dem.par geo/%s.dem geo/%s.dem_par geo %s %f 1 2 -s .7 -e .35 -p -c -d' % (
        r_looks, a_looks, master, pol, r_looks, a_looks, master, pol, interferogram_str, interferogram_str,
        interferogram_str, interferogram_str, interferogram_str, deg_pixel_size))
    execlog(
        'mk_geo_radcal mli_%s_%s/%s_%s.mli mli_%s_%s/%s_%s.mli.par dem/%s_dem dem/%s_dem.par geo/%s.dem geo/%s.dem_par geo %s %f 2 2 -s .7 -e .35 -p -c -d' % (
        r_looks, a_looks, master, pol, r_looks, a_looks, master, pol, interferogram_str, interferogram_str,
        interferogram_str, interferogram_str, interferogram_str, deg_pixel_size))
    execlog(
        'mk_geo_radcal mli_%s_%s/%s_%s.mli mli_%s_%s/%s_%s.mli.par dem/%s_dem dem/%s_dem.par geo/%s.dem geo/%s.dem_par geo %s %f 3 2 -s .7 -e .35 -p -c -d' % (
        r_looks, a_looks, master, pol, r_looks, a_looks, master, pol, interferogram_str, interferogram_str,
        interferogram_str, interferogram_str, interferogram_str, deg_pixel_size))

def Resampling():
    '''
    Using shell scrip S1_coref_TOPS to co-register slvae image to master image and calculate the differential interferogram
    :return:
    '''
    execlog('echo slc/%s_iw%d_%s.slc slc/%s_iw%d_%s.slc.par slc/%s_iw%d_%s.tops_par > SLC_%s_tab' %(master, 1, pol, master, 1, pol, master, 1, pol, master))
    execlog('echo slc/%s_iw%d_%s.slc slc/%s_iw%d_%s.slc.par slc/%s_iw%d_%s.tops_par >> SLC_%s_tab' % (
    master, 2, pol, master, 2, pol, master, 2, pol, master))
    execlog('echo slc/%s_iw%d_%s.slc slc/%s_iw%d_%s.slc.par slc/%s_iw%d_%s.tops_par >> SLC_%s_tab' % (
    master, 3, pol, master, 3, pol, master, 3, pol, master))
    execlog('echo slc/%s_iw%d_%s.slc slc/%s_iw%d_%s.slc.par slc/%s_iw%d_%s.tops_par > SLC_%s_tab' % (
    slave, 1, pol, slave, 1, pol, slave, 1, pol, slave))
    execlog('echo slc/%s_iw%d_%s.slc slc/%s_iw%d_%s.slc.par slc/%s_iw%d_%s.tops_par >> SLC_%s_tab' % (
        slave, 2, pol, slave, 2, pol, slave, 2, pol, slave))
    execlog('echo slc/%s_iw%d_%s.slc slc/%s_iw%d_%s.slc.par slc/%s_iw%d_%s.tops_par >> SLC_%s_tab' % (
        slave, 3, pol, slave, 3, pol, slave, 3, pol, slave))
    execlog('echo slc/%s_iw%d_%s.rslc slc/%s_iw%d_%s.rslc.par slc/%s_iw%d_%s.rtops_par > SLCR_%s_tab' % (
        slave, 1, pol, slave, 1, pol, slave, 1, pol, slave))
    execlog('echo slc/%s_iw%d_%s.rslc slc/%s_iw%d_%s.rslc.par slc/%s_iw%d_%s.rtops_par >> SLCR_%s_tab' % (
        slave, 2, pol, slave, 2, pol, slave, 2, pol, slave))
    execlog('echo slc/%s_iw%d_%s.rslc slc/%s_iw%d_%s.rslc.par slc/%s_iw%d_%s.rtops_par >> SLCR_%s_tab' % (
        slave, 3, pol, slave, 3, pol, slave, 3, pol, slave))
    execlog('S1_coreg_TOPS SLC_%s_tab %s SLC_%s_tab %s SLCR_%s_tab geo/%s_dem.rdc %s %s - - 0.6 0.02 0.8' %(master, master, slave, slave, slave, interferogram_str, r_looks, a_looks))
    
def getDEMwidth():
    global dem_width
    with open('geo/%s.dem_par' %interferogram_str) as f:
        content = f.readlines()
    for line in content:
        words = line.split()
        if len(words) > 0:
            if words[0] == 'width:':
                dem_width =  words[-1]
def Interferogram():
    '''
    Compute interferogram
    '''
    execlog('SLC_intf %s.rslc %s.rslc %s.rslc.par %s.rslc.par %s.off %s.int %s %s' %(master, slave, master, slave, interferogram_str, interferogram_str, r_looks, a_looks))
def Flattening():
    '''
    subtructe simulated unwrap phase from interferogram
    '''
    execlog('sub_phase %s.int %s.sim_unw %s.diff_par flat_%s.int 1' %(interferogram_str, interferogram_str, interferogram_str, interferogram_str))
def Filtering():
    '''
    preforme adaptive filter on interferogram 
    '''
    execlog('adf flat_%s.int filt_flat_%s.int filt_%s.ccw %s 1.0 32 7 - 0 0 .7' %(interferogram_str, interferogram_str, interferogram_str, width))
def Unwrapping():
    execlog('rascc_mask filt_%s.ccw %s.rmli %s 1 1 0 1 1 %s 0. 0.1 0.9 1. .35 1 filt_%s.mask.ras' %(interferogram_str, master, width, cc_threshold, interferogram_str))
    execlog('mcf filt_flat_%s.int filt_%s.ccw filt_%s.mask.ras filt_%s.unw %s 1 - - - - 1 1 1024 1705 1639' %(interferogram_str, interferogram_str, interferogram_str, interferogram_str, width))
def Geocoding_back():
    execlog('geocode_back filt_flat_%s.int %s geo/%s_1.map_to_rdc geo_%s.int %s - 0 1' %(interferogram_str, width, interferogram_str, interferogram_str, dem_width))
    execlog('geocode_back %s.rmli %s geo/%s_1.map_to_rdc geo_%s.rmli %s - 0 0' %(master, width, interferogram_str, master, dem_width))
    execlog('geocode_back filt_%s.unw %s geo/%s_1.map_to_rdc geo_%s.unw %s - 0 0' %(interferogram_str, width, interferogram_str, interferogram_str, dem_width))
    execlog('cpx_to_real geo_%s.int geo_%s_real.int %s 4' %(interferogram_str, interferogram_str, dem_width))
def Make_headers():
    execlog('par2rsc.py geo_%s.unw geo/%s.dem_par -h 0 -g' %(interferogram_str, interferogram_str))
    execlog('par2rsc.py geo_%s_real.int geo/%s.dem_par -h 0 -g' %(interferogram_str, interferogram_str))
    execlog('par2rsc.py geo_%s.rmli geo/%s.dem_par -h 0 -g' %(master, interferogram_str))
    execlog('par2rsc.py geo/%s.dem geo/%s.dem_par -h 0 -g' %(interferogram_str, interferogram_str))
def Disp():
    execlog('rasrmg geo_%s.unw geo_%s.rmli %s' %(interferogram_str, master, dem_width))
    execlog('convert geo_%s.unw.ras geo_%s.unw.jpg' %(interferogram_str, interferogram_str))
    execlog('rasmph_pwr geo_%s.int geo_%s.rmli %s 1 1 0 1 1 1. .35 1 geo_%s.int.ras' %(interferogram_str, master, dem_width, interferogram_str))
    execlog('convert geo_%s.int.ras geo_%s.int.jpg' %(interferogram_str, interferogram_str))
def End():
    print '########## end proccesing ###############'
Process = ['Setupprocdir','Import_SLCs', 'Download_DEM', 'Import_DEM','getWidth','DEM_geocode','Resampling','getDEMwidth', 'Interferogram','Flattening','Filtering','Unwrapping', 'Geocoding_back','Make_headers', 'Disp','End']
Process_dict = {Process[i] : i for i in range(len(Process))}
Process_funcs = {'Setupprocdir':Setupprocdir,'Import_SLCs':Import_SLCs, 'Download_DEM':Download_DEM, 'Import_DEM':Import_DEM,'getWidth':getWidth,'DEM_geocode':DEM_geocode,'Resampling':Resampling,'getDEMwidth':getDEMwidth, 'Interferogram':Interferogram,'Flattening':Flattening,'Filtering':Filtering,'Unwrapping':Unwrapping, 'Geocoding_back':Geocoding_back,'Make_headers':Make_headers, 'Disp':Disp,'End':End}

arg_parser = argparse.ArgumentParser(description="This program process 2-pass sentinel interferogram from raw data to unwraped phase")
arg_parser.add_argument("master", help="Master sentinel SAR image data base dir path")
arg_parser.add_argument("slave", help="Slave sentinel SAR image data base dir path")
arg_parser.add_argument("-s", help="start processing at one of -- " + string.join(Process[:-1], "','"))
arg_parser.add_argument("-e", help="end processing at one of -s following process")
arg_parser.add_argument("--m_name", help="name of master file, if not spesipy taken to by master dir name")
arg_parser.add_argument("--s_name", help="name of slave file, if not spesipy taken to by slave dir name")
arg_parser.add_argument("--pol", help="SLC polarization to extract (hh,hv,vh,vv) default vv")
arg_parser.add_argument("--r_looks", help="number of range looks default: 20")
arg_parser.add_argument("--a_looks", help="number of azimuth looks default: 4")
arg_parser.add_argument("--cc", help="unwraping coherince threshold default: 0.2")
arg_parser.add_argument("--clean", help="delete all but output files defualt: false")
arg_parser.add_argument("--orbit_files", help="path to orbit files directory, if not spesfied assume their is a direcory named 'orbit_files' in the working direcory")
args = arg_parser.parse_args()


master_path = args.master
slave_path = args.slave
if args.m_name:
    master = args.m_name
else:
    master = master_path.split('/')[-1]
if args.s_name:
    slave = args.s_name
else:
    slave = slave_path.split('/')[-1]
interferogram_str = args.master + '_' + args.slave
cmd_logfile = interferogram_str + '_cmd_log'
message_logfile = interferogram_str + '_msg_log'
if args.pol:
    if not args.pol in ('hh', 'hv', 'vh', 'vv'):
        print args.pol + 'is not a valid polarization'
        arg_parser.print_help()
    pol = args.pol
else:
    pol = 'vv'
if args.r_looks:
    r_looks = args.r_looks
else:
    r_looks = '20'
if args.a_looks:
    a_looks = args.a_looks
else:
    a_looks = '4'
if args.cc:
    cc_threshold = args.cc
else:
    cc_threshold = '0.2'
if args.clean:
    clean = True
else:
    clean = False
if args.orbit_files:
    orbit_files = args.orbit_files
else:
    ls = os.listdir('.')
    if 'orbit_files' not in ls:
        print 'no orbit files directory'
        arg_parser.print_help()
        exit(1)
    else:
        orbit_files = 'orbit_files'
    clean = False
if args.s:
    if not args.s in Process:
        print args.s + "not a process"
        arg_parser.print_help()
        exit(1)
    stage = args.s
else:
    stage = Process[0]

if args.e:
    if not args.e in Process:
        print args.e + "not a process"
        arg_parser.print_help()
        exit(1)
    if Process_dict[args.e] < Process_dict[args.s]:
        print args.s + " should be before " + args.e
    end = args.s
else:
    end = Process[-1]

width = 0
r_pixel_size = 0
a_pixel_size = 0
lat = 0
dem_width = 0
skipping = False

if Process_dict[stage] > 4:
    getWidth()
if Process_dict[stage] > 7:
    getDEMwidth()
for i in range(Process_dict[stage], Process_dict[end]):
    stage = Process[i]
    Process_funcs[Process[i]]()





