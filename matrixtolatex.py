import numpy as np

__ALL__ = ['build3D', 'buildCuboid', 'gen_color_matrix', 'wrap_document', 'wrap_tikzpicture',
           'mkfrontmatrix', 'format_2d_matrix']

definitions = r"""
    \def\x{%d}
    \def\y{%d}
    \def\z{%d}
    \def\yscale{%f}
    \def\zslant{%f}
    \def\xlab{%s}
    \def\ylab{%s}
    \def\zlab{%s}
    \def\gridcol{%s}
    \def\shadecolA{%s}
    \def\shadecolB{%s}"""

template_1 = r"""
    \tikzset{
        grid matrix/.style={
            nodes in empty cells,
            matrix of nodes,
            column sep=-\pgflinewidth, row sep=-\pgflinewidth,
            nodes={
                rectangle,
                draw=gray,
                minimum height=1cm,
                anchor=center,
                align=center,
                text width=1cm,
                text height=2ex,
                text depth=0.5ex,
                inner sep=0pt,
                outer sep=0pt,
            }
        },
        grid matrix/.default=1.2em
    }
    
"""

cube_placehldr = r"""
        \begin{scope}[shift={(-0.5*\z, 0.5 * \x)}]
            \draw[opacity=0] (-0.5* \z, -0.5* \x) rectangle (0.5* \z, 0.5* \x);
        \end{scope}
        
        \begin{scope}[shift={(0.5*\x,-0.5*\y)}]
            \draw[opacity=0] (-0.5* \x,-0.5* \y) rectangle (0.5* \x, 0.5* \y);
        \end{scope}
"""


def mktopmatrix(values):
    return r"""
        
        \begin{scope}[transform canvas={xslant=\zslant, yscale=\yscale, shift={(-0.5*\z, 0.5 * \x)}, },transform shape]
            \draw[color=black, thick] (-0.5* \z,-0.5* \x) rectangle (0.5* \z, 0.5* \x);
            
            \matrix (top) [grid matrix]{
            %s};
            \node [above, rotate=90, text width=\x * 1cm, align=center] at (top.west) {\xlab};
        \end{scope}
    """ % values


def mkfrontmatrix(values):
    return r"""
        \begin{scope}[shift={(-0.5*\z, -0.5 * \y)}]
            \draw[color=black, thick, fill=\shadecolA] (-0.5* \z,-0.5* \y) rectangle (0.5* \z, 0.5* \y);
            
            \matrix (front) [grid matrix]{
            %s};
            \node [below, text width=\z * 1cm, align=center] at (front.south) {\zlab};
            \node [above, rotate=90, text width=\y * 1cm, align=center] at (front.west) {\ylab};
            
            \draw[color=black, thick, fill=none] (-0.5* \z,-0.5* \y) rectangle (0.5* \z, 0.5* \y);
        \end{scope}
    """ % values


def mksidematrix(values):
    return r"""
        
        \begin{scope}[transform canvas={yslant=1/\zslant, xscale=\yscale*\zslant, shift={(0.5*\x,-0.5*\y)}, },transform shape]
            \draw[color=black, thick] (-0.5* \x,-0.5* \y) rectangle (0.5* \x, 0.5* \y);
            
            \matrix (side) [grid matrix]{
            %s};
        \end{scope}
    """ % values


begin_scope = r"""
    \begin{scope}"""

end_scope = r"""
    \end{scope}"""

document_header_begin = r"""
\documentclass[tikz, margin=0mm]{standalone}
\usetikzlibrary{matrix}
\usepackage{mathdots}

\begin{document}
"""

document_header_end = r"""
\end{document}
"""

tikzpicture_begin = r"""
    \begin{tikzpicture}
"""

tikzpicture_end = r"""
    \end{tikzpicture}
"""


def gen_color_matrix(labels, col="none"):
    colors = list()
    for row in labels:
        crow = list()
        for i in row:
            crow.append(col)
        colors.append(crow)
    return colors


def format_2d_matrix(label_matrix, color_matrix=None, col="white", invert=False):
    def format_row(labels, colors):
        s = list()
        for i, (lab, col) in enumerate(zip(labels, colors)):
            s.append("|[fill=%s]| %s" % (col, lab))

        return " & ".join(s)

    if color_matrix is None:
        color_matrix = gen_color_matrix(label_matrix, col)
    r = list()
    for (labRow, colRow) in zip(label_matrix, color_matrix):
        r.append(format_row(labRow, colRow))

    if invert:
        r.reverse()

    r.append("")
    return " \\\\\n".join(r)


matrix_template = r"""
        \begin{scope}[shift={(-0.5*\z + %d, -0.5 * \y + %d)}]
            \matrix (%s) [grid matrix]{
%s};
            \draw[color=black, thick, fill=none] (-0.5* \z,-0.5* \y) rectangle (0.5* \z, 0.5* \y);
        \end{scope}"""


def mkmatrix(shift: int, name: str, values: str):
    return matrix_template % (shift, shift, name, values)


def mkcuboidmatrix(x, y, z, value=""):
    front = np.tile(value, (y, z))
    top = np.tile(value, (x, z))
    side = np.tile(value, (y, x))

    return front, top, side


