import re, random, time, json
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Optional
from gtts import gTTS
import httpx

import qrcode
import paddleocr
import io
from PIL import Image
import numpy as np

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API platform!"}

@app.get("/bing-wallpaper/")
async def get_bing_wallpaper(itx: int = 0):    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://cn.bing.com/HPImageArchive.aspx?format=js&idx={itx}&n=1&mkt=zh-CN")
        data = response.json()
        bgUri = data['images'][0]['urlbase'] + "_1920x1080.jpg"
        bgUrl = 'https://cn.bing.com' + bgUri
        bgName = re.search(r'/th\?id=OHR\.(.*?\.jpg)', bgUrl).group(1)
        bgText = data['images'][0]['copyright']
    return { "url": bgUrl, "name": bgName, "text": bgText }


@app.get("/generate-qrcode/")
async def generate_qrcode(text: str):
    # 创建一个QRCode对象
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # 向QRCode对象中添加文本
    qr.add_data(text)
    qr.make(fit=True)
    
    # 创建一个PIL图像对象
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 将PIL图像转换为BytesIO对象
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    
    # 返回生成的二维码图像作为响应
    return StreamingResponse(io.BytesIO(img_bytes.getvalue()), media_type="image/png")

@app.get("/google-translate/")
async def google_translate(q: str, sl: str = 'auto', tl: str = 'zh'):
    url = f"http://translate.google.com/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl={sl}&tl={tl}&q={q}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
    result_text = ""
    for sentence in data['sentences']:
        result_text += sentence['trans'] + " "
    return { "result": result_text }

@app.get("/deepl-translate/")
async def deepl_translate_r(q: str, sl: str = 'EN', tl: str = 'ZH'):
    result_text = await deepl_translate(q, sl, tl)
    return { "result": result_text }

async def deepl_translate(text, sourceLang="EN", targetLang="ZH", numberAlternative=0):
    iCount = text.count("i")
    random.seed(time.time())
    id = random.randint(8300000, 8399998) * 1000

    numberAlternative = max(min(3, numberAlternative), 0)

    ts = int(time.time() * 1000)
    if iCount == 0:
        timestamp = ts
    else:
        iCount += 1
        timestamp = ts - ts % iCount + iCount

    postData = {
        "jsonrpc": "2.0",
        "method": "LMT_handle_texts",
        "id": id,
        "params": {
            "texts": [{"text": text, "requestAlternatives": numberAlternative}],
            "splitting": "newlines",
            "lang": {
                "source_lang_user_selected": sourceLang,
                "target_lang": targetLang,
            },
            "timestamp": timestamp,
            "commonJobParams": {
                "wasSpoken": False,
                "transcribe_as": "",
            },
        },
    }
    postDataStr = json.dumps(postData, ensure_ascii=False)

    if (id + 5) % 29 == 0 or (id + 3) % 13 == 0:
        postDataStr = postDataStr.replace('"method":"', '"method" : "', -1)
    else:
        postDataStr = postDataStr.replace('"method":"', '"method": "', -1)

    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "x-app-os-name": "iOS",
        "x-app-os-version": "16.3.0",
        "Accept-Language": "en-US,en;q=0.9",
        # "Accept-Encoding": "gzip, deflate, br", # windows上用requests或者httpx请求会不自动解压gzip，导致结果乱码，原因未知
        "x-app-device": "iPhone13,2",
        "User-Agent": "DeepL-iOS/2.9.1 iOS 16.3.0 (iPhone13,2)",
        "x-app-build": "510265",
        "x-app-version": "2.9.1",
        "Connection": "keep-alive",
    }

    url = f"https://www2.deepl.com/jsonrpc"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=postDataStr.encode('utf-8'), headers=headers)
        respJson = response.json()

    if numberAlternative <= 1:
        targetText = respJson["result"]["texts"][0]["text"]
        return targetText

    targetTextArray = []
    for item in respJson["result"]["texts"][0]["alternatives"]:
        targetTextArray.append(item["text"])
        # print(item["text"])
    return targetTextArray


# 初始化PaddleOCR
ocr = paddleocr.PaddleOCR(lang="ch", use_gpu=False) # 会自动下载模型

@app.post("/paddle_ocr/")
async def paddle_ocr(file: UploadFile):
    # 读取上传的图像文件
    image_data = await file.read()
    
    # 将图像数据转换成PIL图像
    image = Image.open(io.BytesIO(image_data))
    
    # 将图像转换为RGB通道的图像
    image = image.convert("RGB")

    # 将图像数据转换为np.ndarray类型
    image_array = np.array(image)
    
    # 使用PaddleOCR进行文本检测和识别
    results = ocr.ocr(image_array)
    
    # 打印检测结果
    print(results)

    # 解析OCR结果
    text = []
    for result in results:
        for line in result[1]:
            text.append(line[1])

    return {"text": text}


@app.get("/text-to-speech/")
async def text_to_speech(text: str):
    # 使用 gTTS 将文本转换为语音
    tts = gTTS(text, lang='zh')
    
    # 将语音保存为音频文件
    tts.save("text_to_speech.mp3")
    
    # 将生成的语音作为响应返回给客户端
    return StreamingResponse(io.BytesIO(open("text_to_speech.mp3", "rb").read()), media_type="audio/mpeg")