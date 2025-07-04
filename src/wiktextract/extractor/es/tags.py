from .models import WordEntry

# https://es.wiktionary.org/wiki/Wikcionario:Lista_de_etiquetas

# https://es.wiktionary.org/wiki/Plantilla:uso
USO_TAGS = {
    "académico": "academic",
    "afectado": "literary",
    #  "afectuoso": "affectionate",
    "anticuado": "outdated",
    "antiguo": "obsolete",
    "arcaico": "obsolete",
    "arcaizante": "obsolete",
    "arcaísmo": "obsolete",
    "bajo": "colloquial",
    "chistoso": "jocular",
    "clásico": "Classical",
    "coloq": "colloquial",
    "coloq.": "colloquial",
    "coloquial": "colloquial",
    #  "culto": "worship",
    "cómico": "jocular",
    "despect.": "derogatory",
    "despectivo": "derogatory",
    "desus": "outdated",
    "desus.": "outdated",
    "desusada": "outdated",
    "desusado": "outdated",
    "elevado": "literary",
    "epiceno": "epicene",
    "eufemismo": "euphemism",
    "eutca": "adjective",
    "familiar": "colloquial",
    "figurado": "figurative",
    "formal": "formal",
    "germanía": "slang",
    "grosero": "vulgar",
    "humorístico": "jocular",
    "infantil": "childish",
    "informal": "colloquial",
    "infrecuente": "rare",
    "irónico": "ironic",
    "jerga": "slang",
    #  "jerga legal": "legal jargon",
    #  "jerga metalera": "metal slang",
    #  "jerga skinhead": "skinhead slang",
    "jergal": "slang",
    "jocoso": "jocular",
    "literario": "literary",
    "malsonante": "vulgar",
    #  "mayúscula": "capital letter",
    #  "mayúscula disciplinas": "usually lowercase",
    #  "mayúscula puntos cardinales":
    #  "It is lowercase except when it is part of a proper noun",
    #  "mayúscula taxones": "taxonomy rules for capitalization",
    "medieval": "Medieval",
    "minúscula": "lower case",
    "moderno": "modern",
    "neologismo": "neologism",
    "obsoleto": "obsolete",
    #  "ordinal compuesto": "rules for compound ordinal numbers",
    #  "ordinal-compuesto": "rules for compound ordinal numbers",
    "peyorativo": "derogatory",
    "poco frecuente": "rare",
    "poco usado": "rare",
    "popular": "colloquial",
    "poético": "literary",
    "raro": "rare",
    #  "rur": "rural",
    #  "rural": "rural",
    "sebtc": "noun",
    "setc": "noun",
    #  "sin uso": "The editors have been unable to find any examples of use of
    # this word in published texts or corpus",
    "slang": "slang",
    "soez": "vulgar",
    "sutp": "plural",
    "suts": "singular",
    #  "trans-prefijo": "",
    "ucsp": ["plural", "noun"],
    "umcp": "pronominal",
    "umcs": "noun",
    "umcv": "vocative",
    "umep": "plural",
    "umpl": "plural",
    "utca": "adjective",
    "utcadv": "adverb",
    "utcaf": ["feminine", "adjective"],
    "utcam": ["masculine", "adjective"],
    "utcc": "conjunction",
    "utcf": ["feminine", "noun"],
    "utcg": "gerund",
    # "utci": "It is also used as intransitive",
    "utcm": ["masculine", "noun"],
    "utcp": "pronominal",
    "utcprnl": "pronominal",
    "utcs": "noun",
    "utcsf": ["feminine", "noun"],
    "utcsm": ["masculine", "noun"],
    "utcsma": ["masculine", "feminine", "noun"],
    "utcsmf": "noun",
    "utct": "transitive",
    "utmp": ["pronominal", "verb"],
    "utrep": "repeated",
    "vulg": "vulgar",
    "vulgar": "vulgar",
}

