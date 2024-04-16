import csv
import os
import re
from typing import List, Tuple

from docx import Document
import jionlp as jio


def extract_sentences_from_word(file_path):
    """
    读取word文件，返回文件的句子字符串列表
    参数:
    docx_path (str): docx文件的路径
    返回:
    list[str]: 包含文件中所有句子的字符串列表
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.docx':
        # 读取docx文件
        doc = Document(file_path)
        # 将文档内容合并为一个字符串（按段落连接）
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    # 按照中文句子进行拆分（这里简单地以句号、问号、感叹号结尾作为句子结束标志）
    pattern = re.compile(r'([^。！!？?;；\n]*)([。！!？?;；]|[\r\n]+)')
    matches = pattern.finditer(text)
    chinese_sentences = [match.group(0).rstrip('\n') for match in matches]
    # 过滤掉空字符串和小于10的，防止正则匹配到的符号传入到了模型中
    chinese_sentences = [sentence for sentence in chinese_sentences if sentence and len(sentence.strip()) > 10]

    return chinese_sentences


# if __name__ == '__main__':
#     file_path = "D:\\test.docx"
#     result = extract_sentences_from_word(file_path)
#     for sentence in result:
#         print(sentence)


def swap_and_substitute(sentence: str) -> Tuple[List[str], List[str]]:
    # 这里仅作示例，实际操作中请使用正确的实现
    # 生成噪声句子类型1：邻近汉字换位
    swapped_chars_results = [jio.swap_char_position(sentence, augmentation_num=2)]
    # 生成噪声句子类型2：同音词替换
    homophone_results = [jio.homophone_substitution(sentence, augmentation_num=5)]
    return swapped_chars_results, homophone_results

def create_noised_sentences(file_path: str, output_tsv_path: str):
    source_sentences = extract_sentences_from_word(file_path)
    noised_data: List[List[str]] = []

    for source_sentence in source_sentences:
        swap_results, homophone_results = swap_and_substitute(source_sentence)
        noised_row = [source_sentence] + swap_results + homophone_results
        noised_data.append(noised_row)

    # 写入TSV文件
    with open(output_tsv_path, 'w', newline='', encoding='utf-8') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        for row in noised_data:
            for i in range(len(row[1])):
                writer.writerow([row[1][i], row[0]])

            for j in range(len(row[2])):
                writer.writerow([row[2][j], row[0]])


# 使用方法
input_docx_path = 'D:\\test.docx'
output_tsv_path = 'train5.tsv'

create_noised_sentences(input_docx_path, output_tsv_path)

