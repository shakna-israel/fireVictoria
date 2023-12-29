import time

import requests

r = requests.get("https://emergency.vic.gov.au/public/textonly.html")
# TODO: Check status

x = str(r.content).find("<tbody>")
y = str(r.content).find("</tbody>")
content = str(r.content)[x:y]
rebuild = []
for item in [x.strip() for x in content.split("\\n")]:
	if item and not item.startswith("</") and item != '<td class="sidebar-expanded-only">':
		rebuild.append(item)
content = rebuild[3:]
del rebuild

add_title = True
builder = []
t = []
b = []
for item in content:
	if item[0] == '<':
		add_title = False
	else:
		if not add_title:
			builder.append([t, b])
			t = []
			b = []
		add_title = True

	if add_title:
		t.append(item)
	else:
		b.append(item)

ret = []

for item in builder:
	begin = [x.strip() for x in item[0][0].split("-")]
	subdata = {}

	for y in item[0][1:]:
		begin.append(''.join([z.strip() for z in y.split("-")]))

	for y in item[1]:
		pos = y.find("href=")
		if pos > -1:
			sub = y[pos+6:]
			sub = sub[:sub.find("\"")]
			if sub[0] == "#":
				uri = sub[1:]
				if '-' in uri:
					tmp = uri.split("-")
					uri = uri[:uri.find("-")]
					try:
						int(tmp[-1][0])
					except ValueError:
						tmp = tmp[-1]
						begin.append(tmp)

				subdata['id'] = uri
			else:
				linker = sub
				subdata['uri'] = linker

		else:
			if 'lastLocation' in y:
				sub = y[y.find(">") + 1:]
				sub = sub[:sub.find("<")]
				subdata['lastLocation'] = sub
			elif 'lastUpdated' in y:
				sub = y[y.find(">") + 1:]
				sub = sub[:sub.find("<")]
				subdata['lastUpdated'] = int(sub) / 1000
				subdata['lastUpdated'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(subdata['lastUpdated']))
			else:
				raise ValueError(y)

	classification = begin[0]
	status = ' '.join(begin[1:])
	subdata['classification'] = classification
	subdata['status'] = status

	ret.append(subdata)

ret.sort(key=lambda v: v['lastUpdated'])
for item in ret:
	print(item['classification'])
	print(item['id'])
	print(item['lastUpdated'])
	print(item['status'])
	print(item['lastLocation'])
	print()
 	#dont print uri
