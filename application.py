import os
import datetime
import nltk
import pandas as pd
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

# SEO On Page

def clean_keyword(inkeyword):
    glyphs = '[]|<>*'
    for char in glyphs:
        inkeyword = inkeyword.replace(char, "")
    outkeyword = inkeyword.strip()
    return outkeyword

# Score algorithm 

def make_SEO_dict(textcorpus):
    SEO_dict = {
        "title" : '',
        "heading1": '',
        "description" : "",
        "filename": "",
        "bodytitle" : "",
        "intro" : "",
        "imgtext": "",
        "imgfilename": ""
    }
    introstate = 0
    textcorpus = textcorpus.replace("### ", "(H3) ")
    textcorpus = textcorpus.replace("## ", "(H2) ")
    textlines = textcorpus.split("\n")
    SEO_dict["filename"] = "" # Filename is not scored via the form interface
    for l in textlines:
        if l.find("title:") > -1:
            SEO_dict['title'] = l[l.find("title:")+6:].strip()
        elif l.find("description:") > -1:
            SEO_dict['description'] = l[l.find("description:")+12:].strip()
        elif l.find("![") > -1:
             rawalttext = l[l.find("![")+2:l.find("]")].strip() + " "
             SEO_dict['imgtext'] += rawalttext
             imagepath = l[l.find("](")+2:l.find(")")].replace("-", " ").strip() + " "
             slashes = imagepath.split("/")
             rawfilenameext = slashes[len(slashes)-1]
             rawfilename = rawfilenameext[:rawfilenameext.find(".")] + " "
             SEO_dict['imgfilename'] += rawfilename
        elif l.find("# ") > -1:
            if SEO_dict["heading1"] == "": 
                SEO_dict['heading1'] += l[l.find("# ")+1:].strip()
                introstate = 1
        elif l.find("(H2)") > -1:
            SEO_dict['bodytitle'] += l[l.find("## ")+5:].strip() + " "
        elif l.find("(H3)") > -1:
            SEO_dict['bodytitle'] += l[l.find("## ")+5:].strip() + " "
        elif introstate > 0:
            SEO_dict['intro'] += l + " "
            introstate += 1
            if introstate > 4:
                introstate = 0
    return SEO_dict


def score_SEO(SEO_dict, instring):
    score = 0

    if SEO_dict["title"].find(instring) > -1:
        score += 5
    if SEO_dict["heading1"].find(instring)  > -1:
        score += 5
    if SEO_dict["description"].find(instring) > -1: 
        score += 5
    if SEO_dict["filename"].find(instring)  > -1:
        score += 5
    if SEO_dict["bodytitle"].find(instring)  > -1:
        score += 3
    if SEO_dict["intro"].find(instring)  > -1:
        score += 3
    if SEO_dict["imgtext"].find(instring) > -1:
        score += 2
    if SEO_dict["imgfilename"].find(instring) > -1:
        score += 2

    return score

# Parser Functions using NLTK

def extract_chunks(sent):
    '''With a parsed sentence, return sets of entities.'''
    grammar = r"""
    NBAR:
        # Nouns and Adjectives, terminated with Nouns
        {<NN.*>*<NN.*>}

    NP:
        {<NBAR>}
        # Above, connected with in/of/etc...
        {<NBAR><IN><NBAR>}
    """
    chunker = nltk.RegexpParser(grammar)
    ne = set()
    chunk = chunker.parse(nltk.pos_tag(nltk.word_tokenize(sent)))
    for tree in chunk.subtrees(filter=lambda t: t.label() == 'NP'):
        ne.add(' '.join([child[0] for child in tree.leaves()]))
    return ne


def parse_sentences(incorpus):
    '''Take a body text and return sentences in a list.'''
    sentences = nltk.sent_tokenize(incorpus)
    return sentences


def only_word_pairs(inlist):
    '''Takes an list with strings and removes single items.'''
    outlist = []
    for i in inlist:
        j = i.split()
        if len(j) > 1:
            outlist.append(i)
    return outlist

def remove_blank(inlist):
    '''Iterate over the list to remove blank entries.'''
    noblank = []
    for i in inlist:
        x = i.strip()
        if x:
            noblank.append(x)
    return noblank

