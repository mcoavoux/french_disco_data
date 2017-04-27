from nltk import Tree
import sys

def contains_eldd(tree) :
    """Returns True iff tree contains an effectively long distance dependency"""
    if type(tree) == str :
        return False
    if "::" in tree.label() :
        return True
    for child in tree :
        if contains_eldd(child) :
            return True
    return False

def find_eldd(tree, ancestors) :
    """
    Returns (ancestors, node):
        node: node containing a functional path 
        ancestors: its ancestors.
    Returns (None, None) if there is no such node
    """
    for child in tree :
        if type(child) == str:
            continue
        t,c = find_eldd(child, ancestors + [child])
        if (t,c) != (None, None) :
            return t,c
        if "::" in child.label() :
            return ancestors + [child], child
    return None, None

def attach(parent, node, path, grandparent) :
    """
    Attach node by following functional path starting from parent.
    
    Lots of heuristics to handle these cases
    - if attachment fails, follow functional path from grandparent 
    - functional label mismatch: OBJ vs OBJ_L, *empty* vs DEP, etc
    - ad hoc cases: this function includes patches done after manual
        validation to correct a number of cases.
    """
    if len(path) == 1:
        oldlabel = node.label().split("::")[0].split("-")
        newlabel = oldlabel[0] + "-" + path[0]
        if len(oldlabel) > 1 and oldlabel[1] != path[0] :
            print("replaced label ", oldlabel[1], "by", path[0])
        node.set_label(newlabel)
        parent.append(node)
    else :
        
        ## differences in functional labels
        if path[-1] == "OBJ_L" :
            path[-1] = "OBJ"
            print("Warning: turned OBJ_L into OBJ and searching for grandparent")
            print("parent=", parent.pformat(margin=10000))
            print("grandparent=", grandparent.pformat(margin=10000))
            attach(grandparent, node, path, None)
            return

        if path[-1] == "MOD_L" :
            path[-1] = "MOD"
            print("Warning: turned MOD_L into MOD")
        
        if path[-1] in  {"OBJ.P", "OBJ.CPL", "DEP.COORD"}:
            print("Warning. Matching {} (in path) with {} subtree: {}".format(path[-1], parent[1].label(), parent.pformat(margin=100000)))
            attach(parent[1], node, path[:-1], grandparent)
            return

        ## DEP labels
        if path[-1] in {"DEP_L", "DEP"} :
            for lab in ["PP", "VPinf-OBJ", "VPinf"]:
                for c in reversed(parent) :
                    if c.label() == lab :
                        print("Warning. Matching {} (in path) with {} subtree: {}".format(path[-1], c.label(), parent.pformat(margin=100000)))
                        attach(c, node, path[:-1], grandparent)
                        return
            assert(False)

        
        ## Ad hoc strategy -> solves 3 cases in FTB
        if path[-1] == "MOD" and all(["MOD" not in child.label() for child in parent]):
            #sys.stderr.write("MOD {}\n".format(parent.pformat(margin=100000)))

            for c in reversed(parent) :
                if c.label() == "VPinf" :
                    print("Warning. Matching {} (in path) with {} subtree: {}".format(path[-1], c.label(), parent.pformat(margin=100000)))
                    attach(c, node, path[:-1], grandparent)
                    return
            print("MOD: resuming search from grandparent")
            print("grandparent=", grandparent.pformat(margin=10000))
            attach(grandparent, node, path, None)
            return
        
        ## Ad hoc strategy -> solves 3 cases in FTB
        if path[-1] == "DE_OBJ" and all(["DE_OBJ" not in child.label() for child in parent]):
            #sys.stderr.write("DE_OBJ {}\n".format(parent.pformat(margin=100000)))
            if (parent[0].label() == "ADJ" and parent[1].label() == "PP") or (parent[0].label() == "VN" and parent[1].label() == "PP-DE_OBJ") :
                print("Warning. Matching {} (in path) with {} subtree: {}".format(path[-1], parent[1].label(), parent.pformat(margin=100000)))
                attach(parent[1], node, path[:-1], grandparent)
                return
            elif len(parent) == 3 and [parent[i].label() for i in range(3)] == ["ADV", "ADJ", "PP"]:
                print("Warning. Matching {} (in path) with {} subtree: {}".format(path[-1], parent[2].label(), parent.pformat(margin=100000)))
                attach(parent[2], node, path[:-1], grandparent)
                return
            assert(False)

        ## Ad hoc strategy -> solves 1 case in FTB
        if path[-1] == "COORD" :
            #sys.stderr.write("COORD {}\n".format(parent.pformat(margin=100000)))
            if grandparent != None :
                print("COORD: grandparent")
                attach(grandparent, node, path, None)
                return
            for c in parent :
                if c.label() == "COORD" :
                    print("Warning. Matching {} (in path) with {} subtree: {}".format(path[-1], c.label(), parent.pformat(margin=100000)))
                    attach(c, node, path[:-1], grandparent)
                    return
            assert(False)

        ## Ad hoc strategy -> solves 1 case in FTB
        if path[-1] == "A_OBJ" and all(["A_OBJ" not in child.label() for child in parent]):
            #sys.stderr.write("A_OBJ {}\n".format(parent.pformat(margin=100000)))
            print([child.label() for child in parent])
            assert(len(parent) == 2)
            assert(parent[0].label() == "ADJ")
            assert(parent[1].label() == "PP")
            print("Warning. Matching {} (in path) with {} subtree: {}".format(path[-1], parent[1].label(), parent.pformat(margin=100000)))
            attach(parent[1], node, path[:-1], grandparent)
            return
        

        nts = [child.label().split("-") for child in parent]
        nts = [tt for tt in nts if len(tt) > 1]
        if len([nt for nt in nts if nt[1] == path[-1]]) > 1 :
            print("Warning: several subtrees have same functional label.")
        
        if "NP" in [nt[0] for nt in nts if nt[1] == path[-1]] :
            for child in parent :
                nt = child.label().split("-")
                if len(nt) > 1 :
                    if  nt[1] == path[-1] :
                        attach(child, node, path[:-1], grandparent)
                        return
            assert(False)

        for child in reversed(parent) :
            nt = child.label().split("-")
            if len(nt) > 1 :
                if  nt[1] == path[-1] :
                    attach(child, node, path[:-1], grandparent)
                    return

        print("Functional path not working, trying again from grandparent for subtree : ", node)
        print("parent=", parent.pformat(margin=10000))
        print("grandparent=", grandparent.pformat(margin=10000))
        attach(grandparent, node, path, None)

