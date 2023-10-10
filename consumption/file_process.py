import zipfile
import os
import comtypes.client

def get_month_number(raw_string):
    months = {
        "январь": "01",
        "февраль": "02",
        "март": "03",
        "апрель": "04",
        "май": "05",
        "июнь": "06",
        "июль": "07",
        "август": "08",
        "сентябрь": "09",
        "октябрь": "10",
        "ноябрь": "11",
        "декабрь": "12"
    }
    raw_string = raw_string.lower()
    for month_name, month_number in months.items():
        if month_name in raw_string:
            return month_number
    return "Invalid month name"

def file_naming(raw_string):
    month = get_month_number(raw_string)
    year = raw_string.split()[-2]
    name = f'{year}_{month}.pdf'
    return name


def del_early_report(dir_path):
    for filename in os.listdir(dir_path):
        if filename < "2012_01" and os.path.isfile(os.path.join(dir_path, filename)):
            os.remove(os.path.join(dir_path, filename))



def rename_file(dir_path):
    for filename in os.listdir(dir_path):
        if filename.endswith('.pdf'):
            basename = os.path.splitext(filename)[0]
            if basename <= '2013_04':
                os.rename(os.path.join(dir_path, filename), os.path.join(dir_path, basename + '.zip'))


def doc_to_pdf(dir_path):
    wdFormatPDF = 17
    word = comtypes.client.CreateObject('Word.Application')
    for filename in os.listdir(dir_path):
        if filename.endswith('.doc') or filename.endswith('.docx'):
            in_file = os.path.join(os.path.abspath(dir_path), filename)
            out_file = os.path.join(os.path.abspath(dir_path), os.path.splitext(filename)[0] + '.pdf')
            doc = word.Documents.Open(in_file)
            doc.SaveAs(out_file, FileFormat=wdFormatPDF)
            doc.Close()
            os.remove(in_file)
    word.Quit()


def extract_zip(dir_path):
    for filename in os.listdir(dir_path):
        if filename.endswith('.zip'):
            with zipfile.ZipFile(os.path.join(dir_path, filename), 'r') as zip_file:
                zip_file.extractall(os.path.join(dir_path))
                for extracted_file in zip_file.namelist():
                    os.rename(os.path.join(dir_path, extracted_file), os.path.join(dir_path, filename[:-4] + extracted_file[-4:]))            
            os.remove(os.path.join(dir_path, filename))