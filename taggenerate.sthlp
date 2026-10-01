{smcl}
{* *! version 1.6.0 01oct2026}{...}
{vieweralsosee "tagpreview" "help tagpreview"}{...}

{title:Title}

{phang}
{bf:taggenerate} {hline 2} Transpose tagged variables and extract attributes

{title:Syntax}

{p 8 17 2}
{cmd:taggenerate} {it:attribute_list}
{cmd:,}
{opt columns(column_list)}
[{opt keep(varlist)} {opt saving(filename)} {opt replace}]

{title:Description}

{pstd}
{cmd:taggenerate} parses the variables explicitly named in {opt columns()}.
Those variables contain semicolon-delimited {cmd:Key=Value} tags in the dataset
currently in memory. Each nonempty tagged cell becomes one observation.
Requested attributes become variables; unselected attributes are stored in
{cmd:EntryRem}. By default, variables not named in {opt columns()} are copied
unchanged. When {opt keep()} is supplied, only the ordinary source variables
listed there are copied.
{cmd:OriginalCol} records the source variable, and {cmd:EntryOriginal}
preserves the original tagged value. The generated observations replace the
dataset in memory.

{pstd}
Unknown attributes are ignored with a warning. If none of the requested
attributes exists, the dataset in memory is left unchanged.

{title:Options}

{phang}
{it:attribute_list} specifies one to ten attributes shown by
{cmd:tagpreview}. The attribute names are entered directly after
{cmd:taggenerate}, before the comma.

{phang}
{opt columns(column_list)} specifies one to ten source variables containing
the tagged entries. Only these variables are parsed. Identifier variables such
as {cmd:DocID} are copied and are never interpreted as tags.

{phang}
{opt keep(varlist)} specifies the ordinary source variables to retain after
the tagged entries are split. Other ordinary source variables are discarded.
A variable cannot appear in both {opt keep()} and {opt columns()}.

{phang}
{opt saving(filename)} saves the generated dataset as a Stata {cmd:.dta} file.
If omitted, the generated dataset remains in memory without being saved.

{phang}
{opt replace} permits replacement of the Stata file named in {opt saving()}.

{title:Example}

{phang2}{cmd:. taggenerate Product Service Restriction EffectiveDate, columns(Note1 Note2)}

{phang2}{cmd:. taggenerate Product Service, columns(Note1 Note2) keep(DocID PublishedDate) saving("data/sample_v0_generated.dta") replace}

{title:Requirements}

{pstd}
Requires Stata 16 or newer and Python 3 configured for Stata. No third-party
Python packages are required. Use {cmd:python query} to inspect the current
Python configuration.
