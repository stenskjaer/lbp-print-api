`lbp_print` is a small utility for processing a LombardPress valid XML text with
a relevant XSLT script and compile to PDF with XeLaTeX.


# Installation

Notice that the xslt is included as submodule
of [lbp-print-xslt](https://github.com/lombardpress/lbp-print-xslt), so include
it in cloning by using `--recursive`:
```
git clone --recursive git@github.com:stenskjaer/lbp_print.git
```

If you have already cloned it and just need to install the submodules, run

```
git submodule init && git submodule update
```

## Requirements

The script makes use of *XeLaTeX* and *SaxonHE*. Currently, *Saxon* is included
in the vendor directory, but Java Runtime Environment must be installed to run
it. One might consider going over to
the [pysaxon module](https://github.com/ajelenak/pysaxon).

Aside from that, there are also some internal dependencies, specified in the
`requirements.txt` file.


# TODO

- [ ] Add whitespace cleanup