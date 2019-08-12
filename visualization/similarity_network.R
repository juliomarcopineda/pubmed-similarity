library(igraph)
library(RColorBrewer)

# Read Node Data
nodes_data <- read.csv("~/nodes.csv")
nodes_data$journal <- as.factor(nodes_data$journal)

# Read Edge Data
edges_data <- read.csv("~/edges.csv")

# Create network from data
net <- graph_from_data_frame(d = edges_data,
                             directed = FALSE,
                             vertices = nodes_data)

# Cut edges by a certain threshold
threshold <- 0.5
net.cut <- delete_edges(net, E(net)[weight>threshold])

# Remove lone nodes
net.cut <- delete.vertices(net.cut, degree(net.cut) == 0)

# Set edge width based on weight
## Scale the widths
widths <- E(net.cut)$weight / max(E(net.cut)$weight)
E(net.cut)$width <- widths * 5

# Use graph layout algorithm
l <- layout_with_fr(net.cut)
l <- norm_coords(l, ymin=-1, ymax=1, xmin=-1, xmax=1)

# Plot network
png("network.png", width = 1280*2, height = 1280*2)
plot(net.cut,
     vertex.size = 3,
     vertex.label = NA,
     vertex.color = "steelblue",
     vertex.frame.color = "black",
     edge.color = "black",
     rescale = F,
     layout = l,
     )
dev.off()


# Detect communities in the network
ceb <- cluster_edge_betweenness(net.cut, 
                                weights = 1 - E(net.cut)$weight)

png("cluster.png", width = 1280*2, height = 1280*2)
plot(ceb,
     net.cut,
     vertex.label = NA,
     vertex.size = 3,
     vertex.color = "steelblue",
     vertex.frame.color = "black",
     edge.color = "black",
     rescale = F,
     layout = l
     )
dev.off()

# Dendogram of communitiesular
png(filename = 'dendrogram.png',
    width = 960,
    height = 960)
plot_dendrogram(ceb,
                mode = "hclust",
                xlab = "PMID"
         )
dev.off()

# Get cluster memberships
clusters <- membership(ceb)
clusters_df <- data.frame(matrix(nrow = length(clusters), ncol = 2))
colnames(clusters_df) <- c('ClusterID', 'PMID')
clusters_df$ClusterID <- clusters
clusters_df$PMID <- names(clusters)

write.csv(clusters_df,
          file = '~/clusters.csv',
          quote = FALSE,
          row.names = FALSE)

# Plot membership
V(net.cut)$community <- ceb$membership
colrs <- brewer.pal(11, "Paired")
# colrs[1:4] <- rep("black", 4)
# colrs[6:11] <- rep("black", 6)
net_color <- V(net.cut)$community
net_color <- as.factor(net_color)
levels(net_color) <- colrs
net_color <- as.character(net_color)
V(net.cut)$color <- net_color

png("clusters.png", width = 1280*2, height = 1280*2)
plot(net.cut,
     vertex.label = NA,
     vertex.size = 3,
     vertex.frame.color = "black",
     edge.color = "black",
     rescale = F,
     layout = l
)
# legend(x=1.5,
#        y=1.1,
#        levels(as.factor(V(net.cut)$community)), pch=21,
#        col="#777777", pt.bg=colrs, pt.cex=2, cex=.8, bty="n", ncol=1)
dev.off()
