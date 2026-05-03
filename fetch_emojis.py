import urllib.request, base64, json

urls = {
    'like': 'https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f44d.svg',
    'love': 'https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/2764.svg',
    'haha': 'https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f602.svg',
    'wow': 'https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f632.svg',
    'sad': 'https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f622.svg',
    'angry': 'https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f621.svg',
    'care': 'https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f970.svg'
}

res = {}
for k, v in urls.items():
    try:
        data = urllib.request.urlopen(v).read()
        res[k] = f'<img src="data:image/svg+xml;base64,{base64.b64encode(data).decode("utf-8")}" class="w-full h-full object-contain drop-shadow-sm" alt="{k}" />'
    except Exception as e:
        res[k] = 'Error: ' + str(e)
print(json.dumps(res, indent=4))
