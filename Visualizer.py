#!"C:\Users\nbiswas\Anaconda2\python.exe"

import urllib
# import re
# from urllib2 import HTTPError
import os
import datetime
import requests
from bs4 import BeautifulSoup
import ee

ee.Initialize()
waterThresh = -14;
angle_threshold_1 = ee.Number(45.4);
angle_threshold_2 = ee.Number(31.66);
  
import numpy
from sklearn.cluster import KMeans
import csv
 
        
class AltimeterExtraction(object):
    def __init__(self, locationfile = './Bin/Location_Data.txt'):
        filecontent = open(locationfile, 'r')
        content = csv.DictReader(filecontent, delimiter='\t')
        
        self.stations = []
        self.altpasses = []
        self.minlats = []
        self.maxlats = []
        self.minlons = []
        self.maxlons = []
        self.geoidh = []
        for row in content:
            self.stations.append(row['StationID'])
            self.altpasses.append(row['Pass'])
            self.minlats.append(float(row['Start_Y']))
            self.maxlats.append(float(row['End_Y']))
            self.minlons.append(float(row['Start_X']))
            self.maxlons.append(float(row['End_X']))
            self.geoidh.append(float(row['GeoidH']))
        #self.startdate =
        
        print self.stations 
        
    def altimeterdownloader(self):
        passes = list(set(self.altpasses))
        for passs in passes:
            print passs
            for cycle in xrange(125):
                dataserver = 'https://data.nodc.noaa.gov/jason3/igdr/igdr/cycle' + str(cycle).zfill(3) + '/'
                site = requests.get(dataserver)
                html = site.text
                soup = BeautifulSoup(html, features="lxml")
                table = soup.findAll('td')
                for tr in table:
                    if 'JA3' in tr.text and '_' + str(passs).zfill(3) + '_' in tr.text:
                        print tr.text
                        urllib.urlretrieve(dataserver + tr.text, tr.text)
                
                    
    def altimeterprocess(self, locationfile = 'Location_Data.txt'):
        filecontent = open(locationfile, 'r')
        content = csv.DictReader(filecontent, delimiter='\t')
        
        stations = []
        altpasses = []
        minlats = []
        maxlats = []
        minlons = []
        maxlons = []
        geoidh = []
        for row in content:
            stations.append(row['StationID'])
            altpasses.append(row['Pass'])
            minlats.append(float(row['Start_Y']))
            maxlats.append(float(row['End_Y']))
            minlons.append(float(row['Start_X']))
            maxlons.append(float(row['End_X']))
            geoidh.append(float(row['GeoidH']))
            
        for station in stations:
            print station, geoidh[stations.index(station)], minlats[stations.index(station)], maxlats[stations.index(station)], minlons[stations.index(station)], maxlons[stations.index(station)]
            if minlats[stations.index(station)] < maxlats[stations.index(station)]:
                minlat = minlats[stations.index(station)]
                maxlat = maxlats[stations.index(station)]
            else:
                minlat = maxlats[stations.index(station)]
                maxlat = minlats[stations.index(station)]
            
            vspass = altpasses[stations.index(station)]
            
