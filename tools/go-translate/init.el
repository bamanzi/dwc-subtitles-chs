(add-to-list 'load-path (if load-file-name
                    (file-name-directory load-file-name)
                    default-directory))

(require 'go-translate)

(setq gts-translate-list '(("en" "zh")))

(setq gts-default-translator
      (gts-translator
       :picker (gts-prompt-picker)
       :engines (list (gts-bing-engine) (gts-youdao-dict-engine))
       :render (gts-buffer-render)))
