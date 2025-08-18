import ollama, json, re, os

prompt_system = '''
You are a multilingual personal information detection tool. Personal information is information that can lead to someone in the text being reidentified, classified according to the following pattern:

personal_name — a person's name, including given name, surname, middle name, initials
institution — any relevant institutions, e.g. schools, workplaces, places of worship, hospitals, etc.
geographic — any relevant geographic information, e.g. street name and number, district, city, country, etc.
transportation — unique names or numbers of relevant public transport lines
age — age in digits or words
date — any relevant dates
other — any other relevant personal information, including but not limited to phone number, e-mail address, urls, personal identification number, account number, license number, other numerical sequences, profession, work, education, family relations, spoken languages, religious beliefs, political opinions, sexuality, gender identity, medical conditions

Remember to only mark information that could lead to reidentification of a natural person.
'''

text = '''Mitt namn är Sonja och jag är 29 år. Jag kommer från Polen och  just nu bor i Visby. Jag talar polska, svenska, engelska och lite tyska. Jag jobbar på förskolan som förskollärare. Min dag börjar tidigt: jag går upp vid kl.6.00, borstar tänderna, duschar, tar min morgonkaffe och cyklar till förskolan. Min arbetsdag börjar kl.7.00. Först tar jag  emot mina söta barn. Vi leker ute en liten stund, sedan går vi in och har några aktiviteter inne, t.ex. läser böcker eller  pysslar. Lunch på förskolan brukar vara vid 11.30,  och efter detta har vi en tyst timme. Småbarn har madrasser i ett separat rum där de kan sova, lite äldre barn sitter vid bordet och leker för sig själva, t.ex. målar. Jag hjälper barnen både vid lunch, vid lekar och vid aktiviteter. 

Vid 16-tiden är min arbetsdag slut. Efter jobbet gör jag olika saker: ibland spelar jag tennis med mina väninnor, Kathy och Anna, ibland går jag ut med min pojkvän Måns, och ibland cyklar jag direkt hem. 
Det är en hel del man behöver hinna med hemma: laga mat, städa, fixa kläder, läsa. Varje dag planerar jag att lägga mig vid 23, men det blir aldrig av. Jag lägger mig vid midnatt eller senare. '''

prompt_user ='''
For each token in the given text, determine whether it is a piece of personal information and assign the appropriate tag. Return the results in a JSON format. Only return the JSON, do not provide any explanations. 
Example:
Text: I’m from Slovakia, but one of my best friends, Marie, is from Norway.
Result:
{
"1":{"I’m":""},
"2":{"from":""},
"3":{"Slovakia":"geographic"},
"4":{",":""},
"5":{"but":""},
"6":{"one":""},
"7":{"of":""},
"8":{"my":""},
"9":{"best":""},
"10":{"friends":""},
"11":{",":""},
"12":{"Marie":"personal_name"},
"13":{",":""},
"14":{"is":""},
"15":{"from":""},
"16":{"Norway":"geographic"},
"17":{".":""}
}

Text: Mitt namn är Sonja och jag är 29 år. Jag kommer från Polen och  just nu bor i Visby. Jag talar polska, svenska, engelska och lite tyska. Jag jobbar på förskolan som förskollärare. Min dag börjar tidigt: jag går upp vid kl.6.00, borstar tänderna, duschar, tar min morgonkaffe och cyklar till förskolan. Min arbetsdag börjar kl.7.00. Först tar jag  emot mina söta barn. Vi leker ute en liten stund, sedan går vi in och har några aktiviteter inne, t.ex. läser böcker eller  pysslar. Lunch på förskolan brukar vara vid 11.30,  och efter detta har vi en tyst timme. Småbarn har madrasser i ett separat rum där de kan sova, lite äldre barn sitter vid bordet och leker för sig själva, t.ex. målar. Jag hjälper barnen både vid lunch, vid lekar och vid aktiviteter. 

Vid 16-tiden är min arbetsdag slut. Efter jobbet gör jag olika saker: ibland spelar jag tennis med mina väninnor, Kathy och Anna, ibland går jag ut med min pojkvän Måns, och ibland cyklar jag direkt hem. 
Det är en hel del man behöver hinna med hemma: laga mat, städa, fixa kläder, läsa. Varje dag planerar jag att lägga mig vid 23, men det blir aldrig av. Jag lägger mig vid midnatt eller senare. 

Result:'''

messages = [
  {
    'role': 'system',
    'content': prompt_system,
  },
  {
    'role': 'user',
    'content': prompt_user,
  },
]

response = ollama.chat(model='gemma2:9b', messages=messages, format='json')

json_response = json.loads(response['message']['content'])

tokens_and_anns = []
for value in json_response.values():
    for k, v in value.items():
        tokens_and_anns.append((k, v))

running_idx = 0
anns_to_keep = []    
for token, ann in tokens_and_anns:
    match_indices = [(m.start(0), m.end(0)) for m in re.finditer(re.escape(token), text)]
    for indices in match_indices:
        if indices[0] >= running_idx:
            if len(ann) > 0 and ann in ['personal_name', 'institution', 'geographic', 'transportation', 'age', 'date', 'other']:
                anns_to_keep.append([indices[0], indices[1], ann, token])
            running_idx = indices[1]
            break
            
all_jsons = []
json_to_be = {
            'id': 'sample0',
            'text': text,
            'pair': "",
            'lang': "",
            'label': [ann[:3] for ann in anns_to_keep],
            'comments': ["Generated using gemma2:9b."]
        }
all_jsons.append(json_to_be)
            
with open(os.path.join('./', 'gemma.jsonl'), 'w', encoding='utf-8') as f:
    for element in all_jsons:
        json.dump(element, f, ensure_ascii=False)
        f.write('\n')        