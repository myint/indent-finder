augroup IndentFinder
    autocmd! IndentFinder

    let s:default_tab_width_option = '--default-tab-width=' . &l:tabstop

    let s:default_to_tabs_option = ''
    if &l:expandtab == 0
        let s:default_to_tabs_option = '--default-to-tabs'
    endif

    let s:default_spaces_option = '--default-spaces=' . &l:shiftwidth

    autocmd BufRead * let b:indent_finder_result = system(
        \ fnamemodify(expand('<sfile>'), ':p:h') .
        \ '/indent_finder.py --vim-output ' .
        \ s:default_tab_width_option . ' ' .
        \ s:default_to_tabs_option . ' ' .
        \ s:default_spaces_option . ' ' .
        \ shellescape(expand('%')))

    autocmd BufRead * execute b:indent_finder_result

    if exists('g:indent_finder_debug') && g:indent_finder_debug
        autocmd BufRead * echo "Indent Finder: " . b:indent_finder_result
    endif
augroup End
