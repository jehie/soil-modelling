### Install Packages ###
list.of.packages <- c("raster", "rgdal")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only = TRUE)

#### Configuration
dtm = "F:/data/DTM_1m.tif" # Path to DTM
dsm = "F:/data/DSM_1m.tif" # Path to DSM
output_directory = "F:/resampled_models/"
resolutions = c(5,10,25,50,100) # spatial resolutions to resample

### Define functions
resample_elevation_model <- function(rasterpath, output_directory, prefix="DTM", resample_value=4, resample_method='bilinear'){
  inputRaster <- raster(rasterpath)
  inCols <- ncol(inputRaster)
  inRows <- nrow(inputRaster)
  resampledRaster <- raster(ncol=(inCols / resample_value), nrow=(inRows / resample_value))
  projection(resampledRaster) <- "+proj=utm +zone=37 +south +datum=WGS84 +units=m +no_defs +ellps=WGS84 +towgs84=0,0,0"
  extent(resampledRaster) <- extent(inputRaster)
  filename = file.path(output_directory, paste(prefix,"_",resample_value,"m_",resample_method, ".tif", sep = ""))
  resampledRaster <- resample(inputRaster,resampledRaster,datatype="FLT4S",method=resample_method,filename=filename,overwrite=TRUE)
  return (resampledRaster)
}

### Create resampled Digital Terrain Models
for (i in 1:length(resolutions) ) {
  print(paste("Resampling DTM to: ", resolutions[i], "m"))
# Bilinear interpolation
  resample_elevation_model(dtm, output_directory, "DTM", resolutions[i])
  # Nearest neighbour interpolation
  resample_elevation_model(dtm, output_directory, "DTM", resolutions[i],'ngb')
}

### Create resampled Digital Surface Models
for (i in 1:length(resolutions) ) {
  print(paste("Resampling DSM to: ", resolutions[i], "m"))
  # Bilinear interpolation
  resample_elevation_model(dsm, output_directory, "DSM", resolutions[i])
  # Nearest neighbour interpolation
  resample_elevation_model(dsm, output_directory, "DSM", resolutions[i],'ngb')
}

