from taxadb.taxid import TaxID
from taxadb.names import SciName

taxonomy = []
taxid = TaxID(dbtype='sqlite', dbname='taxadb.sqlite')
entity = "Physisporinus cinereus"
names = SciName(dbtype='sqlite', dbname='taxadb.sqlite')
tx = names.taxid(entity)
if tx != None:
    print(tx)
    lineage = taxid.lineage_name(tx)
    print("Bacteria name", lineage[0])
    print("Phylum level ", lineage[4])
    name = lineage[0] + " , " + lineage[4]
    taxonomy.append(name)
    print(taxonomy)
