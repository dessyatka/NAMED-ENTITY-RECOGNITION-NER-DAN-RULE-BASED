from flask import Flask, request, jsonify, render_template, url_for, send_file, make_response
import numpy
from spacy import load, displacy
from flaskext.markdown import Markdown
from entities_option import get_entity_options, filter_extraction, case_folding, filtering, getDisease
from ipyleaflet import Map, basemaps, Marker, Popup
from ipywidgets import HTML
import pandas as pd
import re
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map as GMap
import sys, os
from werkzeug.utils import secure_filename

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

UPLOAD_FOLDER = 'input/tempData/'
ALLOWED_EXTENSIONS = set(['csv'])

# import model
link_to_model = "finalModel1"
loaded_model = load(link_to_model)
app = Flask(__name__, static_url_path='/static')
app.config['GOOGLEMAPS_KEY'] = "AIzaSyB0-xj32HsDpMEMekzryOYzLiHD1QPnlOA"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the extension
GoogleMaps(app)
Markdown(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    status = 0
    path = request.path
    return render_template("intro.html", data=path, status=status)

@app.route('/classification', methods=["GET"])
def classify():
    status = 0
    path = request.path
   
    return render_template('klasifikasi.html', data=path, status=status)

@app.route("/classification", methods=["POST"])
def classifyProses():
    status = 1
    input_data = request.form['text']
    doc = loaded_model(str(input_data))
    # options = get_entity_options()
    # print(options)
    # colors = {"lokasi": "linear-gradient(90deg, #aa9cfc, #fc9ce7)"}
    # options = {"colors": colors}
    # result = displacy.render(output_data, style='ent', options=options)
    lokasi = [] 
    korban = []
    penyakit = []
    waktu = []
    for ent in doc.ents:
        if ent.label_ == "lokasi":
    #         print("True")
            lokasi.append(str(ent.text))
        elif ent.label_ == "korban":
            korban.append(str(ent.text))
        elif ent.label_ == "penyakit":
            penyakit.append(str(ent.text))
        elif ent.label_ == "waktu":
            waktu.append(str(ent.text))

    print("\nini lokasi\n", lokasi)
    print("\nini korban\n", korban)
    print("\nini penyakit\n", penyakit)
    print("\nini waktu\n", waktu)

    data = {"lokasi":lokasi, "korban":korban, "penyakit":penyakit, "waktu":waktu}
    ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]
    # print("\n\nini", ents[0])
    # i = 0
    # for i in range(len(doc)):
    #     print("=",[doc[i].text, doc[i].ent_iob_, doc[i].ent_type_])
    # data = {"jln":s_jln, "no":s_no, "bgn":s_bgn, "kel":s_kel, "kec":s_kec, "kab":s_kab, "prov":s_prov, "kpos":s_kpos}
    # splitted_data.append(mystr)
    # extraction = [ext_jln, ext_no, ext_bgn, ext_kel, ext_kec, ext_kab, ext_prov, ext_kpos]
    return render_template("klasifikasiResult.html", word=input_data, status=status, data=data, ents=ents)


@app.route('/visualization', methods=["GET"])
def visualize():
    status = 0
    path = request.path
    return render_template('visualisasi.html', data=path, status=status)
    
@app.route("/visualization", methods=["POST"])
def visualizeProses():
    status = 1
    input_data = request.form['text']
    doc = loaded_model(str(input_data))
    lokasi = [] 
    korban = []
    penyakit = []
    waktu = []
    for ent in doc.ents:
        if ent.label_ == "lokasi":
            lokasi.append(str(ent.text))
        elif ent.label_ == "korban":
            korban.append(str(ent.text))
        elif ent.label_ == "penyakit":
            penyakit.append(str(ent.text))
        elif ent.label_ == "waktu":
            waktu.append(str(ent.text))

    data = {"lokasi":lokasi, "korban":korban, "penyakit":penyakit, "waktu":waktu}

    # data = {"jln":s_jln, "no":s_no, "bgn":s_bgn, "kel":s_kel, "kec":s_kec, "kab":s_kab, "prov":s_prov, "kpos":s_kpos}
    # splitted_data.append(mystr)
    # extraction = [ext_jln, ext_no, ext_bgn, ext_kel, ext_kec, ext_kab, ext_prov, ext_kpos]
    return render_template("visualisasi.html", word=input_data, status=status, data=data)

