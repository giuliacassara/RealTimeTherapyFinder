import streamlit as st
import spacy
import scispacy
from spacy import displacy
import pandas as pd
import reqpubmed
from nltk.tokenize import sent_tokenize
from termcolor import colored
import json
import os

#from scispacy.umls_linking import UmlsEntityLinker
from scispacy.linking import EntityLinker
from scispacy.abbreviation import AbbreviationDetector


SPACY_MODEL_NAMES = ["en_core_sci_lg"]
NER_MODEL_NAMES = ["en_ner_bc5cdr_md"]

FILEJSON = "disease.json"

DEFAULT_QUERY = "alkaptonuria treatment"
DEFAULT_NUMBER_ARTICLES = 10
DEFAULT_SAVE_PUBMED_ARTICLES = 'disease_results.csv'
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
def load_linker(kb_name):
    #linker = UmlsEntityLinker(resolve_abbreviations=True)
    linker = EntityLinker(resolve_abbreviations= False, name= kb_name)
    return linker


def return_text(df):
    text = ""
    for index_article in range(0, len(df)):
        #text += str(df['abstract'][index_article])
            text += str(df['abstract'][index_article])
    return text


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
    #df1 = df.iloc[index_article , [0, 1, 2, 3, 4] ]
    df1 = df.iloc[index_article , [0, 1, 3]]

    text = str(df['abstract'][index_article])

    #info_paper = df1.to_string()
    info_paper = str(df1.to_dict())

    df1 = df1.to_frame().reset_index()
    dfStyler = df1.style.set_properties(**{'text-align': 'left'})
    #df1 = df[['pubmed_id', 'title', 'journal','doi']]
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])

    doc = process_text(spacy_model, text)
    st.markdown("Best match of your query from PUBMED.")
    #st.table(dfStyler)
    st.write(text)
    st.header("Symptoms/Phenotypes")
    st.markdown("Mentions are detected with the standard pipeline's mention detector.")

    tokens = sent_tokenize(text)

    #html = displacy.render(doc, style="ent")
    # Newlines seem to mess with the rendering
    #html = html.replace("\n", " ")
    #st.write(HTML_WRAPPER.format(html), unsafe_allow_html=True)

    data = []
    for ent in linker1(doc).ents:
        for ent_id, score in ent._.kb_ents:
            searchterm = ent.text
            sentences = return_sentence_hightlight(tokens, searchterm)
            kb_entity = linker1.kb.cui_to_entity[ent_id]
            tuis = ",".join(kb_entity.types)
            data.append([
                ent.text,
                #kb_entity.canonical_name,
                #ent_id,
                sentences,
                info_paper
            ])

            if show_only_top:
                break

    attrs = ["text", "Sentence matching", "Paper"]

    #attrs = ["text", "Canonical Name", "Definition", "Concept ID"]
    df1 = pd.DataFrame(data, columns=attrs)
    df1 = df1.drop_duplicates()

    dfStyler = df1.style.set_properties(**{'text-align': 'left'})
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    st.table(dfStyler)
    
    st.header("Therapy/Chemicals")

    ner_doc = process_text(ner_model, text)

    #tokenize abstract into sentences 
    #html = displacy.render(ner_doc, style="ent") 
    data2 = []
    for ent in linker2(doc).ents:
        for ent_id, score in ent._.kb_ents:
            kb_entity = linker2.kb.cui_to_entity[ent_id]
            tuis = ",".join(kb_entity.types)
            searchterm = ent.text
            sentences = return_sentence_hightlight(tokens, searchterm)
            data2.append([
                ent.text,
                sentences,
                info_paper
            ])

            if show_only_top:
                break
    
    attrs = ["text", "Sentence matching", "Paper"]
    df2 = pd.DataFrame(data2, columns=attrs)
    df2 = df2.drop_duplicates()

    #append the two dataframes and convert them to json
    #st.dataframe(df)
    dfStyler = df2.style.set_properties(**{'text-align': 'left'})
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    
    st.table(dfStyler)

    frames = [df1, df2]
    result = pd.concat(frames, ignore_index=True)

    print(result)
    result = result.to_json(orient="index")
    
    with open(FILEJSON, 'a+') as json_file:
        json.dump(result, json_file)

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

linker1 = load_linker('hpo')
linker2 = load_linker('rxnorm')
#linker3 = load_linker('umls')

st.sidebar.header("Entity Linking")
threshold = st.sidebar.slider("Mention Threshold", 0.0, 1.0, 0.95)
linker1.threshold = threshold
show_only_top = st.sidebar.checkbox("Show only top entity per mention", value=True)


ner_model = st.sidebar.selectbox("NER Model", NER_MODEL_NAMES)
ner_load_state = st.info(f"Loading NER Model '{ner_model}'...")
ner = load_model(ner_model)
ner_load_state.empty()


st.header("Enter a query term:")
query = st.text_area("", DEFAULT_QUERY)
df = reqpubmed.search_pubmed(query, DEFAULT_SAVE_PUBMED_ARTICLES, DEFAULT_NUMBER_ARTICLES)
#text = reqpubmed.return_text(df)

try:
    os.remove(FILEJSON)
except OSError:
    pass

for index in range(0, DEFAULT_NUMBER_ARTICLES):
    render(df, index)



