" Vim syntax file
" Language:        Tdb
" Author:          Mark Summerfield <mark@qtrac.eu>
" URL:             https://github.com/mark-summerfield/tdb-go
" Licence:         Public Domain
" Latest Revision: 2022-11-16

if exists("b:current_syntax")
  finish
endif

syn clear
syn sync fromstart linebreaks=3 minlines=50

" Order matters!

syn keyword tdbTodo TODO FIXME DELETE CHECK TEST XXX
syn keyword tdbConst T F
syn keyword tdbType bool bytes date datetime int real str
syn match tdbNull /?/
syn match tdbPunctuation /[][%]/
syn match tdbIdentifier /\<\w\+\>/ 
syn region tdbStr start="<" end=">"
syn region tdbBytes start="(" end=")"
"syn match tdbBytes /([A-Fa-f0-9\s]\+)/ contains=tdbIdentifier keepend
syn match tdbNumber /\<[-+]\=\d\+\(\.\d\+\([Ee][-+]\=\d\+\)\=\)\=\>/
syn match tdbDateTime /\<\d\d\d\d-\d\d-\d\d\(T\d\d\(:\d\d\(:\d\d\)\=\)\=\)\=\>/
syn match tdbHeader /^Tdb1.*$/

" See https://sashamaps.net/docs/resources/20-colors/
hi tdbIdentifier guifg=#9A6324 "brown
hi tdbStr  guifg=#469990 "teal
hi tdbBytes guifg=#A6A6ED "lavender
"hi tdbBytes guifg=#808000 "olive
hi tdbConst guifg=#000075 "navy
hi tdbNull guifg=#E6194B "red
"hi tdbBytes  guifg=#F58231 "orange
hi tdbTodo guibg=#FFE119 term=italic cterm=italic gui=italic "yellow
hi tdbDateTime guifg=#297B33 "green
hi tdbNumber  guifg=#4363D8 "blue
hi tdbType guifg=#F032E6 "magenta
hi tdbPunctuation guifg=#911EB4 term=bold   cterm=bold   gui=bold "purple
hi tdbHeader  guifg=navy guibg=#FFFAC8 "beige
