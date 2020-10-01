from pymed import PubMed
import csv 
import pandas as pd

pubmed = PubMed(tool="PubMedSearcher", email="giulia@genomeup.com")

def return_text(df):
    text = ""
    for index_article in range(0, len(df)):
        #text += str(df['abstract'][index_article])
        if str(df['abstract'][index_article]) == 'nan':
            pass
        else:
            text += str(df['abstract'][index_article])
    return text


def search_pubmed(search_term, name_save, max_results):
    results = pubmed.query(search_term, max_results)
    print(results)
    articleList = []
    articleInfo = []

    for article in results:
    # Print the type of object we've found (can be either PubMedBookArticle or PubMedArticle).
    # We need to convert it to dictionary with available function
        articleDict = article.toDict()
        articleList.append(articleDict)

    # Generate list of dict records which will hold all article details that could be fetch from PUBMED API
    for article in articleList:
    #Sometimes article['pubmed_id'] contains list separated with comma - take first pubmedId in that list - thats article pubmedId
        pubmedId = article['pubmed_id'].partition('\n')[0]
        # Append article info to dictionary         
        #keyslist = ['pubmed_id', 'title', 'abstract', 'doi', 'authors']
        #for key in article.keys():
        #    if key in keyslist:    
        try:    
            articleInfo.append({u'pubmed_id':pubmedId,
                                u'title':article['title'],
                                #u'keywords':article['keywords'],
                                #u'journal':article['journal'],
                                u'abstract':article['abstract'],
                                #u'conclusions':article['conclusions'],
                                #u'methods':article['methods'],
                                #u'results': article['results'],
                                #u'copyrights':article['copyrights'],
                                u'doi':article['doi'],
                                #u'publication_date':article['publication_date'], 
                                u'authors':article['authors']})
        except: 
            pass

        
        
    # Generate Pandas DataFrame from list of dictionaries
    articlesPD = pd.DataFrame.from_dict(articleInfo)
    articlesPD.to_csv(name_save, index = None, header=True) 
    print(articlesPD.head())
    return articlesPD


def main():
    search_pubmed('alkaptonuria mutations', 'disease_results.csv', 3)
    #search_pubmed('TRIM25', 'gene_results.csv', 10)
    #search_pubmed('bifidobacterium', 'bacteria_results.csv', 10)

if __name__ == "__main__":
    main()

