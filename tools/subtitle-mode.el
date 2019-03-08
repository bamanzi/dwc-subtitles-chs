;;; -*- coding:utf-8; mode: emacs-lisp; indent-tabs-mode:nil -*-
;;; subtitle-mode.el -- *.srt subtiltle editing mode

;; Copyright 2014 Naoaki Iwakiri

;; Licensed under the Apache License, Version 2.0 (the "License");
;; you may not use this file except in compliance with the License.
;; You may obtain a copy of the License at

;;     http://www.apache.org/licenses/LICENSE-2.0

;; Unless required by applicable law or agreed to in writing, software
;; distributed under the License is distributed on an "AS IS" BASIS,
;; WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
;; See the License for the specific language governing permissions and
;; limitations under the License.


;;
;; commands
;;

(defun jump-next-subtitle ()
  "次の字幕位置へ飛ぶ" ; TODO:もうちょっと真面目に字幕位置を探す
  (interactive)
  (forward-sentence)
  (next-line))

(defun jump-previous-subtitle ()
  "前の字幕を入力したい位置に飛ぶ" ;TODO: 同上
  (interactive)
  (backward-sentence)
  (previous-line))

(defun find-movie-file (srtfilename)
  "find same named movie file. search from current directory then from path list." 
  (let ((basename (file-name-base srtfilename)))
    (catch 'movieFound
      (dolist (dir movie-path-list)
        (dolist (ext movie-extention-list)
          (let ((moviefile (format "%s/%s.%s" dir basename ext)))
            (when (file-regular-p moviefile) (throw 'movieFound moviefile))))))))

(defun seek-play-movie (time)
  "play the same file name movie seeked, using some other program. (mplayer2 only for now)"
  ;; TODO: what should I do with other movie players?
    (let* ((filename (buffer-file-name (current-buffer)))
          (moviename (find-movie-file filename)))
      (if (null moviename) (message "movie not found.")
        (message moviename)
        (shell-command (format "mplayer2 --sub=%s --ss=%d %s" (shell-quote-argument (expand-file-name filename)) time (shell-quote-argument (expand-file-name moviename)))))))

(defun at-number-p ()
  "cursor is on number"
  (save-excursion
    (beginning-of-line)
    (looking-at "^[0-9]+$")))

(defun check-movie-at ()
  "play the movie of where the cursor is"
  (interactive)
  (save-excursion
	(cond 
     ((at-number-p) (re-search-forward "^\\([0-9][0-9]\\):\\([0-9][0-9]\\):\\([0-9][0-9]\\)" nil t))
     (t (re-search-backward "^\\([0-9][0-9]\\):\\([0-9][0-9]\\):\\([0-9][0-9]\\)" nil t))))
    (let ((h (string-to-int (buffer-substring (match-beginning 1) (match-end 1))))
          (m (string-to-int (buffer-substring (match-beginning 2) (match-end 2))))
          (s (string-to-int (buffer-substring (match-beginning 3) (match-end 3)))))
      (seek-play-movie (+ (* (+ (* h 60) m) 60) s))))
;;
;; faces
;;
(defface subtitle-num
  '((t (:foreground "cyan" :background "dark" :bold t))) nil)

(defface subtitle-time
  '((t (:foreground "dark violet" :background "dark" :italic t))) nil)


(define-derived-mode subtitle-mode text-mode "SRT subtitle"
  "mode for editing .srt movie subtitle text file."
  (set (make-local-variable 'font-lock-defaults)
	   '((("\t" . 'underline)
		  ("^[0-9]+$" . 'subtitle-num)
		  ("[0-9]+:[0-9]+:[0-9]+,[0-9]+ --> [0-9]+:[0-9]+:[0-9]+,[0-9]+" . 'subtitle-time)
		  t t nil nil)))

  (set (make-local-variable 'movie-path-list) `(,(file-name-directory (buffer-file-name)))) ; movie file search path
  (set (make-local-variable 'movie-extention-list) '("mp4" "avi")) ; movie file extentions list

  (define-key subtitle-mode-map "\C-c\C-n" 'jump-next-subtitle)
  (define-key subtitle-mode-map "\C-c\C-p" 'jump-previous-subtitle)
  (define-key subtitle-mode-map "\C-c\C-c" 'check-movie-at)
  
  (add-hook 'subtitle-mode-hook 'turn-on-font-lock))

(provide 'subtitle-mode)

