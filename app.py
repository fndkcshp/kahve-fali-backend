from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import base64
import openai

# .env dosyasını yükle
load_dotenv()

# OpenAI API anahtarını .env dosyasından al
fal_api_key = os.getenv("FAL_API_KEY")
fal_client = openai.OpenAI(api_key=fal_api_key)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

@app.route('/fal', methods=['POST'])
def fal():
    try:
        on_foto = request.files.get('on_foto')
        arka_foto = request.files.get('arka_foto')
        tabak_foto = request.files.get('tabak_foto')

        if not on_foto or not arka_foto or not tabak_foto:
            return jsonify({"hata": "Tüm fotoğraflar gönderilmelidir"}), 400

        def kaydet_ve_encode(foto, ad):
            path = os.path.join(UPLOAD_FOLDER, secure_filename(ad))
            foto.save(path)
            return encode_image(path)

        on_b64 = kaydet_ve_encode(on_foto, "on.jpg")
        arka_b64 = kaydet_ve_encode(arka_foto, "arka.jpg")
        tabak_b64 = kaydet_ve_encode(tabak_foto, "tabak.jpg")

        response = fal_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Aşağıda sana üç adet kahve falı fotoğrafı gönderiyorum: "
                                "ilki fincanın içinin ön tarafı, ikincisi arka tarafı, üçüncüsü ise tabaktaki telve. "
                                "Lütfen bu görsellere bakarak gördüğün şekilleri yorumla. "
                                "Yorumlarına şeklin nerede olduğunu (örneğin 'fincanın sağ tarafında', 'tabağın ortasında') belirterek başla. "
                                "Aşk, para, sağlık ve kariyer gibi konuları ele al fakat bunları başlıklar halinde yazma. "
                                "Gerçek bir kahve falı bakan teyze gibi konuş. Gördüğünü anlat. Net göremesen bile görebilmiş gibi yaz."
                            )
                        },
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{on_b64}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{arka_b64}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{tabak_b64}"}}
                    ]
                }
            ],
            max_tokens=1600
        )

        yanit = response.choices[0].message.content
        return jsonify({"fal": yanit})

    except Exception as e:
        print("❌ Fal Hatası:", e)
        return jsonify({"hata": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
