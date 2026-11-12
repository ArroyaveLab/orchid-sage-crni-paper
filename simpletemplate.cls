%% simpletemplate.cls -- a minimal class for scientific papers
%%
%% Options: twocolumn (default), onecolumn, preprint (12pt, double-spaced,
%% one column), linenumbers, supplementary (Supplementary Information:
%% sections, figures, tables, equations, and references numbered S1, S2, ...)
%%
%% \affiliation[key]{Text}    define an affiliation
%% \author[key1,key2]{Name}   add an author with affiliation keys
%% \orcid{id}, \email{addr}, \equalcontrib   apply to the preceding author
%% \abstract{Text}, \keywords{List}  in the preamble
%% \externaldocument[prefix]{file}   import labels from file.aux (xr-hyper);
%%     they print as plain text unless a PDF is given: [prefix]{file}[file.pdf]
%% Bibliography style: unsrtnat unless \bibliographystyle is given
%%
%% The title block is printed automatically at \begin{document}.
%%
%% Based on simple-journal-template by thermoatoms
%% https://github.com/thermoatoms/simple-journal-template

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{simpletemplate}[2026/11/03 v2.2 Simple template for scientific papers]

\newif\if@preprint   \@preprintfalse
\newif\if@linenumbers \@linenumbersfalse
\newif\if@twocol     \@twocoltrue
\newif\if@supplementary \@supplementaryfalse

