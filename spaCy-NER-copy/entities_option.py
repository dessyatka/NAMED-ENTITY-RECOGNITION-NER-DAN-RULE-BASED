import random, re
import pandas as pd

df_location = pd.read_csv('output/df_location_newest.csv')
districts = df_location['district'].values.tolist()
diseases = ['DBD', 'demam berdarah', 'malaria', 'diare', 'tuberkulosis', 'kusta']
# diseases = ['DBD','demam berdarah', 'malaria', 'diare', 'tuberkulosis']

def get_entity_options(random_colors=False):
    """
    generating color options for visualizing the named entities
    """
    def color_generator(number_of_colors):
        color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                 for i in range(number_of_colors)]
        return color

    # entities = ["GGP", "SO", "TAXON", "CHEBI", "GO", "CL", 
    #             "DNA", "CELL_TYPE", "CELL_LINE", "RNA", "PROTEIN",
    #             "DISEASE", "CHEMICAL",
    #             "CANCER", "ORGAN", "TISSUE", "ORGANISM", "CELL", "AMINO_ACID", "GENE_OR_GENE_PRODUCT", "SIMPLE_CHEMICAL", "ANATOMICAL_SYSTEM", "IMMATERIAL_ANATOMICAL_ENTITY", "MULTI-TISSUE_STRUCTURE", "DEVELOPING_ANATOMICAL_STRUCTURE", "ORGANISM_SUBDIVISION", "CELLULAR_COMPONENT"]
    
    entities = ["KORBAN", "LOKASI", "PENYAKIT", "WAKTU"]
    colors = {"ENT":"#563d7c"}
    
    if random_colors:
        color = color_generator(len(entities))
        for i in range(len(entities)):
            colors[entities[i]] = color[i]
    else:
        entities_cat_1 = {"KORBAN":"#F9E79F", "LOKASI":"#F7DC6F", "PENYAKIT":"#F4D03F", "WAKTU":"#FAD7A0"}
        # entities_cat_2 = {"DNA":"#82E0AA", "CELL_TYPE":"#AED6F1", "CELL_LINE":"#E8DAEF", "RNA":"#82E0AA", "PROTEIN":"#82E0AA"}
        # entities_cat_3 = {"DISEASE":"#D7BDE2", "CHEMICAL":"#D2B4DE"}

        entities_cats = [entities_cat_1]
        for item in entities_cats:
            colors = {**colors, **item}
    
    options = {"ents": entities, "colors": colors}
    
    return options

# the format to send options
# {
#     'ents': ['KORBAN', 'LOKASI', 'PENYAKIT', 'WAKTU'], 
#     'colors': {
#         'ENT': '#563d7c', 
#         'KORBAN': '#688BC2', 
#         'LOKASI': '#DB0500', 
#         'PENYAKIT': '#AA4BD7', 
#         'WAKTU': '#5ED761'
#     }
# }

#case folding
def case_folding(str):
    return str.lower()

def getDistrict(str):
    retval=None
    identifiedDisrict=[]
    for district in districts:
        if (district in str):
            retval=district
            identifiedDisrict.append(district)
    if (len(identifiedDisrict)>0):
        retval=identifiedDisrict
    return retval

def getDisease(str):
    retval=None
    for disease in diseases:
        if (disease in str):
            retval=disease
    return retval

def filtering(str):
    #remove URLs
    str = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', str)   
    #remove \...
    str = re.sub(r'\\[^\s]+',' ',str)  
    #Remove #word
    str = re.sub(r'#([^\s]+)', ' ', str)
    #remove @
    str = re.sub(r'@[^\s]+',' ',str)
    #remove dot
    str = re.sub(r'[.]|_','',str)
    #Remove additional white spaces
    str = re.sub(r'[\s]+', ' ', str)
    #Remove quote
    str = re.sub('"', '', str)
    return str

def filter_extraction(paragraph):
    retval=False
    filtered_paragraph = filtering(paragraph)
    digits = re.findall(r' \d+ ', filtered_paragraph)
    if (len(digits)==0):
        retval=False    
    else:
        if ("kasus" in filtered_paragraph):
            retval=True
        elif ("orang" in filtered_paragraph):
            retval=True
        elif ("jumlah" in filtered_paragraph):
            retval=True
        elif ("pasien" in filtered_paragraph):
            retval=True
        elif ("jiwa" in filtered_paragraph):
            retval=True
        elif ("warga" in filtered_paragraph):
            retval=True
    return retval

def myWorker():
    districts = df_location['district'].values.tolist()
    diseases = ['DBD','demam berdarah', 'malaria', 'diare', 'tuberkulosis']
    return 0

kommen = """
1. perbaiki data latih (jika di rasa perlu)
2. Format klasifikasi mau per entitas atau keseluruhan
3. logic visualize, mau gimana ?
*paraghraf harus ada semua, [date, diseases, place, korban]
    ada semua ? pre-proses kan : lewati -> berikan respon param yg tidak cukup.
*pre-proses untuk district , cek ke data district , ambil satu place saja. jika lebih dari 1 ? 
*pre-proses untuk diseases, ambil satu saja, jika lebih dari 1 ?
*pre-proses untuk korban, jumlahkan keseluruhan yang terdapat dalam satu paraghraph
*kemudian baru set up ke map visualize nya
"""