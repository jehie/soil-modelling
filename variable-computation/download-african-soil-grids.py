import csv
import urllib, os
from processing import Processing
from qgis._analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from qgis._core import QgsApplication
import GraduTools

qgishome = "C:/OSGeo4W64/apps/qgis-ltr/"
app = QgsApplication([], True)
app.setPrefixPath(qgishome, True)
app.initQgis()
os.environ['QGIS_DEBUG'] = '1'
Processing.initialize()


class data_pair:
    def __init__(self, download_name, real_name, short_name, folder, very_short_name, soiltype):
        """
        Simple object to store information about each file we are going to download
        :param download_name: Name in the WCS Service (Look for this in the Get Capabilities Document (
        http://webservices.isric.org/geoserver/ows?service=wcs&version=1.1.0&request=GetCapabilities, inside
        <wcs:Identifier> tags: eg.
        <wcs:Identifier>geonode:orcdrc_m_sl1_250m</wcs:Identifier>
        :param real_name:
        :param short_name:
        :param folder:
        :return:
        """
        self.download_name = download_name
        self.real_name = real_name
        self.short_name = short_name
        self.folder = folder
        self.very_short_name = very_short_name
        self.soiltype = soiltype


def write_log_file(output_directory, data_pairs):
    with open(os.path.join(output_directory, 'downloaded-soil-rasters.csv'), 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['Resolution'] + ['Path'] + ['Description'] + ['Short Name'] + ['Soil Type'])
        for file in data_pairs:
            csvwriter.writerow(
                ['250'] + [os.path.join(download_directory, file.folder, file.download_name.split(':')[1] + ".tif")] + [
                    file.real_name] + [file.very_short_name] + [file.soiltype])


def construct_short_name(name):
    if name in "SUBSOIL_SOC_ha":
        return "SH"
    if name in "SUBSOIL_SOC_kg":
        return "SK"
    if name in "TOPSOIL_SOC_ha":
        return "TH"
    if name in "TOPSOIL_SOC_kg":
        return "TK"


