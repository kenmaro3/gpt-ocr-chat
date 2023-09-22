from paddleocr import PaddleOCR, draw_ocr
from pdf2image import convert_from_path
from PIL import Image
import openai
import os

openai_key = ""
openai.api_key = openai_key

# 環境変数に設定
os.environ['OPENAI_API_KEY'] = openai_key

functions = [
    {
        "name": "rirekisho_information_extraction",
        "description": """これは履歴書のpdfをOCRにかけたものから情報を抽出するための処理です。
        OCRで抽出されたテキストは以下の形式に従います
        (x座標, y座標): {OCRで抽出されたテキスト}
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "氏名"
                },
                "date_of_birth": {
                    "type": "string",
                    "description": "生年月日"
                },
                "age": {
                    "type": "string",
                    "description": "年齢"
                },
                "sex": {
                    "type": "string",
                    "enum": ["男", "女"],
                    "description": "性別",
                },
                "address": {
                    "type": "number",
                    "description": "住所"
                },
                "phone_number": {
                    "type": "string",
                    "description": "電話番号"
                },
                "contact_info": {
                    "type": "string",
                    "description": "連絡先"
                },
                "email": {
                    "type": "string",
                    "description": "メールアドレス"
                },
                "education_history": {
                    "type": "array",
                    "description": "学歴",
                    "items": {
                        "type": "object",
                        "properties": {
                            "year": {
                                "type": "string",
                                "description": "年"
                            },
                            "month": {
                                "type": "number",
                                "description": "月"
                            },
                            "education": {
                                "type": "string",
                                "description": "学歴"
                            },
                        }
                    },
                },
                "job_history": {
                    "type": "array",
                    "description": "職歴",
                    "items": {
                        "type": "object",
                        "properties": {
                            "year": {
                                "type": "string",
                                "description": "年"
                            },
                            "month": {
                                "type": "number",
                                "description": "月"
                            },
                            "job": {
                                "type": "string",
                                "description": "職歴"
                            },
                        }
                    },
                },
                "certificate": {
                    "type": "array",
                    "description": "資格、免許",
                    "items": {
                        "type": "object",
                        "properties": {
                            "year": {
                                "type": "string",
                                "description": "年"
                            },
                            "month": {
                                "type": "number",
                                "description": "月"
                            },
                            "certificate": {
                                "type": "string",
                                "description": "資格免許"
                            },
                        }
                    },
                },
            },
        }
    }
]


def process_pdf(pdf_path):
    # PDFを画像に変換
    images = convert_from_path(pdf_path)

    # OCRモデルの初期化
    ocr = PaddleOCR(lang='japan')
    results = []
    for i, image in enumerate(images, start=1):
        print(f"Processing page {i}")
        image_path = f'{i}.png'
        image.save(image_path, 'PNG')
        result = ocr.ocr(image_path)
        results.append(result)

    ocr_info = ""
    for r in results[0][0]:
        # ocr_info += f"{r[0][0]}: {r[1][0]}\n"
        ocr_info += f"({r[0][0][0]}, {r[0][0][1]}): {r[1][0]}\n"

    messages = [
        {"role": "user", "content": ocr_info}
    ]

    response = openai.ChatCompletion.create(
        # model="gpt-4-0613",
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        temperature=0,
        max_tokens=1024,
        function_call={"name": "rirekisho_information_extraction"}  # auto is default, but we'll be explicit
    )

    res = response["choices"][0]["message"]["function_call"]["arguments"]

    return res
