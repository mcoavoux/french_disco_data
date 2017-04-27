from nltk import Tree as nTree
from collections import Counter, defaultdict
import sys
from read_headrules import *
from replace_brackets import replace_brackets

ID,FORM,LEMMA,CPOS,FPOS,MORPH,HEAD,DEPREL,PHEAD,PDEPREL=range(10)

SPACE="  "

## mapping tagsets used in corpus and in headrules
tagset_mapping={"VS" : "V", "VINF" : "V", "VPP" : "V", "VPR" : "V", "VIMP" : "V",
                "NC" : "N", "NPP" : "N", "CS" : "C", "CC" : "C",
                "CLS" : "CL", "CLO" : "CL", "CLR" : "CL", "P+D" : "P", "P+PRO" : "P",
                "ADJ" : "A", "ADJWH" : "A", "ADVWH" : "ADV",
                "PROREL" : "PRO", "PROWH" : "PRO", "DET" : "D", "DETWH" : "D",
                "V" : "V",
                "P" : "P",
                "I" : "I",
                "PONCT" : "PONCT",
                "ET" : "ET",
                "ADV" : "ADV",
                "PRO" : "PRO",
                "P+" : "P",
                "NC+" : "NC",
                "CC+" : "C"}

## morphological attributes used in ctbk
MORPH_FIELDS = {"french" : ["m", "n", "p", "t", "s", "g", "mwehead", "component"],
                "german" : ["case", "number", "gender", "degree", "tense", "mood", "person"]}

def get_ctbk_token(postag, conll_token, mfields) :
    morph = conll_token[MORPH]
    morphd = defaultdict(lambda:"UNDEF")
    for av in morph.split("|") :
        if av != "_" :
            a,v = av.split("=")
            if a in mfields:
                morphd[a] = v
            else :
                print("ignoring : {}".format(av))
    return [str(conll_token[ID]), conll_token[FORM], postag] + [morphd[key] for key in mfields] + [conll_token[DEPREL]]

def map_tag(tag, lang) :
    if lang == "french" :
        if tag in tagset_mapping :
            return tagset_mapping[tag]
        return tag
    else :
        return tag

def find_head(label, nonterminals, headrules) :
    label = map_tag(label, headrules["__LANG__"])
    nonterminals = [ map_tag(nt, headrules["__LANG__"]) for nt in nonterminals ]

    for d, cats in headrules[label] :
        if d == "left-to-right" :
            for c in cats :
                for i, nt in enumerate(nonterminals) :
                    if nt == c :
                        return i
            if headrules["__LANG__"] == "german" :
                return 0
        elif d == "right-to-left" :
            for c in cats :
                for i, nt in reversed(list(enumerate(nonterminals))) :
                    if nt == c :
                        return i
            if headrules["__LANG__"] == "german" :
                return len(nonterminals) - 1

    print(label, nonterminals)
    assert(False)


