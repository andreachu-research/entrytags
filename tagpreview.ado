*! version 1.6.0 01oct2026
program define tagpreview
    version 16.0
    syntax anything(name=columns id="column list")

    quietly findfile transpose_tags.py
    local pyscript `"`r(fn)'"'

    tempfile input_csv
    quietly export delimited using `"`input_csv'"', replace

    python script `"`pyscript'"', args("preview" `"`input_csv'"' `columns')
end