@app.route('/visualize1', methods=["POST"])
def visualize1():
    path = request.path
   
    error = ""
    if 'file' in request.files:
        filetxt = request.files["file"]
        if filetxt and allowed_file(filetxt.filename):
            filename = secure_filename(filetxt.filename)
            print("ini file name nya =>>>>>>>>>>>>",filename,filetxt.filename)
            filetxt.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            error = "Format file salah"
            return jsonify({ 'code':422, 'message' : 'Format file salah' }), 422
    
    # initiate Map
    # yang diperlukan hanya * ,paragraph,date *
    print(app.config['UPLOAD_FOLDER']+filetxt.filename)
    df_preprocessed = pd.read_csv(app.config['UPLOAD_FOLDER']+filename)
    # checker file.csv must have paragraph & date
    if ('paragraph' not in df_preprocessed.columns and 'date' not in df_preprocessed.columns) :
        print('not okays')
        return jsonify({ 'code':422, 'message' : 'file tidak memiliki kolom paragraph atau date' }), 422
    print('okays')
    df_location = pd.read_csv('output/df_location_newest.csv')
    df_extraction = df_preprocessed
    df_extraction = df_extraction.drop(columns=['category', 'preprocessed'])
    df_extraction['filter'] = df_extraction['paragraph'].apply(filter_extraction)
    df_extraction = df_extraction[df_extraction['filter']==True]

    # do preprocessing paraghraph
    df_extraction['preprocessed'] = df_extraction['paragraph'].apply(filtering)
    df_extraction['preprocessed'] = df_extraction['preprocessed'].apply(case_folding)
    df_extraction['disease'] = df_extraction['preprocessed'].apply(getDisease)
    df_extraction = df_extraction[df_extraction['disease'].notnull()]
    df_extraction = df_extraction.drop_duplicates()

    arrayOfParagraph=df_extraction['preprocessed'].values.tolist()
    arrayOfTime=df_extraction['date'].values.tolist()

    arrayOfParagraphPhrase= []
    arrayOfPhrase=[]
    arrayOfDate=[]
    arrayOfDistrict=[]
    arrayOfDisease=[]
    arrayOfCount=[]
    arrayOfLatitude=[]
    arrayOfLongitude=[]

    for i in range(len(arrayOfParagraph)):
        paragraph = arrayOfParagraph[i]
        # print(paragraph)
        time = arrayOfTime[i]
        # district_retval=None
        # disease_retval=None
        # count_retval=None 
        phrases = paragraph.split(',')
        districts = df_location['district'].values.tolist()
        diseases = ['DBD', 'demam berdarah', 'malaria', 'diare', 'tuberkulosis', 'kusta']
        for phrase in phrases:
            for district in districts:
                for disease in diseases:
                    if (district.lower() in phrase and disease in paragraph):
                        digits = re.findall(r' \d+ ', phrase)
                        if (len(digits)!=0):
                            digit = digits[0]
                            unit_identifier = phrase.split(digit,1)[1]
                            latitude = df_location[df_location['district']==district]['latitude'].values.tolist()[0]
                            longitude = df_location[df_location['district']==district]['longitude'].values.tolist()[0]
                            if (unit_identifier in ['jumlah', 'korban', 'orang', 'warga', 'kasus', 'penyakit', 'pasien', 'penderita', 'terdapat']):
                                arrayOfParagraphPhrase.append(paragraph)
                                arrayOfDate.append(time)
                                arrayOfPhrase.append(phrase)
                                arrayOfDistrict.append(district)
                                arrayOfDisease.append(disease)
                                arrayOfCount.append(digit.replace(' ',''))
                                arrayOfLatitude.append(latitude)
                                arrayOfLongitude.append(longitude)
                            

    d = {'date':arrayOfDate, 'paragraph':arrayOfParagraphPhrase, 'district':arrayOfDistrict, 'disease': arrayOfDisease, 'count': arrayOfCount, 'latitude':arrayOfLatitude, 'longitude': arrayOfLongitude}
    df_visualisation = pd.DataFrame(d, columns=['date','paragraph', 'district', 'disease', 'count', 'latitude', 'longitude'])
    df_visualisation.reset_index(inplace = True, drop=True) #reset index

    markerIterate = []
    marker_count = len(arrayOfDistrict)
    if marker_count > 0:
        for i in range (marker_count):
            mrkr = {
                'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat': arrayOfLatitude[i],
                'lng': arrayOfLongitude[i],
                'infobox': str(arrayOfDate[i])+"</br>"+arrayOfDistrict[i].upper()+"</br>"+str(arrayOfDisease[i])+": "+str(arrayOfCount[i])
            }
            print("->",mrkr)
            markerIterate.append(mrkr)

    # usage of Map from Gmaps
    sndmap = GMap(
        identifier="sndmap",
        varname="sndmap",
        lat=-3.457242,
        lng=114.810318,
        markers=markerIterate,
        style=(
            "height:400px;"
            "width:1000px;"
        ),
        zoom=5
    )
    status = 1
    # try:
    #     # return jsonify({ 'code':200, 'message' : 'Success' ,'data':report[1] }), 200
    #     return jsonify({ 'code':200, 'message' : 'Success' }), 200
    # except e:
    #     return jsonify({ 'code':500, 'message' : 'Success', 'error': str(e) }), 500
    return render_template("visualisasiResult.html", visualize=status, sndmap=sndmap, marker_count=marker_count)

