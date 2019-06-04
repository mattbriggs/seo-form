import os
import datetime
import nltk
import pandas as pd
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap


app = Flask(__name__)
Bootstrap(app)

# stop words



# SEOpage

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
    SEO_dict["filename"] = ""
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
    '''Takes an list with strings, splits by space, and removes single items.'''
    outlist = []
    for i in inlist:
        j = i.strip()
        h = j.split()
        if len(h) > 1:
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


def apply_stoplist(inlist):
    '''Iterate over the list to remove stop items.'''
    stoplist = '''
1
2
3
4
5
6
7
8
9
.NET
/
/p
access
Account
Add
admin
administrator
ADV190001
agent
alert
ApiName
application
apply
article
ASDK
authentication
AzCopy
Azure
AzureStack-QuickStart-Templates
Back
backup
Backup-restor
backups
Billing
BitLocker
br
C
certificate
Changes
choice
Choose
Clean
configuration
Connect
connection
container
Containers
Controller
Core
course
Create
Custom
customer
CVE-2018-8477
dash
Datacenter
Delete
delsub1
delsub2
delsub3
Deploy
deployment
Description
Develop
Dimensions
directory
disk
disks
DNS
Do
Download
drain
endpoint
environment
ExpressRoute
f5
Face
failover
failure
features
FileZilla
Fixes
format
GeoType
Get
Get-StorageJob
GitHub
Go
group
H
Helm
Help
history
hotfix
Hotfixes
How
https
identity
image
IMPORTANT
INCLUDE
infrastructure
Install
Inventory
IPv6
issue
issues
Java
key
Later
Learn
li
Linux
machine
machines
Manage
Marketplace
Maximum
Metrics
Microsoft
Microsoft.Storage
Minikube
Modify
multi-tenancy
MySQL
name
NAT
Network
Networking
New-AzureRmPolicyDefinition
No
NodeJS
NOTE
NTP
ODX20537
offer
p
package
parameters
Password
paths
permissions
PFX
PHP
pipeline
plan
Portal
PowerShell
Prerequisites
process
profile
profiles
progress
project
provider
Publish
quota
Quotas
records
Register
registration
registrationName
release
repository
resourceGroup
resources
resume
Role
rotation
RSS
Ruby
script
section
Service
ServiceAdminPassword
services
Set
shares
Sign
site
SKU
SMB
Stack
state
Status
step
Steps
Storage
Subscribe
subscription
support
Supported
systems
Tags
Telemetry
template
templates
test
tile
TIP
TLS
Tomcat
tool
tools
UI
Uninstall
unit
update
URI
use
user
users
V
VaaS
VaaSAccountTenantId
VaaSSolutionName
VaaSTestPassName
Validation
variables
version
VM
VMs
VPN
warning
web
Windows
zone
div class
'''
    stoplist = stoplist.split("\n")
    outlist = []
    for i in inlist:
        if i not in stoplist:
            outlist.append(i)
    return outlist


def clean_keyword(inlist):
    glyphs = '[]|<>*='
    outlist = []
    for i in inlist:
        for char in glyphs:
            i = i.replace(char, "")
        outlist.append(i)
    return outlist


def extract_entities(bodytext):
    '''Take a multisentence text and return a list of unique entities.'''
    breakdown = parse_sentences(bodytext)
    entities = []
    for sent in breakdown:
        for i in extract_chunks(sent):
            entities.append(i)
    step1_entities = clean_keyword(entities)
    step2_entities = remove_blank(step1_entities)
    step3_entities = set(step2_entities) # remove duplicates
    step4_entities = only_word_pairs(list(step3_entities))
    step5_entities = apply_stoplist(step4_entities)
    return step5_entities


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

if __name__ == '__main__':
   app.run(debug = True)
