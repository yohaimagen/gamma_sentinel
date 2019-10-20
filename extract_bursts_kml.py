#! /home/yohai/anaconda2/bin/python
import os, argparse, re

arg_parser = argparse.ArgumentParser(description="This program generate bursts kml from sentinel raw dir")
arg_parser.add_argument("path", help="path to sentinel raw dir")
arg_parser.add_argument("name", help="image name")
arg_parser.add_argument("-c", help="color for polygon lines one of [r:red, b:blue, g:green, y:yellow], defualt red")
args = arg_parser.parse_args()

if args.c:
    if args.c == 'r':
        color = 'ff0000ff'
    elif args.c == 'b':
        color = 'ffff5b33'
    elif args.c == 'g':
        color = '6414f00a'
    elif args.c == 'y':
        color = 'ff14f0fa'
    else:
        print 'not a valid color'
        exit(1)
else:
    color='ff0000ff'

kml='''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>%s.kml</name>
	<Style id="sh_ylw-pushpin">
		<IconStyle>
			<scale>1.3</scale>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
			</Icon>
			<hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
		</IconStyle>
		<BalloonStyle>
		</BalloonStyle>
		<LineStyle>
			<color>%s</color>
		</LineStyle>
		<PolyStyle>
			<color>00ffffff</color>
		</PolyStyle>
	</Style>
	<StyleMap id="msn_ylw-pushpin">
		<Pair>
			<key>normal</key>
			<styleUrl>#sn_ylw-pushpin</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#sh_ylw-pushpin</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="sn_ylw-pushpin">
		<IconStyle>
			<scale>1.1</scale>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
			</Icon>
			<hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
		</IconStyle>
		<BalloonStyle>
		</BalloonStyle>
		<LineStyle>
			<color>%s</color>
		</LineStyle>
		<PolyStyle>
			<color>00ffffff</color>
		</PolyStyle>
	</Style>
	<Placemark>
		<name>test_Polygon_2</name>
		<styleUrl>#msn_ylw-pushpin</styleUrl>
		<Polygon>
			<tessellate>1</tessellate>
			<outerBoundaryIs>
				<LinearRing>
					<coordinates>
						%s,%s,0 %s,%s,0 %s,%s,0 %s,%s,0 %s,%s,0 
					</coordinates>
				</LinearRing>
			</outerBoundaryIs>
		</Polygon>
	</Placemark>
</Document>
</kml>

'''


home_dir = '%s/annotation' %args.path
name = args.name
files = a = os.listdir(home_dir)

regex = re.compile(r'.*vv.*')

selected_files = sorted(list(filter(regex.search, files)))

for file in selected_files:
    cmd_strerror = os.strerror(os.system('S1_burstloc ' + home_dir +'/' + file + ' > temp_file'))
    if not cmd_strerror == 'Success':
        print 'Gamma error'
        exit(1)
    with open('temp_file') as f:
        content = f.readlines()
    for line in content:
        words = line.split()
        if len(words) > 0:
            if words[0] == 'Burst:':
                burst_kml = kml %(name + '_' + words[4] + '_' + words[2], color, color, words[10], words[9], words[12], words[11], words[14], words[13], words[16], words[15], words[10], words[9])
                with open(name + '_' + words[4] + '_' + words[2] + '.kml', "w") as text_file:
                    text_file.write(burst_kml)
                print 'outputed: ' + name + '_' + words[4] + '_' + words[2] + '.kml'
os.remove('temp_file')