@app.route("/visualize2", methods=["POST"])
def visualize2():
    path = request.path
    status = 1
    error_msg = ''
    time = ''
    input_data = request.form['text']
    output_data = loaded_model(str(input_data))
    options = get_entity_options()
    print(options)
    # colors = {"lokasi": "linear-gradient(90deg, #aa9cfc, #fc9ce7)"}
    # options = {"colors": colors}
    result = displacy.render(output_data, style='ent', options=options)
    
    waktu = []
    for ent in output_data.ents:
        if ent.label_ == "waktu":
            waktu.append(str(ent.text))
    if len(waktu) == 0:
        error_msg = "waktu tidak ditemukan, data tidak bisa di proses"
        print(error_msg)
    elif len(waktu) > 1:
        print("lebih dari satu entitas Waktu ditemukan, mengambil default")
        time = str(waktu[0])

    print("\nini waktu => ", waktu, "\ntime default => ", time)

    # data = {"lokasi":lokasi, "korban":korban, "penyakit":penyakit, "waktu":waktu}
    data = {"waktu":waktu}
    df_location = pd.read_csv('output/df_location_newest.csv')
    arrayOfParagraphPhrase= []
    arrayOfPhrase=[]
    arrayOfDate=[]
    arrayOfDistrict=[]
    arrayOfDisease=[]
    arrayOfCount=[]
    arrayOfLatitude=[]
    arrayOfLongitude=[]

    # for i in range(len(arrayOfParagraph)):
        # paragraph = arrayOfParagraph[i]
    paragraph = input_data
    # time = arrayOfTime[i]
    phrases = paragraph.split(',')
    print(phrases)
    districts = df_location['district'].values.tolist()
    diseases = ['DBD', 'demam berdarah', 'malaria', 'diare', 'tuberkulosis', 'kusta']
    for phrase in phrases:
        for district in districts:
            for disease in diseases:
                if (district.lower() in phrase and disease in paragraph):
                    digits = re.findall(r' \d+ ', phrase)
                    if (len(digits)!=0):
                        digit = digits[0]
                        unit_identifier = phrase.split(digit,1)[1]
                        latitude = df_location[df_location['district']==district]['latitude'].values.tolist()[0]
                        longitude = df_location[df_location['district']==district]['longitude'].values.tolist()[0]
                        if (unit_identifier in ['jumlah', 'korban', 'orang', 'warga', 'kasus', 'penyakit', 'pasien', 'penderita', 'terdapat']):
                            arrayOfParagraphPhrase.append(paragraph)
                            arrayOfDate.append(time)
                            arrayOfPhrase.append(phrase)
                            arrayOfDistrict.append(district)
                            arrayOfDisease.append(disease)
                            arrayOfCount.append(digit.replace(' ',''))
                            arrayOfLatitude.append(latitude)
                            arrayOfLongitude.append(longitude)
                        

    d = {'date':arrayOfDate, 'paragraph':arrayOfParagraphPhrase, 'district':arrayOfDistrict, 'disease': arrayOfDisease, 'count': arrayOfCount, 'latitude':arrayOfLatitude, 'longitude': arrayOfLongitude}
    df_visualisation = pd.DataFrame(d, columns=['date','paragraph', 'district', 'disease', 'count', 'latitude', 'longitude'])
    df_visualisation.reset_index(inplace = True, drop=True) #reset index

    markerIterate = []
    marker_count = len(arrayOfDistrict)
    if marker_count > 1:
        for i in range (marker_count):
            mrkr = {
                'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat': arrayOfLatitude[i],
                'lng': arrayOfLongitude[i],
                'infobox': str(arrayOfDate[i])+"</br>"+arrayOfDistrict[i].upper()+"</br>"+str(arrayOfDisease[i])+": "+str(arrayOfCount[i])
            }
            print("->",mrkr)
            markerIterate.append(mrkr)

    # usage of Map from Gmaps
    sndmap = GMap(
        identifier="sndmap",
        varname="sndmap",
        lat=-3.457242,
        lng=114.810318,
        markers=markerIterate,
        style=(
            "height:400px;"
            "width:1000px;"
        ),
        zoom=5
    )

    return render_template("visualisasiResult.html", word=input_data, visualize=status,
                            htmlPage=result, data=data, time=time, error_msg=error_msg, 
                            sndmap=sndmap, marker_count=marker_count, path=path)

