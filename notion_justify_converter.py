import os
import tempfile
import time
import zipfile
from base64 import b64decode
from selenium import webdriver

def inspect_folder():
    files = os.listdir()
    for f in files:
        if ".zip" in f:
            extract_zip_and_convert(os.path.abspath(f))


def extract_zip_and_convert(path_zip):
    zf = zipfile.ZipFile(path_zip)
    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        for obj in os.listdir(tempdir):
            if ".html" in obj:
                html_path = tempdir + "/" + obj
                add_justify(html_path)
                from_html_to_pdf(html_path, path_zip)


def add_justify(path_file):
    with open(path_file, "r", encoding="utf8") as f:
        contents = f.readlines()
        f.close()

    i = 0
    for line in contents:
        if "</style>" in line:
            break
        i += 1

    index = i - 1

    contents.insert(index + 1, "article {\n")
    contents.insert(index + 2, "    text-align:justify;\n")
    contents.insert(index + 3, "}\n")
    contents.insert(index + 4, "\n")

    with open(path_file, "w", encoding="utf8") as f:
        contents = "".join(contents)
        f.write(contents)
        f.close()


def from_html_to_pdf(path_file, pdf_path):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('file:///' + path_file)
    time.sleep(7)
    a = driver.execute_cdp_cmd(
        "Page.printToPDF", {"path": '', "format": 'A4'})
    pdf_bytes = b64decode(a['data'], validate=True)
    if pdf_bytes[0:4] != b'%PDF':
        raise ValueError('Missing the PDF file signature')
    f = open(pdf_path.replace(".zip", ".pdf"), 'wb')
    f.write(pdf_bytes)
    f.close()
    driver.close()


inspect_folder()
