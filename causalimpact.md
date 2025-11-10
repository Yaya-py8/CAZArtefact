# --- 1. Install and load necessary libraries ---
# (You only need to run install.packages once)
# install.packages("CausalImpact")
# install.packages("zoo")
# install.packages("dplyr")
library(CausalImpact)
library(zoo)
library(dplyr) # For duplicate handling

# --- 2. Load your master dataset ---
# Make sure the file path is correct
master_file <- "/Users/yahye/Desktop/Masters Project/CAZArtefact/master_combined.csv"
print(paste("Loading master file:", master_file))
data <- read.csv(master_file)

# --- 3. Convert 'datetime' column and CHECK FOR DUPLICATES ---
print("Converting datetime and checking for duplicates...")
data$datetime <- as.POSIXct(data$datetime, format="%Y-%m-%d %H:%M:%S", tz = "GMT")

# Count duplicates BEFORE removing
duplicate_count <- sum(duplicated(data$datetime))
print(paste("Found", duplicate_count, "duplicate timestamps."))

if (duplicate_count > 0) {
  print("Removing duplicate timestamps, keeping the first occurrence...")
  data <- data %>%
    distinct(datetime, .keep_all = TRUE)
  print(paste("Duplicates remaining after removal:", sum(duplicated(data$datetime))))
}

# --- 4. Create HOURLY zoo object ---
print("Creating hourly zoo object...")
data_zoo_hourly <- zoo(data[, -which(names(data) == "datetime")], order.by = data$datetime)

# --- 5. !! NEW STEP: Aggregate to Daily Averages !! ---
print("Aggregating data to daily averages...")

# Define a "safe mean" function that returns NA if the whole day is missing
# This prevents 'NaN' from mean(na.rm=TRUE) on an all-NA day
safe_mean <- function(x) {
  if (all(is.na(x))) {
    return(NA_real_)
  } else {
    return(mean(x, na.rm = TRUE))
  }
}

# Aggregate the hourly data to daily data using the safe_mean function
data_daily <- aggregate(data_zoo_hourly, as.Date(index(data_zoo_hourly)), FUN = safe_mean)

# --- 6. !! MODIFIED: Interpolate missing DAILY data !! ---
print("Interpolating missing daily values...")
data_interpolated <- na.approx(data_daily, na.rm = FALSE)
data_interpolated <- na.locf(data_interpolated, na.rm = FALSE, fromLast = TRUE)
data_interpolated <- na.locf(data_interpolated, na.rm = FALSE)

print("Checking for remaining NAs...")
print(paste("NAs remaining after interpolation:", sum(is.na(data_interpolated))))

# --- 7. Prepare data for the model ---
print("Preparing data for model...")

# Create the 'treatment' variable (y) by averaging Bristol stations
y_avg_values <- rowMeans(data_interpolated[, c("TW_NO2", "SP_NO2")], na.rm = TRUE)

# Convert the result back into a zoo object with the correct index
y_Bristol_CAZ_NO2 <- zoo(y_avg_values, order.by = index(data_interpolated))

# Create the 'control' variables (X)
control_vars <- c(
    "Cardiff_NO2",
    "TW_M_T",
    "TW_M_SPED"# Wind Speed from Temple Way
)
X_controls <- data_interpolated[, control_vars]

# Combine y and X into the final model data frame
print("Combining treatment and control variables...")
model_data <- cbind(y_Bristol_CAZ_NO2, X_controls)

# --- 8. !! MODIFIED: Define Time Periods using Dates !! ---
print("Defining pre/post periods using Dates...")

# Get the start date from the data
pre_period_start <- start(model_data)

# Define the intervention date as a Date object
intervention_date <- as.Date("2022-11-28")

# Define the end date as a Date object
post_period_end <- min(as.Date("2025-10-24"), end(model_data))


# Define pre-period from the start up to the day BEFORE intervention
pre_period_end <- intervention_date - 1 # Subtracts 1 day
pre_period <- c(pre_period_start, pre_period_end)

# Define post-period from the intervention date to the end date
post_period_start <- intervention_date
post_period <- c(post_period_start, post_period_end)

# --- Verification ---
print("Final period vectors created:")
print("Pre-period:")
print(pre_period)
print("Post-period:")
print(post_period)
if (anyNA(pre_period) || anyNA(post_period)) {
   stop("ERROR: NA values detected in period definitions. Check dates.")
}
# --- End Verification ---

# --- 9. !! MODIFIED: Run the model with Seasonality !! ---
print("Running CausalImpact analysis...")
# We add model.args to account for weekly seasonality (7 days)
# This often significantly improves the model for daily data
impact <- CausalImpact(model_data,
                       pre.period = pre_period,
                       post.period = post_period,
                       model.args = list(nseasons = 7)) # nseasons = 7 for weekly pattern

# --- 10. Print summary and save plot ---
print("--- CausalImpact Summary ---")
summary(impact)        # Prints the statistical table to the console
summary(impact, "report") # Prints the longer explanation to the console

print("Saving plot...")
# Save the plot as a PNG file in your current folder
png("causal_impact_results_Test3_R.png", width=800, height=600)
plot(impact)
dev.off() # Closes the PNG device

print("Success! Results plot saved as 'causal_impact_results_Test3_R.png'")

