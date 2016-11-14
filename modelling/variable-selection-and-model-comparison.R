### Install Packages ###
list.of.packages <- c("randomForest", "VSURF")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only = TRUE)

### Config ###
input.list = "F:/data/models.csv" #
y.variables = c("Carbon", "Nitrogen") # What Y-variables to model
x.variables.beginning = 11 # First column to have X-variables
modeling.selected.variables.output = "F:/data/variable_selection_results.txt"
modeling.results.output = "F:/data/RFResultsAll.txt"

### Functions ###
readTable <- function(path, header=TRUE, separator=";"){
  return(read.csv2(file=path, header=header, sep=separator))
}

#####
# Function for accuracy assessment
#####
print.accuracy <- function(obs, fit) {
  res <- fit-obs
  bias <- signif(mean(res), 3)
  bias.r <- signif(bias/mean(obs)*100, 3)
  RMSE <- signif(sqrt(sum((res^2)/length(res))), 3)
  RMSE.r <- signif(RMSE/mean(obs)*100, 3)
  R2 <- signif(cor(obs,fit,method="pearson")^2, 3) #pseudo R^2
  ret <- as.numeric(c(RMSE, RMSE.r, bias, bias.r, R2))
}

#####
# Function for leave-one-out cross-validation (LOOCV) of random forest:
# regression
# returns accuracy statistics and predictions for plotting
#####
cv.reg <- function(data, y, x) {
  pred <- numeric(nrow(data)) #empty vector for results
  for(cv.i in 1:nrow(data)){
    ref <- which(row.names(data)!=cv.i)
    val <- which(row.names(data)==cv.i)
    xi  <- as.data.frame(data[ref, x])
    names(xi) <- x #name is lost if only one x-variable
    yi  <- data[ref, y]
    rf  <- randomForest(x=xi,y=yi, ntree=400, importance=FALSE, 
                        proximity=TRUE, na.action=na.omit)
    x.val <- as.data.frame(data[val, x])
    names(x.val) <- x
    pred[cv.i] <- predict(rf, newdata=x.val)
  }
  res <- print.accuracy(data[,y], pred)
  res <- c(res, pred)
  return(res)
  rm(pred,ref,val,xi,yi,rf,x.val,res,pred,cv.i)
}

### Read CSVs ###
modeling.dataset.list = readTable(input.list)

### Variable Selection ###
res.all.inputs <- NULL
res.vs <- list() #save final variables to a list
f <- 0 #needed for saving results to list

total.run.time<-Sys.time()
for(i in 1:nrow(modeling.dataset.list)){ # Loop for all files in the modeling csv
  res.all.y <- NULL #results for all y-variables
  modeling.dataset = readTable(paste(tools::file_path_sans_ext(as.character(modeling.dataset.list[i, 'Path'])),".csv", sep=""))
  modeling.dataset.name = basename(as.character(modeling.dataset.list[i, 'Path']))
  modeling.dataset.resolution = as.character(modeling.dataset.list[i, 'Resolution'])
  modeling.dataset = modeling.dataset[complete.cases(modeling.dataset),] #Remove rows with NA values
  
  for(y.variable in y.variables){ # Loop for all Y-variables
    strt<-Sys.time()
    print(paste(y.variable, " : ", modeling.dataset.resolution, "m. Start Time: ", strt  , sep=""))
    
    x=modeling.dataset[, x.variables.beginning:ncol(modeling.dataset)]
    y=modeling.dataset[, y.variable]
    res.y <- NULL
    
    vs <- VSURF(x, y, ntree=500, parallel=TRUE, ncores=8)
    
    if (is.null(vs$varselect.pred) == FALSE) { #sometimes prediction set is not produced
      x <- x[vs$varselect.pred] #include only selected x
    }
    
    f <- f + 1 
    res.vs[[f]] <- c(modeling.dataset.resolution, y.variable, colnames(x))
    
    ##
    # random forest
    ##
    n.rf <- 10 #set how many times RF is averaged
    for(x.rf in 1:n.rf) { 
      print(paste("Round:", x.rf))
      res <- cv.reg(modeling.dataset, y.variable, colnames(x))
      res.y <- rbind(res.y, res)
    }
    res.y <- colMeans(res.y)
    res.all.y <- as.data.frame(rbind(res.all.y, res.y))
    names(res.all.y) <- c("RMSE","RRMSE","Bias","RBias","R.squared",rownames(modeling.dataset)) 
    
    # Print How Long It TOok
    run.time = Sys.time()-strt
    print(run.time) #print how much time was required
    print("Run ended")
  }
  res.all.y["Attribute"] <- y.variables
  res.all.y["Input"] <- modeling.dataset.resolution
  res.all.inputs <- as.data.frame(rbind(res.all.inputs, res.all.y))
}

print("All Runs Ended")
print(Sys.time()-total.run.time)

### Write Selected Variables to CSV ###
ml <- max(as.numeric(summary(res.vs)[,1])) # max length
mnv <- ml - 2 # max number of variables

out <- NULL
for(e in 1:length(res.vs)) {
  t <- unlist(res.vs[e])
  l <- length(t) - 2 #no variables
  t <- c(t[1:2],l,t[3:ml])
  out <- rbind(out, t)
}
out <- as.data.frame(out)
row.names(out) <- NULL
names(out) <- c("Input","Y","No X", 1:mnv)
write.table(out, modeling.selected.variables.output)

### Write RF Results to CSV ###
res.rf3.vs <- res.all.inputs
columns = ncol(res.all.inputs)
res.rf3.vs <- res.rf3.vs[,c(columns,(columns-1),1:(columns-2))] 
row.names(res.rf3.vs) <- NULL
write.table(res.rf3.vs, modeling.results.output)