def reattach_eldd(tree) :
    
    ancestors, node = find_eldd(tree, [tree])  # get the node with functional path
    parent = ancestors[-2]
    grandparent = ancestors[-3] if len(ancestors) > 2 else None
    
    path = node.label().split("::")[1].split("/")  # retrieve functional path
    
    deli = None
    if len(parent) == 1 :
        if len(grandparent) == 1 :
            grandparent=ancestors[-4]
            for i in range(len(grandparent)) :
                if len(grandparent[i]) == 1 and grandparent[i][0][0].label() == node.label() :
                    deli = i
                    break
            print("Removing node + parent + grandparent (all unary nodes).", grandparent.pformat(margin=100000))
            del grandparent[deli]   # delete node
            attach(grandparent, node, path, None) # reattach it by following functional path
        else :
            for i in range(len(grandparent)) :
                if len(grandparent[i]) == 1 and type(grandparent[i]) != str and len(grandparent[i][0]) == 1 and grandparent[i][0].label() == node.label() :
                    deli = i
                    break
            print("Removing node + parent (was an unary node).", grandparent.pformat(margin=100000))
            del grandparent[deli]   # delete node
            attach(grandparent, node, path, None) # reattach it by following functional path
    else :
        for i in range(len(parent)) :
            if parent[i].label() == node.label() :
                deli = i
                break
        del parent[deli]   # delete node

        attach(parent, node, path, grandparent) # reattach it by following functional path

def remove_annotations_on_terminals(tree) :
    if type(tree) == str :
        return
    else :
        if len(tree) == 1 and type(tree[0]) == str :
            label = tree.label()
            if "##" in label:
                tree.set_label(label.split("##")[0])
                print("Replacing {} by {}".format(label, tree.label()))
        for c in tree :
            remove_annotations_on_terminals(c)

def get_list_of_terminals(tree) :
    if type(tree) == str :
        return [tree]
    else :
        res = []
        for c in tree :
            res.extend(get_list_of_terminals(c))
        return res

def get_number_of_nodes(tree) :
    if type(tree) == str :
        return 1
    return 1 + sum((get_number_of_nodes(c) for c in tree))

if __name__=="__main__":
    import sys
    import argparse
    import random
    
    usage = """
    Use eldd annotations (See Candito & Seddah, 2012) to produce
    a discontinuous corpus from a projective corpus.
    input and output format: discbracket.
        input treebank is anotated with functional paths: ex: NP::OBJ/OBJ
    """
    
    parser = argparse.ArgumentParser(description = usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("corpus", type = str, help="corpus")

    args = parser.parse_args()
    corpus = args.corpus
    
    folder,corpus = corpus.rsplit("/", 1)

    
    trees = []
    original_trees = []
    with open(folder + "/" + corpus, "r", encoding="utf8") as instream :
        lines = [ line.strip()[1:-1] for line in instream ]
        trees = [Tree.fromstring(line) for line in lines]
        original_trees = [Tree.fromstring(line) for line in lines]
    
    print(len(trees))
    print(len(original_trees))
    
    
    ## Print trees that have been modified for manual checking
    modified = open(folder + "/modified_trees", "w", encoding="utf8")
    for i,tree in enumerate(trees) :
        while contains_eldd(tree) :
            modified.write(tree.pformat(margin=100000) + "\n")
            reattach_eldd(tree)
            modified.write(tree.pformat(margin=100000) + "\n")
        
        frontier1 = sorted(get_list_of_terminals(tree))
        frontier2 = sorted(get_list_of_terminals(original_trees[i]))
        
        if frontier1 != frontier2 :
            print(frontier1)
            print(frontier2)
        assert(frontier1 == frontier2)
        assert(get_number_of_nodes(tree) == get_number_of_nodes(original_trees[i]))
        
    modified.close()
    
    ## print discontinuous corpus
    newcorpus = open(folder + "/disco_" + corpus.split(".")[0] + ".discbracket", "w", encoding="utf8")
    for tree in trees : 
        newcorpus.write(tree.pformat(margin=100000) + "\n")
    newcorpus.close()





