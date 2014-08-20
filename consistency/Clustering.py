def CommonValueClustering(items, function):
    clusters = {}
    
    for item in items:
        clusterName = function(item)
        if not clusterName in clusters:
            clusters[clusterName] = set()
        clusters[clusterName].add(item)
        
    return clusters

# Modification of single-linkage clustering in which the items are processed in a certain order
# without the possibility of clusters getting combined
def SingleLinkageOrderedClustering(items, ordering, metric, threshold):
    clusters = {}
    added = False
    
    for item in sorted(items, key=ordering.get, reverse=True):
        for cluster in clusters.values():
            for cmpItem in cluster:
                if (metric(item, cmpItem) <= threshold):
                    cluster.add(item)
                    added = True
                    break
            if added:
                break
        if not added:
            clusterName = str(len(clusters)+1)
            clusters[clusterName] = set([item])
            
    return clusters

