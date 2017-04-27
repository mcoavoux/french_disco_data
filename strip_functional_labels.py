

from nltk import Tree as Tree
from replace_brackets import replace_brackets

def strip_functional_labels(tree) :
    if type(tree) == str :
        return
    tree.set_label(tree.label().split("-")[0])
    tree.set_label(tree.label().split("@@")[0]) # also strip diatheses annotation
    for t in tree :
        strip_functional_labels(t)

def replace(tree) :
    for i,t in enumerate(tree) :
        if type(t) == str :
            tree[i] = replace_brackets(t)
        else :
            replace(t)
            



if __name__=="__main__":
    import sys
    import argparse

    usage = """
        input: bracketed corpus (1 sent per line)
        output: idem without functional labels
    """

    parser = argparse.ArgumentParser(description = usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("input", type = str)
    parser.add_argument("output", type = str)
    
    
    args = parser.parse_args()
    
    infile = args.input
    outfile = args.output
    
    trees = [Tree.fromstring(line.strip()) for line in open(infile)]
    
    out = open(outfile, "w")
    for tree in trees: 
        strip_functional_labels(tree)
        replace(tree)
        out.write("{}\n".format(tree.pformat(margin=10000000)))
    out.close()

