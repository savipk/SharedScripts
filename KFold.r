library(plyr)
library(randomForest)

data <- iris
k = 5 #Folds

# sample from 1 to k, nrow times 
data$id <- sample(1:k, nrow(data), replace = TRUE)
list <- 1:k

prediction <- data.frame()
testsetCopy <- data.frame()


#Creating a progress bar to know the status of CV
progress.bar <- create_progress_bar("text")
progress.bar$init(k)

for (i in 1:k){
	# remove rows with id i from dataframe to create training set
	# select rows with id i to create test set
	trainingset <- subset(data, id %in% list[-i])
	testset <- subset(data, id %in% c(i))
	
	# run the model
	mymodel <- randomForest(trainingset$Sepal.Length ~ ., data = trainingset, ntree = 100)
	
	# remove response column 
	temp <- as.data.frame(predict(mymodel, testset[,-1]))
	# append this iteration's predictions to the end of the prediction data frame
	prediction <- rbind(prediction, temp)
	
	# append this iteration's test set to the test set copy data frame
	# keep only the Sepal Length Column
	testsetCopy <- rbind(testsetCopy, as.data.frame(testset[,1]))
	
	progress.bar$step()
}

# add predictions and actual values
result <- cbind(prediction, testsetCopy[, 1])
names(result) <- c("Predicted", "Actual")
mse <- mean((result$Actual - result$Predicted)^2)
