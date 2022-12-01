# Tdb Overview

Tdb “Text DataBase” format is a plain text human readable typed database
storage format.

Tdb is an ideal alternative to CSV. A Tdb file can store any number of
tables. Every table is named, and every field has a name and a type. Types
are not-null by default, but can be nullable if required. The seven
supported types include strings which respect all whitespace (including
newlines), and which may contain any UTF-8 characters (using XML-escaping
conventions), binary (e.g., for images), Booleans, numbers (integer and
real), and dates and datetimes.

Tdb libraries are available in Go and Python with a Rust library _in
development_. The Tdb format is designed to be very easy to parse, so
creating a Tdb library in virtually any language should be straightforward.

- [Datatypes](#datatypes)
- [Examples](#examples)
    - [CSV](#csv)
    - [Database](#database)
    - [Minimal Tdb Files](#minimal-tdb-files)
- [Timezones and Metadata](#timezones-and-metadata)
- [Libraries](#libraries) (Go, Python, Rust)
- [BNF](#bnf)
- [Supplementary](#supplementary)
    - [Vim Support](#vim-support)
    - [Tdb Logo](#tdb-logo)

## Datatypes

Tdb supports the following seven built-in datatypes.

|**Type**   |**Example(s)**        |**Notes**|
|-----------|----------------------|---------|
|`bool`     |`F`|A Tdb reader should also accept 'f', 'N', 'n', 't', 'Y', 'y', '0', '1'|
|`bytes`    |`(20AC 65 66 48)`|There must be an even number of case-insensitive hex digits; whitespace (spaces, newlines, etc.) optional.|
|`date`     |`2022-04-01`|Basic ISO8601 YYYY-MM-DD format.|
|`datetime` |`2022-04-01T16:11:51`|ISO8601 YYYY-MM-DDTHH[:MM[:SS]] format; 1-sec resolution no timezone support.|
|`int`      |`-192` `234` `7891409`|Standard integers.|
|`real`     |`0.15` `0.7e-9` `2245.389`|Standard and scientific notation.|
|`str`      |`<Some text which may include newlines>`|For &, <, >, use \&amp;, \&lt;, \&gt; respectively.|

All fields are _not null_ by default and must contain a valid value of the
field's type. To make a field _nullable_, append `?` to its typename, e.g.,
`int?`.

Strings may not include `&`, `<` or `>`, so if they are needed, they must be
replaced by the XML/HTML escapes `&amp;`, `&lt;`, and `&gt;` respectively.
Strings respect any whitespace they contain, including newlines.

Each field value is separated from its neighbor by whitespace, and
conventionally records are separated by newlines. However, in practice,
since every field in every record must be present (even if only a null value
or an empty bytes or string), records may be laid out however you like.

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

    [Customers CID int Company str Address str? Contact str Email str
    %
    50 <Best People> <123 Somewhere> <John Doe> <j@doe.com> 
    19 <Supersuppliers> ? <Jane Doe> <jane@super.com> 
    ]
    [Invoices INUM int CID int Raised_Date date Due_Date date Paid bool Description str?
    %
    152 50 2022-01-17 2022-02-17 no <COD> 
    153 19 2022-01-19 2022-02-19 yes ?
    ]
    [Items IID int INUM int Delivery_Date date Unit_Price real Quantity int Description str
    %
    1839 152 2022-01-16 29.99 2 <Bales of hay> 
    1840 152 2022-01-16 5.98 3 <Straps> 
    1620 153 2022-01-19 11.5 1 <Washers (1-in)> 
    ]

In the Customers table the second customer's Address and in the Invoices
table, the second invoice's Description both have nulls as their values. (No
other fields may have nulls only these fields are nullable).

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

	[T f int?
	%
	0
	?
	]

Again like the previous table, but now with two records, the first
containing the value `0`, and the second containing null which is permitted
since the field's type is nullable.

### Timezones and Metadata

Tdb does not have direct timezone support. There are three simple solutions
for this.

If all the dates in the database are in the same timezone, then one approach
is to store all the dates as UTC. Alternatively, add a tiny configuration
table with the timezone data, for example:

    [Config key str value str?
    %
    <timezone> <+02:30>
    ]

If, however, the dates being stored have varying timezones, then add another
column specifically for the timezone. Something along these lines:

    [Readings meter str reading real when date timezone str
    %
    <EX194B4> 1932.49 2024-11-17 <-03:00>
    <V1938DX> 8492.1 2024-10-30 <+02:30>
    ]

If comments or metadata are required, simply create an additional table to
store this data and add it to the Tdb. For example, use a Config table as
shown above.

## Libraries

|**Library**|**Language**|**Homepage**                 |
|-----------|------------|-----------------------------|
|tdb-go|Go|https://pkg.go.dev/github.com/mark-summerfield/tdb-go|
|tdb-py|Python|https://pypi.org/project/tdb-py|
|tdb-rs|Rust|https://crates.io/crates/tdb-rs _(in development)_|

We will happily add links to implementations in other languages.

## BNF

A Tdb file consists of one or more tables.

    TDB         ::= TABLE+
    TABLE       ::= OWS '[' OWS TABLEDEF OWS '%' OWS RECORD* OWS ']' OWS
    TABLEDEF    ::= IDENFIFIER (RWS FIELDDEF)+ # IDENFIFIER is the tablename
    FIELDDEF    ::= IDENFIFIER RWS FIELDTYPE # IDENFIFIER is the fieldname
    FIELDTYPE   ::= ('bool' | 'bytes' | 'date' | 'datetime' | 'int' | 'real' | 'str') NULL?
    RECORD      ::= OWS VALUE (RWS VALUE)*
    VALUE       ::= BOOL | BYTES | DATE | DATETIME | INT | REAL | STR | NULL # NULL is only allowed for nullable field types
    BOOL        ::= /[FfTtYyNn01]/
    BYTES       ::= '(' (OWS [A-Fa-f0-9]{2})* OWS ')'
    DATE        ::= /\d\d\d\d-\d\d-\d\d/  # basic ISO8601 YYYY-MM-DD format
    DATETIME    ::= /\d\d\d\d-\d\d-\d\dT\d\d(\d\d(\d\d)?)?/ 
    INT         ::= /[-+]?\d+/ 
    REAL        ::= ... # standard or scientific notation
    STR         ::= /[<][^<>]*?[>]/ # newlines allowed, and &amp; &lt; &gt; supported i.e., XML
    NULL        ::= '?'
    IDENFIFIER  ::= /[_\p{L}]\w{0,31}/ # Must start with a letter or underscore; may not be a built-in constant
    OWS         ::= /[\s\n]*/
    RWS         ::= /[\s\n]+/ # in some cases RWS is actually optional

_Notes_

- Every field is _not null_ by default and must contain a valid value of the
  field's type. To make a field _nullable_, append `?` to its typename,
  e.g., `str?`; for nullable fields the value must either be one of the
  field's type (e.g., `str`) _or_ null `?`.
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
