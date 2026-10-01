{smcl}
{* *! version 1.6.0 01oct2026}{...}
{vieweralsosee "taggenerate" "help taggenerate"}{...}

{title:Title}

{phang}
{bf:tagpreview} {hline 2} Preview attributes stored in tagged variables

{title:Syntax}

{p 8 17 2}
{cmd:tagpreview} {it:column_list}

{title:Description}

{pstd}
{cmd:tagpreview} reads one to ten variables from the dataset currently in
memory. The variables must contain semicolon-delimited {cmd:Key=Value} tags.
It prints one summary across source observations and another summary after the
selected variables are transposed into individual entries. The dataset in
memory is not changed.

{title:Option}

{phang}
{it:column_list} specifies one to ten exact variable names. The names are
entered directly after {cmd:tagpreview}.

{title:Example}

{phang2}{cmd:. use "data/sample_v0.dta", clear}

{phang2}{cmd:. tagpreview Note1 Note2}

{title:Requirements}

{pstd}
Requires Stata 16 or newer and Python 3 configured for Stata. No third-party
Python packages are required. Use {cmd:python query} to inspect the current
Python configuration.