class Tree :
    """Tree class with different types of annotations"""
    def __init__(self, t) :
        """
        t -- nltk tree
        """
        if type(t) == str :
            i,label = t.split("=",1)
            self.label = label
            self.children = []
            self.left_index = int(i)
            self.span = {self.left_index}
        else :
            self.label = t.label()
            self.children = [Tree(c) for c in t]
            self.children.sort(key = lambda x : x.left_index)
            self.left_index = min((c.left_index for c in self.children))
            self.span = set()
            for c in self.children :
                self.span |= c.span

        self.full_label = None
        self.functional_label = None
        self.head = None
        self.is_head = False

    def is_leaf(self):
        return self.children == []

    def is_preterminal(self) :
        return len(self.children) == 1 and self.children[0].is_leaf()

    def assign_full_label(self, conlltree) :
        """
        Uses conlltree given as argument to annotate each terminal with
        the corresponding conll token.
        """
        if self.is_leaf() :
            self.full_label = conlltree[self.left_index]
            self.head = self.left_index
            assert self.left_index + 1 == self.full_label[0]  # checking that ID matches between c and d corpus
        else :
            for c in self.children :
                c.assign_full_label(conlltree)

    def assign_heads(self, headrules) :
        if self.is_leaf() :
            return

        for c in self.children :
            c.assign_heads(headrules)

        if len(self.children) > 1 :
            heads = [c.get_head() for c in self.children]

            heads_outside_current_const = [h not in self.span for h in heads]
            if sum(heads_outside_current_const) == 1 :
                idx = heads_outside_current_const.index(True)
                self.children[idx].is_head = True

                self.head = self.children[idx].head
                self.full_label = self.children[idx].full_label
                if not all( [h == self.children[idx].head for i,h in enumerate(heads) if not heads_outside_current_const[i]] ) :
                    print("Mismatch c/d: (internal structure)")
                    self.print_discbracket(sys.stdout)
                    print()
            else :

                cats = [ c.full_label[FPOS] for c in self.children ]
                nonterminals = [ c.label for c in self.children ]
                print(self.label, cats)
                print(self.label, nonterminals)
                self.print_discbracket(sys.stdout)
                print()

                idx = find_head(self.label, nonterminals, headrules)
                if idx != -1 :
                    self.children[idx].is_head = True

                    self.head = self.children[idx].head
                    self.full_label = self.children[idx].full_label
                    if not all( [h == self.children[idx].head for i,h in enumerate(heads) if not heads_outside_current_const[i]] ) :
                        print("Mismatch c/d: (internal structure)")
                        self.print_discbracket(sys.stdout)
                        print()
                else :
                    assert(False)
        else :
            self.head = self.children[0].head
            self.full_label = self.children[0].full_label

    def get_head(self) :
        """get head idx in sentence"""
        return int(self.full_label[HEAD]) - 1

    def print_discbracket(self, os):
        """Prints tree in discbracket format on os"""
        if self.is_leaf() :
            os.write("{}={}".format(self.left_index, replace_brackets(self.label)))
        else :
            os.write("({}".format(self.label))
            for c in self.children :
                os.write(" ")
                c.print_discbracket(os)
            os.write(")")

    def get_frontier(self, lst) :
        """
        Update recursively lst to contain a list of all (unordered)
        terminals in the tree
        """
        if self.is_leaf() :
            lst.append(self.full_label)
        for c in self.children :
            c.get_frontier(lst)

    def get_list_of_terminals(self, lst) :
        if self.is_leaf() :
            lst.append(self.label)
        for c in self.children :
            c.get_list_of_terminals(lst)

    def print_conll(self, os) :
        """Prints tree in conll format on os"""
        frontier = []
        self.get_frontier(frontier)
        frontier = sorted(frontier)
        for line in frontier :
            os.write("{}\n".format("\t".join(map(str, line))))

    def strip_functional_labels(self) :
        """
        Removes functional labels on non-terminals,
        stores them in self.functional_label

        Also: strip ## and @@
        """
        if not self.is_leaf() :
            f = self.label.split("-")
            self.label = f[0]
    
            if "##" in self.label :
                lab = self.label.split("##")
                print("Replaced {} by \t{}".format(self.label, lab))
                self.label = lab[0]

            if "@@" in self.label :
                lab = self.label.split("@@")
                print("Replaced {} by \t{}".format(self.label, lab))
                self.label = lab[0]

            if len(f) > 1 :
                assert(len(f) == 2)
                self.functional_label = f[1]
            for c in self.children :
                c.strip_functional_labels()

    def strip_spmrl_morphological_annotations(self):
        """Remove spmrl morphological annotations on preterminals (bracketed by ## and ##)"""
        if not self.is_leaf() :
            if "##" in self.label :
                assert(self.is_preterminal())
            f = self.label.split("##")
            self.label = f[0]

            for c in self.children :
                c.strip_spmrl_morphological_annotations()

    def print_ctbk(self, os, mfields, offset=0) :
        """
        Prints tree in ctbk format.
        """
        if self.is_preterminal() :
            tok = get_ctbk_token(self.label, self.children[0].full_label, mfields)
            
            # token mismatch between c-corpus and d-corpus -> harmonize tokens and log modiications
            if tok[FORM] != self.children[0].label :
                if tok[FORM] not in {"(", ")", "[", "]", "-LRB-", "-RRB-", "-LSB-", "-RSB-"} :
                    sys.stderr.write("{} {}\n".format(tok[FORM], self.children[0].label))
                assert(tok[FORM] in {"(", ")", "[", "]", "-LRB-", "-RRB-", "-LSB-", "-RSB-"})
                
            if self.label != self.children[0].full_label[FPOS] :
                print("Warning: d/c do not agree about this POS tag, replacing {} by {} ({})".format(self.children[0].full_label[FPOS], self.label, self.children[0].full_label[FORM]))
            os.write(SPACE * offset)
            if self.is_head :
                tok[0] += "^head"
            os.write("{}\n".format("\t".join(tok)))
        else :
            os.write(SPACE * offset)
            if self.is_head :
                os.write("<{}^head>\n".format(self.label))  # ^ instead of - (reserved for functional labels)
            else :
                os.write("<{}>\n".format(self.label))
            for c in self.children :
                c.print_ctbk(os, mfields, offset + 1)
            os.write(SPACE * offset)
            os.write("</{}>\n".format(self.label))


    def equal_modulo_functional_paths(self, t2) :
        if self.label.split("::")[0] != t2.label.split("::")[0] :
            return False
        if len(self.children) != len(t2.children) :
            return False
        for i,c in enumerate(self.children) :
            if not c.equal_modulo_functional_paths(t2.children[i]) :
                return False
        return True

    def replace_tag(self, old, new) :
        if self.is_preterminal() :
            self.label = self.label.replace(old, new)
        else :
            for c in self.children :
                c.replace_tag(old, new)




