
(let ((cwd (if load-file-name
               (file-name-directory load-file-name)
             default-directory)))
  ;; for `subtitle-mode'
  (load-file (concat cwd "subtitle-mode.el"))
  (add-to-list 'auto-mode-alist '("\\.srt" . subtitle-mode))

  ;; for `srt-renumber-subtitles'
  (load-file (concat cwd "subtitles.el"))

  ;; for `bing-dict
  (load-file (concat cwd "bing-dict.el"))
  (define-key search-map (kbd "M-b") 'bing-dict-brief)
  
  (defun subtitle-mode-my-init ()
    (setq fill-column 50)
    (when (require 'fill-column-indicator nil t)
      (fci-mode 1)))
  (add-hook 'subtitle-mode-hook 'subtitle-mode-my-init)
  )
