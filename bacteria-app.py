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
from spacy.matcher import Matcher
import re
import sys
import json
import os

SPACY_MODEL_NAMES = ["en_core_sci_lg"]
FILEJSON = "bacteria.json"
DEFAULT_QUERY = "Clostridium Autism"
DEFAULT_TEXT = "insert your text here"
DEFAULT_NUMBER_ARTICLES = 10
DEFAULT_SAVE_PUBMED_ARTICLES = 'bacteria_results.csv'
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
    linker = EntityLinker(resolve_abbreviations= False, name="mesh")
    return linker

def load_linker_ner():
    #linker = UmlsEntityLinker(resolve_abbreviations=True)
    linker = EntityLinker(resolve_abbreviations= False, name="hpo")
    return linker

    
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


#return a vector of taxonomy of the bacteria name
def retrieve_taxonomy(bacteria_name):
    taxid = TaxID(dbtype='sqlite', dbname='taxadb.sqlite')
    entity = bacteria_name
    names = SciName(dbtype='sqlite', dbname='taxadb.sqlite')
    tx = names.taxid(entity)
    if tx != None:
        print(tx)
        lineage = taxid.lineage_name(tx)
    return lineage


def return_bacterias(bact_sentence, spacy_model, linker):
    doc2 = process_text(spacy_model, bact_sentence)
    bacterias = []
    for ent in linker(doc2).ents:
        entity = ent.text
        names = SciName(dbtype='sqlite', dbname='taxadb.sqlite')
        taxid = names.taxid(entity)
        if taxid != None:
            bacterias.append(entity)
    return bacterias   

def return_percentage_normal(tk):
    item = "normal"
    pattern = re.compile("\w+\s\(\d{1,2}.\d{1,}%\)")
    if item in tk:
        matches = re.findall(pattern, tk)
        return matches

def return_percentage(tokens):
    data_bacteria = []
    #item = "normal"
    diet_terms = ['high', 'higher', 'high level', 'higher level', 'abundant', 'abundance', 'normal']
    #pattern = re.compile("\w+\s\(\d{1,2}.\d{1,}%\)")
    pattern = re.compile("\w+.\d{1,}%")
    for tk in tokens:
        #if 'normal' in tk :
        #    matches = re.findall(pattern, tk)
            #print(matches)
        #    if matches:
        #        print(tk)
        #        data_bacteria.append([
        #                matches,
        #                tk
                        #bacterias
        #        ])
        for term in diet_terms:
            if term in tk:
                matches = re.findall(pattern, tk)
                if matches:
                    print(tk)

                    data_bacteria.append([
                            matches,
                            tk
                    ])
            
    return data_bacteria
        

def render(text, df, index_article):

    #use index article to retrieve document information

    df1 = df.iloc[index_article , [0, 1, 2, 3, 4] ]

    df1 = df1.to_frame().reset_index()
    dfStyler = df1.style.set_properties(**{'text-align': 'left'})
    
    info_paper = df1.to_string()

    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    
    st.markdown("Best match of your query from PUBMED.")
    #st.write(text)

    
    tokens = sent_tokenize(text)
    doc = process_text(spacy_model, text)

    terms_of_interest = ['increased', 'decreased', 'increase', 'decrease']
    bacteriodes = ['Bacteroidetes', 'Firmicutes']

    data = []
    data_bacteria = []
    taxonomy =[]

    for term in terms_of_interest:
        if term in text:
            searchterm = term
            sentences = return_sentence_hightlight(tokens, searchterm)
            bacterias = return_bacterias(sentences, spacy_model, linker)
            if bacterias:
                for bact in bacterias:
                    lineage = retrieve_taxonomy(bact)
                    try:
                        name_phylum = [lineage[0], lineage[4]]
                        if name_phylum not in taxonomy:                    
                            taxonomy.append(name_phylum)
                    except:
                        pass
                    #print(taxonomy)
                    
            data_bacteria.append([
                    term,
                    sentences, 
                    taxonomy
                    #bacterias
            ])
            print(data_bacteria)

    st.header("Phenotype/Symptoms")
    st.markdown("Mentions are detected with the standard pipeline's mention detector.")

    for ent in linker_ner(doc).ents:
        for ent_id, score in ent._.kb_ents:

            kb_entity = linker_ner.kb.cui_to_entity[ent_id]
            tuis = ",".join(kb_entity.types)
            searchterm = ent.text
            sentences = return_sentence_hightlight(tokens, searchterm)
            
            data.append([
                ent.text,
                #kb_entity.canonical_name,
                #ent_id
                kb_entity.definition, 
                sentences
            ])

            # if ent.text in terms_of_interest:
            #     bacterias = return_bacterias(sentences, spacy_model, linker)
            #     data_bacteria.append([
            #         ent.text,
            #         sentences, 
            #         bacterias
            # ])

            if show_only_top:
                break

    #attrs = ["text", "Definition"]
    attrs = ["text", "Definition", "Sentence matching"]

    #attrs = ["text", "Canonical Name", "Definition", "Concept ID"]
    df = pd.DataFrame(data, columns=attrs)
    df = df.drop_duplicates()
    dfStyler = df.style.set_properties(**{'text-align': 'left'})
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    st.table(dfStyler)

