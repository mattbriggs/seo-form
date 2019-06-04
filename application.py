import os
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

import seoonpage as SEO

app = Flask(__name__)
Bootstrap(app)

# Flask

@app.route('/')
def student():
   return render_template('onpage.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      seo_dict=SEO.get_top_ten(result['Markdown'])
      return render_template("result.html", result = seo_dict)

if __name__ == '__main__':
   app.run(debug = True)
