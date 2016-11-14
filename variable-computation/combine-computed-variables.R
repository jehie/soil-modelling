### Install Packages
list.of.packages <- c("rgdal")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only = TRUE)

### Default Values . Use these if no interactive calls are made
input.cloudmetrics.list = "F:/data/CloudMetricsPredictors.csv"
input.predictor.list = "F:/data/RasterPredictor.csv"
input.modeling = "F:/Gradu/FinalCalculations/TopSoil.csv"
input.modeling.soiltype = tools::file_path_sans_ext(basename(input.modeling))

### Functions
readCSV <- function(path, header=TRUE, separator=";"){ # Method for Reading CSV Files
  file = read.csv(file=path, header=header, sep=separator)
  return(file)
}

findPlotName <- function(path) { # Method for Finding Plot Name for File Path
  return(tools::file_path_sans_ext(basename(path)))
}

### Read CSV Files
files.legend = readCSV(input.legend)
files.predictor.list = readCSV(input.predictor.list, TRUE)
files.modeling = readCSV(input.modeling)
files.cloudmetric.files = readCSV(input.cloudmetrics.list)

### Read with OGR and convert to dataframes (Combine with Modeling data)
rasters.shapefiles = vector("list", nrow(files.predictor.list[]))
rasters.dataframes = vector("list", nrow(files.predictor.list[]))

for(i in 1:nrow(files.predictor.list)){ # Loop shapefiles with different resolutions
  filepath = as.character(files.predictor.list[i,]$Path) # Take filepath from the input CSV
  rasters.shapefiles[[i]] = readOGR(dsn=dirname(filepath), layer=tools::file_path_sans_ext(basename(filepath))) # Read Shapefile with OGR
  rasters.dataframes[[i]] = merge(files.modeling, as(rasters.shapefiles[[i]],"data.frame"), by.x=c("Cluster", "Plot"), by.y=c("Cluster", "Plot")) # Merge with Carbon Measurements
  rasters.dataframes[[i]]$CombinedID = paste(rasters.dataframes[[i]]$Cluster, ".", rasters.dataframes[[i]]$Plot, sep="") # Create a Combined ID column (Cluster.Plot)
  first = TRUE
  for (f in 1:nrow(files.cloudmetric.files)) { # Loop all Cloud Metrics Files
    if(files.predictor.list[i,]$Resolution == files.cloudmetric.files[f, "Resolution"]){ # Process only shapefiles and cloudmetrics files with same resolution

      files.cloudmetrics.current = readCSV(as.character(files.cloudmetric.files[f, "Path"]), separator=",") # Read CSV
      files.cloudmetrics.current$CombinedID <- findPlotName(as.character(files.cloudmetrics.current$DataFile)) # Create Combined ID

      if(first == TRUE) { # Attach all not "ABOVE" related variables from the first dataset
        columns.to.delete = c("DataFile","Total.return.count","Elev.minimum","First.returns.above.mean", "First.returns.above.mode","All.returns.above.mean","All.returns.above.mode","Total.first.returns","Total.all.returns")
        files.cloudmetrics.current = files.cloudmetrics.current[ , !(names(files.cloudmetrics.current) %in% columns.to.delete)] # Remove unnecessary columns
        first = FALSE
      } else { # IN the next rounds, only attach the ABOVE related variables

        if(grepl("0h_", as.character(files.cloudmetric.files[f, "Path"]))){
          columns.to.keep = c("CombinedID","Percentage.first.returns.above.0.00", "Percentage.all.returns.above.0.00", "X.All.returns.above.0.00.....Total.first.returns....100")
        }
        if(grepl("2h_", as.character(files.cloudmetric.files[f, "Path"]))){
          columns.to.keep = c("CombinedID","Percentage.first.returns.above.2.00", "Percentage.all.returns.above.2.00", "X.All.returns.above.2.00.....Total.first.returns....100")
        }
        if(grepl("4h_", as.character(files.cloudmetric.files[f, "Path"]))){
          columns.to.keep = c("CombinedID","Percentage.first.returns.above.4.00", "Percentage.all.returns.above.4.00", "X.All.returns.above.4.00.....Total.first.returns....100")
        }

        files.cloudmetrics.current= files.cloudmetrics.current[columns.to.keep]
      }

      rasters.dataframes[[i]] = merge(rasters.dataframes[[i]], files.cloudmetrics.current, by.x=c("CombinedID"), by.y=c(paste("CombinedID"))) # Combine
    }
  }
  write.csv2(rasters.dataframes[[i]], file = file.path(dirname(filepath), paste(input.modeling.soiltype, "_", tools::file_path_sans_ext(basename(filepath)),".csv", sep=""))) # Write Table to CSV
}
### Read with OGR and convert to dataframes (Combine with Modeling data) ###