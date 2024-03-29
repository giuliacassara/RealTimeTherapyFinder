import streamlit as st
import spacy
from spacy import displacy
import pandas as pd
import reqpubmed

from scispacy.umls_linking import UmlsEntityLinker
from scispacy.abbreviation import AbbreviationDetector

SPACY_MODEL_NAMES = ["en_core_sci_lg"]
NER_MODEL_NAMES = ["en_ner_bc5cdr_md"]
DEFAULT_QUERY = "alkaptonuria treatment"
DEFAULT_NUMBER_ARTICLES = 3
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
def load_linker():
    linker = UmlsEntityLinker(resolve_abbreviations=True)

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
    


def render(df, index_article):
    #use index article to retrieve document information
    df1 = df.iloc[index_article , [0, 1, 3, 9, 10] ]
    text = str(df['abstract'][index_article])
    df1 = df1.to_frame().reset_index()
    dfStyler = df1.style.set_properties(**{'text-align': 'left'})
    #df1 = df[['pubmed_id', 'title', 'journal','doi']]
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    
    st.markdown("Best match of your query from PUBMED.")
    st.table(dfStyler)
    st.write(text)
    
    ner_doc = process_text(ner_model, text)
    
     
    st.header("Specialized NER")
     
    #html = displacy.render(ner_doc, style="ent") 
    data = []

    for ent in linker(ner_doc).ents:
        for ent_id, score in ent._.umls_ents:
            kb_entity = linker.umls.cui_to_entity[ent_id]
            #--------------------------------------------#
            if(ent.label_ == 'CHEMICAL'):
                #reference = search_term_in_text(ent.text, text)
                data.append([
                    ent.text,
                    ent.label_,
                    kb_entity.canonical_name,
                    kb_entity.definition
                ])
    
            if show_only_top:
                break
    
    attrs = ["text", "label_", "Canonical Name", "Definition"]
    df = pd.DataFrame(data, columns=attrs)
    df = df.drop_duplicates()
    #st.dataframe(df)
    dfStyler = df.style.set_properties(**{'text-align': 'left'})
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    
    st.markdown("NER labeled entities are linked to the Unified Medical Language System (UMLS).")
    st.table(dfStyler)



def main():
    # Register your pages
    pages = {
        "First page": page_first,
        "Second page": page_second,
    }

    st.sidebar.title("App with pages")

    # Widget to select your page, you can choose between radio buttons or a selectbox
    page = st.sidebar.radio("Select your page", tuple(pages.keys()))
    #page = st.sidebar.selectbox("Select your page", tuple(pages.keys()))

    # Display the selected page
    pages[page]()

def page_first():
    st.title("Scispacy - Demo")
    st.image("https://www.genomeup.com/wp-content/uploads/2018/04/logo_TM.png")

    st.sidebar.markdown(
        """
    Analyze text with [ScispaCy](https://allenai.github.io/scispacy/) models and visualize entity linking, named entities,
    dependencies and more.
    """
    )

    linker = load_linker()

    st.sidebar.header("Entity Linking")
    threshold = st.sidebar.slider("Mention Threshold", 0.0, 1.0, 0.85)
    linker.threshold = threshold
    show_only_top = st.sidebar.checkbox("Show only top entity per mention", value=True)

    st.sidebar.header("Specialized NER")
    ner_model = st.sidebar.selectbox("NER Model", NER_MODEL_NAMES)
    ner_load_state = st.info(f"Loading NER Model '{ner_model}'...")
    ner = load_model(ner_model)
    ner_load_state.empty()


    st.header("Enter a query term:")
    query = st.text_area("", DEFAULT_QUERY)
    df = reqpubmed.search_pubmed(query, DEFAULT_SAVE_PUBMED_ARTICLES, DEFAULT_NUMBER_ARTICLES)
    #text = reqpubmed.return_text(df)

for index in range(0, DEFAULT_NUMBER_ARTICLES):
    render(df, index)
    # ...

def page_second():
    st.title("This is my second page")
    # ...

if __name__ == "__main__":
        main()
