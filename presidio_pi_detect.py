# Microsoft Presidio for Swedish on the sample essay, code adapted from:
# https://microsoft.github.io/presidio/getting_started/getting_started_text/#__tabbed_1_1
# https://microsoft.github.io/presidio/analyzer/customizing_nlp_models/

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
import os, json

configuration = {
    "nlp_engine_name": "spacy",
    "models": [{'lang_code': 'sv', 'model_name': 'sv_core_news_sm'}]
}

provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine_with_swedish = provider.create_engine()

# following https://microsoft.github.io/presidio/supported_entities/
entity_mapping = {
    'CREDIT_CARD': 'other',
    'CRYPTO': 'other', 
    'DATE_TIME': 'date',
    'EMAIL_ADDRESS': 'other',
    'IBAN_CODE': 'other',
    'IP_ADDRESS': 'other',
    'NRP': 'other',
    'LOCATION': 'geographic',
    'PERSON': 'personal_name',
    'PHONE_NUMBER': 'other',
    'MEDICAL_LICENSE': 'other',
    'URL': 'other'
}

text='''Mitt namn är Sonja och jag är 29 år. Jag kommer från Polen och  just nu bor i Visby. Jag talar polska, svenska, engelska och lite tyska. Jag jobbar på förskolan som förskollärare. Min dag börjar tidigt: jag går upp vid kl.6.00, borstar tänderna, duschar, tar min morgonkaffe och cyklar till förskolan. Min arbetsdag börjar kl.7.00. Först tar jag  emot mina söta barn. Vi leker ute en liten stund, sedan går vi in och har några aktiviteter inne, t.ex. läser böcker eller  pysslar. Lunch på förskolan brukar vara vid 11.30,  och efter detta har vi en tyst timme. Småbarn har madrasser i ett separat rum där de kan sova, lite äldre barn sitter vid bordet och leker för sig själva, t.ex. målar. Jag hjälper barnen både vid lunch, vid lekar och vid aktiviteter. 

Vid 16-tiden är min arbetsdag slut. Efter jobbet gör jag olika saker: ibland spelar jag tennis med mina väninnor, Kathy och Anna, ibland går jag ut med min pojkvän Måns, och ibland cyklar jag direkt hem. 
Det är en hel del man behöver hinna med hemma: laga mat, städa, fixa kläder, läsa. Varje dag planerar jag att lägga mig vid 23, men det blir aldrig av. Jag lägger mig vid midnatt eller senare.'''

# Set up the engine, loads the NLP module (spaCy model by default) 
# and other PII recognizers
analyzer = AnalyzerEngine(
    nlp_engine=nlp_engine_with_swedish,
    supported_languages=['sv']
)

# Call analyzer to get results
results = analyzer.analyze(text=text,
                        #    entities=["PHONE_NUMBER"],
                           language='sv')

all_jsons = []
json_to_be = {
        'id': 'sample0',
        'text': text,
        'pair': "",
        'lang': "",
        'label': [[ann.start, ann.end, entity_mapping[ann.entity_type]] for ann in results],
        'comments': ["Generated using a Microsoft Presidio."]
    }
all_jsons.append(json_to_be)
                  
with open(os.path.join('./', 'presidio.jsonl'), 'w', encoding='utf-8') as f:
    for element in all_jsons:
        json.dump(element, f, ensure_ascii=False)
        f.write('\n')     
