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

    def analyses_whole(self, text):
        while re.search(r"\#+\s+.*\n", text):
            t = text[re.search(r"\#+\s+.*\n", text).start():re.search(r"\#+\s+.*\n", text).end()]
            times = t.count("#")
            t = re.sub(r"\#", "", t)
            t = re.sub(r"\s", "", t)
            text = re.sub(r"\#+\s*.*", "<h{}>".format(times) + t + "</h{}>".format(times), text, 1)
        while re.search(r"\n\>\s+.*\n", text):
            t = text[re.search(r"\n\>\s+.*\n", text).start():re.search(r"\n\>\s+.*\n", text).end()]
            t = re.sub(r"\>", "", t)
            t = re.sub(r"\s", "", t)
            text = re.sub(r"\n\>\s*.*", "\n<p><q>" + t + "</q></p>", text, 1)
        while re.search(r"\!\[.*\]\(\S+\)", text):
            start, end = re.search(r"\!\[.*\]\(\S+\)", text).span()
            t = text[start:end]
            start_a, end_a = re.search(r"\(\S+\)", t).span()
            start_t, end_t = re.search(r"\!\[.*\]", t).span()
            text = re.sub(r"\!\[.*\]\(\S+\)", '<img src="{}"  alt="{}" />'.format(t[start_a + 1:end_a - 1],
                                                                      t[start_t + 2:end_t - 1]), text)
        while re.search(r"\[\S*\]\(\S+\)", text):
            t = text[re.search(r"\[\S*\]\(\S+\)", text).start():re.search(r"\[\S*\]\(\S+\)", text).end()]
            start_a, end_a = re.search(r"\(\S+\)", t).span()
            start_t, end_t = re.search(r"\[\S*\]", t).span()
            text = re.sub(r"\[\S*\]\(\S*\)", '<a href="{}">{}</a>'.format(t[start_a + 1:end_a - 1],
                                                                          t[start_t + 1:end_t - 1]), text)

        while re.search(r"\`\`\`.+\`\`\`", text):
            t = text[re.search(r"\`\`\`.+\`\`\`", text).start():re.search(r"\`\`\`.+\`\`\`", text).end()]
            text = re.sub(r"\`\`\`.+\`\`\`", "<code>" + t[3: -3] + "</code>", text, 1)
            break

        while re.search(r"\`\`\`", text):
            if self.point == "pre":
                self.point = None
                text = re.sub(r"\`\`\`", "</pre>", text, 1)
            else:
                self.point = "pre"
                text = re.sub(r"\`\`\`", "</pre>", text, 1)

        lists = text.split("\n")
        text = ""
        for li in lists:
            if li == "":
                continue
            if re.search(r"\<[^\/]*.*\>", li):
                text += li + '\n'
                continue
            if self.point == "/" and re.search(r"\<\[^\/]*\>", li):
                self.point = None
                text += li + '\n'
                continue
            elif self.point == "/":
                text += li + '\n'
                continue
            elif re.search(r"\<\[^\/]*\>", li):
                text += li + '\n'
                self.point = "/"
                continue
            text += "<p>" + li + "</p>" + '\n'

        while re.search(r"\*\*\*", text):
            if self.point == "emi":
                self.point = None
                text = re.sub(r"\*\*\*", "</b></i>", text, 1)
            else:
                self.point = "emi"
                text = re.sub(r"\*\*\*", "<i><b>", text, 1)
        while re.search(r"\*\*", text):
            if self.point == "em":
                self.point = None
                text = re.sub(r"\*\*", "</b>", text, 1)
            else:
                self.point = "em"
                text = re.sub(r"\*\*", "<b>", text, 1)
        while re.search(r"\*", text):
            if self.point == "i":
                self.point = None
                text = re.sub(r"\*", "</i>", text, 1)
            else:
                self.point = "i"
                text = re.sub(r"\*", "<i>", text, 1)

        return text

    def html_output(self, text):
        try:
            with open("resource/web_view.html", "w", encoding="utf-8") as f:
                f.write(self.analyses_whole(text))
        except OSError:
            pass

