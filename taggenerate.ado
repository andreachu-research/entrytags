*! version 1.6.0 01oct2026
program define taggenerate
    version 16.0
    syntax anything(name=attributes id="attribute list") , COLUMNS(string asis) [ KEEP(string asis) SAVING(string) REPLACE ]

    quietly findfile transpose_tags.py
    local pyscript `"`r(fn)'"'

    tempfile input_csv output_csv
    quietly export delimited using `"`input_csv'"', replace

    if `"`keep'"' == "" {
        python script `"`pyscript'"', args("generate" `"`input_csv'"' `attributes' "--columns" `columns' "--output" `"`output_csv'"')
    }
    else {
        python script `"`pyscript'"', args("generate" `"`input_csv'"' `attributes' "--columns" `columns' "--keep" `keep' "--output" `"`output_csv'"')
    }

    quietly import delimited using `"`output_csv'"', clear varnames(1) bindquote(strict) case(preserve)

    if `"`saving'"' != "" {
        if "`replace'" == "" {
            save `"`saving'"'
        }
        else {
            save `"`saving'"', replace
        }
    }
end
