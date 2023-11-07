
(let ((cwd (if load-file-name
               (file-name-directory load-file-name)
             default-directory)))
  (add-to-list 'load-path cwd)

  ;; for `subtitle-mode'
  (load-file (concat cwd "subtitle-mode.el"))
  (add-to-list 'auto-mode-alist '("\\.srt" . subtitle-mode))

  ;; for `srt-renumber-subtitles'
  (load-file (concat cwd "subtitles.el"))

  ;; for `bing-dict
  (load-file (concat cwd "bing-dict.el"))
  (define-key search-map (kbd "M-b") 'bing-dict-brief)

  (load-library "sdcv")
  (define-key search-map (kbd "M-d") 'sdcv-search-pointer+)
  
  (defun subtitle-mode-my-init ()
    (setq fill-column 50)
    (setq scroll-margin 0)
    (when (require 'fill-column-indicator nil t)
      (fci-mode 1)))
  (add-hook 'subtitle-mode-hook 'subtitle-mode-my-init)

 (defun srt-fix-chinese-punctuations ()
    (interactive)
    (save-restriction
;;      (goto-char (point-min))
;;      (query-replace-regexp "\\([^0-9a-zA-z]\\), " "\\1，")
      (goto-char (point-min))
      (query-replace "。" ". ")
      (goto-char (point-min))      
      (query-replace "．" ". ")
      (goto-char (point-min))      
      (query-replace "，" ", ")
      (goto-char (point-min))
      (query-replace "？" "? ")
      (goto-char (point-min))
      (query-replace "！" "! ")
      ))

  (global-set-key (kbd "C-x ＜") "《")
  (global-set-key (kbd "C-x ＞") "》")
;;  (global-set-key (kbd "C-x  ")  "﻿")
  (global-set-key (kbd "<apps> i SPC")  "﻿")
  )

(add-to-list 'load-path
             (concat (if load-file-name
                                  (file-name-directory load-file-name)
                                default-directory)
                     "go-translate")
             )
(when (string> emacs-version "27.0")
  (require 'eieio)
  (require 'go-translate)

  (setq gts-translate-list '(("en" "zh")))

  (setq gts-default-translator
        (gts-translator
         :picker (gts-prompt-picker)
         :engines (list (gts-bing-engine) (gts-youdao-dict-engine))
         :render (gts-buffer-render)))
  ;; now you can use command `gts-do-translate'
  )

