import pandas as pd
import spacy
import numpy as np
from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk
import re

data = pd.read_csv('Bioclassification.csv')


bio = data.Biography

position_list = []
company_list = []
prev_company_list = []
nlp = spacy.load('en')

## Cleans the string and gets rid of the extra fullstops, converts P.hd -> phd and so on
def string_cleaner(sentence):
    S = sentence
    S = S.replace('M.A.', 'Masters')
    S = S.replace('B.S.EE', 'Bachelors')
    S = S.replace('BSEE', 'Bachelors')
    S = S.replace('B.S.F.S.', 'Bachelors')
    S = S.replace('B.B.A.', 'Bachelors')
    S = S.replace('B.B.A.', 'Bachelors')
    S = S.replace('B.S.E.E.', 'Bachelors')
    S = S.replace('M.S.E.E.', 'Masters')
    S = S.replace('B.S.E.', 'Bachelors')
    S = S.replace('bachelor’s', 'Bachelors')
    S = S.replace("bachelor's", 'Bachelors')
    S = S.replace('Master', 'Masters')
    S = S.replace('M.B.A.', 'Masters')
    S = S.replace('B.S.', 'Bachelors')
    S = S.replace('B.A.', 'Bachelors')
    S = S.replace('Ph.D.', 'Masters')
    S = S.replace('MBA', 'Masters')
    S = S.replace('LLB', 'Bachelors')
    S = S.replace('undergraduate', 'Bachelors')
    S = S.replace('M.D.', 'Masters')
    S = S.replace('M.S.', 'Masters')
    S = S.replace('B.Sc.', 'Bachelors')
    S = S.replace("Bachelors's", 'Bachelors')
    S = S.replace('Masterss', 'Masters')
    S = S.replace('BA', 'Bachelors')
    S = S.replace('BS', 'Bachelors')
    S = S.replace('MS', 'Masters')
    return(S)


## Cleans the bio after running the function 
final_bio = []
    
for i in range(len(bio)):
    final_bio.append(string_cleaner(bio[i]))
    

### Gets the educational institites out of the sentence in the form of a list 
def educational_finder(sentence):
    the_org_list = []
    nlp_sent = nlp(sentence)
    for orgs in nlp_sent.ents:
        if orgs.label_ == 'ORG' and ('University' in str(orgs) or 'School' in str(orgs) or 'College' in str(orgs)):
            the_org_list.append(orgs)
    return(the_org_list)

## Gets only the important sentences from the whole paragraph, Seperate for masters and bachelors.
def important_sent(sentence):
    S= {}
    sent = sent_tokenize(sentence)
    for each_sent in sent:
        if 'BACHELORS' in each_sent.upper() and 'MASTERS' not in each_sent.upper():
            S['Bachelors'] = each_sent
        elif 'MASTERS' in each_sent.upper() and 'BACHELORS' not in each_sent.upper():
            S['Masters'] = each_sent
        elif 'BACHELORS' in each_sent.upper() and 'MASTERS' in each_sent.upper():
            S['Both'] = each_sent
        elif 'GRADUATED' in each_sent.upper():
            S['Bachelors'] = each_sent
        elif 'GRADUATE' in each_sent.upper():
            S['Bachelors'] = each_sent
    return(S)

## Depending on the type of sentence it returns a list in the form [Bachelors, masters] and   
## if they have len 3 include the middle one in other educations          
def education_both(sentence):
    words = word_tokenize(sentence)
    list_edu = []
    for i in range(len(words)):
        if words[i].upper() == "BACHELORS" or words[i].upper() == 'GRADUATED' or words[i].upper() == 'PASSED' or words[i].upper() == 'GRADUATE':
            list_edu = educational_finder(sentence)
            return list_edu
        if words[i].upper() == "MASTERS":
            list_edu = educational_finder(sentence)
            list_edu.reverse()
            return list_edu
        
        

final_bio = final_bio    
###looping through the whole list
final_list = []
for bios in final_bio:
    education_list = []
    important = important_sent(bios)
    try:
        if important['Bachelors'] != [] and education_both(important['Bachelors']) != None:
            education_list +=education_both(important['Bachelors'])
    except KeyError:
        pass
    
    try:
        if important['Masters'] != [] and education_both(important['Masters']) != None:
           education_list +=education_both(important['Masters'])
    except KeyError:
        pass
    
    try:
        if important['Both'] != []:
            single_college = education_both(important['Both'])
            try:
                if len(single_college) == 1:
                    single_college.append(single_college[0])
                    education_list += single_college
                else:
                    education_list +=single_college
            except TypeError:
                pass
    except KeyError:
        pass
    final_list.append(education_list)

# Correction for harvard Business school 
    
for row in final_list:
    try:
        if row[0]:
            x = str(row[0])
            y = x.upper()
        if 'BUSINESS' in y and 'HARVARD' in y:
            try:
                row[0],row[1] = row[1],row[0]
            except IndexError:
                pass
    except IndexError:
        pass
