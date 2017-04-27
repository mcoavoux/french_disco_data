import ctbk





if __name__=="__main__":
    import sys
    import argparse

    usage = """
        Convert a ctbk format treebank to raw parsing data.
    """

    parser = argparse.ArgumentParser(description = usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("ctbk", type = str, help="corpus .ctbk")
    parser.add_argument("output", type = str, help="Output")

    args = parser.parse_args()
    ctbkfile = args.ctbk
    output = args.output

    corpus, header = ctbk.read_ctbk_corpus(ctbkfile)
    out = open(output, "w")
    out.write("word\ttag\n")
    for tree in corpus :
        lst = []
        tree.get_frontier(lst)
        lst.sort(key = lambda x : x.idx)
        for token in lst :
            out.write("{}\tUNKNOWN\n".format(token.token))
        out.write("\n")
    out.close()

