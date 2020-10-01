import streamlit as st
import spacy
from spacy import displacy
import pandas as pd
import reqpubmed
from nltk.tokenize import sent_tokenize
from termcolor import colored
from scispacy.linking import EntityLinker
#from scispacy.umls_linking import UmlsEntityLinker
from scispacy.abbreviation import AbbreviationDetector
from taxadb.taxid import TaxID
from taxadb.names import SciName

def taxon_existence(entity):
    taxid = names.taxid(entity)
    return taxid

@st.cache(allow_output_mutation=True)
def process_text(model_name, text):
    nlp = load_model(model_name)
    return nlp(text)

@st.cache(allow_output_mutation=True)
def load_linker_ner():
    #linker = UmlsEntityLinker(resolve_abbreviations=True)
    linker = EntityLinker(resolve_abbreviations= False, name="mesh")
    return linker

@st.cache(allow_output_mutation=True)
def load_model(name):
    nlp = spacy.load(name)
    # Add abbreviation detector
    abbreviation_pipe = AbbreviationDetector(nlp)
    nlp.add_pipe(abbreviation_pipe)
    return nlp

def return_bacterias(text, model, linker_ner):
    doc = process_text(model, text)
    bacterias = []
    for ent in linker_ner(doc).ents:
        #for ent_id, score in ent._.kb_ents:
            #kb_entity = linker_ner.kb.cui_to_entity[ent_id]
            #tuis = ",".join(kb_entity.types)
        entity = ent.text
        names = SciName(dbtype='sqlite', dbname='taxadb.sqlite')
        taxid = names.taxid(entity)
        if taxid != None:
            bacterias.append(ent.text)
    return bacterias     

spacy_model = "en_core_sci_lg"
nlp = load_model(spacy_model)

linker_ner = load_linker_ner()

text = "An increase in beneficial bacteria (Bifidobacteriales and B. longum) \
and suppression of suspected pathogenic bacteria (Clostridium) emerged after probiotics + FOS intervention, \
with significant reduction in the severity of autism and gastrointestinal symptoms."


bacterias = return_bacterias(text, spacy_model, linker_ner)
print(bacterias)