def clean_current_company(sentence):
    sent_token = sent_tokenize(sentence)
    sent_token = sent_token[0]
    sent_token = re.sub(r'\bis\b', 'serves as', sent_token)
    sent_token = re.sub(r'\ba\b', '', sent_token)
    sent_token = re.sub(r'\b&\b', '', sent_token)
    sent_token = re.sub(r'\band\b', '', sent_token)
    return sent_token

def get_current_comp(sentence):
    sent_token = clean_current_company(sentence)
    word_token = list(pos_tag(word_tokenize(sent_token)))
    position = ''
    company = ''
    for i in range(len(word_token)):
        try:
            if (word_token[i][0]) == 'as':
                j = i+1
                while(word_token[j][1]!='IN'):
                    position += word_token[j][0]
                    position += ' '
                    j+=1
            if (word_token[i][0]) == 'at':
                j = i+1
                while(word_token[j][1]=='NNP'):
                    company += word_token[j][0]
                    company += ' '
                    j+=1 
        except IndexError:
            break
    position_list.append(position)
    company_list.append(company)


def write_to_excel():
    df = pd.DataFrame({'Previous Company':prev_company_list})
    writer = pd.ExcelWriter('output_prev.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()

## String cleaner for replacement of words.

def string_cleaner(sentence):
    S = sentence
    S = S.replace('M.A.', 'MA')
    S = S.replace('MBA', 'Masters')
    S = S.replace('BA', 'Bachelors')
    S = S.replace('Bachelor', 'Bachelors')
    S = S.replace('graduated', 'Bachelors')
    S = S.replace('bachelor', 'Bachelors')
    S = S.replace('B.S.EE', 'Bachelors')
    S = S.replace('B.S.F.S.', 'Bachelors')
    S = S.replace('B.B.A.', 'Bachelors')
    S = S.replace('B.S.E.E.', 'Bachelors')
    S = S.replace('M.S.E.E.', 'MSEE')
    S = S.replace('M.Sc.', 'MSC')
    S = S.replace('B.S.E.', 'Bachelors')
    S = S.replace('bachelor’s', 'Bachelors')
    S = S.replace("bachelor's", 'Bachelors')
    S = S.replace('Master', 'Masters')
    S = S.replace('M.B.A.', 'MBA')
    S = S.replace('B.S.', 'Bachelors')
    S = S.replace('B.A.', 'Bachelors')
    S = S.replace('Ph.D.', 'PHD')
    S = S.replace('LLB', 'Bachelors')
    S = S.replace('undergraduate', 'Bachelors')
    S = S.replace('M.D.', 'MD')
    S = S.replace('M.S.', 'MS')
    S = S.replace('B.Sc.', 'Bachelors')
    S = S.replace("Bachelors's", 'Bachelors')
    S = S.replace('Masterss', 'Masters')

    return(S)
    
## Data cleaned that is without any bachlors or masters 
def Cleaner_rev(sentence):
    clean_bio = ''
    sentence = string_cleaner(sentence)
    sents = sent_tokenize(sentence)
    sents = sents[1:]
    index = None
    for i in range(len(sents)):
        if 'PRIOR' in sents[i].upper():
            index = i
            break
    if index is not None:
        sents = sents[index:]
    else:
        sents = []
    for i in sents:
        if 'BACHELORS' in i.upper() or 'MASTERS'in i.upper() or 'COLLEGE' in i.upper():
            pass
        else:
            clean_bio+= i 
    return(clean_bio)

## get the current organisation.
    
def get_the_org(sentence):
    nlp_sent = nlp(sentence)
    print(nlp_sent)
    for i in nlp_sent.ents:
        if str(i) in ['Chair', 'Co-Chair', 'Board']:
            pass
        else:
            return(i.label_, i)
            
#normalising the data            
  
def comp_cleaner(bios):
    bios = bios.replace('was','served')
    bios = bios.replace('worked','served')
    bios = Cleaner_rev(bios)
    return bios

#extracting relevant data from the bio

def comp_bio(bios):
    bio_list = sent_tokenize(bios)
    imp_bio = []
    for i in bio_list:
        if 'served' in i:
            imp_bio.append(i)
            
    return imp_bio
            
#extracting org from the sentence 
     
def get_org_from_sent(sentence):
#    prev_position_list = []
    sentence = Cleaner_rev(sentence)
    company_name = []
    prev_company_list = []
    sent_list = list(pos_tag(word_tokenize(sentence)))
    print(sent_list)
#    nlp_sents = nlp(sentence)
    
    for verbs in range(len(sent_list)):
        try:
            if sent_list[verbs][1] == 'VBZ' or sent_list[verbs][1]== 'VBG':
                j = verbs+1
                if sent_list[j][1]!= 'NNP':
                    print('hi')
                    while sent_list[j][1]!= 'NNP':
                        j = j+1
                    j = j-1
                while sent_list[j][1] == 'NNP':
                    print('finally')
                    print(sent_list[j][0])
                    company_name.append(sent_list[j][0])
                    j = j+1
                print(sent_list[j][0])
                verbs = j
                prev_company_list.append(company_name)
        except IndexError:
            break
    return prev_company_list
    
