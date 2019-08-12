library(RColorBrewer)
library(wordcloud)

clusters_tfidf <- read.csv("~/clusters_tfidf.csv")
clusters_tfidf$Token <- as.character(clusters_tfidf$Token)
clusters_tfidf[clusters_tfidf$Token == "Receptor_Epidermal_Growth_Factor", c("Token")] <- "EFG_receptor"
clusters_tfidf[clusters_tfidf$Token == "Triple_Negative_Breast_Neoplasms", c("Token")] <- "TripleNeg_Breast_Neoplasms"
clusters_tfidf[clusters_tfidf$Token == "Leukemia_Myeloid_Acute", c("Token")] <- "Leukemia_Myeloid"

id <- 5
clust <- clusters_tfidf[clusters_tfidf$ClusterID == id,]
pal2 <- brewer.pal(8,"Dark2")
w <- 1280
h <- 800

png(paste("wordcloud", id, ".png", sep = ""), width = w, height = h)
wordcloud(words = clust$Token,
          freq =  clust$Weight,
          random.order = FALSE,
          scale = c(7, .2),
          rot.per = .15,
          max.words = 100,
          colors = pal2)
dev.off()

for (id in seq(1, max(clusters_tfidf$ClusterID))) {
    clust <- clusters_tfidf[clusters_tfidf$ClusterID == id,]
    
    # clust$Scaled <- clust$Weight / max(clust$Weight)
    # clust$Scaled <- clust$Scaled * 1000
    # clust$Scaled[200:length(clust$Scaled)] <- clust$Scaled[200:length(clust$Scaled)] / 100
    
    pal2 <- brewer.pal(8,"Dark2")
    w <- 1280
    h <- 800
    
    png(paste("wordcloud", id, ".png", sep = ""), width = w, height = h)
    wordcloud(words = clust$Token,
              freq =  clust$Weight,
              random.order = FALSE,
              # scale = c(8, .2),
              rot.per = .15,
              # max.words = 100,
              colors = pal2)
    dev.off()
}
    