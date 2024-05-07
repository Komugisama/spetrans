'''
Author: chentx
Date: 2024-05-06 14:58:06
LastEditTime: 2024-05-07 10:35:05
LastEditors: chentx
Description:
'''

import json
from pathlib import Path
from openai import OpenAI


class Spetrans:
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = None

        if api_key and base_url:
            self.initialize_client()

    def set_api_key(self, api_key):
        self.api_key = api_key

    def set_base_url(self, base_url):
        self.base_url = base_url

    def initialize_client(self):
        if self.api_key and self.base_url:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            raise ValueError(
                "API key and base URL must be set before initializing the client.")

    def get_label_data(self, image_path):
        if not self.client:
            self.initialize_client()

        file_object = self.client.files.create(
            file=Path(image_path), purpose="file-extract")
        file_content = self.client.files.content(file_id=file_object.id).text

        messages = [
            {
                "role": "system",
                "content": "你是一个植物标本图像中的标签OCR识别工具，你可以识别用户上传植物标本图像中的文本信息，并返回符合Darwin Core标准的一层JSON对象字符串，其中包含recordedBy（采集人）、recordNumber（采集号，该信息一般在采集人附近）、verbatimEventDate（采集时间）、country（国家）、stateProvince（省、直辖市、自治区/一级行政区）、county（市/二级行政区）、municipality（县/三级行政区）、verbatimLocality（县以下的详细地点文本）、verbatimLongitude（经度文本，请包含N、E、正负号、度分秒符号）、verbatimLatitude（纬度文本，请包含N、E、正负号、度分秒符号）、verbatimElevation（海拔文本，请包含单位）、habitat（生境/生活环境/栖息地）、eventRemarks（事件备注）、scientificName（学名）、scientificNameAuthorship（学名命名人/学名作者）、identifiedBy（鉴定人）、dateIdentified（鉴定日期），你会优先返回中文信息，如果中文信息不存在，则返回英文信息，如果两类信息都不存在，则返回空，你不需要做任何推测，如实将图像中的信息落入json字符串中就好。",
            },
            {
                "role": "system",
                "content": file_content,
            },
            {"role": "user", "content": "请提取这张照片中的标签信息，返回符合DarwinCore标准的JSON字符串"},
        ]

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=messages,
            temperature=0.3,
        )

        self.client.files.delete(file_id=file_object.id)

        label_data = completion.choices[0].message.content
        return json.loads(label_data[label_data.find('{'):label_data.rfind('}')+1])


def main():
    spetrans = Spetrans()
    spetrans.set_api_key("your api key")
    spetrans.set_base_url(
        "openai api base url e.g.https://api.openai.com/v1/"
    )
    label_data = spetrans.get_label_data("./test_images/02432001.jpg")
    print(label_data)


if __name__ == "__main__":
    main()