# https://es.wiktionary.org/wiki/Plantilla:ámbito
AMBITO_TAGS = {
    "Acaxochitlán": "Acaxochitlán",
    "Alemania": "Germany",
    "Algarve": "Algarve",
    "Almería": "Almería",
    "Am.": "America",
    "Amecameca": "Amecameca",
    "América": "America",
    "América Central": "Central-America",
    "América Latina": "America",
    "América central": "Central-America",
    "América del Sur": "South-America",
    "Andalucía": "Andalusia",
    "Antioquia": "Antioquia",
    "Aragón": "Aragon",
    "Aragón Oriental": "Eastern-Aragon",
    "Arg.": "Argentina",
    "Argentina": "Argentina",
    "Asturias": "Asturias",
    "Atlapexco": "Atlapexco",
    "Australia": "Australia",
    "Baja California": "Lower-California",
    "Baja Navarra": "Lower-Navarre",
    "Bearn": "Bearn",
    "Bearne": "Bearn",
    "Belluno": "Belluno",
    "Bolivia": "Bolivia",
    "Bolonia": "Bologna",
    "Brasil": "Brazil",
    "Brasil meridional": "Southern-Brazil",
    "Burgos": "Burgos",
    "Calpan": "Calpan",
    "Campeche": "Campeche",
    "Canadá": "Canada",
    "Canarias": "Canaries",
    "Canoa": "Canoe",
    "Cantabria": "Cantabria",
    "Caribe": "Caribbean",
    "Carpi": "Carpi",
    "Cartagena": "Cartagena",
    "Castilla": "Castile",
    "Cataluña": "Catalonia",
    "Centro América": "Central-America",
    "Centro de Chile": "Central-Chile",
    "Centro de México": "Central-Mexico",
    "Centroamérica": "Central-America",
    "Ceuta": "Ceuta",
    "Chiapas": "Chiapas",
    "Chicontepec": "Chicontepec",
    "Chihuahua": "Chihuahua",
    "Chile": "Chile",
    "Chiloé": "Chiloé",
    "Chipilo": "Chipilo",
    "Chl.": "Chile",
    "Cholula": "Cholula",
    "Chubut": "Chubut",
    "Ciudad de México": "Mexico-City",
    "Colombia": "Colombia",
    "Connacht": "Connacht",
    "Connemara": "Connemara",
    "Cono Sur": "South-Cone",
    "Costa Rica": "Costa-Rica",
    "Cuba": "Cuba",
    "Cuentepec": "Cuentepec",
    "Cuetzalan": "Cuetzalan",
    "Cádiz": "Cádiz",
    "Córdoba (España)": "Córdoba",
    "Dominicana": "Dominican-Republic",
    "EEUU": "US",
    "Ecuador": "Ecuador",
    "El Salv.": "El-Salvador",
    "El Salvador": "El-Salvador",
    "Escocia": "Scotland",
    "España": "Spain",
    "Estados Unidos": "US",
    "Europa": "Europe",
    "Euskadi": "Basque Country",
    "Extremadura": "Extremadura",
    "Extremadura (España)": "Extremadura",
    "Filipinas": "Philippines",
    "Francia": "France",
    "Galicia": "Galicia",
    "Gascuña": "Gascony",
    "Granada": "Grenada",
    #  "Grischun": "grisón",
    "Guadalajara": "Guadalajara",
    "Guanajuato": "Guanajuato",
    "Guatemala": "Guatemala",
    "Guernsey": "Guernsey",
    "Guinea Ecuatorial": "Equatorial-Guinea",
    "Hidalgo": "Hidalgo",
    "Hond.": "Honduras",
    "Honduras": "Honduras",
    "Huauchinango": "Huauchinango",
    "Huejutla": "Huejutla",
    "Huelva": "Huelva",
    "Hueyapan": "Hueyapan",
    "Inglaterra": "England",
    "Iparralde": "Iparralde",
    "Irlanda": "Ireland",
    "Islas Baleares": "Balearic-Islands",
    "Italia": "Italy",
    "Jalisco": "Jalisco",
    "Jaltocán": "Jaltocan",
    "Jamaica": "Jamaica",
    "Jersey": "Jersey",
    "La Rioja": "La Rioja",
    "La Rioja (Argentina)": "La Rioja (Argentina)",
    "Labort": "Labort",
    "Languedoc": "Languedoc",
    "Lapurdi": "Labort",
    "León": "León",
    "Liechtenstein": "Liechtenstein",
    "Logudoro": "Logudoro",
    "Lunfardo": "Lunfardo",
    "Mallorca": "Mallorca",
    "Marruecos": "Morocco",
    "Matlapa": "Matlapa",
    "Michoacán": "Michoacán",
    "Milpa Alta": "Milpa Alta",
    "Mirandola": "Mirandola",
    "Munster": "Munster",
    "Murcia": "Murcia",
    "Méjico": "Mexico",
    "México": "Mexico",
    "México (México)": "Mexico",
    "Módena": "Modena",
    "Navarra": "Navarra",
    "Nicaragua": "Nicaragua",
    "Normandía": "Normandy",
    "Norte de Argentina": "Northern-Argentina",
    "Norte de Chile": "Northern-Chile",
    "Nueva Zelanda": "New-Zealand",
    "Nueva Zelandia": "New-Zealand",
    "Nuevo León": "Nuevo-León",
    "Nuevo México": "New-Mexico",
    "Oaxaca": "Oaxaca",
    "Orizatlán": "Orizatlán",
    "Palencia": "Palencia",
    "Panamá": "Panama",
    "Paraguay": "Paraguay",
    "País Vasco": "Basque Country",
    "País Vasco francés": "French Basque Country",
    "Perú": "Peru",
    "Portugal": "Portugal",
    "Provenza": "Provence",
    "Puebla": "Puebla",
    "Puerto Rico": "Puerto-Rico",
    #  "Puter": "high engadino"
    "Quebec": "Quebec",
    "Querétaro": "Querétaro",
    "Reino Unido": "UK",
    "República Dominicana": "Dominican-Republic",
    "Ribera de Navarra": "Ribera-Navarra",
    "Rioja": "Rioja",
    "Rioplatense": "Río-de-la-Plata",
    "Río de la Plata": "Río-de-la-Plata",
    "Salamanca": "Salamanca",
    "Salamanca (España)": "Salamanca",
    "San Juan Quiahije": "San-Juan-Quiahije",
    "San Luis Potosí": "San-Luis-Potosí",
    "Santa María Yosoyúa": "Santa-María-Yosoyúa",
    "Sevilla": "Seville",
    "Sinaloa": "Sinaloa",
    "Sola": "Sola",
    "Sonora": "Sonora",
    "Soria": "Soria",
    "Soule": "Sola",
    "Sudamérica": "South-America",
    "Suiza": "Switzerland",
    "Sur de Chile": "Southern-Chile",
    "Suramérica": "South-America",
    "Surmiran": "Surmirano",
    "Sursilvan": "Sursilvano",
    "Sutsilvan": "Sutsilvano",
    "Tamazunchale": "Tamazunchale",
    "Tepeojuma": "Tepeojuma",
    "Texcoco": "Texcoco",
    "Tlaxcala": "Tlaxcala",
    "Tlaxpanaloya": "Tlaxpanaloya",
    "Toulouse": "Toulouse",
    "USA": "United States",
    "Ulster": "Ulster",
    "Uruguay": "Uruguay",
    "Valencia": "Valencia",
    "Vallader": "Bajo-engadino",
    "Venecia": "Venice",
    "Venezuela": "Venezuela",
    "Veracruz": "Veracruz",
    "Vizcaya": "Vizcaya",
    "Waterford": "Waterford",
    "Xayacatlán": "Xayacatlán",
    "Xilitla": "Xilitla",
    "Xochiatipan": "Xochiatipan",
    "Yaganiza": "Yaganiza",
    "Yahualica": "Yahualica",
    "Yojovi": "Yojovi",
    "Yucatán": "Yucatán",
    "Zacatecas": "Zacatecas",
    "Zamora": "Zamora",
    "Zuberoa": "Sola",
    "Zulia": "Zulia",
    # "alto engadino": "alto engadino",
    "anglonormando": "Anglo-Norman",
    # "bajo engadino": "bajo engadino",
    #  "grischun": "grisón",
    #  "grisón": "grisón",
    #  "haquetía": "haquety",
    "logudorés": "Logudoro",
    "lunf": "Lunfardo",
    "lunfardismo": "Lunfardo",
    "lunfardo": "Lunfardo",
    "parlache": ["Colombia", "slang"],
    #  "puter": "high engadino",
    "rioplatense": "Río-de-la-Plata",
    "rpl": "Río-de-la-Plata",
    "subsilvano": "Sursilvan",
    "supramirano": "Surmiran",
    "suprasilvano": "Sursilvan",
    "sur de Chile": "Southern-Chile",
    "surmirano": "Surmiran",
    "sursilvano": "Sursilvan",
    "sutsilvano": "Sursilvan",
    "vallader": "Lower-Engadine",
    "Á. R. Plata": "Río-de-la-Plata",
    "Álava": "Álava",
}


