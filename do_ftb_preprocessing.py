from discbracket_to_ctbk import*


def split_conll_corpus(conll):
    """SPMRL standard split"""
    train, dev, test = [],[],[]

    bound = len(conll) - (2541-1235)

    test = [conll[i] for i in range(bound, len(conll))] + [conll[i] for i in range(1235)]
    dev = [conll[i] for i in range(1235, 2470)]
    train = [conll[i] for i in range(2470, bound)]

    return train, dev, test

def check_identity(ccorpus, dcorpus) :
    """Returns true if both corpora have the same terminals
    (modulo special symbols for brackets, etc)"""
    assert(len(ccorpus) == len(dcorpus))
    for c,d in zip(ccorpus, dcorpus) :
        cterminals = []
        c.get_list_of_terminals(cterminals)
        dterminals = [word[FORM].replace("(", "-LRB-").replace(")", "-RRB-").replace("[", "-LSB-").replace("]", "-RSB-") for word in d]
        if cterminals != dterminals :
            print(cterminals)
            print(dterminals)
            assert(cterminals == dterminals)

def has_functional_label(s) :
    return len(s.split("-")) > 1

def is_mwe(s) :
    """True iff s is a MWE tag"""
    res = "+" in s.split("-")[0]
    if res :
        assert s.split("-")[0][-1] == "+"
    return res

def add_functional_paths_rec(c, d) :
    if c.is_preterminal() :
        idx = c.left_index
        assert(idx == int(d[idx][ID]) - 1)
        dmorph = d[idx][MORPH]

        if dmorph != "_" :
            dmorph = dict([ av.split("=")  for av in dmorph.split("|") ])

            if "fctpath" in dmorph:
                path = dmorph["fctpath"]
                #if has_functional_label(c.label) :
                c.label += "::{}".format(path.upper())
                #else :
                print("Changed {} to {}".format(c.label.split("::")[0], c.label))
    elif is_mwe(c.label) :
        idxes = [p.left_index for p in c.children]
        dmorphes = [d[idx][MORPH] for idx in idxes]
        dmorphes = [ dict([ av.split("=")  for av in dmorph.split("|") ]) for dmorph in dmorphes if dmorph != "_" ]
        dmorphes = [ dic["fctpath"] for dic in dmorphes if "fctpath" in dic ]
        if len(set(dmorphes)) > 0 :
            assert(len(set(dmorphes))==1)
            print("Spotted mwe with fctpath, annotating MWE+ cat instead of terminals")
            path = dmorphes[0]
            #if has_functional_label(c.label) :
            c.label += "::{}".format(path.upper())
            #else :
            print("Changed {} to {}".format(c.label.split("::")[0], c.label))
    else :
        for subtree in c.children :
            add_functional_paths_rec(subtree, d)

def has_prorel(c) :
    if c.label.startswith("PROREL") or c.label.startswith("DETWH"):
        if c.label.startswith("DETWH"):
            print("DETWH")
        return True
    for child in c.children :
        hasp = has_prorel(child)
        if hasp :
            return True
    return False

def has_functional_path(c) :
    return "::" in c.label or (len(c.children) == 1 and "::" in c.children[0].label)

def conll_functional_paths(dtree):
    res = []
    for token in dtree :
        dmorph = token[MORPH]
        if "fctpath" in dmorph :
            res.append(token)
    return res


