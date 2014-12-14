#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script imports the languages from amara into the database into the 
# language table in the columns lang_amara_short and lang_en
# The amara data is available here:
# http://www.amara.org/api2/partners/languages/?format=json
#==============================================================================

import os
import sys
from lxml import etree
from urllib import request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Language

# All languages and their code from the json file
lang_dict = {"aa": "Afar", "ab": "Abkhazian", "ae": "Avestan", "af": "Afrikaans", "aka": "Akan", "am": "Amharic", "amh": "Amharic", "an": "Aragonese", "ar": "Arabic", "arc": "Aramaic", "arq": "Algerian Arabic", "as": "Assamese", "ase": "American Sign Language", "ast": "Asturian", "av": "Avaric", "ay": "Aymara", "az": "Azerbaijani", "ba": "Bashkir", "bam": "Bambara", "be": "Belarusian", "ber": "Berber", "bg": "Bulgarian", "bh": "Bihari", "bi": "Bislama", "bn": "Bengali", "bnt": "Ibibio", "bo": "Tibetan", "br": "Breton", "bs": "Bosnian", "bug": "Buginese", "ca": "Catalan", "cak": "Cakchiquel, Central", "ce": "Chechen", "ceb": "Cebuano", "ch": "Chamorro", "cho": "Choctaw", "cku": "Koasati", "co": "Corsican", "cr": "Cree", "cs": "Czech", "ctd": "Chin, Tedim", "ctu": "Chol, Tumbal\u00e1", "cu": "Church Slavic", "cv": "Chuvash", "cy": "Welsh", "da": "Danish", "de": "German", "de-at": "German (Austria)", "de-ch": "German (Switzerland)", "din": "Dinka", "dsb": "Lower Sorbian", "dv": "Divehi", "dz": "Dzongkha", "ee": "Ewe", "efi": "Efik", "el": "Greek", "en": "English", "en-ca": "English (Canada)", "en-gb": "English, British", "en-ie": "English (Ireland)", "en-us": "English (United States)", "eo": "Esperanto", "es": "Spanish", "es-419": "Spanish (Latin America)", "es-ar": "Spanish, Argentinian", "es-es": "Spanish (Spain)", "es-mx": "Spanish, Mexican", "es-ni": "Spanish, Nicaraguan", "et": "Estonian", "eu": "Basque", "fa": "Persian", "fa-af": "Persian (Afghanistan)", "ff": "Fulah", "fi": "Finnish", "fil": "Filipino", "fj": "Fijian", "fo": "Faroese", "fr": "French", "fr-be": "French (Belgium)", "fr-ca": "French (Canada)", "fr-ch": "French (Switzerland)", "ful": "Fula", "fy": "Western Frisian", "fy-nl": "Frisian", "g": "v", "ga": "Irish", "gd": "Scottish Gaelic", "gl": "Galician", "gn": "Guaran", "gu": "Gujarati", "gv": "Manx", "ha": "Hausa", "hai": "Haida", "hau": "Hausa", "haw": "Hawaiian", "haz": "Hazaragi", "hb": "HamariBoli (Roman Hindi-Urdu)", "hch": "Huichol", "he": "Hebrew", "hi": "Hindi", "ho": "Hiri Motu", "hr": "Croatian", "hsb": "Upper Sorbian", "ht": "Creole, Haitian", "hu": "Hungarian", "hup": "Hupa", "hus": "Huastec, Veracruz", "hy": "Armenian", "hz": "Herero", "ia": "Interlingua", "ibo": "Igbo", "id": "Indonesian", "ie": "Interlingue", "ii": "Sichuan Yi", "ik": "Inupia", "ilo": "Ilocano", "inh": "Ingush", "io": "Ido", "iro": "Iroquoian languages", "is": "Icelandic", "it": "Italian", "iu": "Inuktitut", "iw": "Hebrew", "ja": "Japanese", "jv": "Javanese", "ka": "Georgian", "kar": "Karen", "kau": "Kanuri", "kik": "Gikuyu", "kin": "Rwandi", "kj": "Kuanyama, Kwanyama", "kk": "Kazakh", "kl": "Greenlandic", "km": "Khmer", "kn": "Kannada", "ko": "Korean", "kon": "Kongo", "ks": "Kashmiri", "ksh": "Colognian", "ku": "Kurdish", "kv": "Komi", "kw": "Cornish", "ky": "Kyrgyz", "la": "Latin", "lb": "Luxembourgish", "lg": "Ganda", "li": "Limburgish", "lin": "Lingala", "lkt": "Lakota", "lld": "Ladin", "ln": "Lingala", "lo": "Lao", "lt": "Lithuanian", "ltg": "Latgalian", "lu": "Luba-Katagana", "lua": "Luba-Kasai", "luo": "Luo", "luy": "Luhya", "lv": "Latvian", "mad": "Madurese", "meta-audio": "Metadata: Audio Description", "meta-geo": "Metadata: Geo", "meta-tw": "Metadata: Twitter", "meta-wiki": "Metadata: Wikipedia", "mg": "Malagasy", "mh": "Marshallese", "mi": "Maori", "mk": "Macedonian", "ml": "Malayalam", "mlg": "Malagasy", "mn": "Mongolian", "mni": "Manipuri", "mnk": "Mandinka", "mo": "Moldavian, Moldovan", "moh": "Mohawk", "mos": "Mossi", "mr": "Marathi", "ms": "Malay", "mt": "Maltese", "mus": "Muscogee", "my": "Burmese", "na": "Naurunan", "nan": "Hokkien", "nb": "Norwegian Bokmal", "nci": "Nahuatl, Classical", "ncj": "Nahuatl, Northern Puebla", "nd": "North Ndebele", "ne": "Nepali", "ng": "Ndonga", "nl": "Dutch", "nl-be": "Dutch (Belgium)", "nn": "Norwegian Nynorsk", "no": "Norwegian", "nr": "Southern Ndebele", "nso": "Northern Sotho", "nv": "Navajo", "nya": "Chewa", "oc": "Occitan", "oji": "Ojibwe", "om": "Oromo", "or": "Oriya", "orm": "Oromo", "os": "Ossetian, Ossetic", "pa": "Punjabi", "pam": "Kapampangan", "pan": "Punjabi", "pap": "Papiamento", "pi": "Pali", "pl": "Polish", "pnb": "Western Punjabi", "prs": "Dari", "ps": "Pashto", "pt": "Portuguese", "pt-br": "Portuguese, Brazilian", "pt-pt": "Portuguese (Portugal)", "qu": "Quechua", "que": "Quechua", "qvi": "Quichua, Imbabura Highland", "raj": "Rajasthani", "rm": "Romansh", "rn": "Rundi", "ro": "Romanian", "ru": "Russian", "run": "Rundi", "rup": "Macedo", "rw": "Kinyarwanda", "ry": "Rusyn", "sa": "Sanskrit", "sc": "Sardinian", "sco": "Scots", "sd": "Sindhi", "se": "Northern Sami", "sg": "Sango", "sgn": "Sign Languages", "sh": "Serbo-Croatian", "si": "Sinhala", "sk": "Slovak", "skx": "Seko Padang", "sl": "Slovenian", "sm": "Samoan", "sn": "Shona", "sna": "Shona", "so": "Somali", "som": "Somali", "sot": "Sotho", "sq": "Albanian", "sr": "Serbian", "sr-latn": "Serbian, Latin", "srp": "Montenegrin", "ss": "Swati", "st": "Southern Sotho", "su": "Sundanese", "sv": "Swedish", "sw": "Swahili", "swa": "Swahili", "szl": "Silesian", "ta": "Tamil", "tar": "Tarahumara, Central", "te": "Telugu", "tet": "Tetum", "tg": "Tajik", "th": "Thai", "ti": "Tigrinya", "tir": "Tigrinya", "tk": "Turkmen", "tl": "Tagalog", "tlh": "Klingon", "tn": "Tswana", "to": "Tonga", "toj": "Tojolabal", "tr": "Turkish", "ts": "Tsonga", "tsn": "Tswana", "tsz": "Purepecha", "tt": "Tatar", "tw": "Twi", "ty": "Tahitian", "tzh": "Tzeltal, Oxchuc", "tzo": "Tzotzil, Venustiano Carranza", "ug": "Uyghur", "uk": "Ukrainian", "umb": "Umbundu", "ur": "Urdu", "uz": "Uzbek", "ve": "Venda", "vi": "Vietnamese", "vls": "Flemish", "vo": "Volapuk", "wa": "Walloon", "wbl": "Wakhi", "wo": "Wolof", "wol": "Wolof", "xh": "Xhosa", "xho": "Xhosa", "yaq": "Yaqui", "yi": "Yiddish", "yo": "Yoruba", "yor": "Yoruba", "yua": "Maya, Yucat\u00e1n", "za": "Zhuang, Chuang", "zam": "Zapotec, Miahuatl\u00e1n", "zh": "Chinese, Yue", "zh-cn": "Chinese, Simplified", "zh-hans": "Chinese (Simplified Han)", "zh-hant": "Chinese (Traditional Han)", "zh-hk": "Chinese, Traditional (Hong Kong)", "zh-sg": "Chinese, Simplified (Singaporean)", "zh-tw": "Chinese, Traditional", "zu": "Zulu", "zul": "Zulu"}

# List var for the languages and short codes
lang_list = []

# Create language list from the dictionary
for any_lang in lang_dict:  
   lang_list.append([any_lang, lang_dict[any_lang]])

# Put data into the database, check if dataset already in there   
for any_lang in lang_list:
    print (any_lang[0], any_lang[1])
    Language.objects.get_or_create(lang_amara_short=any_lang[0])
 
print ("done")

