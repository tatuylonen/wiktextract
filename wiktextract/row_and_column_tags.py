# In certain cases, what 'direction' a header is pointing changes its meaning,
# like with Swahili: there, "c5" means subject concord (subject is class five)
# when the header is in a column, and object concord (object is class five) when
# the header is at the start of a row, in the same table. The only way to
# distinguish these is by direction, which we do using the tables here to make
# explicit replacements of tags in certain languages when they're the row or
# column header, in inflection.py/replace_directional_tags() and rows after
# around 2490.

rowtag_replacements = {
    "Swahili": {
    "class-1": "object-class-1",
    "class-2": "object-class-2",
    "class-3": "object-class-3",
    "class-4": "object-class-4",
    "class-5": "object-class-5",
    "class-6": "object-class-6",
    "class-7": "object-class-7",
    "class-8": "object-class-8",
    "class-9": "object-class-9",
    "class-10": "object-class-10",
    "class-11": "object-class-11",
    "class-12": "object-class-12",
    "class-13": "object-class-13",
    "class-14": "object-class-14",
    "class-15": "object-class-15",
    "class-16": "object-class-16",
    "class-17": "object-class-17",
    "class-18": "object-class-18",
    "first-person": "object-first-person",
    "second-person": "object-second-person",
    "third-person": "object-third-person",
    "singular": "object-singular",
    "plural": "object-plural",
    },
    
}

coltag_replacements = {

}

