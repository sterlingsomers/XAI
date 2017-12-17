;;;Notes below
;;;A3rev2: Adds a chunk type for relative-location with 8 direction categories
;;;A3rev1: Adds recall of current location and target location
;;;--both the request and retrieval



;;; Copyright (c) 2017 Carnegie Mellon University
;;;
;;; Permission is hereby granted, free of charge, to any person obtaining a copy of this
;;; software and associated documentation files (the "Software"), to deal in the Software
;;; without restriction, including without limitation the rights to use, copy, modify,
;;; merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
;;; permit persons to whom the Software is furnished to do so, subject to the following
;;; conditions:
;;;
;;; The above copyright notice and this permission notice shall be included in all copies
;;; or substantial portions of the Software.
;;;
;;; THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
;;; INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
;;; PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
;;; HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
;;; CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
;;; OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

;;; This is a trivial example of Voorhees in action. It uses the addition model from the
;;; first unit of the ACT-R tutorial to add numbers, the numbers being supply over a
;;; TCP connection, and the result then being returned over that connection.
;;;
;;; To run the example first ensure you have Voorhees installed as suggested in its
;;; documentation, so that it can be loaded with QuickLisp. Then cd to a directory that
;;; contains an actr7 directory. (Alternatively you can set *actr7-parent*, below, to such
;;; a directory and run this from anywhere.) Then launch Lisp and load this file. It will
;;; start listenting for connections on port 9907 (you can change this port below). Then,
;;; from a separate terminal, send it a JSON object such as
;;;
;;; { "arg1": 3, "arg2": 5 }
;;;
;;; The ACT-R model will be run and the sum returned. For example, if you use netcat (nc)
;;; to connection the interaction in the second terminal might look something like this:
;;;
;;; $ nc localhost 9907
;;; {"arg1": 3, "arg2": 5}
;;; 8
;;; {"arg1": 3, "arg2": 2}
;;; 5
;;;

;; Run this in the CL-USER package 'cause that's the easiest place to use ACT-R.
(in-package :cl-user)

;; A couple of default values that can be changed if necessary.
(defparameter *actr7-parent* nil)

(defparameter *port* 14555)

(defparameter *msg* nil)

(defparameter *map* nil)

;; Load ACT-R if it's not already present, and then Voorhees.
#-ACT-R
(load (merge-pathnames (make-pathname :directory "actr7"
                                      :name "load-act-r"
                                      :type "lisp")
                       *actr7-parent*)
      :verbose t
      :print nil)

(ql:quickload :voorhees)

;; Define the ACT-R model. This will generate a pair of warnings about slots in the goal
;; buffer not being accessed from productions; these may be ignored.


(clear-all)