# https://es.wiktionary.org/wiki/Plantilla:csem
CSEM_TOPICS = {
    "aeronáutica": "aeronautics",
    "agricultura": "agriculture",
    "ajedrez": "chess",
    #  "Algas": "algae",
    "alimento": "food",
    "alimentos": "food",
    "alpinismo": "mountaineering",
    "alquimia": "alchemy",
    "anatomía": "anatomy",
    #  "Anfibios": "amphibians",
    #  "Angiología": "angiology",
    #  "Animales": "animals",
    #  "Animales extintos": "extinct animals",
    "antropología": "anthropology",
    #  "Antropotomía": "anthropotomy",
    #  "Antropónimos": "anthroponyms",
    #  "Anélidos": "annelids",
    #  "Apellidos": "surnames",
    "apicultura": "beekeeping",
    #  "Arbustos": "shrubbery",
    "aritmética": "arithmetic",
    "armas": "weaponry",
    "arqueología": "archeology",
    "arquitectura": "architecture",
    "arte": "art",
    "arte marciales": "martial arts",
    "artes marciales": "martial arts",
    #  "Artrópodos": "arthropods",
    #  "Arácnidos": "arachnids",
    "astrofísica": "astrophysics",
    "astrología": "astrology",
    "astronomía": "astronomy",
    "atletismo": "athletics",
    #  "Audiología": "audiology",
    #  "Automovilismo": "motoring",
    #  "Aves": "birds",
    #  "Bacterias": "bacteria",
    "danza": "dance",
    "baloncesto": "basketball",
    "balonmano": "handball",
    #  "Batería de cocina": "cookware",
    #  "Bebidas": "drinks",
    "billar": "billiards",
    "biología": "biology",
    "bioquímica": "biochemistry",
    "bolos": "bowling",
    "botánica": "botany",
    "béisbol": "baseball",
    #  "Caza": "hunt",
    #  "Cactus": "cactus",
    #  "Campamento": "camp",
    "cardiología": "cardiology",
    "carpintería": "carpentry",
    #  "Casos gramaticales": "grammatical cases",
    #  "Cereales": "cereals",
    #  "Cerrajería": "locksmith",
    "cetrería": "falconry",
    "ciclismo": "cycling",
    "ciencia": "science",
    "ciencia ficción": "science fiction",
    #  "Cine": "cinema",
    "cinegética": "hunting",
    "cinematografía": "cinematography",
    #  "Cinología": "cynology",
    "cirugía": "surgery",
    "ciudades": "cities",
    #  "Cnidarios": "cnidarians",
    #  "Colores": "colors",
    #  "Comercio": "trade",
    "comunicación": "communication",
    #  "Condimentos": "condiments",
    #  "Constelaciones": "constellations",
    "construcción": "construction",
    "contabilidad": "accounting",
    "continentes": "continents",
    #  "Cordilleras": "mountain ranges",
    "correos": "mail",
    #  "Cosmetología": "cosmetology",
    "cosmología": "cosmology",
    "cosmética": "cosmetics",
    "costura": "sewing",
    "cristianismo": "Christianity",
    "cronología": "chronology",
    #  "Crustáceos": "crustaceans",
    #  "Cubertería": "cutlery",
    #  "Cultura": "culture",
    "deporte": "sports",
    #  "Derecho": "right",
    #  "Dinosaurios": "dinosaurs",
    #  "Dioses": "gods",
    "diseño": "design",
    "días de la semana": "weekdays",
    "ecología": "ecology",
    "economía": "economics",
    #  "Edafología": "edaphology",
    "educación": "education",
    "electricidad": "electricity",
    "electromagnetismo": "electromagnetism",
    "electrónica": "electronics",
    #  "Elementos químicos": "chemical elements",
    #  "Emojis": "emoji",
    #  "Emoticonos": "emoticons",
    #  "Enfermedades": "diseases",
    "enología": "oenology",
    #  "Enseñanza": "teaching",
    "entomología": "entomology",
    #  "Equinodermos": "echinoderms",
    #  "Equitación": "horse riding",
    #  "Eras históricas": "historical eras",
    #  "Escultura": "sculpture",
    "esgrima": "fencing",
    #  "Especias": "spices",
    "estaciones": "seasons",
    "estadística": "statistics",
    #  "Estomatología": "stomatology",
    #  "Estética": "esthetic",
    "fabril": "manufacturing",
    #  "Fantasía": "fancy",
    #  "Farmacia": "pharmacy",
    "farmacología": "pharmacology",
    "feminismo": "feminism",
    #  "Festividades": "festivities",
    "ficción": "fiction",
    #  "Ficción fantástica": "fantasy fiction",
    "ficología": "phycology",
    "filatelia": "philately",
    "filosofía": "philosophy",
    "finanzas": "finance",
    "fisiología": "physiology",
    #  "Flores": "flowers",
    #  "Fobias": "phobias",
    "folclore": "folklore",
    "fonética": "phonetics",
    #  "Formas": "shapes",
    "fotografía": "photography",
    #  "Fraccionarios": "fractionals",
    #  "Frutas": "fruit",
    #  "Frutos": "fruits",
    "fármacos": "drugs",
    #  "Física": "physical",
    "fútbol": "soccer",
    #  "Ganadería": "cattle raising",
    #  "Gastronomía": "gastronomy",
    #  "Gentilicios": "gentilicios",
    "genética": "genetics",
    "geografía": "geography",
    "geología": "geology",
    "geometría": "geometry",
    #  "Gimnasia": "gym",
    #  "Glotónimos": "gluttonyms",
    "gramática": "grammar",
    #  "Granjería": "farming",
    #  "Guarismos": "figures",
    "halconería": "falconry",
    "herramientas": "tools",
    "heráldica": "heraldry",
    "hidrología": "hydrology",
    #  "Hierbas": "herbs",
    #  "Higiene": "hygiene",
    #  "Hipocorísticos": "hypocoristic",
    "historia": "history",
    #  "Historieta": "cartoon",
    #  "Hockey sobre césped": "field hockey",
    #  "Hongos": "fungus",
    "horticultura": "horticulture",
    #  "Hostelería": "hostelry",
    #  "Huesos": "bones",
    #  "Humanidades": "humanities",
    "ictiología": "ichthyology",
    #  "Lenguas": "languages",
    "imprenta": "printing",
    #  "Industria": "industry",
    "informática": "computing",
    "ingeniería": "engineering",
    "inmunología": "immunology",
    "insectos": "insects",
    #  "Instrumentos": "instruments",
    #  "Instrumentos de medición": "measurement tools",
    #  "Instrumentos musicales": "musical instruments",
    "interfaz gráfica de usuario": "graphical user interface",
    "internet": "Internet",
    #  "Invertebrados": "invertebrates",
    "islam": "Islam",
    #  "Islas": "islands",
    #  "Judaísmo": "judaism",
    "juegos": "games",
    #  "Juguetes": "toys",
    "lgbt": "LGBT",
    #  "Lagos": "lakes",
    "lexicografía": "lexicography",
    "lingüística": "linguistics",
    "literatura": "literature",
    #  "Logística": "logistics",
    #  "Lucha": "struggle",
    #  "Líquidos": "liquids",
    "lógica": "logic",
    "malabarismo": "juggling",
    "mamíferos": "mammals",
    #  "Mares": "seas",
    "náutica": "nautical",
    "matemática": "mathematics",
    #  "Materia": "subject",
    #  "Materiales": "materials",
    "mecánica": "mechanics",
    "medicina": "medicine",
    #  "Meses": "months",
    #  "Metales": "metals",
    "metalurgia": "metallurgy",
    "meteorología": "meteorology",
    "metrología": "metrology",
    "micología": "mycology",
    "microbiología": "microbiology",
    "milicia": "military",
    #  "Minerales": "minerals",
    "mineralogía": "mineralogy",
    "minería": "mining",
    "mitología": "mythology",
    "mobiliario": "furniture",
    #  "Moluscos": "mollusks",
    #  "Monedas": "coins",
    #  "Moneras": "moneras",
    #  "Montañas": "mountains",
    "muebles": "furniture",
    "música": "music",
    #  "Naipes": "playing cards",
    "natación": "swimming",
    #  "Naturaleza": "nature",
    #  "Nemátodos": "nematodes",
    "neurología": "neurology",
    "numismática": "numismatics",
    #  "Nutrición": "nutrition",
    #  "Números": "numbers",
    "ocultismo": "occultism",
    #  "Ocupaciones": "activities",
    #  "Océanos": "oceans",
    "odontología": "odontology",
    #  "Oficios": "trades",
    "oftalmología": "ophthalmology",
    "ornitología": "ornithology",
    "paleontología": "paleontology",
    "parapsicología": "parapsychology",
    #  "Parentesco": "relationship",
    #  "Partes del día": "parts of the day",
    "países": "countries",
    "peces": "fish",
    #  "Penínsulas": "peninsulas",
    "periodismo": "journalism",
    "perros": "dogs",
    #  "Personajes bíblicos": "biblical characters",
    #  "Personajes ficticios": "fictional characters",
    #  "Personajes históricos": "historical figures",
    "pesca": "fishing",
    #  "Pesos y medidas": "weights and measures",
    #  "Pintura": "paint",
    "planetas": "planets",
    #  "Plantas": "floors",
    #  "Platelmintos": "platyhelminths",
    #  "Platos": "dishes",
    #  "Poblaciones": "populations",
    "poesía": "poetry",
    #  "Política": "policy",
    "pragmática": "pragmatics",
    #  "Prehistoria": "prehistory",
    #  "Vestimenta": "outfit",
    #  "Profesiones": "professions",
    #  "Protistas": "protists",
    #  "Pseudociencias": "pseudosciences",
    "psicología": "psychology",
    "psiquiatría": "psychiatry",
    "química": "chemistry",
    "química orgánica": "organic chemistry",
    #  "Radiocomunicación": "radiocomunication",
    #  "Regiones": "regions",
    #  "Reinos biológicos": "biological kingdoms",
    "religión": "religion",
    #  "Relojería": "watchmaking",
    #  "Reptiles": "reptiles",
    #  "Restaurantes": "restaurants",
    #  "Retórica": "rhetoric",
    "rugby": "rugby",
    #  "Ríos": "rivers",
    #  "Sabores": "flavors",
    "salud": "health",
    #  "Saludos": "greetings",
    #  "Satélites": "satellites",
    #  "Seguridad": "security",
    #  "Semiología": "semiology",
    "semiótica": "semiotics",
    #  "Sentidos": "senses",
    #  "Sentimientos": "feelings",
    "serpientes": "snakes",
    "sexualidad": "sexuality",
    #  "Signos": "signs",
    #  "Signos ortográficos": "spelling signs",
    "silvicultura": "forestry",
    #  "Sociedad": "society",
    "sociología": "sociology",
    #  "Símbolos": "symbols",
    #  "Símbolos alquímicos": "alchemical symbols",
    #  "Símbolos astronómicos": "astronomical symbols",
    #  "Símbolos de unidades monetarias": "symbols of monetary units",
    "tauromaquia": "bullfighting",
    "taxonomía": "taxonomy",
    "teatro": "theater",
    "tecnología": "technology",
    "textiles": "textiles",
    "telecomunicaciones": "telecommunications",
    #  "Telecomunicación": "telecommunication",
    "tenis": "tennis",
    "teología": "theology",
    "termodinámica": "thermodynamics",
    "tiempo": "time",
    "tipografía": "typography",
    "topografía": "topography",
    #  "Topónimos": "toponyms",
    "transporte": "transport",
    #  "Tribus urbanas": "urban tribes",
    "turismo": "tourism",
    #  "Unidades de tiempo": "time units",
    #  "Urbanismo": "town planning",
    #  "Utensilios": "utensils",
    "vegetales": "vegetable",
    "vehículos": "vehicles",
    "verduras": "vegetable",
    #  "Vertebrados": "vertebrates",
    #  "Veterinaria": "vet",
    #  "Virtudes": "virtues",
    #  "Vivienda": "living place",
    #  "Waterpolo": "water polo",
    "zoología": "zoology",
    "zootomía": "zootomy",
    "álgebra": "algebra",
    #  "Árboles": "trees",
    "ética": "ethics",
    "óptica": "optics",
}

