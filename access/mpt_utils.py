#Generate tree list from queryset using Materialized Path Tree (MPT)
#Object must have Path field and follow MPT structure
#MPT: https://youtu.be/CRxjoklS8v0?t=428
def create_tree_list(qs, max_depth, depth=1, leaf=None):
    #Declare list
    tree_list = []
    
    #Filter queryset based on path level (length) and starting characters from the parent
    if leaf:
        result = qs.filter(path__length=depth, path__startswith=leaf).distinct().order_by('path')
    else:
        result = qs.filter(path__length=depth).order_by('path')

    #Increment depth 
    depth += 1

    #For each result:
    #   Add to list
    #   Recursive call this function to get children
    for r in result:
        tree_list.append(r)

        if depth <= max_depth:
            child_list = []
            child_list = create_tree_list(qs=qs, max_depth=max_depth, depth=depth, leaf=r.path)
            if child_list:
                tree_list.append(child_list)

    return tree_list