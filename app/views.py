from flask import Flask
from flask import send_from_directory, make_response
from flask import render_template, Response, request, redirect, url_for, send_file
from werkzeug import secure_filename
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./tmp"

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

@app.route('/get_meme', methods=['GET', 'POST'])
def get_memes():
	args = request.args.to_dict()

	#These are from the two sliders do whatever you want with them
	range1 = args['range']
	range2 = args['range1']

	#put text here
	sample_txt = "sample text 3"

	#open image to use here
	img = Image.open("./static/kronwall.jpg")


	# resize to height 300
	baseheight = 300
	hpercent = (baseheight/float(img.size[1]))
	wsize = int((float(img.size[0])*float(hpercent)))
	img = img.resize((wsize,baseheight), Image.ANTIALIAS)

	#add caption
	draw_caption(img, sample_txt, top=True)

	#save to show. THE FILE NAME HERE WILL BE USED AGAIN AT SEND_IMG
	img.save("./tmp/test.jpg")
	#Response here is never used. Doesnt really matter
	return Response("./tmp/test.jpg")

if __name__ == '__main__':
   app.run()