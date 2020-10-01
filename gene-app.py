import streamlit as st
import os
import subprocess
import sys
import spacy
from spacy import displacy
import pandas as pd
import reqpubmed
from nltk.tokenize import sent_tokenize
from termcolor import colored
from scispacy.linking import EntityLinker
#from scispacy.umls_linking import UmlsEntityLinker
from scispacy.abbreviation import AbbreviationDetector


SPACY_MODEL_NAMES = ["en_core_sci_lg"]
NER_MODEL_NAMES = ["en_ner_bionlp13cg_md"]
DEFAULT_QUERY = "ACE2 mutations"
DEFAULT_NUMBER_ARTICLES = 10
DEFAULT_SAVE_PUBMED_ARTICLES = 'gene_results.csv'
DEFAULT_TEXT = "Spinal and bulbar muscular atrophy (SBMA) is an inherited motor neuron disease caused by the expansion of a polyglutamine tract within the androgen receptor (AR). SBMA can be caused by this easily."
HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""


@st.cache(allow_output_mutation=True)
def load_model(name):

    nlp = spacy.load(name)
    # Add abbreviation detector
    abbreviation_pipe = AbbreviationDetector(nlp)
    nlp.add_pipe(abbreviation_pipe)
    return nlp

@st.cache(allow_output_mutation=True)
def process_text(model_name, text):
    nlp = load_model(model_name)
    return nlp(text)

@st.cache(allow_output_mutation=True)
def load_linker_er():
    #linker = UmlsEntityLinker(resolve_abbreviations=True)
    linker = EntityLinker(resolve_abbreviations= False, name="hpo")
    return linker

def load_linker_ner():
    #linker = UmlsEntityLinker(resolve_abbreviations=True)
    linker = EntityLinker(resolve_abbreviations= False, name="umls")
    return linker

def search_term_in_text(term, sentence):
    return [sentence + '.' for sentence in term.split('.') if term in sentence]
    

def search_term_in_text(term, sentence):
    splitted = sentence.split(',')
    positions = []
    for index in range(0, len(splitted)):
        if term in splitted[index]:
            positions.append(splitted[index])
    return positions
    

def return_tokenized_doc(text):
    tokens = sent_tokenize(text)
    return tokens


def return_sentence_hightlight(tokens, searchterm):
    sentences = ""
    for t in tokens:
        if searchterm in t:
            sentence = t 
            sentences += sentence
            sentences += '\n'
    return sentences



def render(df, index_article):
    #use index article to retrieve document information

    #df1 = df.iloc[index_article , [0, 1, 3, 9, 10] ]
    df1 = df.iloc[index_article , [0, 1, 2, 3, 4] ]
    pmid = str(df['pubmed_id'][index_article])
    text = str(df['abstract'][index_article])
    df1 = df1.to_frame().reset_index()
    dfStyler = df1.style.set_properties(**{'text-align': 'left'})
    #df1 = df[['pubmed_id', 'title', 'journal','doi']]
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])

    doc = process_text(spacy_model, text)
    st.markdown("Best match of your query from PUBMED.")
    #st.table(dfStyler)
    #st.write(text)
    st.header("Symptoms/Phenotypes")

    #tokenize abstract into sentences 
    tokens = sent_tokenize(text)
    #html = displacy.render(ner_doc, style="ent") 

    data = []
    for ent in linker_er(doc).ents:
        for ent_id, score in ent._.kb_ents:
            kb_entity = linker_er.kb.cui_to_entity[ent_id]
            tuis = ",".join(kb_entity.types)
            searchterm = ent.text
            sentences = return_sentence_hightlight(tokens, searchterm)
            data.append([
                ent.text,
                kb_entity.definition,
                sentences

            ])
            if show_only_top:
                break

    attrs = ["text", "Definition", "Sentence matching"]
    df = pd.DataFrame(data, columns=attrs)
    df = df.drop_duplicates()
    dfStyler = df.style.set_properties(**{'text-align': 'left'})
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    st.table(dfStyler)
    st.write(text)

    st.header("Variants/Mutations")

    # write PMID, tab separated with text then read with variation_finder.py

    text_file = open("./VariationFinder/corpora/prova2.txt", 'wt')

    to_write = pmid + "\t" + text.replace('\n','') + '\n'
    n = text_file.write(to_write)
    text_file.close()

    var_finder_out = subprocess.run(['/home/ubuntu/SciSpacy-Therapy/VariationFinder/variation_finder.py', '/home/ubuntu/SciSpacy-Therapy/VariationFinder/corpora/prova2.txt', '-r',  '/home/ubuntu/SciSpacy-Therapy/VariationFinder/regex.txt'])
    #read the first line and output from file prova2.txt.mf
    filepath = 'prova2.txt.mf'
    with open(filepath) as fp:
        #for cnt, line in enumerate(fp):
            #print("Line {}: {}".format(cnt, line))
            #st.write("Line {}: {}".format(cnt, line))
        for l in fp:
            line = l.strip().split("\t")
    data = []
    mutations = line[1:]
    for mut in mutations:
        mut = mut.strip()
        searchterm = mut
        sentences = return_sentence_hightlight(tokens, searchterm)
        data.append([
            mut,
            sentences

        ])

    attrs = ["text", "Sentence matching"]
    df = pd.DataFrame(data, columns=attrs)
    df = df.drop_duplicates()
    dfStyler = df.style.set_properties(**{'text-align': 'left'})
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    st.table(dfStyler)
##########################################################################################################

st.title("Scispacy - Demo")
st.image("https://www.genomeup.com/wp-content/uploads/2018/04/logo_TM.png")

st.sidebar.markdown(
    """
Analyze text with [ScispaCy](https://allenai.github.io/scispacy/) models and visualize entity linking, named entities,
dependencies and more.
"""
)

spacy_model = st.sidebar.selectbox("Model name", SPACY_MODEL_NAMES)
model_load_state = st.info(f"Loading model '{spacy_model}'...")
nlp = load_model(spacy_model)
model_load_state.empty()

linker_er = load_linker_er()
#linker_ner = load_linker_ner()

st.sidebar.header("Entity Linking")
threshold = st.sidebar.slider("Mention Threshold", 0.0, 1.0, 0.80)
linker_er.threshold = threshold
show_only_top = st.sidebar.checkbox("Show only top entity per mention", value=True)

try: os.remove("prova2.txt.mf")
except: pass
st.header("Enter a query term:")
query = st.text_area("", DEFAULT_QUERY)
df = reqpubmed.search_pubmed(query, DEFAULT_SAVE_PUBMED_ARTICLES, DEFAULT_NUMBER_ARTICLES)
#text = reqpubmed.return_text(df)

for index in range(0, DEFAULT_NUMBER_ARTICLES):
    render(df, index)

