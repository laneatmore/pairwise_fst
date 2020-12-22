library(viridis)
library(ggplot2)
library(tidyverse)

pairwise_fst <- read.csv("output/pairwise_fst.csv", header = TRUE)
row.names(pairwise_fst) <- pairwise_fst$X

pairwise_fst <- pairwise_fst %>%
  pivot_longer(
    cols = -X, 
    names_to = "colname", 
    values_to = "fst"
  ) %>% 
  mutate(rowname = fct_inorder(X),
         colname = fct_inorder(colname))

pdf('output/pairwise_matrix.pdf')
ggplot(pairwise_fst, aes(X, fct_rev(colname), 
                 fill = fst)) + 
  geom_tile() + 
  geom_text(aes(label = round(fst, 3))) +
  coord_fixed() +
  labs(x = NULL, y = NULL)
dev.off()

