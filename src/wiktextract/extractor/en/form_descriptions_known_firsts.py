# Temporary file to avoid circular dependencies between form_descriptions
# and english_words
from .taxondata import known_firsts

# Add some additional known taxonomic species names.  Adding the family name
# here may be the answer if a taxonomic name goes in "alt".
known_firsts.update(
    [
        "Aglaope",
        "Albulidae",
        "Alphonsus",
        "Artipus",
        "Bubo",
        "Busycotypus",
        "Callistosporium",
        "Caprobrotus",
        "Chaetodontinae",
        "Chalchicuautla",
        "Citriobatus",
        "Citrofortunella",
        "Coriandum",
        "Eriophyes",
        "Fulgar",
        "Lagerstomia",
        "Lyssavirus",
        "Maulisa",
        "Megamimivirinae",
        "Mercenaria",
        "Monetaria",
        "Mugillidae",
        "Ogcocephalus",
        "Onchorhynchus",
        "Plebidonax",
        "Poncirus",
        "Rugosomyces",
        "Tanagra",
    ]
)
# Some starts are only recognized as exact known species due to too many false
# positives
known_firsts = known_firsts - set(["The"])
