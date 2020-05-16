import re


def publish(text):
    text = re.sub(r" +", "", text)
    if re.search(r"\*\*", text, re.I):
        point = None
        while re.search(r"\*{2}", text, re.I):
            if point == "b":
                point = None
                text = re.sub(r"\*{2}", "</b>", text, 1)
            else:
                point = "b"
                text = re.sub(r"\*{2}", "<b>", text, 1)
    if re.search(r"\*", text, re.I):
        point = None
        while re.search(r"\*", text, re.I):
            if point == "i":
                point = None
                text = re.sub(r"\*", "</i>", text, 1)
            else:
                point = "i"
                text = re.sub(r"\*", "<i>", text, 1)
    if re.search(r"\!\(\S*\)\[\S*\]", text, re.I):
        while re.search(r"\!\(\S*\)\[\S*\]", text, re.I):
            start_a, end_a = re.search(r"\[\S*\]", text, re.I).span()
            start_t, end_t = re.search(r"\(\S*\)", text, re.I).span()
            text = re.sub(r"\!\(\S*\)\[\S*\]", '<img src="{}"  alt="{}" />'.format(text[start_a + 1:end_a - 1],
                                                                                   text[start_t + 1:end_t - 1]), text)
    if re.search(r"\[\S*\]\(\S*\)", text, re.I):
        while re.search(r"\[\S*\]\(\S*\)", text, re.I):
            start_a, end_a = re.search(r"\(\S*\)", text, re.I).span()
            start_t, end_t = re.search(r"\[\S*\]", text, re.I).span()
            text = re.sub(r"\[\S*\]\(\S*\)", '<a href="{}">{}</a>'.format(text[start_a + 1:end_a - 1],
                                               text[start_t + 1:end_t - 1]), text)
    return text


class MarkdownAnalyses:
    def __init__(self):
        self.point = None
        self.text = ""

    def analyses(self, text):
        if self.point == "code":
            if re.search(r"\`{3}", text, re.I):
                while re.search(r"\`{3}", text, re.I):
                    if self.point == "code":
                        self.point = None
                        text = re.sub(r"\`{3}", "</pre>", text, 1)
                    else:
                        self.point = "code"
                        text = re.sub(r"\`{3}", "</pre>", text, 1)
            else:
                return text
        if self.point == "list":
            if re.match(r"\s*\-\s*", text, re.I):
                self.point = "list"
                return "<li> ● " + re.sub(r"\s*\-\s*", "", text, 1) + "</li>"
            else:
                self.point = None
        if self.point is None:
            if re.search(r"\`{3}", text, re.I):
                while re.search(r"\`{3}", text, re.I):
                    if self.point == "code":
                        self.point = None
                        text = re.sub(r"\`{3}", "</pre>", text, 1)
                    else:
                        self.point = "code"
                        text = re.sub(r"\`{3}", "<pre>", text, 1)
                return text
            if re.match(r"\s*\-\s*", text, re.I):
                self.point = "list"
                return "<li> ● " + re.sub(r"\s*\-\s*", "", text, 1) + "</li>"
            if re.match(r"(\*|\-){3,}", text, re.I):
                return re.sub(r"(\*|\-){3,}", "<hr>", text)
            if re.match("#", text, re.I):
                times = text.count("#")
                text = re.sub(r"#+", "", text)
                return "<h{}>".format(times) + text + "</{}>".format(times)
            text = publish(text)
            return "<p>" + text + "</p>"

    def html_output(self,text):
        self.text += self.analyses(text)

