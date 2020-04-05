# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： bookparser
@Description:
@Author: caimmy
@date： 2020/1/13 17:11
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""

import os
import codecs
from utils.apptools import application_path
from gensim.models.word2vec import LineSentence
from gensim.models import Word2Vec
from models import db_session
from models.trunck import OpsKnowledgeDiscovery
import jiagu

# 加载停止词表
stopwords = None
with codecs.open(application_path("ini", "stopwords.txt"), "r", "utf-8") as stop_file:
    stopwords = [w.replace("\r\n", "") for w in stop_file.readlines()]

def read_book_2_words_file(src, desc):
    """
    阅读文本，并生成拆分词汇后构建的段落文件
    :param src: 源文件地址
    :return:
    """
    split_words_contents = []
    with codecs.open(src, "r", encoding="utf-8") as f:
        try:
            raw_content = f.readlines()
            fulltext = "".join([_line.replace("\r\n", "") for _line in raw_content])
            contents = fulltext.split("。")
            # 逐行分词解析
            for raw_sentence in contents:
                words_sentence = [p.strip() for p in jiagu.seg(raw_sentence) if "" != p.strip()]
                _tmp_words_list = []
                for _word in words_sentence:
                    if _word not in stopwords:
                        _tmp_words_list.append(_word)
                split_words_contents.append(" ".join(_tmp_words_list) + "\n")
        except Exception as e:
            print(e)
            print(src)

    if len(split_words_contents) > 0:
        with codecs.open(desc, "w", "utf-8") as desc_file:
            desc_file.writelines(split_words_contents)
    print(f"{src} file translation completed!")


def train_word2vector(src_words_file, modelname):
    keyword_file = src_words_file + ".keywords"
    if not os.path.isfile(keyword_file):
        read_book_2_words_file(src_words_file, keyword_file)
    if os.path.isfile(keyword_file):
        train_sentences = LineSentence(keyword_file)
        model = Word2Vec(train_sentences, window=10, workers=8, sg=1, min_count=3, iter=20, size=200)
        model.save(application_path("ai", "models", "wordvector", modelname + ".model"))
        print("model train finished")
    else:
        print("model train miss!")

def train_knowledgegraph(src, bookname):
    with codecs.open(src, "r", encoding="utf-8") as f:
        try:
            raw_content = f.readlines()
            fulltext = "".join([_line.replace("\r\n", "") for _line in raw_content])
            contents = fulltext.split("。")
            # 逐行分词解析
            for raw_sentence in contents:
                rs = raw_sentence + "。"
                kn_res = jiagu.knowledge(rs)
                if 0 < len(kn_res):
                    for kn_item in kn_res:
                        if 3 == len(kn_item):
                            OpsKnowledgeDiscovery.addItem(db_session, rs, kn_item[0], kn_item[1], kn_item[2], bookname)
                    print(rs)
                    print(kn_res)
                    print("--------------------------------")
        except Exception as e:
            print(e)
            print(src)

    print("analysis finished!")


if "__main__" == __name__:
    # read_book_2_words_file(application_path("data", "books", "二十四史全译", "二十四史全译02 汉书.txt"),
    #                        application_path("data", "books", "二十四史全译", "二十四史全译02汉书keywords.txt"))

    material_name = application_path("data", "books", "二十四史全译", "二十四史全译03_后汉书.txt")
    train_word2vector(material_name, "后汉书")
    # for knowledge test
    train_knowledgegraph(material_name, "后汉书")


    # for most similar in word2vec model test
    # model = Word2Vec.load(application_path("ai", "models", "wordvector", "汉书.model"))
    # print(model.most_similar("刘邦"))

