import spacy
import scispacy
from scispacy.linking import EntityLinker
import en_core_sci_lg
from spacy.matcher import Matcher



def display_bacteria_info(text, nlp):
    nlp = spacy.load("en_core_sci_lg")
    matcher = Matcher(nlp.vocab)
    matched_sents = []  # Collect data of matched sentences to be visualized
    print(text)
    pattern = [{"LEMMA": "composition"},{"POS": "ADV", "OP": "*"},{"LOWER": "Microbiota"}, {"LOWER": "Microbiome"}]
    matcher.add("Composition", collect_sents, pattern)  # add pattern
    doc = nlp("The composition and abundance of the fecal microbiota of different experimental groups are shown in Figure 5C,D. On the phylum level, \
    Bacteroidetes and Firmicutes were the two dominant taxa in all groups (Figure 5C). \
    In the mice fed a normal diet, the most numerous were Bacteroidetes (65.6%), followed by Firmicutes (32.3%).\
    However, in the mice fed a high-fat diet, Firmicutes was more abundant (70.4%) than Bacteroidetes (21.7%). \
    The ratios of Firmicutes/Bacteroidetes differed between the mice fed a normal diet (0.49) and those fed a high-fat diet (3.24). \
    Moreover, in mice fed a high-fat diet, the proportion of the microbiota from the phylum Proteobacteria (7.4%) increased, which differed from that of the mice fed a normal diet (1.7%).\
    Dietary supplementation with low-dose LGG and high-dose LGG in the high-fat diet decreased the microbial proportion from the phylum Proteobacteria to 0.08% and 0.10%, respectively. \
    In addition, supplementation with low-dose LGG in the high-fat diet decreased the proportion of Bacteroidetes to 14.3% and increased the proportion of Firmicutes to 84.3%. \
    In contrast, supplementation with high-dose LGG increased the proportion of Bacteroidetes to 25.0% and increased the proportion of Firmicutes to 74.1%. The ratios of Firmicute"")
    matches = matcher(doc)

    # Serve visualization of sentences containing match with displaCy
    # set manual=True to make displaCy render straight from a dictionary
    # (if you're not running the code within a Jupyer environment, you can
    # use displacy.serve instead)
    displacy.render(matched_sents, style="ent", manual=True)


def collect_sents(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    span = doc[start:end]  # Matched span
    sent = span.sent  # Sentence containing matched span
    # Append mock entity for match in displaCy style to matched_sents
    # get the match span by ofsetting the start and end of the span with the
    # start and end of the sentence in the doc
    match_ents = [{
        "start": span.start_char - sent.start_char,
        "end": span.end_char - sent.start_char,
        "label": "MATCH",
    }]
    matched_sents.append({"text": sent.text, "ents": match_ents})


