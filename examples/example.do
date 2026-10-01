version 16.0
clear all
set more off

import delimited using "examples/sample_tags.csv", ///
    clear varnames(1) bindquote(strict) case(preserve)

tagpreview Note1 Note2

taggenerate Product Service Restriction EffectiveDate, ///
    columns(Note1 Note2) ///
    keep(DocID PublishedDate) ///
    saving("examples/generated_entries.dta") replace

list DocID PublishedDate Product Service Restriction EffectiveDate ///
    OriginalCol, noobs abbreviate(20)
