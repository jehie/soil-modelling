### Install Packages ###
list.of.packages <- c("randomForest")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only = TRUE)

### Functions
readTable <- function(path, header=TRUE, separator=";"){
  file = read.csv2(file=path, header=header, sep=separator, dec=".", colClasses=c("character",rep("numeric",3)))
  return(file)
}
readTable2 <- function(path, header=TRUE, separator=";"){
  file = read.csv2(file=path, header=header, sep=separator)
  return(file)
}

### Nitrogen model
input.predicting.data.path = "F:/data/SelectedVariablesForWholeStudyAreaN.csv" # Data for whole study area to predict
input.model.path = "F:/data/ModelDataN.csv" # Data used for creating the model
output.modeled = "F:/data/PredictedN.csv"
modeling.data = readTable(input.predicting.data.path)
learning.data = readTable2(input.model.path)

rf  <- randomForest(x=learning.data[5:21],y=learning.data$Nitrogen, ntree=5000, importance=TRUE ,na.action=na.omit) # Create RF model
modeling.data$predicted.response <- predict(rf , modeling.data[2:18]) # Predict for the whole study area
write.csv2(modeling.data, file = output.modeled) # Write Table to CSV

### Soil organic carbon model
input.predicting.data.path = "F:/data/SelectedVariablesForWholeStudyAreaSOC.csv" # Data for whole study area to predict
input.model.path = "F:/data/ModelDataSOC.csv" # Data used for creating the model
output.modeled = "F:/data/PredictedSOC.csv"
modeling.data = readTable(input.predicting.data.path)
learning.data = readTable2(input.model.path)

rf  <- randomForest(x=learning.data[2:4],y=learning.data$Carbon, ntree=5000, importance=TRUE ,na.action=na.omit) # Create RF model
modeling.data$predicted.response <- predict(rf, modeling.data[2:4]) # Predict for the whole study area
write.csv2(modeling.data, file = output.modeled) # Write Table to CSV