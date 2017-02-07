'''
Program to find intertextualities between two texts. Algorithm uses
fuzzywuzzy string matching and special doublet hashing by Zach Schollz
https://github.com/schollz/string_matching in order to lookup fuzzy matches.
This program thus accounts for differing orthography or case/syntactic
variation with the threshold parameter.

This function writes output to linked HTML file.

Author = Christopher Hench
License = MIT
'''


def write_to_html(matches, ntext1, ntext2, f1name, f2name):
    # write html output

    matches = [(" ".join(m[0]), " ".join(m[1])) for m in matches]
    alinks = ''
    blinks = ''
    for i, item in enumerate(matches):

        alinks += '<a href="#intta' + str(i) + '"> [' + str(i) + ']</a>'
        blinks += '<a href="#inttb' + str(i) + '"> [' + str(i) + ']</a>'

        pos = ntext1.find(item[0])
        if pos != -1:
            ntext1 = ntext1[:pos] + '<a name="intta' + str(i) + '"></a><h4 style="color:red;">(' + str(i) + ") " + ntext1[
                pos:pos + len(item[0])] + '<a href="#inttb' + str(i) + '"> (' + f2name + ')</a></h4>' + ntext1[pos + len(item[0]):]

        pos = ntext2.find(item[1])
        if pos != -1:
            ntext2 = ntext2[:pos] + '<a name="inttb' + str(i) + '"></a><h4 style="color:red;">(' + str(i) + ") " + ntext2[
                pos:pos + len(item[1])] + '<a href="#intta' + str(i) + '"> (' + f1name + ')</a></h4>' + ntext2[pos + len(item[1]):]

    html = '''<style type="text/css">
    #wrap {
       width:800px;
       margin:0 auto;
    }
    #left_col {
       float:left;
       width:350px;
    }
    #right_col {
       float:right;
       width:350px;
    }
    #header {
      text-align:center;
      padding:5px;
    }
    </style>

    <div id="header">
    <h1>Inter Text v 0.2</h1>
    <p>''' + f1name.upper() + ': ' + alinks + '''</p>
    <p>''' + f2name.upper() + ': ' + blinks + '''</p>
    </div>

    <div id="wrap">
        <div id="left_col">
            <h2>''' + f1name.upper() + '''</h2>''' + ntext1 + '''
        </div>
        <div id="right_col">
            <h2>''' + f2name.upper() + '''</h2>''' + ntext2 + '''
                </div>
    </div>'''

    with open(f1name + "_" + f2name + ".html", 'w') as f:
        f.write(html)
