import csv
import re
import os
import processing
from processing.core import Processing
from qgis.core import QgsApplication, QgsVectorLayer, QgsMapLayerRegistry
from qgis.analysis import QgsGeometryAnalyzer, QgsZonalStatistics
import GeneralTools

qgishome = "C:/OSGeo4W64/apps/qgis-ltr/"
app = QgsApplication([], True)
app.setPrefixPath(qgishome, True)
app.initQgis()
os.environ['QGIS_DEBUG'] = '1'
Processing.initialize()

class predictor_object():
    def __init__(self, short_name, full_name, path, resolution):
        self.full_name = full_name
        self.short_name = short_name
        self.path = path
        self.resolution = resolution


def compute_raster_variables(dem_path, output_folder):
    """
    Method for creating Topographic variables.
    :param dem_path: Path to the input dem
    :return: object containing the computed variables
    """

    new_file_prefix = GeneralTools.find_basename_from_file(dem_path)

    # Create the output folder if it does not exists
    GeneralTools.create_folder_if_not_exists(os.path.join(output_folder, new_file_prefix))
    new_folder = new_file_prefix

    resol = int(re.findall(r'[0-9]+', dem_path)[0])

    input_raster = GeneralTools.load_raster(dem_path)

    ##Calculate extend and combine proper string
    ymax = input_raster.extent().yMaximum()
    ymin = input_raster.extent().yMinimum()
    xmax = input_raster.extent().xMaximum()
    xmin = input_raster.extent().xMinimum()
    extent_string = str(int(xmin)) + "," + str(int(xmax)) + "," + str(int(ymin)) + "," + str(int(ymax))

    ##Create names for the new files - stores to new folder
    slope_path = os.path.join(output_folder, new_folder, new_file_prefix + "_Slope.tif")
    aspect_path = os.path.join(output_folder, new_folder, new_file_prefix + "_Aspect.tif")
    profice_curvature_path = os.path.join(output_folder, new_folder, new_file_prefix + "_Profice_curvatures.tif")
    tangential_curvature_path = os.path.join(output_folder, new_folder, new_file_prefix + "_Tangential_Curvature.tif")
    first_order_derivative_ew_path = os.path.join(output_folder, new_folder,
                                                  new_file_prefix + "_First_order_derivatire_EW.tif")
    first_order_derivative_ns_path = os.path.join(output_folder, new_folder,
                                                  new_file_prefix + "_First_order_derivatire_NS.tif")
    second_order_derivative_dxx_path = os.path.join(output_folder, new_folder,
                                                    new_file_prefix + "_Second_order_derivatire_DXX.tif")
    second_order_derivative_dyy_path = os.path.join(output_folder, new_folder,
                                                    new_file_prefix + "_Second_order_derivatire_DYY.tif")
    second_order_derivative_dxy_path = os.path.join(output_folder, new_folder,
                                                    new_file_prefix + "_Second_order_derivatire_DXY.tif")

    irradiation_path = os.path.join(output_folder, new_folder,
                                    new_file_prefix + "_Irradiation.tif")
    insilation_time_path = os.path.join(output_folder, new_folder,
                                        new_file_prefix + "_InsilationTime.tif")
    diffuse_radiation_path = os.path.join(output_folder, new_folder,
                                          new_file_prefix + "_DiffuseRadiation.tif")
    ground_reflected_irradiation_path = os.path.join(output_folder, new_folder,
                                                     new_file_prefix + "_GroundReflectedIrradiation.tif")
    global_total_output_path = os.path.join(output_folder, new_folder,
                                            new_file_prefix + "_GlobalTotalOutput.tif")

    catchment_area_path = os.path.join(output_folder, new_folder,
                                       new_file_prefix + "_CatchmentArea.tif")
    slope_saga_path = os.path.join(output_folder, new_folder, new_file_prefix + "_SagaSlope.tif")
    twi_path = os.path.join(output_folder, new_folder, new_file_prefix + "_TWI.tif")
    tpi_path = os.path.join(output_folder, new_folder, new_file_prefix + "_TPI.tif")

    # Call the processing algorithm
    processing.runalg("grass:r.slope.aspect", dem_path, 0, 1, False, 1, 0, extent_string, 0,
                      slope_path,
                      aspect_path,
                      profice_curvature_path,
                      tangential_curvature_path,
                      first_order_derivative_ew_path,
                      first_order_derivative_ns_path,
                      second_order_derivative_dxx_path,
                      second_order_derivative_dyy_path,
                      second_order_derivative_dxy_path)

    processing.runalg("grass7:r.sun", dem_path,
                      aspect_path,
                      slope_path,
                      None, None, None, None, None, None,
                      180, 0.5, 0, 1, False, False, extent_string, 0,
                      irradiation_path,
                      insilation_time_path,
                      diffuse_radiation_path,
                      ground_reflected_irradiation_path,
                      global_total_output_path)

    processing.runalg("saga:catchmentarea", dem_path, 0, catchment_area_path)
    processing.runalg("saga:slopeaspectcurvature", dem_path, 6, 1, 1, slope_saga_path, None, None, None, None, None,
                      None, None, None, None, None, None)
    processing.runalg("saga:topographicwetnessindextwi", slope_saga_path, catchment_area_path, None, 1, 0, twi_path)
    processing.runalg("gdalogr:tpitopographicpositionindex", dem_path, 1, False, tpi_path)

    predictors = []
    predictors.extend(
        [predictor_object("SLO", "Slope", slope_path, resol),
         predictor_object("ASP", "Aspect", aspect_path, resol),
         predictor_object("PRC", "Profice Curvature Path", profice_curvature_path, resol),
         predictor_object("TAC", "Tangential Curvature Path", tangential_curvature_path, resol),
         predictor_object("FEW", "First Order Derivative EW", first_order_derivative_ew_path, resol),
         predictor_object("FNS", "First Order Derivative NS", first_order_derivative_ns_path, resol),
         predictor_object("SXX", "Second Order Derivative DXX", second_order_derivative_dxx_path, resol),
         predictor_object("SXY", "Second Order Derivative DXY", second_order_derivative_dxy_path, resol),
         predictor_object("SYY", "Second Order Derivative DYY", second_order_derivative_dyy_path, resol),
         predictor_object("CAA", "Catchment ARea", catchment_area_path, resol),
         predictor_object("TWI", "Topographic Wetness Index", twi_path, resol),
         predictor_object("TPI", "Topographic Position Index", tpi_path, resol),
         predictor_object("DTM", "Digital Terrain Model", dem_path, resol)
         ])

    return predictors