def buildCuboid(front, top, side, xlab="x", ylab="y", zlab="z", gridcol="black!80", front_col=None, top_col=None,
                side_col=None, declarations=""):
    y, z = np.shape(front)
    x, _ = np.shape(top)

    s = list()
    s.append(definitions % (x, y, z, 0.75, 1.0, xlab, ylab, zlab, gridcol, "white", "black!20"))
    s.append(declarations)
    s.append(template_1)
    s.append(begin_scope)
    s.append(mktopmatrix(format_2d_matrix(top, top_col, invert=True)))
    s.append(mkfrontmatrix(format_2d_matrix(front, front_col)))
    s.append(mksidematrix(format_2d_matrix(side, side_col)))
    s.append(cube_placehldr)
    s.append(end_scope)

    return "".join(s)


def build3D(matrix_3d, xlab="x", ylab="y", zlab="z", gridcol="black!80", col_matrix_3d=None, col=None,
            declarations=""):
    x, y, z = np.shape(matrix_3d)

    s = list()
    s.append(definitions % (x - 1, y, z, 1.0, 1.0, xlab, ylab, zlab, gridcol, "white", "black!20"))
    s.append(declarations)
    s.append(template_1)
    s.append(begin_scope)

    if col_matrix_3d is None:
        col_matrix_3d = np.tile(col, np.shape(matrix_3d))
        if col is None:
            for i in range(col_matrix_3d.shape[0]):
                col_matrix_3d[i,] = "black!%d" % ((15 / (max(1, col_matrix_3d.shape[0] - 1))) * i)

    for i, (matrix_2d, col_matrix_2d) in reversed(list(enumerate(zip(matrix_3d, col_matrix_3d)))):
        if i == 0:
            s.append(mkfrontmatrix(format_2d_matrix(matrix_2d, col_matrix_2d)))
        else:
            s.append(mkmatrix(i, "front_%d" % i, format_2d_matrix(matrix_2d, col_matrix_2d)))

    (front, top, side) = mkcuboidmatrix(x, y, z, "")
    s.append(mktopmatrix(format_2d_matrix(top, col="none, draw=none")))
    s.append(mksidematrix(format_2d_matrix(side, col="none, draw=none")))

    s.append(cube_placehldr)
    s.append(end_scope)

    return "".join(s)


def build2D(matrix_2d, xlab="x", ylab="y", gridcol="black!80", col_matrix_2d=None,
            front_col="white", top_col="white", side_col="white", declarations=""):
    y, z = np.shape(matrix_2d)

    s = list()
    s.append(definitions % (1, y, z, 0.5, 1.0, "", ylab, xlab, gridcol, "white", "black!20"))
    s.append(declarations)
    s.append(template_1)
    s.append(begin_scope)

    if col_matrix_2d is None:
        col_matrix_2d = np.tile(front_col, np.shape(matrix_2d))

    (front, top, side) = mkcuboidmatrix(1, y, z, "")
    s.append(mkfrontmatrix(format_2d_matrix(matrix_2d, col_matrix_2d)))
    s.append(mktopmatrix(format_2d_matrix(top, col=top_col)))
    s.append(mksidematrix(format_2d_matrix(side, col=side_col)))

    s.append(cube_placehldr)
    s.append(end_scope)

    return "".join(s)


def wrap_document(texcode):
    return "".join((document_header_begin, texcode, document_header_end))


def wrap_tikzpicture(texcode):
    return "".join((tikzpicture_begin, texcode, tikzpicture_end))


# example:
if __name__ == "__main__":
    print(wrap_document(wrap_tikzpicture(buildCuboid(
        [  # front
            [r"$a_{1,1,1}$", r"$\cdots$", r"$a_{1,1,i}$"],
            [r"$\vdots$", r"$\ddots$", ""],
            [r"$a_{1,j,1}$", "", r"$a_{1,j,i}$"],
        ],
        [  # top
            [r"$a_{1,1,1}$", r"$\cdots$", r"$a_{k,1,i}$"],
            [r"$\vdots$", r"$\iddots$", ""],
            [r"$a_{k,1,1}$", "", r"$a_{k,1,i}$"],
        ],
        [  # side

            [r"$a_{1,1,i}$", r"$\cdots$", r"$a_{k,1,i}$"],
            [r"$\vdots$", r"$\ddots$", ""],
            [r"$a_{1,j,i}$", "", r"$a_{k,j,i}$"],
        ],
        declarations=r"""
            \pgfdeclareverticalshading{red_green}{100bp}{
                color(0bp)=(red); color(25bp)=(red); color(75bp)=(green); color(100bp)=(green)
            }
            
            \pgfdeclareverticalshading{brown_green}{100bp}{
                color(0bp)=(brown); color(25bp)=(brown); color(75bp)=(green); color(100bp)=(green)
            }
            
            \pgfdeclareverticalshading{brown_red}{100bp}{
                color(0bp)=(brown); color(25bp)=(brown); color(75bp)=(red); color(100bp)=(red)
            }
        """,
        front_col=[
            [r"none", r"green", r"none"],
            [r"red", r"none, shading=red_green, shading angle= -45", r"red"],
            [r"none", r"green", r"none"],
        ],
        top_col=[
            [r"none", r"green", r"none"],
            [r"brown", r"none, shading=brown_green, shading angle= -45", r"brown"],
            [r"none", r"green", r"none"],
        ],
        side_col=[
            [r"none", r"brown", r"none"],
            [r"red", r"none, shading=brown_red, shading angle= -45", r"red"],
            [r"none", r"brown", r"none"],
        ],
        xlab=r"\textcolor{brown}{\textbf{k}}",
        ylab=r"\textcolor{red}{\textbf{j}}",
        zlab=r"\textcolor{green}{\textbf{i}}"))))