#             p = open(r'Altimeter/Extraction/Station_' + vstation + '.txt','w')
#             p.write('Date\tlatitude\tlongitude\theight\tBS\n')
#             p.close()
#             print('Virtual Station: ' + vstation + ', Virtual Pass: ' + vspass + ', Minimum Latitude: ' + str(minlat) + ', Maximum Latitude: '+ str(maxlat) + ', Geoid Constant: ' + str(geoidh))
#             
            datadir = r'IGDRData'
            for fn in os.listdir(datadir):
                if '_' + str(int(vspass)).zfill(3) + '_' in fn:
                    print fn
                    dataset = Dataset(os.path.join(datadir, fn))
                    lat = dataset.variables['lat']
                    lon = dataset.variables['lon']
                    meas_ind = dataset.variables['meas_ind']
                    time = dataset.variables['time']
                    model_dry_tropo_corr = dataset.variables['model_dry_tropo_corr']
                    model_wet_tropo_corr = dataset.variables['model_wet_tropo_corr']
                    iono_corr_gim_ku = dataset.variables['iono_corr_gim_ku']
                    solid_earth_tide = dataset.variables['solid_earth_tide']
                    pole_tide = dataset.variables['pole_tide']
                    alt_state_flag_ku_band_status = dataset.variables['alt_state_flag_ku_band_status']
                    lon_20hz = dataset.variables['lon_20hz']
                    lat_20hz = dataset.variables['lat_20hz']
                    ice_qual_flag_20hz_ku = dataset.variables['ice_qual_flag_20hz_ku']
                    time_20hz = dataset.variables['time_20hz']
                    alt_20hz = dataset.variables['alt_20hz']
                    ice_range_20hz_ku = dataset.variables['ice_range_20hz_ku']
                    ice_sig0_20hz_ku = dataset.variables['ice_sig0_20hz_ku']                
                     
                    initime = datetime.datetime(2000, 1, 1,0,0,0)
      
                    for i in xrange(len(lat)):
                        if model_dry_tropo_corr[i] != 32767 and model_wet_tropo_corr[i] != 32767 and iono_corr_gim_ku[i] != 32767 and solid_earth_tide[i] != 32767 and pole_tide[i] != 32767 and alt_state_flag_ku_band_status[i] == 0:
                            media_corr = model_dry_tropo_corr[i] + model_wet_tropo_corr[i] + iono_corr_gim_ku[i] + solid_earth_tide[i] + pole_tide[i]
                            for j in xrange(len(meas_ind)):
                                if ice_qual_flag_20hz_ku[i, j] !=1 and lat_20hz[i, j] != 2147483647:
                                    longitude = lon_20hz[i, j]
                                    latitude = lat_20hz[i, j]
                                    finaldate = initime + datetime.timedelta(seconds=float(time_20hz[i, j]))
                                    if latitude>=minlat and latitude<=maxlat:
                                        height = alt_20hz[i, j] -(media_corr + ice_range_20hz_ku[i, j]) - 0.7
                                        bs = ice_sig0_20hz_ku[i, j]
                                        print str(latitude) 
                                        print str(longitude)
                                        print str(height - geoidh)
                                        print str(bs)
                                        
                                        with open(r'AltimeterHeights/StationID_' + station + "_" + datetime.datetime.strftime(finaldate, '%Y-%m-%d') + '.txt', 'a') as txt:
                                            txt.write(str(latitude) + '\t' + str(longitude) + '\t' + str(height - geoidh) + '\t' + str(bs) + '\n')
        print 'Data processed successfully.'
 
 
    def kmeanscluster(self, vstation = 2):
        for vstation in self.stations:
            print vstation
            outfile = open(r'Timeseries_KMeans/Station_' + vstation + '.txt', 'w')
            outfile.write('Date,Height\n')
            outfile.close()
            allHeights = []
            datescol = []
            lines = []
            
            altimeterpath = 'AltimeterHeights/'
            for fn in os.listdir(altimeterpath):
                if fn[:3] == vstation:
                    print fn
                    infile = open(r'AltimeterHeights/' + fn, 'r')
                    filecontent = csv.DictReader(infile, delimiter = '\t')
                    for row in filecontent:
                        date = row['Date']
                        allHeights.append(float(row['H(m)']))
                        lines.append(row)
                        datescol.append(datetime.datetime.strptime(row['Date'], '%Y-%m-%d'))
            dates = sorted(list(set(datescol)))
            
            heightsData = numpy.asarray(allHeights)
            q75, q25 = numpy.percentile(heightsData, [75, 25])
            IQR = q75-q25
            loweroutlier = q25 - 1.5*IQR
            upperoutlier = q75+1.5*IQR
                      
            for date in dates:
                heights = []
                for row in lines:
                    if date == datetime.datetime.strptime(row['Date'], '%Y-%m-%d'):
                        if float(row['H(m)'])>=loweroutlier and float(row['H(m)'])<=upperoutlier:
                            heights.append(float(row['H(m)']))
                 
                if len(heights)>3:
                    kmeans = KMeans(n_clusters=2)
                    cycleheights = numpy.asarray(heights)
                    rangeH = numpy.amax(cycleheights) - numpy.amin(cycleheights)
#                     print 'Initial Range: ' + str(rangeH) + ", Average: " + str(numpy.average(cycleheights))
#                     print 'Initial Count: ' + str(len(cycleheights))
                    heights =0
                    while rangeH>5.0:
                        kmeans.fit(cycleheights.reshape(-1, 1))
                        label = kmeans.predict(cycleheights.reshape(-1, 1))
                        centroid = kmeans.cluster_centers_
                        classarray = label.tolist()
                        occur0 = classarray.count(0)
                        occur1 = classarray.count(1)
                          
                        if occur0>occur1:
                            cycleheights = numpy.delete(cycleheights, numpy.where(label==1))
                            rangeH = numpy.amax(cycleheights) - numpy.amin(cycleheights)
                        else:
                            cycleheights = numpy.delete(cycleheights, numpy.where(label==0))
                            rangeH = numpy.amax(cycleheights) - numpy.amin(cycleheights)
