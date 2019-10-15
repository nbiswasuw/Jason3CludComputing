# Jason3CludComputing
The "www" directory is the Jason 3 server hosted at UW.

"HeightExtractor" C# based code is used to:
1) Detect lates altimeter IGDR product from PODAAC/AVISO FTP server
2) download of the latest product if not already downloaded
3) Unzip the latest downloaded products  
4) Extract the coordinates of altimeter data using bankfull river extent
Input: Jason 3 IGDR Data server (PODAAC/AVISO FTP)
Output: Extracted coordinates and heights of altimeter data using bankfull width database 

"Visualizer.py" is for processing altimeter timeseries. The specific tasks of this python code is:
1) Take altimeter datasets and apply K Means Clustering to get static river width based heights
2) Go to GEE to retrieve closest available Sentinel 1 SAR imagery at the time of Jason 3 altimeter pass
3) Apply look angle correction, speckle filtering, terrain correction and get the corrected imagery product
4) Retrieve the backscatter coefficient using the altimeter coordinates
5) Filter the altimeter locations with Sentinel 1 water pixels
6) Apply Interquartile Range(IQR) filtering to filter out unrealistic heights
7) Prepare the dynamic river width based rievr heights with IQR filtering
Input: 4) of the "HeightExtractor" C# Code
Output: Timseseries
