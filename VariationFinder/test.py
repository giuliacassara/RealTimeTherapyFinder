import os
import subprocess
import sys

doi = "10336378"

text = """Structural basis for the activity of two muconate cycloisomerase variants toward substituted muconates. We have refined to 2.3 A resolution two muconate cycloisomerase (MCIase) variant structures, F329I and I54V, that differ from each other and from wild-type in their activity  toward cis,cis-muconate (CCM) and substituted CCMs. The working and free R-factors for F329I are 17.4/21.6% and for I54V, 17.6/22.3% with good stereochemistry. Except for the mutated residue, there are no significant changes in structure.  To understand the differences in enzymatic properties we docked substituted CCMs and CCM into the active sites of the variants and wild type. The extra space the mutations create appears to account for most of the enzymatic differences. The lack of other structural changes explains why, although structurally equivalent changes occur in chloromuconate cycloisomerase (CMCIase), the changes in themselves do not convert a MCIase into a dehalogenating CMCIase. Reanalysis of the CMCIase structure revealed only one general acid/base, K169. The structural implication is that, in 2-chloro-CCM conversion by CMCIase, the lactone ring of 5-chloromuconolactone rotates before dehalogenation to bring the acidic C4 proton next to K169. Therefore, K169 alone performs both required protonation and deprotonation steps, the first at C5 as in MCIase, and the second, after ring rotation, at C4. This distinguishes CMCIase from alpha/beta barrel isomerases and racemases, which use two different bases."""

text_file = open("./corpora/prova2.txt", "wt")

to_write = doi + "\t" + text
n = text_file.write(to_write)
text_file.close()

var_finder_out = subprocess.run(["/home/ubuntu/SciSpacy-Therapy/VariationFinder/variation_finder.py", "/home/ubuntu/SciSpacy-Therapy/VariationFinder/corpora/prova2.txt"])
print(var_finder_out)