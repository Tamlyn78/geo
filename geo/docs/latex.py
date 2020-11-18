"""Tools for LaTex document processing."""

def master_figure(subfigs, caption='', label=''):
    """"""
    txt = """\\begin{figure}[""" + pos + """]\n\centering\n"""
    txt += subfigs
    txt += """\caption{""" + caption + """}\n""" if caption else ''
    txt += """\label{""" + label + """}\n""" if label else ''
    txt += """\end{figure}\n"""
    return(txt) 

def subfigure(path, width=0.45, pos='!thb', caption='', label=''):
    """"""
    txt = """\t\\begin{subfigure}[t]{""" + str(width) + """\\textwidth}"""
    txt += """\n\t\t\centering"""
    txt += """\n\t\t\captionsetup[subfigure]{width=0.9\\textwidth}"""
    txt += """\n\t\t\includegraphics[width=0.9\\textwidth]{""" + path + """}"""
    txt += """\n\t\t\caption{""" + caption + """}"""
    txt += """\n\t\t\label{""" + label + """}""" if label else ''
    txt += """\n\t\end{subfigure}"""
    return(txt) 

def figure(path=None, subfigures=None, width=1, pos='!thb', caption='', label='', sideways=False):
    """An optional subfigures clause will cause the input text to replace the path to an image."""
    orientation = 'sidewaysfigure' if sideways else 'figure'
    txt = """\\begin{""" + orientation + """}[""" + pos + """]\n\centering\n"""
    if subfigures:
        txt += subfigures + '\n\n'
    else:
        txt += """\includegraphics[width=""" + str(width) + """\\textwidth]{""" + path + """}\n"""
    txt += """\caption{""" + caption + """}\n""" if caption else ''
    txt += """\label{""" + label + """}\n""" if label else ''
    txt += """\end{""" + orientation + """}\n"""
    return(txt) 


def utf2latex(utf, exception=None):
    """Convert a utf character to latex"""
    import latexcodec
    if utf == exception:
        return(utf)
    else:
        latex = utf.encode('latex').decode('utf-8')
        return(latex)
    
def special_character(x, exception=None):
    if x==exception:
        y = x
    elif x=='<':
        y = '$<$'
    elif x=='>':
        y = '$>$'
    elif x=='%':
        y = '\%'
    elif x=='&':
        y='\&'
    else:
        y = x
    return(y)

def csv_to_tabular(path):
    """Convert a csv file to LaTex tabular format."""
    lines = []
    with open(path, 'r') as f:
        for i in f.readlines():
            i = i.strip()
            line = ''.join([special_character(j) for j in i]) + ' \\\\ \n'
            
            lines += [' & '.join(line.split(','))]
    return(lines)