NUMBER_TAGS = {
    # "inflect.*" templates
    "singular": "singular",
    "plural": "plural",
    "dual": "dual",
}

GENDER_TAGS = {
    "masculino": "masculine",
    "femenino": "feminine",
    "neutro": "neuter",
}

COMPARISON_TAGS = {
    "positivo": "positive",
    "comparativo": "comparative",
    "superlativo": "superlative",
}

PERSON_TAGS = {
    "primera": "first-person",
    "segunda": "second-person",
    "tercera": "third-person",
}

TENSE_TAGS = {
    "presente": "present",
    "pretérito imperfecto": ["past", "imperfect"],
    "pretérito indefinido": ["indefinite", "preterite"],
    "futuro": "future",
    "condicional": "conditional",
    "pretérito perfecto": ["present", "perfect"],
    "pretérito pluscuamperfecto": "pluperfect",
    "pretérito anterior": ["past", "anterior"],
    "futuro perfecto": ["future", "perfect"],
    "condicional perfecto": ["conditional", "perfect"],
}

VERB_FORM_TAGS = {
    "infinitivo": "infinitive",
    "gerundio": "gerund",
    "participio": "participle",
}

TABLE_TAGS = {
    # Plantilla:es.v
    "formas no personales (verboides)": "impersonal",
    "futuro compuesto": ["future", "compound"],
    "pretérito perfecto compuesto": ["present", "perfect", "compound"],
    "condicional simple": "conditional",
    "condicional compuesto": ["conditional", "compound"],
    "indicativo": "indicative",
    "subjuntivo": "subjunctive",
    "imperativo": "imperative",
    # Plantilla:es.v.conj.ar
    "formas no personales": "impersonal",
    "formas personales": "personal",
    "modo indicativo": "indicative",
    "modo subjuntivo": "subjunctive",
    "modo imperativo": "imperative",
    "pretérito": "preterite",
    # Template:inflect.ine.sust.atem.his.mf-C
    "nominativo": "nominative",
    "vocativo": "vocative",
    "acusativo": "accusative",
    "genitivo": "genitive",
    "ablativo": "ablative",
    "dativo": "dative",
    "locativo": "locative",
    "instrumental": "instrumental",
    # Template:inflect.eu.sust.inanim.prop
    "indefinido": "indefinite",
    "definido": "definite",
    "ergativo": "ergative",
    "comitativo": "comitative",
    "benefactivo": "benefactive",
    "causativo": "causative",
    "inesivo": "inessive",
    "separativo": "separative",
    "adlativo": "allative",
    # "adl. extremo": ["allative"],
    "adverbial": "adverbial",
    "partitivo": "partitive",
    "prolativo": "prolative",
}

