import json
import magic
import mimetypes
import os
import urllib

f = open('meme_scraper/memes.json', 'r')
data = json.loads(f.read())
f.close()

captions = []
filenames = []

counter = 1000000
for meme in data:
	filename = 'reddit/' + str(counter)
	success = False
	for i in range(3):
		try:
			urllib.urlretrieve(meme['meme_url'], filename)
		except Exception as e:
			print e, meme['meme_url']
			continue
		success = True
		break
	if not success:
		continue
	mime_type = magic.from_file(filename, mime=True)
	extension = mimetypes.guess_extension(mime_type)
	if extension in ['.jpeg', '.jpg', '.jpe', '.png']:
		if extension == '.jpe':
			extension = '.jpg'
		os.rename(filename, filename + extension)

		captions.append({'image_id': counter, 'caption': meme['title']})
		filenames.append({'image_id': counter, 'file_name': filename + extension})
		counter += 1
	else:
		os.remove(filename)

	if counter %100 == 0:
		print counter
		f = open('captions.json', 'w+')
		f.write(json.dumps(captions))
		f.close()

		f = open('filenames.json', 'w+')
		f.write(json.dumps(filenames))
		f.close()
