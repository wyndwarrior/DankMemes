import json
import magic
import mimetypes
import os
import urllib.request

f = open('memes2.json', 'r')
data = json.loads(f.read())
f.close()

captions = []
filenames = []

counter = 1000000
for meme in data[:10]:
	filename = 'reddit/' + str(counter)
	urllib.request.urlretrieve(meme['meme_url'], filename)
	mime_type = magic.from_file(filename, mime=True)
	extension = mimetypes.guess_extension(mime_type)
	if extension in ['.jpeg', '.jpg', '.jpe', '.png']:
		os.rename(filename, filename + extension)

		captions.append({'image_id': counter, 'caption': meme['title']})
		filenames.append({'image_id': counter, 'file_name': filename + extension})
		counter += 1
	else:
		os.remove(filename)

f = open('captions.json', 'w+')
f.write(json.dumps(captions))
f.close()

f = open('filenames.json', 'w+')
f.write(json.dumps(filenames))
f.close()