# Google Earth Engine based Jason 3 height visualization

# About the system
The frontend portal of this system shows 166 virtual station locations of JASON-3 altimeter that cross a river in South and Southeast Asia. At these locations, two different types of altimeter height extraction are shown in near real-time. One is based on using only JASON-3 altimeter and assuming a static (fixed) river with. The other is based on latest river condition that is inferred from the most recent Sentinel-1 SAR imagery. The SAR image helps identify the most likely river width around the time of the JASON-3 overpass, which is then used to extract height only over the track that has the highest confidence of having water. For rivers that frequently change in width and direction due to seasonal hydrology (monsoon) or human impacts (dams, barrages, diversions), such a SAR-based JASON-3 altimeter height extraction has been shown to improve JASON-3 height estimation accuracy for medium to large rivers (> 300 m). The analysis to infer latest river conditions is done in a cloud computing environment using Google Earth Engine, which makes the entire process very efficient and minimizes the need for data download. This work is experimental in nature and users should use the estimated heights at their own risk. Our vision for the future is that such a system will cater to the strengths of the planned SWOT and NISAR missions, along with altimeters that will be flying by 2021, and rapidly provide users anywhere in the world, the best possible height estimate in near real-time to enable important decisions on the fly. 

# Citation
The standard citation for this portal and data is “Biswas, N., F. Hossain, M. Bonnema, H. Lee and M.A. Okeowo (2019) An Altimeter Height Extraction Technique for Dynamically Changing Rivers of South and South-East Asia, Remote Sensing of the Environment, vol. 221, pp. 24-37 (https://doi.org/10.1016/j.rse.2018.10.033).

# Directory Structure
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