def write_combined_log_file(output_directory, soiltypes):
    with open(os.path.join(output_directory, 'combined-soil-rasters.csv'), 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(
            ['Resolution'] + ['Path'] + ['Description'] + ['Short Name'] + ['Short Names'] + ['Soil Type'])
        for soiltype in soiltypes:
            input_files = ""
            input_descriptions = ""
            input_short_names = ""
            for data in soiltypes[soiltype]:
                input_files = input_files + data.output_uri + ","
                input_descriptions = input_descriptions + data.real_name + ","
                input_short_names = input_short_names + data.short_name + ","

            csvwriter.writerow(['250'] + [os.path.join(output_directory, soiltype + ".tif")] + [input_descriptions] + [
                construct_short_name(soiltype)] + [input_short_names] + [soiltype])


def combine_rasters(rasters, raster_out):
    entries = []

    i = 1
    calculation = "("
    for r in rasters:
        # Define band1
        rast = QgsRasterCalculatorEntry()
        rast.ref = 'r' + str(i) + '@1'
        rast.raster = r.raster
        rast.bandNumber = 1
        entries.append(rast)

        if i == len(rasters):
            calculation = calculation + rast.ref
        else:
            calculation = calculation + rast.ref + " + "
        i = i + 1

    calculation = calculation + ")" + "/" + str(len(rasters))

    # Process calculation with input extent and resolution
    raster1 = rasters[0].raster
    calc = QgsRasterCalculator(calculation, raster_out, 'GTiff', raster1.extent(), raster1.width(), raster1.height(),
                               entries)
    calc.processCalculation()


# Configs
download_directory = "F:/Gradu/AfricanSoilGrids/WCS/"  # Where to download the files (In your local drive)

# Data Pair Objects to handle what we want to download - extend by creating new objects
data_to_download = []
data_to_download.extend(
    # SOC G PER KG
    [data_pair("geonode:orcdrc_m_sl1_250m",
               "Soil organic carbon content (fine earth fraction) in g per kg at depth 0.00 m",
               "SOC_g_per_kg_0.00m",
               "SOC_kg",
               "SK1",
               "TOPSOIL"),
     data_pair("geonode:orcdrc_m_sl2_250m",
               "Soil organic carbon content (fine earth fraction) in g per kg at depth 0.05 m",
               "SOC_g_per_kg_0.05m",
               "SOC_kg",
               "SK2",
               "TOPSOIL"),
     data_pair("geonode:orcdrc_m_sl3_250m",
               "Soil organic carbon content (fine earth fraction) in g per kg at depth 0.15 m",
               "SOC_g_per_kg_0.15m",
               "SOC_kg",
               "SK3",
               "TOPSOIL"),
     data_pair("geonode:orcdrc_m_sl4_250m",
               "Soil organic carbon content (fine earth fraction) in g per kg at depth 0.30 m",
               "SOC_g_per_kg_0.30m",
               "SOC_kg",
               "SK4",
               "SUBSOIL"),
     data_pair("geonode:orcdrc_m_sl5_250m",
               "Soil organic carbon content (fine earth fraction) in g per kg at depth 0.60 m",
               "SOC_g_per_kg_0.60m",
               "SOC_kg",
               "SK5",
               "SUBSOIL"),
     # SOC T PER HA
     data_pair("geonode:ocstha_m_sd1_250m",
               "Soil organic carbon stock in tonnes per ha for depth interval 0.00 m - 0.05 m",
               "SOC_t_per_ha_0.00-0.05m",
               "SOC_ha",
               "SC1",
               "TOPSOIL"),
     data_pair("geonode:ocstha_m_sd2_250m",
               "Soil organic carbon stock in tonnes per ha for depth interval 0.05 m - 0.15 m",
               "SOC_t_per_ha_0.05-0.15m",
               "SOC_ha",
               "SC2",
               "TOPSOIL"),
     data_pair("geonode:ocstha_m_sd3_250m",
               "Soil organic carbon stock in tonnes per ha for depth interval 0.15 m - 0.30 m",
               "SOC_t_per_ha_0.15m-0.30m",
               "SOC_ha",
               "SC3",
               "SUBSOIL"),
     data_pair("geonode:ocstha_m_sd4_250m",
               "Soil organic carbon stock in tonnes per ha for depth interval 0.30 m - 0.60 m",
               "SOC_t_per_ha_0.30m-0.30m",
               "SOC_ha",
               "SC4",
               "SUBSOIL")
     ])

# Loop over the downloadble files list and store to correct folder
for file in data_to_download:
    print "Downloading: " + file.download_name + " to: " + os.path.join(download_directory, file.folder,
                                                                        file.download_name.split(':')[1] + ".tif")
    download_url = "http://webservices.isric.org/geoserver/ows?service=WCS&version=2.0.1" \
                   "&request=GetCoverage" \
                   "&CoverageId=" + file.download_name + \
                   "&subset=Long(38.281771435832226,38.37234746699569)" \
                   "&subset=Lat(-3.448906634066586,-3.345927432376734)"
    dir_path = os.path.join(download_directory, file.folder)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    output_uri = os.path.join(dir_path, file.download_name.split(':')[1] + ".tif")
    file.output_uri = output_uri
    urllib.urlretrieve(download_url, output_uri)
print "Download Complete!"

soiltypes = {}
for f in data_to_download:
    name = f.soiltype + "_" + f.folder
    if name in soiltypes:
        f.raster = GraduTools.load_raster(f.output_uri)
        soiltypes[name].append(f)
    else:
        soiltypes[name] = []
        f.raster = GraduTools.load_raster(f.output_uri)
        soiltypes[name].append(f)

for key in soiltypes:
    combined_path = os.path.join(download_directory, key + ".tif")
    combine_rasters(soiltypes[key], combined_path)
r1 = soiltypes["TOPSOIL_SOC_kg"]

write_log_file(download_directory, data_to_download)
write_combined_log_file(download_directory, soiltypes)
