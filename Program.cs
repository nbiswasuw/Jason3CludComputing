using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Research.Science.Data.Imperative;
using System.Data.SQLite;
using System.IO;
using System.IO.Compression;
using System.Globalization;
using System.Net;
using HtmlAgilityPack;

namespace HeightExtractor
{
    class Program
    {
        static void Main(string[] args)
        {
            string rootdirectory = @"C:\Users\nbiswas\Desktop\UWPhD\AltimetryVisualization\Visualization\";
            string binDir = rootdirectory + @"Bin\";
            string granuledir = rootdirectory + @"IGDRData\";
            string virtualHdir = rootdirectory + @"AltimeterHeights\";
            string latloninfofilepath = binDir + "Location_Data.txt";
            WebClient ftpClient = new WebClient();
            ftpClient.Credentials = new NetworkCredential("nbiswas@uw.edu", "vWyEg5");
            string[] allTxt = File.ReadAllLines(latloninfofilepath);
            List<string> stations = new List<string>();
            List<string> downloadedFiles = new List<string>();
            List<string> netcFiles = new List<string>();

            Dictionary<string, int> passids = new Dictionary<string, int>();
            Dictionary<string, float> minlats = new Dictionary<string, float>();
            Dictionary<string, float> maxlats = new Dictionary<string, float>();
            Dictionary<string, float> hcorrs = new Dictionary<string, float>();

            for (int i = 0; i < allTxt.Length - 1; i++)
            {
                var elements = allTxt[i + 1].Split('\t');
                stations.Add(elements[9]);
                passids.Add(elements[9], int.Parse(elements[2]));
                if (float.Parse(elements[5]) < float.Parse(elements[7]))
                {
                    minlats.Add(elements[9], float.Parse(elements[5]));
                    maxlats.Add(elements[9], float.Parse(elements[7]));
                }
                else
                {
                    minlats.Add(elements[9], float.Parse(elements[7]));
                    maxlats.Add(elements[9], float.Parse(elements[5]));
                }

                hcorrs.Add(elements[9], float.Parse(elements[8]));
            }

            try
            {


                List<string> jason3Files = new List<string>();
                FtpWebRequest ftpRequest = (FtpWebRequest)WebRequest.Create("ftp://ftp-access.aviso.altimetry.fr/geophysical-data-record/jason-3/igdr/latest_data/");
                ftpRequest.Credentials = new NetworkCredential("nbiswas@uw.edu", "vWyEg5");
                ftpRequest.Method = WebRequestMethods.Ftp.ListDirectory;
                FtpWebResponse response = (FtpWebResponse)ftpRequest.GetResponse();
                StreamReader streamReader = new StreamReader(response.GetResponseStream());
                string line = streamReader.ReadLine();
                while (!string.IsNullOrEmpty(line))
                {
                    jason3Files.Add(line);
                    line = streamReader.ReadLine();
                }
                streamReader.Close();



                foreach (var pass in passids.Values.Distinct())
                {
                    for (int i = 0; i < jason3Files.Count; i++)
                    {
                        string j3ftp = "ftp://ftp-access.aviso.altimetry.fr/geophysical-data-record/jason-3/igdr/latest_data/" + jason3Files[i];
                        string j3filepath = granuledir + jason3Files[i];
                        if (int.Parse(jason3Files[i].Substring(16, 3)) == pass && !File.Exists(j3filepath))
                        {
                            Console.ForegroundColor = ConsoleColor.Magenta;
                            Console.WriteLine("Latest JA3 File: " + jason3Files[i]);
                            Console.ResetColor();
                            try
                            {
                                ftpClient.DownloadFile(j3ftp, j3filepath);
                                downloadedFiles.Add(jason3Files[i]);

                            }
                            catch (Exception error)
                            {
                                Console.ForegroundColor = ConsoleColor.Red;
                                Console.WriteLine("Error in download data from " + j3ftp + ", Error: " + error);
                                Console.ReadKey();
                                Console.ResetColor();
                            }
                        }

                    }
                }
            }
            catch (Exception)
            {
                Console.WriteLine("Thgere are some error, please check and come back again!");
            }


            try
            {
                Console.ForegroundColor = ConsoleColor.Cyan;
                Console.WriteLine("Extracting Virtual Station files ...");
                Console.ResetColor();

                if (downloadedFiles.Count == 0)
                {
                    Console.WriteLine("No new files found in the FTP server.");
                    Environment.Exit(0);
                }
                Console.ForegroundColor = ConsoleColor.Cyan;
                Console.WriteLine("Unzipping the latest virtual station files ...");
                Console.ResetColor();
                foreach (string element in downloadedFiles)
                {
                    string zippedfilepath = granuledir + element;
                    if (!File.Exists(zippedfilepath.Substring(0, zippedfilepath.Length - 4) + ".nc"))
                    {
                        netcFiles.Add(element.Substring(0, element.Length - 4) + ".nc");
                        ZipFile.ExtractToDirectory(zippedfilepath, granuledir);
                    }
                }
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("The selected virtual station file unzipped successfully.");
                Console.ResetColor();
            }
            catch (Exception error)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("Error in unzipping downloaded File. Error: " + error);
                Console.ResetColor();
            }

