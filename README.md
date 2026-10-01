# entrytags

`entrytags` is a Stata package for previewing and transposing semicolon-delimited
`Key=Value` tags stored in string variables. It provides two commands:

- `tagpreview` lists available attributes and their frequency before and after
  tagged variables are transposed.
- `taggenerate` converts each nonempty tagged cell into an observation and
  extracts up to ten selected attributes into variables.

The commands operate on the dataset currently loaded in Stata. CSV files are
used only as temporary files between Stata and the bundled Python helper.

## Requirements

- Stata 16 or newer
- Python 3 configured for Stata
- No third-party Python packages

Check the Python configuration from Stata:

```stata
python query
```

If Python is not configured, point Stata to the Python executable and restart
Stata:

```stata
python set exec "/path/to/python3", permanently
```

## Install from GitHub

After uploading this folder as the root of a GitHub repository, replace
`GITHUB-USER` below with the repository owner. Replace `entrytags` too if the
repository has a different name.

```stata
net install entrytags, from("https://raw.githubusercontent.com/GITHUB-USER/entrytags/main")
```

To reinstall or upgrade:

```stata
net install entrytags, from("https://raw.githubusercontent.com/GITHUB-USER/entrytags/main") replace
discard
```

To install from a local clone:

```stata
net install entrytags, from("/absolute/path/to/entrytags") replace
```

Confirm the installation:

```stata
which tagpreview
which taggenerate
help tagpreview
```

## Tag format

Each selected source variable may contain one or more semicolon-delimited tags:

```text
Product="Diamond"; Restriction="Import and Re-Export";
```

Attribute names are case-sensitive. Within one cell, an attribute may appear
only once. Values may be quoted or unquoted.

## Preview attributes

Load a dataset, then name one to ten variables containing tags:

```stata
tagpreview Note1 Note2
```

The first summary counts each attribute once per source observation. The second
summary counts attributes after nonempty tagged cells are transposed into
individual entries. `tagpreview` does not change the dataset in memory.

## Generate entries

Attributes appear directly after the command. Tagged source variables belong
in `columns()`:

```stata
taggenerate Product Service Restriction EffectiveDate, ///
    columns(Note1 Note2)
```

By default, all variables not listed in `columns()` are copied to the generated
observations. Use `keep()` to retain only selected ordinary variables:

```stata
taggenerate Product Service Restriction EffectiveDate, ///
    columns(Note1 Note2) ///
    keep(DocID PublishedDate) ///
    saving("generated_entries.dta") replace
```

`taggenerate` replaces the dataset in memory with the generated observations.
The output also contains:

- `EntryRem`: unselected tags from the source cell
- `OriginalCol`: source variable containing the entry
- `EntryOriginal`: complete original tagged value

Unknown requested attributes are ignored with a warning. If none of the
requested attributes exist, no output is generated and the dataset in memory
is left unchanged.

## Example

From a clone of this repository:

```stata
do examples/example.do
```

## Uninstall

```stata
ado uninstall entrytags
```

## Development

Run the Python tests without installing dependencies:

```bash
python3 -m unittest discover -s tests -v
```

Run the Stata installation test from the repository root:

```bash
/path/to/stata -b do tests/test_install.do "$(pwd)"
```

## License

MIT License. See [LICENSE](LICENSE).