#                     print 'After K Means, Range: ' + str(rangeH)  + ", Average: " + str(numpy.average(cycleheights))
#                     print 'After K Means, Count: ' + str(len(cycleheights))
                      
                    stdev = numpy.std(cycleheights, ddof=1)
#                     print 'First Standard Deviation: '+ str(stdev)
                    while stdev>0.3:
                        devArray = numpy.absolute(cycleheights - numpy.average(cycleheights))
                        cycleheights = numpy.delete(cycleheights, numpy.argmax(devArray))
                        stdev = numpy.std(cycleheights, ddof=1)
                      
                    height = numpy.average(cycleheights)
#                     print 'Final Standard Deviation: '+ str(stdev)
#                     print 'Final Count: ' + str(len(cycleheights))
#                     print 'date: ' + datetime.datetime.strftime(date, '%Y-%m-%d') + ", height: " + str(round(height, 3))
                    with open('Timeseries_KMeans/Station_'+ vstation + '.txt', 'a') as txt:
                        txt.write(datetime.datetime.strftime(date, '%Y-%m-%d') + "," + str(round(height, 3)) + '\n')
                else:
                    if len(heights)>0:
                        print datetime.datetime.strftime(date, '%Y-%m-%d'), len(heights)
                        height = sum(heights)/len(heights)
                        print 'date: ' + datetime.datetime.strftime(date, '%Y-%m-%d') + ", height: " + str(round(height, 3))
                        with open('Timeseries_KMeans/Station_'+ vstation + '.txt', 'a') as txt:
                            txt.write(datetime.datetime.strftime(date, '%Y-%m-%d') + "," + str(round(height, 3)) + '\n')



        
    def watertestpoint(self, lat=17.196052923913715,lon=95.62327072739777, date1='2018-06-01'):
        lat = ee.Number(lat)
        lon = ee.Number(lon)