SOUND_TAGS = {
    # Template:pron-graf
    "brasilero": "Brazilian",
    "carioca": "Rio-de-Janeiro",
    "gaúcho": "Rio-Grande-De-Sul",
    "europeo": "European",
    "central": "Central",
    "valenciano": "Valencian",
    "baleárico": "Balearic",
    "eclesiástico": "Ecclesiastical",
    "received pronunciation": "Received-Pronunciation",
    "received pronunciation anticuado": ["Received-Pronunciation", "obsolete"],
    "reino unido, obsoleto o dialectal": ["UK", "obsolete", "dialectal"],
    "ee. uu.": "US",
    "australia": "Australia",
    "nueva zelanda": "New-Zealand",
    "california": "California",
    "received pronunciation, general american, canadá": [
        "Received-Pronunciation",
        "General-American",
        "Canada",
    ],
    "australia, nueva zelanda": ["Australia", "New-Zealand"],
    "india": "India",
    "general american": "General-American",
    "general american, canadá": ["General-American", "Canada"],
    "general american, standard canadian": [
        "General-American",
        "Standard-Canadian",
    ],
    "londres": "London",
}

# Template:es.v
ES_V_SUP_TAGS = {
    "adj/adv": ["adjective", "adverb"],
    "part": "participle",
    "part/adj": ["participle", "adjective"],
    "arg/uru": ["Argentina", "Uruguay"],
}


