## Brought to you by:
[![Quantum Leaps](https://www.state-machine.com/attachments/logo_ql_400.png)](https://www.state-machine.com)
<hr>

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/QuantumLeaps/spexygen)](https://github.com/QuantumLeaps/spexygen/releases/latest)
[![GitHub](https://img.shields.io/github/license/QuantumLeaps/spexygen)](https://github.com/QuantumLeaps/spexygen/blob/main/LICENSE)


# Spexygen - Traceable Specifications Based on Doxygen
**Spexygen** is a system for creating formal, [traceable](https://www.state-machine.com/qpc/fsm-qp_tr.html) specifications based on Doxygen, such as:

- functional safety specification ([example](https://www.state-machine.com/qpc/fsm-qp.html))
- requirements specification ([example](https://www.state-machine.com/qpc/srs-qp.html))
- architecture specification ([example](https://www.state-machine.com/qpc/sas-qp.html))
- design specification ([example](https://www.state-machine.com/qpc/sds-qp.html))
- source code ([example](https://www.state-machine.com/qpc/annotated.html))

# Use
Suppose that you have the following directory structure:


```
+---spexygen/          // Spexygen (copy of this repo)
|       . . .
|       Spexyfile      // <== to be included in Doxyfiles
|
+---my_docs/           // example documentation project
|   +---DOC-MAN-QM/    // example document
|   |   +---images/
|   |   +---examples/
|   |       Doxyfile   // @INCLUDE $(SPEXYGEN)/Spexyfile
|   |       qm.dox
|   |       qm_gui.dox
|   |       . . .
|
+---DOC-SRS-QP         // example document
|   |   +---images/
|   |       Doxyfile   // @INCLUDE $(SPEXYGEN)/Spexyfile
|   |       srs.dox
|   |       srs_sect1.dox
|   |       . . .
```

1. Define the `SPEXYGEN` environment variable pointing to the Spexygen installation directory. This could be a relative path with respect to your `Doxyfile`. For example, if you intend to invoke doxygen from the `my_docs/DOC-MAN-QM/` directory, you can define (on Windows):

```
set SPEXYGEN=../../spexygen
```

2. Include the `Spexyfile` at the top of your `Doxyfile`

```
# Doxyfile

@INCLUDE = $(SPEXYGEN)/Spexyfile
. . .
```

3. Run doxygen in this directory:

```
doxygen
```

# Output

## HTML
Spexygen supports HTML output, nicely formatted using the
[doxygen-awesome theme](https://github.com/jothepro/doxygen-awesome-css).
In fact, Spexygen project is cloned from doxygen-awesome. By the nature of HTML,
the HTML ouptut provides the most comprehensive links (incling traceability links).

## PDF
Sexygen supports PDF output, with enhanced customized formatting. The items in the
PDF output is also linked, but the linking is necessarily limited to the single
document.

# Licensing
Spexygen is released under the terms of the permissive
[MIT open source license](LICENSE). Please note that the attribution clause
in the MIT license requires you to preserve the original copyright notice
in all changes and derivate works.


# How to Help this Project?
Please feel free to clone, fork, and make pull requests to improve **spexygen**.
If you like this project, please give it a star (in the upper-right corner of your browser window):

<p align="center"><img src="github-star.jpg"/></p>
