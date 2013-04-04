augroup IndentFinder
    au! IndentFinder
    au BufRead *.* let b:indent_finder_result = system(fnamemodify(expand('<sfile>'), ':p:h') . '/indent_finder.py --vim-output "' . expand('%') . '"' )
    au BufRead *.* execute b:indent_finder_result

    " Uncomment the next line to see which indentation is applied on all your loaded files
    " au BufRead *.* echo "Indent Finder: " . b:indent_finder_result
augroup End
