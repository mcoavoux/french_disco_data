
ID,FORM,LEMMA,CPOS,FPOS,MORPH,HEAD,DEPREL,PHEAD,PDEPREL=range(10)

class CtbkTree:
    def __init__(self, label, children = []) :
        self.label = label
        self.children = children
        self.token = None
        self.head = None
        self.morph = None
        self.idx = None

    def is_leaf(self) :
        return len(self.children) == 0

    def get_dep_graph(self, dic) :
        """Extract a dependency graph from lexicalized constituency tree"""
        if self.is_leaf() :
            return self.idx
        if len(self.children) == 1 :
            return self.children[0].get_dep_graph(dic)
        idxes = []
        for i,c in enumerate(self.children) :
            if c.head :
                h_idx = c.get_dep_graph(dic)
            else :
                idxes.append(c.get_dep_graph(dic))
        for i in idxes :
            dic[i] = h_idx
        return h_idx

    def get_frontier(self, lst) :
        if self.is_leaf() :
            lst.append(self)
        else :
            for c in self.children :
                c.get_frontier(lst)


def is_xml(s) : return s[0] == "<" and s[-1] == ">"
def is_xml_beg(s) : return is_xml(s) and s[1] != "/"
def is_xml_end(s) : return is_xml(s) and not is_xml_beg(s)
def is_head(s) : return is_xml(s) and "^head" in s
def get_nt_from_xml(s) :
    if is_xml_beg(s) :
        s = s[1:-1]
    elif is_xml_end(s) :
        s = s[2:-1]
    else : assert(False)
    if s[-5:] == "^head" :
        return s[:-5]
    return s


def parse_token(line) :
    idx, line = line[0],line[1:]
    tok = CtbkTree(line[1], [])
    tok.token = line[0]
    tok.head = "^head" in idx
    tok.morph = line[2:]
    tok.idx = int(idx.split("^")[0])
    return tok

def read_tbk_tree_rec(lines, beg, end, headersize) :
    if len(lines[beg]) == 1 :
        assert(is_xml_beg(lines[beg][0]))
        assert(is_xml_end(lines[end-1][0]))
        label = get_nt_from_xml(lines[beg][0])
        assert(label == get_nt_from_xml(lines[end-1][0]))
        i = beg + 1
        c_beg = []
        counter = 0
        while i < end :
            if counter == 0 :
                c_beg.append(i)
            if is_xml_beg(lines[i][0]) :
                counter += 1
            elif is_xml_end(lines[i][0]) :
                counter -= 1
            i += 1
        children = [ read_tbk_tree_rec(lines, i, j, headersize) for i,j in zip(c_beg[:-1], c_beg[1:]) ]
        is_head = "^head" in lines[beg][0]
        node = CtbkTree(label, children)
        node.head = is_head
        node.idx = min([c.idx for c in node.children])
        node.children = sorted(node.children, key = lambda x : x.idx)
        return node
    else :
        assert(len(lines[beg]) == headersize + 1)
        assert(end == beg + 1)
        return parse_token(lines[beg])

def read_tbk_tree(string, headersize) :
    lines = [ line.strip().split("\t") for line in string.split("\n") if line.strip()]
    return read_tbk_tree_rec(lines, 0, len(lines), headersize)

def read_ctbk_corpus(filename) :
    instream = open(filename, "r")
    header = instream.readline().strip().split()
    sentences = instream.read().split("\n\n")

    return [ read_tbk_tree(s, len(header)) for s in sentences if s.strip() ], header

def get_conll(tree, mheader):
    dic = {}
    tokens = []
    tree.get_dep_graph(dic)
    tree.get_frontier(tokens)

    conll_tokens = []
    for tok in tokens :
        newtok = ["_" for i in range(10)]
        newtok[ID]   = str(tok.idx)
        newtok[FORM] = tok.token
        newtok[CPOS] = newtok[FPOS] = tok.label
        newtok[MORPH] = "|".join(["{}={}".format(a,v) for a,v in zip( mheader, tok.morph) if v != "UNDEF"])
        if tok.idx in dic :
            newtok[HEAD] = str(dic[tok.idx])
        else :
            newtok[HEAD] = "0"
        conll_tokens.append(newtok)
    return sorted(conll_tokens, key = lambda x : int(x[0]))

def write_conll(ctree, out) :
    for tok in ctree :
        out.write("{}\n".format("\t".join(tok)))

if __name__=="__main__":
    import sys
    import argparse

    usage = """
        Convert a lexicalized constituency treebank to conll dependency corpus.
        Input format: .ctbk
        Algo: 
            for a rewrite rule: A[h] -> B[x1] C[x2] D[h] E[x4] F[x5]
                add arcs    x1 -> h
                            x2 -> h
                            x3 -> h
                            x4 -> h
                (and call recursively on each subtree)
        No additional heuristic is used
    """

    parser = argparse.ArgumentParser(description = usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("ctbk", type = str, help="corpus .ctbk")
    parser.add_argument("output", type = str, help="Output (conll format)")

    args = parser.parse_args()
    ctbkfile = args.ctbk
    output = args.output

    corpus, header = read_ctbk_corpus(ctbkfile)
    out = open(output, "w")
    for tree in corpus :
        ctree = get_conll(tree, header[2:])
        write_conll(ctree, out)
        out.write("\n")