#############################################################################################

    st.header("Bacteria information")

    #attrs = ["text", "Definition"]
    attrs2 = ["text", "Sentence matching", "Taxonomy"]

    #attrs = ["text", "Canonical Name", "Definition", "Concept ID"]
    df = pd.DataFrame(data_bacteria, columns=attrs2)
    df.head()
    df2 = df.drop_duplicates(subset=['text'])
    df2.head()
    #df2 = df2.drop_duplicates()

    #print(data_bacteria)

    dfStyler = df2.style.set_properties(**{'text-align': 'left'})
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    st.table(dfStyler)

    

##########################################################################################################


#############################################################################################

    st.header("Diet and percentage information")
    other_infos = return_percentage(tokens)
    #attrs = ["text", "Definition"]
    attrs3 = ["match", "sentence"]

    #attrs = ["text", "Canonical Name", "Definition", "Concept ID"]
    df = pd.DataFrame(other_infos, columns=attrs3)
    #df3 = df.drop_duplicates(subset=['text'])

    #print(data_bacteria)

    dfStyler = df.style.set_properties(**{'text-align': 'left'})
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    st.table(dfStyler)

    

def return_information(tokens):
    data_bacteria = []
    #item = "normal"
    #diet_terms = ['high', 'higher', 'high level', 'higher level', 'abundant', 'abundance', 'normal']
    diet_terms = ['high', 'higher', 'high level', 'higher level', 'abundant', 'abundance', 'normal', 'increased', 'decreased', 'increase', 'decrease']

    #pattern = re.compile("\w+\s\(\d{1,2}.\d{1,}%\)")
    pattern = re.compile("\w+.\d{1,}%")
    for tk in tokens:
        terms =[]
        matches = re.findall(pattern, tk)
        if(matches):
            for term in diet_terms:
                if term in tk:
                    terms.append(term)
            data_bacteria.append([
                matches,
                terms,
                tk
            ])    
        else:
            taxonomy = []
            bacterias = return_bacterias(tk, spacy_model, linker)
            bacterias = list(dict.fromkeys(bacterias))
            print(bacterias)
            for bact in bacterias:
                lineage = retrieve_taxonomy(bact)
                                #try:
                                #    name_phylum = [lineage[0], lineage[4]]
                                #    if name_phylum not in taxonomy:               
                                    #except:
                                    #    pass
                                        
                data_bacteria.append([
                    bact,
                    lineage, 
                    tk
                                        #bacterias
                ])
            
    return data_bacteria

##########################################################################################################

def render_less(text, info):
    #use index article to retrieve document information
    st.write(text)
    
    tokens = sent_tokenize(text)
    doc = process_text(spacy_model, text)

    data_bacteria = []

    st.header("Bacteria information - Taxonomy, Diet and abundance")
    other_infos = return_information(tokens)
    #attrs = ["text", "Definition"]
    attrs3 = ["Percentage/Bacteria", "Term/Taxonomy", "Sentence"]
    df3 = pd.DataFrame(other_infos, columns=attrs3)
    #df3 = df.drop_duplicates(subset=['text'])
    df3["Paper"] = info
    #print(data_bacteria)

    dfStyler = df3.style.set_properties(**{'text-align': 'left'})
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    st.table(dfStyler)

    result = df3.to_json(orient="index")
    
    with open(FILEJSON, 'a+') as json_file:
        json.dump(result, json_file)


##########################################################################################################

if __name__ == "__main__":

    st.title("Bacteria - Demo")
    st.image("https://www.genomeup.com/wp-content/uploads/2018/04/logo_TM.png")

    st.sidebar.markdown(
        """
    Analyze text with [ScispaCy](https://allenai.github.io/scispacy/) to find Bacteria information
    """
    )

    spacy_model = st.sidebar.selectbox("Model name", SPACY_MODEL_NAMES)
    model_load_state = st.info(f"Loading model '{spacy_model}'...")
    nlp = load_model(spacy_model)
    model_load_state.empty()

    linker = load_linker_er()
    linker_ner = load_linker_ner()

    try:
        os.remove(FILEJSON)
    except OSError:
        pass

    st.sidebar.header("Entity Linking")
    threshold = st.sidebar.slider("Mention Threshold", 0.0, 1.0, 0.95)
    linker_ner.threshold = threshold
    linker.threshold = threshold

    show_only_top = st.sidebar.checkbox("Show only top entity per mention", value=True)

    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))

    if len(sys.argv) < 2:
        st.header("Enter a query term:")
        query = st.text_area("", DEFAULT_QUERY)
        df = reqpubmed.search_pubmed(query, DEFAULT_SAVE_PUBMED_ARTICLES, DEFAULT_NUMBER_ARTICLES)

        for index in range(0, DEFAULT_NUMBER_ARTICLES):   
            try:
                text = str(df['abstract'][index])
                df1 = df.iloc[index , [0, 1, 3]]
                #info_paper = df1.to_string()
                info_paper = str(df1.to_dict())
                if text != 'nan':
                    #render(text, df, index)
                    render_less(text, info_paper)
                    #render(query)
            except:
                pass

    else:
        st.header("Enter a text to extract information")
        text = st.text_area("", DEFAULT_TEXT)
        st.write(text)



