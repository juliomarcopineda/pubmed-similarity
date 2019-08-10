library(igraph)

nodes_data <- read.csv("~/nodes.csv")
# nodes_data$journal <- as.character(nodes_data$journal)
# nodes_data[nodes_data$journal == "Science (New York, N.Y.)",] <- rep("Science", nrow(nodes_data[nodes_data$journal == "Science (New York, N.Y.)",]))
nodes_data$journal <- as.factor(nodes_data$journal)

edges_data <- read.csv("~/edges.csv")
threshold <- 0.5

# edges <- edges_data[edges_data$weight > threshold,]

net <- graph_from_data_frame(d = edges_data,
                             directed = FALSE,
                             vertices = nodes_data)
plot(net,
     vertex.size = 3,
     vertex.label = NA)

colrs <- c("gray50", "tomato", "gold")

net_color <- V(net)$journal
net_color <- as.factor(net_color)
levels(net_color) <- colrs
net_color <- as.character(net_color)

# V(net)$color <- net_color
E(net)$width <- E(net)$weight*1.5

net.cut <- delete_edges(net, E(net)[weight>threshold])
net.cut <- delete.vertices(net.cut, degree(net.cut) == 0)

l <- layout_with_fr(net.cut)
l <- norm_coords(l, ymin=-1, ymax=1, xmin=-1, xmax=1)

plot(net.cut,
     vertex.size = 3,
     vertex.label = NA,
     # edge.lty = 0,
     rescale = F,
     layout = l*1.5,
     )
legend(x=-1.5,
       y=-1.1,
       levels(as.factor(V(net)$journal)), pch=21,
       col="#777777", pt.bg=colrs, pt.cex=2, cex=.8, bty="n", ncol=1)

ceb <- cluster_edge_betweenness(net.cut, weights = E(net.cut)$weight)
plot(ceb,
     net.cut,
     #vertex.label.cex = 0.75,
     #vertex.label.family = "Helvetica",
     vertex.label = NA,
     vertex.size = 3,
     rescale = F,
     layout = l*1.5
     )

netm <- get.adjacency(net, attr = "weight", sparse = F)
palf <- colorRampPalette(c("gold", "dark orange")) 
heatmap(netm, col = palf(100))

    