POS_TITLE_TAGS = {
    "sustantiva": "substantive",
    "femenina": "feminine",
    "masculina": "masculine",
    "ordinal": "ordinal",
    "partitiva": "partitive",
    "adjetiva": "adjectival",
}


ALL_TAGS = {
    **NUMBER_TAGS,
    **GENDER_TAGS,
    **COMPARISON_TAGS,
    **PERSON_TAGS,
    **TENSE_TAGS,
    **VERB_FORM_TAGS,
    **TABLE_TAGS,
    **SOUND_TAGS,
    **ES_V_SUP_TAGS,
    **POS_TITLE_TAGS,
    "afirmativo": "affirmative",
    "negativo": "negative",
    "simples": "simple",
    "compuestas": "compound",
    "invariante": "invariable",
}


def translate_raw_tags(data: WordEntry):
    raw_tags = []
    for raw_tag in data.raw_tags:
        lower_raw_tag = raw_tag.lower()
        if lower_raw_tag in ALL_TAGS:
            tr_tag = ALL_TAGS[lower_raw_tag]
            if isinstance(tr_tag, str) and tr_tag not in data.tags:
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                for tag in tr_tag:
                    if tag not in data.tags:
                        data.tags.append(tag)
        elif lower_raw_tag in CSEM_TOPICS and hasattr(data, "topics"):
            data.topics.append(CSEM_TOPICS[lower_raw_tag])
        elif raw_tag in AMBITO_TAGS:
            tr_tag = AMBITO_TAGS[raw_tag]
            if isinstance(tr_tag, str) and tr_tag not in data.tags:
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
