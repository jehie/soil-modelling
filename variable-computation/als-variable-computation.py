# Import packages
import os, subprocess, glob, logging, csv


class cloudmetrics_file:
    def __init__(self, path, min_height, above):
        """
        Represent single output cloudmetrics file
        :param path: Path to the output file
        :param min_height: Minimum height value
        :param above: Above value
        :return:
        """
        self.path = path
        self.min_height = min_height
        self.above = above


class study_plot:
    """
    Class to represent study plot
    """

    def __init__(self, cluster, plot, long_x, lat_y):
        """
        Constructor for study plot
        :param cluster: number of the cluster
        :param plot: number of the plot
        :param long_x: longitude of plot
        :param lat_y: latitude of plot
        """
        self.cluster = cluster
        self.plot = plot
        self.long_x = long_x
        self.lat_y = lat_y
        self.plot_paths = {}

    def add_plot_path(self, radius, path):
        """
        Method for adding stu
        :param radius:
        :param path:
        :return:
        """
        self.plot_paths[radius] = path



class study_cluster:
    """
    Class to represent study cluster. Cluster consists of study plots.
    """

    def __init__(self, cluster_number):
        """
        Constructor for study_cluster.
        :param cluster_number: Number of the cluster
        """
        self.cluster_number = cluster_number
        self.plots = []

    def add_plot(self, plot):
        """
        Add plots to this cluster
        :param plot: instance of study_plot
        """
        self.plots.append(plot)


class study_area:
    """
    Class to represent study_area. Study area is made from clusters.
    """

    def __init__(self, study_area_name):
        """
        Constructor for study_area
        :param study_area_name: Name of the study area
        """
        self.study_area_name = study_area_name
        self.clusters = []
        self.cloudmetric_files = {}

    def add_clusters(self, clusters):
        """
        Add clusters to study_area.
        :param clusters: List of Clusters.
        """
        self.clusters = clusters

    def add_cloudmetrics_file(self, radius, path):
        """
        Add a cloudmetrics file to the study area
        :param radius: Radius used to calculate the cloudmetrics files
        :param path: Path to this generated cloudmetrics file
        :return:
        """
        if radius in self.cloudmetric_files:
            self.cloudmetric_files[radius].append(path)
        else:
            self.cloudmetric_files[radius] = []
            self.cloudmetric_files[radius].append(path)


def create_fusion_dem(fusion_folder, output_path, list_of_input_files, resolution, utm_zone, classes_to_use):
    """
    Method for creating Fusion DTM. Calls the Fusion executables using Python Subprocess.

    :param fusion_folder: Path to the folder containing Fusion executables
    :param output_path: Path to the output DTM dataset (Will be created)
    :param list_of_input_files: Text file containing input .las files
    :param resolution: Spatial resolution of the output DTM (In meters)
    :param utm_zone: UTM Zone of the output/input DTM (37S For Taita Hills)
    :param classes_to_use: Las classes (2 for ground), comma separated string
    :return:
    """
    method_call = fusion_folder + "gridsurfacecreate.exe /class:" + classes_to_use + " " + output_path + " " + \
                  resolution + " M M 1 " + utm_zone + " 0 0 " + list_of_input_files
    subprocess.call(method_call)

    if os.path.isfile(output_path):
        logging.info("Fusion (plans) DTM Created succesfully: " + output_path)
    else:
        raise RuntimeError("DTM Generation failed. See logs and check input parameter & file validity")


def execute_subprocess(method_call):
    """
    Method for calling the subprocess (call command line tools)
    :param method_call: Method call as String
    """
    subprocess.call(method_call)


def create_clipdata_call(fusion_folder, classes, dtm_path, las_files, output_path, studyarea, plot_length):
    for cluster in studyarea.clusters:
        for plot in studyarea.clusters[cluster].plots:
            clipped_file_path = os.path.join(output_path, plot.cluster + "." + plot.plot + ".las")
            call = fusion_folder + "clipdata.exe /height /shape:1 /class:" + classes + " /dtm:" + dtm_path + \
                   " " + las_files + " " + clipped_file_path + " " + make_bounding_box(plot, plot_length)
            plot.clip_data_call = call
            plot.add_plot_path(plot_length, clipped_file_path)
            plot.path = clipped_file_path
            if not os.path.exists(clipped_file_path):
                execute_subprocess(call)


def create_cloudmetrics(fusion_folder, above, plot_path, output_path):
    call = fusion_folder + "cloudmetrics.exe" + " /id /above:" + str(above) + " " + plot_path + " " + output_path
    if os.path.exists(plot_path):
        execute_subprocess(call)
    else:
        print(plot_path + " plot not found")

def make_bounding_box(plot, plot_width):
    """
    Generate a bounding box string out of the Plot instance.
    :param plot: Instance of study plot
    :param plot_width: Plot width used for calculating the bounding box
    :return: Generated bounding box as string
    """
    x1 = str(float(plot.long_x) - plot_width)
    x2 = str(float(plot.long_x) + plot_width)
    y1 = str(float(plot.lat_y) - plot_width)
    y2 = str(float(plot.lat_y) + plot_width)
    return x1 + " " + y1 + " " + x2 + " " + y2


def list_files_in_directory(folder_path, file_extension):
    """
    Method to list files in directory and return them as list
    :param folder_path: Path to the folder where to list files
    :param file_extension: File extension to search e.g. .txt, .las etc
    :return: List of files
    """
    path = str(os.path.join(folder_path, "*" + file_extension))
    return glob.glob(path)


