from softtek_llm.vectorStores import Vector
def parseText(text):
    text_from_file = text.replace('"', "").replace("'", "").replace(
        "\\", ""
    ).replace("  ", " ")

    text_from_file = text_from_file.split("\n")

    text_from_file = [x.strip() for x in text_from_file if x != "" and x != " " and x != "\n" and x != "\t" and x != "\r" and x != "\r\n"]
    text_from_file = [x for x in text_from_file if len(x) > 10]


    # print(len(text_from_file))

    # get paragraphs of 300 words
    paragraphs = []
    paragraph = ""
    for _, text in enumerate(text_from_file):
        text = text.strip()
        if(text != "" or text != " " or text != "\n" or text != "\t" or text != "\r" or text != "\r\n"):
            paragraph += text + " "
        if len(paragraph) >= 2000:
            paragraphs.append(paragraph)
            paragraph = ""
    
            if paragraph != "":
                paragraphs.append(paragraph)
    paragraphs.append(paragraph)
    return paragraphs