(define-model plan-model

(sgp :esc t :lf .05)


;;lat = 38.967163
;;lon = -104.81937
;;t_lat = 38.99343742021595
;;t_lon = -105.05530266366
(chunk-type initialize state)
(chunk-type waypoint-location my_lat my_lon tar_lat tar_lon value)
(chunk-type relative-location cur-lat cur-lon north north_east east south-east south south_west west north_west)
(chunk-type runway-gps end-lat end-lon)
(chunk-type waypoint-state value)


;38.97727 x -104.8219822
(add-dm
 (goal ISA initialize state clear-mission)
 (start-location ISA waypoint-location my_lat 38.967163 my_lon -104.81937 tar_lat 38.993437 tar_lon -105.055303 value 0)
 (run-way ISA runway-gps end-lat 38.97727 end-lon -104.8219822))


(P clear-mission
   =goal>
       ISA        initialize
       state      clear-mission
   ==>
   =goal>
       state      set-mission-count
   !eval! (setf *msg* (list (cons "Forward_Message" (list (cons "FLIGHT" "CLEAR_MISSION")))))
)

(P set-mission-count
   =goal>
       ISA        initialize
       state      set-mission-count
   ==>
   =goal>
       state      request-current-waypoint
   !eval! (setf *msg* (list (cons "Forward_Message" (list (cons "FLIGHT" (list (cons "SET_MISSION_COUNT" 100)))))))
)

(P request-current-waypoint
   =goal>
       ISA        initialize
       state      request-current-waypoint
   ==>
   =goal>
       state      recall-current-waypoint
   +retrieval>
       ISA         waypoint-location
       value       0

)
   
(P set-current-waypoint
   =goal>
       ISA        initialize
       state      recall-current-waypoint
   =retrieval>
       ISA        waypoint-location
       my_lat     =cur_lat
       my_lon     =cur_lon
       tar_lat    =target_lat
       tar_lon    =target_lon
       value      =waypoint_state
   ?imaginal>
       state      free
   ==>
   =goal>
       state      determine-takeoff-lat-lon

   +imaginal>
       ISA        waypoint-state
       img_lat    =cur_lat
       img_lon    =cur_lon
       value      1
  
   !eval! (setf *msg* (list (cons "Forward_Message" (list (cons "FLIGHT" (list (cons "SET_MISSION_ITEM" =waypoint_state) (cons "1" 1) (cons "2" 0) (cons "3" 16) (cons "4" 0.0) (cons "5" 0.0) (cons "6" 0.0) (cons "7" 0.0) (cons "8" =cur_lat) (cons "9" =cur_lon) (cons "10" 2004.4) (cons "11" 1) (cons "12" 0)))))))

)

(P determine-takeoff-lat-lon
  =goal>
      ISA          initialize
      state        determine-takeoff-lat-lon
  =imaginal>
      ISA          waypoint-state
      img_lat      =lat
      img_lon      =lon
      value        =waypoint_state
  ==>
  =goal>
      state        recall-takeoff-waypoint
  ;=imaginal>
  
  !eval! (setf *msg* (list (cons "Map_Request" (list (cons "method" "getRunwayEnd") (cons "args" (list))))))

)

;the following production is just to make sure the communication is working
(P recall-takeoff-waypoint
   =goal>
       ISA          initialize
       state        recall-takeoff-waypoint
   =imaginal>
       what         "RUNWAY_END"
       lat          =lat
       lon          =lon
   ==>
   =goal>
       state        set-takeoff-waypoint
   =imaginal>
   +retrieval>
       ISA          waypoint-state
    -  value        nil

   ;!output! target
   ;!eval! (setf *msg* (list (cons "Forward_Message" (list (cons "FLIGHT" (list (cons "SET_MISSION_ITEM" =waypoint_state) (cons "1" 1) (cons "2" 0) (cons "3" 16) (cons "4" 0.0) (cons "5" 0.0) (cons "6" 0.0) (cons "7" 0.0) (cons "8" =cur_lat) (cons "9" =cur_lon) (cons "10" 2004.4) (cons "11" 1) (cons "12" 0)))))))
)

(P set-takeoff-waypoint
   =goal>
       ISA          initialize
       state        set-takeoff-waypoint
   =retrieval>
       value        =waypoint_state
   =imaginal>
       what         "RUNWAY_END"
       lat          =lat
       lon          =lon
   ==>
   =goal>
       state        get-target-direction
   +retrieval>
       ISA          waypoint-location
     - tar_lat      nil
   !eval! (setf *msg* (list (cons "Forward_Message" (list (cons "FLIGHT" (list (cons "SET_MISSION_ITEM" =waypoint_state) (cons "1" 0) (cons "2" 3) (cons "3" 22) (cons "4" 0.0) (cons "5" 0.0) (cons "6" 0.0) (cons "7" 0.0) (cons "8" =lat) (cons "9" =lon) (cons "10" 50.0) (cons "11" 1) (cons "12" 0)))))))
   ;#TODO Why is this right beside the previous point?
)

(P get-target-direction
   =goal>
       ISA          initialize
       state        get-target-direction
   =retrieval>
       ISA          waypoint-location
       tar_lat      =tar_lat
       tar_lon      =tar_lon
       my_lat       =my_lat
       my_lon       =my_lon
   ==>
   =goal>
       state        none
   ;#TODO I need some way to get the direction of the larget (north, s, etc.) 
)






;(P set-takeoff-waypoint
;   =goal>
;       ISA        initialize
;       state      takeoff-waypoint
;   =imaginal>
;       state      =waypoint_state   
;   ==>   
;   =goal>
;       state      none
;   =imaginal>
;       state      2
;
;   !eval! (setf *msg* (list (cons "Forward_Message" (list (cons "FLIGHT" (list (cons "SET_MISSION_ITEM" =waypoint_state) (cons "1" 0) (cons "2" 3) (cons "3" 22) (cons "4" 0.0) (cons "5" 0.0) (cons "6" 0.0) (cons "7" 0.0) (cons "8" =cur_lat) (cons "9" =cur_lon) (cons "10" 2004.4) (cons "11" 1) (cons "12" 0)))))))
;)



;;{"Map_Request": {"args": {"lat": 38.967163, "meters": 7300, "lon": -104.81937, "exclude_list": []}, "method": "pathInRadius"}}
       ;;!eval! (setf *msg*


;;!eval! (setf *msg* `((lat .,=lat)(lon ., =lon)(meth . "foo")





(goal-focus goal)
) ; end define-model


;; Define the function that will do the work.
(defun run-plan-model (args)
  "Creates a chunk from the parsed JSON args, sets it to be the goal, runs the model,
and then returns the value of the sum slot of the chunk in the goal buffer. Note that an
integer is itself a JSON value."
  (let (socket)
    (unwind-protect
        (let ((stream (usocket:socket-stream
                       (setf socket (usocket:socket-connect "127.0.0.1" 37999 :timeout 100)))))
          (loop for x from 1 to 20
            do (run 0.05)
            do (if *msg*
                   (progn
                     (format t (vh:json-string *msg*))
                     
                     (vh:write-json *msg* stream)
                     (format t "here")
                     (let ((result (vh:read-json stream)))
                       (unless result
                         (setf result (vh:read-json stream)))
                       (format t "here2")
                       (unless (assoc 'ack result)
                         (vh:chunkify result :buffer 'imaginal :time-delta 0)))
                     (format t "here3")
                     ))
                     ;(let (result (read-line stream nil)) (format t "asdf"))))
                     ;(let (result (vh::unpack-json (st-json:read-json-from-string (read-line stream nil))))
                     ;  (format t "test"))))
            do (setf *msg* nil))

          (when socket
            (usocket:socket-close socket))))))
  ;(goal-focus-fct (vh:chunkify args))
  ;(run 0.5))
  ;(no-output (chunk-slot-value-fct (first (buffer-chunk goal)) 'sum)))


;; Run Voorhees and wait for connections, writing log information to the terminal, where
;; it will be interspersed with what ACT-R spits out.
;;(vh:run-model #'run-addition-model *port*
;;              :log-file *terminal-io*
;;              :log-json t)
