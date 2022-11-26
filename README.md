# Tdb Overview

Tdb “Text DataBase” format is a plain text human readable typed database
storage format.

Tdb provides a superior alternative to CSV. In particular, Tdb tables are
named and Tdb fields are strictly typed. Also, there is a clear distinction
between field names and data values, and strings respect whitespace
(including newlines) and have no problems with commas, quotes, etc.
Perhaps best of all, a single Tdb file may contain one—or more—tables.

- [Datatypes](#datatypes)
- [Examples](#examples)
    - [CSV](#csv)
    - [Database](#database)
    - [Minimal Tdb Files](#minimal-tdb-files)
    - [Metadata](#metadata)
- [Libraries](#libraries)
	- [Go](#go)
	- [Python](#py)
- [BNF](#bnf)
- [Supplementary](#supplementary)
    - [Vim Support](#vim-support)
    - [Tdb Logo](#tdb-logo)

## Datatypes

Tdb supports the following seven built-in datatypes.

|**Type**<a name="table-of-built-in-types"></a>|**Sentinal**|**Example(s)**|**Notes**|
|-----------|----------------------|--|--|
|`bool`     ||`F` `T`|No sentinal. A Tdb reader should also accept 'f', 'N', 'n', 't', 'Y', 'y', '0', '1'|
|`bytes`    ||`(20AC 65 66 48)`|No sentinal; use `()` empty. There must be an even number of case-insensitive hex digits; whitespace (spaces, newlines, etc.) optional.|
|`date`     |`1808-08-08`   |`2022-04-01`|Basic ISO8601 YYYY-MM-DD format.|
|`datetime` |`1808-08-08T08:08:08`|`2022-04-01T16:11:51`|ISO8601 YYYY-MM-DDTHH[:MM[:SS]] format; 1-sec resolution no timezone support.|
|`int`      |`-1808080808`|`-192` `+234` `7891409`|Standard integers with optional sign.|
|`real`     |`-1808080808.0808`|`0.15` `0.7e-9` `2245.389`|Standard and scientific notation.|
|`str`      ||`<Some text which may include newlines>`|No sentinal; use `<>` empty. For &, <, >, use \&amp;, \&lt;, \&gt; respectively.|

All fields are _not null_ and must contain a valid value of the field's
type. For `date`, `datetime`, `int`, and `real` fields there is a sentinal
value (signified with `!`) which can be used (e.g., to indicate an unknown
value).

Strings may not include `&`, `<` or `>`, so if they are needed, they must be
replaced by the XML/HTML escapes `&amp;`, `&lt;`, and `&gt;` respectively.
Strings respect any whitespace they contain, including newlines.

Each field value is separated from its neighbor by whitespace, and
conventionally records are separated by newlines. However, in practice,
since every field in every record must be present (even if only a sentinal
value or an empty bytes or string), records may be laid out however you
like.

Where whitespace is allowed (or required) it may consist of one or more
spaces, tabs, or newlines in any combination.

## Examples

### CSV

Although widely used, the CSV format is not standardized and has a number of
problems. Tdb is a standardized alternative that can distinguish fieldnames
from data records, can handle multiline text (including text with commas and
quotes) without formality, and can store one—or more—tables in a single Tdb
file.

Here's a simple CSV file:

    Date,Price,Quantity,ID,Description
    "2022-09-21",3.99,2,"CH1-A2","Chisels (pair), 1in & 1¼in"
    "2022-10-02",4.49,1,"HV2-K9","Hammer, 2lb"
    "2022-10-02",5.89,1,"SX4-D1","Eversure Sealant, 13-floz"

Here's a Tdb equivalent:

    [PriceList Date date Price real Quantity int ID str Description str
    %
    2022-09-21 3.99 2 <CH1-A2> <Chisels (pair), 1in &amp; 1¼in> 
    2022-10-02 4.49 1 <HV2-K9> <Hammer, 2lb> 
    2022-10-02 5.89 1 <SX4-D1> <Eversure Sealant, 13-floz> 
    ]

Every table starts with a tablename followed by one or more fields. Each
field consists of a fieldname and a type.

Superficially this may not seem much of an improvement on CSV (apart from
Tbd's superior string handling and strong typing), but as the next example
shows, a Tdb file can contain one _or more_ tables, not just one like CSV.

### Database

Database files aren't normally human readable and usually require
specialized tools to read and modify their contents. Yet many databases are
relatively small (both in size and number of tables), and would be more
convenient to work with if human readable. For these, Tdb format provides a
viable alternative. For example:

    [Customers CID int Company str Address str Contact str Email str
    %
    50 <Best People> <123 Somewhere> <John Doe> <j@doe.com> 
    19 <Supersuppliers> <> <Jane Doe> <jane@super.com> 
    ]
    [Invoices INUM int CID int Raised_Date date Due_Date date Paid bool Description str
    %
    152 50 2022-01-17 2022-02-17 no <COD> 
    153 19 2022-01-19 2022-02-19 yes <>
    ]
    [Items IID int INUM int Delivery_Date date Unit_Price real Quantity int Description str
    %
    1839 152 2022-01-16 29.99 2 <Bales of hay> 
    1840 152 2022-01-16 5.98 3 <Straps> 
    1620 153 2022-01-19 11.5 1 <Washers (1-in)> 
    ]

In the Customers table the second customer's Address and in the Invoices
table, the second invoice's Description both have empty strings as their
values.

### Minimal Tdb Files

	[T f int
	%
	]

This file has a single table called `T` which has a single field called `f`
of type `int`, and no records.

	[T f int
	%
	0
	]

This is like the previous table but now with one record containing the value
`0`.

	[T f int
	%
	0
	!
	]

Again like the previous table, but now with two records, the first
containing the value `0`, and the second containing the `int` type's
sentinal value of `-1808080808`.

### Metadata

If comments or metadata are required, simply create an additional table to
store this data and add it to the Tdb.

## Libraries

|**Library**|**Language**|**Notes**                    |
|-----------|------------|-----------------------------|
|tdb-go|Go|https://pkg.go.dev/github.com/mark-summerfield/tdb-go|
|tdb-py|Python|https://pkg.go.dev/github.com/mark-summerfield/tdb-py|

We will happily add links to implementations in other languages if they pass
the tests. (Tdb is a relatively simple format to parse and write.) 

## BNF

A Tdb file consists of one or more tables.

    TDB         ::= TABLE+
    TABLE       ::= OWS '[' OWS TABLEDEF OWS '%' OWS RECORD* OWS ']' OWS
    TABLEDEF    ::= IDENFIFIER (RWS FIELDDEF)+ # IDENFIFIER is the tablename
    FIELDDEF    ::= IDENFIFIER RWS TYPE # IDENFIFIER is the fieldname
    TYPE        ::= 'bool' | 'bytes' | 'date' | 'datetime' | 'int' | 'real' | 'str'
    RECORD      ::= OWS FIELD (RWS FIELD)*
    FIELD       ::= BOOL | BYTES | DATE | DATETIME | INT | REAL | STR
    BOOL        ::= /[FfTtYyNn01]/
    BYTES       ::= '(' (OWS [A-Fa-f0-9]{2})* OWS ')'
    DATE        ::= /\d\d\d\d-\d\d-\d\d/ | SENTINAL # basic ISO8601 YYYY-MM-DD format
    DATETIME    ::= /\d\d\d\d-\d\d-\d\dT\d\d(\d\d(\d\d)?)?/ | SENTINAL
    INT         ::= /[-+]?\d+/ | SENTINAL
    REAL        ::= ... | SENTINAL # standard or scientific notation
    STR         ::= /[<][^<>]*?[>]/ # newlines allowed, and &amp; &lt; &gt; supported i.e., XML
    SENTINAL    ::= '!'
    IDENFIFIER  ::= /[_\p{L}]\w{0,31}/ # Must start with a letter or underscore; may not be a built-in constant
    OWS         ::= /[\s\n]*/
    RWS         ::= /[\s\n]+/ # in some cases RWS is actually optional

_Notes_

- Every field is _not null_ and must contain a valid value of the field's
  type. For `date`, `datetime`, `int`, and `real` fields there is a sentinal
  value (signified with `!`) which can be used (e.g., to indicate an unknown
  value).
- A Tdb file _must_ contain at least one table even if it is empty, i.e.,
  has no records.
- A Tdb writer should always write ``bool``s as `F` or `T`; but a Tdb reader
  should accept any of `F`, `f`, `N`, `n`, `0`, for false, and any of `T`,
  `t`, `Y`, `y`, `1`, for true.
- Within any `.tdb` file each tablename must be unique, and within each
  table each fieldname must be unique.
- No tablename or fieldname (i.e., no identifier) may be the same as a
  built-in constant or `bool` value:  
  `bool`, `bytes`, `date`, `datetime`, `f`, `F`, `int`, `n`, `N`, `real`, `str`, `t`, `T`, `y`, `Y`

## Supplementary

### Vim Support

If you use the vim editor, simple color syntax highlighting is available.
Copy `tdb.vim` into your `$VIM/syntax/` folder and add this line (or
similar) to your `.vimrc` or `.gvimrc` file:

    au BufRead,BufNewFile,BufEnter *.tdb set ft=tdb|set expandtab|set textwidth=80

### Tdb Logo

![tdb logo](tdb.svg)

---