def percolate_functional_paths_to_extracted_phrases(c, d) :
    if c.is_preterminal() :
        return
    if c.label.startswith("PP") or c.label.startswith("NP") :
        if len(c.children) == 2 :
            if has_functional_path(c.children[0]) :
                path = c.children[0].label.split("::")
                c.children[0].label = path[0]
                c.label += "::{}".format(path[1])
                print("Percolating information to phrase: from {} to {} (full binary PP with PROREL extracted)".format(path, c.label))
                return
        if len(c.children) == 1 :
            if has_prorel(c.children[0]) and has_functional_path(c.children[0]) :
                path = c.children[0].label.split("::")
                c.children[0].label = path[0]
                c.label += "::{}".format(path[1])
                print("Percolating information to phrase: from {} to {} (full unary PP with PROREL extracted)".format(path, c.label))
                return
            if has_functional_path(c.children[0]) :
                path = c.children[0].label.split("::")
                if len(path) == 2 :
                    c.children[0].label = path[0]
                elif len(path) == 1 :
                    path = c.children[0].children[0].label.split("::")
                    c.children[0].children[0].label = path[0]
                c.label += "::{}".format(path[1])
                print("Percolating information to phrase: from {} to {} (full unary PP extracted)".format(path, c.label))
                return
        if len(c.children) == 3 :
            if has_prorel(c.children[0]) and has_functional_path(c.children[1]) :
                path = c.children[1].label.split("::")
                c.children[1].label = path[0]
                c.label += "::{}".format(path[1])
                print("Percolating information to phrase: from {} to {} (full unary PP with PROREL extracted)".format(path, c.label))
                return
    for child in c.children :
        percolate_functional_paths_to_extracted_phrases(child, d)

def add_functional_paths_on_preterminals(ccorpus, dcorpus, logger) :

    for i,c in enumerate(ccorpus) :
        c.strip_spmrl_morphological_annotations()

        paths = conll_functional_paths(dcorpus[i])
        if len(paths) > 0 :
            add_functional_paths_rec(c, dcorpus[i])
            percolate_functional_paths_to_extracted_phrases(c, dcorpus[i])
            c.print_discbracket(logger)
            logger.write("\n")

def write_conll(corpus, filename):
    with open(filename, "w") as f :
        for sentence in corpus :
            for word in sentence :
                f.write("\t".join(map(str, word)) + "\n")
            f.write("\n")




if __name__ == "__main__" :
    """
    input:
        unsplit conll file with functional paths annotated at the token level
        spmrl constituency treebanks
    output:
        spmrl treebanks with functional paths annotated on non-terminals
    """
    
    
    dirname="disco_ftb"

    fctrain = "{}/spmrl_{}.discbracket".format(dirname, "train")
    fcdev = "{}/spmrl_{}.discbracket".format(dirname, "dev")
    fctest = "{}/spmrl_{}.discbracket".format(dirname, "test")

    fd="{}/surf.ftb.np_conll".format(dirname)


    td = read_conll(fd)

    ctrain, cdev, ctest = [[Tree(nTree.fromstring(line.strip())) for line in open(f)] for f in [fctrain, fcdev, fctest]]

    print(len(ctrain), len(cdev), len(ctest), sum((len(ctrain), len(cdev), len(ctest))))
    print(len(td))

    dtrain, ddev, dtest = split_conll_corpus(td)

    for corpus, type in zip([dtrain, ddev, dtest], ["train", "dev", "test"]) :
        write_conll(corpus, "{}/surf.ftb.{}.np_conll".format(dirname, type))

    logger = open("{}/paths_annotation_logger.txt".format(dirname), "w")

    for cc, dc, corpus in zip( [ctrain, cdev, ctest], [dtrain, ddev, dtest], ["train", "dev", "test"] ) :
        check_identity(cc, dc)

        add_functional_paths_on_preterminals(cc, dc, logger)

        outfile = open("{}/spmrl_{}_with_paths.discbracket".format(dirname, corpus), "w")
        for t in cc :
            t.print_discbracket(outfile)
            outfile.write("\n")
        outfile.close()
    logger.close()


    ctrain2, cdev2, ctest2 = [[Tree(nTree.fromstring(line.strip())) for line in open(f)] for f in [fctrain, fcdev, fctest]]

    for c1,c2 in zip([ctrain, cdev, ctest], [ctrain2, cdev2, ctest2]) :
        for t1,t2 in zip(c1,c2) :
            t2.strip_spmrl_morphological_annotations()
            if not t1.equal_modulo_functional_paths(t2) :
                t1.print_discbracket(sys.stdout)
                print()
                t2.print_discbracket(sys.stdout)
                print()
                print()
            assert(t1.equal_modulo_functional_paths(t2))
