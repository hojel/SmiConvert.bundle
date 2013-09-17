import re

LANG_PTN = re.compile("^\s*\.([A-Z]{2}CC) *{ *[Nn]ame:.*; *[Ll]ang: *(\w{2})-(\w{2});.*}", re.M|re.I)
CLASS_PTN = re.compile("<[Pp] [Cc]lass=([A-Z]{2}CC)>")
CLOSETAG_PTN = re.compile("</(BODY|SAMI)>", re.I)

def demuxSMI(smi_sgml):
    langinfo = LANG_PTN.findall(smi_sgml)
    if len(langinfo) < 2:
    	return {'unknown':smi_sgml}
    result = dict()
    lines = smi_sgml.split('\n')
    for capClass, lang, country in langinfo:
        outlines = []
        passLine = True
        for line in lines:
            query = CLASS_PTN.search(line)
            if query:
                curCapClass = query.group(1)
                passLine = True if curCapClass == capClass else False
            if passLine or CLOSETAG_PTN.search(line):
                outlines.append(line)
        #print "%s = %d" % (lang, len(outlines))
        result[lang] = '\n'.join(outlines)
    return result
# vim:sw=4:ts=4:et