def reproject_rasters(raster_path):
    GeneralTools.load_raster(raster_path)


def create_study_area_shapefile(plot_list, buffer_size, output_path):
    uri = "file:///" + plot_list + "?crs=epsg:32737&delimiter=%s&xField=%s&yField=%s" % (";", "Long_X", "Lat_y")
    vlayer = QgsVectorLayer(uri, "VectorLayer", "delimitedtext")

    QgsGeometryAnalyzer().buffer(vlayer, output_path, buffer_size, False, False, -1)

    filename = os.path.basename(output_path)
    splitted_filename = filename.split(".")
    shape = QgsVectorLayer(output_path, splitted_filename[0], "ogr")
    QgsMapLayerRegistry.instance().addMapLayer(shape)
    return shape


def create_grass_created_raster_predictors(dem_directory, output_directory):
    grass_predictors = {}
    for dem_file in os.listdir(dem_directory):
        if dem_file.endswith(".tif"):
            grass_predictors[construct_shortened_name(dem_file)] = compute_raster_variables(
                os.path.join(dem_directory, dem_file), output_directory)

    return grass_predictors


def construct_shortened_name(file_path):
    short_name = ""
    if "DTM" in file_path:
        short_name += "T"
    elif "DSM" in file_path:
        short_name += "S"

    if "bilinear" in file_path:
        short_name += "B"
    elif "ngb" in file_path:
        short_name += "N"

    res = re.findall(r'[0-9]+', file_path)
    short_name += res[0]
    return short_name


def write_results_file(buffered_files, output_directory):
    with open(os.path.join(output_directory, 'predictor.csv'), 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['Resolution'] + ['Path'])
        for file in buffered_files:
            csvwriter.writerow([str(file)] + [buffered_files[file]])


def write_legend_file(predictors, output_directory):
    with open(os.path.join(output_directory, 'legend.csv'), 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['Short Name'] + ['Type'] + ['Resolution'] + ['Predictor'] + ['Input'])
        for predictor_resolution, all_predictors_per_resolution in predictors.iteritems():
            for predictor in all_predictors_per_resolution:
                csvwriter.writerow(
                    [predictor_resolution + predictor.short_name] + [resolve_type(predictor_resolution)] + [
                        resolve_resolution(predictor_resolution)] + [predictor.full_name] + [predictor.path])