def write_to_file(output_path, list_to_write):
    """
    Helper method for writing a list to CSV or TXT file
    :param output_path:
    :param list_to_write:
    :return:
    """
    text_file = open(output_path, "w")
    for row in list_to_write:
        text_file.write(row + "\n")
    text_file.close()


def read_plots_from_csv(path):
    """
    Method for reading plots out of a CSV file defining the study area
    :param path: Path to CSV file containing the individual plots
    :return:
    """
    clusters = {}

    with open(path, 'rb') as f:
        csv_reader = csv.reader(f, delimiter=";")

        header = next(csv_reader)

        # Check that the header of plot list matches - maybe parametrize in future
        if header != ['Cluster', 'Plot', 'Long_X', 'Lat_y']:
            raise ValueError("Input Plot CSV has faulty header, please verify")

        # Loop over each row and extract values
        for row in csv_reader:
            cluster = row[0]
            plot = row[1]
            long_x = row[2]
            long_y = row[3]

            # Create a cluster instance if it no already exists - otherwise add the study plot there
            if cluster not in clusters:
                current_cluster = study_cluster(cluster);
                clusters[cluster] = current_cluster
            else:
                current_cluster = clusters.get(cluster)

            current_plot = study_plot(cluster, plot, long_x, long_y)
            current_cluster.add_plot(current_plot)

    return clusters


def write_helper_file(output_path, sarea):
    """
    Write a CSV file that will be used later in the modelling. Contains the paths and parameters of the computed
    cloudmetrics files
    :param output_path: Path to the output file
    :param sarea: Instance of study area object
    :return:
    """
    with open(output_path, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(["Resolution"] + ["Above"] + ["Path"])
        for cm_file in sarea.cloudmetric_files:
            for cm_file2 in sarea.cloudmetric_files[cm_file]:
                csvwriter.writerow([str(cm_file)] + [str(cm_file2.above)] + [cm_file2.path])

def main():
    #################################################################################################
    # Input Variables & Settings
    #################################################################################################
    las_data_dir = "F:/Gradu/OverageRemoved_500m"  # Path to directory containing input .las files
    output_folder = "F:/Gradu/FinalCalculations"  # Path to directory to store intermediate and result files
    output_folder_ground = "F:/Gradu/FinalCalculations/Ground"
    fusion_folder = "F:/FUSION/"  # Path to directory containing FUSION executables'
    radius_to_process = [17.84, 25.23, 35.68, 50.46, 71.37]  # Radiuses to used for clipping (in meters)
    classes_to_select = "2,3,5"  # What Lidar Class files to select from las files
    plot_csv_path = "F:/Gradu/FinalCalculations/AllPlots_Fixed.csv"
    above_values = [0, 2, 4]

    # Setup logging to output to stdout and file
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("{0}/{1}.log".format(las_data_dir, "fusion_processing"))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    logging.info("********************")
    logging.info("Starting to process Pro Gradu Stuff")
    logging.info("********************")
    logging.info("Input Parameters: ")
    logging.info("  Input Las Folder: " + las_data_dir)
    logging.info("  Output Folder: " + output_folder)
    logging.info("  Fusion Folder: " + fusion_folder)
    logging.info("  Input Las Files: ")
    las_files = list_files_in_directory(las_data_dir, ".las")
    for las_file in las_files:
        logging.info("      " + las_file)
    logging.info("********************")

    # Write list of files to directory
    las_file_list_path = os.path.join(las_data_dir, "las_list.txt")
    write_to_file(las_file_list_path, las_files)

    # Create DTM only if it does not exist
    dem_path = os.path.join(output_folder, "Sentinel_1m.dtm")
    if not os.path.exists(dem_path):
        create_fusion_dem(fusion_folder, dem_path, las_file_list_path, "1", "37S", "2")
    else:
        print "DEM EXITS"

    logging.info("********************")

    sarea = study_area("Sentinel")
    sarea.add_clusters(read_plots_from_csv(plot_csv_path))

    # Clip the study plots
    for radius in radius_to_process:
        logging.info("Clipping data with " + str(radius) + " m radius")
        radius_directory = os.path.join(output_folder, str(radius))
        if not os.path.exists(radius_directory):
            os.mkdir(radius_directory)
        create_clipdata_call(fusion_folder, classes_to_select, dem_path, las_file_list_path,
                             os.path.join(output_folder, str(radius)), sarea, radius)



    # Calculate the cloudmetrics for all radiuses and heights
    for above_value in above_values:
        for radius in radius_to_process:
            radius_directory = os.path.join(output_folder, str(radius))
            output_path = os.path.join(radius_directory,
                                       str(above_value) + "h_cloudmetrics_result.csv")
            sarea.add_cloudmetrics_file(radius, cloudmetrics_file(output_path, above_value, above_value))
            for cluster in sarea.clusters:
                for plot in sarea.clusters[cluster].plots:
                    create_cloudmetrics(fusion_folder, above_value, plot.plot_paths[radius], output_path)

    # Write a CSV file that can be read by other scripts
    write_helper_file(os.path.join(output_folder, "CloudMetricFiles.csv"), sarea)

    # Return the instance of Study Area, in case some other process wants to use it.
    return sarea

main()
