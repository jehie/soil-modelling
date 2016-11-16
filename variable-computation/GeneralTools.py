import os
from qgis.core import QgsRasterLayer, QgsVectorLayer


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def load_raster(raster_path):
    """
    Method for loading raster to QGIS. Returns it as QgsRasterLayer
    :param raster_path: Path to the raster layer
    :return: Loaded QgsRasterLayer.
    :throws: Throws a ValueError if cannot load the raster
    """
    input_raster = QgsRasterLayer(raster_path, os.path.basename(raster_path))
    if not input_raster.isValid():
        print raster_path
        raise ValueError("Cannot load raster: " + raster_path)
    return input_raster

def find_basename_from_file(file_path):
    """
    Method for finding basename from a file path
    :param file_path: Path to the file from which to find base name
    :return: Basename of the file, e.g (C:/test/blalala.tif would return blabla)
    """
    return os.path.basename(file_path).split(".")[0]

def split_filename_from_path(input_path, splitter):
    filename = os.path.basename(input_path)
    splitted_filename = filename.split(splitter)

    return splitted_filename[0]

def read_shapefile(input_path):
    filename = split_filename_from_path(input_path, ".")

    shape = QgsVectorLayer(input_path, filename, "ogr")

    if shape.isValid():
        print "Valid Layer: " + filename
    else:
        print "Invalid layer: " + filename