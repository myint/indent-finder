augroup IndentFinder
    au! IndentFinder

    let s:default_tab_width = &l:tabstop

    au BufRead * let b:indent_finder_result = system(
        \ fnamemodify(expand('<sfile>'), ':p:h') .
        \ '/indent_finder.py --vim-output --default-tab-width=' .
        \ s:default_tab_width . ' "' . expand('%') . '"' )

    au BufRead * execute b:indent_finder_result

    if exists('g:indent_finder_debug') && g:indent_finder_debug
        au BufRead * echo "Indent Finder: " . b:indent_finder_result
    endif
augroup End