def resolve_type(short_name):
    if "T" in short_name[0]:
        return "DTM"
    elif "S" in short_name[0]:
        return "DSM"


def resolve_resolution(resolution):
    found = re.findall(r'[0-9]+', resolution)
    return found[0]


def construct_soil_short_name(short_name):
    return "SP" + short_name


def construct_soil_resolution(size):
    return "SP" + str(size)


def construct_rs_resolution(size):
    return "RS" + str(size)


#####Configuration#####
dem_directory = "F:/data/DEM"
output_directory = "F:/data/RasterPredictors"
plot_list_path = "F:/data/AllPlots.csv"
soil_250m_data_list_path = "F:/data/AfricanSoilGrids/combined-soil-rasters.csv"
rs_data_list_path = "F:/data/RS/rs-datasets.csv"
plot_buffers = [17.84, 25.23, 35.68, 50.46, 71.37]
buffered_studyareas = {}

## Create Raster Predictors
predictors = create_grass_created_raster_predictors(dem_directory, output_directory)

### African soil Grids
with open(soil_250m_data_list_path, 'rb') as f:
    reader = csv.reader(f, delimiter=';')
    headers = reader.next()
    for row in reader:
        resolution = row[0]
        path = row[1]
        description = row[2]
        short_name = row[3]
        soiltype = row[4]

        reprojected_path = os.path.join(os.path.dirname(path), "32737_" + os.path.basename(path))
        processing.runalg("gdalogr:warpreproject", path, "EPSG:4326", "EPSG:32737", "", 250, 1, 5, 4, 75, 6, 1,
                          False, 0, False, "", reprojected_path)
        if construct_soil_resolution(250) in predictors:
            predictors[construct_soil_resolution(250)].append(
                predictor_object(short_name, description, reprojected_path, 250))
        else:
            predictors[construct_soil_resolution(250)] = []
            predictors[construct_soil_resolution(250)].append(
                predictor_object(short_name, description, reprojected_path, 250))

### Read Landsat data
with open(rs_data_list_path, 'rb') as f:
    reader = csv.reader(f, delimiter=';')
    headers = reader.next()
    for row in reader:
        resolution = row[0]
        path = row[1]
        description = row[2]
        short_name = row[3]
        band = row[4]

        scaled_path = os.path.join(os.path.dirname(path), "32737__" + os.path.basename(path))
        processing.runalg("gdalogr:warpreproject", path, "EPSG:32637", "EPSG:32737", "", 30, 0, 5, 4, 75, 6, 1,
                         False, 0, False, "", scaled_path)
        predictor_rs = predictor_object(short_name, description, scaled_path, 30)
        predictor_rs.band = band
        if construct_rs_resolution(30) in predictors:
            predictors[construct_rs_resolution(30)].append(predictor_rs)
        else:
            predictors[construct_rs_resolution(30)] = []
            predictors[construct_rs_resolution(30)].append(predictor_rs)

## Create Plot Shapefiles
for plot_buffer_size in plot_buffers:
    study_area_shape_path = os.path.join(output_directory, "StudyArea_" + str(plot_buffer_size) + "m.shp")
    buffered_vector = create_study_area_shapefile(plot_list_path, plot_buffer_size, study_area_shape_path)
    buffered_studyareas[plot_buffer_size] = study_area_shape_path
    for predictor_resolution, all_predictors_per_resolution in predictors.iteritems():
        for predictor in all_predictors_per_resolution:
            if "RS" not in predictor_resolution:
                zoneStat = QgsZonalStatistics(buffered_vector, predictor.path,
                                              str(predictor_resolution + predictor.short_name), 1,
                                              QgsZonalStatistics.Mean | QgsZonalStatistics.Max |
                                              QgsZonalStatistics.Min | QgsZonalStatistics.Range | QgsZonalStatistics.StDev)
                zoneStat.calculateStatistics(None)
            else:
                zoneStat = QgsZonalStatistics(buffered_vector, predictor.path,
                                              str(predictor_resolution + predictor.short_name + str(predictor.band)),
                                              int(predictor.band),
                                              QgsZonalStatistics.Mean | QgsZonalStatistics.StDev)
                zoneStat.calculateStatistics(None)

write_results_file(buffered_studyareas, output_directory)
write_legend_file(predictors, output_directory)
