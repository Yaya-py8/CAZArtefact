# --- 1. Install and load necessary libraries ---
# install.packages("CausalImpact")
# install.packages("zoo")
# install.packages("dplyr")
library(CausalImpact)
library(zoo)
library(dplyr) # For duplicate handling

# --- 2. Load your master dataset ---
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

# --- 5. Aggregate to Daily Averages and Interpolate ---
print("Aggregating data to daily averages and interpolating...")

safe_mean <- function(x) {
  if (all(is.na(x))) {
    return(NA_real_)
  } else {
    return(mean(x, na.rm = TRUE))
  }
}

data_daily <- aggregate(data_zoo_hourly, as.Date(index(data_zoo_hourly)), FUN = safe_mean)
data_interpolated <- na.approx(data_daily, na.rm = FALSE)
data_interpolated <- na.locf(data_interpolated, na.rm = FALSE, fromLast = TRUE)
data_interpolated <- na.locf(data_interpolated, na.rm = FALSE)
print(paste("NAs remaining after interpolation:", sum(is.na(data_interpolated))))

# --- 6. Prepare data for the model ---
y_avg_values <- rowMeans(data_interpolated[, c("TW_NO2", "SP_NO2")], na.rm = TRUE)
y_Bristol_CAZ_NO2 <- zoo(y_avg_values, order.by = index(data_interpolated))

# --- Define Time Periods ---
pre_period_start <- start(data_interpolated)
intervention_date <- as.Date("2022-11-28")
post_period_end <- min(as.Date("2025-10-24"), end(data_interpolated))
pre_period_end <- intervention_date - 1 
pre_period <- c(pre_period_start, pre_period_end)
post_period_start <- intervention_date
post_period <- c(post_period_start, post_period_end)


# ======================================================================
# --- RUN 1: MAIN MODEL (Figure 4.2) ---
# Full Controls: Cardiff, Liv, Leeds + Temp, Speed
# ======================================================================
control_vars_main <- c("Cardiff_NO2", "Liv_NO2", "Leeds_NO2", "TW_M_T", "TW_M_SPED")
X_controls_main <- data_interpolated[, control_vars_main]
model_data_main <- cbind(y_Bristol_CAZ_NO2, X_controls_main)

print("Running Main Model (Fig. 4.2)...")
impact_main <- CausalImpact(model_data_main, pre.period = pre_period, post.period = post_period, model.args = list(nseasons = 7))

# --- SAVE PLOT FOR FIGURE 4.2 (Main Result) ---
png("causal_impact_results_DAILY_R.png", width=800, height=600)
# Use par and mtext to reliably add the title to the plot margin
par(oma = c(0, 0, 2, 0)) 
plot(impact_main)
mtext("Figure 4.2: Causal Impact Model - Refined Daily Analysis", outer = TRUE, cex = 1.2, line = 0.5) 
dev.off() 


# ======================================================================
# --- RUN 2: SENSITIVITY TEST 1 (Figure 4.3) ---
# No Meteorology
# ======================================================================
control_vars_test1 <- c("Cardiff_NO2", "Liv_NO2", "Leeds_NO2")
X_controls_test1 <- data_interpolated[, control_vars_test1]
model_data_test1 <- cbind(y_Bristol_CAZ_NO2, X_controls_test1)

print("Running Sensitivity Test 1 (Fig. 4.3 - No Meteorology)...")
impact_test1 <- CausalImpact(model_data_test1, pre.period = pre_period, post.period = post.period, model.args = list(nseasons = 7))

# --- SAVE PLOT FOR FIGURE 4.3 ---
png("causal_impact_results_Test2_R.png", width=800, height=600)
par(oma = c(0, 0, 2, 0)) 
plot(impact_test1)
mtext("Figure 4.3: Sensitivity Analysis - Excluding Meteorological Controls", outer = TRUE, cex = 1.2, line = 0.5)
dev.off()


# ======================================================================
# --- RUN 3: SENSITIVITY TEST 2 (Figure 4.4) ---
# Cardiff Only
# ======================================================================
control_vars_test2 <- c("Cardiff_NO2", "TW_M_T", "TW_M_SPED")
X_controls_test2 <- data_interpolated[, control_vars_test2]
model_data_test2 <- cbind(y_Bristol_CAZ_NO2, X_controls_test2)

print("Running Sensitivity Test 2 (Fig. 4.4 - Cardiff Only)...")
impact_test2 <- CausalImpact(model_data_test2, pre.period = pre.period, post.period = post.period, model.args = list(nseasons = 7))

# --- SAVE PLOT FOR FIGURE 4.4 ---
png("causal_impact_results_Test3_R.png", width=800, height=600)
par(oma = c(0, 0, 2, 0)) 
plot(impact_test2)
mtext("Figure 4.4: Sensitivity Analysis - Cardiff Only Predictor", outer = TRUE, cex = 1.2, line = 0.5)
dev.off()


# ======================================================================
# --- FINAL SUMMARY OUTPUT ---
# Print the reports for the final chapter write-up.
# ======================================================================
print("--- FINAL STATISTICAL SUMMARIES FOR CHAPTER 4 ---")
# Get the R-squared for the main model (needed for Chapter 4.4.1)
print("Main Model R-Squared:")
summary(impact_main$model$bsts.model)

print("--- Main Model (Fig 4.2) Full Report ---")
summary(impact_main, "report")
print("--- Test 1 (No Met) Full Report ---")
summary(impact_test1, "report")
print("--- Test 2 (Cardiff Only) Full Report ---")
summary(impact_test2, "report")

print("Success! All CausalImpact models have run, and all three plots (Fig 4.2, 4.3, 4.4) are saved.")