def read_conll(filename) :
    """Reads and returns a conll corpus"""
    sents = []
    with open(filename) as instream :
        sents = instream.read().strip().split("\n\n")
        sents = [[l.split("\t") for l in sent.split("\n") if l[0] != "#"] for sent in sents]
        for s in sents:
            for l in s :
                l[0] = int(l[0])
    return sents


if __name__=="__main__":
    import sys
    import argparse

    usage = """
    Treebank format conversion script
    
    Input: .conll + .discbracket aligned treebank
    Output: .ctbk file (discontinuous constituent trees, head annotation + morphological annotation)
    
    Head annotation uses:
        - conll corpus
        - headrules
    
    Procedure:
        use dep corpus to annotate constituents
        use headrules in case of failure / mismtach
    """

    parser = argparse.ArgumentParser(description = usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("conll", type = str, help="corpus .conll")
    parser.add_argument("discbracket", type = str, help="corpus .discbracket")
    parser.add_argument("output", type = str, help="Output")
    parser.add_argument("--headrules", "-r", type=str, default="french.headrules", help="Head rules (default=french.headrules)")
    parser.add_argument("--language", "-l", type=str, default="french", help="language (default=frenc)")

    args = parser.parse_args()
    conllc = args.conll
    dbrackc = args.discbracket
    output = args.output

    ctrees = [nTree.fromstring(line.strip()) for line in open(dbrackc)]
    dtrees = read_conll(conllc)

    ftrees = [Tree(t) for t in ctrees]

    print("N ctrees ", len(ctrees))
    print("N dtrees ", len(dtrees))

    headrules = get_headrules(args.headrules)

    for i,t in enumerate(ftrees) :
        t.strip_functional_labels()
        if args.language == "german" :
            t.replace_tag("$[", "$LRB")
        t.assign_full_label(dtrees[i])
        t.assign_heads(headrules)

    out = open(output, "w")
    out.write("{}\n".format("\t".join(["word", "tag"] + MORPH_FIELDS[args.language] + ["gdeprel"])))
    for i,t in enumerate(ftrees) :
        t.print_ctbk(out, MORPH_FIELDS[args.language])
        if i != len(ftrees) -  1 :
            out.write("\n")