def extract_entities(bodytext):
    '''Take a multisentence text and return a list of unique entities.'''
    breakdown = parse_sentences(bodytext)
    entities = []
    for sent in breakdown:
        for i in extract_chunks(sent):
            entities.append(i)
    pairplus_entities = only_word_pairs(entities)
    clean_entities = []
    for e in pairplus_entities:
        clean_entities.append(clean_keyword(e))
    remove_dups = set(clean_entities)
    preentities = list(remove_dups)
    entities = remove_blank(preentities)
    return entities


def get_top_ten(bodytext):
    '''With a path name to a markdown file return the top 10 SEO ranked keywords in the file as a dictionary.'''
    try:
        seo_dict = make_SEO_dict(bodytext)
        record_terms = extract_entities(bodytext)
        pagedata = {"SEO score" : [], "Count" : [], "Keyword" : []}
        for term in record_terms:
            pagedata["SEO score"].append(score_SEO(seo_dict, term))
            pagedata["Count"].append(bodytext.count(term))
            pagedata["Keyword"].append(term)
        SEO_df_full = pd.DataFrame(pagedata).sort_values(by=["SEO score", "Count"], ascending=False).reset_index()
        SEO_summary = SEO_df_full.loc[0:9].to_dict()
        SEO_out = {}
        count = 0
        for i in SEO_summary['index']:
            count += 1
            record = {}
            record['score rank'] = i + 1
            record['keyword'] = SEO_summary['Keyword'][i]
            SEO_out[count] = record
    except Exception as e:
        SEO_out = {1: {"error": "Unable to process file.", "message": str(e)}}
    return SEO_out


def devrel_function(path_in):
    '''Takes a filepath and returns data in a dictionary.'''
    try:
        message = {"message" : "success"}
    except Exception as e:
        message = {"message" : str(e) }
    return(message)


# Flask

@app.route('/')
def student():
   return render_template('onpage.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      seo_dict=get_top_ten(result['Markdown'])
      return render_template("result.html", result = seo_dict)

@app.route("/test")
def test():
   return "<h1>Test</h1>"

@app.route("/lang")
def lang():
    testex = '''
# App Service on Azure Stack update 1 release notes

*Applies to: Azure Stack integrated systems and Azure Stack Development Kit*

These release notes describe the improvements and fixes in Azure App Service on Azure Stack Update 1 and any known issues. Known issues are divided into issues directly related to the deployment, update process, and issues with the build (post-installation).

> [!IMPORTANT]
> Apply the 1802 update to your Azure Stack integrated system or deploy the latest Azure Stack development kit before deploying Azure App Service.
>
>

## Build reference

The App Service on Azure Stack Update 1 build number is **69.0.13698.9**

### Prerequisites

> [!IMPORTANT]
> New deployments of Azure App Service on Azure Stack now require a [three-subject wildcard certificate](azure-stack-app-service-before-you-get-started.md#get-certificates) due to improvements in the way in which SSO for Kudu is now handled in Azure App Service. The new subject is **\*.sso.appservice.\<region\>.\<domainname\>.\<extension\>**
>
>

Refer to the [Before You Get Started documentation](azure-stack-app-service-before-you-get-started.md) before beginning deployment.

### New features and fixes

Azure App Service on Azure Stack Update 1 includes the following improvements and fixes:

- **High Availability of Azure App Service** - The Azure Stack 1802 update enabled workloads to be deployed across fault domains. Therefore App Service infrastructure is able to be fault tolerant as it will be deployed across fault domains. By default all new deployments of Azure App Service has this capability however for deployments completed prior to Azure Stack 1802 update being applied refer to the [App Service Fault Domain documentation](azure-stack-app-service-before-you-get-started.md )

- **Deploy in existing virtual network** - Customers can now deploy App Service on Azure Stack within an existing virtual network. Deploying in an existing virtual network enables customers to connect to the SQL Server and File Server, required for Azure App Service, over private ports. During deployment, customers can select to deploy in an existing virtual network, however [must create subnets for use by App Service](azure-stack-app-service-before-you-get-started.md#virtual-network) prior to deployment.

- Updates to **App Service Tenant, Admin, Functions portals and Kudu tools**. Consistent with Azure Stack Portal SDK version.
'''
    ent_items = extract_entities(testex)
    return "Entities: {}".format(ent_items)


if __name__ == '__main__':
   app.run(debug = True)
