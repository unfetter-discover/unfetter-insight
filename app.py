# -*- coding: utf-8 -*-
###############################################################################
# INTRODUCTION                                                                #
###############################################################################
# Unfetter Insight performs natural language processing and analysis for text 
# data to determine and convert to CTI Stix data automatically.
# Version:    1.00
# Author:     Alex Cruz
# Date:       2017_10_04
###############################################################################

from flask import Flask,render_template,request,Markup
import time
import json
import babelfish,os
app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report.html', methods=['POST'])
def report():
    if request.method == 'POST':
        threshold = 0
        coefset = 'technique'
        report = request.files['file']
        fullpath = os.path.join(UPLOAD_FOLDER, report.filename)
        report.save(fullpath)
        plotdata = babelfish.plot_report(fullpath,threshold,coefset)
        tag_results = babelfish.tag_report(fullpath, 0.5, 0, coefset, 'json')
        tagged_report = tag_results[0]['text']
        chart_labels = []
        chart_values = []
        total_size = 100
        for key in tag_results.keys():
            chart_labels.append(tag_results[key]['detected'])
            chart_values.append(str(float(tag_results[key]['confidence'])*100))
            total_size = total_size - float(tag_results[key]['confidence'])*100
        chart_labels.append("Undefined")
        chart_values.append(total_size)
        attack = tag_results[0]['detected']
        return render_template('report.html', chart_values=chart_values, report=Markup(tagged_report), chart_labels=chart_labels,plotdata=plotdata, filename=report.filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080)