#         print lat, lon
        datep = datetime.datetime.strptime(date1, "%Y-%m-%d")
        date2 = datep + datetime.timedelta(days = -30)
        
        point = ee.Geometry.Point([lon,lat])
  
        S1 = ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(point).filterDate(date2, date1)
        S1 = S1.map(self.maskByAngle)
        S1 = S1.select('VV').median().rename('VV')
        S1 = S1.focal_median(100,'circle','meters').rename('VV')
        WaterMask = S1.lt(waterThresh)
        flag = S1.reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': point,
            'scale': 10
        })
        return flag.get("VV").getInfo()

  
    def maskByAngle(self, img):
        I = ee.Image(img)
        angle = I.select('angle')
        mask1 = angle.lt(angle_threshold_1)
        mask2 = angle.gt(angle_threshold_2)
        I = I.updateMask(mask1)
        return I.updateMask(mask2)
  
    

    def testWater(self):
        for station in self.stations:
            infilepath = 'AltimeterHeights/' + str(station).zfill(3) + '.txt'
            sob = 'Date\tH\tSAR'
            infile = open(infilepath, 'r')
            infile1 = csv.DictReader(infile, delimiter = '\t')
            lat = []
            lon = []
            dates = []
            heights = []
            for row in infile1:
                lat.append(float(row['Lat(D)']))
                lon.append(float(row['Lon(D)']))
                dates.append(row['Date'])
                heights.append(row['H(m)'])
            for i in xrange(len(lat)):   
                print lat[i], lon[i], dates[i]
                try:
                    x = self.watertestpoint(lat[i], lon[i], dates[i])
                    sob = sob + '\n' + dates[i] + '\t' + heights[i] + '\t' + str(x)
                except:
                    continue;
            with open('SARGEE/' + str(station).zfill(3) + '.txt', 'w') as txt:
                txt.write(sob)
    def rmsarextract(self, sarthreshold = -13.0):
        for vstation in self.stations:
            print vstation
            outfile = open(r'Timeseries_RMSAR/Station_' + vstation + '.txt', 'w')
            sob = 'Date,Height'
            outfile.close()
            allHeights = []
            datescol = []
            lines = []
            
            altimeterpath = 'SARGEE/'
            for fn in os.listdir(altimeterpath):
                if fn[:3] == vstation:
                    print fn
                    infile = open(r'SARGEE/' + fn, 'r')
                    filecontent = csv.DictReader(infile, delimiter = '\t')
                    for row in filecontent:
                        date = row['Date']
                        allHeights.append(float(row['H(m)']))
                        lines.append(row)
                        datescol.append(datetime.datetime.strptime(row['Date'], '%Y-%m-%d'))
            dates = sorted(list(set(datescol)))

             
            for date in dates:
                heights = []
                for row in lines:
                    if row['SAR']!='None' and date == datetime.datetime.strptime(row['Date'], '%Y-%m-%d') and float(row['SAR'])<=sarthreshold:
                        heights.append(float(row['H']))
                height = 0
                if len(heights)>0:
                    height = sum(heights)/len(heights)
                    sob = sob + '\n' + datetime.datetime.strftime(date, '%Y-%m-%d') + "," + str(round(height, 3))
            with open(outfile, 'w') as txt:
                txt.write(sob)
        print 'Finished writing file successfully.'

    def sarrearrange(self):
        for station in self.stations:
            print station
            if int(station)>=235:
                infile = open(r'SARGEE/' + str(station).zfill(3) + '.txt', 'r')
                filecontent = csv.DictReader(infile, delimiter = '\t')
                datescol = []
                lines = []
                for row in filecontent:
                    date = row['Date']
                    lines.append(row)
                    datescol.append(datetime.datetime.strptime(row['Date'], '%Y-%m-%d'))
                dates = sorted(list(set(datescol)))
                 
                for date in dates:
                    outfile = 'SARGEE/' + str(station).zfill(3) + "_" + datetime.datetime.strftime(date, '%Y-%m-%d') + '.txt'
                    sob = 'Date\tH\tSAR'
                    for row in lines:
                        if date == datetime.datetime.strptime(row['Date'], '%Y-%m-%d'):
                            sob = sob + '\n' + datetime.datetime.strftime(date, '%Y-%m-%d') + '\t' + row['H'] + '\t' + row['SAR']
                    with open(outfile, 'w') as txt:
                        txt.write(sob)
        print 'Finished writing file successfully.'

    def iqrsar(self, sarthreshold = -13.0):
        for vstation in self.stations:
            print vstation
            outfile = r'Timeseries_RMSAR/Station_' + vstation + '.txt'
            sob = 'Date,Height'
            allHeights = []
            datescol = []
            lines = []
            
            altimeterpath = 'SARGEE/'
            for fn in os.listdir(altimeterpath):
                if fn[:3] == vstation:
                    print fn
                    infile = open(r'SARGEE/' + fn, 'r')
                    filecontent = csv.DictReader(infile, delimiter = '\t')
                    for row in filecontent:
                        date = row['Date']
                        allHeights.append(float(row['H']))
                        lines.append(row)
                        datescol.append(datetime.datetime.strptime(row['Date'], '%Y-%m-%d'))
            dates = sorted(list(set(datescol)))
             
            heightsData = numpy.asarray(allHeights)
            q75, q25 = numpy.percentile(heightsData, [75, 25])
            IQR = q75-q25
            loweroutlier = q25 - 1.5*IQR
            upperoutlier = q75+1.5*IQR

             
            sdates = []
            sheights = []
            for date in dates:
                heights = []
                for row in lines:
                    if row['SAR']!='None' and date == datetime.datetime.strptime(row['Date'], '%Y-%m-%d') and float(row['SAR'])<=sarthreshold:
                        if float(row['H'])>=loweroutlier and float(row['H'])<=upperoutlier:
                            heights.append(float(row['H']))
                height = 0
                if len(heights)>0:
                    height = sum(heights)/len(heights)
                    sdates.append(date)
                    sheights.append(height)
                    sob = sob + '\n' + datetime.datetime.strftime(date, '%Y-%m-%d') + "," + str(round(height, 3))
            with open(outfile, 'w') as txt:
                txt.write(sob)
                
        print 'Finished writing file successfully.'

    def sarvalues(self):
        altimeterpath = 'AltimeterHeights/'
        for fn in os.listdir(altimeterpath):
            sarpath = 'SARGEE/' + fn
            if os.path.exists(sarpath) == False:
                infilepath = altimeterpath + fn
                print infilepath
                sob = 'Date\tH\tSAR'
                infile = open(infilepath, 'r')
                infile1 = csv.DictReader(infile, delimiter = '\t')
                lat = []
                lon = []
                dates = []
                heights = []
                for row in infile1:
                    lat.append(float(row['Lat(D)']))
                    lon.append(float(row['Lon(D)']))
                    dates.append(row['Date'])
                    heights.append(row['H(m)'])
                for i in xrange(len(lat)):   
                    print lat[i], lon[i], dates[i]
                    try:
                        x = self.watertestpoint(lat[i], lon[i], dates[i])
                        sob = sob + '\n' + dates[i] + '\t' + heights[i] + '\t' + str(x)
                    except:
                        continue;
                with open(sarpath, 'w') as txt:
                    txt.write(sob)


if __name__ == '__main__':
    P = AltimeterExtraction()
    P.kmeanscluster()
    P.sarvalues()
    P.iqrsar()
    x = input("Print dksncn")