@app.route('/download')
def downloadFile():
    # initiate Map
    df_preprocessed = pd.read_csv('output/df_preprocessed.csv')
    df_location = pd.read_csv('output/df_location_newest.csv')
    df_extraction = df_preprocessed
    df_extraction['filter'] = df_extraction['paragraph'].apply(filter_extraction)
    df_extraction = df_extraction[df_extraction['filter']==True]
    df_extraction = df_extraction.drop(columns=['category', 'preprocessed'])

    # do preprocessing paraghraph
    df_extraction['preprocessed'] = df_extraction['paragraph'].apply(filtering)
    df_extraction['preprocessed'] = df_extraction['preprocessed'].apply(case_folding)
    df_extraction['disease'] = df_extraction['preprocessed'].apply(getDisease)
    df_extraction = df_extraction[df_extraction['disease'].notnull()]
    df_extraction = df_extraction.drop_duplicates()

    arrayOfParagraph=df_extraction['preprocessed'].values.tolist()
    arrayOfTime=df_extraction['date'].values.tolist()

    arrayOfParagraphPhrase= []
    arrayOfPhrase=[]
    arrayOfDate=[]
    arrayOfDistrict=[]
    arrayOfDisease=[]
    arrayOfCount=[]
    arrayOfLatitude=[]
    arrayOfLongitude=[]

    for i in range(len(arrayOfParagraph)):
        paragraph = arrayOfParagraph[i]
        time = arrayOfTime[i]
        # district_retval=None
        # disease_retval=None
        # count_retval=None 
        phrases = paragraph.split(',')
        districts = df_location['district'].values.tolist()
        diseases = ['DBD','demam berdarah', 'malaria', 'diare', 'tuberkulosis']
        for phrase in phrases:
            for district in districts:
                for disease in diseases:
                    if (district.lower() in phrase and disease in paragraph):
                        digits = re.findall(r' \d+ ', phrase)
                        if (len(digits)!=0):
                            digit = digits[0]
                            unit_identifier = phrase.split(digit,1)[1]
                            latitude = df_location[df_location['district']==district]['latitude'].values.tolist()[0]
                            longitude = df_location[df_location['district']==district]['longitude'].values.tolist()[0]
                            if (unit_identifier in ['jumlah','korban','orang', 'warga', 'kasus', 'penyakit', 'pasien', 'penderita','terdapat']):
                                arrayOfParagraphPhrase.append(paragraph)
                                arrayOfDate.append(time)
                                arrayOfPhrase.append(phrase)
                                arrayOfDistrict.append(district)
                                arrayOfDisease.append(disease)
                                arrayOfCount.append(digit.replace(' ',''))
                                arrayOfLatitude.append(latitude)
                                arrayOfLongitude.append(longitude)
                            

    d = {'date':arrayOfDate, 'paragraph':arrayOfParagraphPhrase, 'district':arrayOfDistrict, 'disease': arrayOfDisease, 'count': arrayOfCount, 'latitude':arrayOfLatitude, 'longitude': arrayOfLongitude}
    df_visualisation = pd.DataFrame(d, columns=['date','paragraph', 'district', 'disease', 'count', 'latitude', 'longitude'])
    df_visualisation.reset_index(inplace = True, drop=True) #reset index

    markerIterate = []

    for i in range (len(arrayOfDistrict)):
        # marker = Marker(location=(arrayOfLatitude[i], arrayOfLongitude[i]))
        # m.add_layer(marker)
        # message = HTML()
        # message.value = arrayOfDate[i]+"</br>"+arrayOfDistrict[i].upper()+"</br>"+arrayOfDisease[i]+": "+arrayOfCount[i]
        # marker.popup = message
        # 'infobox': arrayOfDate[i]+"</br>"+arrayOfDistrict[i].upper()+"</br>"+arrayOfDisease[i]+": "+arrayOfCount[i]
        mrkr = {
            'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
            'lat': arrayOfLatitude[i],
            'lng': arrayOfLongitude[i],
            'infobox': arrayOfDate[i]+"</br>"+arrayOfDistrict[i].upper()+"</br>"+arrayOfDisease[i]+": "+arrayOfCount[i]
        }
        print(mrkr)
        markerIterate.append(mrkr)



    # usage of Map from Gmaps
    sndmap = GMap(
        identifier="sndmap",
        varname="sndmap",
        lat=-3.457242,
        lng=114.810318,
        markers=markerIterate,
        style=(
            "height:400px;"
            "width:1000px;"
        ),
        zoom=5
    )
    status = 1
    # usage of Map from ipyleaflet
    # m = Map(
    #     basemap=basemaps.OpenStreetMap.Mapnik,
    #     center=(-3.457242, 114.810318),
    #     zoom=5
    # )

    # marker = Marker(location=(5.55,95.3166667))
    # m.add_layer(marker)
    # message = HTML()
    # message.value = "12 Desember 2020"+"</br>"+"Aceh"+"</br>"+"Kusta"+": "+"343"
    # marker.popup = message

    # for i in range (len(arrayOfDistrict)):
    #     marker = Marker(location=(arrayOfLatitude[i], arrayOfLongitude[i]))
    #     m.add_layer(marker)
    #     message = HTML()
    #     message.value = arrayOfDate[i]+"</br>"+arrayOfDistrict[i].upper()+"</br>"+arrayOfDisease[i]+": "+arrayOfCount[i]
    #     marker.popup = message

    # m.save('output/map_visualization.html', title='Map Visualization Test')

    #For windows you need to use drive name [ex: F:/Example.pdf]
    # path = "output/map_visualization.html"
    # return send_file(path, as_attachment=True)


    # print('data existing')
    # print(data_csv) == some DEBUG here

    # return resp
    return render_template("visualisasiResult.html", visualize=status, sndmap=sndmap)