            foreach (string station in stations)
            {
                Console.WriteLine(station);
                foreach (string ncFile in netcFiles)
                {
                    try
                    {
                        string element = Path.GetFileName(ncFile);

                        string passID = element.Substring(16, 3);
                        int altpass = passids[station];
                        if (int.Parse(passID) == altpass)
                        {
                            StringBuilder sob = new StringBuilder();
                            sob.AppendLine("Date\tLat(D)\tLon(D)\tH(m)\tBS(dB)");

                            Console.WriteLine("Extracting Height: " + element);
                            double minlat = minlats[station];
                            double maxlat = maxlats[station];
                            double hcorr = hcorrs[station];

                            var dataset = Microsoft.Research.Science.Data.DataSet.Open(granuledir + element + "?openMode=readOnly");
                            int[] lat = dataset.GetData<int[]>("lat");
                            int[] lon = dataset.GetData<int[]>("lon");
                            sbyte[] meas_ind = dataset.GetData<sbyte[]>("meas_ind");
                            double[] time = dataset.GetData<double[]>("time");
                            short[] model_dry_tropo_corr = dataset.GetData<short[]>("model_dry_tropo_corr");
                            short[] model_wet_tropo_corr = dataset.GetData<short[]>("model_wet_tropo_corr");
                            short[] iono_corr_gim_ku = dataset.GetData<short[]>("iono_corr_gim_ku");
                            short[] solid_earth_tide = dataset.GetData<short[]>("solid_earth_tide");
                            short[] pole_tide = dataset.GetData<short[]>("pole_tide");
                            sbyte[] alt_state_flag_ku_band_status = dataset.GetData<sbyte[]>("alt_state_flag_ku_band_status");
                            int[,] lon_20hz = dataset.GetData<int[,]>("lon_20hz");
                            int[,] lat_20hz = dataset.GetData<int[,]>("lat_20hz");
                            sbyte[,] ice_qual_flag_20hz_ku = dataset.GetData<sbyte[,]>("ice_qual_flag_20hz_ku");
                            double[,] time_20hz = dataset.GetData<double[,]>("time_20hz");
                            int[,] alt_20hz = dataset.GetData<int[,]>("alt_20hz");
                            int[,] ice_range_20hz_ku = dataset.GetData<int[,]>("ice_range_20hz_ku");
                            short[,] ice_sig0_20hz_ku = dataset.GetData<short[,]>("ice_sig0_20hz_ku");

                            string datetime = dataset.GetAttr(1, "units").ToString();
                            DateTime refDate = DateTime.ParseExact(datetime.Substring(14, 19), "yyyy-MM-dd hh:mm:ss", CultureInfo.InvariantCulture);

                            double s_latlon = 0.000001;
                            double s_model_wet = 0.0001;
                            double s_model_dry = 0.0001;
                            double s_iono_corr = 0.0001;
                            double s_pole_tide = 0.0001;
                            double s_solid_earth_tide = 0.0001;
                            double s_alt = 0.0001;
                            double s_icerange_ku = 0.0001;
                            double s_ice_sig0_20hz = 0.01;

                            double media_corr;
                            double bsValue;
                            double height;
                            double latitude;
                            double longitude;

                            List<double> heights = new List<double>();
                            List<double> bsValues = new List<double>();

                            DateTime dataDate = new DateTime();
                            for (int i = 0; i < lat.Length; i++)
                            {
                                if (model_dry_tropo_corr[i] != 32767 && model_wet_tropo_corr[i] != 32767 && iono_corr_gim_ku[i] != 32767 && solid_earth_tide[i] != 32767 && pole_tide[i] != 32767 && alt_state_flag_ku_band_status[i] == 0)
                                {
                                    media_corr = model_dry_tropo_corr[i] * s_model_dry + model_wet_tropo_corr[i] * s_model_wet + iono_corr_gim_ku[i] * s_iono_corr + solid_earth_tide[i] * s_solid_earth_tide + pole_tide[i] * s_pole_tide;
                                    for (int j = 0; j < meas_ind.Length; j++)
                                    {
                                        if (ice_qual_flag_20hz_ku[i, j] != 1 && lat_20hz[i, j] != 2147483647 && lat_20hz[i, j] * s_latlon >= minlat && lat_20hz[i, j] * s_latlon <= maxlat)
                                        {
                                            height = alt_20hz[i, j] * s_alt - (media_corr + ice_range_20hz_ku[i, j] * s_icerange_ku) - 0.7 - hcorr;
                                            bsValue = ice_sig0_20hz_ku[i, j] * s_ice_sig0_20hz;
                                            heights.Add(height);
                                            bsValues.Add(bsValue);

                                            longitude = lon_20hz[i, j] * s_latlon;
                                            latitude = lat_20hz[i, j] * s_latlon;
                                            dataDate = refDate.AddSeconds(time_20hz[i, j]);
                                            sob.AppendLine(dataDate.ToString("yyyy-MM-dd") + "\t" + latitude.ToString("0.000000000000") + "\t" + longitude.ToString("0.000000000000") + "\t" + Math.Round(height, 2).ToString("0.00") + "\t" + bsValue.ToString("0.00"));
                                        }
                                    }
                                }
                            }

                            File.WriteAllText(virtualHdir + station + "_" + dataDate.ToString("yyyy-MM-dd") + ".txt", sob.ToString());
                            sob.Clear();
                            bsValues.Clear();
                            heights.Clear();
                        }

                    }
                    catch (Exception)
                    {
                        Console.WriteLine("Thgere are some error, please check and come back again!");
                        continue;
                    }
                    
                }
            }

        }
    }
}
