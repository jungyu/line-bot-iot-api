import base64
data = open("example.wav", "rb").read()
encoded = base64.b64encode(data)
print(encoded)

with open("base64.txt","wb") as f:
            f.write(encoded)