@app.route('/extraction', methods=["GET"])
def subIndex():
    status = 1
    path = request.path
    return render_template("home.html", status=status, data=path)

@app.route("/extraction", methods=["POST"])
def submit():
    status = 1
    time = ''
    input_data = request.form['text']
    output_data = loaded_model(str(input_data))
    options = get_entity_options()
    path = request.path
    error_msg = ''
    print(options)
    # colors = {"lokasi": "linear-gradient(90deg, #aa9cfc, #fc9ce7)"}
    # options = {"colors": colors}
    result = displacy.render(output_data, style='ent', options=options)
# start from here ----------------------------------
    lokasi = [] 
    korban = []
    penyakit = []
    waktu = []

    for ent in output_data.ents:
        x = ent.text
        if ent.label_ == "lokasi" and x.lower() not in lokasi:
            lokasi.append(x.lower())
        elif ent.label_ == "korban" and x.lower() not in korban:
            korban.append(x.lower())
        elif ent.label_ == "penyakit" and x.lower() not in penyakit:
            penyakit.append(x.lower())
        elif ent.label_ == "waktu" and x.lower() not in waktu:
            waktu.append(x.lower())

    if len(waktu) == 0:
        error_msg = "waktu tidak ditemukan, data tidak bisa di proses"
        print(error_msg)
    elif len(waktu) >= 1:
        error_msg = "mengambil wktu default => " + str(waktu[0])
        time = str(waktu[0])
        print(error_msg)

    print("\nini lokasi\n", lokasi)
    print("\nini korban\n", korban)
    print("\nini penyakit\n", penyakit)
    print("\nini waktu\n", waktu)

    if len(lokasi) > 0 and len(korban) > 0 and len(penyakit) > 0 and len(waktu) > 0:
        print('ok')
        #sum total korban 
        strKorban = ' '.join(korban)
        print(strKorban)
        strKorban = strKorban.replace('.', '')
        digits = re.findall(r'\d+', strKorban)
        print(digits)
        totalSum = 0
        for digit in digits:
            totalSum += int(digit)
        print(totalSum)
        if len(waktu) is 1:
            for loc in lokasi:
                for disease in penyakit:
                    print(loc, disease, waktu, totalSum)
    else :
        print('not ok')

