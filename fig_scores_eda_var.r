library(tidyr)
library(magrittr)
#install.packages("reticulate")
library(reticulate)
library(RcppCNPy)
library(ggbeeswarm)
library(dplyr)
library(stringr)
library(ggplot2)

###### UNCOMMENT IF RUNNING FOR THE FIRST TIME ######
#conda_create("r-reticulate")
#conda_install("r-reticulate", "numpy")
use_python("C:/Users/dadam/anaconda3/python.exe")
np <- import("numpy", convert=TRUE)
#####################################################


#### Set parameters ####
measure <- 'eda'
y_stat <- 'var'
date_and_time <- '02-09--21-11' #extract from plots' directory
########################

if (.Platform$OS.type == "windows"){
  setwd("C:/Users/dadam/arousal_project/arousal_decoding_extended")
} else {
  setwd("/arousal_decoding_extended")
}

source('config.r')

#np <- import("numpy")

# Create a for loop here to open dataframes, add a 'subject' column,
# concatenate this dfs and calculate mean of every column depending on subject

subjects <- sprintf("%02d", 1:32) 

measure_uppercase <- toupper(measure)

fname <- str_glue("./outputs/DEAP-bids/derivatives/mne-bids-pipeline/eda_predictions/{date_and_time}/")
scores_dir <- str_glue('{measure}_{y_stat}_scores--{date_and_time}')

for (sub in subjects)
{
  
  fname_2 <- str_glue("{scores_dir}/")
  
  scores_filename <- str_glue('sub-{sub}_all_scores_models_DEAP_{measure}_{y_stat}_r2_2Fold.npy')
  
  fname_data <- fname + fname_2 + scores_filename
  
  data <- np$load(
    fname_data,
    allow_pickle = T)[[1]] %>%
    as.data.frame()
  
  data <- data %>% rename(dummy = random,  diag = log_diag)
  
  colnames(data)[6] <- "spoc_opt"
  colnames(data)[7] <- "riemann_opt"
  
  data <- data[,c(5,4,3,2,1,6,7)]
  
  # PRINT MEAN AND SD OF DUMMY MODEL SCORE
  sprintf("Dummy score %0.3f (+/-%0.3f)", mean(data$dummy),
          sd(data$dummy))
  
  # DELETE 'DUMMY' FROM MODELS TO COMPARE
  data_x <- data[, (!names(data) %in% c("dummy"))]
  n_splits <- nrow(data_x) # -> ONLY IF THIS IS FOR ONE SUBJECT
  
  # CALCULATE MEAN ON DATA_
  data_x$sub <- sub
  
  data_x <- data_x %>%
    group_by(sub) %>%
    summarise_each(funs(mean(., na.rm = TRUE)))
  
  
  # CONCATENATE ALL SUBJECTS
  if (sub == '01'){
    data_ <- data_x
  } else {
    data_ <- rbind(data_x, data_)  
  }
  
}

data_$sub <- NULL

# GATHER ON 'ESTIMATOR' VARIABLE
data_long <- data_ %>% gather(key = "estimator", value = "score")

# move to long format
data_long$estimator <- factor(data_long$estimator)

# DEFINE ESTIMATOR TYPES
est_types <- c(
  "naive",
  "diag",
  "SPoC",
  "Riemann",
  "SPoC",
  "Riemann"
)

# DEFINE ESTIMATOR NAMES (TO PLOT)
est_names <- c(
  "upper",
  "diag",
  "SPoC",
  "Riemann",
  "SPoC_opt",
  "Riemann_opt"
)

est_labels <- setNames(
  c("upper", est_types[c(-1, -5, -6)]),
  est_types[c(-5, -6)]
)

# categorical colors based on: https://jfly.uni-koeln.de/color/
# beef up long data
data_long$est_type <- factor(rep(est_types, each = 32))


# CALCULATE MEAN OVER FOLD


data_long$sub <- rep(1:32, times = length(est_types))

# prepare properly sorted x labels
sort_idx <- order(apply(data_, 2, mean))
# IS GOING TO BE USEFUL WHEN PLOTING
levels_est <- est_names[rev(sort_idx)]

my_color_cats <- setNames(
  with(
    color_cats,
    c(`sky blue`, `blueish green`, vermillon, orange)),
  c("naive", "diag", "SPoC", "Riemann"))

ggplot(data = subset(data_long, estimator != "dummy"),
       mapping = aes(y = score, x = reorder(estimator, I(-score)))) +
  geom_beeswarm(
    priority = 'random',
    mapping = aes(color = est_type,
                  alpha = 0.1),
    size = 2.5,
    show.legend = T, cex = 0.15) +
  scale_size_continuous(range = c(0.5, 2)) +
  scale_alpha_continuous(range = c(0.4, 0.7)) +
  geom_boxplot(mapping = aes(fill = est_type, color = est_type),
               alpha = 0.4,
               outlier.fill = NA, outlier.colour = NA) +
  stat_summary(geom = 'text',
               mapping = aes(label  = sprintf("%1.2f",
                                              ..y..)),
               fun.y= mean, size = 3.2, show.legend = FALSE,
               position = position_nudge(x=-0.49)) +
  my_theme +
  labs(y = expression(R^2), x = NULL, parse = T) +
  guides(size = F, alpha = F) +
  theme(legend.position = c(0.8, 0.86)) +
  coord_flip(ylim = c(-1, 1)) +
  scale_fill_manual(values = my_color_cats, breaks = names(my_color_cats),
                    labels = est_labels,
                    name = NULL) +
  scale_color_manual(values = my_color_cats, breaks = names(my_color_cats),
                     labels = est_labels,
                     name = NULL) +
  scale_x_discrete(labels = parse(text = levels_est)) +
  geom_hline(yintercept = mean(data$dummy), linetype = 'dashed') +
  annotate(geom = "text",
           y = mean(data$dummy) + 0.02, x = 2, label = str_glue('predicting~bar({measure_uppercase})'),
           size = annotate_text_size,
           parse = T, angle = 270)

score_out <- str_glue("fig_DEAP_{measure}_{y_stat}_model_comp_{date_and_time}")

fname_output <- fname + fname_2 + score_out


ggsave(paste0(fname_output, ".png"),
       width = 8, height = 5, dpi = 300)
ggsave(paste0(fname_output, ".pdf"),
       useDingbats = F,
       width = 8, height = 5 , dpi = 300)