\DeclareOption{preprint}{\@preprinttrue}
\DeclareOption{linenumbers}{\@linenumberstrue}
\DeclareOption{twocolumn}{\@twocoltrue}
\DeclareOption{onecolumn}{\@twocolfalse}
\DeclareOption{supplementary}{\@supplementarytrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\if@preprint \@twocolfalse \fi

\if@preprint
  \LoadClass[12pt]{article}
\else
  \if@twocol
    \LoadClass[10pt,twocolumn]{article}
  \else
    \LoadClass[10pt]{article}
  \fi
\fi

\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage{mathpazo}
\RequirePackage{microtype}
\RequirePackage{geometry}
\RequirePackage{graphicx}
\RequirePackage{booktabs}
\RequirePackage{caption}
\captionsetup[table]{position=top}
\RequirePackage{amsmath,amssymb}
\RequirePackage{siunitx}
\sisetup{
  per-mode = symbol,
  uncertainty-mode = separate,
  list-final-separator = {, and },
}
\RequirePackage[numbers,sort&compress]{natbib}
\RequirePackage[bottom]{footmisc}
\RequirePackage{xr-hyper}
\RequirePackage{hyperref}
\RequirePackage{xcolor}

\if@twocol
  \geometry{a4paper, margin=1.8cm, columnsep=0.6cm}
\else
  \geometry{a4paper, left=2.5cm, right=2.5cm, top=2.5cm, bottom=2.5cm}
\fi

\hypersetup{
  colorlinks=true,
  linkcolor={blue!60!black},
  citecolor={blue!60!black},
  urlcolor={blue!60!black},
}

\def\stpl@xr@nolink{stpl-xr-nolink}
\let\stpl@externaldocument\externaldocument
\RenewDocumentCommand{\externaldocument}{o o m o}{%
  \stpl@externaldocument[\IfValueT{#1}{#1}][\IfValueT{#2}{#2}]{#3}%
    [\IfValueTF{#4}{#4}{\stpl@xr@nolink}]}
\let\stpl@hyper@link@\hyper@link@
\def\hyper@link@[#1]#2#3#4{%
  \protected@edef\stpl@tempa{#2}%
  \ifx\stpl@tempa\stpl@xr@nolink
    \expandafter\@firstoftwo
  \else
    \expandafter\@secondoftwo
  \fi
  {#4}%
  {\stpl@hyper@link@[#1]{#2}{#3}{#4}}}

\RequirePackage{cleveref}
\crefname{figure}{Fig.}{Figs.}
\Crefname{figure}{Figure}{Figures}
\crefname{table}{Table}{Tables}
\Crefname{table}{Table}{Tables}
\crefname{equation}{Eq.}{Eqs.}
\Crefname{equation}{Equation}{Equations}
\crefname{section}{Section}{Sections}
\Crefname{section}{Section}{Sections}
\crefname{subsection}{Section}{Sections}
\Crefname{subsection}{Section}{Sections}
\crefname{subsubsection}{Section}{Sections}
\Crefname{subsubsection}{Section}{Sections}
\newcommand{\crefrangeconjunction}{--}
\newcommand{\creflastconjunction}{, and\nobreakspace}

\if@preprint
  \RequirePackage{setspace}
  \doublespacing
\fi

\if@linenumbers
  \RequirePackage[mathlines]{lineno}
  \AtBeginDocument{%
    \linenumbers
    \if@twocol
      \def\makeLineNumber{%
        \if@firstcolumn \makeLineNumberLeft \else \makeLineNumberRight \fi}%
    \fi
  }%
\fi

\RequirePackage{titlesec}
\titleformat{\section}{\large\bfseries}{\thesection.}{0.5em}{}
\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection.}{0.5em}{}
\titleformat{\subsubsection}{\normalsize\itshape}{\thesubsubsection.}{0.5em}{}

\if@supplementary
  \renewcommand{\thesection}{S\arabic{section}}
  \renewcommand{\thefigure}{S\arabic{figure}}
  \renewcommand{\thetable}{S\arabic{table}}
  \renewcommand{\theequation}{S\arabic{equation}}
  \renewcommand{\citenumfont}[1]{S#1}
  \renewcommand{\bibnumfmt}[1]{[S#1]}
\fi

\RequirePackage{parskip}

\newif\ifstpl@front
\newif\ifstpl@abstractset
\newif\ifstpl@keywordsset
\newif\ifstpl@titledone

\let\stpl@title@orig\title
\renewcommand{\title}[1]{\global\stpl@fronttrue\stpl@title@orig{#1}}
\renewcommand{\abstract}[1]{%
  \global\stpl@fronttrue\global\stpl@abstractsettrue\gdef\stpl@abstract{#1}}
\let\endabstract\relax
\newcommand{\keywords}[1]{\global\stpl@keywordssettrue\gdef\stpl@keywords{#1}}

\newcommand{\stpl@frontblock}[2]{%
  \begin{center}%
    \begin{minipage}{0.88\textwidth}%
      \small\textbf{#1}~\ignorespaces#2%
    \end{minipage}%
  \end{center}%
  \vskip 1em}

\RequirePackage{orcidlink}

\newcommand{\supplementaryname}{Supplementary Information for}
\newcommand{\correspondingauthortext}{Corresponding author:}
\newcommand{\equalcontribtext}{These authors contributed equally to this work.}
\newcommand{\authorsep}{, }
\newcommand{\authortwosep}{ and }
\newcommand{\authorlastsep}{, and }
\newcommand{\authormarksep}{\kern0.1em}
\newcommand{\affilfont}{\normalsize\itshape}

\newcommand{\stpl@titlenote}[1]{%
  \stepcounter{footnote}%
  \protected@xdef\@thefnmark{\thefootnote}%
  \@makefnmark
  \protected@xdef\@thanks{\@thanks
    \protect\stpl@titlenotetext{\protect\@fnsymbol{\the\c@footnote}}{#1}}}
\newcommand{\stpl@titlenotetext}[2]{%
  \begingroup
    \def\@thefnmark{#1}%
    \ifdefined\H@@footnotetext
      \H@@footnotetext{#2}%
    \else
      \@footnotetext{#2}%
    \fi
  \endgroup}
\newcommand{\stpl@emailnote}[1]{%
  \stpl@titlenote{\correspondingauthortext\space\href{mailto:#1}{#1}}}
\newif\ifstpl@eqdone
\newcommand{\stpl@eqmark}{%
  \ifstpl@eqdone
    \textsuperscript{\normalfont\@fnsymbol{\stpl@eqfn}}%
  \else
    \global\stpl@eqdonetrue
    \stpl@titlenote{\equalcontribtext}%
    \xdef\stpl@eqfn{\the\c@footnote}%
  \fi}

\ExplSyntaxOn

\int_new:N   \g__stpl_author_int
\int_new:N   \g__stpl_affil_int
\prop_new:N  \g__stpl_affil_prop
\seq_new:N   \g__stpl_affil_seq
\prop_new:N  \g__stpl_number_prop
\seq_new:N   \g__stpl_used_seq
\int_new:N   \g__stpl_used_int
\bool_new:N  \g__stpl_any_keys_bool
\seq_new:N   \g__stpl_names_seq
\seq_new:N   \l__stpl_items_seq
\clist_new:N \l__stpl_nums_clist
\tl_new:N    \l__stpl_tmp_tl

\msg_new:nnn { simpletemplate } { duplicate-key }
  { Affiliation~key~'#1'~is~defined~more~than~once. }
\msg_new:nnn { simpletemplate } { undefined-key }
  { Affiliation~key~'#2'~used~by~author~no.~#1~is~not~defined. }
\msg_new:nnn { simpletemplate } { unused-affil }
  {
    Affiliation~'#1'~is~not~used~by~any~\iow_char:N \\author~
    and~will~not~be~printed.
  }
\msg_new:nnn { simpletemplate } { no-author }
  { \iow_char:N \\#1~used~before~any~\iow_char:N \\author;~ignored. }

\cs_new:Npn \__stpl_key:nn #1#2 { g__stpl_ #1 _ #2 _tl }

\RenewDocumentCommand \author { o m }
  {
    \int_gincr:N \g__stpl_author_int
    \global \stpl@fronttrue
    \tl_gclear_new:c  { \__stpl_key:nn { name }  { \int_use:N \g__stpl_author_int } }
    \tl_gset:cn       { \__stpl_key:nn { name }  { \int_use:N \g__stpl_author_int } } {#2}
    \tl_gclear_new:c  { \__stpl_key:nn { orcid } { \int_use:N \g__stpl_author_int } }
    \tl_gclear_new:c  { \__stpl_key:nn { email } { \int_use:N \g__stpl_author_int } }
    \tl_gclear_new:c  { \__stpl_key:nn { eq }    { \int_use:N \g__stpl_author_int } }
    \clist_gclear_new:c { g__stpl_keys_ \int_use:N \g__stpl_author_int _clist }
    \clist_gclear_new:c { g__stpl_nums_ \int_use:N \g__stpl_author_int _clist }
    \IfValueT {#1}
      { \clist_gset:cn { g__stpl_keys_ \int_use:N \g__stpl_author_int _clist } {#1} }
    \seq_gput_right:Nn \g__stpl_names_seq {#2}
    \cs_gset:Npx \@author { \seq_use:Nn \g__stpl_names_seq { ,~ } }
  }

\cs_new_protected:Npn \__stpl_set_field:nn #1#2
  {
    \int_compare:nNnTF \g__stpl_author_int = 0
      { \msg_warning:nnn { simpletemplate } { no-author } {#1} }
      { \tl_gset:cn { \__stpl_key:nn {#1} { \int_use:N \g__stpl_author_int } } {#2} }
  }

\NewDocumentCommand \orcid        { m } { \__stpl_set_field:nn { orcid } {#1} }
\NewDocumentCommand \email        { m } { \__stpl_set_field:nn { email } {#1} }
\NewDocumentCommand \equalcontrib { }   { \__stpl_set_field:nn { eq } { yes } }

\NewDocumentCommand \affiliation { o m }
  {
    \IfNoValueTF {#1}
      { \tl_set:Nx \l__stpl_tmp_tl { __stpl_auto_ \int_eval:n { \g__stpl_affil_int + 1 } } }
      { \tl_set:Nx \l__stpl_tmp_tl { \tl_trim_spaces:n {#1} } }
    \prop_if_in:NVTF \g__stpl_affil_prop \l__stpl_tmp_tl
      { \msg_error:nnV { simpletemplate } { duplicate-key } \l__stpl_tmp_tl }
      {
        \int_gincr:N \g__stpl_affil_int
        \prop_gput:NVn \g__stpl_affil_prop \l__stpl_tmp_tl {#2}
        \seq_gput_right:NV \g__stpl_affil_seq \l__stpl_tmp_tl
      }
  }

\cs_new_protected:Npn \__stpl_resolve_affils:
  {
    \prop_gclear:N \g__stpl_number_prop
    \seq_gclear:N  \g__stpl_used_seq
    \int_gzero:N   \g__stpl_used_int
    \bool_gset_false:N \g__stpl_any_keys_bool
    \int_step_inline:nn { \g__stpl_author_int }
      {
        \clist_clear:N \l__stpl_nums_clist
        \clist_map_inline:cn { g__stpl_keys_ ##1 _clist }
          {
            \bool_gset_true:N \g__stpl_any_keys_bool
            \prop_if_in:NnTF \g__stpl_affil_prop {####1}
              {
                \prop_get:NnNF \g__stpl_number_prop {####1} \l__stpl_tmp_tl
                  {
                    \int_gincr:N \g__stpl_used_int
                    \tl_set:Nx \l__stpl_tmp_tl { \int_use:N \g__stpl_used_int }
                    \prop_gput:NnV \g__stpl_number_prop {####1} \l__stpl_tmp_tl
                    \seq_gput_right:Nn \g__stpl_used_seq {####1}
                  }
                \clist_if_in:NVF \l__stpl_nums_clist \l__stpl_tmp_tl
                  { \clist_put_right:NV \l__stpl_nums_clist \l__stpl_tmp_tl }
              }
              { \msg_error:nnnn { simpletemplate } { undefined-key } {##1} {####1} }
          }
        \clist_sort:Nn \l__stpl_nums_clist
          {
            \int_compare:nNnTF {####1} > {####2}
              { \sort_return_swapped: } { \sort_return_same: }
          }
        \clist_gset_eq:cN { g__stpl_nums_ ##1 _clist } \l__stpl_nums_clist
      }
    \bool_if:NT \g__stpl_any_keys_bool
      {
        \seq_map_inline:Nn \g__stpl_affil_seq
          {
            \prop_if_in:NnF \g__stpl_number_prop {##1}
              {
                \msg_warning:nne { simpletemplate } { unused-affil }
                  { \prop_item:Nn \g__stpl_affil_prop {##1} }
              }
          }
      }
  }

\cs_new_protected:Npn \__stpl_typeset_authors:
  {
    \__stpl_resolve_affils:
    \seq_clear:N \l__stpl_items_seq
    \int_step_inline:nn { \g__stpl_author_int }
      {
        \seq_put_right:Nx \l__stpl_items_seq
          {
            \exp_not:v { \__stpl_key:nn { name } {##1} }
            \tl_if_empty:cF { \__stpl_key:nn { orcid } {##1} }
              {
                \exp_not:N \authormarksep
                \exp_not:N \orcidlink { \exp_not:v { \__stpl_key:nn { orcid } {##1} } }
              }
            \bool_lazy_any:nT
              {
                { ! \clist_if_empty_p:c { g__stpl_nums_ ##1 _clist } }
                { ! \tl_if_empty_p:c { \__stpl_key:nn { email } {##1} } }
                { ! \tl_if_empty_p:c { \__stpl_key:nn { eq } {##1} } }
              }
              { \exp_not:N \authormarksep }
            \clist_if_empty:cF { g__stpl_nums_ ##1 _clist }
              {
                \exp_not:N \ensuremath
                  { ^ { \clist_use:cn { g__stpl_nums_ ##1 _clist } { , } } }
              }
            \bool_lazy_and:nnT
              { ! \clist_if_empty_p:c { g__stpl_nums_ ##1 _clist } }
              {
                \bool_lazy_or_p:nn
                  { ! \tl_if_empty_p:c { \__stpl_key:nn { eq } {##1} } }
                  { ! \tl_if_empty_p:c { \__stpl_key:nn { email } {##1} } }
              }
              { \exp_not:N \textsuperscript { , } }
            \tl_if_empty:cF { \__stpl_key:nn { email } {##1} }
              {
                \exp_not:N \stpl@emailnote { \exp_not:v { \__stpl_key:nn { email } {##1} } }
                \tl_if_empty:cF { \__stpl_key:nn { eq } {##1} }
                  { \exp_not:N \textsuperscript { , } }
              }
            \tl_if_empty:cF { \__stpl_key:nn { eq } {##1} }
              { \exp_not:N \stpl@eqmark }
          }
      }
    \seq_use:Nnnn \l__stpl_items_seq
      { \authortwosep } { \authorsep } { \authorlastsep }
  }

\cs_new_protected:Npn \__stpl_typeset_affils:
  {
    \int_compare:nNnT \g__stpl_affil_int > 0
      {
        \vskip 6pt
        \group_begin:
          \large
          \dim_set_eq:NN \l_tmpa_dim \baselineskip
          \affilfont
          \dim_set_eq:NN \baselineskip \l_tmpa_dim
          \bool_if:NTF \g__stpl_any_keys_bool
            {
              \seq_map_indexed_inline:Nn \g__stpl_used_seq
                {
                  \ensuremath { ^ {##1} }
                  \prop_item:Nn \g__stpl_affil_prop {##2}
                  \par
                }
            }
            {
              \seq_map_inline:Nn \g__stpl_affil_seq
                { \prop_item:Nn \g__stpl_affil_prop {##1} \par }
            }
        \group_end:
      }
  }

\AtBeginDocument
  {
    \int_compare:nNnT \g__stpl_author_int > 0
      { \hypersetup { pdfauthor = { \@author } } }
  }

\cs_new_eq:NN \stpl@authors      \__stpl_typeset_authors:
\cs_new_eq:NN \stpl@affiliations \__stpl_typeset_affils:

\ExplSyntaxOff

\newcommand{\stpl@titleprefix}{%
  \if@supplementary {\Large\supplementaryname\par}\vskip 0.5em\fi}

\newcommand{\stpl@maketitle}{%
  \setcounter{footnote}{0}%
  \global\stpl@eqdonefalse
  \renewcommand{\thefootnote}{\fnsymbol{footnote}}%
  \begingroup
  \if@twocol
    \twocolumn[{%
      \centering
      \stpl@titleprefix
      {\LARGE\bfseries\@title\par}\vskip 0.8em
      {\large\stpl@authors\par}\stpl@affiliations\vskip 0.4em
      {\small\@date\par}\vskip 1.2em
      \ifstpl@abstractset
        \begin{center}\leavevmode\vbox{\hsize=0.88\textwidth
          \leftskip\z@skip \rightskip\z@skip \parfillskip\@flushglue
          \parindent\z@
          \small\textbf{Abstract.}~\ignorespaces\stpl@abstract}\end{center}\vskip 1em
      \fi
      \ifstpl@keywordsset \stpl@frontblock{Keywords:}{\stpl@keywords}\fi
    }]%
  \else
    \global\@topnum\z@
    \begin{center}
      \parskip\z@skip
      \stpl@titleprefix
      {\LARGE\bfseries\@title\par}\vskip 0.8em
      {\large\stpl@authors\par}\stpl@affiliations\vskip 0.4em
      {\small\@date\par}
    \end{center}
    \vskip 1em
  \fi
  \endgroup
  \@thanks
  \global\let\@thanks\@empty
  \setcounter{footnote}{0}%
  \renewcommand{\thefootnote}{\arabic{footnote}}%
  \if@twocol\else
    \ifstpl@abstractset \stpl@frontblock{Abstract.}{\stpl@abstract}\fi
    \ifstpl@keywordsset \stpl@frontblock{Keywords:}{\stpl@keywords}\fi
  \fi}

\AddToHook{begindocument/end}{%
  \ifstpl@front \stpl@maketitle \fi
  \global\stpl@titledonetrue
  \renewcommand{\maketitle}{%
    \ClassWarning{simpletemplate}{\string\maketitle\space is not needed:
      the title is printed\MessageBreak automatically at \string\begin{document}}}%
  \renewcommand{\abstract}{%
    \ClassError{simpletemplate}{The abstract goes in the preamble}%
      {Write \string\abstract{...} before \string\begin{document}.}%
    \ifx\@currenvir\stpl@absname
      \setbox\z@\vbox\bgroup
    \else
      \expandafter\@gobble
    \fi}%
  \def\endabstract{\egroup}%
  \renewcommand{\keywords}[1]{%
    \ClassError{simpletemplate}{Keywords go in the preamble}%
      {Write \string\keywords{...} before \string\begin{document}.}}}
\def\stpl@absname{abstract}

\newif\ifstpl@bibstyle
\newif\ifstpl@bibdata
\let\stpl@bibliographystyle@orig\bibliographystyle
\renewcommand{\bibliographystyle}[1]{%
  \global\stpl@bibstyletrue\stpl@bibliographystyle@orig{#1}}
\let\stpl@bibliography@orig\bibliography
\renewcommand{\bibliography}[1]{%
  \global\stpl@bibdatatrue\stpl@bibliography@orig{#1}}
\AtEndDocument{%
  \ifstpl@bibdata\ifstpl@bibstyle\else
    \if@filesw\immediate\write\@auxout{\string\bibstyle{unsrtnat}}\fi
  \fi\fi}

\providecommand{\doi}[1]{{\urlstyle{same}\href{https://doi.org/#1}{doi:\nolinkurl{#1}}}}
\providecommand{\url}[1]{\texttt{#1}}

\endinput