# end here ----------------------------------------
    df_location = pd.read_csv('output/df_location_newest.csv')

    arrayOfLatitude=[]
    arrayOfLongitude=[]
    arrayOfDistrict=[]

    districts = df_location['district'].values.tolist()
    for district in districts:
        if district.lower() in lokasi:
            print(district)
            latitude = df_location[df_location['district']==district]['latitude'].values.tolist()[0]
            longitude = df_location[df_location['district']==district]['longitude'].values.tolist()[0]
            arrayOfLatitude.append(latitude)
            arrayOfLongitude.append(longitude)
            arrayOfDistrict.append(district)
                        
    markerIterate = []
    marker_count = len(arrayOfDistrict)
    if marker_count > 0:
        for i in range (marker_count):
            for p in penyakit:
                mrkr = {
                    'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                    'lat': arrayOfLatitude[i],
                    'lng': arrayOfLongitude[i],
                    'infobox': time+"</br>"+arrayOfDistrict[i].upper()+"</br>"+str(p)+": "+str(totalSum)
                }
                print("->",mrkr)
                markerIterate.append(mrkr)

    # usage of Map from Gmaps
    sndmap = GMap(
        identifier="sndmap",
        varname="sndmap",
        lat=-3.457242,
        lng=114.810318,
        markers=markerIterate,
        style=(
            "height:400px;"
            "width:1000px;"
        ),
        zoom=5
    )

    return render_template("result.html", word=input_data, visualize=status,
                            htmlPage=result, time=time, error_msg=error_msg, 
                            sndmap=sndmap, path=path, marker_count=marker_count)


# @app.route("/")
# def index():
#     return render_template("simple_client.html")

# HTTP Errors handlers
@app.errorhandler(404)
def url_error(e):
    return """
    Wrong URL!
    <pre>{}</pre>""".format(e), 404

@app.errorhandler(500)
def server_error(e):
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    