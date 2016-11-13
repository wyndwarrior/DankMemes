from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from flask import Flask
from flask import send_from_directory, make_response
from flask import render_template, Response, request, redirect, url_for, send_file
from werkzeug import secure_filename
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import math
import os


import tensorflow as tf

from im2txt import configuration
from im2txt import inference_wrapper
from im2txt.inference_utils import caption_generator
from im2txt.inference_utils import vocabulary
from os import listdir
from os.path import isfile, join

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./tmp"

g = tf.Graph()
with g.as_default():
    model = inference_wrapper.InferenceWrapper()
    restore_fn = model.build_graph_from_config(configuration.ModelConfig(), "/home/andrewliu/im2txt/memesmodel/train")
g.finalize()
vocab = vocabulary.Vocabulary("/home/andrewliu/im2txt/data/memes/word_counts.txt")


def draw_caption(img, text, top=False):
	draw = ImageDraw.Draw(img)
	#Find a suitable font size to fill the entire width:
	w = img.size[0]
	s = 60
	while w >= (img.size[0] - 20):
		#font = ImageFont.load_default()
		font = ImageFont.truetype("./static/impact.ttf", size=s)
		w, h = draw.textsize(text, font=font)
		s -= 1
		if s <= 12: break
        h += 5
	#Draw the text multiple times in black to get the outline:
	for x in range(-3, 4):
		for y in range(-3, 4):
			draw_y = y if top else img.size[1] - h + y
			draw.text((10 + x, draw_y), text, font=font, fill='black')
	#Draw the text once more in white:
	draw_y = 0 if top else img.size[1] - h
	draw.text((10, draw_y), text, font=font, fill='white')

@app.route('/')
@app.route('/index')
def index():
	return render_template("index.html")

@app.route('/send_img')
def send_img():
	return send_from_directory('./tmp', 'test.jpg')

import numpy as np

@app.route('/get_meme', methods=['GET', 'POST'])
def get_memes():
	args = request.args.to_dict()

	#These are from the two sliders do whatever you want with them
	range1 = args['range']
	range2 = args['range1']

        imgs = listdir("./static/train/")
        idx = np.random.choice(range(len(imgs)), 1)[0]
        filename = "./static/train/" + imgs[idx]

        with tf.Session(graph=g) as sess:
            restore_fn(sess)
            generator = caption_generator.CaptionGenerator(model, vocab)
            with tf.gfile.GFile(filename, "r") as f:
                image = f.read()
            captions = []
            while len(captions) == 0:
                captions = generator.beam_search(sess, image, np.random.uniform(0.2, 1.2, 1)[0])
            caption = captions[0]
            sentence = [vocab.id_to_word(w) for w in caption.sentence[1:-1]]
            sentence = " ".join(sentence)
            sentence = sentence.replace(" n't", "n't").replace(" 're", "'re").replace(" ?", "?").replace(" .", ".").replace(" 'm", "'m").upper().split(" ")

            cap1 = sentence[:int(len(sentence)/2)]
            cap2 = sentence[int(len(sentence)/2):]
            #sentence = " ".join(sentence)
	#put text here
	sample_txt = sentence#"sample text 3"

	#open image to use here
	img = Image.open(filename)#"./static/kronwall.jpg")


	# resize to height 300
	baseheight = 300
	hpercent = (baseheight/float(img.size[1]))
	wsize = int((float(img.size[0])*float(hpercent)))
	img = img.resize((wsize,baseheight), Image.ANTIALIAS)

	#add caption
	draw_caption(img, " ".join(cap1), top=True)
        draw_caption(img, " ".join(cap2), top=False)
	#save to show. THE FILE NAME HERE WILL BE USED AGAIN AT SEND_IMG
	img.save("./tmp/test.jpg")
	#Response here is never used. Doesnt really matter
	return Response("./tmp/test.jpg")

if __name__ == '__main__':
   app.run(host='0.0.0.0')
